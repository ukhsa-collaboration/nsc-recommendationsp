"""
Test utils.configurations
"""
from configurations import values

from ..configurations import PathValue


def test_path_value__no_env_check__value_from_file(monkeypatch, tmp_path):
    monkeypatch.setenv("DJANGO_TEST", "env value")
    file = tmp_path / "DJANGO_TEST"
    file.write_text("file value")

    # Simulate TEST = PathValue(tmp_path, values.Value)
    path_value = PathValue(str(tmp_path), values.Value)
    value = path_value.to_value("TEST")

    # Value will be a string because we've set an environ_name
    assert value == "file value"


def test_path_value__env_check_without_env__value_from_file(monkeypatch, tmp_path):
    file = tmp_path / "DJANGO_TEST"
    file.write_text("file value")

    path_value = PathValue(str(tmp_path), values.Value, environ=True)
    value = path_value.to_value("TEST")
    value.setup("TEST")
    assert value.default == "file value"
    assert value.value == "file value"


def test_path_value__env_check_with_env__value_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("DJANGO_TEST", "env value")
    file = tmp_path / "DJANGO_TEST"
    file.write_text("file value")

    path_value = PathValue(str(tmp_path), values.Value, environ=True)
    value = path_value.to_value("TEST")
    value.setup("TEST")
    assert value.default == "file value"
    assert value.value == "env value"


def test_path_value__dict_backend_value_class__from_value_class(monkeypatch, tmp_path):
    """
    Value classes which subclass DictBackendMixin (such as DatabaseURLValue) have
    different defaults for environ_prefix and environ_name
    """
    file = tmp_path / "DATABASE_URL"
    file.write_text("sqlite:///file_value")

    # Simulate DATABASES = PathValue(tmp_path, values.DatabaseURLValue)
    path_value = PathValue(str(tmp_path), values.DatabaseURLValue)
    value = path_value.to_value("DATABASES")

    # Value will be a string because we've set an environ_name
    assert "default" in value.value
    assert value.value["default"]["ENGINE"] == "django.db.backends.sqlite3"
    assert value.value["default"]["NAME"] == "file_value"


def test_path_value__file_has_newline__value_has_no_newline(monkeypatch, tmp_path):
    file = tmp_path / "DJANGO_TEST"
    file.write_text("file value\n")

    path_value = PathValue(str(tmp_path), values.Value)
    value = path_value.to_value("TEST")
    assert value == "file value"


def test_path_configuration__no_env_check__value_from_file(monkeypatch, tmp_path):
    monkeypatch.setenv("DJANGO_CONFIGURATION", "Config")
    monkeypatch.setenv(
        "DJANGO_SETTINGS_MODULE", "nsc.utils.tests.configurations.no_env_check"
    )
    monkeypatch.setenv("DJANGO_TMP_PATH", str(tmp_path))
    monkeypatch.setenv("DJANGO_TEST", "env value")

    file = tmp_path / "DJANGO_TEST"
    file.write_text("file value")

    from .configurations import no_env_check as settings

    assert settings.TEST == "file value"


def test_path_configuratio__env_check_without_env__value_from_file(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("DJANGO_CONFIGURATION", "Config")
    monkeypatch.setenv(
        "DJANGO_SETTINGS_MODULE", "nsc.utils.tests.configurations.env_check_without_env"
    )
    monkeypatch.setenv("DJANGO_TMP_PATH", str(tmp_path))

    file = tmp_path / "DJANGO_TEST"
    file.write_text("file value")

    from .configurations import env_check_without_env as settings

    assert settings.TEST == "file value"


def test_path_configuratio__env_check_with_env__env_check__value_from_env(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("DJANGO_CONFIGURATION", "Config")
    monkeypatch.setenv(
        "DJANGO_SETTINGS_MODULE", "nsc.utils.tests.configurations.env_check_with_env"
    )
    monkeypatch.setenv("DJANGO_TMP_PATH", str(tmp_path))
    monkeypatch.setenv("DJANGO_TEST", "env value")

    file = tmp_path / "DJANGO_TEST"
    file.write_text("file value")

    from .configurations import env_check_with_env as settings

    assert settings.TEST == "env value"
