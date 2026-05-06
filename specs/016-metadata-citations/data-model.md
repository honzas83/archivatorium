# Data Model: Metadata Citations

This document describes the data structures and templates used for generating citations.

## CitationData

Internal structure used by the citation formatter:

| Field | Type | Description |
|-------|------|-------------|
| `author_first` | string | First name(s) of the author. |
| `author_last` | string | Surname of the author. |
| `author_initials` | string | Initials of the first name(s). |
| `title` | string | Title of the document. |
| `date` | string | Formatted date (YYYY/MM/DD). |
| `year` | string | Year (YYYY). |
| `month` | string | Month name or number. |
| `day` | string | Day of the month. |
| `institution` | string | Author's institution. |
| `archive_code` | string | Reference code. |
| `platform_name` | string | Name of the hosting platform. |
| `url` | string | URL or placeholder to the document. |
| `url_date` | string | Today's date (YYYY-MM-DD). |

## Templates

### Chicago
`Author First, Author Last, “Title,” YYYY/MM/DD, Author_Institution, Archive_Code, Our Platform Name, URL, URLDate.`

### Harvard
`Author Last, Author First Initials. (YYYY). “Title,” Author_Institution, Archive_Code, Our Platform Name, URL, URLDate.`

### BibTeX
```bibtex
@misc{citekey,
  author = {Author Last Name, First Name},
  title = {Title},
  year = {YYYY},
  month = {Month},
  day = {Day},
  note = {Author_Institution, Archive_Code, Our Platform Name},
  url = {URL},
  urldate = {Today’s Date}
}
```
