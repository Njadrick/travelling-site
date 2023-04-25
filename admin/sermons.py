from django.contrib import admin
from kanisa.admin.base import KanisaBaseAdmin
from kanisa.models import (SermonSeries,
                           SermonSpeaker,
                           Sermon)


class SermonSeriesAdmin(KanisaBaseAdmin):
    search_fields = ('title', 'details', )
    list_display = (
        'title',
        'image_thumb',
        'passage',
        'active',
        'num_sermons'
    )

admin.site.register(SermonSeries, SermonSeriesAdmin)


class SermonSpeakerAdmin(KanisaBaseAdmin):
    search_fields = ('forename', 'surname', )
    list_display = ('name', 'image_thumb', )

admin.site.register(SermonSpeaker, SermonSpeakerAdmin)


class SermonAdmin(admin.ModelAdmin):
    search_fields = ('title', 'details', )
    list_display = (
        'title',
        'date',
        'passage',
        'series',
        'speaker',
        'downloads',
    )
    readonly_fields = ('downloads', 'podcast_downloads', )
    date_hierarchy = 'date'

admin.site.register(Sermon, SermonAdmin)
