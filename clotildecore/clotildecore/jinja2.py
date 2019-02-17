from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment
from base import functions

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        "slugify": functions.slugify,
    })
    return env
