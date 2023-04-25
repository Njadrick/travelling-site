from django.contrib import admin
from kanisa.conf import KANISA_ADMIN_THUMBS_SIZE
from sorl.thumbnail import default


class KanisaBaseAdmin(admin.ModelAdmin):
    def image_thumb(self, obj):
        if obj.image:
            thumb = default.backend.get_thumbnail(obj.image.file,
                                                  KANISA_ADMIN_THUMBS_SIZE)
            return u'<img width="%s" height="%s" src="%s" />' % (thumb.width,
                                                                 thumb.height,
                                                                 thumb.url)
        return "No Image"
    image_thumb.short_description = 'Image'
    image_thumb.allow_tags = True
