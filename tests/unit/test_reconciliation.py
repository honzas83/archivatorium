from archivatorium.utils.metadata import reconcile_metadata


def test_reconcile_metadata_all_cases() -> None:
    existing = {
        "title": "Manually Corrected Title",
        "summary": "Old summary.",
        "abstract": "Old abstract.",
        "pages": 12,
        "source": "[[old_source.pdf]]",
        "sender": "Original Sender",
        "recipient": "",  # Empty recipient in existing
        "date": "1974-12-01",
        "archive_code": "NPG-74-2",
        "citekey": "old-citekey",
        "references": ["RefA", "RefB"],
        "custom_user_field": "KeepMe",
    }

    newly_extracted = {
        "title": "Newly Extracted Title",
        "summary": "This is a new one-sentence summary.",
        "abstract": "This is a new abstract.",
        "pages": 15,
        "source": "[[new_source.pdf]]",
        "sender": "New Sender",
        "recipient": "New Recipient",
        "date": "1974-12-02",
        "archive_code": "NPG-74-3",
        "citekey": "new-citekey",
        "references": ["RefB", "RefC"],
    }

    reconciled = reconcile_metadata(existing, newly_extracted)

    # 1. Title, sender, date, archive_code are preserved from existing if non-empty
    assert reconciled["title"] == "Manually Corrected Title"
    assert reconciled["sender"] == "Original Sender"
    assert reconciled["date"] == "1974-12-01"
    assert reconciled["archive_code"] == "NPG-74-2"

    # 2. Recipient is filled from newly_extracted as existing was empty
    assert reconciled["recipient"] == "New Recipient"

    # 3. Summary, pages, source, citekey, abstract are overwritten with newly calculated/extracted values
    assert reconciled["summary"] == "This is a new one-sentence summary."
    assert reconciled["abstract"] == "This is a new abstract."
    assert reconciled["pages"] == 15
    assert reconciled["source"] == "[[new_source.pdf]]"
    assert reconciled["citekey"] == "new-citekey"

    # 4. References are set union, sorted
    assert reconciled["references"] == ["RefA", "RefB", "RefC"]

    # 5. Custom user fields are preserved
    assert reconciled["custom_user_field"] == "KeepMe"
