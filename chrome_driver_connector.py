from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def setup_driver():   
    options = get_default_chrome_options()
    try:
        driver = webdriver.Chrome(options = options)            
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize Chrome driver: {str(e)}")
        raise RuntimeError("Chrome driver initialization failed from")

def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    ## commented for debugging. This should be uncommented for production.
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    return options