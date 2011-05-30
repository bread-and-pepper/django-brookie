import os
from django.contrib import admin
from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

from brookie.models import Client, Invoice, Tax, Quote, Item, QuotePart
from brookie.templatetags.monetize import euro, pound, sek
from brookie.views import generate_pdf
from brookie import brookie_settings as br_settings

from admin_wmdeditor import WmdEditorModelAdmin

from datetime import datetime

def is_expired(self):
    """ Check if an invoice is expired """
    now = datetime.now().date()
    extra = ""
    image = 'img/admin/icon_success.gif'
    days_left = (self.exp_date - now).days
    if self.status == 1: image = 'img/admin/icon_changelink.gif'
    elif self.status in (2,3):
        if days_left <= 0:
            image = 'img/admin/icon_error.gif'
            extra = _(' <strong>(%s days late.)</strong>' % (days_left * -1))
        else:
            image = 'img/admin/icon_clock.gif'
            extra = _(" (%s days left.)" % days_left)
    return '<img src="%(admin_media)s%(image)s" />%(extra)s' % {'admin_media': settings.ADMIN_MEDIA_PREFIX,
                                                               'image': image,
                                                               'extra': extra,}
is_expired.short_description = _('Payed?')
is_expired.allow_tags = True

def total_monetized(self):
    """ Shows currency in admin, currently only euro's, pounds, sek and dollars """
    if self.currency == 'euro':
        return '&euro; %s' % euro(self.total)
    elif self.currency == 'gbp':
        return '&pound; %s' % pound(self.total)
    elif self.currency == 'dollar':
        return '&dollar; %s' % pound(self.total)
    elif self.currency == 'sek':
        return '&kronor; %s' % sek(self.total)
total_monetized.short_description = _("Total amount")
total_monetized.allow_tags = True

def pdf_invoice(self):
    """ Show link to invoice that has been sent """
    filename = br_settings.BROOKIE_SAVE_PATH + '%s.pdf' % self.invoice_id
    if os.path.exists(filename):
        return '<a href="%(url)s">%(invoice_id)s</a>' % {'url': reverse('view-invoice', kwargs={'id': self.id }),
                                                         'invoice_id': self.invoice_id }
    else: return ''
pdf_invoice.short_description = _("Download")
pdf_invoice.allow_tags = True

class ItemInline(generic.GenericTabularInline):
    model = Item

    def get_readonly_fields(self, request, obj=None):
        readonly = super(ItemInline, self).get_readonly_fields(request, obj)

        # if the invoice is send you can no longer alter it
        # Still working on this on
        if hasattr(obj, 'status') and obj.status in br_settings.INVOICE_FINISH_STATUS:
            self.max_num = obj.items.all().count()
            self.can_delete = False
        #    readonly = ('date', 'description', 'time', 'amount')
        return readonly

class QuoteItemInline(generic.GenericTabularInline):
    model = Item
    fields = ('description', 'time', 'amount',)

class QuotePartAdmin(admin.ModelAdmin):
    pass

class QuoteAdmin(WmdEditorModelAdmin):

    def change_view(self, request, object_id, extra_context=None):
        parts = QuotePart.objects.all()
        extra_context = {'parts': parts, }
        return super(QuoteAdmin, self).change_view(request,
                                                   object_id,
                                                   extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        parts = QuotePart.objects.all()
        extra_context = {'parts': parts, }
        return super(QuoteAdmin, self).add_view(request,
                                                form_url=form_url,
                                                extra_context=extra_context)


    wmdeditor_fields = ['content', ]
    list_display = ('quote_id', 'client', 'date', 'status', )
    list_filter = ['status',]
    ordering = ('id', )
    inlines = [QuoteItemInline, ]

    class Media:
        js = ('http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js', 'brookie/js/brookie.js')

class ClientAdmin(admin.ModelAdmin):
    list_display = ('company', )
    search_fields = ['company', 'first_name', 'last_name',]
    ordering = ('company', )

class TaxAdmin(admin.ModelAdmin):
    pass

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('client', 'status', 'date', total_monetized, is_expired, pdf_invoice)
    list_filter = ('status', 'client')
    exclude = ('invoice_no',)
    ordering = ('-id', )
    search_fields = ['client__company', ]
    readonly_fields = ()
    inlines = [ItemInline,]

    class Media:
        js = ('http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js', 'brookie/js/brookie.js')

    def get_readonly_fields(self, request, obj=None):
        readonly = super(InvoiceAdmin, self).get_readonly_fields(request, obj)

        # if the invoice is send you can no longer alter it
        if getattr(obj, 'status', None) in br_settings.INVOICE_FINISH_STATUS:
            readonly = ('invoice_id', 'client', 'date', 'currency', 'tax', 'hourly_rate')

        return readonly

    def save_model(self, request, obj, form, change):
        obj.save()
        if obj.status in br_settings.INVOICE_FINISH_STATUS:
            # Set the invoice id
            if not obj.invoice_no:
                invoice_list = Invoice.objects.filter(invoice_no__isnull=False).order_by('-invoice_no')
                try:
                    invoice = invoice_list[0]
                except:
                    # There are no numbered invoices
                    invoice_no = getattr(br_settings, 'INVOICE_START_NUMBER', 1)
                else:
                    invoice_no = invoice.invoice_no + 1
                obj.invoice_no = invoice_no
                obj.save()

            # Generate the pdf for this invoice
            context_dict = {'invoice': obj,
                            'client': obj.client,
                            'items': obj.items.all(),}

            generate_pdf(obj.invoice_id, context_dict, "brookie/invoice_%s_pdf.html" % obj.currency, save=True)

admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Tax, TaxAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(QuotePart, QuotePartAdmin)
