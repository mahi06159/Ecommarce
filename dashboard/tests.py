from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Order, OrderItem, Payment, Address

User = get_user_model()

class DashboardTests(APITestCase):
    def test_dashboard_endpoint(self):
        url = reverse('api_dashboard')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('Authentication', response.data['data'])
        self.assertIn('Cart', response.data['data'])
        self.assertIn('Products', response.data['data'])
        self.assertIn('Orders', response.data['data'])
        self.assertIn('Reviews', response.data['data'])


class SellerStatsTests(APITestCase):
    def setUp(self):
        # 1. Create Sellers
        self.seller_a = User.objects.create_user(
            username="seller_a", email="sellera@example.com", password="password123", role="Seller"
        )
        self.seller_b = User.objects.create_user(
            username="seller_b", email="sellerb@example.com", password="password123", role="Seller"
        )
        # 2. Create Buyer
        self.buyer = User.objects.create_user(
            username="buyer_x", email="buyerx@example.com", password="password123", role="Buyer"
        )

        # 3. Create Categories
        self.cat = Category.objects.create(name="Electronics")

        # 4. Create Products
        self.prod_a1 = Product.objects.create(
            seller=self.seller_a, category=self.cat, name="Laptop A", details="Fine", price=1000.00, stock=10
        )
        self.prod_a2 = Product.objects.create(
            seller=self.seller_a, category=self.cat, name="Mouse A", details="Fine", price=50.00, stock=2
        )
        self.prod_b = Product.objects.create(
            seller=self.seller_b, category=self.cat, name="Phone B", details="Fine", price=500.00, stock=15
        )

        # 5. Create Address
        self.address = Address.objects.create(
            user=self.buyer, address_line1="123 Street", city="Mumbai", state="MH", postal_code="400001", country="India"
        )

    def test_seller_stats_anonymous_denied(self):
        url = reverse('seller_stats')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_seller_stats_buyer_denied(self):
        url = reverse('seller_stats')
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seller_stats_empty_state(self):
        # Create a new seller with no products/orders
        new_seller = User.objects.create_user(
            username="new_seller", email="new@example.com", password="password123", role="Seller"
        )
        url = reverse('seller_stats')
        self.client.force_authenticate(user=new_seller)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data['data']
        self.assertEqual(data['total_revenue'], 0.0)
        self.assertEqual(data['total_orders'], 0)
        self.assertEqual(data['pending_orders_count'], 0)
        self.assertEqual(data['total_products'], 0)
        self.assertEqual(data['low_stock_products'], 0)
        self.assertEqual(len(data['top_5_selling_products']), 0)
        self.assertEqual(len(data['monthly_revenue_trend']), 0)

    def test_seller_stats_correct_revenue_and_filtering(self):
        # 1. Place order containing products from both Seller A and Seller B
        # Let's create an Order
        order = Order.objects.create(
            buyer=self.buyer,
            shipping_address=self.address,
            status='Pending'
        )
        
        # Order items
        item_a1 = OrderItem.objects.create(
            order=order,
            product=self.prod_a1,
            product_name="Laptop A",
            quantity=2, # 2 * 1000 = 2000
            price=1000.00,
            status='Pending'
        )
        item_a2 = OrderItem.objects.create(
            order=order,
            product=self.prod_a2,
            product_name="Mouse A",
            quantity=5, # 5 * 50 = 250
            price=50.00,
            status='Pending'
        )
        item_b = OrderItem.objects.create(
            order=order,
            product=self.prod_b,
            product_name="Phone B",
            quantity=1, # 1 * 500 = 500
            price=500.00,
            status='Pending'
        )
        
        # Verify stats before payment (revenue is 0 because status is Pending and not Paid)
        url = reverse('seller_stats')
        self.client.force_authenticate(user=self.seller_a)
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['data']['total_revenue'], 0.0)
        
        # Create a paid Payment record for the order
        Payment.objects.create(
            order=order,
            razorpay_order_id="pay_ord_1",
            amount=2750.00,
            status='Paid'
        )
        
        # Verify stats after payment for Seller A
        response_a = self.client.get(url, format='json')
        self.assertEqual(response_a.status_code, status.HTTP_200_OK)
        data_a = response_a.data['data']
        # Seller A revenue: Laptop A (2000) + Mouse A (250) = 2250
        self.assertEqual(data_a['total_revenue'], 2250.00)
        self.assertEqual(data_a['total_orders'], 1)
        self.assertEqual(data_a['pending_orders_count'], 1)
        self.assertEqual(data_a['total_products'], 2)
        # Mouse A stock is 2 (< 5), Laptop A stock is 10
        self.assertEqual(data_a['low_stock_products'], 1)
        
        # Verify stats for Seller B
        self.client.force_authenticate(user=self.seller_b)
        response_b = self.client.get(url, format='json')
        self.assertEqual(response_b.status_code, status.HTTP_200_OK)
        data_b = response_b.data['data']
        # Seller B revenue: Phone B (500) = 500
        self.assertEqual(data_b['total_revenue'], 500.00)
        self.assertEqual(data_b['total_orders'], 1)
        self.assertEqual(data_b['pending_orders_count'], 1)
        self.assertEqual(data_b['total_products'], 1)
