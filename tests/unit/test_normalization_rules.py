import re

import yaml


def test_normalization_regex_logic():
    # Simulate the logic we'll implement in InterlinkingService
    rules = [
        {"pattern": r"\(Staff[ -]?Group\)", "replacement": "(SG)"},
        {"pattern": r"\(Study[ -]?Group\)|Study/", "replacement": "(STUDY)"}
    ]
    
    test_cases = [
        ("NPG(Staff Group)N(72)65", "NPG(SG)N(72)65"),
        ("NPG(Staff-Group)N(72)65", "NPG(SG)N(72)65"),
        ("NPG(StaffGroup)N(72)65", "NPG(SG)N(72)65"),
        ("NPG/Study/38", "NPG/(STUDY)38"), # Note: / will be handled by standard normalization later
        ("NPG(Study Group)38", "NPG(STUDY)38"),
    ]
    
    for original, expected in test_cases:
        current = original
        for rule in rules:
            current = re.sub(rule["pattern"], rule["replacement"], current, flags=re.IGNORECASE)
        assert current == expected

def test_yaml_loading(tmp_path):
    yaml_content = """
unifications:
  - pattern: "\\\\(Staff[ -]?Group\\\\)"
    replacement: "(SG)"
  - pattern: "\\\\(Study[ -]?Group\\\\)|Study/"
    replacement: "(STUDY)"
"""
    yaml_file = tmp_path / "unifications.yaml"
    yaml_file.write_text(yaml_content)
    
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    
    assert "unifications" in data
    assert len(data["unifications"]) == 2
    assert data["unifications"][0]["replacement"] == "(SG)"
