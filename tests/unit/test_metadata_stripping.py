from archivatorium.utils.metadata import strip_generated_sections


def test_strip_generated_sections_all_present() -> None:
    content = """---
title: Sample Title
author_name: Author Name
---
> [!info] Metadata
> | Field | Value |
> | --- | --- |
> | ≡&nbsp;**title**: | Sample Title |

> [!abstract]
> # Sample Title
> This is a sample abstract summary.
> ## Entities
> * States
>   - #Entities/State/Belgium

Some actual content text remains here.
It has multiple lines.

> [!citing this document]
> **Chicago**:
> ```
> Citation Chicago Style
> ```
"""
    cleaned = strip_generated_sections(content)
    assert "Some actual content text remains here." in cleaned
    assert "It has multiple lines." in cleaned
    assert "Sample Title" not in cleaned
    assert "[!info]" not in cleaned
    assert "[!abstract]" not in cleaned
    assert "[!citing" not in cleaned
    assert "---" not in cleaned


def test_strip_generated_sections_no_generated() -> None:
    content = "Just some clean body text with no frontmatter or callouts."
    cleaned = strip_generated_sections(content)
    assert cleaned == content
