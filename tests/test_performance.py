from dataclasses import dataclass

from pydantic import BaseModel


class B:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


@dataclass
class T:
    name: str
    age: int


class P(BaseModel):
    name: str
    age: int


def test_py_class():
    B(name="a", age=2)


def test_dataclass():
    T(name="a", age=2)


def test_domino():
    P(name="a", age=2)


def test_pydantic():
    P(name="a", age=2)
