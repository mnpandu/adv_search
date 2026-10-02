"""Load and validate the editable JSON search-field catalog."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("search_fields.json")
SUPPORTED_OPERATORS = {
    "text": {
        "Equals", "In", "Does not equal", "Contains", "Does not contain",
        "Starts with", "Is empty", "Is not empty",
    },
    "number": {
        "Equals", "Greater than", "Less than", "At least", "At most",
        "Is empty", "Is not empty",
    },
    "date": {
        "On", "Before", "After", "Within last (days)", "Is empty", "Is not empty",
    },
}

with CONFIG_PATH.open(encoding="utf-8") as config_file:
    _config = json.load(config_file)

if not isinstance(_config, dict) or not _config:
    raise ValueError("search_fields.json must contain a non-empty object of field groups")

FIELD_GROUPS = {}
FIELD_TYPES = {}
FIELD_OPERATORS = {}
_seen_keys = set()

for _group_name, _fields in _config.items():
    if not isinstance(_group_name, str) or not _group_name.strip() or not isinstance(_fields, list):
        raise ValueError("Each search field group must have a name and a list of fields")

    FIELD_GROUPS[_group_name] = []
    for _field in _fields:
        if not isinstance(_field, dict):
            raise ValueError(f"Fields in {_group_name!r} must be JSON objects")

        _key = _field.get("key")
        _label = _field.get("label")
        _field_type = _field.get("type")
        _operators = _field.get("operators")
        if not isinstance(_key, str) or not _key.strip():
            raise ValueError(f"A field in {_group_name!r} is missing a non-empty key")
        if _key in _seen_keys:
            raise ValueError(f"Duplicate search field key: {_key}")
        if not isinstance(_label, str) or not _label.strip():
            raise ValueError(f"Search field {_key!r} is missing a non-empty label")
        if _field_type not in SUPPORTED_OPERATORS:
            raise ValueError(f"Search field {_key!r} has unsupported type: {_field_type!r}")
        if not isinstance(_operators, list) or not _operators:
            raise ValueError(f"Search field {_key!r} must define at least one operator")
        if any(not isinstance(_operator, str) or _operator not in SUPPORTED_OPERATORS[_field_type]
               for _operator in _operators):
            raise ValueError(f"Search field {_key!r} contains an unsupported operator")
        if len(_operators) != len(set(_operators)):
            raise ValueError(f"Search field {_key!r} contains duplicate operators")

        _seen_keys.add(_key)
        FIELD_GROUPS[_group_name].append((_key, _label, _field_type))
        FIELD_TYPES[_key] = _field_type
        FIELD_OPERATORS[_key] = list(_operators)
