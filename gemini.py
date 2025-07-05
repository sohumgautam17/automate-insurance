import enum
import mimetypes
from pyclbr import Function
from google import genai
from google.genai import types
import httpx
import os 
from dotenv import load_dotenv
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
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def query_gemini_async(gemini_client, pdf_path, prompt, model="gemini-2.5-flash-preview-04-17", max_retries=5):
    filepath = Path(pdf_path)

    for attempt in range(max_retries):
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: gemini_client.models.generate_content(
                    model=model,
                    contents=[
                        types.Part.from_bytes(
                            data=filepath.read_bytes(),
                            mime_type="application/pdf"
                        ),
                        prompt]
                )
            )
            return response.text
            
        except Exception as e:
            if "503" in str(e) or "overloaded" in str(e).lower():
                wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                logger.warning(f"Server overload (503) on attempt {attempt + 1}/{max_retries}. Waiting {wait_time:.2f}s before retry...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Max retries ({max_retries}) reached. Server still overloaded.")
                    raise
            else:
                # For non-503 errors, don't retry
                logger.error(f"Non-retryable error: {e}")
                raise

class PAFormAnswer(BaseModel):
    name:str
    page:int
    field_label:str
    answer: str = Field(description="Answer to the questions on the PA form")


async def query_gemini_for_answers(gemini_client, pdf_path, prompt, model="gemini-2.5-flash-preview-04-17", max_retries=5):
    filepath = Path(pdf_path)

    for attempt in range(max_retries):
        try:
            response = gemini_client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(
                        data=filepath.read_bytes(),
                        mime_type="application/pdf"
                    ),
                    prompt],
                config={
                    "response_mime_type":"application/json",
                    "response_schema": list[PAFormAnswer],
                }
            )
            return response.text
            
        except Exception as e:
            if "503" in str(e) or "overloaded" in str(e).lower():
                wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                logger.warning(f"Server overload (503) on attempt {attempt + 1}/{max_retries}. Waiting {wait_time:.2f}s before retry...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Max retries ({max_retries}) reached. Server still overloaded.")
                    raise
            else:
                # For non-503 errors, don't retry
                logger.error(f"Non-retryable error: {e}")
                raise


def form_context_prompt(pa_form: List):
    return f'''
        You are given:
        1. The complete Prior Authorization form PDF document.

        Required Processing:
        For each form field, analyze sequentially by page number and:
        1. Extract the implicit question being asked by the field:
        - For checkboxes: Frame the label as a yes/no question.
        - For text fields: Frame as an information request.
        - For dates: Specify what event/action the date refers to.

        2. Generate rich contextual information (25 words max) that includes:
        - The section/category the field belongs to
        - Whether it's a primary question or sub-question
        - Whose information is being requested (patient, provider, insurer)
        - Any dependencies on other fields
        - Clinical relevance of the requested information

        3. Maintain relationships between related fields by:
        - Identifying parent-child relationships between questions
        - Noting conditional fields that depend on other answers
        - Preserving the logical flow of the form's structure

        Output Requirements:
        Return a JSON array where each object contains:
        - name: The field identifier (e.g., "CB1", "T1")
        - type: Field type ("checkbox", "text", etc.)
        - page: Page number in the form
        - field_label: Original field label text
        - question: The explicit question being asked by this field
        - context: Rich contextual description (max 25 words)

        <CRITICAL_REQUIREMENTS>
            - Every field must have both question and context added
            - Context must be specific and clinically relevant
            - Maintain logical relationships between fields
            - Preserve exact field names and labels
            - Keep context concise but informative (25 words max)
            - ONLY output valid JSON - no markdown formatting, no code blocks
            - Start with [ and end with ]
            - Use double quotes for all strings
        </CRITICAL_REQUIREMENTS>

        <RESPONSE_FORMAT>
            Return ONLY a JSON array like this:
            [
                {{
                    "name": "CB1",
                    "type": "checkbox",
                    "page": 2,
                    "field_label": "Start of treatment",
                    "question": "Is this a new treatment start for the patient? (yes/no)",
                    "context": "The answer to this question will indicate if the patient is beginning a new medication vs. continuing an existing one"
                }},
                {{
                    "name": "T2",
                    "type": "text",
                    "page": 2,
                    "field_label": "Start date: (MM)",
                    "question": "What is the month when treatment started?",
                    "context": "1 sentence describing the context of the field label"
                }}
            ]
        </RESPONSE_FORMAT>

        <PA_FORM_DATA>
        {pa_form}
        </PA_FORM_DATA>
    '''

