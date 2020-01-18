from tox.exception import Error


class MissingWheelFile(Error):
    """Wheel file could not be found"""


class MultipleMatchingPatterns(Error):
    """More than one parameter supplied pattern matches current environment"""
