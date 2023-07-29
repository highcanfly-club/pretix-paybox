import sys
from collections import OrderedDict
from decimal import Decimal
from django import forms
from django.http import HttpRequest
from django.forms import Form
from django.template.loader import get_template
from django.utils.crypto import get_random_string
from django.utils.translation import get_language, gettext_lazy as _, to_locale
from pretix.base.forms.questions import guess_country
from pretix.helpers.countries import CachedCountries
from pretix.base.models import OrderPayment, InvoiceAddress, Order
from pretix.base.payment import BasePaymentProvider
from pretix.presale.views.cart import cart_session
from .Paybox import Transaction


def getNonce(request):
    if "_paybox_nonce" not in request.session:
        request.session["_paybox_nonce"] = get_random_string(32)
    return request.session["_paybox_nonce"]


class PayboxPayment(BasePaymentProvider):
    identifier = "payboxpayment"
    verbose_name = _("Paybox Payment")
    abort_pending_allowed = True
    ia = InvoiceAddress()

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
            ('endoint_production_server',
                forms.CharField(
                    label=_('Production server'),
                    help_text=_("The production server base URL"),
                    initial='https://tpeweb.e-transactions.fr',
                )),
            ('endoint_sandbox_server',
             forms.CharField(
                 label=_('Sandbox server'),
                 help_text=_("The sandbox server base URL"),
                 initial='https://recette-tpeweb.e-transactions.fr',
             )),
            ('endoint_application_path',
             forms.CharField(
                 label=_('Application path'),
                 help_text=_("The path part of the complete URL (server+path)"),
                 initial='/cgi/FramepagepaiementRWD.cgi',
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

    def payment_form_render(self, request: HttpRequest, total: Decimal, order: Order = None) -> str:
        def get_invoice_address():
            if order and getattr(order, 'invoice_address', None):
                request._checkout_flow_invoice_address = order.invoice_address
            if not hasattr(request, '_checkout_flow_invoice_address'):
                cs = cart_session(request)
                iapk = cs.get('invoice_address')
                if not iapk:
                    request._checkout_flow_invoice_address = InvoiceAddress()
                else:
                    try:
                        request._checkout_flow_invoice_address = InvoiceAddress.objects.get(pk=iapk, order__isnull=True)
                    except InvoiceAddress.DoesNotExist:
                        request._checkout_flow_invoice_address = InvoiceAddress()
            return request._checkout_flow_invoice_address

        cs = cart_session(request)
        self.ia = get_invoice_address()
        # print(cs, file=sys.stderr)
        # print(self.ia.name_parts, file=sys.stderr)
        form = self.payment_form(request)
        template = get_template('pretixpresale/event/checkout_payment_form_default.html')
        ctx = {'request': request, 'form': form}
        return template.render(ctx)

    @property
    def payment_form_fields(self):
        print("PayboxPayment.payment_form_fields", file=sys.stderr)
        print(self.ia.name_parts, file=sys.stderr)
        return OrderedDict(
            [
                ('lastname',
                 forms.CharField(
                     label=_('Card Holder Last Name'),
                     required=True,
                     initial=self.ia.name_parts["given_name"],
                 )),
                ('firstname',
                 forms.CharField(
                     label=_('Card Holder First Name'),
                     required=True,
                     initial=self.ia.name_parts["family_name"],
                 )),
                ('line1',
                 forms.CharField(
                     label=_('Card Holder Street'),
                     required=True,
                     initial=self.ia.street,
                 )),
                ('line2',
                 forms.CharField(
                     label=_('Card Holder Address Complement'),
                     required=False,
                 )),
                ('postal_code',
                 forms.CharField(
                     label=_('Card Holder Postal Code'),
                     required=True,
                     initial=self.ia.zipcode,
                 )),
                ('city',
                 forms.CharField(
                     label=_('Card Holder City'),
                     required=True,
                     initial=self.ia.city,
                 )),
                ('country',
                 forms.ChoiceField(
                     label=_('Card Holder Country'),
                     required=True,
                     choices=CachedCountries(),
                     initial=self.ia.country or guess_country(self.event),
                 )),
            ])

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

    def payment_form(self, request: HttpRequest) -> Form:
        """
        This is called by the default implementation of :py:meth:`payment_form_render`
        to obtain the form that is displayed to the user during the checkout
        process. The default implementation constructs the form using
        :py:attr:`payment_form_fields` and sets appropriate prefixes for the form
        and all fields and fills the form with data form the user's session.

        If you overwrite this, we strongly suggest that you inherit from
        ``PaymentProviderForm`` (from this module) that handles some nasty issues about
        required fields for you.
        """
        form = self.payment_form_class(
            data=(request.POST if request.method == 'POST' and request.POST.get("payment") == self.identifier else None),
            prefix='payment_%s' % self.identifier,
            initial={
                k.replace('payment_%s_' % self.identifier, ''): v
                for k, v in request.session.items()
                if k.startswith('payment_%s_' % self.identifier)
            }
        )
        form.fields = self.payment_form_fields

        for k, v in form.fields.items():
            v._required = v.required
            v.required = False
            v.widget.is_required = False

        return form
