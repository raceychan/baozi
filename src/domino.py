import sys
import typing
from dataclasses import (
    _process_class,
    MISSING,
    is_dataclass,
    FrozenInstanceError,
    field,
)

from frozen import is_class_immutable, is_field_immutable
from slots import create_slots_struct


DATACLASS_DEFAULT_KW = dict(
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
)

if sys.version_info.minor >= 11:
    DATACLASS_DEFAULT_KW.update(weakref_slot=False)

FIELDS_DEFAULT_KW = dict(
    match_args=True,
    kw_only=False,
    slots=False,
)


FIELDS_PARAMS = "__DOMINO_FIELD_PARAMS__"


def read_slots(cls):
    slots = getattr(cls, "__slots__", ())
    values = {k: getattr(cls, k) for k in slots} if slots else {}
    return values


class InvalidType(Exception):
    def __init__(self, attr_name, type_) -> None:
        self.attr_name = attr_name
        self.type_ = type_

    def __str__(self) -> str:
        msg = f"Attribute {self.attr_name} of type {self.type_} is mutable"
        return msg


class ArgumentError(Exception):
    def __str__(self):
        msg = f"Positional arguments are not allowed"
        return msg


class ImmutableFieldError(Exception):
    ...


class _MISSING_DEFAULT:
    ...


MISSING_DEFAULT = _MISSING_DEFAULT()


def get_dc_params(dataclass):
    params = read_slots(dataclass.__dataclass_params__)
    return params


def resort_annotations(cls):
    default_fields, non_defaults = dict(), dict()
    for name, type_ in cls.__annotations__.items():
        if getattr(cls, name, MISSING_DEFAULT) != MISSING_DEFAULT:
            default_fields[name] = type_
        else:
            non_defaults[name] = type_
    return non_defaults | default_fields


def resort_fields(cls):
    default_fields, non_defaults = dict(), dict()

    for f_name, field in cls.__dataclass_fields__.items():
        if field.default is not MISSING:
            default_fields[f_name] = field
        else:
            default_fields[f_name] = field

    return non_defaults | default_fields


class MetaConfig:
    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False
    match_args: bool = True
    kw_only: bool = False
    slots: bool = False


@typing.dataclass_transform(kw_only_default=True)
class StructMeta(type):
    def __new__(meta: "StructMeta", cls_name: str, bases: tuple, namespace: dict, _domino_subinit_hook: bool = False, **kwargs):  # type: ignore
        if _domino_subinit_hook:
            raw_cls = super().__new__(meta, cls_name, bases, namespace)
            return raw_cls

        raw_cls = super().__new__(meta, cls_name, bases, namespace)

        base_m_params = dict()
        base_f_params = dict()
        for base in bases:
            if is_dataclass(base):
                base_m_params.update(get_dc_params(base))
                base_f_params.update(getattr(base, FIELDS_PARAMS, {}))

        config = namespace.get(MetaConfig, {})  # BUG: this currently does not work

        current_m_config = {k: kwargs[k] for k in kwargs if k in DATACLASS_DEFAULT_KW}
        current_f_config = {k: kwargs[k] for k in kwargs if k in FIELDS_DEFAULT_KW}
        model_config = DATACLASS_DEFAULT_KW | base_m_params | current_m_config | config
        field_config = FIELDS_DEFAULT_KW | base_f_params | current_f_config | config

        if field_params := getattr(raw_cls, FIELDS_PARAMS, {}):
            field_config |= field_params

        setattr(raw_cls, FIELDS_PARAMS, field_config)
        cls_config = model_config | field_config

        if cls_config["slots"]:
            cls_ = create_slots_struct(raw_cls, cls_config)
        else:
            cls_ = _process_class(raw_cls, **cls_config)

        if cls_config["frozen"] and not is_class_immutable(cls_):
            raise ImmutableFieldError

        return cls_

    def __call__(self, *args, **kwargs):
        if args:
            raise ArgumentError

        obj = super().__call__(**kwargs)
        return obj


class Struct(metaclass=StructMeta, kw_only=True):
    ...

    def but(self, **kw_attrs):
        # TODO: return a new object with current attributes + kw_attrs
        ...


@typing.dataclass_transform(frozen_default=True)
class FrozenStruct(metaclass=StructMeta, kw_only=True, frozen=True, slots=True):
    ...
