from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.classes.gonggang import Gonggang


WALKING_SPEED_M_PER_MIN = 70.0
MIN_STAY_MINUTES = 10


CATEGORY_COLUMNS = {
    "휴식": "rest",
    "공부": "study",
    "밥": "meal",
    "식사": "meal",
    "meal": "meal",
    "study": "study",
    "rest": "rest",
    "exercise": "exercise",
}


@dataclass(frozen=True)
class Place:
    name: str
    building: str
    rest: int
    study: int
    meal: int
    exercise: int
    open_time: str

    def score_for(self, category: str) -> int:
        column = CATEGORY_COLUMNS.get(category, category)
        if column == "rest":
            return self.rest
        if column == "study":
            return self.study
        if column == "meal":
            return self.meal
        if column == "exercise":
            return self.exercise
        return 0


def load_places() -> list[Place]:
    csv_path = Path(__file__).resolve().parents[1] / "data" / "places.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"Place data file not found: {csv_path}")

    places: list[Place] = []

    with csv_path.open(newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)

        for row in reader:
            places.append(
                Place(
                    name=str(row["name"]).strip(),
                    building=str(row["building"]).strip(),
                    rest=int(row["rest"] or 0),
                    study=int(row["study"] or 0),
                    meal=int(row["meal"] or 0),
                    exercise=int(row["exercise"] or 0),
                    open_time=str(row.get("open_time", "")).strip(),
                )
            )

    return places


def _time_to_minutes(value: str) -> int:
    dt = datetime.strptime(value, "%H:%M")
    return dt.hour * 60 + dt.minute


def _minutes_to_time(value: int) -> str:
    value %= 24 * 60
    hour = value // 60
    minute = value % 60
    return f"{hour:02d}:{minute:02d}"


def _is_place_open(place: Place, start_time: str, end_time: str) -> bool:
    if not place.open_time:
        return True

    start_min = _time_to_minutes(start_time)
    end_min = _time_to_minutes(end_time)

    for period in place.open_time.split(";"):
        period = period.strip()
        if not period or "-" not in period:
            continue

        open_start, open_end = period.split("-", 1)
        open_start_min = _time_to_minutes(open_start.strip())
        open_end_min = _time_to_minutes(open_end.strip())

        if start_min >= open_start_min and end_min <= open_end_min:
            return True

    return False


def _building_distance_from_path(gonggang: Gonggang, building_number: str) -> float | None:
    for item in gonggang.nearby_buildings:
        if item.building_number == building_number:
            return item.distance_to_path_m
    return None


def recommend_for_gonggang(gonggang: Gonggang, category: str) -> dict[str, Any]:
    places = load_places()

    nearby_building_numbers = {
        item.building_number for item in gonggang.nearby_buildings
    }

    valid_places: list[dict[str, Any]] = []

    for place in places:
        if place.building not in nearby_building_numbers:
            continue

        score = place.score_for(category)
        if score <= 0:
            continue

        distance_from_path = _building_distance_from_path(gonggang, place.building)
        if distance_from_path is None:
            continue

        extra_walk_minutes = round(distance_from_path / WALKING_SPEED_M_PER_MIN)
        total_move_minutes = extra_walk_minutes * 2

        stay_minutes = gonggang.empty_duration_minutes - total_move_minutes

        if stay_minutes < MIN_STAY_MINUTES:
            continue

        visit_start = _minutes_to_time(
            _time_to_minutes(gonggang.previous_end_time) + extra_walk_minutes
        )
        visit_end = _minutes_to_time(
            _time_to_minutes(gonggang.next_start_time) - extra_walk_minutes
        )

        if not _is_place_open(place, visit_start, visit_end):
            continue

        valid_places.append(
            {
                "place_name": place.name,
                "building": place.building,
                "category": category,
                "score": score,
                "distance_from_path_m": round(distance_from_path, 2),
                "extra_walk_minutes_each_way": extra_walk_minutes,
                "available_stay_minutes": stay_minutes,
                "schedule": {
                    "start": visit_start,
                    "end": visit_end,
                    "description": f"{place.name}에서 {category} 활동",
                },
            }
        )

    valid_places.sort(
        key=lambda item: (
            -int(item["score"]),
            float(item["distance_from_path_m"]),
            -int(item["available_stay_minutes"]),
        )
    )

    return {
        "gonggang": gonggang.to_dict(),
        "category": category,
        "recommended_places": valid_places[:3],
    }


def recommend_places(gonggangs: list[Gonggang], category: str) -> list[dict[str, Any]]:
    return [recommend_for_gonggang(gonggang, category) for gonggang in gonggangs]
