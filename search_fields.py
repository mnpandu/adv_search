"""Shared operators. Fields, labels, and column order come directly from SQL metadata."""
OPERATORS = {
    "text": ["Equals", "In", "Does not equal", "Contains", "Does not contain", "Starts with", "Is empty", "Is not empty"],
    "number": ["Equals", "Greater than", "Less than", "At least", "At most", "Is empty", "Is not empty"],
    "date": ["On", "Before", "After", "Within last (days)", "Is empty", "Is not empty"],
}
