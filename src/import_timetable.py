"""Utilities for converting timetable screenshots into structured dictionaries.

This module uses OpenAI's ChatGPT API with vision input to read a timetable
image and return a polished dictionary representation.
"""

from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI
from dotenv import load_dotenv


DEFAULT_MODEL = "gpt-4.1-mini"
DAY_ORDER = {
	"Monday": 0,
	"Tuesday": 1,
	"Wednesday": 2,
	"Thursday": 3,
	"Friday": 4,
	"Saturday": 5,
	"Sunday": 6,
}

# Load environment variables from .env when available.
load_dotenv()


@dataclass(frozen=True)
class TimetableImportConfig:
	"""Configuration for the timetable importer."""

	api_key: str | None = None
	model: str = DEFAULT_MODEL
	max_tokens: int = 1800


def _encode_image_to_data_url(image_path: str | Path) -> str:
	path = Path(image_path)
	if not path.exists():
		raise FileNotFoundError(f"Image file not found: {path}")

	suffix = path.suffix.lower().lstrip(".")
	mime = {
		"jpg": "image/jpeg",
		"jpeg": "image/jpeg",
		"png": "image/png",
		"webp": "image/webp",
	}.get(suffix)
	if mime is None:
		raise ValueError("Unsupported image format. Use one of: jpg, jpeg, png, webp")

	raw = path.read_bytes()
	b64 = base64.b64encode(raw).decode("ascii")
	return f"data:{mime};base64,{b64}"


def _extract_json_object(text: str) -> dict[str, Any]:
	text = text.strip()
	try:
		data = json.loads(text)
		if isinstance(data, dict):
			return data
	except json.JSONDecodeError:
		pass

	start = text.find("{")
	end = text.rfind("}")
	if start == -1 or end == -1 or start >= end:
		raise ValueError("Model response did not contain a JSON object.")

	data = json.loads(text[start : end + 1])
	if not isinstance(data, dict):
		raise ValueError("Model response JSON was not an object.")
	return data


def _clean_string(value: Any) -> str:
	if value is None:
		return ""
	return str(value).strip()


def _normalize_day(day: str) -> str:
	raw = _clean_string(day).lower()
	aliases = {
		"mon": "Monday",
		"monday": "Monday",
		"tue": "Tuesday",
		"tues": "Tuesday",
		"tuesday": "Tuesday",
		"wed": "Wednesday",
		"wednesday": "Wednesday",
		"thu": "Thursday",
		"thur": "Thursday",
		"thurs": "Thursday",
		"thursday": "Thursday",
		"fri": "Friday",
		"friday": "Friday",
		"sat": "Saturday",
		"saturday": "Saturday",
		"sun": "Sunday",
		"sunday": "Sunday",
	}
	return aliases.get(raw, day.strip().title())


def _normalize_time(value: str) -> str:
	text = _clean_string(value)
	if not text:
		return ""

	text = text.replace(".", ":").replace(" ", "")
	text = text.replace("：", ":")
	suffix = ""
	if text.startswith("오전"):
		suffix = "am"
		text = text[2:]
	elif text.startswith("오후"):
		suffix = "pm"
		text = text[2:]

	if text.lower().endswith("am") or text.lower().endswith("pm"):
		suffix = text[-2:].lower()
		text = text[:-2]

	match_korean = re.fullmatch(r"(\d{1,2})시(?:(\d{1,2})분?)?", text)
	if match_korean:
		hour = int(match_korean.group(1))
		minute = int(match_korean.group(2) or "0")
		text = f"{hour}:{minute}"

	if ":" not in text:
		if len(text) in (3, 4) and text.isdigit():
			text = f"{text[:-2]}:{text[-2:]}"
		elif len(text) <= 2 and text.isdigit():
			text = f"{text}:00"

	match_hhmm = re.search(r"(\d{1,2}):(\d{1,2})", text)
	if not match_hhmm:
		return _clean_string(value)

	hour = int(match_hhmm.group(1))
	minute = int(match_hhmm.group(2))

	if suffix == "pm" and 1 <= hour <= 11:
		hour += 12
	if suffix == "am" and hour == 12:
		hour = 0

	if not (0 <= hour <= 23 and 0 <= minute <= 59):
		return _clean_string(value)

	return f"{hour:02d}:{minute:02d}"


