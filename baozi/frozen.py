import typing
from datetime import date, datetime

from .error import InvalidType

SINGLETON = {
    True,
    False,
    None,
    ...,  # Ellipsis is immutable
}

IMMUTABLE_NONCONTAINER_TYPES = {
    int,
    float,
    complex,
    bool,
    str,
    bytes,
} | SINGLETON

IMMUTABLE_CUSTOM_TYPES = {date, datetime}
IMMUTABLE_CONTAINER_TYPES = {tuple, frozenset, typing.Union, typing.Literal}


def is_field_immutable(field, imtypes: typing.Iterable[type] = {}):
    # Base case: if this is a non-container type, it is immutable
    if field in IMMUTABLE_NONCONTAINER_TYPES:
        return True

    if field in IMMUTABLE_CUSTOM_TYPES or field in imtypes:
        return True

    # Get the original type for types from the typing module
    origin = getattr(field, "__origin__", None)

    # If this is a container type, it is immutable if all its contained types are immutable
    if origin and origin in IMMUTABLE_CONTAINER_TYPES:
        return all(is_field_immutable(arg, imtypes) for arg in field.__args__)

    # If this is a class, it is immutable if all its fields are
    if isinstance(field, type) and hasattr(field, "__annotations__"):
        return is_class_immutable(field, imtypes)

    # TODO: should return information about field that is mutable
    return False


def is_class_immutable(cls: type, imtypes: typing.Iterable[type]):
    # BUG: cosnsider class T(tuple): ...
    # class B(T): ...
    # both are subclass of immutable,
    # yet would be assert to be mutable in current impl

    annotations = typing.get_type_hints(cls)
    namespace = annotations.items()
    for attr_name, attr_type in namespace:
        if not is_field_immutable(attr_type, imtypes):
            raise InvalidType(attr_name, attr_type)
    return True


class Mutability(typing.NamedTuple):
    obj: object
    attr_name: str
    attr_type: type
    is_immutable: bool
