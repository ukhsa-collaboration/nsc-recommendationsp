import io

import pytest

from nsc.utils.virus_scanner import is_file_clean


@pytest.fixture
def clean_file():
    return io.BytesIO(b"This is a clean file for testing.")


@pytest.fixture
def malware_file():
    # EICAR test virus string (not real malware, safe to use for testing)
    eicar = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$" b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    return io.BytesIO(eicar)


def test_clean_file(clean_file):
    result = is_file_clean(clean_file)
    assert result is True, "Expected clean file to be marked as clean"


@pytest.mark.skip(reason="Skipping malware test temporarily")
def test_malware_file(malware_file):
    result = is_file_clean(malware_file)
    assert result is False, "Expected malware file to be detected"
