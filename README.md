# Introduction

**domino is a thin wrapper around python's builtin dataclass, which offers extract features like:**

- inheritance
- immutability
- typecasting(experimental)
- keyword-only arguments and random order attributes

# Installation

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

# Usage

## 1. Usage of plain Struct

```python
from domino import Struct

class Person(Struct, kw_only=True):
    age: int = 15
    name: str

p = Person(name="domino")
```

> - note here that attribute with default value does not have to show before regular attributeo
> - you might place dataclass configration directly in class inheritance

## 2. Usage of FrozenStruct

### Domino is fully compatible with dataclasses.dataclass

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
