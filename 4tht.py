from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import time
import re
from colorama import Fore, Style, init
import argparse

# Initialize colorama
init(autoreset=True)

# Configuration
DRIVER_PATH = '/usr/bin/chromedriver'
BASE_TENDERS_URL = 'https://tenders.go.ke/tenders'
BASE_ENTITIES_URL = 'https://tenders.go.ke/procuringentities'
TENDER_NUMBER_REGEX = re.compile(r'\b(?:[A-Za-z]{2,}[-/]?\d+[-/]?\d*[A-Za-z]*)\b', re.IGNORECASE)

FILES = {
    'urls': 'file2.txt',
    'keywords': 'file3.txt',
    'extracted_tenders': 'extracted_tender_numbers.txt'
}

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File {filename} not found{Style.RESET_ALL}")
        return []

def setup_driver(headless=False):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    service = Service('/usr/bin/chromedriver')
    return webdriver.Chrome(service=service, options=options)

def contains_phrase(text, phrase):
    return all(word in text for word in phrase.split())

def process_external_urls(driver, urls, keywords, extracted_tender_numbers):
    print(f"\n{Fore.CYAN}=== Processing External URLs ==={Style.RESET_ALL}")
    tender_terms = ['tender', 'bid', 'rfp', 'proposal']
    
    for url in urls:
        try:
            driver.get(url)
            links = driver.find_elements(By.XPATH, "|".join(
                [f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{term}')]" 
                 for term in tender_terms]
            ))
            
            for link in links:
                href = link.get_attribute('href')
                driver.execute_script(f"window.open('{href}');")
                driver.switch_to.window(driver.window_handles[1])
                
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )
                    body_text = driver.find_element(By.TAG_NAME, 'body').text.upper()
                    
                    matches = [phrase for phrase in keywords if contains_phrase(body_text.lower(), phrase.lower())]
                    if len(matches) >= 2:
                        tender_numbers_found = TENDER_NUMBER_REGEX.findall(body_text)
                        unique_tns = set(tender_numbers_found)
                        extracted_tender_numbers.update(unique_tns)
                        
                        print(f"{Fore.GREEN}🔥 Strong match at {Fore.BLUE}{href}{Style.RESET_ALL}")
                        print(f"{Fore.LIGHTMAGENTA_EX}📌 Matched keywords: {Fore.LIGHTCYAN_EX}{', '.join(matches)}{Style.RESET_ALL}")
                        if unique_tns:
                            print(f"{Fore.LIGHTGREEN_EX}🔖 Found tender numbers: {Fore.LIGHTYELLOW_EX}{', '.join(unique_tns)}{Style.RESET_ALL}")
                    
                finally:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
        except Exception as e:
            print(f"{Fore.RED}⚠️ Error processing {url}: {str(e)}{Style.RESET_ALL}")

def main(headless=False):
    urls = read_file(FILES['urls'])
    keywords = read_file(FILES['keywords'])
    
    extracted_tender_numbers = set()
    
    driver = setup_driver(headless)
    try:
        if urls and keywords:
            process_external_urls(driver, urls, keywords, extracted_tender_numbers)
        
        if extracted_tender_numbers:
            with open(FILES['extracted_tenders'], 'w') as f:
                for tn in sorted(extracted_tender_numbers):
                    f.write(f"{tn}\n")
            print(f"\n{Fore.LIGHTGREEN_EX}🎉 Extracted {len(extracted_tender_numbers)} tender numbers to {Fore.LIGHTYELLOW_EX}{FILES['extracted_tenders']}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}😞 No new tender numbers extracted.{Style.RESET_ALL}")
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract tender numbers from websites.")
    parser.add_argument('--headless', action='store_true', help="Run in headless mode")
    args = parser.parse_args()
    
    main(headless=args.headless)
