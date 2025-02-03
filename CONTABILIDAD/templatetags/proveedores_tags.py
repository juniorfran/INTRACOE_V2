from django import template

register = template.Library()

@register.filter
def estado_clase(value):
    return 'bg-success' if value else 'bg-danger'
