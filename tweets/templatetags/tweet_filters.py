from django import template

register = template.Library()


@register.filter
def replace(value, arg):
    if ':' in str(arg):
        old, new = str(arg).split(':', 1)
    elif ',' in str(arg):
        old, new = str(arg).split(',', 1)
    else:
        return value
    return str(value).replace(old, new)