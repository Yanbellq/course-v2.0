import jwt
from django.test import TestCase
from django.conf import settings
from unittest.mock import patch

from apps.api.authentication.user_jwt_authentication import MongoJWTAuthentication


class DummyRequest:
    def __init__(self, token=None):
        self.headers = {}
        self.COOKIES = {}
        if token:
            self.headers['Authorization'] = f'Bearer {token}'


def make_token(payload: dict):
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


class MongoJWTAuthTests(TestCase):

    def test_missing_user_returns_none(self):
        """Если токен указывает на неіснуючого користувача — authenticate має повернути None"""
        token = make_token({'user_id': '507f1f77bcf86cd799439011'})
        req = DummyRequest(token=token)

        with patch('apps.main.models.User.find_by_id', return_value=None):
            auth = MongoJWTAuthentication()
            result = auth.authenticate(req)
            self.assertIsNone(result)

    def test_invalid_token_raises_auth_failed(self):
        """Невірний токен — має підніматися AuthenticationFailed"""
        req = DummyRequest(token="not.a.valid.token")
        auth = MongoJWTAuthentication()

        from rest_framework.exceptions import AuthenticationFailed
        with self.assertRaises(AuthenticationFailed):
            auth.authenticate(req)
