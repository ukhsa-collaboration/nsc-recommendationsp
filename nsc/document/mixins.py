from django.core.exceptions import NON_FIELD_ERRORS

from nsc.utils.virus_scanner import is_file_clean


class FileVirusScanMixin:
    virus_scan_fields = ()

    def clean(self):
        cleaned_data = super().clean()

        for html_name, file in self.files.items():
            if any(
                html_name.startswith(self.add_prefix(prefix))
                for prefix in self.virus_scan_fields
            ):
                if file and not is_file_clean(file):
                    # translate ‘document-0-upload’ → ‘upload’
                    bare_name = (
                        html_name[len(self.prefix) + 1 :] if self.prefix else html_name
                    )
                    if bare_name not in self.fields:
                        bare_name = NON_FIELD_ERRORS
                    self.add_error(
                        bare_name,
                        "Malware detected in the uploaded file. "
                        "Please upload a clean file.",
                    )
        return cleaned_data
