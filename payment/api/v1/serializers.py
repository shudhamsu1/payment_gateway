from rest_framework import serializers


class CardDetailSerializer(serializers.Serializer):
    card_number = serializers.CharField(required=True)
    card_holder = serializers.CharField(required=True)
    card_exp_month = serializers.CharField(required=True)
    card_exp_year = serializers.CharField(required=True)
    card_cvv = serializers.CharField(required=True)
    amount = serializers.IntegerField(help_text="Provide amount in cents", required=True)


class BankDetailSerializer(serializers.Serializer):
    country = serializers.CharField(required=True)
    currency = serializers.CharField(required=True)
    account_holder_name = serializers.CharField(required=True)
    account_holder_type = serializers.CharField(required=True)
    routing_number = serializers.CharField(required=True)
    account_number = serializers.CharField(required=True)
    amount = serializers.IntegerField(help_text="Provide amount in cents", required=True)



