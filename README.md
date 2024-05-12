# Table of Contents

- [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Extract features baozi offers](#extract-features-baozi-offers)
  - [Installation](#installation)
  - [Usage](#usage)
  - [1. Usage of plain Struct](#1-usage-of-plain-struct)
    - [pre\_init hook](#pre_init-hook)
  - [2. Usage of FrozenStruct](#2-usage-of-frozenstruct)
    - [baozi is fully compatible with dataclasses.dataclass](#baozi-is-fully-compatible-with-dataclassesdataclass)
    - [FrozenStruct is equal to dataclass(frozen=True, slots=True, kw\_only=True)](#frozenstruct-is-equal-to-dataclassfrozentrue-slotstrue-kw_onlytrue)
    - [Defining FrozenStruct with mutable fields would raise error](#defining-frozenstruct-with-mutable-fields-would-raise-error)
    - [Technical Details](#technical-details)
      - [config override order](#config-override-order)
  - [Rationale of existence](#rationale-of-existence)
    - [why wouldn't I just use dataclass?](#why-wouldnt-i-just-use-dataclass)
    - [why wouldn't I just use pydantic.BaseModel?](#why-wouldnt-i-just-use-pydanticbasemodel)

## Introduction

'baozi' is a dataclass alternative with a greater emphasis on the 'class' aspect.

## Extract features baozi offers

- Inheritance
- Immutability
- Keyword-only arguments and random order attributes
- Support user-defined `__pre_init__` method that gets executed before object instantiation
- Typecasting(experimental)

## Installation

```bash
pip install baozi
```

## Usage

## 1. Usage of plain Struct

```python
from baozi import Struct

class Person(Struct, kw_only=True):
    age: int = 15
    name: str

p = Person(name="baozi")
```

### pre_init hook

```python
class B(baozi.Struct):
    name: str
    age: int

    @classmethod
    def __pre_init__(cls, **data):
        data["age"] = int(data["age"])
        return data

assert asdict(B(name="name", age="15")) == {"name": "name", "age": 15}
```

- Note here that attribute with default value does not have to show before regular attributeo
- You might place dataclass configration directly in class inheritance
- configs will be passed to subclasses

- config class meta by passing class arguments or defining `__model_config__` field in the class

## 2. Usage of FrozenStruct

### baozi is fully compatible with dataclasses.dataclass

```python
from dataclass import is_dataclass
from baozi import FrozenStruct

assert is_dataclass(FrozenStruct)
```

### FrozenStruct is a more powerful alternative to dataclass(frozen=True, slots=True, kw_only=True)

```python
from baozi import FrozenStruct, field
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
from baozi import FrozenStruct

class Mutable(FrozenStruct):
    address: list[str]

baozi.MutableFieldError
```

### Technical Details

#### config override order

baozi receive config in following order:

1. config defined explicitly using `__model_config__` field defined in the class
2. config defined in the inheritance params
3. config defined in the parent class of current class
4. default config of baozi, which goes like this:

```python
init=True
repr=True
eq=True
order=False
unsafe_hash=False
frozen=False
match_args=True
kw_only=True
slots=False
```

Struct default:
kw_only=True

FrozenStruct defaults:
kw_only=True
frozen=True
slots=True

## Rationale of existence

### why wouldn't I just use dataclass?

Mostly because of the **decorator** approach python builtin dataclass takes, dataclass uses decorators for transforming a regular class into a dataclass, and this would lead to:

1. Code repetition, when there are tons of dataclasses, you are going to decorate them with `@dataclass` over and over again

2. Error-prone, for non-trivial application, you often have different configuration of dataclass, like `@dataclass(frozen)`, if you inherit from a frozen dataclass and you use regular `@dataclass` decorator, odds are you are going to have a bad time.

3. It simply does not make sense to use decorator, when you decorating a class, it implies that your class would still work without the decorator, and that is not the case, if you get rid of the `@dataclass` decorator, your class won't work.

### why wouldn't I just use pydantic.BaseModel?

Mostly because of **You don't need validation**, and you can use both.

pydantic is very powerful and strong and I use it in various projects, but there are
certain scenarios where I find pydantic to be an overkill.

1. **Data are already validated** in the API layer, and once the input goes through API and penetrate into my application layer, i know those data are safe, cause they are generated by my code.

2. **performance**, despite how performant pydantic is, depending on complexity, it is ususally 5x to 100x times slower than a dataclass, which is essentially a regular python class. baozi is constantly faster than pydantic, especially for model with complex validation logic(since baozi does not validate by default),  baozi also support usage of slots, which effciently cut about 1/3 of memory usage comparing to regular python class.
