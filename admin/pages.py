from django.contrib import admin
from kanisa.models import Page
from mptt.admin import MPTTModelAdmin


class PageAdmin(MPTTModelAdmin):
    pass

admin.site.register(Page, PageAdmin)
