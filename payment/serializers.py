from rest_framework import serializers
from routine.fields import CustomSerializers


class CreatePayment(serializers.Serializer):
    amount    = serializers.IntegerField(max_value=10000, min_value=0)