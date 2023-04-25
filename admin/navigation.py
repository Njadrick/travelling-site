from django.contrib import admin
from kanisa.models import NavigationElement
from mptt.admin import MPTTModelAdmin


class NavigationElementAdmin(MPTTModelAdmin):
    list_display = ('title', 'url', 'parent', )

admin.site.register(NavigationElement, NavigationElementAdmin)
