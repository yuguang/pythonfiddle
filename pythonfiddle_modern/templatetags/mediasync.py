"""
Stub replacement for the legacy django-mediasync package.
Renders proper <link>/<script> tags using Django's static files framework.
"""
from django.template import Library
from django.templatetags.static import static
from django.conf import settings

register = Library()


@register.simple_tag(takes_context=True)
def media_url(context, path=''):
    base = getattr(settings, 'STATIC_URL', '/static/').rstrip('/')
    return base + path


@register.simple_tag
def css(path):
    url = static(path) if not path.startswith('/') else path
    return f'<link rel="stylesheet" type="text/css" href="{url}" />'


@register.simple_tag
def js(path):
    url = static(path) if not path.startswith('/') else path
    return f'<script type="text/javascript" src="{url}"></script>'
