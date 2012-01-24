from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse

import ho.pisa as pisa
import cStringIO as StringIO
import cgi, os, datetime

from brookie.models import Invoice, Quote, Item
from brookie import brookie_settings as br_settings

def user_is_staff(user):
    """ Check if a user has the staff status """
    return user.is_authenticated() and user.is_staff

def fetch_resources(uri, rel):
    """
    Callback to allow pisa/reportlab to retrieve Images,Stylesheets, etc.
    `uri` is the href attribute from the html link element.
    `rel` gives a relative path, but it's not used here.

    """
    if 'django.contrib.staticfiles' in settings.INSTALLED_APPS:
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

def generate_pdf(filename, context_dict, template, save=False):
    """ Generates a invoice PDF in desired language """
    template = get_template(template)
    context = Context(context_dict)
    html  = template.render(context)
    # Insert page skips
    html = html.replace('-pageskip-', '<pdf:nextpage />')
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(
        html.encode("UTF-8")), result, link_callback=fetch_resources)
    if not pdf.err:
        if not save:
            response = HttpResponse(result.getvalue(), mimetype='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=%s.pdf' % filename
            return response
        else:
            f = open(br_settings.BROOKIE_SAVE_PATH + '%s.pdf' % filename, 'w')
            f.write(result.getvalue())
            f.close()
            return True
            
    return http.HttpResponse('There was an error creating your PDF: %s' % cgi.escape(html))

@user_passes_test(user_is_staff)
def generate_invoice(request, id):
    """ Compile dictionary and generate pdf for invoice """
    invoice = get_object_or_404(Invoice, pk=id)

    context_dict = {'invoice': invoice,
                    'client': invoice.client,
                    'items': invoice.items.all(),}
    
    return generate_pdf(invoice.invoice_id, context_dict, "brookie/invoice_%s_pdf.html" % invoice.currency)

@user_passes_test(user_is_staff)
def view_invoice(request, id):
    """ Return the invoice """
    invoice = get_object_or_404(Invoice, pk=id)
    file_path = br_settings.BROOKIE_SAVE_PATH + '%s.pdf' % invoice.invoice_id
    
    if os.path.exists(file_path):
        f = open(file_path)

        response = HttpResponse(f.read(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % invoice.invoice_id
        return response
    else: raise Http404
    
@user_passes_test(user_is_staff)
def generate_quote(request, id):
    """ Generate dictionary and generate pdf for quote """
    quote = get_object_or_404(Quote, pk=id)

    # Replace values in the quote
    quote.content = quote.content.replace('-company-', quote.client.company)
    
    context_dict = {'quote': quote,
                    'client': quote.client,
                    'items': quote.items.all(),}

    return generate_pdf(quote.quote_id, context_dict, "brookie/quote_pdf.html")

@user_passes_test(user_is_staff)
def quote_to_invoice(request, id):
    """ Copy a Quote to an Invoice and redirects """
    q = get_object_or_404(Quote, pk=id)
    i = Invoice(client=q.client,
                date=datetime.datetime.now(),
                currency='euro',
                status=1,
                hourly_rate=str(br_settings.INVOICE_HOURLY_RATE),)
    i.save()
    for item in q.items.all():
        new_item = Item(date=datetime.datetime.now(),
                        description=item.description,
                        time = item.time,
                        amount = item.amount,
                        object=i)
        new_item.save()
    return HttpResponseRedirect(reverse('admin:brookie_invoice_change', args=[i.id,]))
