import sys
import typing


VersionLike: typing.TypeAlias = typing.Union["PythonVersion", str, float]


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

    match sys_ver:
        case [major, minor, patch]:
            return int(major), int(minor), int(patch)
        case [major, minor]:
            return int(major), int(minor), 0
        case [major, minor, *extra]:
            size = len(sys_ver)
            raise ValueError(
                f"Python version should contain at most 3 numbers, got: {size}"
            )
        case _:
            raise ValueError("Python version should contain at least 2 numbers")


@typing.runtime_checkable
class RichComparable(typing.Protocol):
    def __lt__(self, other):
        raise NotImplemented

    def __eq__(self, other):
        raise NotImplemented

    def __gt__(self, other):
        raise NotImplemented

    def __le__(self, other):
        raise NotImplemented

    def __ge__(self, other):
        raise NotImplemented


class PythonVersion:
    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        if major == 0 and minor == 0 and patch == 0:
            self.major, self.minor, self.patch = _read_sys()
        else:
            self.major = major
            self.minor = minor
            self.patch = patch

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: VersionLike):
        major, minor, patch = _read_str(str(other))
        return self.major < major or self.minor < minor or self.patch < patch

    def __eq__(self, other: VersionLike):
        major, minor, patch = _read_str(str(other))
        return self.major == major and self.minor and minor and self.patch == patch

    def __gt__(self, other: VersionLike):
        return not self.__le__(other)

    def __le__(self, other: VersionLike):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other: VersionLike):
        return self.__gt__(other) or self.__eq__(other)

    @property
    def is_py3(self):
        return self.major == 3


