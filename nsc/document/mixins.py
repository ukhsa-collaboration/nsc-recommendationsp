from nsc.utils.virus_scanner import is_file_clean
import logging

logger = logging.getLogger('nsc.utils.virus_scanner')

class FileVirusScanMixin:
    virus_scan_fields = ()

    def clean(self):
        cleaned_data = super().clean()

        logger.debug(f"Starting virus scan on fields: {self.virus_scan_fields}")
        logger.debug(f"Files submitted: {list(self.files.keys())}")

        for field_prefix in self.virus_scan_fields:
            # Find all keys in self.files that contain the prefix
            matching_fields = [f for f in self.files if field_prefix in f]
            for field in matching_fields:
                file = self.files.get(field)
                if file:
                    # Log the file name
                    logger.debug(f"Scanning file '{getattr(file, 'name', str(file))}' for field '{field}'")
                    if not is_file_clean(file):
                        self.add_error(
                            field,
                            "Malware detected in the uploaded file. Please upload a clean file.",
                        )
        return cleaned_data