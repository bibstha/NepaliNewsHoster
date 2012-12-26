from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def thumbnail_url(value):
	return value.replace(".pdf", ".png")    