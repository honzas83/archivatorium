# Feature Specification: Normalize Qwen 3.8 OCR Output

**Feature Branch**: `037-qwen38-ocr-cleanup`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Adapt OCR processing to Qwen 3.8 output by removing reasoning text through the closing `</think>` tag, removing shared top-level indentation while preserving relative indentation, logging average processing time per input page, and reporting overall performance since the beginning of the OCR command."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Remove leaked reasoning from OCR text (Priority: P1)

As an archive operator, I want reasoning emitted before a closing `</think>` marker removed from OCR output so that saved documents contain only recognized page content.

**Why this priority**: Reasoning text is not part of the source document and would directly corrupt the archival transcription.

**Independent Test**: Process an OCR response containing reasoning, a closing `</think>` marker, and recognized page text; verify that the saved result begins with the recognized text and contains neither the marker nor anything preceding it.

**Acceptance Scenarios**:

1. **Given** an OCR response containing `analysis text</think>Recognized page`, **When** the response is normalized, **Then** the result contains `Recognized page` and excludes both `analysis text` and `</think>`.
2. **Given** an OCR response containing multiple closing `</think>` markers, **When** the response is normalized, **Then** everything through the final closing marker is discarded and only the content following it remains.
3. **Given** an OCR response without a closing `</think>` marker, **When** the response is normalized, **Then** no content is removed by reasoning cleanup.

---

### User Story 2 - Remove shared top-level indentation (Priority: P2)

As an archive operator, I want artificial top-level indentation removed from OCR output so that document text starts at the correct margin while meaningful relative indentation remains intact.

**Why this priority**: Qwen 3.8 may indent the entire response, which produces incorrectly formatted archival documents, but nested structures still need their relative indentation.

**Independent Test**: Normalize output whose nonblank lines begin with four or eight spaces; verify that four spaces are removed from every nonblank line, leaving the originally eight-space lines indented by four spaces.

**Acceptance Scenarios**:

1. **Given** nonblank OCR lines indented by four and eight spaces, **When** the response is normalized, **Then** four spaces are removed from each line and the four-space difference is preserved.
2. **Given** OCR output where at least one nonblank line has no leading spaces, **When** the response is normalized, **Then** indentation is unchanged because there is no shared top-level indentation.
3. **Given** blank lines among indented OCR lines, **When** the response is normalized, **Then** blank lines do not reduce the shared indentation calculation or gain visible whitespace.

---

### User Story 3 - Observe average OCR throughput (Priority: P3)

As an archive operator, I want the OCR log to report both per-PDF average processing time and overall average processing time since the OCR command began so that I can compare individual documents, model and host performance, and whole-batch throughput.

**Why this priority**: Throughput visibility supports operational planning and model evaluation without changing the recognized content.

**Independent Test**: Run one OCR command over multiple PDFs with known page counts and durations; verify each PDF retains its own timing summary and the command completion log reports command-wide elapsed time divided by all pages attempted across the batch.

**Acceptance Scenarios**:

1. **Given** an OCR run that attempts ten input pages in 50 seconds, **When** the run completes, **Then** the completion log reports an average of 5 seconds per page.
2. **Given** a run containing retries or failed page attempts, **When** average time is calculated, **Then** their elapsed time remains included and every attempted input page is counted once.
3. **Given** a run with zero input pages, **When** the run completes, **Then** the log reports that average page time is unavailable and the run does not fail.
4. **Given** one OCR command processes multiple PDFs, **When** the command completes, **Then** the log reports overall attempted pages, total elapsed time since command entry, and the resulting overall average seconds per attempted page.
5. **Given** an OCR command finds no PDFs or attempts no pages, **When** it completes, **Then** the overall average is reported as unavailable without an error.
6. **Given** a long OCR command is still processing a batch, **When** each PDF run finishes, **Then** the log reports the cumulative attempted pages, elapsed time since command entry, and current average seconds per page without waiting for the entire command to finish.

### Edge Cases

