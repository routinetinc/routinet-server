from django.shortcuts import render
from supplyAuth.models import User

# Create your views here.
user = User.objects.create_user('username', 'foo@example.com', 'password')