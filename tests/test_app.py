import json
from pathlib import Path


def test_dataset_has_five_valid_cases():
    path = Path("data/test_cases.json")
    cases = json.loads(path.read_text(encoding="utf-8"))

    assert len(cases) >= 5

    required_fields = {"id", "category"}
    for case in cases:
        assert required_fields.issubset(case.keys())


def test_required_project_files_exist():
    assert Path("app.py").exists()
    assert Path("requirements.txt").exists()
    assert Path(".gitignore").exists()
