from django.contrib import admin
from kanisa.models import Document


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ('title', 'details', )
    list_display = ('title', 'modified', )

admin.site.register(Document, DocumentAdmin)
