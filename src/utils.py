import sys

def _read_sys() -> tuple[int, int, int]:
    """
    _read_sys() -> (3, 11, 0)
    """

    vs = sys.version_info
    return vs.major, vs.minor, vs.micro

def _read_str(str_repr: str) -> tuple[int, int, int]:
    """
    read_str("3.11.0") -> (3, 11, 0)
    read_str("3.8") -> (3, 8)
    """
    sys_ver = str_repr.split(".")
    if len(sys_ver) < 2:
        raise ValueError("Python version should contain at least 2 numbers")

    major, minor, *patch = sys_ver
    patch = patch[0] if patch else 0
    return int(major), int(minor), int(patch)


class PythonVersion:
    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        if major == 0 and minor == 0 and patch == 0:
            self.major, self.minor, self.patch = _read_sys()
        else:
            self.major = major
            self.minor = minor
            self.patch = patch

    @classmethod
    def _read_str(cls, str_repr):
        major, minor, *patch = str_repr.split(".")
        patch = patch[0] if patch else 0
        return int(major), int(minor), int(patch)

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other):
        major, minor, patch = _read_str(str(other))
        return self.major < major or self.minor < minor or self.patch < patch

    def __eq__(self, other):
        major, minor, patch = _read_str(str(other))
        return self.major == major and self.minor and minor and self.patch == patch

    def __gt__(self, other):
        return not self.__le__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gq__(self, other):
        return self.__gt__(other) or self.__eq__(other)

