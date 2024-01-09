# Changelog

## [0.0.6] - 2024-01-10

### Added

- User might now import 'dataclasses.field' directly from baozi for convenience

### Fixed

- Fixed a bug where a immutable type annotated by typing.ClassVar[...] in frozenstruct would raise a mutable error