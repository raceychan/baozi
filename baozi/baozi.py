import inspect
import sys
import typing as ty
from dataclasses import MISSING as MISSING
from dataclasses import _process_class as _process_class  # type: ignore
from dataclasses import asdict, is_dataclass
from dataclasses import field as field
from types import MethodType as MethodType

from .error import ArgumentError, InvalidTypeError, MutableFieldError
from .frozen import is_class_immutable
from .slots import create_slots_struct
from .typecast import parse_config

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


FIELDS_PARAMS = "__BAOZI_FIELD_PARAMS__"


class SlotProtocol(ty.Protocol):
    __slots__: tuple[str, ...]


class _MISSING_DEFAULT:
    ...


MISSING_DEFAULT = _MISSING_DEFAULT()


def read_slots(obj: SlotProtocol):
    slots = {key: getattr(obj, key) for key in obj.__slots__ if not key.startswith("_")}
    return slots


def read_attributes(obj) -> ty.Mapping:
    if isinstance(obj, dict):
        return obj

    try:
        obj_attrs = obj.__dict__
    except AttributeError:
        pass
    else:
        return {key: val for key, val in obj_attrs.items() if not key.startswith("_")}

    obj_slots = obj.__slots__

    return {key: getattr(obj, key) for key in obj_slots if not key.startswith("_")}


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


class MetaConfig(ty.TypedDict):
    init: ty.NotRequired[bool]  # = True
    repr: ty.NotRequired[bool]  # = True
    eq: ty.NotRequired[bool]  # = True
    order: ty.NotRequired[bool]  # = False
    unsafe_hash: ty.NotRequired[bool]  # = False
    frozen: ty.NotRequired[bool]  # = False
    match_args: ty.NotRequired[bool]  # = True
    kw_only: ty.NotRequired[bool]  # = False
    slots: ty.NotRequired[bool]  # = False
    flyweight: ty.NotRequired[bool]  # = False


BAOZI_META_TYPE: tuple[type] = (MetaConfig,)


@ty.dataclass_transform(kw_only_default=True)
class StructMeta(type):
    __meta_config__: ty.ClassVar[MetaConfig]

    def __new__(
        meta_cls: type["StructMeta"],  # type: ignore
        cls_name: str,
        bases: tuple,
        namespace: dict,
        _baozi_subinit_hook: bool = False,
        **m_configs: ty.Unpack[MetaConfig],
    ):
        if _baozi_subinit_hook:
            raw_cls = super().__new__(meta_cls, cls_name, bases, namespace)
            return raw_cls

        if user_defined_slot := namespace.get("__slots__", False):
            if not isinstance(user_defined_slot, ty.Iterable):
                raise TypeError("__slots__ must be iterable")

        raw_cls = super().__new__(meta_cls, cls_name, bases, namespace)

        base_m_params = dict()
        base_f_params = dict()
        for base in bases:
            if is_dataclass(base):
                base_m_params.update(get_dc_params(base))
                base_f_params.update(getattr(base, FIELDS_PARAMS, {}))

        meat_config = namespace.get("__meta_config__", {})

        current_m_config = {
            k: v for k, v in m_configs.items() if k in DATACLASS_DEFAULT_KW
        }
        current_f_config = {
            k: v for k, v in m_configs.items() if k in FIELDS_DEFAULT_KW
        }

        model_config = (
            DATACLASS_DEFAULT_KW | base_m_params | current_m_config | meat_config
        )
        field_config = (
            FIELDS_DEFAULT_KW | base_f_params | current_f_config | meat_config
        )

        if field_params := getattr(raw_cls, FIELDS_PARAMS, {}):
            field_config |= field_params

        setattr(raw_cls, FIELDS_PARAMS, field_config)
        cls_config = model_config | field_config

        # configs are all set

        if "__repr__" in namespace:
            cls_config["repr"] = False

        if cls_config["slots"]:
            cls_ = create_slots_struct(raw_cls, cls_config)
        else:
            cls_ = _process_class(raw_cls, **cls_config)

        # TODO: extract imtypes from cls_config
        if cls_config["frozen"]:
            try:
                is_class_immutable(cls_, imtypes=BAOZI_META_TYPE)
            except InvalidTypeError as it:
                raise MutableFieldError(it.attr_name, it.type_) from it

        pre_init: ty.Callable | None = getattr(cls_, "__pre_init__", None)

        if pre_init is not None:
            if not (inspect.ismethod(pre_init) and pre_init.__self__ is cls_):
                raise TypeError(
                    f"__pre_init__ must be a class method of {cls_.__name__}"
                )

            def new_call(obj_type: type, *args, **kwargs):
                if args:
                    raise ArgumentError

                return super().__call__(**pre_init(**kwargs))  # type: ignore

        else:

            def new_call(obj_type: type, *args, **kwargs):
                if args:
                    raise ArgumentError
                return super().__call__(**kwargs)  # type: ignore

        meta_cls.__call__ = new_call  # type: ignore
        return cls_


class Struct(metaclass=StructMeta):
    __meta_config__: ty.ClassVar[MetaConfig] = MetaConfig(kw_only=True)


# TODO: add flyweight support for frozen
@ty.dataclass_transform(kw_only_default=True, frozen_default=True)
class FrozenStruct(metaclass=StructMeta):
    __meta_config__: ty.ClassVar[MetaConfig] = MetaConfig(
        kw_only=True, frozen=True, slots=True
    )

    def but(self, **kw_attrs):
        data = asdict(self)
        updated = data | kw_attrs
        return self.__class__(**updated)


class ConfigBase(FrozenStruct):  # type: ignore
    def __repr__(self):
        return pretty_repr(self)

    @classmethod
    def parse(cls, config: ty.Mapping[str, ty.Any]):
        return cls(**parse_config(cls, config))
