from django import forms


class BaseMixin:
    backup_email = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"style": "display:none", "tabindex": "-1"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("backup_email"):
            raise forms.ValidationError("Invalid email address")
        return cleaned_data
