"""
Utilities to build workout reporting data structures.
"""
from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, List

from .models import WorkoutSession

MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


@dataclass(frozen=True)
class WeekSlot:
    """Represents a fixed week slot for a month."""

    index: int
    start: date
    end: date
    display_start: date
    display_end: date

    @property
    def label(self) -> str:
        start_label = self.display_start.strftime("%b %d")
        end_label = self.display_end.strftime("%b %d")
        return f"Week {self.index} ({start_label} - {end_label})"


def get_week_slots(year: int, month: int, weeks_count: int = 4) -> List[WeekSlot]:
    """
    Build fixed week slots (default 4) covering a given month.

    Each slot starts on a Monday. The final slot stretches to cover any remaining
    days in the month to avoid data loss when a month spans more than four Mondays.
    """
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    first_monday = first_day - timedelta(days=first_day.weekday())

    slots: List[WeekSlot] = []
    current_start = first_monday

    for index in range(1, weeks_count + 1):
        current_end = current_start + timedelta(days=6)
        display_start = max(current_start, first_day)
        display_end = min(current_end, last_day)
        slots.append(
            WeekSlot(
                index=index,
                start=current_start,
                end=current_end,
                display_start=display_start,
                display_end=display_end,
            )
        )
        current_start = current_end + timedelta(days=1)

    # Extend the final slot so it always covers the last day of the month
    if slots:
        last_slot = slots[-1]
        if last_slot.display_end < last_day:
            slots[-1] = WeekSlot(
                index=last_slot.index,
                start=last_slot.start,
                end=last_day,
                display_start=last_slot.display_start,
                display_end=last_day,
            )

    return slots


def get_month_name(month: int) -> str:
    """Return the English name for a month index (1-based)."""
    return MONTH_NAMES[month - 1]


def _prefetch_month_sessions(user, year: int, month: int) -> List[WorkoutSession]:
    """Fetch workout sessions for a month with related sets/exercises."""
    return list(
        WorkoutSession.objects.filter(
            user=user,
            date__year=year,
            date__month=month,
        )
        .prefetch_related("sets__exercise")
        .order_by("date", "created_at")
    )


def build_monthly_week_data(user, year: int, month: int):
    """
    Build weekly data for the monthly report view/export.

    Returns (weeks, stats, flat_rows) where weeks is an ordered list of week slots
    containing the rows for that slot, stats includes aggregate counters, and
    flat_rows contains every row irrespective of week (for Excel export reuse).
    """
    sessions = _prefetch_month_sessions(user, year, month)
    week_slots = get_week_slots(year, month)

    weeks_map: Dict[int, Dict[str, List[dict]]] = {
        slot.index: {"label": slot.label, "rows": []} for slot in week_slots
    }
    flat_rows: List[dict] = []

    for session in sessions:
        slot = next(
            (
                week_slot
                for week_slot in week_slots
                if week_slot.start <= session.date <= week_slot.end
            ),
            None,
        )
        if not slot:
            continue

        for set_entry in session.sets.all():
            exercise = set_entry.exercise
            row = {
                "date": session.date.isoformat(),
                "category": exercise.get_category_display()
                if hasattr(exercise, "get_category_display")
                else exercise.category,
                "exercise": exercise.name,
                "set_number": set_entry.set_number,
                "reps": set_entry.reps,
                "weight": set_entry.weight,
            }
            weeks_map[slot.index]["rows"].append(row)
            flat_rows.append(row)

    # Sort rows within each week by date then exercise then set number
    for week_data in weeks_map.values():
        week_data["rows"].sort(
            key=lambda r: (r["date"], r["exercise"], r["set_number"])
        )

    flat_rows.sort(key=lambda r: (r["date"], r["exercise"], r["set_number"]))

    stats = {
        "total_sessions": len(sessions),
        "total_sets": len(flat_rows),
        "unique_exercises": len({row["exercise"] for row in flat_rows}),
    }

    return [weeks_map[slot.index] for slot in week_slots], stats, flat_rows


def build_annual_week_tables(user, year: int):
    """
    Build the 4 weekly tables per month required for the annual Excel export.

    Returns a dict keyed by month index with an ordered list of 4 week tables.
    Each week table contains a label and a list of rows, where each row includes
    a "label" cell plus up to 4 set dictionaries (weight/reps).
    """
    sessions = list(
        WorkoutSession.objects.filter(user=user, date__year=year)
        .prefetch_related("sets__exercise")
        .order_by("date", "created_at")
    )

    sessions_by_month: Dict[int, List[WorkoutSession]] = defaultdict(list)
    for session in sessions:
        sessions_by_month[session.date.month].append(session)

    annual_tables: Dict[int, List[dict]] = {}

    for month in range(1, 13):
        month_sessions = sessions_by_month.get(month, [])
        week_slots = get_week_slots(year, month)
        week_tables = [
            {"label": slot.label, "rows": []}
            for slot in week_slots
        ]

        for session in month_sessions:
            slot = next(
                (
                    week_slot
                    for week_slot in week_slots
                    if week_slot.start <= session.date <= week_slot.end
                ),
                None,
            )
            if not slot:
                continue

            table = week_tables[slot.index - 1]

            exercise_groups: Dict[int, Dict[str, Any]] = {}
            for set_entry in session.sets.all():
                exercise_id = set_entry.exercise_id
                if exercise_id not in exercise_groups:
                    exercise_groups[exercise_id] = {
                        "name": set_entry.exercise.name,
                        "sets": []
                    }
                exercise_groups[exercise_id]["sets"].append(set_entry)

            for exercise_id in sorted(
                exercise_groups.keys(),
                key=lambda ex_id: exercise_groups[ex_id]["name"]
            ):
                exercise_name = exercise_groups[exercise_id]["name"]
                ordered_sets = sorted(
                    exercise_groups[exercise_id]["sets"], key=lambda s: s.set_number
                )
                for chunk_index in range(0, len(ordered_sets), 4):
                    chunk = ordered_sets[chunk_index : chunk_index + 4]
                    label = f"{session.date.strftime('%a %d')} - {exercise_name}"
                    chunk_number = chunk_index // 4
                    if chunk_number > 0:
                        label = f"{label} (cont. {chunk_number + 1})"

                    row_sets = [
                        {"weight": set_entry.weight, "reps": set_entry.reps}
                        for set_entry in chunk
                    ]
                    table["rows"].append({"label": label, "sets": row_sets})

        # Ensure blank tables still have labels even if no data
        annual_tables[month] = week_tables

    return annual_tables


