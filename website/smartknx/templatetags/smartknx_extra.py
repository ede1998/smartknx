from django import template

register = template.Library()

@register.filter
def classname(obj):
    return obj.__class__.__name__

@register.filter
def group_address_to_tag(ga):
    return "address" + str(ga).replace("/", "-")