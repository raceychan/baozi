import sys
import typing
from typing import Union, Literal
from dataclasses import dataclass, field, is_dataclass, _process_class



__all__ = ["Struct"]

IMMUTABLE_NONCONTAINER_TYPES = {
    int,
    float,
    complex,
    bool,
    str,
    bytes,
    True,
    False,
    None,
}

IMMUTABLE_CONTAINER_TYPES = {tuple, frozenset, Union, Literal}
DATACLASS_DEFAULT_KW = dict(
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
    match_args=True,
    kw_only=False,
    slots=False,
)

if sys.version_info.minor >= 11:
    DATACLASS_DEFAULT_KW.update(weakref_slot=False)


class InvalidType(Exception):
    def __init__(self, attr_name, type_) -> None:
        self.attr_name = attr_name
        self.type_ = type_

    def __str__(self) -> str:
        msg = f"Attribute {self.attr_name} of type {self.type_} is mutable"
        return msg


def is_type_immutable(field):
    # Base case: if this is a non-container type, it is immutable
    if field in IMMUTABLE_NONCONTAINER_TYPES:
        return True

    # Get the original type for types from the typing module
    origin = getattr(field, "__origin__", None)

    # If this is a container type, it is immutable if all its contained types are
    if origin and origin in IMMUTABLE_CONTAINER_TYPES:
        return all(is_type_immutable(arg) for arg in field.__args__)

    # If this is a class, it is immutable if all its fields are
    if isinstance(field, type) and hasattr(field, "__annotations__"):
        return is_class_immutable(field)

    # If this is an unknown type, we can't determine its mutability
    return False


def is_class_immutable(cls):
    # BUG: cosnsider class T(tuple): ...
    # class B(T): ...
    # both are subclass of immutable,
    # yet would be assert to be mutable in current impl

    annotations = typing.get_type_hints(cls)
    namespace = annotations.items()
    for attr_name, attr_type in namespace:
        if not is_type_immutable(attr_type):
            print(f"Attribute {attr_name} of {cls} is mutable")
            return False
    return True


def get_dc_params(dataclass):
    cls_params = dataclass.__dataclass_params__
    params = {k: getattr(cls_params, k) for k in cls_params.__slots__}
    return params


def inherit_bases():
    ...


@typing.dataclass_transform()
class StructMeta(type):
    def __new__(meta, cls_name, bases, namespace, **kwargs):  # type: ignore
        raw_cls = super().__new__(meta, cls_name, bases, namespace)
        parent_params = dict()
        for base in bases:
            parent_params.update(get_dc_params(base))
        # TODO: ignore the attribute constructor order
        # NOTE: need to sort annotations in cls namespace
        kw = DATACLASS_DEFAULT_KW | parent_params | kwargs
        return _process_class(raw_cls, **kw)

    def __call__(self, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        return obj


class MetaConfig(metaclass=StructMeta):
    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False
    match_args: bool = True
    kw_only: bool = False
    slots: bool = False

    def __set_name__(self, obj_type, name):
        ...


class Struct(metaclass=StructMeta):
    ...

