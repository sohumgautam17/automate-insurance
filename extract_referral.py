def referral_package_prompt(pa_fields_with_context):
    return f"""
You are an expert assistant for processing prior authorization (PA) forms. Given a list of PA 
form fields (with context/questions) and a PDF referral package, extract the most relevant, 
specific information from the referral to fill each PA form field.

Guidelines:
1. For each PA form field, extract the exact answer from the referral package (dates, diagnoses, medications, dosages, etc.).
2. If information is missing or unclear, respond with "MISSING" or "UNCLEAR".
3. Use precise values and terminology from the source documents.
4. Format all dates as MM/DD/YYYY unless otherwise specified.
5. Only output valid JSON as described below.

<PA_FORM_DATA>
{pa_fields_with_context}
</PA_FORM_DATA>

## RESPONSE FORMAT
Return a JSON array. Each object must have:
- name: field identifier (e.g., "CB1")
- page: page number
- field_label: original field label
- answer: answer to the question based on the referral package PDF

Example:
[
  {{
    "name": "CB1",
    "page": 2,
    "field_label": "Start of treatment",
    "answer": "06/15/2024"
  }},
  {{
    "name": "T2",
    "page": 2,
    "field_label": "Start date: (MM/DD/YYYY)",
    "answer": "06/15/2024"
  }},
  {{
    "name": "CB2",
    "page": 2,
    "field_label": "Is the patient currently taking medication?",
    "answer": "No"
  }},
  {{
    "name": "T3",
    "page": 3,
    "field_label": "Diagnosis code (ICD-10)",
    "answer": "MISSING"
  }}
]
"""
