import io
import os
import logging
import heapq
import fitz

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence import DocumentIntelligenceClient

logger = logging.getLogger("ragapp")

MIN_WORD_THRESHOLD = os.environ.get("MIN_WORD_THRESHOLD", 1)
DOCUMENT_INTELLIGENCE_KEY=os.environ.get("DOCUMENT_INTELLIGENCE_KEY")
DOCUMENT_INTELLIGENCE_ENDPOINT=os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_API_VERSION=os.environ.get("DOCUMENT_INTELLIGENCE_API_VERSION", "2024-02-29-preview")
api_version="2024-02-29-preview"

def table_to_markdown(table):
    markdown = ""
    # Extract headers
    headers = [cell.content for cell in table.cells if cell.row_index == 0]
    markdown += "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    # Extract rows
    for row_index in range(1, table.row_count):
        row = [cell.content for cell in table.cells if cell.row_index == row_index]
        markdown += "| " + " | ".join(row) + " |\n"
    return markdown

class PriorityQueue:
    def __init__(self):
        self._queue = []

    def push(self, priority, item):
        # Push an item with its priority into the queue
        # The priority queue uses a tuple where the first element is the priority
        # By using -priority, we can turn heapq into a max-heap instead of a min-heap
        heapq.heappush(self._queue, (priority, item))
        
    def is_empty(self):
        return len(self._queue) == 0

    def pop(self):
        # Pop the item with the highest priority
        return heapq.heappop(self._queue)[-1]

class AzDocumentIntelligenceClient:
    document_intelligence_client = None

    @classmethod
    def create_document_intelligence_client(cls,
            DOCUMENT_INTELLIGENCE_ENDPOINT=DOCUMENT_INTELLIGENCE_ENDPOINT, 
            DOCUMENT_INTELLIGENCE_KEY=DOCUMENT_INTELLIGENCE_KEY,
            DOCUMENT_INTELLIGENCE_API_VERSION=DOCUMENT_INTELLIGENCE_API_VERSION):
        if not cls.document_intelligence_client:
            cls.document_intelligence_client = DocumentIntelligenceClient(
                endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT, 
                credential=AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY), 
                api_version=DOCUMENT_INTELLIGENCE_API_VERSION
            )
        return cls.document_intelligence_client

def OCR_text_from_pdf(pdfBytes, pages):
    document_analysis_client = AzDocumentIntelligenceClient.create_document_intelligence_client()
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-layout", analyze_request=io.BufferedReader(pdfBytes), content_type="application/octet-stream", pages=pages
    )
    result: AnalyzeResult = poller.result()
    result_string = ""
    pq = PriorityQueue()

    for paragraph in result.paragraphs:
        content = paragraph.content
        check = False
        for table in result.tables:
            if any(content == cell.content for cell in table.cells):
                check = True
                break
        if not check and paragraph.role != 'pageNumber' and len(content.split(' ')) > MIN_WORD_THRESHOLD:
            pq.push(paragraph.spans[0].offset, content)
        
    for table in result.tables:
        table_string = table_to_markdown(table)
        pq.push(table.spans[0].offset, table_string)
        
    while not pq.is_empty():
        items = pq.pop()
        result_string += items + "\n"
    return result_string


def analyze_document(pdfBytes, file_type = 'pdf'):
    pdfBytes.seek(0)
    if file_type == 'docx':
        return OCR_text_from_pdf(pdfBytes, None)
    document = fitz.open(stream=pdfBytes, filetype="pdf")  
    num_pages = document.page_count  
    page = 1
    result_string = ""
    while page < num_pages:
        pages= f"{page}-{page+1999}"
        result_string += OCR_text_from_pdf(pdfBytes, pages)
        page += 2000
    
    return result_string