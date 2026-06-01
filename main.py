from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from src.import_timetable import timetable_from_screenshot


load_dotenv()


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Extract a university timetable dict from a screenshot using ChatGPT API."
	)
	parser.add_argument("image", help="Path to timetable screenshot image (png/jpg/jpeg/webp)")
	parser.add_argument(
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
	except Exception as exc:
		print(f"Error: {exc}", file=sys.stderr)
		return 1

	print(json.dumps(timetable, ensure_ascii=False, indent=2))
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

