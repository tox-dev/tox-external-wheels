from tox.exception import Error


class MissingWheelFile(Error):
    """Wheel file could not be found"""


class MultipleMatchingPatterns(Error):
    """More than one parameter supplied pattern matches current environment"""


class ExternalBuildNonZeroReturn(Error):
    """Non zero return code from external build script"""


class MalformedExternalWheelsParameter(Error):
    """Invalid external_wheel argument"""
