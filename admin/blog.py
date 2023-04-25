from datetime import date
from django.contrib import admin
from django.contrib.auth import get_user_model
from kanisa.forms.fields import AccountChoiceField
from kanisa.models import BlogPost


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_full', 'publish_date', )
    date_hierarchy = 'publish_date'
    search_fields = ('title', 'teaser_text', 'main_text', )

    def author_full(self, obj):
        if not obj.author:
            return 'None'

        return obj.author.get_full_name()
    author_full.short_description = 'Author'

    def get_form(self, request, obj=None, **kwargs):
        self.current_user = request.user
        return super(BlogPostAdmin,
                     self).get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, field, **kwargs):
        if field.name == 'author':
            queryset = get_user_model().objects.filter(
                is_active=True
            )
            return AccountChoiceField(
                required=False,
                queryset=queryset,
                initial=self.current_user.id
            )
        elif field.name == 'publish_date':
            rval = super(BlogPostAdmin,
                         self).formfield_for_dbfield(field, **kwargs)
            rval.initial = date.today()
            return rval

        return super(BlogPostAdmin,
                     self).formfield_for_dbfield(field, **kwargs)

admin.site.register(BlogPost, BlogPostAdmin)
