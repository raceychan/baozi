class InvalidType(Exception):
    def __init__(self, attr_name, type_) -> None:
        self.attr_name = attr_name
        self.type_ = type_

    def __str__(self) -> str:
        msg = f"Attribute {self.attr_name} of type {self.type_} is mutable"
        return msg


class ArgumentError(Exception):
    def __str__(self):
        msg = f"Positional arguments are not allowed"
        return msg


class ImmutableFieldError(TypeError):
    ...
