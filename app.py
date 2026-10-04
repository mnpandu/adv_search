import csv
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

import streamlit as st
from database import fetch_records_by_group, fetch_field_groups
from db_config import get_settings

from search_fields import OPERATORS, load_sidebar_fields

MATCH_MODES = ["Match all (AND)", "Match any (OR)"]
CASE_QUERY_CATEGORIES = ["Case Details"]
CLAIM_QUERY_CATEGORIES = ["Claim Details"]
QUERY_CATEGORIES = CASE_QUERY_CATEGORIES + CLAIM_QUERY_CATEGORIES
FILTER_CATEGORIES = QUERY_CATEGORIES


def configure_fields(groups, use_sidebar_config=False):
    global FIELD_GROUPS, SIDEBAR_FIELD_GROUPS, FIELD_LABELS, FIELD_TYPES
    global FIELD_OPERATORS, FIELD_CATEGORY_BY_KEY, CASE_RESULT_FIELDS, CLAIM_RESULT_FIELDS
    FIELD_GROUPS = SIDEBAR_FIELD_GROUPS = groups
    FIELD_LABELS = {key: label for fields in groups.values() for key, label, kind in fields}
    FIELD_TYPES = {key: kind for fields in groups.values() for key, label, kind in fields}
    FIELD_OPERATORS = {key: OPERATORS[kind] for key, kind in FIELD_TYPES.items()}
    FIELD_CATEGORY_BY_KEY = {key: group for group, fields in groups.items() for key, _, _ in fields}
    CASE_RESULT_FIELDS = [key for key, _, _ in groups["Case Details"]]
    CLAIM_RESULT_FIELDS = [key for key, _, _ in groups["Claim Details"]]
    if use_sidebar_config:
        SIDEBAR_FIELD_GROUPS, FIELD_OPERATORS = load_sidebar_fields(groups)


configure_fields({"Case Details": [], "Claim Details": []})


def _result_headers(field_keys):
    return [FIELD_LABELS.get(key, key.replace("_", " ").title()) for key in field_keys]


def _index_by(records, key_field):
    indexed = defaultdict(list)
    for record in records:
        key = record.get(key_field)
        if key is not None:
            indexed[key].append(record)
    return indexed


def _aggregate_fields(records, field_keys):
    aggregated = {}
    for field_key in field_keys:
        values = []
        seen = set()
        for record in records:
            value = record.get(field_key)
            text = _as_text(value)
            if text and text not in seen:
                seen.add(text)
                values.append(text)
        aggregated[field_key] = ", ".join(values) if values else None
    return aggregated


def _build_case_details_rows(records_by_category):
    return records_by_category["Case Details"]


def _build_claim_details_rows(records_by_category):
    return records_by_category["Claim Details"]


def _result_rows(records, field_keys):
    headers = _result_headers(field_keys)
    return [
        {header: _as_text(record.get(field_key)) for field_key, header in zip(field_keys, headers)}
        for record in records
    ]


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
    return FIELD_OPERATORS.get(field_key, [])


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
    criteria_by_category = {category: [] for category in QUERY_CATEGORIES}
    for index, field_key in enumerate(selected_fields):
        category = FIELD_CATEGORY_BY_KEY.get(field_key)
        if category not in FILTER_CATEGORIES:
            raise ValueError(f"Field {field_key!r} has no active category query")
        criteria_by_category[category].append((
            field_key,
            field_values[index * 2],
            field_values[index * 2 + 1],
        ))

    raw_records = fetch_records_by_group(backend, QUERY_CATEGORIES)
    records_by_category = {}
    query_text_by_category = {}
    for category in QUERY_CATEGORIES:
        criteria = criteria_by_category[category]
        records_by_category[category] = filter_records(
            raw_records[category], criteria, match_mode
        )
        query_text_by_category[category] = f" { 'OR' if match_mode == 'Match any (OR)' else 'AND' } ".join(
            f"{key} {match_operator.lower()} {_as_text(value)!r}"
            for key, match_operator, value in criteria
        )
    # A selected case number scopes claims even when claim filters use OR.
    case_number_criteria = [
        ("Claim Details::Case Number", operator, value)
        for key, operator, value in criteria_by_category["Case Details"]
        if key == "Case Details::Case Number"
    ]
    if case_number_criteria:
        if "Claim Details::Case Number" not in FIELD_TYPES:
            raise ValueError('Claim Details query must select the case number AS "Case Number" to filter related claims.')
        records_by_category["Claim Details"] = filter_records(
            records_by_category["Claim Details"], case_number_criteria, "Match all (AND)"
        )
        scope_text = " AND ".join(
            f"Case Number {operator.lower()} {_as_text(value)!r}"
            for _, operator, value in case_number_criteria
        )
        existing = query_text_by_category["Claim Details"]
        query_text_by_category["Claim Details"] = (
            f"({existing}) AND ({scope_text})" if existing else scope_text
        )
    total_rows = sum(len(records) for records in records_by_category.values())
    return f"{total_rows} source rows across {len(QUERY_CATEGORIES)} queries", records_by_category, query_text_by_category


