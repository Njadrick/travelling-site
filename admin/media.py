from django.contrib import admin
from kanisa.admin.base import KanisaBaseAdmin
from kanisa.models import InlineImage
from sorl.thumbnail.admin import AdminImageMixin


class InlineImageAdmin(KanisaBaseAdmin, AdminImageMixin):
    list_display = ('image_thumb',
                    'title',
                    'slug', )

    search_fields = ('title', )

admin.site.register(InlineImage, InlineImageAdmin)
