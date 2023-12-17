# Introduction

**domino is a thin wrapper around python's builtin dataclass, which offers extract features like:**

- inheritance
- immutability
- typecasting(experimental)
- keyword-only arguments and random order attributes

## Rationale of existence

## why would I choose this over dataclass?

Mostly because of **the decorator** approach, dataclass uses decorators for transforming a regular class into a dataclass, and when I use dataclass in production, I soon realize that:

1. Code repetition, when there are tons of dataclasses, you are going to decorate them with `@dataclass` over and over again

2. Error-prone, for non-trivial application, you often have different configuration of dataclass, like `@dataclass(frozen)`, if you inherit from a frozen dataclass and you use regular `@dataclass` decorator, odds are you are going to have a bad time.

3. It simply does not make sense to use decorator, when you decorating a class, it implies that your class would work just fine without the decorator, and that is not the case, if you get rid of the `@dataclass` decorator, your class won't work.

## why would I choose this over pydantic.BaseModel?

Mostly because of **You don't need validation**

pydantic is very powerful and strong and I use it in various projects, but there are
certain scenarios where I find pydantic to be an overkill.

1. **Data are already validated** in the API layer, and once the input goes through API and penetrate into my application layer, i know those data are safe, cause they are generated by my code.

2. **performance**, despite how performant pydantic is, depending on complexity, it is ususally 5x to 100x times slower than a dataclass, which is essentially a regular python class. you dont event need an advanced bench test mark to verify, just copy this into a jupyter notebook

```python
from dataclasses import dataclass
from pydantic import BaseModel

class B:
    def __init__(self, name: str, age:int):
        self.name = name
        self.age = age
@dataclass
class T:
    name: str
    age: int

class P(BaseModel):
    name: str
    age: int
```

```python
%%timeit
>>> B(name="a",age=2)
104 ns ± 0.992 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)


%%timeit
>>> T(name="a",age=2)
102 ns ± 0.941 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)


%%timeit
>>> P(name="a", age=2)
515 ns ± 9.23 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)
```

## Installation

1. clone the source code to your chosen folder

```bash
mkdir domino && cd domino
git clone git@github.com:raceychan/domino.git
```

2. install the source code from the folder

```bash
pip install -e .
```

3. import domino packages in your project

```python
from domino import Struct

# Your Code
```

## Usage

## 1. Usage of plain Struct

```python
from domino import Struct

class Person(Struct, kw_only=True):
    age: int = 15
    name: str

p = Person(name="domino")
```

> - Note here that attribute with default value does not have to show before regular attributeo
> - You might place dataclass configration directly in class inheritance

## 2. Usage of FrozenStruct

### Domino is fully compatible with dataclasses.dataclass

```python
from dataclass import is_dataclass
from domino import FrozenStruct

assert is_dataclass(FrozenStruct)
```

### FrozenStruct is equal to dataclass(frozen=True, slots=True, kw_only=True)

```python
from domino import FrozenStruct, field
from datetime import datetime

class Event(FrozenStruct):
    name: str
    create_at: datetime = field(default_factory=datetime.now)

>> e = Event(name="event")
>> assert isinstance(e.created_at, datetime)
>> e.created_at = datetime.now()

dataclasses.FrozenInstanceError: cannot assign to field 'created_at'
```

### Defining FrozenStruct with mutable fields would raise error

> since any mutable field would cause failure in immutability of the class

```python
from domino import FrozenStruct

class Mutable(FrozenStruct):
    address: list[str]

domino.ImmutableFieldError
```
