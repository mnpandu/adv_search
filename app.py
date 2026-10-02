import csv
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

import gradio as gr
from database import fetch_records
from db_config import get_settings

from search_fields import FIELD_GROUPS, FIELD_OPERATORS, FIELD_TYPES

SIDEBAR_FIELD_GROUPS = {
    group: fields for group, fields in FIELD_GROUPS.items() if group != "Case Details"
}

FIELD_LABELS = {
    field_key: label
    for fields in FIELD_GROUPS.values()
    for field_key, label, _field_type in fields
}
MATCH_MODES = ["Match all (AND)", "Match any (OR)"]

SAMPLE_RECORDS = [
    {
        "case_number": "5001001",
        "mbi": "MBR-1042",
        "provider_name": "Northside Clinic",
        "claim_number": "CLM-1001",
        "claim_status": "Finalized",
        "qc_status": "Completed",
        "qc_review_status": "Agree",
        "qc_review": "Agree",
        "qc_review_comment": "Completed",
        "focus_code": ["Coding"],
        "over_payment": 2.5,
        "reviewed_by": "pandu",
        "reviewed_dts": "2026-04-10",
    },
    {
        "case_number": "5001001",
        "mbi": "MBR-1042",
        "provider_name": "Northside Clinic",
        "claim_number": "CLM-1002",
        "claim_status": "Pending",
        "qc_status": "Returned for Corrections",
        "qc_review_status": "Returned for Corrections",
        "qc_review": "Action Required",
        "qc_review_comment": "Return for Correction",
        "focus_code": ["Clinical Determination", "Coding"],
        "over_payment": 4,
        "reviewed_by": "regine",
        "reviewed_dts": "2026-04-12",
    },
    {
        "case_number": "5002007",
        "mbi": "MBR-2088",
        "provider_name": "Lakeshore Medical",
        "claim_number": "CLM-2044",
        "claim_status": "Finalized",
        "qc_status": "Completed",
        "qc_review_status": "Agree",
        "qc_review": "Re-review",
        "qc_review_comment": "Complete",
        "focus_code": ["Other"],
        "over_payment": 1.5,
        "reviewed_by": "pandu",
        "reviewed_dts": "2026-05-02",
    },
]

RESULT_FIELDS = [
    "case_number",
    "mbi",
    "provider_name",
    "provider_number",
    "claim_number",
    "claim_status",
    "qc_status",
    "qc_review",
    "qc_review_comment",
    "focus_code",
    "over_payment",
    "reviewed_by",
    "reviewed_dts",
]
RESULT_HEADERS = [FIELD_LABELS.get(field, field.replace("_", " ").title()) for field in RESULT_FIELDS]


