# Automated PA Form Filling – Implementation Guide

## Overview

This repository contains a **Python pipeline to automate the filling of Prior Authorization (PA) PDF forms** using structured answer data. The solution is designed to be **generic**: it works with any widget-based (fillable) PDF form, as long as you provide a JSON file mapping each field name to its answer.

---

## How It Works

- **Input:**  
  - A fillable PDF form (e.g., `PA.pdf`)
  - An `answers.json` file containing a list of objects, each with:
    - `"name"`: the exact PDF field name
    - `"answer"`: the value to fill in that field

- **Output:**  
  - A filled PDF form (`filled_pa_form.pdf`) with all matching fields populated.

---

## Implementation Details

- **No Hardcoded Mapping:**  
  The script does **not** use any hardcoded field label-to-name mapping. It simply matches the `"name"` in your `answers.json` to the PDF field name.
- **Generic & Portable:**  
  Works with any fillable PDF form, as long as your JSON uses the correct field names.
- **Supported Field Types:**  
  - Text fields (including type 2 and 7 in PyMuPDF)
  - Checkboxes (type 1)
- **Debug Output:**  
  The script prints which fields are found, which are filled, and which are skipped or missing.

---

## Usage

### 1. Prepare Your Files

- Place your fillable PDF (e.g., `Input Data/Adbulla/PA.pdf`) in the appropriate folder.
- Create an `answers.json` file like this:
  ```json
  [
    {"name": "T12", "answer": "John"},
    {"name": "T13", "answer": "Doe"},
    {"name": "CB1", "answer": "Yes"}
    // ...
  ]
  ```

### 2. Run the Script

```bash
python fill_form.py
```

- The script will generate `filled_pa_form.pdf` in the current directory.

### 3. View the Output

- **Use Adobe Acrobat Reader** or another full-featured PDF viewer to see the filled fields. (Some viewers, like macOS Preview, may not display filled fields.)

---

## Installation

1. **Install dependencies:**
   ```bash
   pip install PyMuPDF
   ```
   or, if using conda:
   ```bash
   conda install -c conda-forge pymupdf
   ```

2. **Clone this repo and place your PDFs and JSON files as described above.**

---

## How the Code Works

- Loads all answers from `answers.json` into a dictionary.
- Opens the PDF with PyMuPDF (`fitz`).
- Iterates through all form fields (text and checkbox).
- If a field name matches a key in the answers, fills it with the provided value.
- Saves the filled PDF.

---

## Assumptions & Limitations

- **Field names in `answers.json` must match the PDF field names exactly.**
- Only widget-based (fillable) PDFs are supported.
- If a field is not filled, it's either missing from the JSON or not a fillable field.
- The script does not attempt fuzzy matching or label-based matching (but can be extended to do so).
- Some PDF viewers may not display filled fields unless you use Adobe Acrobat Reader.

---

## Example Output

- See `filled_pa_form.pdf` for a sample filled form.
- The script prints a summary of which fields were filled and which were skipped.

---

## Troubleshooting

- **Fields not appearing filled?**  
  Try opening the PDF in Adobe Acrobat Reader.
- **Fields still blank?**  
  Double-check that the `"name"` in your JSON matches the PDF field name.
- **Want to fill more fields?**  
  Add more entries to your `answers.json` with the correct field names.

---

## Contact

For questions or improvements, open an issue or PR!
