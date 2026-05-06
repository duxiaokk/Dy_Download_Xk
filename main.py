from __future__ import annotations

import argparse
import json

from link_agent import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, LinkAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan txt/csv files and extract links")
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--only-douyin", action="store_true")
    parser.add_argument(
        "--reset-output",
        action="store_true",
        help="Clear previous exported output before processing",
    )
    args = parser.parse_args()

    agent = LinkAgent(batch_size=args.batch_size, only_douyin=args.only_douyin)
    result = agent.process_folder(
        input_dir=args.input_dir,
        output_dir=args.output,
        reset_output=args.reset_output,
    )

    print("Done")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
