"""
Extensions to django-configurations
"""
from pathlib import Path

from configurations import Configuration
from configurations.utils import uppercase_attributes


class PathValue:
    """
    Wrapper for django-configurations Value which takes the value from file on disk,
    suitable for reading secrets without leaking them into the environment.

    Looks for a file matching the variable name, with the prefix PATH_VALUE_DIR.

    Example:

        Given the following::

            class Config(PathConfiguration):
                SECRET = PathValue("/run/secrets", values.Value)

        the value will be loaded from ``/run/secrets/DJANGO_SECRET``
    """

    def __init__(self, path, value_cls, **kwargs):
        """
        Define the value class to use and any arguments for it.

        Arguments:

            path (str): Path to the value store
            value_cls (configurations.value.Value): Value class to instantiate
            **kwargs (dict): Arguments for the Value class

        Defaults:

            environ=False: Don't check the environ by default. Set to True to use an
                environ variable over the value from disk
        """
        self.path = Path(path)
        self.value_cls = value_cls

        # Don't check the environ by default - this can be overridden, but we want to
        # default to only checking the file system
        self.kwargs = {"environ": False}

        # Collect defaults from value class; these are set by __init__, so we need to
        # create a fake instance. Set environ=True to ensure it does not resolve
        # immediately.
        value_instance = value_cls(environ=True)
        self.kwargs["environ_name"] = value_instance.environ_name
        self.kwargs["environ_prefix"] = value_instance.environ_prefix

        # Update with any overrides we've received
        self.kwargs.update(kwargs)

    def to_value(self, name):
        """
        Read the variable from disk and return a django-configurations Value
        """
        # Read the secret
        filename = self.kwargs["environ_name"] or name
        prefix = self.kwargs.get("environ_prefix", None)
        if prefix:
            filename = f"{prefix}_{name}"

        path = Path(self.path / filename)
        if not path.is_file():
            raise ValueError(f"Secret not found at {path}")
        raw = path.read_text().strip()

        # Instantiate the django-configuration value class with the raw value
        value = self.value_cls(raw, **self.kwargs)

        return value


class PathConfiguration(Configuration):
    """
    Configuration class which is aware of PathValue attributes
    """

    @classmethod
    def setup(cls):
        """
        Convert any PathValue to a django-configurations Value
        """
        for name, secret in uppercase_attributes(cls).items():
            if isinstance(secret, PathValue):
                value = secret.to_value(name)
                setattr(cls, name, value)
        super().setup()