def _as_text(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _is_empty(value):
    return value is None or value == "" or value == []


def _within_last_days(actual_date, day_count, today=None):
    try:
        days = int(str(day_count).strip())
    except (TypeError, ValueError):
        return False
    if days < 0:
        return False
    current_date = today or date.today()
    return current_date - timedelta(days=days) <= actual_date <= current_date


def matches(record, field_key, match_operator, expected_value, today=None):
    actual_value = record.get(field_key)
    if match_operator == "Is empty":
        return _is_empty(actual_value)
    if match_operator == "Is not empty":
        return not _is_empty(actual_value)
    if _is_empty(actual_value) or expected_value is None:
        return False

    field_type = FIELD_TYPES[field_key]
    if field_type == "number":
        try:
            actual = Decimal(str(actual_value))
            expected = Decimal(str(expected_value))
        except (InvalidOperation, ValueError):
            return False
        if match_operator == "Equals":
            return actual == expected
        if match_operator == "Greater than":
            return actual > expected
        if match_operator == "Less than":
            return actual < expected
        if match_operator == "At least":
            return actual >= expected
        if match_operator == "At most":
            return actual <= expected
        return False

    actual_text = _as_text(actual_value).casefold()
    expected_text = _as_text(expected_value).casefold()
    if field_type == "date":
        try:
            actual_date = date.fromisoformat(actual_text[:10])
        except ValueError:
            return False
        if match_operator == "Within last (days)":
            return _within_last_days(actual_date, expected_value, today)
        try:
            expected_date = date.fromisoformat(expected_text[:10])
        except ValueError:
            return False
        if match_operator == "On":
            return actual_date == expected_date
        if match_operator == "Before":
            return actual_date < expected_date
        if match_operator == "After":
            return actual_date > expected_date
        return False

    if match_operator == "In":
        try:
            values = {
                item.strip().casefold()
                for item in next(csv.reader([str(expected_value)], skipinitialspace=True, strict=True))
                if item.strip()
            }
        except (csv.Error, StopIteration):
            raise ValueError('Enter comma-separated values; use double quotes for values containing commas.')
        actual_values = actual_value if isinstance(actual_value, list) else [actual_value]
        return any(_as_text(item).casefold() in values for item in actual_values)
    if match_operator == "Equals":
        return actual_text == expected_text
    if match_operator == "Does not equal":
        return actual_text != expected_text
    if match_operator == "Contains":
        return expected_text in actual_text
    if match_operator == "Does not contain":
        return expected_text not in actual_text
    if match_operator == "Starts with":
        return actual_text.startswith(expected_text)
    return False


def filter_records(records, criteria, match_mode="Match all (AND)"):
    if not criteria:
        return list(records)
    if match_mode == "Match any (OR)":
        return [
            record
            for record in records
            if any(matches(record, *criterion) for criterion in criteria)
        ]
    return [
        record
        for record in records
        if all(matches(record, *criterion) for criterion in criteria)
    ]


def _operators_for_field(field_key):
    return FIELD_OPERATORS[field_key]


def _normalize_saved_criterion(field_key, operator, value):
    if not isinstance(field_key, str) or field_key not in FIELD_LABELS:
        return None
    if not isinstance(operator, str) or operator not in _operators_for_field(field_key):
        return None
    if operator in {"Is empty", "Is not empty"}:
        return {"field": field_key, "operator": operator, "value": None}
    if value is None or value == "" or isinstance(value, bool):
        return None

    field_type = FIELD_TYPES[field_key]
    if field_type == "number":
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
        if not number.is_finite():
            return None
        normalized_value = int(number) if number == number.to_integral_value() else float(number)
    elif field_type == "date" and operator == "Within last (days)":
        try:
            normalized_value = int(str(value).strip())
        except ValueError:
            return None
        if normalized_value < 0:
            return None
    elif field_type == "date":
        try:
            normalized_value = date.fromisoformat(str(value)[:10]).isoformat()
        except ValueError:
            return None
    elif isinstance(value, str):
        normalized_value = value
    else:
        return None
    return {"field": field_key, "operator": operator, "value": normalized_value}


def _normalize_saved_search(search):
    if not isinstance(search, dict):
        return None
    name = search.get("name")
    match_mode = search.get("match_mode")
    if not isinstance(name, str) or not name.strip() or match_mode not in MATCH_MODES:
        return None

    raw_criteria = search.get("criteria")
    if not isinstance(raw_criteria, list):
        return None
    criteria = []
    for item in raw_criteria:
        if not isinstance(item, dict):
            return None
        criterion = _normalize_saved_criterion(
            item.get("field"), item.get("operator"), item.get("value")
        )
        if criterion is None:
            return None
        criteria.append(criterion)
    if not criteria:
        return None
    return {"name": name.strip(), "match_mode": match_mode, "criteria": criteria}


def _validated_saved_searches(saved_searches):
    return [
        normalized
        for item in (saved_searches or [])
        if (normalized := _normalize_saved_search(item)) is not None
    ]


def _save_search(saved_searches, name, match_mode, field_keys, field_values):
    existing = _validated_saved_searches(saved_searches)
    if not isinstance(name, str) or not name.strip() or match_mode not in MATCH_MODES:
        return existing
    if len(field_values) != len(field_keys) * 2:
        return existing

    criteria = [
        {"field": field_key, "operator": field_values[index * 2], "value": field_values[index * 2 + 1]}
        for index, field_key in enumerate(field_keys)
    ]
    saved = _normalize_saved_search({
        "name": name,
        "match_mode": match_mode,
        "criteria": criteria,
    })
    if saved is None:
        return existing
    return [
        item for item in existing if item["name"].casefold() != saved["name"].casefold()
    ] + [saved]


def _restore_saved_search(search):
    saved = _normalize_saved_search(search)
    if saved is None:
        return [*([[] for _ in SIDEBAR_FIELD_GROUPS]), MATCH_MODES[0], None]
    selected_keys = {item["field"] for item in saved["criteria"]}
    selections = [
        [field_key for field_key, _label, _kind in fields if field_key in selected_keys]
        for fields in SIDEBAR_FIELD_GROUPS.values()
    ]
    return [*selections, saved["match_mode"], saved]


def _saved_search_values(search):
    saved = _normalize_saved_search(search)
    if saved is None:
        return [], MATCH_MODES[0], []
    keys = [item["field"] for item in saved["criteria"]]
    values = [value for item in saved["criteria"] for value in (item["operator"], item["value"])]
    return keys, saved["match_mode"], values


def _load_saved_search(saved_searches, active_load, name):
    saved = next(
        (
            normalized
            for item in (saved_searches or [])
            if (normalized := _normalize_saved_search(item)) is not None
            and normalized["name"].casefold() == str(name or "").casefold()
        ),
        None,
    )
    if saved is None:
        selections = [[] for _ in SIDEBAR_FIELD_GROUPS]
        return [*selections, MATCH_MODES[0], {"search": None, "revision": 0}, ""]
    restored = _restore_saved_search(saved)
    selections, match_mode, saved = restored[:-2], restored[-2], restored[-1]
    revision = (active_load or {}).get("revision", 0) + 1
    return [
        *selections,
        match_mode,
        {"search": saved, "revision": revision},
        saved["name"],
    ]


def _delete_saved_search(saved_searches, name):
    target = str(name or "").casefold()
    return [
        normalized
        for item in (saved_searches or [])
        if (normalized := _normalize_saved_search(item)) is not None
        and normalized["name"].casefold() != target
    ]


def _save_current_search(saved_searches, name, match_mode, selected_groups, field_values):
    field_keys = [key for selected in selected_groups for key in (selected or [])]
    existing = _validated_saved_searches(saved_searches)
    if not isinstance(name, str) or not name.strip():
        return existing, "Enter a name for this search."
    if not field_keys:
        return existing, "Select at least one field before saving."
    if len(field_values) != len(field_keys) * 2:
        return existing, "Finish configuring each selected field before saving."
    criteria = [
        {"field": field_key, "operator": field_values[index * 2], "value": field_values[index * 2 + 1]}
        for index, field_key in enumerate(field_keys)
    ]
    if _normalize_saved_search({
        "name": name,
        "match_mode": match_mode,
        "criteria": criteria,
    }) is None:
        return existing, "Check each filter operator and value before saving."
    updated = _save_search(saved_searches, name, match_mode, field_keys, field_values)
    if not updated or updated[-1]["name"].casefold() != name.strip().casefold():
        return updated, "Choose a valid operator and value for every selected field."
    return updated, f"Saved '{name.strip()}'."


def _search(selected_fields, match_mode, field_values, backend=None):
    criteria = [
        (field_key, field_values[index * 2], field_values[index * 2 + 1])
        for index, field_key in enumerate(selected_fields)
    ]
    records = filter_records(fetch_records(backend), criteria, match_mode)
    query_text = f" { 'OR' if match_mode == 'Match any (OR)' else 'AND' } ".join(
        f"{key} {match_operator.lower()} {_as_text(value)!r}"
        for key, match_operator, value in criteria
    )
    rows = [
        [_as_text(record.get(field_key)) for field_key in RESULT_FIELDS]
        for record in records
    ]
    return f"{len(records)} matching records", rows, query_text


def _run_saved_search(search, backend=None):
    keys, match_mode, values = _saved_search_values(search)
    if not keys:
        return "Saved search is invalid.", [], ""
    return _search(keys, match_mode, values, backend)


def create_app(backend=None):
    backend = get_settings(backend)["backend"]
    saved_search_secret = "adv-search-saved-searches-v1"
    with gr.Blocks(title="Advanced Search", css="""
        .app-shell { max-width: 1600px; margin: 0 auto; }
        .search-sidebar { flex: 0 0 300px !important; min-width: 280px !important;
            max-width: 340px; max-height: 85vh; overflow-y: auto;
            background: #f5f6f8; padding: 12px; }
        .search-main { min-width: 0; }
        .sidebar-group {
            flex: 0 0 auto !important;
            border: 0 !important;
            border-bottom: 1px solid #dfe3e8 !important;
            border-radius: 0 !important;
            background: transparent !important;
            width: 100%;
        }
        .field-actions {
            display: flex !important;
            flex-direction: row !important;
            gap: 8px !important;
        }
        .field-actions > * {
            flex: 1 1 0 !important;
            min-width: 0 !important;
        }
        .field-actions button {
            min-height: 34px;
            padding: 6px 8px !important;
            font-size: 0.85rem;
        }
        .saved-searches-panel {
            width: 100%;
            border-bottom: 1px solid #dfe3e8;
            padding: 0 0 10px;
        }
        .saved-searches-heading {
            margin: 4px 0 8px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .saved-query-row {
            align-items: center !important;
            flex-wrap: nowrap !important;
            gap: 4px !important;
        }
        .saved-query-row > :first-child {
            flex: 1 1 0 !important;
            min-width: 0 !important;
        }
        .saved-query-row > :not(:first-child) {
            flex: 0 0 auto !important;
            min-width: 0 !important;
        }
        .saved-query-row button:first-child {
            flex: 1 1 auto !important;
            min-width: 0 !important;
            justify-content: flex-start !important;
            text-align: left !important;
            overflow: hidden;
        }
        .saved-query-row button:not(:first-child) {
            flex: 0 0 auto !important;
            min-width: 48px;
            white-space: nowrap !important;
            padding: 5px 6px !important;
            font-size: 0.75rem;
        }
        .saved-searches-empty {
            color: #71717a;
            font-size: 0.85rem;
        }
        .sidebar-group > button {
            display: flex !important;
            flex-wrap: nowrap !important;
            white-space: nowrap !important;
            align-items: center !important;
            justify-content: space-between !important;
            padding: 10px 8px !important;
            font-weight: 600;
            text-align: left;
        }
        .sidebar-group > button span { white-space: nowrap !important; }
        .sidebar-group > button:hover { background: #e9eef8; }
        .search-sidebar {
            display: flex !important;
            flex-direction: column !important;
            flex-wrap: nowrap !important;
        }
        .search-sidebar .field-checklist [data-testid="checkbox-group"] {
            display: grid !important;
            grid-template-columns: minmax(0, 1fr) !important;
            grid-auto-flow: row !important;
            width: 100% !important;
            gap: 4px !important;
        }
        .field-checklist label {
            display: flex !important;
            width: 100% !important;
            box-sizing: border-box;
            margin: 0 !important;
            align-items: center !important;
            gap: 8px !important;
            padding: 6px 8px !important;
            justify-content: flex-start !important;
        }
        .field-checklist label span { white-space: normal; overflow-wrap: anywhere; }
        .filter-row { border-bottom: 1px solid #dfe3e8; padding: 8px 0; }
        @media (max-width: 760px) {
            .search-layout { flex-direction: column !important; }
            .search-sidebar { flex: auto !important; max-width: none; max-height: none; }
        }
        """) as demo:
        with gr.Column(elem_classes="app-shell"):
            gr.Markdown("# Advanced Search")
            with gr.Row(elem_classes="search-layout"):
                with gr.Column(scale=1, elem_classes="search-sidebar"):
                    gr.Markdown("### Select fields")
                    with gr.Row(elem_classes="field-actions"):
                        expand = gr.Button("Expand all", size="sm")
                        collapse = gr.Button("Collapse all", size="sm")
                    saved_search_state = gr.BrowserState(
                        default_value=[],
                        storage_key="adv-search-saved-searches-v2",
                        secret=saved_search_secret,
                    )
                    loaded_search_state = gr.State({"search": None, "revision": 0})
                    with gr.Column(elem_classes="saved-searches-panel"):
                        gr.Markdown("Saved searches", elem_classes="saved-searches-heading")
                        saved_search_name = gr.Textbox(
                            label="Search name",
                            placeholder="e.g. Open cases, last 90 days",
                            max_length=80,
                        )
                        save_status = gr.Markdown()
                        with gr.Column() as saved_search_list:
                            pass
                    groups, selectors = [], []
                    for group, fields in SIDEBAR_FIELD_GROUPS.items():
                        with gr.Accordion(group, open=False, elem_classes="sidebar-group") as accordion:
                            selector = gr.CheckboxGroup(
                                choices=[(label, key) for key, label, kind in fields],
                                value=[], show_label=False, elem_classes="field-checklist")
                        groups.append(accordion)
                        selectors.append(selector)
                    with saved_search_list:
                        @gr.render(inputs=saved_search_state)
                        def render_saved_searches(saved_searches):
                            valid_searches = [
                                normalized
                                for item in (saved_searches or [])
                                if (normalized := _normalize_saved_search(item)) is not None
                            ]
                            if not valid_searches:
                                gr.Markdown("No saved searches yet.", elem_classes="saved-searches-empty")
                            for sequence, saved in enumerate(valid_searches, start=1):
                                with gr.Row(elem_classes="saved-query-row", key="saved_" + saved["name"]):
                                    load = gr.Button(f"{sequence}. {saved['name']}", size="sm")
                                    run = gr.Button("Run", size="sm")
                                    remove = gr.Button("Remove", size="sm")
                                load.click(
                                    lambda current, active, item=saved: _load_saved_search(
                                        current, active, item["name"]
                                    ),
                                    inputs=[saved_search_state, loaded_search_state],
                                    outputs=[*selectors, match_mode, loaded_search_state, saved_search_name],
                                )
                                run.click(
                                    lambda item=saved: _run_saved_search(item, backend),
                                    outputs=[summary, results, preview],
                                )
                                remove.click(
                                    lambda current, name=saved["name"]: _delete_saved_search(current, name),
                                    inputs=saved_search_state,
                                    outputs=saved_search_state,
                                )
                    clear = gr.Button("Clear selections")
                with gr.Column(scale=4, elem_classes="search-main"):
                    gr.Markdown("### Selected filters")
                    match_mode = gr.Radio(choices=MATCH_MODES,
                                          value="Match all (AND)", interactive=True,
                                          label="Match records")
                    summary = gr.Markdown("Select fields on the left to choose their operators here.")
                    preview = gr.Textbox(label="Search criteria", interactive=False)
                    # Define output first so dynamic callbacks can reference it.
                    results = gr.Dataframe(headers=RESULT_HEADERS,
                                           datatype=["str"] * len(RESULT_HEADERS),
                                           value=[], interactive=False, wrap=True, render=False)
                    @gr.render(inputs=[*selectors, loaded_search_state])
                    def render_filters(*render_inputs):
                        selections = render_inputs[:len(selectors)]
                        loaded_state = render_inputs[-1] if render_inputs else None
                        loaded = (loaded_state or {}).get("search") if isinstance(loaded_state, dict) else None
                        revision = (loaded_state or {}).get("revision", 0) if isinstance(loaded_state, dict) else 0
                        saved_criteria = {
                            item["field"]: item
                            for item in (loaded or {}).get("criteria", [])
                        }
                        keys = [key for selected in selections for key in (selected or [])]
                        controls = []
                        for key in keys:
                            kind = FIELD_TYPES[key]
                            saved_criterion = saved_criteria.get(key, {})
                            with gr.Row(elem_classes="filter-row", key=("row_" + key, revision)):
                                gr.Textbox(value=FIELD_LABELS[key], label="Field", interactive=False,
                                           scale=2, key=("label_" + key, revision))
                                choices = _operators_for_field(key)
                                operator = gr.Dropdown(
                                    choices=choices,
                                    value=saved_criterion.get("operator", choices[0]),
                                    label="Operator",
                                    scale=2,
                                    key=("operator_" + key, revision),
                                )
                                value = saved_criterion.get("value")
                                if kind == "number":
                                    value_control = gr.Number(
                                        label="Value",
                                        value=value,
                                        key=("value_" + key, revision),
                                        scale=3,
                                    )
                                else:
                                    value_control = gr.Textbox(
                                        label="Value",
                                        value="" if value is None else str(value),
                                        key=("value_" + key, revision),
                                        scale=3,
                                        placeholder=("YYYY-MM-DD or days" if kind == "date"
                                                     else "For In: 222, 2111"),
                                    )
                            controls.extend([operator, value_control])
                        with gr.Row():
                            search = gr.Button("Search", variant="primary", key=("search", revision))
                            save_search = gr.Button(
                                "Save search",
                                interactive=bool(keys),
                                key=("save_search", revision),
                            )
                        def submit(mode, *values):
                            return _search(keys, mode, values, backend)
                        search.click(submit, inputs=[match_mode, *controls], outputs=[summary, results, preview])
                        def save_current(saved, name, mode, *values):
                            selected_groups = values[:len(selectors)]
                            filter_values = values[len(selectors):]
                            updated, message = _save_current_search(
                                saved, name, mode, selected_groups, filter_values
                            )
                            return updated, message
                        save_search.click(
                            save_current,
                            inputs=[saved_search_state, saved_search_name, match_mode, *selectors, *controls],
                            outputs=[saved_search_state, save_status],
                        )
                    gr.Markdown("### Results")
                    results.render()
                expand.click(lambda: [gr.update(open=True) for _ in groups], outputs=groups)
                collapse.click(lambda: [gr.update(open=False) for _ in groups], outputs=groups)
                clear.click(lambda: [*([[] for _ in selectors]), "Selections cleared.", [], ""],
                            outputs=[*selectors, summary, results, preview])
    return demo


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", choices=["oracle"], default="oracle")
    args = parser.parse_args()
    create_app(args.db).launch(server_name="127.0.0.1", share=True)
