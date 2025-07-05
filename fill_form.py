import fitz
import json
import os
from typing import Dict, List, Any, Optional

class PDFFormFiller:
    def __init__(self, pdf_path: str, answers_path: str = "answers.json"):
        self.pdf_path = pdf_path
        self.answers_path = answers_path
        self.doc = None
    
    def load_answers(self) -> Dict[str, str]:
        """Load answers and convert to simple field_name -> value mapping"""
        try:
            with open(self.answers_path, 'r') as f:
                data = json.load(f)
            
            answers = {}
            for field in data:
                field_name = field.get('name', '')
                answer = field.get('answer', '')
                if answer and answer != 'MISSING':
                    answers[field_name] = answer
            
            return answers

        except Exception as e:
            print(f"Error loading answers: {e}")
            return {}
    
    def fill_form(self, output_path: str = "filled_form.pdf"):
        answers = self.load_answers()
        if not answers:
            print("No answers loaded!")
            return False

        try:
            self.doc = fitz.open(self.pdf_path)
            print(f"Opened PDF: {self.pdf_path}")
            print(f"PDF has {len(self.doc)} pages")
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False

        try:
            filled_count = 0
            total_fields = 0

            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                widgets = list(page.widgets())
                print(f"\nPage {page_num + 1}: Found {len(widgets)} widgets")

                for widget in widgets:
                    total_fields += 1
                    field_name = widget.field_name
                    field_type = widget.field_type

                    print(f"  Field: '{field_name}' (type {field_type})")

                    # Only process text and checkbox fields
                    if field_type not in [1, 2, 7]:
                        print(f"    SKIPPED - not a fillable field")
                        continue

                    if field_name in answers:
                        value = answers[field_name]
                        success = self.fill_field(widget, value)
                        if success:
                            filled_count += 1
                            print(f"    ✓ FILLED: {value}")
                        else:
                            print(f"    ✗ FAILED to fill")
                        continue

                    print(f"    ✗ NO MATCH - field '{field_name}' not in answers")

            print(f"\n=== SUMMARY ===")
            print(f"Total widgets found: {total_fields}")
            print(f"Fields actually filled: {filled_count}")

            self.doc.save(output_path)
            print(f"Saved filled PDF: {output_path}")
            return True

        finally:
            self.doc.close()
    
    def fill_field(self, widget, value):
        try:
            if widget.field_type in [7]:  # Text fields
                widget.field_value = value
                print(f"      Set text field to: '{value}'")
            elif widget.field_type == 2:  # Checkbox
                if value.lower() in ['yes', 'true', 'checked', '1']:
                    widget.field_value = True
                    print(f"      Set checkbox to: True")
                else:
                    widget.field_value = False
                    print(f"      Set checkbox to: False")
            widget.update()
            return True
        except Exception as e:
            print(f"      ERROR filling field: {e}")
            return False

def main():
    filler = PDFFormFiller("Input Data/Adbulla/PA.pdf")
    success = filler.fill_form("filled_pa_form.pdf")
    
    if success:
        print("Form filling completed!")
    else:
        print("Form filling failed!")

if __name__ == "__main__":
    main()
