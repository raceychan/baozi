from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter

from pydantic import BaseModel

from baozi import FrozenStruct


class Timer:
    def __init__(self, floor=0, precision=3):
        self.result = floor
        self.precision = precision

    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = perf_counter()
        self.result = max(round(self.end - self.start, self.precision), self.result)

    def show(self):
        print(f"Time: {self.result} seconds")


@contextmanager
def timer():
    with Timer() as t:
        yield
    t.show()


TRIALS = 10**6


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


class D(FrozenStruct):
    name: str
    age: int


def test_py_class():
    with timer():
        for _ in range(TRIALS):
            B(name="a", age=2)


def test_dataclass():
    with timer():
        for _ in range(TRIALS):
            T(name="a", age=2)


def test_domino():
    with timer():
        for _ in range(TRIALS):
            D(name="a", age=2)


def test_pydantic():
    with timer():
        for _ in range(TRIALS):
            P(name="a", age=2)
