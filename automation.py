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
    
    parser.add_argument("--src", help="Source directory")
    parser.add_argument("--dst", help="Destination directory")
    parser.add_argument("--pattern", default="*.pdf",  help="File pattrn to move")
    
    parser.add_argument("--scrape", action="store_true", help="Url to scrape")
    parser.add_argument("--url", help="Url to scrape")
    parser.add_argument("--selector", help="CSS selector")
    parser.add_argument("-o", help="Output file")
    
    parser.add_argument("--form", action="store_true", help="Form URL")
    parser.add_argument("--field", nargs='+', help="Field input pairs as selector=value")
    
    args = parser.parse_args()
    
    if args.scrape:
        if args.url and args.selector and args.o:
            scrapeTitles(args.url, args.selector, args.o)
        else:
            print("Missing arguements: --url, --selector, --o")
            
    elif args.form:
        if args.url and args.fields:
            fieldData = dict(pair.split("=", 1) for pair in args.field)
            formAutomation(args.url, fieldData)
        else:
            print("Missing arguements: --url, --fields")
            
    elif args.src and args.dst:        
        moveFiles(args.src, args.dst, args.pattern)
           
    else:
        parser.print_help()
        
        
if __name__ == "__main__":
    main()