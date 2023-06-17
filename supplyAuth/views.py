from django.shortcuts import render

# Create your views here.
user = User.objects.create_user('username', 'foo@example.com', 'password')