- A closing `</think>` marker may occur at the beginning or end of a response, on its own line, or adjacent to recognized content.
- A response may contain more than one closing `</think>` marker; only content after the final marker is considered OCR content.
- Removing the reasoning prefix may leave leading blank lines before the recognized content.
- OCR output may be empty or contain only whitespace after reasoning removal.
- Blank lines must be ignored when determining shared indentation.
- Output may contain lines with different indentation depths or a mixture of indented and unindented lines.
- Tabs and mixed tab/space indentation are not treated as removable shared space indentation because their visual width is ambiguous.
- A run may discover no input pages, or individual pages may fail or be retried.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST inspect every OCR model response for a closing `</think>` marker before saving recognized content.
- **FR-002**: When one or more closing `</think>` markers are present, the system MUST discard every character through and including the final marker.
- **FR-003**: When no closing `</think>` marker is present, reasoning cleanup MUST leave the response content unchanged.
- **FR-004**: After reasoning cleanup, the system MUST remove leading blank lines that only separated the marker from recognized page content.
- **FR-005**: The system MUST determine the minimum number of leading spaces shared by all nonblank OCR content lines.
- **FR-006**: The system MUST remove exactly that shared number of leading spaces from every nonblank line.
- **FR-007**: The system MUST preserve indentation differences between lines after shared top-level indentation is removed.
- **FR-008**: Blank lines MUST be excluded from the shared-indentation calculation and MUST remain blank in normalized output.
- **FR-009**: If any nonblank line begins without a space, the system MUST preserve indentation throughout the response.
- **FR-010**: The cleanup MUST apply to OCR responses regardless of which supported model name the operator selects, while specifically supporting observed Qwen 3.8 output.
- **FR-011**: The completion log for each OCR run MUST report the number of input pages attempted, total elapsed OCR processing time, and average elapsed time per attempted input page.
- **FR-012**: Average elapsed time per page MUST equal total elapsed OCR processing time divided by the number of input pages attempted, so retry and failure overhead remains represented while each input page is counted once.
- **FR-013**: For a run with zero attempted pages, the completion log MUST report that average time per page is unavailable without raising an error.
- **FR-014**: Existing model selection, page ordering, output naming, and failure handling behavior MUST remain unchanged.
- **FR-015**: The OCR command MUST emit a command-wide completion log containing all pages attempted across processed PDFs, total monotonic elapsed time since entry into the OCR command, and overall average seconds per attempted page.
- **FR-016**: Command-wide elapsed time MUST include engine initialization, recursive discovery, every per-PDF run, retry and failure handling, output writes, and CLI overhead until the command exits.
- **FR-017**: For a command with zero attempted pages, the command-wide completion log MUST report the overall average as unavailable without raising an error.
- **FR-018**: After every processed PDF, the OCR command MUST emit a cumulative timing log whose average is elapsed monotonic time since command entry divided by all pages attempted so far, using explicit `average_seconds_per_page_since_command_start` naming.

### Key Entities

- **OCR Response**: Raw text returned for one input page, potentially containing reasoning text, a closing reasoning marker, and globally indented recognized content.
- **Normalized Page Text**: Recognized page content after reasoning removal and shared-indentation removal, ready to be saved.
- **OCR Run Metrics**: Run-level measurements comprising attempted input-page count, total elapsed processing time, and derived average time per page.
- **OCR Command Metrics**: Batch-level measurements comprising attempted pages across every processed PDF, elapsed time since command entry, and the derived overall average time per page.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In validation samples containing a closing `</think>` marker, 100% of saved outputs exclude the marker and all preceding content.
- **SC-002**: In validation samples with shared top-level indentation, 100% of outputs start at the correct top-level margin while preserving every relative indentation difference.
- **SC-003**: OCR responses without a closing reasoning marker or shared indentation retain their original meaningful content and layout in 100% of regression cases.
- **SC-004**: Every OCR run completion log reports per-PDF attempted page count, total elapsed time, and average time per page, or an explicit unavailable value for a zero-page run.
- **SC-005**: For test runs with known page counts and durations, the reported average time per page is mathematically correct within the displayed rounding precision.
- **SC-006**: Existing OCR workflows continue to complete with no regression in page count, ordering, filenames, or error handling across the current regression suite.
- **SC-007**: Every OCR command completion log reports overall attempted pages, total time since command entry, and the mathematically correct overall average, or an explicit unavailable value when no pages were attempted.
- **SC-008**: During every multi-PDF OCR command, operators can see the current command-wide average after each PDF completes, before the final command summary.

## Assumptions

- Qwen 3.8 is selected through the existing model-selection interface; changing the default model is outside this feature's scope.
- A closing `</think>` marker indicates that all preceding response content is model reasoning rather than source-document text.
- If multiple closing markers occur, the final marker is the safest boundary because text before it may still contain leaked reasoning.
- Shared indentation means leading ASCII space characters common to every nonblank line; tabs are preserved unchanged.
- Cleanup occurs before recognized page text is persisted or combined with other pages.
- Per-PDF throughput uses elapsed `run_ocr` time divided by distinct pages attempted in that PDF; overall throughput uses elapsed time since OCR command entry divided by distinct pages attempted across the entire command.
