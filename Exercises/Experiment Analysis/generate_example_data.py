from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


def generate_example_data(output: Path, seed: int = 2026, users_per_variant: int = 1000) -> None:
    if users_per_variant < 1:
        raise ValueError("users_per_variant must be positive")

    output.parent.mkdir(parents=True, exist_ok=True)
    generator = random.Random(seed)
    with output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(["user_id", "variant", "converted"])
        for variant, conversion_probability in (("control", 0.10), ("treatment", 0.14)):
            for user_number in range(1, users_per_variant + 1):
                converted = int(generator.random() < conversion_probability)
                writer.writerow(
                    [f"{variant}-{user_number:05d}", variant, converted]
                )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a seeded illustrative experiment file.")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--users-per-variant", type=int, default=1000)
    args = parser.parse_args()
    generate_example_data(args.output, args.seed, args.users_per_variant)
    print(f"Wrote {args.users_per_variant * 2} illustrative rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
