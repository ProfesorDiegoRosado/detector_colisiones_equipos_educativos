"""
core.py — pure business logic, no UI dependencies.

Public API
----------
load_json(filepath)       -> list
compute_collisions(data)  -> dict[tuple[GroupKey, GroupKey], list[str]]

where GroupKey = tuple[str, str]  i.e. (level_string, group_letter)
"""

import json
from itertools import combinations


def _normalize_name(name: str) -> str:
    """Collapse internal whitespace so 'Doe,John' matches 'Doe, John'."""
    return " ".join(name.split())


def load_json(filepath: str) -> list:
    """Load and return the raw data from an equipos_educativos JSON file."""
    with open(filepath, "r", encoding="utf-8") as fh:
        return json.load(fh)


def compute_collisions(data: list) -> dict:
    """
    For every pair of (level, group) keys find the set of shared teacher names.

    Parameters
    ----------
    data : list
        Parsed JSON as returned by load_json().

    Returns
    -------
    dict mapping (group_key_1, group_key_2) -> sorted list of teacher names,
    where group_key = (level_string, group_letter_string).
    """
    group_teachers: dict[tuple, set] = {}
    for level_entry in data:
        level = level_entry["level"]
        for grp_name, grp_data in level_entry["groups"].items():
            teachers = {_normalize_name(t["name"]) for t in grp_data["teachers"]}
            group_teachers[(level, grp_name)] = teachers

    result: dict[tuple, list] = {}
    groups = list(group_teachers.keys())
    for g1, g2 in combinations(groups, 2):
        shared = sorted(group_teachers[g1] & group_teachers[g2])
        result[(g1, g2)] = shared
    return result
