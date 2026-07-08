from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import transaction
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)
import hmac
import hashlib
import json
import base64
import urllib.request
import urllib.error
import uuid

from products.models import Product
from orders.models import Order, OrderItem, Address, Cart, CartItem, Payment
from orders.serializers import (
    OrderSerializer, 
    OrderItemStatusUpdateSerializer,
    AddressSerializer,
    CartSerializer,
    CartItemSerializer
)
from ecom_project.utils import success_response, error_response




class AddressListCreateView(generics.ListCreateAPIView):
    """
    GET: List authenticated user's addresses.
    POST: Create a new address for the authenticated user.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = AddressSerializer(queryset, many=True)
        return success_response(
            message="Addresses retrieved successfully.",
            data=serializer.data
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(
            message="Address created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve an address.
    PUT/PATCH: Update an address.
    DELETE: Delete an address.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Address.DoesNotExist:
            return error_response(
                message="Address not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = AddressSerializer(instance)
        return success_response(
            message="Address details retrieved.",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
        except Address.DoesNotExist:
            return error_response(
                message="Address not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = AddressSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            message="Address updated successfully.",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Address.DoesNotExist:
            return error_response(
                message="Address not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        instance.delete()
        return success_response(
            message="Address deleted successfully."
        )


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET: List orders.
         - Buyers see orders they placed.
         - Sellers see orders containing their products (filtered items).
    POST: Place an order (Buyer only, support multiple items and shipping address).
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Buyer':
            return Order.objects.filter(buyer=user).prefetch_related(
                'items', 'items__product', 'items__product__seller', 'items__product__category'
            ).order_by('-created_at')
        elif user.role == 'Seller':
            return Order.objects.filter(items__product__seller=user).distinct().prefetch_related(
                'items', 'items__product', 'items__product__seller', 'items__product__category'
            ).order_by('-created_at')
        return Order.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = OrderSerializer(queryset, many=True, context={'request': request})
        return success_response(
            message="Orders retrieved successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        if request.user.role != 'Buyer':
            return error_response(
                message="Only Buyers can place orders.",
                errors={"detail": "You do not have permission to perform this action."},
                status_code=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(buyer=request.user)
        return success_response(
            message="Order placed successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class OrderDetailView(generics.RetrieveAPIView):
    """
    GET: Retrieve a specific order.
         - Buyers can retrieve only their own orders.
         - Sellers can retrieve only orders containing their products.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Buyer':
            return Order.objects.filter(buyer=user)
        elif user.role == 'Seller':
            return Order.objects.filter(items__product__seller=user).distinct()
        return Order.objects.none()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset().prefetch_related(
                'items', 'items__product', 'items__product__seller', 'items__product__category'
            ).get(pk=kwargs['pk'])
        except Order.DoesNotExist:
            return error_response(
                message="Order not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(instance, context={'request': request})
        return success_response(
            message="Order details retrieved.",
            data=serializer.data
        )


class OrderItemStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH/PUT: Update order item status (Seller owner of the product only).
    """
    serializer_class = OrderItemStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Seller':
            return OrderItem.objects.filter(product__seller=user).select_related('product', 'order')
        return OrderItem.objects.none()

    def update(self, request, *args, **kwargs):
        if request.user.role != 'Seller':
            return error_response(
                message="Only Sellers can update order item status.",
                errors={"detail": "You do not have permission to perform this action."},
                status_code=status.HTTP_403_FORBIDDEN
            )

        try:
            instance = self.get_queryset().get(pk=kwargs['pk'])
        except OrderItem.DoesNotExist:
            return error_response(
                message="Order item not found or you do not have permission to manage it.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        partial = kwargs.pop('partial', False)
        serializer = OrderItemStatusUpdateSerializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(
            message="Order item status updated successfully.",
            data=serializer.data
        )


class CartView(APIView):
    """
    GET: Get a cart by cart_id (UUID query parameter) or the authenticated user's cart.
    POST: Add a product to the cart.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        cart_id = request.query_params.get('cart_id')
        user = request.user
        cart = None

        if cart_id:
            try:
                cart = Cart.objects.prefetch_related('items', 'items__product').get(pk=cart_id)
                # Link cart to user if authenticated and not yet linked
                if user.is_authenticated and cart.user is None:
                    cart.user = user
                    cart.save()
            except (Cart.DoesNotExist, ValueError, ValidationError):
                pass

        # If no cart found via cart_id but user is authenticated, get/create user's cart
        if cart is None and user.is_authenticated:
            cart, _ = Cart.objects.prefetch_related('items', 'items__product').get_or_create(user=user)

        if cart is None:
            # Create a new empty anonymous cart
            cart = Cart.objects.create()

        serializer = CartSerializer(cart)
        return success_response(
            message="Cart retrieved successfully.",
            data=serializer.data
        )

    def post(self, request):
        cart_id = request.data.get('cart_id')
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)
        user = request.user
        cart = None

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            return error_response(
                message="Quantity must be a positive integer.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if cart_id:
            try:
                cart = Cart.objects.get(pk=cart_id)
            except (Cart.DoesNotExist, ValueError, ValidationError):
                pass

        if cart is None:
            if user.is_authenticated:
                cart, _ = Cart.objects.get_or_create(user=user)
            else:
                cart = Cart.objects.create()

        # Double check user link
        if user.is_authenticated and cart.user is None:
            cart.user = user
            cart.save()

        # Fetch product
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_response(
                message="Product not found or has been deleted.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if product.stock < quantity:
            return error_response(
                message=f"Insufficient stock. Only {product.stock} items available.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Add or update CartItem
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            new_quantity = cart_item.quantity + quantity
            if product.stock < new_quantity:
                return error_response(
                    message=f"Cannot add items. Insufficient stock. Only {product.stock} items available, and you already have {cart_item.quantity} in your cart.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return success_response(
            message="Item added to cart successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class CartItemUpdateDeleteView(APIView):
    """
    PATCH: Update cart item quantity.
    DELETE: Remove cart item from cart.
    """
    permission_classes = [AllowAny]

    def patch(self, request, pk):
        try:
            cart_item = CartItem.objects.select_related('product', 'cart').get(pk=pk)
        except CartItem.DoesNotExist:
            return error_response(
                message="Cart item not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get('quantity')
        if quantity is None:
            return error_response(
                message="Quantity field is required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            return error_response(
                message="Quantity must be a positive integer.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Check stock
        product = cart_item.product
        if product.stock < quantity:
            return error_response(
                message=f"Insufficient stock. Only {product.stock} items available.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        cart_serializer = CartSerializer(cart_item.cart)
        return success_response(
            message="Cart item updated successfully.",
            data=cart_serializer.data
        )

    def delete(self, request, pk):
        try:
            cart_item = CartItem.objects.select_related('cart').get(pk=pk)
        except CartItem.DoesNotExist:
            return error_response(
                message="Cart item not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        cart = cart_item.cart
        cart_item.delete()

        cart_serializer = CartSerializer(cart)
        return success_response(
            message="Item removed from cart successfully.",
            data=cart_serializer.data
        )


class RazorpayOrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'Buyer':
            return error_response(
                message="Only Buyers can initiate payments.",
                errors={"detail": "You do not have permission to perform this action."},
                status_code=status.HTTP_403_FORBIDDEN
            )

        cart_id = request.data.get('cart_id')
        shipping_address_id = request.data.get('shipping_address')

        if not cart_id or not shipping_address_id:
            return error_response(
                message="cart_id and shipping_address are required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Validate request via serializer context to run standard stock checks
        serializer = OrderSerializer(
            data={'cart_id': cart_id, 'shipping_address': shipping_address_id},
            context={'request': request}
        )
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as err:
            errors = err.detail if hasattr(err, 'detail') else {"detail": str(err)}
            return error_response(
                message="Order validation failed.",
                errors=errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Calculate Total Price from Cart items
        try:
            cart = Cart.objects.get(pk=cart_id)
        except Cart.DoesNotExist:
            return error_response(
                message="Cart not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        total_price = sum(item.product.price * item.quantity for item in cart.items.all())

        if total_price <= 0:
            return error_response(
                message="Cart total must be greater than zero.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Create order in Razorpay
        amount_paise = int(total_price * 100)
        receipt_id = f"receipt_{uuid.uuid4().hex[:10]}"

        # Razorpay endpoint configuration
        url = "https://api.razorpay.com/v1/orders"
        post_data = json.dumps({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt_id
        }).encode('utf-8')

        req = urllib.request.Request(url, data=post_data, headers={
            "Content-Type": "application/json"
        })

        # Basic Auth credentials
        key_id = settings.RAZORPAY_KEY_ID
        key_secret = settings.RAZORPAY_KEY_SECRET
        auth_str = f"{key_id}:{key_secret}"
        auth_bytes = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        req.add_header("Authorization", f"Basic {auth_bytes}")

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                razorpay_order_id = res_data.get('id')
        except urllib.error.HTTPError as e:
            error_content = e.read().decode('utf-8')
            return error_response(
                message="Failed to create order on Razorpay.",
                errors={"detail": error_content},
                status_code=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return error_response(
                message="Error contacting payment service.",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Create local payment record
        Payment.objects.create(
            razorpay_order_id=razorpay_order_id,
            amount=total_price,
            status='Created'
        )

        return success_response(
            message="Razorpay order created successfully.",
            data={
                "razorpay_order_id": razorpay_order_id,
                "amount": amount_paise,
                "currency": "INR",
                "key_id": key_id
            }
        )


class RazorpayOrderVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        cart_id = request.data.get('cart_id')
        shipping_address_id = request.data.get('shipping_address')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, cart_id, shipping_address_id]):
            return error_response(
                message="All payment verification details (razorpay_order_id, razorpay_payment_id, razorpay_signature, cart_id, shipping_address) are required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return error_response(
                message="Payment record not found for the provided razorpay_order_id.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Verify Signature
        key_secret = settings.RAZORPAY_KEY_SECRET
        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            key=key_secret.encode('utf-8'),
            msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, razorpay_signature):
            payment.status = 'Failed'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()
            return error_response(
                message="Payment signature verification failed.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # If signature is valid, finalize payment and create order atomically
        order = None
        response_data = None
        try:
            with transaction.atomic():
                # Lock the payment row
                payment = Payment.objects.select_for_update().get(pk=payment.pk)
                
                # Check if it was already processed (to prevent double order creation)
                if payment.status == 'Paid':
                    if payment.order:
                        serializer = OrderSerializer(payment.order, context={'request': request})
                        return success_response(
                            message="Order already placed.",
                            data=serializer.data
                        )
                    else:
                        return error_response(
                            message="Payment already processed but no order linked.",
                            status_code=status.HTTP_400_BAD_REQUEST
                        )

                # Set payment fields
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.status = 'Paid'
                payment.save()

                # Process order creation
                serializer = OrderSerializer(
                    data={'cart_id': cart_id, 'shipping_address': shipping_address_id},
                    context={'request': request}
                )
                serializer.is_valid(raise_exception=True)
                order = serializer.save(buyer=request.user)

                # Link order to payment
                payment.order = order
                payment.save()

                response_data = serializer.data
        except Exception as e:
            errors = e.detail if hasattr(e, 'detail') else {"detail": str(e)}
            return error_response(
                message="Failed to finalize order after payment verification.",
                errors=errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Send emails outside the transaction block
        if order:
            try:
                items = order.items.all().select_related('product', 'product__seller')
                
                # Send email to Buyer
                buyer_email = order.buyer.email
                buyer_username = order.buyer.username
                shipping_addr = order.shipping_address_text or str(order.shipping_address)
                
                item_details_text = ""
                for it in items:
                    name = it.product.name if it.product else it.product_name
                    item_details_text += f"- {name} x {it.quantity} (Price: {it.price})\n"
                
                buyer_subject = f"Order Confirmation - Order #{order.id}"
                buyer_body = (
                    f"Hello {buyer_username},\n\n"
                    f"Your payment has been verified and your order has been placed successfully!\n\n"
                    f"Order Details:\n"
                    f"Order ID: #{order.id}\n"
                    f"Total Price: {order.total_price}\n"
                    f"Shipping Address:\n{shipping_addr}\n\n"
                    f"Items Ordered:\n{item_details_text}\n"
                    f"Thank you for shopping with us! 🌸"
                )
                
                send_mail(
                    subject=buyer_subject,
                    message=buyer_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[buyer_email],
                    fail_silently=False
                )
                
                # Group items by seller
                seller_items = {}
                for it in items:
                    if it.product and it.product.seller:
                        seller = it.product.seller
                        if seller.id not in seller_items:
                            seller_items[seller.id] = {
                                "email": seller.email,
                                "username": seller.username,
                                "items": []
                            }
                        seller_items[seller.id]["items"].append(it)
                
                for s_id, s_info in seller_items.items():
                    s_email = s_info["email"]
                    s_username = s_info["username"]
                    s_item_details_text = ""
                    for it in s_info["items"]:
                        name = it.product.name
                        s_item_details_text += f"- {name} x {it.quantity} (Price: {it.price})\n"
                    
                    seller_subject = f"New Sale Notification - Order #{order.id}"
                    seller_body = (
                        f"Hello {s_username},\n\n"
                        f"You have received a new order!\n\n"
                        f"Order ID: #{order.id}\n\n"
                        f"Your Items Ordered:\n{s_item_details_text}\n"
                        f"Please prepare the shipment. 📦"
                    )
                    
                    send_mail(
                        subject=seller_subject,
                        message=seller_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[s_email],
                        fail_silently=False
                    )
            except Exception as mail_err:
                logger.error("Failed to send order confirmation emails for Order #%s: %s", order.id, str(mail_err))

        return success_response(
            message="Payment verified and order placed successfully.",
            data=response_data,
            status_code=status.HTTP_201_CREATED
        )



