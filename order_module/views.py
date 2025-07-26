import json
from django.conf import settings
import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from jdatetime import datetime

from account_module.models import User
from .forms import CheckOutForm
from .models import OrderCheckout

from order_module.models import Order, OrderDetail
from product_module.models import Product

class ZarinPal:
    BASE_URLS = {
        "sandbox": "https://sandbox.zarinpal.com/pg/v4",
        "main": "https://payment.zarinpal.com/pg/v4"
    }

    def __init__(self, merchant_id: str, callback_url: str, sandbox: bool = False):
        self.merchant_id = merchant_id
        self.mode = "sandbox" if sandbox else "main"
        self.base_url = self.BASE_URLS[self.mode]

        self._payment_request_url = f"{self.base_url}/payment/request.json"
        self._payment_verify_url = f"{self.base_url}/payment/verify.json"
        self._payment_page_url = f"{self.base_url.replace('/v4', '')}/StartPay/"

        self._callback_url = callback_url

    def payment_request(self, amount: int, description: str = "پرداختی کاربر") -> dict:
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "callback_url": self._callback_url,
            "description": description,
            "currency": "IRT"
        }
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        response = requests.post(self._payment_request_url, headers=headers, json=payload)
        json_response = response.json()
        if isinstance(json_response, dict):
            return json_response
        else:
            return json_response

    def payment_verify(self, amount: int, authority: str) -> dict:
        payload = {"merchant_id": self.merchant_id, "amount": amount, "authority": authority}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        response = requests.post(self._payment_verify_url, headers=headers, json=payload)
        json_response = response.json()
        if isinstance(json_response, dict):
            return json_response
        else:
            return json_response

    def generate_payment_url(self, authority: str) -> str:
        return f"{self._payment_page_url}{authority}"

# استفاده از کلاس ZarinPal در ویوها
if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
phone = '09117511811'
CallbackURL = 'http://127.0.0.1:8000/order/verify'

def request_payment(request):
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_order.total_amount

    if total_price == 0:
        return redirect(reverse('user:cart'))

    zarinpal = ZarinPal(settings.MERCHANT, CallbackURL, sandbox=settings.SANDBOX)
    response = zarinpal.payment_request(total_price, description)

    if response.get('data'):
        url = zarinpal.generate_payment_url(response['data']['authority'])
        return redirect(url)
    else:
        return JsonResponse({'status': False, 'code': response})


def verify_payment(request):
    authority = request.GET['Authority']
    status = request.GET['Status']
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_order.calculate_total_price()
    user = User.objects.filter(id=request.user.id).first()

    zarinpal = ZarinPal(settings.MERCHANT, CallbackURL, sandbox=settings.SANDBOX)
    response = zarinpal.payment_verify(total_price, authority)

    if status == "OK":
        current_order.is_paid = True
        user.order_count += 1
        user.total_buy += total_price

        user.save()
        current_order.save()
        return redirect(reverse('order:secces_payment_redirect'))

    return redirect(reverse('order:unsecces_payment_redirect'))



def add_product_to_order(request):
    product_id = int(request.GET.get('product_id'))
    count = int(request.GET.get('count'))

    if count < 1:
        return JsonResponse({
            'status': 'invalid count'
        })

    if request.user.is_authenticated:
        product = Product.objects.filter(id=product_id, is_active=True).first()
        product.count -= 1
        product.save()
        if product is not None:
            current_order, created = Order.objects.get_or_create(user_id=request.user.id, is_paid=False)
            current_order.total_amount += product.price
            current_order.save()
            current_order_detail = current_order.orderdetail_set.filter(product_id=product_id).first()
            if current_order_detail is not None:
                current_order_detail.count += count
                current_order_detail.save()
            else:
                new_detail = OrderDetail(order_id=current_order.id, product_id=product_id, count=count)
                new_detail.save()
            return JsonResponse({
                'status': 'success'
            })


        else:
            return JsonResponse({
                'status': 'not found product'
            })
    else:
        return JsonResponse({
            'status': 'user is not login',
        })


class CheckOutView(View):
    def get(self, request):
        checkout_form = CheckOutForm()
        current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(
            user_id=request.user.id,
            is_paid=False)

        total = current_order.total_amount
        return render(request, "checkout.html", context={
            'order': current_order,
            'sum': total,
            'checkout_form': checkout_form
        })

    def post(self, request):
        checkout_form = CheckOutForm(request.POST)
        if checkout_form.is_valid():
            new_checkout: OrderCheckout = OrderCheckout()

            new_checkout.user = request.user
            new_checkout.order = Order.objects.filter(user=request.user).first()
            new_checkout.first_name = checkout_form.cleaned_data.get('first_name')
            new_checkout.last_name = checkout_form.cleaned_data.get('last_name')
            new_checkout.state = checkout_form.cleaned_data.get('state')
            new_checkout.city = checkout_form.cleaned_data.get('city')
            new_checkout.street = checkout_form.cleaned_data.get('street')
            new_checkout.apartment = checkout_form.cleaned_data.get('apartment')
            new_checkout.zipcode = checkout_form.cleaned_data.get('zipcode')
            new_checkout.phone = checkout_form.cleaned_data.get('phone')
            new_checkout.sended = False

            new_checkout.save()
            return redirect(reverse('order:request_payment'))
        else:
            checkout_form.add_error('phone', 'مشکلی در پرداخت پیش اومده')

        return render(request, "checkout.html", context={
            'checkout_form': checkout_form,
            'sum': 0
        })


def secces_payment_redirect(request):
    return render(request, "seccess_payment.html", context={})


def unsecces_payment_redirect(request):
    return render(request, "unseccess_payment.html", context={})
