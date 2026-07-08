from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import Category, Product, ProductImage

User = get_user_model()


def _dummy_image(name="product.gif"):
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )
    return SimpleUploadedFile(name, small_gif, content_type="image/gif")


class ProductTests(APITestCase):

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
            email="other_seller@example.com",
            password="testpassword",
            role="Seller"
        )
        self.buyer = User.objects.create_user(
            username="buyer_user",
            email="buyer@example.com",
            password="testpassword",
            role="Buyer"
        )

        # Create Category
        self.category = Category.objects.create(name="Electronics")
        self.other_category = Category.objects.create(name="Books")

        # Create Product
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Smartphone",
            details="A premium smartphone.",
            price=699.99,
            stock=10
        )

    def test_category_list_accessible_by_everyone(self):
        url = reverse('category_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 2)

    def test_category_creation_by_seller(self):
        self.client.force_authenticate(user=self.seller)
        url = reverse('category_list_create')
        response = self.client.post(url, {"name": "Clothing"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

    def test_category_creation_fails_for_buyer(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('category_list_create')
        response = self.client.post(url, {"name": "Clothing"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_list_accessible_by_everyone(self):
        url = reverse('product_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)

    def test_product_creation_by_seller(self):
        self.client.force_authenticate(user=self.seller)
        url = reverse('product_list_create')
        product_data = {
            "category": self.category.id,
            "name": "Laptop",
            "details": "A powerful developer laptop.",
            "price": "1299.99",
            "stock": 5
        }
        response = self.client.post(url, product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], "Laptop")

    def test_product_creation_fails_for_buyer(self):
        self.client.force_authenticate(user=self.buyer)
        url = reverse('product_list_create')
        product_data = {
            "category": self.category.id,
            "name": "Laptop",
            "details": "A powerful developer laptop.",
            "price": "1299.99",
            "stock": 5
        }
        response = self.client.post(url, product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_update_by_owner_seller(self):
        self.client.force_authenticate(user=self.seller)
        url = reverse('product_detail', kwargs={'pk': self.product.id})
        response = self.client.patch(url, {"price": "599.99"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(float(response.data['data']['price']), 599.99)

    def test_product_update_fails_for_non_owner_seller(self):
        self.client.force_authenticate(user=self.other_seller)
        url = reverse('product_detail', kwargs={'pk': self.product.id})
        response = self.client.patch(url, {"price": "599.99"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_filtering_and_searching(self):
        # Create second product
        Product.objects.create(
            seller=self.other_seller,
            category=self.other_category,
            name="Django Cookbook",
            details="Learn Django the right way.",
            price=39.99,
            stock=100
        )
        url = reverse('product_list_create')

        # Filter by Category
        response = self.client.get(f"{url}?category={self.other_category.id}", format='json')
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "Django Cookbook")

        # Filter by Seller
        response = self.client.get(f"{url}?seller={self.seller.id}", format='json')
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "Smartphone")

        # Search by Name
        response = self.client.get(f"{url}?search=smart", format='json')
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "Smartphone")

    def test_product_creation_with_image_by_seller(self):
        self.client.force_authenticate(user=self.seller)
        url = reverse('product_list_create')

        product_data = {
            "category": self.category.id,
            "name": "Tablet",
            "details": "A portable tablet.",
            "price": "299.99",
            "stock": 20,
            "uploaded_images": [_dummy_image()]
        }
        response = self.client.post(url, product_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], "Tablet")
        self.assertGreater(len(response.data['data']['images']), 0)
        self.assertEqual(response.data['data']['images'][0]['is_primary'], True)
        self.assertIn('id', response.data['data']['images'][0])
        self.assertIn('image', response.data['data']['images'][0])
        self.assertIn('order', response.data['data']['images'][0])

    def test_product_append_image_on_update(self):
        ProductImage.objects.create(
            product=self.product,
            image=_dummy_image("initial.gif"),
            is_primary=True,
            order=0
        )
        self.client.force_authenticate(user=self.seller)
        url = reverse('product_detail', kwargs={'pk': self.product.id})
        response = self.client.patch(
            url,
            {"uploaded_images": [_dummy_image("appended.gif")]},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        images = response.data['data']['images']
        self.assertEqual(len(images), 2)
        self.assertEqual(images[0]['is_primary'], True)
        self.assertEqual(images[1]['is_primary'], False)

    def test_product_delete_image_on_update(self):
        first = ProductImage.objects.create(
            product=self.product,
            image=_dummy_image("first.gif"),
            is_primary=True,
            order=0
        )
        second = ProductImage.objects.create(
            product=self.product,
            image=_dummy_image("second.gif"),
            is_primary=False,
            order=1
        )
        self.client.force_authenticate(user=self.seller)
        url = reverse('product_detail', kwargs={'pk': self.product.id})
        response = self.client.patch(
            url,
            {"delete_image_ids": [first.id]},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        images = response.data['data']['images']
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['id'], second.id)
        self.assertEqual(images[0]['is_primary'], True)

    def test_product_list_includes_primary_image(self):
        ProductImage.objects.create(
            product=self.product,
            image=_dummy_image(),
            is_primary=True,
            order=0
        )
        url = reverse('product_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product_data = response.data['data'][0]
        self.assertIn('primary_image', product_data)
        self.assertIsNotNone(product_data['primary_image'])
        self.assertNotIn('images', product_data)

    def test_product_detail_nested_images(self):
        ProductImage.objects.create(
            product=self.product,
            image=_dummy_image(),
            is_primary=True,
            order=0
        )
        url = reverse('product_detail', kwargs={'pk': self.product.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        images = response.data['data']['images']
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['is_primary'], True)
        self.assertIn('id', images[0])
        self.assertIn('image', images[0])
        self.assertIn('order', images[0])

    def test_product_dropdown_endpoint(self):
        url = reverse('product_dropdown_list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], "Smartphone")
        self.assertNotIn('price', response.data['data'][0])

    def test_product_dropdown_excludes_soft_deleted(self):
        self.product.delete()
        url = reverse('product_dropdown_list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)

    def test_soft_delete_model_behavior(self):
        # Initial state: not deleted, timestamps set
        self.assertFalse(self.product.is_deleted)
        self.assertIsNone(self.product.deleted_at)
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)

        # Call delete()
        self.product.delete()
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_deleted)
        self.assertIsNotNone(self.product.deleted_at)

        # Undo delete
        self.product.is_deleted = False
        self.product.save()
        self.assertIsNone(self.product.deleted_at)

    def test_soft_delete_via_api(self):
        self.client.force_authenticate(user=self.seller)
        url = reverse('product_detail', kwargs={'pk': self.product.id})
        
        # Delete via API
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify it still exists in the database but is soft deleted
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_deleted)
        self.assertIsNotNone(self.product.deleted_at)

        # Buyer listing API should not return it
        self.client.force_authenticate(user=self.buyer)
        list_url = reverse('product_list_create')
        list_resp = self.client.get(list_url, format='json')
        self.assertEqual(len(list_resp.data['data']), 0)

        # Buyer detail API should return 404
        detail_resp = self.client.get(url, format='json')
        self.assertEqual(detail_resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_fails_for_soft_deleted_product(self):
        from orders.models import Address, Cart, CartItem
        # Create an address
        address = Address.objects.create(
            user=self.buyer,
            address_line1="123 Main St",
            city="Metropolis",
            state="NY",
            postal_code="10001",
            country="USA"
        )
        
        # Soft delete the product
        self.product.delete()

        # Try to place order directly
        self.client.force_authenticate(user=self.buyer)
        order_url = reverse('order_list_create')
        order_data = {
            "shipping_address": address.id,
            "items": [
                {"product": self.product.id, "quantity": 1}
            ]
        }
        response = self.client.post(order_url, order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no longer available", str(response.data))

        # Try to place order via cart
        cart = Cart.objects.create(user=self.buyer)
        # Note: bypassing validation to add to cart to simulate pre-deleted items in cart
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        order_data_cart = {
            "shipping_address": address.id,
            "cart_id": cart.id
        }
        response = self.client.post(order_url, order_data_cart, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no longer available", str(response.data))

    def test_review_fails_for_soft_deleted_product(self):
        self.product.delete()
        self.client.force_authenticate(user=self.buyer)
        review_url = reverse('review_list_create')
        review_data = {
            "product": self.product.id,
            "rating": 5,
            "comment": "Nice product!"
        }
        response = self.client.post(review_url, review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot review a deleted product", str(response.data))

