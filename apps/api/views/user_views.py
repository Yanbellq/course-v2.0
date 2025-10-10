# apps/api/user_views.py
import secrets

from bson import ObjectId
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.customers.models import Customer
from apps.suppliers.models import Supplier
from apps.products.models import Product


@api_view(['POST'])
@permission_classes([AllowAny])
def customer_registration(request):
    try:
        data = json.loads(request.body)

        # Перевірка наявності обов'язкових полів
        if not all([data.get('username'), data.get('email'), data.get('password')]):
            return JsonResponse({'status': 'error', 'message': 'Всі поля (ім\'я користувача, електронна пошта, пароль) є обов\'язковими'}, status=400)

        # Перевірка наявності клієнта з таким ім'ям користувача або електронною поштою
        if Customer.objects(username=data.get('username')).count() > 0:
            return JsonResponse({'status': 'error', 'message': 'Ім\'я користувача вже зайняте'}, status=400)
        if Customer.objects(email=data.get('email')).count() > 0:
            return JsonResponse({'status': 'error', 'message': 'Електронна пошта вже зареєстрована'}, status=400)

        while True:
            token = secrets.token_urlsafe(16)
            if Customer.objects(token=token).count() == 0:
                break

        hashed_password = make_password(data.get('password'))

        customer = Customer(
            username=data.get('username'),
            email=data.get('email'),
            password=hashed_password,
            token=token,
        )
        customer.save()
        return JsonResponse({'status': 'success', 'message': 'Реєстрація успішна!', 'token': token }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Некоректний формат JSON'}, status=400)
