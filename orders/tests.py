from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.conf import settings
from products.models import Category, Product
from orders.models import Address, Order, OrderItem, Payment, Cart, CartItem
from unittest.mock import patch, MagicMock
import hmac
import hashlib

User = get_user_model()

class OrderTests(APITestCase):

    def setUp(self):
        # Create users
        self.seller = User.objects.create_user(
            username="seller_user",
            email="seller@example.com",
            password="testpassword",
            role="Seller"
        )
        self.other_seller = User.objects.create_user(
            username="other_seller",
            email="otherseller@example.com",
            password="testpassword",
            role="Seller"
        )
        self.buyer = User.objects.create_user(
            username="buyer_user",
            email="buyer@example.com",
            password="testpassword",
            role="Buyer"
        )
        self.other_buyer = User.objects.create_user(
            username="other_buyer",
            email="other_buyer@example.com",
            password="testpassword",
            role="Buyer"
        )

        # Create Addresses
        self.address = Address.objects.create(
            user=self.buyer,
            address_line1="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA",
            is_default=True
        )
        self.other_buyer_address = Address.objects.create(
            user=self.other_buyer,
            address_line1="456 Elm St",
            city="Boston",
            state="MA",
            postal_code="02108",
            country="USA",
            is_default=True
        )

        # Category & Products
        self.category = Category.objects.create(name="Electronics")
        self.product1 = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Smartphone",
            details="A premium smartphone.",
            price=500.00,
            stock=10
        )
        self.product2 = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Wireless Earbuds",
            details="Noise cancelling earbuds.",
            price=100.00,
            stock=5
        )
        self.other_product = Product.objects.create(
            seller=self.other_seller,
            category=self.category,
            name="T-Shirt",
            details="Cotton shirt.",
            price=20.00,
            stock=50
        )

    # 1. Address CRUD Tests
    def test_create_address(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('address_list_create')
        data = {
            "address_line1": "789 Oak Ave",
            "city": "Seattle",
            "state": "WA",
            "postal_code": "98101",
            "country": "USA",
            "is_default": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.filter(user=self.buyer).count(), 2)

    def test_list_addresses(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('address_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_delete_address(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('address_detail', kwargs={'pk': self.address.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Address.objects.filter(id=self.address.id).count(), 0)

    # 2. Profiles Tests
    def test_profile_automatically_created_and_retrieved(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain profile block
        self.assertIsNotNone(response.data['data']['profile'])
        self.assertIn('phone_number', response.data['data'])

    def test_update_profile(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('profile')
        data = {
            "phone_number": "+19999999999"
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.phone_number, "+19999999999")

    # 3. Order Placement Tests
    def test_place_order_multi_products(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('order_list_create')
        order_data = {
            "shipping_address": self.address.id,
            "items": [
                {"product": self.product1.id, "quantity": 2},
                {"product": self.product2.id, "quantity": 1}
            ]
        }
        response = self.client.post(url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify total price ($500 * 2 + $100 * 1 = $1100)
        order = Order.objects.get(id=response.data['data']['id'])
        self.assertEqual(order.total_price, 1100.00)
        self.assertEqual(order.items.count(), 2)

        # Verify stock reduction
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertEqual(self.product1.stock, 8)
        self.assertEqual(self.product2.stock, 4)

    def test_place_order_insufficient_stock(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('order_list_create')
        order_data = {
            "shipping_address": self.address.id,
            "items": [
                {"product": self.product2.id, "quantity": 10} # only 5 in stock
            ]
        }
        response = self.client.post(url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_place_order_invalid_address(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('order_list_create')
        order_data = {
            "shipping_address": self.other_buyer_address.id, # belongs to other_buyer
            "items": [
                {"product": self.product1.id, "quantity": 1}
            ]
        }
        response = self.client.post(url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_place_order_fails_for_seller(self):
        self.client.force_authenticate(user=self.seller)
        url = reverse('order_list_create')
        order_data = {
            "shipping_address": self.address.id,
            "items": [
                {"product": self.product1.id, "quantity": 1}
            ]
        }
        response = self.client.post(url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 4. Listing and Visibility Tests
    def test_order_listing_visibility_seller_filters_items(self):
        # Create an order containing products from self.seller and self.other_seller
        order = Order.objects.create(
            buyer=self.buyer,
            shipping_address=self.address,
            shipping_address_text=str(self.address)
        )
        # Item 1 owned by self.seller
        item1 = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=1,
            price=self.product1.price
        )
        # Item 2 owned by self.other_seller
        item2 = OrderItem.objects.create(
            order=order,
            product=self.other_product,
            quantity=1,
            price=self.other_product.price
        )
        order.total_price = self.product1.price + self.other_product.price
        order.save()

        # Seller 1 requests list
        self.client.force_authenticate(user=self.seller)
        url = reverse('order_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # They should see the order, but the items list should ONLY contain item1 (Smartphone)
        orders_data = response.data['data']
        self.assertEqual(len(orders_data), 1)
        items = orders_data[0]['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['product'], self.product1.id)

        # Buyer requests list
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Buyer sees BOTH items
        orders_data = response.data['data']
        self.assertEqual(len(orders_data), 1)
        items = orders_data[0]['items']
        self.assertEqual(len(items), 2)

    # 5. Status Updates Tests
    def test_update_order_item_status_by_seller(self):
        order = Order.objects.create(
            buyer=self.buyer,
            shipping_address=self.address,
            shipping_address_text=str(self.address)
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            price=self.product1.price
        )
        order.total_price = self.product1.price * 2
        order.save()

        self.client.force_authenticate(user=self.seller)
        url = reverse('order_item_status_update', kwargs={'pk': item.id})
        response = self.client.patch(url, {"status": "Completed"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        item.refresh_from_db()
        self.assertEqual(item.status, "Completed")
        # Parent order should also become Completed since its only item is Completed
        order.refresh_from_db()
        self.assertEqual(order.status, "Completed")

    def test_cancel_order_item_restores_stock(self):
        # Place order
        self.client.force_authenticate(user=self.buyer)
        place_url = reverse('order_list_create')
        order_data = {
            "shipping_address": self.address.id,
            "items": [
                {"product": self.product2.id, "quantity": 2}
            ]
        }
        place_resp = self.client.post(place_url, order_data, format='json')
        order_id = place_resp.data['data']['id']
        
        self.product2.refresh_from_db()
        self.assertEqual(self.product2.stock, 3) # stock reduced from 5 to 3

        # Seller cancels item
        order = Order.objects.get(id=order_id)
        item = order.items.first()
        self.client.force_authenticate(user=self.seller)
        status_url = reverse('order_item_status_update', kwargs={'pk': item.id})
        response = self.client.patch(status_url, {"status": "Cancelled"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Stock should be restored
        self.product2.refresh_from_db()
        self.assertEqual(self.product2.stock, 5)

        # Order should be Cancelled
        order.refresh_from_db()
        self.assertEqual(order.status, "Cancelled")

    # 6. Cart Tests
    def test_cart_operations_anonymous(self):
        # Add to cart anonymously
        url = reverse('cart_view')
        data = {
            "product": self.product1.id,
            "quantity": 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        cart_id = response.data['data']['id']
        self.assertIsNotNone(cart_id)

        # Get cart anonymously
        get_url = f"{url}?cart_id={cart_id}"
        response = self.client.get(get_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['items']), 1)
        self.assertEqual(response.data['data']['items'][0]['product'], self.product1.id)
        self.assertEqual(response.data['data']['items'][0]['quantity'], 2)

        # Update cart item quantity
        item_id = response.data['data']['items'][0]['id']
        patch_url = reverse('cart_item_update_delete', kwargs={'pk': item_id})
        response = self.client.patch(patch_url, {"quantity": 4}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['items'][0]['quantity'], 4)

        # Remove from cart
        response = self.client.delete(patch_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['items']), 0)

    def test_cart_checkout_authenticated_only(self):
        # 1. Add item to cart anonymously
        url = reverse('cart_view')
        data = {
            "product": self.product1.id,
            "quantity": 2
        }
        response = self.client.post(url, data, format='json')
        cart_id = response.data['data']['id']

        # 2. Try to checkout anonymously (should fail)
        checkout_url = reverse('order_list_create')
        checkout_data = {
            "shipping_address": self.address.id,
            "cart_id": cart_id
        }
        response = self.client.post(checkout_url, checkout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 3. Authenticate and checkout successfully
        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(checkout_url, checkout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['total_price'], "1000.00") # 500 * 2

        # 4. Verify stock reduction
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, 8)

    # 7. Soft Delete and Historical Product Name Tests
    def test_soft_delete_product_graceful(self):
        # 1. Place order for product1
        self.client.force_authenticate(user=self.buyer)
        place_url = reverse('order_list_create')
        order_data = {
            "shipping_address": self.address.id,
            "items": [
                {"product": self.product1.id, "quantity": 1}
            ]
        }
        response = self.client.post(place_url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['data']['id']

        # 2. Soft delete product1
        self.client.force_authenticate(user=self.seller)
        delete_url = reverse('product_detail', kwargs={'pk': self.product1.id})
        response = self.client.delete(delete_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Verify product is soft deleted (not showing in active endpoints)
        self.client.force_authenticate(user=self.buyer)
        get_prod_url = reverse('product_detail', kwargs={'pk': self.product1.id})
        response = self.client.get(get_prod_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 4. Retrieve order details and verify product_name is preserved
        get_order_url = reverse('order_detail', kwargs={'pk': order_id})
        response = self.client.get(get_order_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the product details are null/filtered out (since it is deleted)
        # but the product_name_display shows the name correct snapshot
        item_data = response.data['data']['items'][0]
        self.assertEqual(item_data['product_name_display'], "Smartphone")


class PaymentTests(APITestCase):

    def setUp(self):
        # Create users
        self.buyer = User.objects.create_user(
            username="buyer_user_pay",
            email="buyerpay@example.com",
            password="testpassword",
            role="Buyer"
        )
        self.seller = User.objects.create_user(
            username="seller_user_pay",
            email="sellerpay@example.com",
            password="testpassword",
            role="Seller"
        )
        # Create address
        self.address = Address.objects.create(
            user=self.buyer,
            address_line1="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA",
            is_default=True
        )
        # Create product
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Smartphone",
            details="A premium smartphone.",
            price=500.00,
            stock=10
        )
        # Create cart and cart item
        self.cart = Cart.objects.create(user=self.buyer)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

    @patch('urllib.request.urlopen')
    def test_create_razorpay_order_success(self, mock_urlopen):
        # Mock successful URL open
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"id": "order_mocked123", "amount": 100000}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.client.force_authenticate(user=self.buyer)
        url = reverse('razorpay_order_create')
        data = {
            "cart_id": str(self.cart.id),
            "shipping_address": self.address.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['razorpay_order_id'], "order_mocked123")
        
        # Check Payment model created
        self.assertEqual(Payment.objects.filter(razorpay_order_id="order_mocked123").count(), 1)
        payment = Payment.objects.get(razorpay_order_id="order_mocked123")
        self.assertEqual(payment.amount, 1000.00)
        self.assertEqual(payment.status, 'Created')

    def test_verify_razorpay_payment_success(self):
        # Create a payment in local DB
        payment = Payment.objects.create(
            razorpay_order_id="order_xyz",
            amount=1000.00,
            status='Created'
        )

        self.client.force_authenticate(user=self.buyer)
        url = reverse('razorpay_order_verify')
        
        # Generate valid signature
        msg = "order_xyz|pay_abc"
        secret = settings.RAZORPAY_KEY_SECRET
        sig = hmac.new(
            key=secret.encode('utf-8'),
            msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        data = {
            "razorpay_order_id": "order_xyz",
            "razorpay_payment_id": "pay_abc",
            "razorpay_signature": sig,
            "cart_id": str(self.cart.id),
            "shipping_address": self.address.id
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify Payment and Order status
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'Paid')
        self.assertIsNotNone(payment.order)
        self.assertEqual(payment.order.total_price, 1000.00)
        
        # Verify Stock reduction
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

    def test_verify_razorpay_payment_invalid_signature(self):
        # Create payment
        payment = Payment.objects.create(
            razorpay_order_id="order_failed",
            amount=1000.00,
            status='Created'
        )

        self.client.force_authenticate(user=self.buyer)
        url = reverse('razorpay_order_verify')

        data = {
            "razorpay_order_id": "order_failed",
            "razorpay_payment_id": "pay_failed",
            "razorpay_signature": "invalid_sig",
            "cart_id": str(self.cart.id),
            "shipping_address": self.address.id
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'Failed')
        
        # Assert no order was created
        self.assertEqual(Order.objects.count(), 0)
        # Assert product stock remained unchanged
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
        # Assert cart still contains the item
        self.assertTrue(self.cart.items.exists())

    def test_verify_razorpay_payment_duplicate(self):
        # 1. First, perform a successful verification to create an order
        payment = Payment.objects.create(
            razorpay_order_id="order_dup",
            amount=1000.00,
            status='Created'
        )

        self.client.force_authenticate(user=self.buyer)
        url = reverse('razorpay_order_verify')

        msg = "order_dup|pay_dup"
        secret = settings.RAZORPAY_KEY_SECRET
        sig = hmac.new(
            key=secret.encode('utf-8'),
            msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        data = {
            "razorpay_order_id": "order_dup",
            "razorpay_payment_id": "pay_dup",
            "razorpay_signature": sig,
            "cart_id": str(self.cart.id),
            "shipping_address": self.address.id
        }

        # First verification call: creates order, status goes to Paid
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        created_order_id = response1.data['data']['id']

        # Second verification call: should return success and NOT create a new order
        response2 = self.client.post(url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(response2.data['data']['id'], created_order_id)