def _sort_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
	def _key(entry: dict[str, Any]) -> tuple[int, str, str]:
		day = _clean_string(entry.get("day"))
		day_idx = DAY_ORDER.get(day, 99)
		start = _clean_string(entry.get("start_time"))
		code = _clean_string(entry.get("course_code"))
		return (day_idx, start, code)

	return sorted(entries, key=_key)


def _polish_timetable(data: dict[str, Any]) -> dict[str, Any]:
	student_info = data.get("student_info") if isinstance(data.get("student_info"), dict) else {}
	entries = data.get("entries") if isinstance(data.get("entries"), list) else []

	polished_entries: list[dict[str, Any]] = []
	for row in entries:
		if not isinstance(row, dict):
			continue

		day = _normalize_day(_clean_string(row.get("day")))
		start = _normalize_time(_clean_string(row.get("start_time")))
		end = _normalize_time(_clean_string(row.get("end_time")))

		polished_entries.append(
			{
				"day": day,
				"start_time": start,
				"end_time": end,
				"course_code": _clean_string(row.get("course_code")),
				"course_title": _clean_string(row.get("course_title")),
			}
		)

	polished = {
		"student_info": {
			"name": _clean_string(student_info.get("name")),
			"student_id": _clean_string(student_info.get("student_id")),
			"department": _clean_string(student_info.get("department")),
			"semester": _clean_string(data.get("semester")),
		},
		"entries": _sort_entries(polished_entries),
		"meta": {
			"source": "chatgpt-vision",
			"polished_at_utc": datetime.now(timezone.utc).isoformat(),
		},
	}
	return polished


def timetable_from_screenshot(
	image_path: str | Path,
	api_key: str | None = None,
	model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
	"""Convert a timetable screenshot into a polished dictionary.

	Parameters
	----------
	image_path:
		Path to the timetable screenshot image.
	api_key:
		OpenAI API key. If omitted, uses OPENAI_API_KEY from env.
	model:
		ChatGPT model name to use.

	Returns
	-------
	dict
		Normalized timetable dictionary with student info and class entries.
	"""

	resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
	if not resolved_api_key:
		raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY or pass api_key.")

	image_data_url = _encode_image_to_data_url(image_path)
	client = OpenAI(api_key=resolved_api_key)

	schema = {
		"name": "timetable_extraction",
		"strict": True,
		"schema": {
			"type": "object",
			"additionalProperties": False,
			"properties": {
				"semester": {"type": "string"},
				"student_info": {
					"type": "object",
					"additionalProperties": False,
					"properties": {
						"name": {"type": "string"},
						"student_id": {"type": "string"},
						"department": {"type": "string"},
					},
					"required": ["name", "student_id", "department"],
				},
				"entries": {
					"type": "array",
					"items": {
						"type": "object",
						"additionalProperties": False,
						"properties": {
							"day": {"type": "string"},
							"start_time": {"type": "string"},
							"end_time": {"type": "string"},
							"course_code": {"type": "string"},
							"course_title": {"type": "string"},
						},
						"required": [
							"day",
							"start_time",
							"end_time",
							"course_code",
							"course_title",
						],
					},
				},
			},
			"required": ["semester", "student_info", "entries"],
		},
	}

	response = client.chat.completions.create(
		model=model,
		temperature=0,
		max_tokens=1800,
		response_format={"type": "json_schema", "json_schema": schema},
		messages=[
			{
				"role": "system",
				"content": (
					"You extract course timetable data from screenshots. "
					"Keep course/class names in their original language (Korean if present), and never translate them to English. "
					"Preserve minute precision for class times, including half-hour values like 10:30. Never round to full hours. "
					"Always return valid JSON matching the schema. "
					"If text is uncertain, use an empty string for that field."
				),
			},
			{
				"role": "user",
				"content": [
					{
						"type": "text",
						"text": (
							"Read this university student timetable screenshot and extract all classes. "
							"Normalize days to English weekday names and times to 24-hour HH:MM when possible. "
							"Keep exact minutes for times (for example, 10:30 must stay 10:30, not 10:00). "
                            "Some classes start at half-hour times, so do not round times to the nearest hour. "
							"Do not translate course names; keep them exactly as shown, including Korean text."
						),
					},
					{
						"type": "image_url",
						"image_url": {"url": image_data_url},
					},
				],
			},
		],
	)

	content = response.choices[0].message.content or "{}"
	extracted = _extract_json_object(content)
	return _polish_timetable(extracted)

