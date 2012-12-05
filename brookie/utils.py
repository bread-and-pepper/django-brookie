from brookie.templatetags.monetize import euro, pound, sek

def decimal_to_string(value, currency):
    """ Convert value to currency string """
    if currency == 'euro':
        return euro(value)
    elif currency == 'gbp':
        return pound(value)
    return sek(value)
