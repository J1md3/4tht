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
    """
    Reads a file and returns a list of non-empty lines.

    Parameters:
    filename (str): The path to the file to be read.

    Returns:
    list: A list of non-empty lines from the file. 
          Returns an empty list if the file is not found or is empty.

    Logs an error message if the file is not found.
    """
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"{Fore.RED}Error: File {filename} not found{Style.RESET_ALL}")
        return []

def process_external_urls(driver, urls, keywords, extracted_tender_numbers, tender_terms):
    """
    Process external URLs by opening each one in a new tab and extracting keywords
    and tender numbers from the body of the page.

    Parameters:
    driver (selenium.webdriver.Chrome): A Chrome driver instance.
    urls (list): A list of URLs to process.
    keywords (list): A list of keywords to search in the body of the page.
    extracted_tender_numbers (set): A set of tender numbers that have already been extracted.
    tender_terms (list): A list of tender terms to search in the page titles.

    Returns:
    None

    Logs information messages for each URL that is processed, including the URL and
    the number of matches found. If a URL is skipped because of a weak match, an error
    message is logged. If an unexpected error occurs, an error message is logged with
    the error message.

    This function assumes that the Chrome driver is set up to run in headless mode.
    """
    
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
                    lower_case_body_text = body_elements.text.lower()
                    
                    matches = identify_matches_from_keywords(keywords = keywords, body_text = lower_case_body_text) 
                    
                    number_of_matches = len(matches)
                    if number_of_matches >= 2:
                        tender_numbers_found = TENDER_NUMBER_REGEX.findall(lower_case_body_text)
                        unique_tns = set(tender_numbers_found)
                        extracted_tender_numbers.update(unique_tns)
                        
                        logging.info(f"{Fore.GREEN}🔥 Strong match at {Fore.BLUE}{href}{Style.RESET_ALL}")
                        logging.info(f"{Fore.LIGHTMAGENTA_EX}📌 Matched keywords: {Fore.LIGHTCYAN_EX}{', '.join(matches)}{Style.RESET_ALL}")
                        if unique_tns:
                            logging.info(f"{Fore.LIGHTGREEN_EX}🔖 Found tender numbers: {Fore.LIGHTYELLOW_EX}{', '.join(unique_tns)}{Style.RESET_ALL}")        
                    else:
                        logging.info(f"⚠️ Weak match at {href}")
                except Exception as e:
                    logging.error(f"Unexpected error: {str(e)}")
                finally:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])                    
        except Exception as e:
            logging.error(f"{Fore.RED}⚠️ Error processing {url}: {str(e)}{Style.RESET_ALL}")

def identify_matches_from_keywords(keywords, body_text):
    """
    Identify matches from given keywords in the body text.
    
    Parameters:
    keywords (list): List of keywords to search in the body text.
    body_text (str): The text to search keywords in.
    
    Returns:
    list: A list of matched keywords.
    """
    matched_keywords = []
    for keyword in keywords:
        if all(word in body_text for word in keyword.lower().split()):
            matched_keywords.append(keyword)
    return matched_keywords

def open_link_in_new_tab(driver, link):
    """
    Opens a link in a new tab and switches to the new tab.
    
    Parameters:
    driver (selenium.webdriver.Chrome): A Chrome driver instance.
    link (selenium.webdriver.remote.webelement.WebElement): The link to open in a new tab.
    
    Returns:
    str: The href of the link that was opened in a new tab.
    """
    href = link.get_attribute('href')
    driver.execute_script(f"window.open('{href}');")
    driver.switch_to.window(driver.window_handles[1])
    return href

def find_tender_links(driver, tender_terms, url):
    
    """
    Finds all links on a given page that contain any of the given tender terms.

    Parameters:
    driver (selenium.webdriver.Chrome): A Chrome driver instance.
    tender_terms (list): A list of tender terms to search for in the page content.
    url (str): The URL of the page to search.

    Returns:
    list: A list of selenium.webdriver.remote.webelement.WebElement objects representing the links found.
    """
    driver.get(url)
            
    links = driver.find_elements(By.XPATH, "|".join(
                 [f"//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{term}')]" 
                for term in tender_terms]
            ))
    
    return links

def main(headless=False):
    
    """
    Main entry point for the script.

    Parameters:
    headless (bool): Whether to run the Chrome driver in headless mode (default: False).

    Returns:
    None

    Reads the list of URLs from file2.txt and the list of keywords from file3.txt.
    Extracts tender numbers from the pages matching the given keywords and
    writes them to extracted_tender_numbers.txt.

    Logs information messages for each URL that is processed, including the URL
    and the number of matches found. If a URL is skipped because of a weak match,
    an error message is logged. If an unexpected error occurs, an error message
    is logged with the error message.

    :return: None
    """
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
