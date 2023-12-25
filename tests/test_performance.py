from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter

from pydantic import BaseModel

from baozi import FrozenStruct, Struct


class Timer:
    def __init__(self, floor: float = 0, precision: int = 3):
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
def timer(floor: float = 0, precision: int = 3):
    with Timer(floor=floor, precision=precision) as t:
        yield t
    t.show()


TRIALS = 10**6


class PlainPythonClass:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


@dataclass
class DataClass:
    name: str
    age: int


class BaoziStruct(Struct):
    name: str
    age: int


class BaoziFrozenStruct(FrozenStruct):
    name: str
    age: int


# pydantic.__version__ == '2.5.2'
class PydanticModel(BaseModel):
    name: str
    age: int


def test_performan_ranking():
    with timer() as plainpyclass:
        for _ in range(TRIALS):
            PlainPythonClass(name="a", age=2)

    with timer() as dataclass:
        for _ in range(TRIALS):
            DataClass(name="a", age=2)

    with timer() as baozistruct:
        for _ in range(TRIALS):
            BaoziStruct(name="a", age=2)

    with timer() as pydanticbase:
        for _ in range(TRIALS):
            PydanticModel(name="a", age=2)

    ECHELON = 0.1

    assert abs(plainpyclass.result - dataclass.result) < ECHELON
    assert plainpyclass.result < baozistruct.result < pydanticbase.result

    print(
        f"PlainPythonClass: {plainpyclass.result} seconds\n"
        f"DataClass: {dataclass.result} seconds\n"
        f"BaoziFrozenStruct: {baozistruct.result} seconds\n"
        f"PydanticModel: {pydanticbase.result} seconds\n"
    )
