import itertools
from dataclasses import fields, _process_class


def _get_slots(cls):
    match cls.__dict__.get("__slots__"):
        case None:
            return
        case str(slot):
            yield slot
        # Slots may be any iterable, but we cannot handle an iterator
        # because it will already be (partially) consumed.
        case iterable if not hasattr(iterable, "__next__"):
            yield from iterable
        case _:
            raise TypeError(f"Slots of '{cls.__name__}' cannot be determined")


def _dataclass_getstate(self):
    return [getattr(self, f.name) for f in fields(self)]


def _dataclass_setstate(self, state):
    for field, value in zip(fields(self), state):
        # use setattr because dataclass may be frozen
        object.__setattr__(self, field.name, value)


def _add_slots(cls, is_frozen, weakref_slot):
    # Need to create a new class, since we can't set __slots__
    #  after a class has been created.

    # Make sure __slots__ isn't already set.
    if "__slots__" in cls.__dict__:
        raise TypeError(f"{cls.__name__} already specifies __slots__")

    # Create a new dict for our new class.
    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in fields(cls))
    # Make sure slots don't overlap with those in base classes.
    inherited_slots = set(
        itertools.chain.from_iterable(map(_get_slots, cls.__mro__[1:-1]))
    )
    # The slots for our class.  Remove slots from our base classes.  Add
    # '__weakref__' if weakref_slot was given, unless it is already present.
    cls_dict["__slots__"] = tuple(
        itertools.filterfalse(
            inherited_slots.__contains__,
            itertools.chain(
                # gh-93521: '__weakref__' also needs to be filtered out if
                # already present in inherited_slots
                field_names,
                ("__weakref__",) if weakref_slot else (),
            ),
        ),
    )

    for field_name in field_names:
        # Remove our attributes, if present. They'll still be
        #  available in _MARKER.
        cls_dict.pop(field_name, None)

    # Remove __dict__ itself.
    cls_dict.pop("__dict__", None)

    # And finally create the class.
    qualname = getattr(cls, "__qualname__", None)
    # NOTE: This would trigger another __new__ call, which leades to calling every function in the call stack
    # cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    # chagned to:
    # cls = type(cls).__base__(cls.__name__, cls.__bases__, cls_dict)
    # does not work, since would call the __new__ of type, which we have not control over
    cls = type(cls)(cls.__name__, cls.__bases__, cls_dict, _domino_subinit_hook=True)
    if qualname is not None:
        cls.__qualname__ = qualname

    if is_frozen:
        # Need this for pickling frozen classes with slots.
        cls.__getstate__ = _dataclass_getstate
        cls.__setstate__ = _dataclass_setstate

    return cls


def create_slots_struct(raw_cls: type, cls_config: dict):
    # BUG: _process_class for FrozenStruct would evoke another __new__ when slots=True
    # and in the second time, kwargs would be None
    # and it thus would no longer be frozen
    """
    1. create a dataclass with slots being False
    2. create another dataclass with slots using previous dataclass
    3. return the new class
    """

    cls_config.update(slots=False)
    dtc = _process_class(raw_cls, **cls_config)

    slot_dtc = _add_slots(
        dtc, is_frozen=cls_config["frozen"], weakref_slot=cls_config["weakref_slot"]
    )

    return slot_dtc
