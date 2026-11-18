"""Send the fictional sample messages to the running Scam Shield API."""

import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "http://127.0.0.1:8000/api/check"
SAMPLE_FILE = Path(__file__).with_name("sample_messages.json")
VERDICTS = {"SCAM", "SUSPICIOUS", "SAFE"}
LANGUAGES = {"en", "hi", "kn"}


def load_test_cases() -> list[dict[str, Any]]:
    try:
        cases = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read {SAMPLE_FILE.name}: {error}") from error

    if not isinstance(cases, list) or len(cases) != 10:
        raise ValueError("sample_messages.json must contain exactly 10 test cases.")

    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Test case {index} must be a JSON object.")
        if type(case.get("number")) is not int or case["number"] < 1:
            raise ValueError(f"Test case {index} must have a positive integer number.")
        if not isinstance(case.get("text"), str) or not case["text"].strip():
            raise ValueError(f"Test case {index} must have non-empty text.")
        if not isinstance(case.get("language"), str) or case["language"] not in LANGUAGES:
            raise ValueError(f"Test case {index} has an unsupported language.")
        if (
            not isinstance(case.get("expected_verdict"), str)
            or case["expected_verdict"] not in VERDICTS
        ):
            raise ValueError(f"Test case {index} has an invalid expected verdict.")
        if not isinstance(case.get("name"), str):
            raise ValueError(f"Test case {index} must have a name.")

    return cases


def _http_error_detail(body: bytes) -> str:
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return ""

    detail = data.get("detail") if isinstance(data, dict) else None
    if isinstance(detail, str):
        return detail[:180]
    if isinstance(detail, list):
        messages = [
            item["message"]
            for item in detail
            if isinstance(item, dict) and isinstance(item.get("message"), str)
        ]
        return " ".join(messages)[:180]
    return ""


def _validate_response(data: Any, requested_language: str) -> tuple[str | None, str | None]:
    if not isinstance(data, dict):
        return None, "Response must be a JSON object."

    verdict = data.get("verdict")
    if not isinstance(verdict, str) or verdict not in VERDICTS:
        return None, "Response has a missing or invalid verdict."

    score = data.get("score")
    if type(score) is not int or not 0 <= score <= 100:
        return None, "Response has an invalid score."

    if not isinstance(data.get("reasons"), list):
        return None, "Response has an invalid reasons field."
    for reason in data["reasons"]:
        explanations = reason.get("explanations") if isinstance(reason, dict) else None
        if (
            not isinstance(reason, dict)
            or not isinstance(reason.get("code"), str)
            or type(reason.get("risk_weight")) is not int
            or not isinstance(explanations, dict)
            or any(not isinstance(explanations.get(code), str) for code in LANGUAGES)
        ):
            return None, "Response contains an invalid reason."

    links = data.get("extracted_links")
    if not isinstance(links, list) or any(not isinstance(link, str) for link in links):
        return None, "Response has an invalid extracted_links field."
    if not isinstance(data.get("explanation"), str):
        return None, "Response has an invalid explanation field."
    if data.get("language") != requested_language:
        return None, "Response language does not match the request."

    return verdict, None


def check_one(case: dict[str, Any]) -> tuple[str, str | None]:
    request_body = json.dumps(
        {"text": case["text"], "language": case["language"]},
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(
        API_URL,
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            response_body = response.read()
    except HTTPError as error:
        detail = _http_error_detail(error.read())
        message = f"HTTP {error.code}"
        if detail:
            message = f"{message}: {detail}"
        return "ERROR", message
    except (URLError, OSError) as error:
        reason = getattr(error, "reason", error)
        return "ERROR", f"Connection error: {reason}"

    try:
        response_data = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "INVALID", "API returned a non-JSON response."

    actual_verdict, validation_error = _validate_response(
        response_data,
        case["language"],
    )
    if validation_error:
        return "INVALID", validation_error
    return actual_verdict or "INVALID", None


def print_table(rows: list[dict[str, str]]) -> None:
    headers = ("Test", "Expected verdict", "Actual verdict", "Result")
    table_rows = [
        (
            row["number"],
            row["expected"],
            row["actual"],
            row["status"],
        )
        for row in rows
    ]
    widths = [
        max(len(headers[column]), *(len(row[column]) for row in table_rows))
        for column in range(len(headers))
    ]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    def print_row(values: tuple[str, ...]) -> None:
        print("| " + " | ".join(value.ljust(widths[i]) for i, value in enumerate(values)) + " |")

    print(border)
    print_row(headers)
    print(border)
    for row in table_rows:
        print_row(row)
    print(border)


def main() -> int:
    try:
        cases = load_test_cases()
    except ValueError as error:
        print(f"Test setup error: {error}", file=sys.stderr)
        return 2

    rows: list[dict[str, str]] = []
    errors: list[tuple[str, str]] = []

    for case in cases:
        actual, error = check_one(case)
        passed = actual == case["expected_verdict"]
        rows.append(
            {
                "number": f'{case.get("number", len(rows) + 1):02}',
                "expected": case["expected_verdict"],
                "actual": actual,
                "status": "PASS" if passed else "FAIL",
            }
        )
        if error:
            errors.append((rows[-1]["number"], error))

    print_table(rows)

    passed_count = sum(row["status"] == "PASS" for row in rows)
    failed_count = len(rows) - passed_count
    accuracy = passed_count / len(rows) * 100

    for number, error in errors:
        print(f"Test {number}: {error}")

    print(f"\nTotal tests passed: {passed_count}")
    print(f"Total tests failed: {failed_count}")
    print(
        f"Overall accuracy: {accuracy:.1f}% "
        "(passed cases divided by all 10 cases; request errors count as failures)"
    )
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
