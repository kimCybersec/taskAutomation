import os
import shutil
import pathlib
import requests
import glob
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def moveFiles(src, dst, pattern):
    os.makedirs(src, exist_ok=True)
    for file in glob.glob(os.path.join(src, pattern)):
        shutil.move(file, os.path.join(dst, os.path.basename(file)))
        print(f"moved: {file} > {dst}")
        
def scrapeTitles(url, selector, outputFile):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.selector(selector)
    with open(outputFile, "w", encoding="utf-8") as f:
        for el in elements:
            f.write(el.get_text(strip=True) + "\n")
    
    print(f"Scraped {len(elements)} item to {outputFile}")
    
def formAutomation(url, fieldData):
    options = Options()
    options.add_argument("__headless")
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(url)
    
    for selector, value in fieldData.items():
        inputElement = driver.find_element(By.CSS_SELECTOR, selector)
        inputElement.send_keys(value)
        
    submitBtn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submitBtn.click()
    print("Form submitted.")
    driver.quit()
    

def main():
    parser = argparse.ArgumentParser(description="Automation Toolkit")
    subparsers = parser.add_subparsers(dest="commands")
    
    fmParser = subparsers.add_parser("move files")
    fmParser.add_argument("--src", required=True, help="Source directory")
    fmParser.add_argument("--dst", required=True, help="Destination directory")
    fmParser.add_argument("--pattern", required=True, default="*.pdf",  help="File pattrn to move")
    
    scParser = subparsers.add_parser("scrape")
    scParser.add_argument("--url", required=True, help="Url to scrape")
    scParser.add_argument("--selector", required=True, help="CSS selector")
    scParser.add_argument("-o", required=True, help="Output file")
    
    formParser = subparsers.add_parser("fill form")
    formParser.add_argument("--url", required=True, help="Form URL")
    formParser.add_argument("--field", nargs='+', help="Field input pairs as selector=value")
    
    args = parser.parse_args()
    
    if args.command == "move files":
        moveFiles(args.src, args.dst, args.pattern)
    elif args.command == "scrape":
        scrapeTitles(args.url, args.selector, args.o)
    elif args.command == ("fill form"):
        fieldData = dict(pair.split("=", 1) for pair in args.field)
        formAutomation(args.url, fieldData)
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()