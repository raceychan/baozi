import pathlib
from dataclasses import FrozenInstanceError

import pytest

import domino
import typecast
from frozen import is_field_immutable

if not is_field_immutable(tuple[str, ...], imtypes=[]):
    raise Exception


class Base(domino.Struct, kw_only=True):
    age: int = 15
    name: str

    @classmethod
    def __pre_init__(cls, **data):
        return data

    __meta_config__ = domino.MetaConfig(frozen=False)


class Time(Base, flyweight=True):
    money: int = 0
    addres: str


class Freeze(domino.FrozenStruct):
    name: str = "freeze"
    age: int


class CoolF(Freeze):
    address: str


class WF(Freeze):
    names: tuple[str, ...]


"""
{
    'name': Field(name='name',type=<class 'str'>,default=<dataclasses._MISSING_TYPE object at 0x7f91a8c8f4d0>
    'age': Field(name='age',type=<class 'int'>,default=15
    'addres': Field(name='addres',type=<class 'str'>,default=<dataclasses._MISSING_TYPE object at 0x7f91a8c8f4d0>
    'money': Field(name='money',type=<class 'int'>,default=0
}
"""


def test_struct():
    b = Base(name="base")
    b.age = 16
    assert b.name == "base" and b.age == 16


def test_subclass_struct():
    t = Time(name="time", addres="addres")
    assert t.name == "time" and t.addres == "addres" and t.money == 0


def test_frozen():
    f = Freeze(name="freeze", age=15)
    assert f.name == "freeze" and f.age == 15

    with pytest.raises(FrozenInstanceError):
        f.age = 16


def test_subclass_frozen():
    cf = CoolF(name="cool", age=15, address="address")


def test_frozen_immutable():
    wf = WF(name="wf", age=15, names=("a", "b", "c"))
    assert wf.name == "wf" and wf.age == 15 and wf.names == ("a", "b", "c")


def test_frozen_class_immutable():
    with pytest.raises(domino.MutableFieldError):

        class Mutable(domino.FrozenStruct):
            address: list[str]


def field_is_immutable(attr_type):
    return is_field_immutable(attr_type)


def test_event():
    from dataclasses import field
    from datetime import datetime

    class Event(domino.FrozenStruct):
        name: str
        created_at: datetime = field(default_factory=datetime.now)

    e = Event(name="event")
    assert isinstance(e.created_at, datetime)


def test_read_attribute():
    domino.read_attributes({"name": "name", "age": 15})
    domino.read_attributes(Base(name="name", age=15))
    domino.read_attributes(Freeze(name="name", age=15))
    domino.read_attributes(tuple)


def test_pretty_repr():
    domino.pretty_repr(Freeze(name="name", age=15))
    domino.pretty_repr(Base(name="name", age=15))
    assert Freeze.__meta_config__["frozen"] == True


def test_pre_init():
    class A(domino.Struct):
        name: str
        age: int

        @classmethod
        def __pre_init__(cls, **data):
            data["name"] = "test"
            return data

    assert domino.asdict(A(name="name", age=15)) == {"name": "test", "age": 15}


def test_arg_error():
    class B(domino.Struct):
        name: str
        age: int

    with pytest.raises(domino.ArgumentError):
        B("name", age=15, address="address")


def test_freeze_but():
    f = Freeze(name="name", age=15)
    f2 = f.but(name="name2")
    assert f2.name == "name2" and f2.age == 15


def test_type_coerce_error():
    class Config(domino.ConfigBase):
        name: str
        age: int

    try:
        typecast.parse_config(Config, {"name": "name", "age": "a"})
    except typecast.TypeCoerceError as tce:
        print(tce)
    else:
        raise Exception("Should not reach here")

    try:
        typecast.parse_config(Config, {"name": "name"})
    except typecast.ValueNotFoundError as vnf:
        print(vnf)
    else:
        raise Exception("Should not reach here")
