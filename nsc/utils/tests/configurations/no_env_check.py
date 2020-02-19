from configurations import values

from nsc.utils.configurations import PathConfiguration, PathValue


class Config(PathConfiguration):
    TMP_PATH = values.Value(environ_name="TMP_PATH")
    TEST = PathValue(TMP_PATH, values.Value)
