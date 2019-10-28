#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import selenium
import csv
import json
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


# Website URL #
url = "https://nvd.nist.gov/vuln/search"

# Execption class #
class NoResult(Exception): pass

# Class that represent a CVE vulnerability #
class CVE:

    def __init__(self, ID, Description, Impact, References, CWE):
        self.ID = ID
        self.Description = Description
        self.Impact = Impact
        self.References = References
        self.CWE = CWE

    def print_CVE(self):
        print(self.ID + " - " + self.Impact + "\n" + self.Description + "\n" + self.CWE + "\n" + self.References)


# Class that represent a list of CVEs
class CVE_list:   

    def __init__(self):
        self.CVEs = []
        
    def add_CVE(self, CVE):
        self.CVEs.append(CVE)

    def to_CSV(self):
        f = csv.writer(open('vuln_list.csv', 'w'))
        f.writerow(['ID', 'Description', 'Impact', 'References', 'CWE'])

        for cve in self.CVEs:
            f.writerow([cve.ID, cve.Description, cve.Impact,   cve.References, cve.CWE])

    def to_JSON(self):
        data = {}
        data['CVEs'] = []

        for cve in self.CVEs:
            data['CVEs'].append({
                'ID': cve.ID,
                'Description': cve.Description,
                'Impact': cve.Impact,
                'References': cve.References,
                'CWE': cve.CWE
            })

        with open('vuln_list.json', 'w') as outfile:
            json.dump(data, outfile, indent=2, separators=(',', ': '))

    def print_CVEs(self):
        for cve in self.CVEs:
            cve.print_CVE()


### Functions ###

# Function that open the search page on the nist website and ask the user to inser the keyword (default value: medical devices)
def open_NIST(browser):
    try:
        browser.set_window_size(900, 900)
        browser.get(url)

        search_box = browser.find_element_by_id('Keywords')

        keyword = input("Enter keywords: ")
        if len(keyword) == 0:
            keyword = "medical devices"
            
        search_box.send_keys(keyword)
        search_button = browser.find_element_by_id('vuln-search-submit')
        return search_button.click()
     
    except Exception as e:
        print (e, 'Error while browsing the NIST website')

# Function that checks the result page 
def open_CVE(browser):

    body = browser.find_element_by_id('body-section')
    content = body.find_element_by_id('page-content')
    data = content.find_element_by_id('row')

    links = data.find_elements_by_partial_link_text("CVE-20")

    try:
        if len(links) == 0:
            raise NoResult

        for link in links:
            href = link.get_attribute("href")
            new_window(href)

    except NoResult:
        print("There is no result for the given keyword/s! \n")

# Function that open each CVE in the result page in a new window in order to get all the detail about
def new_window(url):
    tab = webdriver.Firefox()
    tab.set_window_size(900, 900)
    tab.get(url)
    
    ### Wait Page Loading ###
    time.sleep(3) # for slow connection, add more time

    try:
        element = WebDriverWait(tab, 3).until(EC.presence_of_element_located((By.ID, 'body-section')))
        scrape_data(tab)
        
    except TimeoutException:
        print("Webpage loading took too much time!")
        
    finally:
        tab.quit()


# Function that scrape a CVE webpage and write all the data into a CSV file
def scrape_data(webpage):
    soup = BeautifulSoup(webpage.page_source, 'lxml')
    page = soup.find("div", class_="container")
    content = soup.find(id="page-content")

    # Check if the page is available #
    if  page is None:
        print("The current CVE webpage is unavailable!")
        return

    ### CVE ID
    h2_tag = content.find("h2")
    name = h2_tag.get_text().replace(' Detail', '').strip()

    ### Description
    description = content.find("p").get_text().strip()


    ### Impact
    div_impact = content.find("div", class_="row bs-callout bs-callout-success")
    if div_impact is None: 
        impact = "-"
    else:
        impact = div_impact.find("a").get_text().strip()

    ### References
    ref_table = content.find("table", class_="table table-striped table-condensed table-bordered detail-table")
    if ref_table is None: 
        references = "None"
    else:
        ref_rows = ref_table.find_all("td")
        references = ''
        for i in range(len(ref_rows)):
            if(i%2 == 0):
                references += ref_rows[i].get_text() + "\n"

    ### CWE
    div_cwe = content.find("div", class_="technicalDetails")
    if div_cwe is None or div_cwe.find("li") is None:
        cwe = "-"
    else:
        cwe = div_cwe.find("li").get_text().strip()

    cve = CVE(name, description, impact, references, cwe)
    list_cve.add_CVE(cve)


### Main ###

if __name__ == '__main__':

    browser = webdriver.Firefox()

    open_NIST(browser)

    list_cve = CVE_list()

    open_CVE(browser)

    browser.quit()

# Create the files #
    list_cve.to_JSON()
    #list_cve.to_CSV()


### FINISH ###
    print("\n Your file has just been successfully created! :)")







