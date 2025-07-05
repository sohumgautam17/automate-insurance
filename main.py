import enum
import random
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


from gemini import query_gemini_async, query_gemini_for_answers, form_context_prompt
from extract_referral import referral_package_prompt
from extract_fields import extract_fields_with_positions
from fill_form import PDFFormFiller

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

async def process_page(client, page, PA_path, fields_by_page):
    prompt = form_context_prompt(fields_by_page[page])
    # print(prompt)
    result = await query_gemini_async(client, PA_path, prompt)
    return page, result

async def extract_fields(PA_path):
    gemini_client = genai.Client(api_key=api_key)

    field_forms_with_content = {}

    fields_by_page = extract_fields_with_positions("Input Data/Adbulla/PA.pdf")

    tasks = [process_page(gemini_client, page, PA_path, fields_by_page) for page in 
             extract_fields_with_positions("Input Data/Adbulla/PA.pdf")]

    results = await asyncio.gather(*tasks)

    for page, result in results: 
        field_forms_with_content[page] = result

    with open("output.json", 'w') as f:
        json.dump(field_forms_with_content, f, indent=2)

    return field_forms_with_content

async def extract_referral(field_forms_with_content, referral_path, retry=3):
    gemini_client = genai.Client(api_key=api_key)

    all_answers = []
    
    for page_num in sorted(field_forms_with_content.keys(), key=int):
        print(f"Processing Page : {page_num}")

        page_response = field_forms_with_content[page_num]
    
        prompt = referral_package_prompt(page_response)
        
        for attempt in range(retry):
            try:
                response = await query_gemini_for_answers(gemini_client, referral_path, prompt)
                print(response)
                if response:
                    try:
                        # Parse the JSON string from the response
                        parsed_response = json.loads(response)
                        all_answers.extend(parsed_response)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON: {e}")
                        print(f"Response was: {response}")
                    break
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                if attempt < retry -1:
                    if "503" in str(e) or "overloaded" in str(e).lower():
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print("Server is overloaded. Retrying in ")
                        await asyncio.sleep(wait_time)
                    else: 
                        break
                else:
                    print("Max attempts reached")

    with open("answers.json", 'w') as f:
        json.dump(all_answers, f, indent=2)

    return None

if __name__ == "__main__":
    PA_path = "Input Data/Akshay/PA.pdf"
    referral_path = "Input Data/Akshay/referral_package.pdf"
    start = time.time()
    field_forms_with_content = asyncio.run(extract_fields(PA_path))
    end = time.time()
    print(f'Processing time was: {end-start}s')

    # print(field_forms_with_content)
    asyncio.run(extract_referral(field_forms_with_content, referral_path))

    filler = PDFFormFiller("Input Data/Akshay/PA.pdf")
    success = filler.fill_form("Input Data/Akshay/filled_pa_form.pdf")
    


    

