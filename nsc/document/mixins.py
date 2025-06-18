from nsc.utils.virus_scanner import is_file_clean

class FileVirusScanMixin:
    virus_scan_fields = ()

    def clean(self):
        cleaned_data = super().clean()
        for field in self.virus_scan_fields:
            # Only scan if a new file was uploaded
            if field in self.files:
                file = cleaned_data.get(field)
                if file and not is_file_clean(file):
                    self.add_error(field, "Malware detected in the uploaded file. Please upload a clean file.")
        return cleaned_data