domino.ImmutableFieldError# Introduction

## Domino

domino is a thin wrapper around python's builtin dataclass, which offers extract features like:

1. inheritance
2. immutability
3. typecasting
4. keyword-only arguments and random order attributes

# Usage

## Usage of plain Struct

```python
from domino import Struct

class Person(Struct, kw_only=True):
    age: int = 15
    name: str

p = Person(name="domino")
```

> - note here that you can put attribute with default value before regular attributeo
> - put dataclass configration directly in class inheritance

## Usage of FrozenStruct

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

```python
from domino import FrozenStruct

class Mutable(FrozenStruct):
    address: list[str]

domino.ImmutableFieldError
```
