import sys
from collections import OrderedDict
from django import forms
from django.http import HttpRequest
from django.template.loader import get_template
from django.utils.crypto import get_random_string
from django.utils.translation import get_language, gettext_lazy as _, to_locale
from i18nfield.strings import LazyI18nString
from pretix.base.models import OrderPayment
from pretix.base.payment import BasePaymentProvider


def getNonce(request):
    if "_paybox_nonce" not in request.session:
        request.session["_paybox_nonce"] = get_random_string(32)
    return request.session["_paybox_nonce"]


class PayboxPayment(BasePaymentProvider):
    identifier = "payboxpayment"
    verbose_name = _("Paybox Payment")
    abort_pending_allowed = True

    @property
    def test_mode_message(self):
        return _(
            "In test mode, you can just manually mark this order as paid in the backend after it has been "
            "created."
        )

    @property
    def settings_form_fields(self):
        fields = [
            ('endpoint',
                forms.ChoiceField(
                    label=_('Endpoint'),
                    initial='sandbox',
                    choices=(
                        ('live', _('Live')),
                        ('sandbox', _('Sandbox')),
                     ),
                 )),
            (
                "production_secret",
                forms.CharField(
                    label=_("Paybox production HMAC"),
                    max_length=128,
                    min_length=128,
                    help_text=_("The production HMAC key"),
                ),
            ),
            (
                "sandbox_secret",
                forms.CharField(
                    label=_("Paybox sandbox HMAC"),
                    max_length=128,
                    min_length=128,
                    help_text=_("The sandbox HMAC key"),
                ),
            ),
            (
                "paybox_site",
                forms.CharField(
                    label=_("Paybox site"),
                    max_length=8,
                    min_length=6,
                    help_text=_(
                        "This is the Paybox site ID"
                    ),
                ),
            ),
            (
                "paybox_rank",
                forms.CharField(
                    label=_("Paybox rank"),
                    max_length=2,
                    min_length=2,
                    help_text=_(
                        "This is the two characters rank ID"
                    ),
                ),
            ),
            (
                "paybox_id",
                forms.CharField(
                    label=_("Paybox identifier"),
                    max_length=9,
                    min_length=1,
                    help_text=_(
                        "This is the main Paybox ID"
                    ),
                ),
            ),
        ]
        return OrderedDict(fields + list(super().settings_form_fields.items()))

    def payment_form_render(self, request) -> str:
        print("PayboxPayment.payment_form_render", file=sys.stderr)
        ctx = {}
        template = get_template("pretix_paybox/prepare.html")
        return template.render(ctx)

    def checkout_prepare(self, request, cart):
        print("PayboxPayment.checkout_prepare", file=sys.stderr)
        return True

    def payment_prepare(
        self, request: HttpRequest, payment: OrderPayment
    ) -> bool | str:
        print("PayboxPayment.payment_prepare", file=sys.stderr)
        return True

    def payment_is_valid_session(self, request):
        print("PayboxPayment.payment_is_valid_session", file=sys.stderr)
        return True

    def execute_payment(self, request: HttpRequest, payment: OrderPayment):
        print("PayboxPayment.execute_payment", file=sys.stderr)
        # payment.confirm()

    def get_paybox_locale(self, request):
        languageDjango = get_language()
        localeDjango = to_locale(languageDjango)
        baseLocale = localeDjango[0:2]
        subLocale = localeDjango[3:5].upper()
        if subLocale == "":
            subLocale = baseLocale.upper()
        locale = "{}-{}".format(baseLocale, subLocale)
        return locale

    def checkout_confirm_render(self, request):
        print("PayboxPayment.checkout_confirm_render", file=sys.stderr)
        ctx = {
        }
        template = get_template("pretix_paybox/checkout_payment_form.html")
        return template.render(ctx)

    def order_pending_mail_render(self, order) -> str:
        print("PayboxPayment.order_pending_mail_render", file=sys.stderr)
        template = get_template("pretix_paybox/email/order_pending.txt")
        ctx = {
        }
        return template.render(ctx)

    def payment_pending_render(self, request: HttpRequest, payment: OrderPayment):
        print("PayboxPayment.payment_pending_render", file=sys.stderr)
        template = get_template("pretix_paybox/pending.html")
        ctx = {
        }
        return template.render(ctx)

    def payment_control_render(self, request: HttpRequest, payment: OrderPayment):
        print("PayboxPayment.payment_control_render", file=sys.stderr)
        template = get_template("pretix_paybox/control.html")
        ctx = {
        }
        return template.render(ctx)
