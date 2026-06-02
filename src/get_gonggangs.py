from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.classes.gonggang import Gonggang


def _extract_building_number(course_code: str, known_buildings: set[str]) -> str | None:
	"""Extract a building number from a course code.

	Examples:
	- "26-B101" -> "26"
	- "10-1-203" -> "10-1" (if present in known buildings)
	- "122-A-501" -> "122-A" (if present in known buildings)
	"""

	code = str(course_code or "").strip()
	if not code:
		return None

	if code in known_buildings:
		return code

	parts = [part.strip() for part in code.split("-") if part.strip()]
	if not parts:
		return None

	candidates: list[str] = []
	candidate = parts[0]
	candidates.append(candidate)
	for part in parts[1:]:
		candidate = f"{candidate}-{part}"
		candidates.append(candidate)

	for candidate in sorted(candidates, key=len, reverse=True):
		if candidate in known_buildings:
			return candidate

	return parts[0]


def get_gonggangs(timetable: dict[str, Any], skip_invalid: bool = True) -> list[Gonggang]:
	"""Build Gonggang objects from timetable output.

	Parameters
	----------
	timetable:
		Dictionary returned by timetable_from_screenshot in import_timetable.py.
	skip_invalid:
		When True, ignore rows/pairs that cannot create a valid Gonggang.
		When False, raise ValueError on the first invalid row/pair.
	"""

	entries_raw = timetable.get("entries") if isinstance(timetable, dict) else None
	if not isinstance(entries_raw, list):
		return []

	known_buildings = set(Gonggang._get_building_locations().keys())
	entries_by_day: dict[str, list[dict[str, Any]]] = defaultdict(list)

	for row in entries_raw:
		if not isinstance(row, dict):
			if skip_invalid:
				continue
			raise ValueError("Each timetable entry must be a dictionary.")

		day = str(row.get("day", "")).strip()
		start_time = str(row.get("start_time", "")).strip()
		end_time = str(row.get("end_time", "")).strip()
		course_code = str(row.get("course_code", "")).strip()

		if not day or not start_time or not end_time or not course_code:
			if skip_invalid:
				continue
			raise ValueError(f"Invalid timetable entry: {row}")

		entries_by_day[day].append(row)

	gonggangs: list[Gonggang] = []
	for day_entries in entries_by_day.values():
		sorted_entries = sorted(day_entries, key=lambda item: str(item.get("start_time", "")))

		for index in range(len(sorted_entries) - 1):
			previous_class = sorted_entries[index]
			next_class = sorted_entries[index + 1]

			previous_building = _extract_building_number(
				str(previous_class.get("course_code", "")),
				known_buildings,
			)
			next_building = _extract_building_number(
				str(next_class.get("course_code", "")),
				known_buildings,
			)
			previous_end_time = str(previous_class.get("end_time", "")).strip()
			next_start_time = str(next_class.get("start_time", "")).strip()

			if not previous_building or not next_building:
				if skip_invalid:
					continue
				raise ValueError(
					f"Could not extract building numbers from pair: {previous_class} -> {next_class}"
				)

			try:
				gonggangs.append(
					Gonggang(
						previous_building_number=previous_building,
						next_building_number=next_building,
						previous_end_time=previous_end_time,
						next_start_time=next_start_time,
					)
				)
			except (ValueError, FileNotFoundError):
				if not skip_invalid:
					raise

	return gonggangs
