"""Sidebar configuration; SQL still controls all result columns."""
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).with_name("search_fields")
OPERATORS = {
    "text": ["Equals", "In", "Does not equal", "Contains", "Does not contain", "Starts with", "Is empty", "Is not empty"],
    "number": ["Equals", "Greater than", "Less than", "At least", "At most", "Is empty", "Is not empty"],
    "date": ["On", "Before", "After", "Within last (days)", "Is empty", "Is not empty"],
}


def load_sidebar_fields(groups, config_dir=CONFIG_DIR):
    sidebar, operators = {}, {}
    for group, filename in [("Case Details", "case_fields.json"),
                            ("Claim Details", "claim_fields.json")]:
        config = json.loads((config_dir / filename).read_text(encoding="utf-8"))
        fields = config.get("fields")
        if not isinstance(fields, list):
            raise ValueError(f"{filename}: fields must be a list")
        available = {label: (key, label, kind) for key, label, kind in groups[group]}
        sidebar[group] = []
        seen = set()
        for field in fields:
            if not isinstance(field, dict):
                raise ValueError(f"{filename}: each field must be an object")
            name = field.get("field")
            if not isinstance(name, str) or name not in available:
                raise ValueError(f"{filename}: {name!r} must match a SELECT alias exactly")
            if name in seen:
                raise ValueError(f"{filename}: duplicate field {name!r}")
            seen.add(name)
            key, label, kind = available[name]
            choices = field.get("operators")
            if (not isinstance(choices, list) or not choices
                    or any(not isinstance(op, str) or op not in OPERATORS[kind] for op in choices)
                    or len(choices) != len(set(choices))):
                raise ValueError(f"{filename}: invalid operators for {name!r} ({kind})")
            sidebar[group].append((key, label, kind))
            operators[key] = choices
    return sidebar, operators
