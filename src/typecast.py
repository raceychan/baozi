from pathlib import Path
from typing import Any, ClassVar, Protocol, get_type_hints


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict]


class TypeCoerceError(Exception):
    def __init__(self, attr_name: str, attr_type: type):
        self.attr_name = attr_name
        self.attr_type = attr_type

    def __str__(self):
        return f"Value {self.attr_name} cannot be coerced into type {self.attr_type}"


class ValueNotFoundError(Exception):
    def __init__(self, missed_val):
        self.missed_val = missed_val

    def __str__(self):
        return f"Value {self.missed_val} is not found"


def parse_config(config, values: dict) -> dict:
    attrs = get_type_hints(config).items()
    if not attrs:
        return {}

    config_dict = dict()
    for attr_name, attr_type in attrs:
        if (val := values.get(attr_name)) == None:
            raise ValueNotFoundError(attr_name)
        try:
            config_dict[attr_name] = attr_type(val)
        except ValueError as ve:
            raise TypeCoerceError(attr_name, attr_type)
    return config_dict


def read_env(filename: str = ".env") -> dict[str, Any]:
    file = Path(__file__).parent / filename
    if not file.exists():
        raise Exception(f"{filename} not found")

    def parse(val: str):
        if val[0] in {'"', "'"}:  # Removing quotes if they exist
            if val[0] == val[-1]:
                value = val[1:-1]
            else:
                raise ValueError(f"{val} inproperly quoted")

        # Type casting
        if val.isdecimal():
            value = int(val)  # Integer type
        elif val.lower() in {"true", "false"}:
            value = val.lower() == "true"  # Boolean type
        else:
            if val[0].isdecimal():  # Float type
                try:
                    value = float(val)
                except ValueError as ve:
                    pass
                else:
                    return value
            value = val  # Otherwise, string type
        return value

    config = {}
    ln = 1

    with file.open() as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    key, value = line.split("=", 1)
                    config[key.strip()] = parse(value.strip())
                except ValueError as ve:
                    raise ValueError(f"Invalid env line number {ln}: {line}") from ve
            ln += 1
    return config
