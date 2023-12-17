import sys
import typing as ty
from dataclasses import MISSING, _process_class, is_dataclass  # field,

from error import ArgumentError, MutableFieldError
from frozen import is_class_immutable
from slots import create_slots_struct
from typecast import parse_config, read_env

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


class SlotProtocol(ty.Protocol):
    __slots__: tuple[str, ...]


class _MISSING_DEFAULT:
    ...


MISSING_DEFAULT = _MISSING_DEFAULT()


def read_slots(obj: SlotProtocol):
    if not hasattr(obj, "__slots__"):
        return dict()
    slots = {key: getattr(obj, key) for key in obj.__slots__ if not key.startswith("_")}
    return slots


def read_attributes(obj) -> ty.Mapping:
    if isinstance(obj, dict):
        return obj
    elif obj.__class__ is type or obj.__class__.__class__ is type:
        return {key: val for key, val in obj.__dict__ if not key.startswith("_")}

    slots = {key: getattr(obj, key) for key in obj.__slots__ if not key.startswith("_")}
    return slots


def pretty_repr(obj: SlotProtocol | type):
    if hasattr(obj, "__slots__"):
        lines = "".join(f"\t{key}={val}\n" for key, val in read_slots(obj).items())
    else:
        lines = "".join(
            f"\t{key}={val}\n"
            for key, val in obj.__dict__.items()
            if not key.startswith("_")
        )
    return f"{obj.__class__.__name__}(\t\n{lines})"


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


class MetaConfig(ty.TypedDict, total=False):
    init: bool  # = True
    repr: bool  # = True
    eq: bool  # = True
    order: bool  # = False
    unsafe_hash: bool  # = False
    frozen: bool  # = False
    match_args: bool  # = True
    kw_only: bool  # = False
    slots: bool  # = False


@ty.dataclass_transform(kw_only_default=True)
class StructMeta(type):
    def __new__(
        meta: "StructMeta",
        cls_name: str,
        bases: tuple,
        namespace: dict,
        _domino_subinit_hook: bool = False,
        **m_configs: ty.Unpack[MetaConfig],
    ):
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

        config = namespace.get(
            "__meta_config__", {}
        )  # BUG: this currently does not work

        current_m_config = {
            k: m_configs[k] for k in m_configs if k in DATACLASS_DEFAULT_KW
        }
        current_f_config = {
            k: m_configs[k] for k in m_configs if k in FIELDS_DEFAULT_KW
        }

        model_config = DATACLASS_DEFAULT_KW | base_m_params | current_m_config | config
        field_config = FIELDS_DEFAULT_KW | base_f_params | current_f_config | config

        if field_params := getattr(raw_cls, FIELDS_PARAMS, {}):
            field_config |= field_params

        setattr(raw_cls, FIELDS_PARAMS, field_config)
        cls_config = model_config | field_config

        if "__repr__" in namespace:
            cls_config["repr"] = False

        if cls_config["slots"]:
            cls_ = create_slots_struct(raw_cls, cls_config)
        else:
            cls_ = _process_class(raw_cls, **cls_config)

        # TODO: extract imtypes from cls_config
        if cls_config["frozen"] and not is_class_immutable(cls_, imtypes=[]):
            raise MutableFieldError

        return cls_

    def __call__(obj_type, *args, **kwargs):
        if args:
            raise ArgumentError

        pre_init = getattr(
            obj_type,
            "__pre_init__",
            None,
        )
        if callable(pre_init):
            kwargs = pre_init(**kwargs) if kwargs is not None else kwargs

        obj = super().__call__(**kwargs)
        return obj


class Struct(metaclass=StructMeta, kw_only=True):
    ...

    # @classmethod
    # def validate_all(cls, **kwargs) -> dict:
    #     ...

    # @classmethod
    # def __pre_init__(cls, **kwargs) -> dict:
    #     return cls.validate_all(**kwargs)


@ty.dataclass_transform(kw_only_default=True, frozen_default=False)
class FrozenStruct(metaclass=StructMeta, kw_only=True, frozen=True, slots=True):
    ...

    def but(self, **kw_attrs):
        # TODO: return a new object with current attributes + kw_attrs
        return self.__class__(*kw_attrs)


class ConfigBase(FrozenStruct):  # type: ignore
    def __repr__(self):
        return pretty_repr(self)

    @classmethod
    def from_env(cls, filename=".env"):
        parsed_result = parse_config(cls, read_env(filename=filename))
        return cls(**parsed_result)
