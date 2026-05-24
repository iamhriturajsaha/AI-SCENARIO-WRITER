import argparse
import json
import sys
import time
from pathlib import Path
from src.chain import ScenarioChain
from src.schema import ScenarioOutput
from src.validator import validate_quality
INPUT_DIR = Path("Test Cases/Inputs")
OUTPUT_DIR = Path("Test Cases/Outputs")
def run_single_test(chain: ScenarioChain, input_path: Path, verbose: bool = False) -> dict:
    test_name = input_path.stem
    with open(input_path) as f:
        input_data = json.load(f)
    result = {
        "test_name": test_name,
        "input": input_data,
        "status": "UNKNOWN",
        "schema_valid": False,
        "quality_issues": [],
        "output": None,
        "error": None,
        "duration_seconds": 0,
    }
    start_time = time.time()
    try:
        output = chain.generate(input_data, verbose=verbose)
        result["output"] = output.model_dump()
        result["schema_valid"] = True
        issues = validate_quality(output, input_data["icp_type"], input_data["language"])
        result["quality_issues"] = issues
        if issues:
            result["status"] = "WARN"
        else:
            result["status"] = "PASS"
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = str(e)
    result["duration_seconds"] = round(time.time() - start_time, 2)
    return result
def main():
    parser = argparse.ArgumentParser(description="Run Scenario Writer test cases")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--test", "-t", type=str, help="Run a specific test by name (e.g. icp_a_01)")
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        chain = ScenarioChain()
    except ValueError as e:
        print(f"Setup Error: {e}")
        sys.exit(1)
    if args.test:
        input_files = list(INPUT_DIR.glob(f"{args.test}.json"))
        if not input_files:
            print(f"Test not found: {args.test}")
            sys.exit(1)
    else:
        input_files = sorted(INPUT_DIR.glob("*.json"))
    if not input_files:
        print("No test inputs found in Test Cases/Inputs/")
        sys.exit(1)
    print(f"\nRunning {len(input_files)} test case(s)...\n")
    results = []
    for input_path in input_files:
        print(f"  > Running {input_path.stem}...", end=" ", flush=True)
        result = run_single_test(chain, input_path, verbose=args.verbose)
        results.append(result)
        if input_path != input_files[-1]:
            time.sleep(3)
        output_path = OUTPUT_DIR / f"{input_path.stem}_output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result["output"] if result["output"] else {"error": result["error"]}, f, indent=2, ensure_ascii=False)
        if result["status"] == "PASS":
            print(f"PASS ({result['duration_seconds']}s)")
        elif result["status"] == "WARN":
            print(f"WARN ({result['duration_seconds']}s)")
        else:
            print(f"FAIL ({result['duration_seconds']}s)")
            if result["error"]:
                print(f"     Error: {result['error']}")
    print(f"\n{'='*60}")
    print(f"{'Test Case':<15} {'ICP':<12} {'Skill':<30} {'Lang':<6} {'Schema':<8} {'Status':<8} {'Time'}")
    print(f"{'-'*60}")
    pass_count = 0
    for r in results:
        schema_ok = "OK" if r["schema_valid"] else "FAIL"
        if r["status"] == "PASS":
            pass_count += 1
        elif r["status"] == "WARN":
            pass_count += 1
        print(f"{r['test_name']:<15} {r['input']['icp_type']:<12} {r['input']['skill_target']:<30} {r['input']['language']:<6} {schema_ok:<8} {r['status']:<8} {r['duration_seconds']}s")
    print(f"{'='*60}")
    total = len(results)
    print(f"  Schema pass rate: {sum(1 for r in results if r['schema_valid'])}/{total}")
    print(f"  Quality pass rate: {sum(1 for r in results if not r['quality_issues'])}/{total}")
    print(f"  Overall: {pass_count}/{total} passed")
    print(f"{'='*60}\n")
    full_results_path = OUTPUT_DIR / "_test_results_summary.json"
    with open(full_results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"Outputs saved to: {OUTPUT_DIR}/")
    print(f"Full results: {full_results_path}")
if __name__ == "__main__":
    main()