import json
from pathlib import Path

dataset_path = Path("data/test_cases.json")

with dataset_path.open("r", encoding="utf-8") as file:
    cases = json.load(file)

assert len(cases) >= 5, "Expected at least five test cases."

for case in cases:
    assert case.get("id"), "A test case is missing its ID."
    assert case.get("prompt"), "A test case is missing its prompt."
    assert isinstance(case.get("expected"), list), (
        "Expected criteria must be a list."
    )

print(f"PASS: {len(cases)} valid test cases loaded.")

for case in cases:
    print(f"{case['id']} - {case['category']}")
