from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from authentication.models import BuyerProfile, PasswordResetToken

User = get_user_model()

class AuthenticationTests(APITestCase):

    def setUp(self):
        self.buyer_data = {
            "username": "buyer_user",
            "email": "buyer@example.com",
            "password": "securepassword123"
        }
        self.seller_data = {
            "username": "seller_user",
            "email": "seller@example.com",
            "password": "securepassword123"
        }

    def test_buyer_registration(self):
        url = reverse('buyer_register')
        response = self.client.post(url, self.buyer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['role'], 'Buyer')
        self.assertEqual(response.data['data']['username'], self.buyer_data['username'])

    def test_buyer_registration_with_phone_number_success_and_uniqueness(self):
        url = reverse('buyer_register')
        data = self.buyer_data.copy()
        data['phone_number'] = "+1234567890"
        
        # Register first user
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=data['username'])
        self.assertEqual(user.phone_number, "+1234567890")
        
        # Try registering another user with the same phone number
        data2 = {
            "username": "buyer_user_2",
            "email": "buyer2@example.com",
            "password": "securepassword123",
            "phone_number": "+1234567890"
        }
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response2.data['success'])
        self.assertIn('phone_number', response2.data['errors'])

    def test_buyer_registration_delete_and_reregister(self):
        url_register = reverse('buyer_register')
        url_profile = reverse('profile')
        
        data = self.buyer_data.copy()
        data['phone_number'] = "+1234567890"
        
        # 1. Register user
        response = self.client.post(url_register, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Log in user to get credentials
        url_login = reverse('login')
        login_resp = self.client.post(url_login, {"username": data['username'], "password": data['password']}, format='json')
        access_token = login_resp.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 3. Delete user
        delete_resp = self.client.delete(url_profile, format='json')
        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)
        
        # Clear credentials
        self.client.credentials()
        
        # 4. Register a different user with the same phone number
        data2 = {
            "username": "buyer_user_2",
            "email": "buyer2@example.com",
            "password": "securepassword123",
            "phone_number": "+1234567890"
        }
        response2 = self.client.post(url_register, data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        user2 = User.objects.get(username="buyer_user_2")
        self.assertEqual(user2.phone_number, "+1234567890")

    def test_seller_registration(self):
        url = reverse('seller_register')
        response = self.client.post(url, self.seller_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['role'], 'Seller')
        self.assertEqual(response.data['data']['username'], self.seller_data['username'])

    def test_login_success(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            role="Buyer"
        )
        url = reverse('login')
        response = self.client.post(url, {"username": "testuser", "password": "testpassword"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['user']['username'], 'testuser')

    def test_profile_retrieval(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            role="Buyer"
        )
        self.client.force_authenticate(user=user)
        url = reverse('profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['username'], 'testuser')

    def test_logout_blacklists_token(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            role="Buyer"
        )
        login_url = reverse('login')
        login_resp = self.client.post(login_url, {"username": "testuser", "password": "testpassword"}, format='json')
        refresh_token = login_resp.data['data']['refresh']
        access_token = login_resp.data['data']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_url = reverse('logout')
        response = self.client.post(logout_url, {"refresh": refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # Try to use refresh token again
        refresh_url = reverse('token_refresh')
        refresh_resp = self.client.post(refresh_url, {"refresh": refresh_token}, format='json')
        self.assertEqual(refresh_resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(refresh_resp.data['success'])

    def test_profile_deletion(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            role="Buyer"
        )
        self.client.force_authenticate(user=user)
        url = reverse('profile')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_user_soft_delete_details(self):
        # 1. Register a user with a unique phone number
        url_register = reverse('buyer_register')
        reg_data = {
            "username": "unique_username",
            "email": "unique@example.com",
            "password": "securepassword123",
            "phone_number": "+9998887777"
        }
        response = self.client.post(url_register, reg_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="unique@example.com")
        self.assertFalse(user.is_deleted)
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.buyer_profile)
        self.assertEqual(user.phone_number, "+9998887777")
        self.assertFalse(user.buyer_profile.is_deleted)

        # 2. Delete user
        self.client.force_authenticate(user=user)
        url_profile = reverse('profile')
        delete_resp = self.client.delete(url_profile, format='json')
        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)

        # 3. Check active objects don't return them, but all_with_deleted does
        self.assertFalse(User.objects.filter(id=user.id).exists())
        self.assertFalse(BuyerProfile.objects.filter(id=user.buyer_profile.id).exists())

        deleted_user = User.objects.all_with_deleted().get(id=user.id)
        self.assertTrue(deleted_user.is_deleted)
        self.assertFalse(deleted_user.is_active)
        self.assertIn("unique_username_deleted_", deleted_user.username)
        self.assertIn("unique_deleted_", deleted_user.email)

        deleted_profile = BuyerProfile.objects.all_with_deleted().get(id=user.buyer_profile.id)
        self.assertTrue(deleted_profile.is_deleted)

        # 4. Try re-registering with the exact same original details
        self.client.credentials()  # Clear auth
        response2 = self.client.post(url_register, reg_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        new_user = User.objects.get(email="unique@example.com")
        self.assertEqual(new_user.username, "unique_username")
        self.assertEqual(new_user.phone_number, "+9998887777")

    def test_password_reset_flow_success(self):
        # Create user
        user = User.objects.create_user(
            username="reset_user",
            email="reset@example.com",
            password="oldpassword123",
            role="Buyer"
        )
        # Request reset
        url_request = reverse('password_reset_request')
        response = self.client.post(url_request, {"email": "reset@example.com"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify token created in DB
        reset_token = PasswordResetToken.objects.filter(user=user).first()
        self.assertIsNotNone(reset_token)
        self.assertFalse(reset_token.is_used)
        
        # Confirm reset
        url_confirm = reverse('password_reset_confirm')
        confirm_data = {
            "token": reset_token.token,
            "password": "newpassword123"
        }
        response_confirm = self.client.post(url_confirm, confirm_data, format='json')
        self.assertEqual(response_confirm.status_code, status.HTTP_200_OK)
        self.assertTrue(response_confirm.data['success'])
        
        # Verify token is now marked as used
        reset_token.refresh_from_db()
        self.assertTrue(reset_token.is_used)
        
        # Verify user password is changed (can login with new password)
        url_login = reverse('login')
        response_login = self.client.post(url_login, {"username": "reset_user", "password": "newpassword123"}, format='json')
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)

    def test_password_reset_request_nonexistent_email(self):
        # Request reset for email not in system
        url_request = reverse('password_reset_request')
        response = self.client.post(url_request, {"email": "nonexistent@example.com"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        # Assert no token created
        self.assertEqual(PasswordResetToken.objects.count(), 0)

    def test_password_reset_confirm_invalid_token(self):
        url_confirm = reverse('password_reset_confirm')
        response = self.client.post(url_confirm, {"token": "invalidtoken123", "password": "newpassword123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_password_reset_confirm_expired_token(self):
        user = User.objects.create_user(
            username="expired_reset",
            email="expired@example.com",
            password="oldpassword123",
            role="Buyer"
        )
        # Create an expired token manually
        from django.utils import timezone
        from datetime import timedelta
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token="expired_token_val",
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        
        url_confirm = reverse('password_reset_confirm')
        response = self.client.post(url_confirm, {"token": "expired_token_val", "password": "newpassword123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_password_reset_confirm_reused_token(self):
        user = User.objects.create_user(
            username="reused_reset",
            email="reused@example.com",
            password="oldpassword123",
            role="Buyer"
        )
        from django.utils import timezone
        from datetime import timedelta
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token="reused_token_val",
            is_used=True,
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        
        url_confirm = reverse('password_reset_confirm')
        response = self.client.post(url_confirm, {"token": "reused_token_val", "password": "newpassword123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_password_reset_confirm_weak_password(self):
        user = User.objects.create_user(
            username="weak_reset",
            email="weak@example.com",
            password="oldpassword123",
            role="Buyer"
        )
        from django.utils import timezone
        from datetime import timedelta
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token="weak_token_val",
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        
        url_confirm = reverse('password_reset_confirm')
        response = self.client.post(url_confirm, {"token": "weak_token_val", "password": "123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn("password", response.data['errors'])

    def test_password_reset_invalidates_existing_tokens(self):
        user = User.objects.create_user(
            username="jwt_reset",
            email="jwt_reset@example.com",
            password="oldpassword123",
            role="Buyer"
        )
        
        # 1. Login to generate refresh token
        url_login = reverse('login')
        response_login = self.client.post(url_login, {"username": "jwt_reset", "password": "oldpassword123"}, format='json')
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        refresh_token = response_login.data['data']['refresh']
        
        # 2. Verify we can use this refresh token successfully before reset
        url_refresh = reverse('token_refresh')
        response_refresh_before = self.client.post(url_refresh, {"refresh": refresh_token}, format='json')
        self.assertEqual(response_refresh_before.status_code, status.HTTP_200_OK)
        
        # 3. Create reset token and complete reset flow
        from django.utils import timezone
        from datetime import timedelta
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token="jwt_token_val",
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        url_confirm = reverse('password_reset_confirm')
        response_confirm = self.client.post(url_confirm, {"token": "jwt_token_val", "password": "newpassword123"}, format='json')
        self.assertEqual(response_confirm.status_code, status.HTTP_200_OK)
        
        # 4. Attempt to use old refresh token to verify it fails
        response_refresh_after = self.client.post(url_refresh, {"refresh": refresh_token}, format='json')
        self.assertEqual(response_refresh_after.status_code, status.HTTP_401_UNAUTHORIZED)




