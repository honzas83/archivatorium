import re

import yaml


def test_normalization_regex_logic():
    # Simulate the logic we'll implement in InterlinkingService
    rules = [
        {"pattern": r"\(Staff[ -]?Group\)", "replacement": "(SG)"},
        {"pattern": r"\(Study[ -]?Group\)|Study/", "replacement": "(STUDY)"},
    ]

    test_cases = [
        ("NPG(Staff Group)N(72)65", "NPG(SG)N(72)65"),
        ("NPG(Staff-Group)N(72)65", "NPG(SG)N(72)65"),
        ("NPG(StaffGroup)N(72)65", "NPG(SG)N(72)65"),
        (
            "NPG/Study/38",
            "NPG/(STUDY)38",
        ),  # Note: / will be handled by standard normalization later
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


def test_real_unifications_file():
    with open("topics/unifications.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    rules = data.get("unifications", [])

    test_cases = [
        ("NPG(Staff Group)N(72)65", "NPG(SG)N(72)65"),
        ("NPG(Staff-Group)N(72)65", "NPG(SG)N(72)65"),
        ("NPG(StaffGroup)N(72)65", "NPG(SG)N(72)65"),
        ("NPG/Study/38", "NPG(STUDY)38"),
        ("NPG(Study Group)38", "NPG(STUDY)38"),
        ("NGP/D(74)10", "NPG/D(74)10"),
        ("NPC/D(74)10", "NPG/D(74)10"),
        ("NPQ/D(74)10", "NPG/D(74)10"),
        ("DFC/D(69)4", "DPC/D(69)4"),
        ("DPO/D(69)18", "DPC/D(69)18"),
        ("DPP/69/126", "DPC/D(69)126"),
        ("DFP/69/51", "DPC/D(69)51"),
        ("DPC/0(69)36", "DPC/D(69)36"),
        ("DPC/1(69)36", "DPC/D(69)36"),
        ("G-M(53)104", "C-M(53)104"),
        ("O-M(55)15", "C-M(55)15"),
        ("C-N(55)15", "C-M(55)15"),
        ("G-R(54)21", "C-R(54)21"),
        ("O-R(56)1", "C-R(56)1"),
        ("FO/55/112", "PO/55/112"),
        ("AO/127-D/189", "AC/127-D/189"),
        ("AC/23-REPORT(01)23 to 01", "AC/23-REPORT(01)23 to 01"),
        ("NPG(SG)WP(68)2(Revised)", "NPG(SG)WP(68)2-REV1"),
        ("NPG(SG)WP(68)2(2nd Revise)", "NPG(SG)WP(68)2-REV2"),
        ("DRC/WP(74)1(Revised)", "DRC/WP(74)1(Revised)"),
        ("DFC/DS(69)4", "DRC/DS(69)4"),
        ("DEC/N(71)1", "DRC/N(71)1"),
        ("DFC/WP(72)1", "DRC/WP(72)1"),
        ("NP(Staff Group)WP(68)2", "NPG(SG)WP(68)2"),
        ("MPG(Staff Group)N(72)65", "NPG(SG)N(72)65"),
        ("DPO(72)", "DPQ(72)"),
        ("DPG(73)", "DPQ(73)"),
        ("DFC(74)1", "DPQ(74)1"),
        ("DPO(72) NETHERLANDS - D/1", "DPQ(72) NETHERLANDS - D/1"),
    ]

    for original, expected in test_cases:
        current = original
        for rule in rules:
            current = re.sub(rule["pattern"], rule["replacement"], current, flags=re.IGNORECASE)
        assert current == expected


