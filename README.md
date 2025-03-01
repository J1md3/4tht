## An automated Tender Hunting Tool
4tht v4.0
A python tool that lets both organistions and individuals hunt for tenders relevant to them from a wide range of websites with just a click of a button!

## Features
- Customisable key words to look for in tenders
- Dynamic combination of keywords to minimise false positives
- Customisable list of URLs you wish to scrape for tenders
- Detailed & colorful output
- Headless mode

## Requirements
- Python3
  - Required Dependenciies
      - selenium
      - Colorama
      - re
      - argparse
      
- Google chrome
- Chromedriver (preffarably stored in /usr/bin)
- Input Files:
    - file2.txt: Contains a list of URLs to scan.
    - file3.txt: Contains a list of keywords to search for in the page content.
- Output file:
    - extracted_tender_numbers.txt
      
  ## ✨ Usage: ✨
    Run the script in the terminal:

      python 4tht.py

    To run in headless mode:
    
      python script_name.py --headless

  ## Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request with your changes.

## Acknowledgments

Made with ❤️ by j1md3!
