from django.conf import settings

ugettext = lambda s: s

# Path to store finished invoices, don't make this public accessible
BROOKIE_SAVE_PATH = getattr(settings, 'BROOKIE_SAVE_PATH', 'brookie/invoices/')

# Amount of days before an invoice expires.
INVOICE_EXPIRATION_DAYS = getattr(settings, 'INVOICE_EXPIRATION_DAYS', 14)

# Number of digits that your Invoice ID has.
INVOICE_ID_LENGTH =  getattr(settings, 'INVOICE_ID_LENGTH', 4)

# Prefix for your Invoice ID.
INVOICE_ID_PREFIX =  getattr(settings, 'INVOICE_ID_PREFIX', "BRI")

# Default hourly rate
INVOICE_HOURLY_RATE =  getattr(settings, 'INVOICE_HOURLY_RATE', 50.00)

# Invoice status choices.
INVOICE_STATUS_CHOICES =  getattr(settings, 'INVOICE_STATUS_CHOICES', ((1, ugettext('Under development')),
                                                                      (2, ugettext('Sent')),
                                                                      (3, ugettext('Reminded')),
                                                                      (4, ugettext('Payed'))))

# When the invoice is finished you will be able to download it in the admin
INVOICE_FINISH_STATUS = getattr(settings, 'INVOICE_FINISH_STATUS', (2, 3, 4))

# Invoice numbering starts at number
INVOICE_START_NUMBER =  getattr(settings, 'INVOICE_START_NUMBER', 1)
# In what valuta do you want your invoices to be available.

# Note: Each valuta requires it's own template. For ex., pounds will look
# for a template called ``invoice_gbp_pdf.html``.
INVOICE_CURRENCY_CHOICES = getattr(settings, 'INVOICE_CURRENCY_CHOICES', (('euro', ugettext('Euro')),
                                                                          ('gbp', ugettext('Pound')),
                                                                          ('dollar', ugettext('Dollar'))))

# Length of your Quote ID.
QUOTE_ID_LENGTH = getattr(settings, 'QUOTE_ID_LENGTH', 4)

# Prefix for your Quote ID.
QUOTE_ID_PREFIX = getattr(settings, 'QUOTE_ID_PREFIX', "BRQ")

# Quote status possibilities.
QUOTE_STATUS_CHOICES = getattr(settings, 'QUOTE_STATUS_CHOICES', ((1, ugettext('Draft')),
                                                                 (2, ugettext('Sent')),
                                                                 (3, ugettext('Declined')),
                                                                 (4, ugettext('Accepted'))))


