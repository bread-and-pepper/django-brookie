from django.conf.urls.defaults import *

urlpatterns = patterns('brookie.views',
    url(r'^invoice/(?P<id>[\d]+)/pdf/$',
        'generate_invoice',
        name='generate-invoice'),

    url(r'^invoice/(?P<id>[\d]+)/download/$',
        'view_invoice',
        name='view-invoice'),

    url(r'^quote/(?P<id>[-\d]+)/pdf/$',
        'generate_quote',
        name='generate-quote'),

    url(r'^quote/(?P<id>[-\d]+)/invoice/$',
        'quote_to_invoice',
        name='quote-to-invoice'),
)
