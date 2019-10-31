from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation,safestring
from django.template import defaultfilters


from jinja2 import Environment,PackageLoader
from base import functions

def environment(**options):
    opts=options.copy()
    if "extensions" not in opts:
        opts["extensions"]=['jinja2.ext.i18n']
    elif 'jinja2.ext.i18n' not in opts["extensions"]:
        opts["extensions"].append('jinja2.ext.i18n')
    
    env = Environment(**opts)
    env.install_gettext_translations(translation)
    env.globals.update({
        'static': static,
        'url': reverse,
        "slugify": functions.slugify,
        "iriencode": defaultfilters.iriencode,
        "urlencode": defaultfilters.urlencode,
        "mark_safe": safestring.mark_safe,
    })
    return env
