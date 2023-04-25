from django import forms
from kanisa.forms.widgets import KanisaAccountMultipleSelector


class AccountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        full_name = obj.get_full_name()
        return full_name or obj.username


class MultipleAccountChoiceField(forms.ModelMultipleChoiceField):
    widget = KanisaAccountMultipleSelector

    def label_from_instance(self, obj):
        full_name = obj.get_full_name()
        return full_name or obj.username
