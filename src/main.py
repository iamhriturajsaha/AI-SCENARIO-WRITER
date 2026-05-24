import argparse
import json
import sys
from pathlib import Path
from src.chain import ScenarioChain
console_encoding_fixed = False
def main():
    parser = argparse.ArgumentParser(
        description="Scenario Writer -- Generate workplace scenarios for career upskilling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main --input test_cases/inputs/icp_a_01.json
  python -m src.main --json "{\\\"icp_type\\\":\\\"high_wage\\\",\\\"milestone_code\\\":\\\"M03\\\",\\\"skill_target\\\":\\\"conflict_resolution\\\",\\\"language\\\":\\\"en\\\"}"
  python -m src.main --input test_cases/inputs/icp_b_01.json --output result.json
        """,
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input", "-i",
        type=str,
        help="Path to input JSON file",
    )
    input_group.add_argument(
        "--json", "-j",
        type=str,
        help="Inline JSON input string",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Path to save output JSON (default: print to stdout)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose logging",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Groq API key (overrides .env)",
    )
    args = parser.parse_args()
    try:
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: Input file not found: {input_path}")
                sys.exit(1)
            with open(input_path) as f:
                input_data = json.load(f)
        else:
            input_data = json.loads(args.json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}")
        sys.exit(1)
    if not args.quiet:
        print(f"\n--- INPUT ---")
        print(json.dumps(input_data, indent=2))
        print(f"-------------\n")
    try:
        chain = ScenarioChain(api_key=args.api_key)
        result = chain.generate(input_data, verbose=not args.quiet)
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    output_json = result.model_dump_json(indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_json)
        if not args.quiet:
            print(f"\nOutput saved to: {output_path}")
    if not args.quiet:
        print(f"\n--- GENERATED SCENARIO ---")
        sys.stdout.buffer.write(output_json.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        print(f"--------------------------")
    else:
        sys.stdout.buffer.write(output_json.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
if __name__ == "__main__":
    main()