# Tag Format and Syntax Contract

This contract defines the authoritative hashtag syntax and schemas used by OCRPolish processors, parsers, and indexing services.

---

## 1. Authoritative Tag Grammar

Every canonical generated tag MUST conform to the following syntax:

```text
#<Prefix>/<Type-or-Path>
```

Where:
- `<Prefix>` is one of `Entities`, `Topics`, or `Tags`.
- All path components are separated by `/`.
- Components must not contain spaces or special characters; they use kebab-case (`Camel-Case` or `kebab-case`) containing only letters, numbers, and hyphens.

---

## 2. Supported Schemas

### 2.1. Entity Tags (`#Entities/`)

Entity tags represent structured real-world entities. The supported types and their exact structure are:

1. **State Tag**:
   - Format: `#Entities/State/<State-Name>`
   - Example: `#Entities/State/United-States`, `#Entities/State/West-Germany`
2. **Organization Tag**:
   - Format: `#Entities/Org/<Org-Name>`
   - Example: `#Entities/Org/NATO`, `#Entities/Org/European-Community`
3. **Person Tag**:
   - Format: `#Entities/Person/<Person-Name>`
   - Example: `#Entities/Person/Joseph-Luns`, `#Entities/Person/Richard-Nixon`
4. **City Tag**:
   - Format: `#Entities/City/<State-Name>/<City-Name>`
   - Example: `#Entities/City/United-Kingdom/London`, `#Entities/City/United-States/Washington`

### 2.2. Topic Tags (`#Topics/`)

Topic tags represent hierarchical classification items from the taxonomy:

- Format: `#Topics/<Category>/[<Subcategory>/...]/<Topic>`
- Example: `#Topics/Nuclear-Planning/Consultation-Procedures`, `#Topics/Force-Planning/Command-Structure`

### 2.3. Conceptual Tags (`#Tags/`)

Conceptual tags represent flat, vocabulary-driven keywords:

- Format: `#Tags/<Tag-Value>`
- Example: `#Tags/Strategic-Concept`, `#Tags/Exercise/Wintex-71` (if sub-categorized)

---

## 3. Invalid/Malformed Syntax (Diagnostics)

Any tag that does not match the rules above is treated as invalid and ignored. Examples of invalid tags:

- Obsolete unprefixed tags: `#Nuclear-Deterrence` (no prefix)
- Legacy prefixed tags: `#Category/Nuclear-Planning` (incorrect prefix `Category`)
- Malformed State tags: `#Entities/State` (missing name), `#Entities/State/US/East` (too many parts)
- Malformed City tags: `#Entities/City/London` (missing state), `#Entities/City/` (empty value)
- Unsupported Entity types: `#Entities/Country/France` (unsupported type `Country`)
