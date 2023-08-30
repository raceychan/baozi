from domino import Struct, FrozenInstanceError, FrozenStruct, is_field_immutable

if not is_field_immutable(tuple[str, ...]):
    raise Exception


class Base(Struct, kw_only=True):
    age: int = 15
    name: str

    # config = MetaConfig(frozen=True)


class Time(Base):
    money: int = 0
    addres: str


class Freeze(FrozenStruct):
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

    try:
        f.age = 16
    except FrozenInstanceError:
        pass
    else:
        raise Exception("FrozenInstanceError not raised")


def test_subclass_frozen():
    cf = CoolF(name="cool", age=15, address="address")


def test_frozen_immutable():
    wf = WF(name="wf", age=15, names=("a", "b", "c"))


def test_is_field_immutable(attr_type):
    return is_field_immutable(attr_type)


def test():
    test_struct()
    test_subclass_struct()
    test_frozen()
    test_subclass_frozen()
    test_frozen_immutable()


if __name__ == "__main__":
    test()
