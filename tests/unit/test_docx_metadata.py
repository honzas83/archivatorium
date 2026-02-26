from ocrpolish.data_model import PageMetadata

def test_page_metadata_init():
    metadata = PageMetadata(
        pdf_page_number=1,
        original_page_number="-1-",
        header_left=["HeaderL"],
        header_right=["HeaderR"],
        footer_left=["FooterL"],
        footer_right=["FooterR"]
    )
    assert metadata.pdf_page_number == 1
    assert metadata.original_page_number == "-1-"
    assert "HeaderL" in metadata.header_left
