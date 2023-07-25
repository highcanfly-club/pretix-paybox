# Register your receivers here
# Register your receivers here
from django.dispatch import receiver
from django.http import HttpRequest, HttpResponse
from django.urls import resolve
from pretix.base.signals import register_payment_providers


@receiver(register_payment_providers, dispatch_uid="payment_paybox")
def register_payment_provider(sender, **kwargs):
    from .payment import PayboxPayment

    return PayboxPayment

