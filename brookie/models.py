from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from brookie import brookie_settings as settings

from decimal import *
from datetime import datetime, timedelta

class Client(models.Model):
    """ Model representing a client """
    company = models.CharField(_('company'), max_length=80)
    first_name = models.CharField(_('first name'), max_length=80, blank=True)
    last_name = models.CharField(_('last name'), max_length=80, blank=True)
    address = models.CharField(_('address'), max_length=255)
    zipcode = models.CharField(_('zipcode'), max_length=7)
    city = models.CharField(_('city'), max_length=128)
    country = models.CharField(_('country'), max_length=255)
    tax_name = models.CharField(_('tax name'), max_length=255, blank=True)
    tax_number = models.CharField(_('tax number'), max_length=255, blank=True)
    additional_info = models.TextField(_('additional payment info'), blank=True)

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')
        ordering = ('company', 'last_name', 'first_name')

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __unicode__(self):
        return '%s' % self.company

class Invoice(models.Model):
    """ Model representing an invoice """
    client = models.ForeignKey(Client, verbose_name=_('client'))
    date = models.DateField(_('date'))
    currency = models.CharField(_('currency'),
                                max_length=124,
                                choices=settings.INVOICE_CURRENCY_CHOICES)
    status = models.IntegerField(_('status'), choices=settings.INVOICE_STATUS_CHOICES)
    tax = models.ForeignKey('Tax', blank=True, null=True)
    hourly_rate = models.DecimalField(_('hourly rate'),
                                      max_digits=6,
                                      decimal_places=2,
                                      default=settings.INVOICE_HOURLY_RATE)
    items = generic.GenericRelation('Item')


    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')

    def __unicode__(self):
        return self.invoice_id

    @property
    def total(self):
        """ Total amount including the taxes """
        return self.subtotal if not self.tax else self.subtotal + self.total_tax

    @property
    def subtotal(self):
        """ Subtotal, the amount excluding the taxes """
        subtotal = Decimal(0)
        for item in self.items.all(): subtotal += item.amount
        return subtotal

    @property
    def total_tax(self):
        """ Total of tax payed """
        if self.tax: total_tax = (self.subtotal * (self.tax.percentage)) / 100
        else: total_tax = Decimal(0)
        return total_tax.quantize(Decimal('0.01'), ROUND_HALF_UP)

    @property
    def invoice_id(self):
        """ Unique invoice ID """
        number = (settings.INVOICE_ID_LENGTH - len(str(self.id))) * "0" + str(self.id)
        return '%(prefix)s%(year)s%(unique_id)s' % {'prefix': settings.INVOICE_ID_PREFIX,
                                                    'year': self.date.strftime("%y"),
                                                    'unique_id': number}

    @property
    def is_credit(self):
        """ Check if the invoice is a credit invoice """
        if self.total < 0:
            return True
        else: return False
    
    @property
    def exp_date(self):
        """ Expiration date of the invoice """
        expiration_time = timedelta(days=settings.INVOICE_EXPIRATION_DAYS)
        return (self.date + expiration_time)

class Tax(models.Model):
    """ Model representing different taxes to be used in Invoices"""
    name = models.CharField(_('name'), max_length=255)
    abbrevation = models.CharField(_('abbrevation'), max_length=255)
    percentage = models.DecimalField(_('percentage'),
                                     max_digits=4,
                                     decimal_places=2)

    class Meta:
        verbose_name = _('tax')
        verbose_name_plural = _('taxes')

    def __unicode__(self):
        return '%s' % self.name

class QuotePart(models.Model):
    """ A default part that can be inserted in a quote """
    name = models.CharField(_('name'), max_length=255)
    content = models.TextField(_('content'), help_text=_('The above will be selectable when creating a new Quote. Markdown is enabled.'))

    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return '%s' % self.name

class Quote(models.Model):
    """ Model representing a quote """
    client = models.ForeignKey(Client, related_name=_('quote'))
    date = models.DateField(_('date'))
    status = models.SmallIntegerField(_('status'), choices=settings.QUOTE_STATUS_CHOICES)
    content = models.TextField(_('content'))
    items = generic.GenericRelation('Item')
    hourly_rate = models.DecimalField(_('hourly rate'),
                                      max_digits=6,
                                      decimal_places=2,
                                      default=settings.INVOICE_HOURLY_RATE)

    class Meta:
        verbose_name = _('quote')
        verbose_name_plural = _('quotes')

    def __unicode__(self):
        return '%s' % self.quote_id

    @property
    def total(self):
        """ Total amount """
        total = Decimal(0)
        for item in self.items.all():
            total += item.amount
        return total

    @property
    def quote_id(self):
        """ Unique quote ID """
        number = (settings.QUOTE_ID_LENGTH - len(str(self.id))) * "0" + str(self.id)
        return '%(prefix)s%(year)s%(unique_id)s' % {'prefix': settings.QUOTE_ID_PREFIX,
                                                    'year': self.date.strftime("%y"),
                                                    'unique_id': number}
    @property
    def exp_date(self):
        """ Expiration date of the quote """
        expiration_time = timedelta(days=31)
        return (self.date + expiration_time)

class Item(models.Model):
    """ Items of which a Quote or an Invoice exists. """
    date = models.DateField(_('date'), blank=True, null=True)
    description = models.CharField(_('description'), max_length=255)
    time = models.IntegerField(_('time in minutes'), blank=True, null=True)
    amount = models.DecimalField(_('amount'), max_digits=19, decimal_places=2)

    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ['date']
    
    def __unicode__(self):
        return '%s' % self.description
