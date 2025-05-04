from django import template

register = template.Library()

@register.filter
def sum(field_list, field_name):
    return sum(getattr(item, field_name, 0) or 0 for item in field_list)
