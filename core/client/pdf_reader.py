import PyPDF2
import pytesseract
import re
from pdf2image import convert_from_path
import pytesseract
import logging

class PDF_Reader:
    
    @classmethod
    def is_digital_pdf(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pages = len(reader.pages)
                for page in range(pages):
                    page = reader.pages[page]
                    text = page.extract_text()
                    if text:
                        if re.search(r'[a-zA-Z0-9]', text):
                            return True
                    else:
                        return False
        except Exception as e:
            logging.error(e)
            return None
    
    @classmethod
    def ocr(self, filepath):
        pages = convert_from_path(filepath)
        extracted_text = []
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page)
            extracted_text.append(text)
        
        full_text = "\n".join(extracted_text)
        return full_text
    
    @classmethod
    def read_digital_pdf(self, filepath):
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pages = len(reader.pages)
            extracted_text = []
            
            for page in range(pages):
                page = reader.pages[page]
                text = page.extract_text()
                extracted_text.append(text)
            
            full_text = "\n".join(extracted_text)
        return full_text
    
    @classmethod
    def extract_text_from_pdf(self, filepath):
        if self.is_digital_pdf(filepath):
            full_text =  self.read_digital_pdf(filepath)
        else:
            full_text =  self.ocr(filepath)
        
        logging.info(f'text extracted from pdf: \n\n{full_text}')
        return full_text
