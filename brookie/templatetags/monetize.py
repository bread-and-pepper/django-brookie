from django import template

register = template.Library()

def beautify(val, sep):
    val = str(val)
    if val != ".": val = val.replace('.', sep)
    if val.find(sep) == -1: val = val + sep + "00"
    elif len(val.split(sep)[-1]) == 1: val = val + "0"
    return val

@register.filter(name="euro")
def euro(value):
    """ 
    Converts a number to humanized prices in euro. Thus replacing dots by
    comma's and making sure that there are always to decimals. 

    """
    return beautify(value, ',')

@register.filter(name="pound")
def pound(value):
    """ Same as above, but than pounds. """
    return beautify(value, '.') 

@register.filter(name="sek")
def sek(value):
    """ Same as above, but than sek. """
    return beautify(value, '.') 
