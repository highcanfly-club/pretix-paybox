import sys
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import resolve
from django.utils.translation import gettext_lazy as _
from django_scopes import scope
from pretix.base.models import Event, OrderPayment, Organizer
from pretix.multidomain.urlreverse import eventreverse
from urllib.parse import parse_qs, urlparse

from .PayboxCheck import get_object_response, verify_response
from .payment import PayboxPayment, check_signed_uuid4, getNonce


def refuse(request, *args, **kwargs):
    print('views.refuse', file=sys.stderr)
    return annule(request, kwargs)


def repondre_a(request, *args, **kwargs):
    print('views.repondre_a', file=sys.stderr)
    return annule(request, kwargs)


def get_response_code(request):
    uri = request.build_absolute_uri()
    url_parsed = urlparse(uri)
    query = parse_qs(url_parsed.query)  # dictionnary
    error = query["error"][0]
    return error


def effectue(request, *args, **kwargs):
    print('views.effectue', file=sys.stderr)
    pid = request.GET.get('paymentId')
    if pid == request.session['payment_payboxpayment_uuid4']:
        if request.session.get('paybox_payment_info'):
            paybox_payment_info = request.session.get('paybox_payment_info')
            payment = OrderPayment.objects.get(pk=paybox_payment_info["payment_id"])
        else:
            payment = None
        if payment:
            check = verify_response(request.build_absolute_uri())
            if check:
                if get_response_code(request) == "00000":
                    payment.info_data = get_object_response(request.build_absolute_uri())
                    payment.confirm()
                    return redirect(eventreverse(request.event, 'presale:event.order', kwargs={
                        'order': payment.order.code,
                        'secret': payment.order.secret
                    }) + '?paid=yes')
                else:
                    payment.fail()
                    return redirect(eventreverse(request.event, 'presale:event.order', kwargs={
                        'order': payment.order.code,
                        'secret': payment.order.secret
                    }))
    return HttpResponse(_("unkown error"), status=200)


def annule(request, *args, **kwargs):
    print('views.annule', file=sys.stderr)
    pid = request.GET.get('paymentId')
    if pid == request.session['payment_payboxpayment_uuid4']:
        check = verify_response(request.build_absolute_uri())
        if check:
            if request.session.get('paybox_payment_info'):
                paybox_payment_info = request.session.get('paybox_payment_info')
                payment = OrderPayment.objects.get(pk=paybox_payment_info["payment_id"])
                payment.fail()
                return redirect(eventreverse(request.event, 'presale:event.order', kwargs={
                    'order': payment.order.code,
                    'secret': payment.order.secret
                }))
    return HttpResponse(_("canceled"), status=500)


def attente(request, *args, **kwargs):
    print('views.attente', file=sys.stderr)
    return annule(request, kwargs)


def redirectview(request, *args, **kwargs):
    print('views.redirect', file=sys.stderr)
    url = resolve(request.path_info)
    print("PayboxPayment.redirectview {}".format(url.url_name), file=sys.stderr)
    spid = request.GET.get('suuid4')
    pid = check_signed_uuid4(spid)
    print(pid, file=sys.stderr)
    if pid == request.session['payment_payboxpayment_uuid4']:
        event_slug = request.session["payment_payboxpayment_event_slug"]
        organizer_slug = request.session["payment_payboxpayment_organizer_slug"]
        organizer = Organizer.objects.filter(slug=organizer_slug).first()
        with scope(organizer=organizer):
            event = Event.objects.filter(slug=event_slug).first()
        payment_provider = PayboxPayment(event)
        transaction = payment_provider.get_transaction(request)
        paybox_transaction = transaction.post_to_paybox()
        ctx = {
            "nonce": getNonce(request),
            "action": transaction.get_action(),
            'elements': transaction.get_html_elements(),
            'hmac': paybox_transaction['hmac'],
            "html": transaction.construct_html_form()["fields"]
        }
        r = render(request, 'pretix_paybox/redirect.html', ctx)
        return r

    return HttpResponse(_('Server Error'), status=500)
