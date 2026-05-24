import json
import os
import sys
import time
from dotenv import load_dotenv
from src.schema import ScenarioInput, ScenarioOutput
from src.prompts import SYSTEM_PROMPT, build_user_prompt, build_repair_prompt
from src.validator import validate_quality
load_dotenv()
MAX_TOKENS = 2048
MAX_RETRIES = 2
API_RETRIES = 5
API_RETRY_DELAY = 8
GENERATE_RETRIES = 3
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
class ScenarioChain:
    def __init__(self, api_key: str | None = None):
        from groq import Groq
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in .env file or pass it directly.\n"
                "Get your key at: https://console.groq.com/keys"
            )
        self.client = Groq(api_key=key)
        self.model_name = GROQ_MODEL
        print(f">> Using Groq ({self.model_name})")
    def generate(self, input_data: dict | ScenarioInput, verbose: bool = False) -> ScenarioOutput:
        if isinstance(input_data, dict):
            scenario_input = ScenarioInput(**input_data)
        else:
            scenario_input = input_data
        if verbose:
            print(f"\n{'='*60}")
            print(f">> Input: {scenario_input.icp_type} | {scenario_input.milestone_code} | {scenario_input.skill_target} | {scenario_input.language}")
            print(f"{'='*60}")
        user_prompt = build_user_prompt(
            icp_type=scenario_input.icp_type,
            milestone_code=scenario_input.milestone_code,
            skill_target=scenario_input.skill_target,
            language=scenario_input.language,
        )
        scenario_output = None
        last_gen_error = None
        for gen_attempt in range(GENERATE_RETRIES):
            if verbose:
                print(f"\n>> Stage 1: Calling {self.model_name} (attempt {gen_attempt + 1}/{GENERATE_RETRIES})...")
            raw_output = self._call_groq(user_prompt)
            if verbose:
                print(f">> Got response ({len(raw_output)} chars)")
            scenario_output, parse_error = self._parse_output(raw_output)
            if parse_error:
                last_gen_error = parse_error
                if verbose:
                    print(f">> Parse/validation error: {parse_error}")
                if gen_attempt < GENERATE_RETRIES - 1:
                    if verbose:
                        print(f">> Retrying full generation...")
                    time.sleep(2)
                    continue
                else:
                    raise ValueError(f"Failed to produce valid JSON after {GENERATE_RETRIES} generation attempts: {parse_error}")
            else:
                break
        if verbose:
            print(f">> Schema validation passed")
        for attempt in range(MAX_RETRIES + 1):
            issues = validate_quality(
                scenario_output,
                icp_type=scenario_input.icp_type,
                language=scenario_input.language,
            )
            if not issues:
                if verbose:
                    print(f">> All quality checks passed")
                break
            if attempt < MAX_RETRIES:
                if verbose:
                    print(f"\n>> Quality issues found (attempt {attempt + 1}/{MAX_RETRIES}):")
                    for issue in issues:
                        print(f"   - {issue}")
                    print(f">> Sending repair prompt...")
                repair_prompt = build_repair_prompt(
                    scenario_output.model_dump_json(indent=2),
                    issues,
                )
                raw_output = self._call_groq(repair_prompt)
                repaired_output, parse_error = self._parse_output(raw_output)
                if parse_error:
                    if verbose:
                        print(f">> Repair produced invalid output: {parse_error}, keeping previous valid output")
                    continue
                scenario_output = repaired_output
            else:
                if verbose:
                    print(f"\n>> Remaining quality issues after {MAX_RETRIES} retries:")
                    for issue in issues:
                        print(f"   - {issue}")
                    print(f"   Returning best available output.")
        return scenario_output
    def _call_groq(self, user_prompt: str) -> str:
        last_error = None
        for attempt in range(API_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=MAX_TOKENS,
                    temperature=0.7,
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                error_str = str(e)
                is_retryable = any(keyword in error_str.lower() for keyword in [
                    "503", "429", "413", "400", "rate limit", "rate_limit",
                    "connection", "timeout", "overloaded", "too many",
                    "request too large", "service unavailable",
                    "internal server error", "500",
                    "json_validate_failed", "failed to generate json",
                    "failed_generation",
                ])
                if is_retryable:
                    wait = API_RETRY_DELAY * (attempt + 1)
                    print(f">> API error (retryable), retrying in {wait}s (attempt {attempt + 1}/{API_RETRIES})...")
                    time.sleep(wait)
                else:
                    raise
        raise last_error
    def _parse_output(self, raw: str) -> tuple[ScenarioOutput | None, str | None]:
        try:
            text = raw.strip()
            if text.startswith("```"):
                first_newline = text.index("\n")
                text = text[first_newline + 1:]
                if text.endswith("```"):
                    text = text[:-3].strip()
            data = json.loads(text)
            output = ScenarioOutput(**data)
            return output, None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {e}"
        except Exception as e:
            return None, f"Validation error: {e}"