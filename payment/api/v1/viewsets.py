import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from djstripe.models import Customer
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from payment.api.v1.serializers import CardDetailSerializer,BankDetailSerializer
from payment.models import ErrorLog
from django.views.generic import TemplateView
from django.shortcuts import render
from rest_framework.renderers import TemplateHTMLRenderer

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
User = get_user_model()

# class HomePageView(TemplateView):
#     template_name = 'home.html'
    
#     def get_context_data(self, **kwargs): #new
#         context = super().get_context_data(**kwargs)
#         context['key'] = settings.STRIPE_PUBLIC_SECRET_KEY
#         return context
 
 
 
 
 
 
class AddCash(ListCreateAPIView):
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'home.html'
    
    serializer_class = CardDetailSerializer
    queryset = User.objects.none

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            serializer = CardDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            try:
                token = stripe.Token.create(
                    card={
                        "number": data.get("card_number"),
                        "exp_month": data.get("card_exp_month"),
                        "exp_year": data.get("card_exp_year"),
                        "cvc": data.get("card_cvv")
                    }, )
                try:
                    customer = Customer.objects.get(subscriber=request.user)
                except Customer.DoesNotExist:
                    customer = Customer.create(subscriber=request.user)
                    customer.save()
                print(customer.default_payment_method)
                try:
                    payment_method = stripe.PaymentMethod.create(
                        type="card",
                        card={"token": token.id},
                    )

                    customer.add_payment_method(
                        payment_method=payment_method.id, set_default=True)
                    customer.save()
                    customer.api_retrieve()
                except stripe.error.CardError as e:
                    print(e)
                try:
                    pi = stripe.PaymentIntent.create(
                        amount=int(data.get("amount")),
                        currency="usd",
                        payment_method_types=["card"],
                        customer=customer.id,
                        description='Added cash',
                    )
                    stripe.PaymentIntent.confirm(
                        pi.id,
                        payment_method=customer.payment_methods.first().id,
                    )
                    if pi.id:
                        try:
                            amount = data.get("amount") / 100
                            user.amount += amount
                            user.save()
                        except Exception as e:
                            ErrorLog.objects.create(error=e)
                    return Response(status=status.HTTP_200_OK, data={
                        "ok": True,
                        "error": None,
                    })
                except Exception as err:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={
                        "ok": False,
                        "error": str(err),
                    })
            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    "ok": False,
                    "error": err.get('type'),
                    "message": err.get('message')
                })
            except Exception as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={
                    "ok": False,
                    "error": "Server Error",
                    "message": f"Invalid Card Detail {e}"
                })
        return Response({"error": "Please login first."}, status=status.HTTP_403_FORBIDDEN)
        # return render(request, 'templates/home.html')

class BankDetailViewSet(ListCreateAPIView):
    serializer_class = BankDetailSerializer
    queryset = User.objects.none

    def get(self, request, *args, **kwargs):
        return Response()

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            serializer = BankDetailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            try:
                token = stripe.Token.create(
                    bank_account={
                        "country": data.get('country'),
                        "currency": data.get('currency'),
                        "account_holder_name": data.get('account_holder_name'),
                        "account_holder_type": data.get('account_holder_type'),
                        "routing_number": data.get('routing_number'),
                        "account_number": data.get('account_number'),
                    },
                )
                try:
                    customer = Customer.objects.get(subscriber=request.user)
                except Customer.DoesNotExist:
                    customer = Customer.create(subscriber=request.user)
                    customer.save()
                # print(customer.default_payment_method)
                # try:
                #     payment_method = stripe.PaymentMethod.create(
                #         type="bank_account",
                #         bank_account={"token": token.id},
                #     )
                #
                #     customer.add_payment_method(
                #         payment_method=payment_method.id, set_default=True)
                #     customer.save()
                #     customer.api_retrieve()
                # except stripe.error.CardError as e:
                #     print(e)
                try:
                    pi = stripe.PaymentIntent.create(
                        amount=int(data.get("amount")),
                        currency=data.get('currency'),
                        payment_method_types=["bank_account"],
                        customer=customer.id,
                        description='Added cash',
                    )
                    stripe.PaymentIntent.confirm(
                        pi.id,
                        payment_method="bank_account"
                    )
                    # if pi.id:
                    #     try:
                    #         amount = data.get("amount") / 100
                    #         user.amount += amount
                    #         user.save()
                    #         # credit_setting = CreditsSetting.objects.first()
                    #         # if credit_setting:
                    #         #     user.credits += int(credit_setting.credits * amount)
                    #     except Exception as e:
                    #         ErrorLog.objects.create(error=e)
                    return Response(status=status.HTTP_200_OK, data={
                        "ok": True,
                        "error": None,
                        "amount": user.amount
                    })
                except Exception as err:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={
                        "ok": False,
                        "error": str(err),
                    })
            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    "ok": False,
                    "error": err.get('type'),
                    "message": err.get('message')
                })
            except Exception as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={
                    "ok": False,
                    "error": "Server Error",
                    "message": f"Invalid Card Detail {e}"
                })
        return Response({"error": "Please login first."}, status=status.HTTP_403_FORBIDDEN)





