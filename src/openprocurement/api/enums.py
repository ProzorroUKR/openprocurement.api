from collections.abc import Iterable


def enum_members(values: Iterable[str]) -> dict[str, str]:
    """
    Members for an enum generated from a list of values (a constant or data of the standards):
    `OraCode = StrEnum("OraCode", enum_members(ORA_CODES))`
    The names are generated: a value isn't always a valid member name ("", "mro").
    """
    return {f"VALUE_{index}": value for index, value in enumerate(dict.fromkeys(values))}
