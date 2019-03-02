from django import template
import os

register = template.Library()

@register.filter
def classname(obj):
    return obj.__class__.__name__

@register.filter
def group_address_to_tag(ga):
    return "address" + str(ga).replace("/", "-")

@register.simple_tag
def get_ws_port():
    return os.environ.get('WS_PORT', '8765')