from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Category, Product
from reviews.models import Review

User = get_user_model()

class ReviewTests(APITestCase):

    def setUp(self):
        # Create users
        self.seller = User.objects.create_user(
            username="seller_user",
            email="seller@example.com",
            password="testpassword",
            role="Seller"
        )
        self.buyer1 = User.objects.create_user(
            username="buyer1",
            email="buyer1@example.com",
            password="testpassword",
            role="Buyer"
        )
        self.buyer2 = User.objects.create_user(
            username="buyer2",
            email="buyer2@example.com",
            password="testpassword",
            role="Buyer"
        )

        # Product
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            seller=self.seller,
            category=self.category,
            name="Smartphone",
            details="A premium smartphone.",
            price=500.00,
            stock=10
        )

    def test_view_reviews_accessible_by_everyone(self):
        # Create a review
        Review.objects.create(buyer=self.buyer1, product=self.product, rating=4, comment="Good product")
        
        url = reverse('review_list_create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)

    def test_create_review_by_buyer(self):
        self.client.force_authenticate(user=self.buyer1)
        url = reverse('review_list_create')
        review_data = {
            "product": self.product.id,
            "rating": 5,
            "comment": "Perfect phone!"
        }
        response = self.client.post(url, review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['rating'], 5)

    def test_create_review_invalid_rating(self):
        self.client.force_authenticate(user=self.buyer1)
        url = reverse('review_list_create')
        
        # Rating too high
        response = self.client.post(url, {"product": self.product.id, "rating": 6, "comment": "Okay"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Rating too low
        response = self.client.post(url, {"product": self.product.id, "rating": 0, "comment": "Okay"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_fails_for_seller(self):
        self.client.force_authenticate(user=self.seller)
        url = reverse('review_list_create')
        response = self.client.post(url, {"product": self.product.id, "rating": 5, "comment": "Self rating"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review_by_owner_buyer(self):
        review = Review.objects.create(buyer=self.buyer1, product=self.product, rating=4, comment="Initial comment")
        self.client.force_authenticate(user=self.buyer1)
        url = reverse('review_detail', kwargs={'pk': review.id})
        response = self.client.patch(url, {"rating": 5, "comment": "Updated comment"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Updated comment")

    def test_update_review_fails_for_other_buyer(self):
        review = Review.objects.create(buyer=self.buyer1, product=self.product, rating=4, comment="Initial comment")
        self.client.force_authenticate(user=self.buyer2)
        url = reverse('review_detail', kwargs={'pk': review.id})
        response = self.client.patch(url, {"rating": 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_average_rating_calculation(self):
        # Add reviews
        Review.objects.create(buyer=self.buyer1, product=self.product, rating=5, comment="Excellent")
        Review.objects.create(buyer=self.buyer2, product=self.product, rating=3, comment="Average")

        # Fetch product details
        url = reverse('product_detail', kwargs={'pk': self.product.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Average is (5 + 3) / 2 = 4.0
        self.assertEqual(response.data['data']['average_rating'], 4.0)