def _run_saved_search(search, backend=None):
    keys, match_mode, values = _saved_search_values(search)
    if not keys:
        return "Saved search is invalid.", {}, {}
    return _search(keys, match_mode, values, backend)


def _apply_saved_search(search):
    saved = _normalize_saved_search(search)
    if saved is None:
        return

    restored = _restore_saved_search(saved)
    selections, match_mode = restored[:-2], restored[-2]
    for (group, _fields), selected in zip(SIDEBAR_FIELD_GROUPS.items(), selections):
        st.session_state[f"selected_fields::{group}"] = selected

    for field_key in FIELD_LABELS:
        _clear_field_widget_state(field_key)
    for criterion in saved["criteria"]:
        field_key = criterion["field"]
        operator = criterion["operator"]
        st.session_state[f"operator::{field_key}"] = operator
        value = criterion["value"]
        if FIELD_TYPES[field_key] == "date" and value is not None and operator != "Within last (days)":
            value = date.fromisoformat(str(value)[:10])
        st.session_state[f"value::{field_key}::{operator}"] = value

    st.session_state["match_mode"] = match_mode
    st.session_state["saved_search_name"] = saved["name"]


def _run_query(selected_fields, match_mode, field_values):
    try:
        st.session_state["search_result"] = _search(
            selected_fields, match_mode, field_values, "oracle"
        )
        st.session_state["search_error"] = None
    except Exception as exc:
        st.session_state["search_result"] = None
        st.session_state["search_error"] = str(exc)


def _clear_field_widget_state(field_key):
    st.session_state.pop(f"operator::{field_key}", None)
    value_prefix = f"value::{field_key}::"
    for state_key in list(st.session_state):
        if state_key.startswith(value_prefix):
            st.session_state.pop(state_key, None)


