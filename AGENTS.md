<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/032-item-type-metadata/plan.md
<!-- SPECKIT END -->

## Active Technologies
- Python 3.12 (`requires-python = ">=3.12"`) + Click CLI, Pydantic models, PyYAML, xlsxwriter, Ollama client integration, pytest/pytest-cov (027-fix-metadata-correctness)
- Filesystem Markdown/PDF vault output; YAML taxonomy and useful-tags configuration files; generated XLSX metadata index (027-fix-metadata-correctness)
- Python 3.12 (`requires-python = ">=3.12"`) + Click CLI, Pydantic metadata/tagging models, PyYAML taxonomy/useful-tags loading, Ollama client integration, pytest/pytest-cov (031-prompt-tag-normalization)
- Local filesystem Markdown/PDF vault output, YAML taxonomy/useful-tags files, generated XLSX metadata index; no storage changes for this feature (031-prompt-tag-normalization)

## Recent Changes
- 027-fix-metadata-correctness: Added Python 3.12 (`requires-python = ">=3.12"`) + Click CLI, Pydantic models, PyYAML, xlsxwriter, Ollama client integration, pytest/pytest-cov
