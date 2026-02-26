# Feature Specification: Improve DOCX Header and Footer Export

**Feature Branch**: `007-docx-header-footer-enhancement`  
**Created**: 2026-02-26  
**Status**: Draft  
**Input**: User description: "In this feature branch, we will improve DOCX export. First - regarding header and footer, include text 'PDF Page N' from the '# Page N' markdown header to DOCX footer and align right. If there is no original page number -X- in the page, use an empty string in the header and footer, do not reuse the previous page number. If the filtered line based on input filter is near the top / bottom page number, instead include it into DOCX header / footer. Filtering from MD stays as is. If it is before the page number, align left, if after the page number, align right. If there is an empty # Page N in markdown, include an empty page in DOCX containing just the footer with PDF Page N"

## Clarifications

### Session 2026-02-26
- Q: Handling Multiple -X- Markers on One Page → A: Use only the first (top-most) and last (bottom-most) -X- markers as anchors.
- Q: Conflict Resolution for Overlapping Proximity → A: Assign the line to the nearest -X- marker (in terms of number of lines).
- Q: Formatting of the "PDF Page N" Footer → A: Combine "PDF Page N" and any right-aligned filtered metadata in the same footer area.
- Q: Handling of Multiline Filtered Metadata → A: Join with a specific separator (e.g., " | " or "; ") on a single line.
- Q: Interaction with Existing Filter Sidecars → A: Keep strictly separate; .filtered.md shows clean text body, DOCX layout only affects .docx.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated "PDF Page N" Footer (Priority: P1)

As a user, I want every page in my DOCX to have a right-aligned footer "PDF Page N" derived from the `# Page N` marker in Markdown, even if the page content is empty.

**Why this priority**: Core navigation requirement for tracking the sequence of pages in the output document.

**Independent Test**: Convert MD with `# Page 1` and `# Page 2`. Verify both pages have "PDF Page 1" and "PDF Page 2" in the footer, even if one page is blank.

**Acceptance Scenarios**:

1. **Given** a Markdown marker `# Page 10`, **When** exported, **Then** the corresponding DOCX page footer must contain "PDF Page 10" right-aligned.
2. **Given** a marker `# Page 11` followed immediately by `# Page 12`, **When** exported, **Then** an empty page is created for Page 11 containing only the "PDF Page 11" footer.

---

### User Story 2 - Metadata Isolation for Original Page Numbers (Priority: P1)

As a user, I want the "original" page number (formatted as `-X-`) to be reflected in the headers/footers only for the page it belongs to. If a page lacks this marker, it should not inherit the marker from the previous page.

**Why this priority**: Prevents incorrect OCR metadata from being repeated across pages where it doesn't apply.

**Independent Test**: Page 1 has `-1-`, Page 2 has no `-X-`. Verify Page 2 header/footer does not contain `-1-` but still contains its own "PDF Page N" footer.

**Acceptance Scenarios**:

1. **Given** a page with an original marker `-42-`, **When** exported, **Then** that marker is included in the header/footer (in addition to "PDF Page N").
2. **Given** a page with *no* original marker, **When** exported, **Then** the area reserved for the original page number must be an empty string, while "PDF Page N" remains.

---

### User Story 3 - Contextual Metadata Migration (Priority: P2)

As a user, I want filtered lines (like document codes) that appear near the original page numbers (`-X-`) to be moved into the DOCX header or footer to keep the body text clean.

**Why this priority**: Improves document aesthetics by moving non-content metadata into dedicated margins.

**Independent Test**: Place a filtered line (e.g., "CONFIDENTIAL") before a `-1-` marker at the top of a page. Verify it moves to the Header, left-aligned.

**Acceptance Scenarios**:

1. **Given** a filtered line near an `-X-` marker at the *top* of a page, **When** exported, **Then** it is moved to the Header.
2. **Given** a filtered line near an `-X-` marker at the *bottom* of a page, **When** exported, **Then** it is moved to the Footer.
3. **Given** the filtered line is *before* the `-X-` marker, **When** exported, **Then** it is aligned left in its respective header/footer.
4. **Given** the filtered line is *after* the `-X-` marker, **When** exported, **Then** it is aligned right in its respective header/footer.

### Edge Cases

- **Multiple -X- Markers**: If a page has three or more `-X-` markers, only the first (top-most) and last (bottom-most) are used as anchors for moving filtered metadata.
- **Overlapping Metadata**: If a filtered line falls within the search window of both the first and last `-X-` markers, it MUST be assigned to the marker to which it is vertically closest (by line count).
- **Filtered Line without -X-**: If a filtered line exists but there is no `-X-` marker on the page. (Assumption: The line remains in the body or is handled by standard MD filtering rules).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use `# Page N` markers to define page breaks and the "PDF Page N" footer text.
- **FR-002**: The system MUST scan each page for original page number markers using the pattern `-X-` (where X is numeric).
- **FR-003**: The system MUST ensure the "PDF Page N" footer is always present and right-aligned. It MUST be combined with any other right-aligned filtered metadata (from FR-007/FR-008) in the same footer area.
- **FR-004**: If no `-X-` marker is present on a page, the system MUST NOT include an original page number in the header/footer and MUST NOT reuse the value from the previous page.
- **FR-005**: The system MUST detect filtered lines that are adjacent to `-X-` markers (separated only by whitespace or other filtered lines).
- **FR-006**: **Header Assignment**: Filtered lines near the *first* (top-most) `-X-` marker on the page MUST be moved to the DOCX Header.
- **FR-007**: **Footer Assignment**: Filtered lines near the *last* (bottom-most) `-X-` marker on the page MUST be moved to the DOCX Footer.
- **FR-008**: **Horizontal Alignment**:
    - Lines *before* the `-X-` marker MUST be aligned Left.
    - Lines *after* the `-X-` marker MUST be aligned Right.
    - If multiple filtered lines are assigned to the same position, they MUST be joined on a single line using a separator (e.g., " | ").
- **FR-009**: The system MUST support generating a blank page for any `# Page N` marker that has no following content, preserving only the "PDF Page N" footer.

### Key Entities *(include if feature involves data)*

- **PDF Page Label**: The mandatory "PDF Page N" string in the footer.
- **Original Marker**: The `-X-` string found within the page text.
- **Filtered Metadata**: Text lines identified by the input filter that are subject to migration to margins.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of pages contain the mandatory "PDF Page N" footer.
- **SC-002**: 0% of `-X-` markers are "leaked" or inherited by subsequent pages that lack their own marker.
- **SC-003**: Filtered lines adjacent to top/bottom `-X-` markers are successfully removed from the body text in 100% of cases.
- **SC-004**: Correct four-way alignment (Top-Left, Top-Right, Bottom-Left, Bottom-Right) is achieved based on the filtered line's position relative to the `-X-` marker.

## Assumptions

- "Upper portion" and "Lower portion" of a page are determined by the appearance of the first and last `-X-` markers respectively.
- If only one `-X-` marker exists, the system decides whether it is "Header" or "Footer" based on its relative vertical position in the Markdown block.
- Standard MD filtering (removing lines from the output) still occurs for any filtered lines NOT moved to headers/footers.
- The logic for moving metadata to DOCX headers/footers is strictly layout-specific and DOES NOT affect the content of `.filtered.md` sidecar files, which will continue to show the "clean" text body as per existing logic.
