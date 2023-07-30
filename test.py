from src.domino import Struct, FrozenStruct


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



"""
{
    'name': Field(name='name',type=<class 'str'>,default=<dataclasses._MISSING_TYPE object at 0x7f91a8c8f4d0>
    'age': Field(name='age',type=<class 'int'>,default=15
    'addres': Field(name='addres',type=<class 'str'>,default=<dataclasses._MISSING_TYPE object at 0x7f91a8c8f4d0>
    'money': Field(name='money',type=<class 'int'>,default=0
}
"""


def test():
    ...


if __name__ == "__main__":
    test()
