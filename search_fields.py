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
TABLE_SOURCE_ALIASES = {
    "case_table": "c",
    "case_details_table": "cd",
    "claim_table": "cl",
    "provider_table": "p",
    "decision_table": "d",
    "focus_table": "f",
}

_category_configs = []
_seen_categories = set()
_seen_orders = set()
for _config_path in CONFIG_DIR.glob("*.json"):
    _category_config = json.loads(_config_path.read_text(encoding="utf-8"))
    _group_name = _category_config.get("category")
    _order = _category_config.get("order")
    _fields = _category_config.get("fields")
    _query = _category_config.get("query")
    _result_key = _category_config.get("result_key")
    if not isinstance(_group_name, str) or not _group_name.strip():
        raise ValueError(f"{_config_path.name} must define a non-empty category")
    if not isinstance(_order, int) or isinstance(_order, bool) or _order < 0:
        raise ValueError(f"{_config_path.name} must define a non-negative integer order")
    if not isinstance(_fields, list):
        raise ValueError(f"{_config_path.name} must define a list of fields")
    if not isinstance(_query, dict):
        raise ValueError(f"{_config_path.name} must define a query object")
    _query_file = _query.get("file")
    _table_setting = _query.get("table_setting")
    _source_alias = _query.get("source_alias")
    if not isinstance(_query_file, str) or Path(_query_file).name != _query_file or not _query_file.endswith(".sql"):
        raise ValueError(f"{_config_path.name} must define a local SQL filename")
    if _table_setting not in TABLE_SOURCE_ALIASES or _source_alias != TABLE_SOURCE_ALIASES[_table_setting]:
        raise ValueError(f"{_config_path.name} has an unsupported Oracle table mapping")
    if not isinstance(_result_key, str) or not _result_key.strip():
        raise ValueError(f"{_config_path.name} must define a result_key")
    if _group_name in _seen_categories:
        raise ValueError(f"Duplicate search field category: {_group_name}")
    if _order in _seen_orders:
        raise ValueError(f"Duplicate search field category order: {_order}")
    _seen_categories.add(_group_name)
    _seen_orders.add(_order)
    _category_configs.append((_order, _group_name, _fields, _query_file, _table_setting, _source_alias, _result_key))

if not _category_configs:
    raise ValueError(f"No category JSON files found in {CONFIG_DIR}")

SUPPORTED_RESULT_GROUPS = {config[-1] for config in _category_configs}

FIELD_GROUPS = {}
FIELD_TYPES = {}
FIELD_OPERATORS = {}
FIELD_RESULT_GROUPS = {}
FIELD_GROUP_QUERIES = {}
FIELD_GROUP_RESULT_KEYS = {}
_seen_keys = set()

for (_order, _group_name, _fields, _query_file, _table_setting,
     _source_alias, _result_key) in sorted(_category_configs):
    FIELD_GROUPS[_group_name] = []
    FIELD_GROUP_QUERIES[_group_name] = {
        "file": _query_file,
        "table_setting": _table_setting,
        "source_alias": _source_alias,
    }
    FIELD_GROUP_RESULT_KEYS[_group_name] = _result_key
    for _field in _fields:
        if not isinstance(_field, dict):
            raise ValueError(f"Fields in {_group_name!r} must be JSON objects")

        _key = _field.get("key")
        _label = _field.get("label")
        _field_type = _field.get("type")
        _operators = _field.get("operators")
        _result_groups = _field.get("result_groups", [])
        if isinstance(_result_groups, list) and _result_groups and set(_result_groups) <= {"cases", "claims"}:
            _result_groups = [_result_key]
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
        if not isinstance(_result_groups, list) or any(
            _group not in SUPPORTED_RESULT_GROUPS for _group in _result_groups
        ):
            raise ValueError(f"Search field {_key!r} contains an unsupported result group")
        if len(_result_groups) != len(set(_result_groups)):
            raise ValueError(f"Search field {_key!r} contains duplicate result groups")

        _seen_keys.add(_key)
        FIELD_GROUPS[_group_name].append((_key, _label, _field_type))
        FIELD_TYPES[_key] = _field_type
        FIELD_OPERATORS[_key] = list(_operators)
        FIELD_RESULT_GROUPS[_key] = list(_result_groups)
