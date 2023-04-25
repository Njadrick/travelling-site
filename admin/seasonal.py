from django.contrib import admin
from kanisa.admin.base import KanisaBaseAdmin
from kanisa.models import SeasonalEvent


class SeasonalEventAdmin(KanisaBaseAdmin):
    list_display = ('title', 'season', 'date', )
    date_hierarchy = 'date'
    list_filter = ('season', )
    search_fields = ('title', 'intro', )

admin.site.register(SeasonalEvent, SeasonalEventAdmin)
