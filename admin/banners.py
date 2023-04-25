from django.contrib import admin
from kanisa.admin.base import KanisaBaseAdmin
from kanisa.models import Banner
from sorl.thumbnail.admin import AdminImageMixin


class BannerAdmin(KanisaBaseAdmin, AdminImageMixin):
    list_display = ('image_thumb',
                    'headline',
                    'url',
                    'publish_from',
                    'publish_until',
                    'active', )

    search_fields = ('headline',
                     'contents',
                     'url', )

    readonly_fields = ('visits', )

admin.site.register(Banner, BannerAdmin)
