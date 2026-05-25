# Quickstart: fix-interlink-pages-timeout

This feature fixes several bugs and adds configuration for Ollama calls.

## Archive Code Unification
Documents referencing `NPG(Staff Group)N(72)65` will now automatically link to documents with archive code `NPG(SG)N(72)65`.

## Page Counting
If a document has headers for Page 1, Page 2, and Page 5, `ocrpolish` will now correctly report `3` pages instead of `5`.

## Ollama Timeout
If Ollama is slow, `ocrpolish` will wait up to 5 minutes by default. You can change this in `ocrpolish/services/ollama_client.py`.
