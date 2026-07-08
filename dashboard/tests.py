from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

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
