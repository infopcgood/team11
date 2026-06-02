from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from src.get_gonggangs import get_gonggangs
from src.import_timetable import timetable_from_screenshot
from src.recommend_places import recommend_places

load_dotenv()


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Extract a university timetable dict from a screenshot using ChatGPT API."
	)
	parser.add_argument("image", help="Path to timetable screenshot image (png/jpg/jpeg/webp)")
	parser.add_argument(
			"--category",
		default="공부",
		help="Activity category: 공부, 휴식, 밥",
	)
		"--model",
		default="gpt-4.1-mini",
		help="OpenAI model name (default: gpt-4.1-mini)",
	)
	parser.add_argument(
		"--api-key",
		default=None,
		help="OpenAI API key (optional if OPENAI_API_KEY is set)",
	)
	return parser


def main() -> int:
	parser = build_parser()
	args = parser.parse_args()

	try:
		timetable = timetable_from_screenshot(
			image_path=args.image,
			api_key=args.api_key,
			model=args.model,
		)
		gonggangs = get_gonggangs(timetable)
		recommendations = recommend_places(gonggangs, args.category)
		
	except Exception as exc:
		print(f"Error: {exc}", file=sys.stderr)
		return 1

	output = {
		"gonggangs": [item.to_dict() for item in gonggangs],
		'recommendations": recommendations,
	}
	print(json.dumps(output, ensure_ascii=False, indent=2))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

