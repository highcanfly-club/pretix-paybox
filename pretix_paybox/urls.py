from django.urls import re_path
from pretix.multidomain import event_url
from . import views

event_patterns = [
    re_path(r'^paybox/payment/refuse',
            views.refuse, name='paybox.refuse'),
    re_path(r'^paybox/payment/repondre_a',
            views.repondre_a, name='paybox.repondre_a'),
    re_path(r'^paybox/payment/effectue',
            views.effectue, name='paybox.effectue'),
    re_path(r'^paybox/payment/annule',
            views.annule, name='paybox.annule'),
    re_path(r'^paybox/payment/attente',
            views.attente, name='paybox.attente'),
    event_url(r'^paybox/payment/redirect',
              views.redirectview, name='paybox.redirect'),
]
