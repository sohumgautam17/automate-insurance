import enum
from google import genai
from google.genai import types
import httpx
import os 
import asyncio
import time
import json
import logging
import warnings
from typing import Dict, List, Any, Optional, Tuple
import pathlib
from pathlib import Path
import re
from datetime import datetime
import fitz
from pydantic import BaseModel, Field


def extract_fields_with_positions(pdf_path):
    doc = fitz.open(pdf_path)
    # print(doc.page_count)
    # print(doc.metadata)
    fields = []
    for page_num, page in enumerate(doc, start=1):
        for w in page.widgets() or []: # Extract all the text entry points in the pdf
            field = {
                "name": w.field_name,
                "type": "checkbox" if w.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX else "text",
                "value": w.field_value,
                "page":page_num,
                "field_type": w.field_type,
                "field_type_string": w.field_type_string,
                "label": w.field_label,
            }
            fields.append(field)

    fields_by_pages = {}
    for field in fields:
        page_num = field["page"]
        if field["page"] not in fields_by_pages:
            fields_by_pages[page_num] = []
        fields_by_pages[page_num].append(field)

    return fields_by_pages

if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    fields_by_page = extract_fields_with_positions("Input Data/Adbulla/PA.pdf")
    print(fields_by_page)
