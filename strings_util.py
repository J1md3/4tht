import re

# Configuration
BASE_TENDERS_URL = 'https://tenders.go.ke/tenders'
BASE_ENTITIES_URL = 'https://tenders.go.ke/procuringentities'
TENDER_NUMBER_REGEX = re.compile(r'\b(?:[A-Za-z]{2,}[-/]?\d+[-/]?\d*[A-Za-z]*)\b', re.IGNORECASE)

URL_KEY = 'urls'
KEYWORD_KEY = 'keywords'
EXTRACTED_TENDERS = 'extracted_tenders'

FILES = {
    URL_KEY: 'file2.txt',
    KEYWORD_KEY: 'file3.txt',
    EXTRACTED_TENDERS: 'extracted_tender_numbers.txt'
}

