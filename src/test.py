from domino import Struct


class Base(Struct):
    age: int
    name: str

base = Base(age=3, name='a')
print(base)
