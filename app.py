import csv
from datetime import date
from decimal import Decimal, InvalidOperation

import gradio as gr
from database import fetch_records
from db_config import get_settings

from search_fields import FIELD_GROUPS

FIELD_LABELS = {
    field_key: label
    for fields in FIELD_GROUPS.values()
    for field_key, label, _field_type in fields
}
FIELD_TYPES = {
    field_key: field_type
    for fields in FIELD_GROUPS.values()
    for field_key, _label, field_type in fields
}

TEXT_OPERATORS = [
    "Equals",
    "In",
    "Does not equal",
    "Contains",
    "Does not contain",
    "Starts with",
    "Is empty",
    "Is not empty",
]
NUMBER_OPERATORS = [
    "Equals",
    "Greater than",
    "Less than",
    "At least",
    "At most",
    "Is empty",
    "Is not empty",
]
DATE_OPERATORS = ["On", "Before", "After", "Is empty", "Is not empty"]

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


def matches(record, field_key, match_operator, expected_value):
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


def create_app(backend=None):
    backend = get_settings(backend)["backend"]
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
                    groups, selectors = [], []
                    for group, fields in FIELD_GROUPS.items():
                        with gr.Accordion(group, open=False, elem_classes="sidebar-group") as accordion:
                            selector = gr.CheckboxGroup(
                                choices=[(label, key) for key, label, kind in fields],
                                value=[], show_label=False, elem_classes="field-checklist")
                        groups.append(accordion)
                        selectors.append(selector)
                    clear = gr.Button("Clear selections")
                with gr.Column(scale=4, elem_classes="search-main"):
                    gr.Markdown("### Selected filters")
                    match_mode = gr.Radio(choices=["Match all (AND)", "Match any (OR)"],
                                          value="Match all (AND)", label="Combine filters")
                    summary = gr.Markdown("Select fields on the left to choose their operators here.")
                    preview = gr.Textbox(label="Search criteria", interactive=False)
                    # Define output first so dynamic callbacks can reference it.
                    results = gr.Dataframe(headers=RESULT_HEADERS,
                                           datatype=["str"] * len(RESULT_HEADERS),
                                           value=[], interactive=False, wrap=True, render=False)
                    @gr.render(inputs=selectors)
                    def render_filters(*selections):
                        keys = [key for selected in selections for key in (selected or [])]
                        controls = []
                        for key in keys:
                            kind = FIELD_TYPES[key]
                            with gr.Row(elem_classes="filter-row", key="row_" + key):
                                gr.Textbox(value=FIELD_LABELS[key], label="Field", interactive=False,
                                           scale=2, key="label_" + key)
                                choices = {"text": TEXT_OPERATORS, "number": NUMBER_OPERATORS,
                                           "date": DATE_OPERATORS}[kind]
                                operator = gr.Dropdown(choices=choices, value=choices[0], label="Operator",
                                                       scale=2, key="operator_" + key)
                                if kind == "number":
                                    value = gr.Number(label="Value", key="value_" + key, scale=3)
                                else:
                                    value = gr.Textbox(label="Value", key="value_" + key, scale=3,
                                                       placeholder="YYYY-MM-DD" if kind == "date" else "For In: 222, 2111")
                            controls.extend([operator, value])
                        search = gr.Button("Search", variant="primary", key="search")
                        def submit(mode, *values):
                            return _search(keys, mode, values, backend)
                        search.click(submit, inputs=[match_mode, *controls], outputs=[summary, results, preview])
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
    parser.add_argument("--db", choices=["postgres"], default=None)
    args = parser.parse_args()
    create_app(args.db).launch(server_name="127.0.0.1", share=True)