def main():
    st.set_page_config(page_title="Advanced Search", layout="wide")
    st.title("Advanced Search")
    try:
        configure_fields(fetch_field_groups(), use_sidebar_config=True)
    except Exception as exc:
        st.error(f"Cannot load SQL result columns: {exc}")
        st.stop()
    signature = (tuple((group, tuple(fields)) for group, fields in FIELD_GROUPS.items()),
                 tuple((group, tuple(fields)) for group, fields in SIDEBAR_FIELD_GROUPS.items()),
                 tuple((key, tuple(ops)) for key, ops in FIELD_OPERATORS.items()))
    if st.session_state.get("query_columns") != signature:
        st.session_state["search_result"] = None
        for group, fields in SIDEBAR_FIELD_GROUPS.items():
            key = f"selected_fields::{group}"
            allowed = {field[0] for field in fields}
            st.session_state[key] = [v for v in st.session_state.get(key, []) if v in allowed]
        st.session_state["query_columns"] = signature

    state_defaults = {
        "saved_searches": [],
        "match_mode": MATCH_MODES[0],
        "expand_field_groups": False,
        "search_result": None,
        "search_error": None,
    }
    for state_key, default in state_defaults.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = default

    saved_searches = _validated_saved_searches(st.session_state["saved_searches"])
    st.session_state["saved_searches"] = saved_searches

    with st.sidebar:
        st.subheader("Saved searches")
        if not saved_searches:
            st.caption("No saved searches in this session.")
        for sequence, saved in enumerate(saved_searches, start=1):
            load_col, run_col, remove_col = st.columns([3.5, 1.4, 1.5], gap="small")
            if load_col.button(
                f"{sequence}. {saved['name']}",
                key=f"load_saved::{sequence}",
                width="stretch",
            ):
                _apply_saved_search(saved)
                st.rerun()
            if run_col.button(
                "Run",
                key=f"run_saved::{sequence}",
                help="Run this saved search",
                icon=":material/play_arrow:",
                type="secondary",
                width="stretch",
            ):
                _run_query(*_saved_search_values(saved))
                st.rerun()
            if remove_col.button(
                "Remove",
                key=f"remove_saved::{sequence}",
                help="Remove this saved search",
                icon=":material/delete_outline:",
                type="secondary",
                width="stretch",
            ):
                st.session_state["saved_searches"] = _delete_saved_search(
                    saved_searches, saved["name"]
                )
                st.rerun()

        st.text_input(
            "Search name",
            placeholder="e.g. Open cases, last 90 days",
            max_chars=80,
            key="saved_search_name",
        )
        st.caption("Saved searches are kept for this active session.")

        expand_col, collapse_col = st.columns(2)
        if expand_col.button("Expand all", use_container_width=True):
            st.session_state["expand_field_groups"] = True
            st.rerun()
        if collapse_col.button("Collapse all", use_container_width=True):
            st.session_state["expand_field_groups"] = False
            st.rerun()

        if st.button("Clear selections", use_container_width=True):
            for group in SIDEBAR_FIELD_GROUPS:
                st.session_state[f"selected_fields::{group}"] = []
            for field_key in FIELD_LABELS:
                _clear_field_widget_state(field_key)
            st.session_state["match_mode"] = MATCH_MODES[0]
            st.session_state["search_result"] = None
            st.session_state["search_error"] = None
            st.rerun()

        st.divider()
        st.subheader("Select fields")
        for group, fields in SIDEBAR_FIELD_GROUPS.items():
            with st.expander(group, expanded=st.session_state["expand_field_groups"]):
                st.multiselect(
                    "Fields",
                    options=[field_key for field_key, _label, _kind in fields],
                    format_func=lambda field_key: FIELD_LABELS[field_key],
                    key=f"selected_fields::{group}",
                    label_visibility="collapsed",
                    placeholder="Choose fields",
                )

    selected_fields = [
        field_key
        for group in SIDEBAR_FIELD_GROUPS
        for field_key in st.session_state.get(f"selected_fields::{group}", [])
    ]

    st.subheader("Selected filters")
    st.radio("Match records", MATCH_MODES, horizontal=True, key="match_mode")

    field_values = []
    if selected_fields:
        for field_key in selected_fields:
            field_type = FIELD_TYPES[field_key]
            operator_key = f"operator::{field_key}"
            operators = _operators_for_field(field_key)
            if st.session_state.get(operator_key) not in operators:
                st.session_state[operator_key] = operators[0]
            operator = st.session_state[operator_key]
            value_key = f"value::{field_key}::{operator}"

            with st.container(border=True):
                field_col, operator_col, value_col = st.columns([3, 2, 5])
                field_col.markdown("Field")
                field_col.markdown(f"**{FIELD_LABELS[field_key]}**")
                operator = operator_col.selectbox(
                    "Operator", operators, key=operator_key
                )

                if operator in {"Is empty", "Is not empty"}:
                    value = None
                    value_col.caption("No value required")
                elif field_type == "number":
                    value = value_col.number_input(
                        "Value", value=st.session_state.get(value_key), key=value_key
                    )
                elif field_type == "date" and operator == "Within last (days)":
                    if value_key not in st.session_state:
                        st.session_state[value_key] = 90
                    value = value_col.number_input(
                        "Days", min_value=0, step=1, key=value_key
                    )
                elif field_type == "date":
                    current_value = st.session_state.get(value_key)
                    if isinstance(current_value, str):
                        current_value = date.fromisoformat(current_value[:10])
                    value = value_col.date_input(
                        "Date", value=current_value, key=value_key
                    )
                else:
                    value = value_col.text_input(
                        "Value",
                        placeholder="For In: 222, 2111",
                        key=value_key,
                    )
            field_values.extend([operator, value])
    else:
        st.info("Choose one or more fields from the sidebar to build a search.")

    search_col, save_col = st.columns([1, 1])
    with search_col:
        if st.button("Search", type="primary", disabled=False):
            _run_query(selected_fields, st.session_state["match_mode"], field_values)
    with save_col:
        if st.button("Save search", disabled=not selected_fields):
            updated, message = _save_current_search(
                saved_searches,
                st.session_state.get("saved_search_name", ""),
                st.session_state["match_mode"],
                [st.session_state.get(f"selected_fields::{group}", [])
                 for group in SIDEBAR_FIELD_GROUPS],
                field_values,
            )
            st.session_state["saved_searches"] = updated
            if message.startswith("Saved "):
                st.success(message)
                st.rerun()
            else:
                st.warning(message)

    if st.session_state.get("search_error"):
        st.error(f"Search failed: {st.session_state['search_error']}")
    result = st.session_state.get("search_result")
    if result:
        summary, records_by_category, query_text_by_category = result
        case_rows = _build_case_details_rows(records_by_category)
        claim_rows = _build_claim_details_rows(records_by_category)
        claim_count = len(claim_rows)
        st.subheader("Results")
        st.caption(summary)
        case_tab, claim_tab = st.tabs([
            f"Case Details ({len(case_rows)})",
            f"Claim Details ({claim_count})",
        ])
        with case_tab:
            case_filters = [
                f"{category}: {query_text_by_category[category]}"
                for category in CASE_QUERY_CATEGORIES
                if query_text_by_category.get(category)
            ]
            st.caption(" | ".join(case_filters) if case_filters else "No case-related filters; showing all case details.")
            if CASE_RESULT_FIELDS and case_rows:
                st.dataframe(
                    _result_rows(case_rows, CASE_RESULT_FIELDS),
                    hide_index=True,
                    width="stretch",
                )
            elif not CASE_RESULT_FIELDS:
                st.info("No result fields are enabled for Case Details in the SELECT query.")
            else:
                st.info("No case details matched this search.")
        with claim_tab:
            claim_filters = [
                f"{category}: {query_text_by_category[category]}"
                for category in CLAIM_QUERY_CATEGORIES
                if query_text_by_category.get(category)
            ]
            st.caption(" | ".join(claim_filters) if claim_filters else "No claim-related filters; showing all claim details.")
            if CLAIM_RESULT_FIELDS and claim_rows:
                st.dataframe(
                    _result_rows(claim_rows, CLAIM_RESULT_FIELDS),
                    hide_index=True,
                    width="stretch",
                )
            elif not CLAIM_RESULT_FIELDS:
                st.info("No result fields are enabled for Claim Details in the SELECT query.")
            else:
                st.info("No claim details matched this search.")


if __name__ == "__main__":
    main()
