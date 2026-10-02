"""Load and validate the editable JSON search-field catalog."""
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).with_name("search_fields")
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

_category_configs = []
_seen_categories = set()
_seen_orders = set()
for _config_path in CONFIG_DIR.glob("*.json"):
    _category_config = json.loads(_config_path.read_text(encoding="utf-8"))
    _group_name = _category_config.get("category")
    _order = _category_config.get("order")
    _fields = _category_config.get("fields")
    if not isinstance(_group_name, str) or not _group_name.strip():
        raise ValueError(f"{_config_path.name} must define a non-empty category")
    if not isinstance(_order, int) or isinstance(_order, bool) or _order < 0:
        raise ValueError(f"{_config_path.name} must define a non-negative integer order")
    if not isinstance(_fields, list):
        raise ValueError(f"{_config_path.name} must define a list of fields")
    if _group_name in _seen_categories:
        raise ValueError(f"Duplicate search field category: {_group_name}")
    if _order in _seen_orders:
        raise ValueError(f"Duplicate search field category order: {_order}")
    _seen_categories.add(_group_name)
    _seen_orders.add(_order)
    _category_configs.append((_order, _group_name, _fields))

if not _category_configs:
    raise ValueError(f"No category JSON files found in {CONFIG_DIR}")

FIELD_GROUPS = {}
FIELD_TYPES = {}
FIELD_OPERATORS = {}
_seen_keys = set()

for _order, _group_name, _fields in sorted(_category_configs):
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
