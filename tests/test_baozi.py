from dataclasses import FrozenInstanceError, asdict, field

import pytest

import baozi
from baozi.frozen import is_field_immutable


class Base(baozi.Struct, kw_only=True):
    age: int = 15
    name: str

    @classmethod
    def __pre_init__(cls, **data):
        return data

    __meta_config__ = baozi.MetaConfig(frozen=False)


class Time(Base, flyweight=True):
    money: int = 0
    addres: str


class Freeze(baozi.FrozenStruct):
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
    with pytest.raises(baozi.MutableFieldError):

        class Mutable(baozi.FrozenStruct):
            address: list[str]


def field_is_immutable(attr_type):
    return is_field_immutable(attr_type)


def test_event():
    from dataclasses import field
    from datetime import datetime

    class Event(baozi.FrozenStruct):
        name: str
        created_at: datetime = field(default_factory=datetime.now)

    e = Event(name="event")
    assert isinstance(e.created_at, datetime)


def test_read_attribute():
    baozi.read_attributes({"name": "name", "age": 15})
    baozi.read_attributes(Base(name="name", age=15))
    baozi.read_attributes(Freeze(name="name", age=15))
    baozi.read_attributes(tuple)


def test_pretty_repr():
    baozi.pretty_repr(Freeze(name="name", age=15))
    baozi.pretty_repr(Base(name="name", age=15))
    assert Freeze.__meta_config__["frozen"] == True


def test_pre_init():
    class A(baozi.Struct):
        name: str
        age: int

        @classmethod
        def __pre_init__(cls, **data):
            data["name"] = "test"
            return data

    assert asdict(A(name="name", age=15)) == {"name": "test", "age": 15}


def test_arg_error():
    class B(baozi.Struct):
        name: str
        age: int

    with pytest.raises(baozi.ArgumentError):
        B("name", age=15, address="address")


def test_freeze_but():
    f = Freeze(name="name", age=15)
    f2 = f.but(name="name2")
    assert f2.name == "name2" and f2.age == 15


def test_type_coerce_error():
    class Config(baozi.ConfigBase):
        name: str
        age: int

    config = {"name": "name", "age": "a"}

    try:
        baozi.parse_config(Config, config)
    except baozi.TypeCoerceError as tce:
        print(tce)
    else:
        raise Exception("Should not reach here")

    try:
        baozi.parse_config(Config, {"name": "name"})
    except baozi.ValueNotFoundError as vnf:
        print(vnf)
    else:
        raise Exception("Should not reach here")

    new_config = {"name": "name", "age": "15"}
    c = Config.parse(new_config)
    print(c)

    e = baozi.parse_config(baozi.FrozenStruct, {})


def test_error():
    e = baozi.InvalidTypeError("name", type)
    str(e)
    age = baozi.ArgumentError()
    str(age)


def test_immutable_check():
    assert is_field_immutable(tuple[str, ...], imtypes=[])

    assert not is_field_immutable(list[str], imtypes=[])

    class Base:
        name: str
        names: tuple[str]

    assert is_field_immutable(Base, imtypes=[])

    from collections import deque
    from datetime import datetime

    class C:
        b: Base
        d: datetime
        q: deque

    with pytest.raises(baozi.InvalidTypeError):
        is_field_immutable(C)

    assert is_field_immutable(C, imtypes=[deque])


from baozi.slots import _add_slots, _dataclass_getstate, _dataclass_setstate, _get_slots


def test_get_slots_with_defined_slots():
    class TestClass:
        __slots__ = ("a", "b", "c")

    slots = list(_get_slots(TestClass))
    assert slots == ["a", "b", "c"]


def test_get_slots_with_no_slots():
    class TestClass:
        pass

    slots = list(_get_slots(TestClass))
    assert slots is None or slots == []


def test_get_slots_with_invalid_slots():
    with pytest.raises(TypeError):

        class TestClass:
            __slots__ = str  # Invalid, should be an iterable


def test_slost_error():
    class TestDataClass(baozi.FrozenStruct):
        name: str
        age: int
        active: bool

    test_instance = TestDataClass(name="John", age=30, active=True)
    state = _dataclass_getstate(test_instance)
    assert state == ["John", 30, True]

    new_state = ["Orange", 5]
    _dataclass_setstate(test_instance, new_state)
    assert test_instance.name == "Orange"
    assert test_instance.age == 5

    with pytest.raises(TypeError):

        class B(baozi.FrozenStruct):
            __slots__ = ("name", "age", "active")

    with pytest.raises(TypeError):

        class C(baozi.FrozenStruct):
            __slots__ = int


class MyTestDataClass(baozi.Struct):
    name: str = field(default="Unknown")
    age: int = field(repr=False)
    active: bool = field(compare=False)


def test_field():
    test_instance = MyTestDataClass(age=30, active=True)
    assert test_instance.name == "Unknown"
    assert test_instance.age == 30
    assert test_instance.active is True


def test_field_repr():
    test_instance = MyTestDataClass(age=30, active=True)
    assert "age" not in repr(test_instance)


def test_field_compare():
    instance1 = MyTestDataClass(name="John", age=30, active=True)
    instance2 = MyTestDataClass(name="John", age=25, active=False)
    # Even though 'active' is different, comparison should only consider 'name' and 'age'
    assert instance1 != instance2  # Different 'age'
    instance2.age = 30
    assert instance1 == instance2  # Same 'name' and 'age', despite different 'active'
