from chrome_driver_connector import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from colorama import Fore, Style, init
import argparse
import logging
from strings_util import *

# Initialize colorama
init(autoreset=True)

def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"{Fore.RED}Error: File {filename} not found{Style.RESET_ALL}")
        return []

def process_external_urls(driver, urls, keywords, extracted_tender_numbers, tender_terms):
    logging.info(f"\n{Fore.CYAN}=== Processing External URLs ==={Style.RESET_ALL}")
        
    for url in urls:
        try:
            links = find_tender_links(driver, tender_terms, url)
            
            for link in links:
                href = open_link_in_new_tab(driver, link)
                
                try:
                    body_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )
                    body_text = body_elements.find_element(By.TAG_NAME, 'body').text.lower()
                    
                    matches = [
                        phrase for phrase in keywords 
                        if all(word in body_text.lower() for word in phrase.lower().split())
                        ] 
                    
                    if len(matches) >= 2:
                        tender_numbers_found = TENDER_NUMBER_REGEX.findall(body_text)
                        unique_tns = set(tender_numbers_found)
                        extracted_tender_numbers.update(unique_tns)
                        
                        logging.info(f"{Fore.GREEN}🔥 Strong match at {Fore.BLUE}{href}{Style.RESET_ALL}")
                        logging.info(f"{Fore.LIGHTMAGENTA_EX}📌 Matched keywords: {Fore.LIGHTCYAN_EX}{', '.join(matches)}{Style.RESET_ALL}")
                        if unique_tns:
                            logging.info(f"{Fore.LIGHTGREEN_EX}🔖 Found tender numbers: {Fore.LIGHTYELLOW_EX}{', '.join(unique_tns)}{Style.RESET_ALL}")                
                except Exception as e:
                    logging.error(f"Unexpected error: {str(e)}")
                finally:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])                    
        except Exception as e:
            logging.error(f"{Fore.RED}⚠️ Error processing {url}: {str(e)}{Style.RESET_ALL}")

def open_link_in_new_tab(driver, link):
    href = link.get_attribute('href')
    driver.execute_script(f"window.open('{href}');")
    driver.switch_to.window(driver.window_handles[1])
    return href

def find_tender_links(driver, tender_terms, url):
    driver.get(url)
            
    links = driver.find_elements(By.XPATH, "|".join(
                 [f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{term}')]" 
                for term in tender_terms]
            ))
    
    return links

def main(headless=False):
    urls = read_file(FILES[URL_KEY])
    keywords = read_file(FILES[KEYWORD_KEY])
    tender_terms = ['tender', 'bid', 'rfp', 'proposal']
    extracted_tender_numbers = set()
    
    driver = setup_driver()
    try:
        if urls and keywords:
            process_external_urls(driver, urls, keywords, extracted_tender_numbers, tender_terms = tender_terms)
        
        if extracted_tender_numbers:
            with open(FILES['extracted_tenders'], 'w') as f:
                for tn in sorted(extracted_tender_numbers):
                    f.write(f"{tn}\n")
            logging.info(f"\n{Fore.LIGHTGREEN_EX}🎉 Extracted {len(extracted_tender_numbers)} tender numbers to {Fore.LIGHTYELLOW_EX}{FILES['extracted_tenders']}{Style.RESET_ALL}")
        else:
            logging.warning(f"\n{Fore.YELLOW}😞 No new tender numbers extracted.{Style.RESET_ALL}")
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract tender numbers from websites.")
    parser.add_argument('--headless', action='store_true', help="Run in headless mode")
    args = parser.parse_args()
    
    main(headless=args.headless)
