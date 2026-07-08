from rest_framework import serializers
from orders.models import Address, Order, OrderItem, Cart, CartItem
from products.models import Product
from products.serializers import ProductOutputSerializer
from django.db import transaction
from decimal import Decimal


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'postal_code',
            'country',
            'is_default',
            'created_at'
        ]
        read_only_fields = ['user']

    def validate(self, attrs):
        return attrs


class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductOutputSerializer(source='product', read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_details',
            'quantity'
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'items',
            'total_price',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        total = Decimal('0.00')
        for item in obj.items.all():
            total += item.product.price * item.quantity
        return total


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all_with_deleted())
    product_details = ProductOutputSerializer(source='product', read_only=True)
    product_name_display = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_details',
            'product_name_display',
            'quantity',
            'price',
            'status'
        ]
        read_only_fields = ['price', 'status']

    def get_product_name_display(self, obj):
        return obj.product.name if obj.product else obj.product_name


class OrderSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    items = OrderItemSerializer(many=True, required=False)
    cart_id = serializers.UUIDField(write_only=True, required=False)
    shipping_address_details = AddressSerializer(source='shipping_address', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'buyer',
            'buyer_username',
            'items',
            'cart_id',
            'total_price',
            'status',
            'shipping_address',
            'shipping_address_details',
            'shipping_address_text',
            'created_at'
        ]
        read_only_fields = ['buyer', 'total_price', 'status', 'shipping_address_text']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user and request.user.role == 'Seller':
            data['items'] = [
                item for item in data['items']
                if item['product_details'] and item['product_details']['seller']['id'] == request.user.id
            ]
        return data

    def validate(self, attrs):
        items_data = attrs.get('items', [])
        cart_id = attrs.get('cart_id')
        shipping_address = attrs.get('shipping_address')

        if not items_data and not cart_id:
            raise serializers.ValidationError("An order must contain either an items list or a cart_id.")

        if cart_id:
            try:
                cart = Cart.objects.get(pk=cart_id)
            except Cart.DoesNotExist:
                raise serializers.ValidationError({"cart_id": "Cart not found."})
            
            if not cart.items.exists():
                raise serializers.ValidationError({"cart_id": "Cart is empty."})
            
            # Validate stock and active status for all items
            for item in cart.items.all():
                product = item.product
                quantity = item.quantity
                if product.is_deleted:
                    raise serializers.ValidationError({
                        "cart_id": f"Product '{product.name}' is no longer available."
                    })
                if product.stock < quantity:
                    raise serializers.ValidationError({
                        "cart_id": f"Insufficient stock for '{product.name}'. Only {product.stock} items available."
                    })
        else:
            for item in items_data:
                product = item.get('product')
                quantity = item.get('quantity')

                if product.is_deleted:
                    raise serializers.ValidationError({"items": f"Product '{product.name}' is no longer available."})

                if quantity <= 0:
                    raise serializers.ValidationError({"items": f"Quantity for product '{product.name}' must be a positive integer."})

                if product.stock < quantity:
                    raise serializers.ValidationError({
                        "items": f"Insufficient stock for '{product.name}'. Only {product.stock} items available."
                    })

        # Verify address belongs to the request user
        request = self.context.get('request')
        if request and request.user:
            if shipping_address.user != request.user:
                raise serializers.ValidationError({"shipping_address": "This address does not belong to you."})

        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        cart_id = validated_data.pop('cart_id', None)
        shipping_address = validated_data.get('shipping_address')
        
        validated_data['shipping_address_text'] = str(shipping_address)

        with transaction.atomic():
            order = Order.objects.create(total_price=0.00, **validated_data)
            total_price = Decimal('0.00')

            if cart_id:
                cart = Cart.objects.get(pk=cart_id)
                for cart_item in cart.items.all():
                    product = cart_item.product
                    quantity = cart_item.quantity
                    price = product.price

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=quantity,
                        price=price
                    )

                    product.stock -= quantity
                    product.save()

                    total_price += price * quantity
                
                # Empty the cart items on checkout success
                cart.items.all().delete()
            else:
                for item_data in items_data:
                    product = item_data['product']
                    quantity = item_data['quantity']
                    price = product.price
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=quantity,
                        price=price
                    )
                    
                    product.stock -= quantity
                    product.save()
                    
                    total_price += price * quantity
            
            order.total_price = total_price
            order.save()

        return order


class OrderItemStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['status']

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        if new_status == old_status:
            return instance

        product = instance.product

        if product:
            # If status changes to Cancelled, return stock to product inventory
            if new_status == 'Cancelled' and old_status != 'Cancelled':
                product.stock += instance.quantity
                product.save()

            # If status was Cancelled and is now restored, reduce stock again (if possible)
            elif old_status == 'Cancelled' and new_status != 'Cancelled':
                if product.stock < instance.quantity:
                    raise serializers.ValidationError({
                        "status": f"Cannot change status. Insufficient product stock to restore order item. Stock available: {product.stock}"
                    })
                product.stock -= instance.quantity
                product.save()

        instance.status = new_status
        instance.save()

        # Update parent order status based on all item statuses
        order = instance.order
        all_items = order.items.all()
        statuses = [item.status for item in all_items]
        
        if all(s == 'Cancelled' for s in statuses):
            order.status = 'Cancelled'
        elif all(s in ['Completed', 'Cancelled'] for s in statuses) and any(s == 'Completed' for s in statuses):
            order.status = 'Completed'
        else:
            order.status = 'Pending'
        order.save()

        return instance


