from django import forms


class BaseMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the backup_email field if it's not already in the form
        if "backup_email" not in self.fields:
            self.fields["backup_email"] = forms.CharField(
                required=False,
                widget=forms.HiddenInput(),
            )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("backup_email"):
            raise forms.ValidationError("Invalid email address")
        return cleaned_data
