import stripe
from rest_framework.views import APIView
from routine.utils.handle_json import RequestInvalid, get_json, make_response
from payment import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import secret

# Stripe のシークレットキーを設定
stripe.api_key = secret.StripeAPI.SECRET_KEY

@method_decorator(csrf_exempt, name='dispatch')  # Stripe 決済システムと連携のため CSRF 保護を無効化
class CreatePayment(APIView):
    def post(self, request, format=None):
        try:
            datas: dict = get_json(request, serializers.CreatePayment)
        except RequestInvalid:
            return make_response(status_code=400)
        try:
            # フロントエンドから送信された支払い金額を取得
            payment_amount = datas['amount']

            # Stripeの支払いインテントを作成
            payment_intent = stripe.PaymentIntent.create(
                amount=payment_amount,
                currency='usd',
                payment_method_types=['card']
            )

            # 支払いインテントのクライアントシークレットを返す
            data = {'client_secret': payment_intent.client_secret}
            return make_response(data = data)

        except Exception as e:
            return make_response(500, {'error': str(e)})
    
'''
class サブスクプラン
  (id(userと1対多), 元値, 割引率)
class User
  (サブスクid)
'''