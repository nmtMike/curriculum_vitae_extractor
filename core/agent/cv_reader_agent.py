import json
import logging
from core.base.base_agent import BaseAgent
from core.client.pdf_reader import PDF_Reader
from core.base.base_prompt import BasePrompt

class InformationExtractPrompt(BasePrompt):
    """Prompt to extract information from text"""
    template_path = 'information_extraction.tmpl'

class CV_Reader_Agent(BaseAgent):
    
    def parse_into_json(self, llm_response:str, separator:str='```JSON'):
        if not (len(llm_response.split(separator)) > 1):
            separator = separator.lower()
        if separator in llm_response and len(llm_response.split(separator)) > 1:
            llm_response = llm_response.split(separator)[1]
        json_data = llm_response.split('```')[0]
            
        return json.loads(json_data)
    
    def get_information_extraction_from_llm(self, prompt):
        logging.info(f'Using Prompt:\n{prompt}')
        llm_response = self.llm.chat_completion(prompt)
        json_data = self.parse_into_json(llm_response)
        logging.info(f'CV JSON Data: \n{json_data}')
        return json_data
    
    def get_information_from_CV(self, filepath):
        cv_content = PDF_Reader.extract_text_from_pdf(filepath)
        prompt = InformationExtractPrompt(cv_content=cv_content).to_string()
        json_data = self.get_information_extraction_from_llm(prompt)
        return json_data