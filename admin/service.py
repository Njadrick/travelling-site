from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import formats
from kanisa.admin.base import KanisaBaseAdmin
from kanisa.models import (
    Band,
    Composer,
    Song,
    Service,
    SongInService,
    ScheduledEvent
)


class ComposerAdmin(KanisaBaseAdmin):
    search_fields = ('forename', 'surname', )
    list_display = ('full_name_reversed', )

admin.site.register(Composer, ComposerAdmin)


class SongAdmin(KanisaBaseAdmin):
    search_fields = ('title', )
    list_display = ('title', )

admin.site.register(Song, SongAdmin)


class SongInline(admin.TabularInline):
    model = SongInService


class ServiceAdmin(KanisaBaseAdmin):
    list_display = ('event_title', 'event_date', )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(ServiceAdmin,
                      self).formfield_for_foreignkey(db_field,
                                                     request,
                                                     **kwargs)

        if db_field.rel.to == get_user_model():
            field.label_from_instance = self.get_user_label
        if db_field.rel.to == ScheduledEvent:
            field.label_from_instance = self.get_event_label

        return field

    def get_user_label(self, user):
        full_name = user.get_full_name()
        return full_name or user.username

    def get_event_label(self, event):
        event_date = formats.date_format(event.date, "DATE_FORMAT")
        return '%s (%s)' % (unicode(event), event_date)

    inlines = [
        SongInline,
    ]

admin.site.register(Service, ServiceAdmin)


class BandAdmin(KanisaBaseAdmin):
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(BandAdmin,
                      self).formfield_for_foreignkey(db_field,
                                                     request,
                                                     **kwargs)

        if db_field.rel.to == get_user_model():
            field.label_from_instance = self.get_user_label

        return field

    def get_user_label(self, user):
        full_name = user.get_full_name()
        return full_name or user.username

admin.site.register(Band, BandAdmin)
