# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _

class MenuRow(object):
    def __init__(self,xlong,xshort,xurl):
        self.long=xlong
        self.short=xshort
        self.url=xurl

HEADERMENU=[
    ( MenuRow("Home","Home","/"), [] ),
    ( MenuRow("Languages","Languages","/languages/"), [] ),
    ( MenuRow("Corpora","Corpora","/corpora/"), [] ),
    ( MenuRow("Morphology","Morphology","/morphology/"), [] ),
    ( MenuRow("Tools","Tools","/tools/"), [ 
            MenuRow("Helper Italiano","Helper Italiano","/tools/helper_italiano/"), 
            ] ),
    ( MenuRow("Admin","Admin","/admin/"), [
            MenuRow("Languages","Languages","/admin/languages/"),
            MenuRow("Corpora","Corpora","/admin/corpora/"),
            MenuRow("Morphology","Morphology","/admin/morphology/"),
            MenuRow("Helper Italiano","Helper Italiano","/admin/helper_italiano/"),
            ] ),
    ( MenuRow("Help","Help","/help/"), [] ),
    ]


#Analogic 50 gradi ffcd00

#Primary Color A (header, back e link):
#FFCD00	BFA330	A68500	FFD940	FFE373

#Secondary Color A (menu):
#CCF600	A1B92E	85A000	DAFB3F	E3FB71

#Secondary Color B (titoli):
#FF7F00	BF7730	A65200	FF9F40	FFB873


colors={
    "TEXT_FORE": "black",
    "TEXT_BACK": "white",
    "LINK_INLINE_FORE": "#a68500",
    "LINK_INLINE_BACK": "white",
    "LINK_INLINE_ACTIVE_FORE": "white",
    "LINK_INLINE_ACTIVE_BACK": "#a68500",

    "BODY_BACK_START":"white",
    "BODY_BACK_STOP":"#ffcd00",
    "CONTENT_BACK_START":"white",
    "CONTENT_BACK_STOP":"#ffe373",

    "HEADER_BACK":"#bfa330",
    "HEADERTITLE_BACK":"#a68500",
    "HEADERTITLE_FORE":"#a68500",
    "HEADERTITLE_TEXT_SHADOW":"#ffe373",

    "MENU_BACK": "rgba(227, 251, 113,0.5)",
    "MENU_ITEM_BACK_START":"#dafb3f",
    "MENU_ITEM_BACK_STOP":"#e3fb71",
    "MENU_ITEM_FORE":"#85a000",
    "MENU_ITEM_ACTIVE_BACK_START":"#85a000",
    "MENU_ITEM_ACTIVE_BACK_STOP":"#a1b92e",
    "MENU_ITEM_ACTIVE_FORE":"#e3fb71",

    "TITLE_FORE": "#a65200",
    "TITLE_BACK": "#ffb873"

}
#Secondary Color B (titoli):
#FF7F00	BF7730	A65200	FF9F40	FFB873

def get_template_vars(request=None):
    T={
        "SITE_NAME":"Clotilde",
        "SITE_ICON":settings.STATIC_URL+"/logo-mini.png",
        "BACKGROUND":settings.STATIC_URL+"backgrounds/back.png",
        "JQUERY":settings.STATIC_URL+"js/jquery.js",
        "DYNAMIC_CSS":"/css",
        "HEADERMENU": HEADERMENU,
        }
    for cname,cdef in colors.items():
        T["COLOR_"+cname]=cdef
    return T
