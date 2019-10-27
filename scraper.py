#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import selenium
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from time import sleep

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

    def write_CVE(self):
        f.writerow([self.ID, self.Description, self.Impact, self.References, self.CWE])

    def print_CVE(self):
        print(self.ID + " - " + self.Impact + "\n" + self.Description + "\n" + self.CWE + "\n" + self.References)


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
    scrape_data(tab)
    tab.quit()

# Function that scrape a CVE webpage and write all the data into a CSV file
def scrape_data(webpage):
    soup = BeautifulSoup(webpage.page_source, 'lxml')
    page = soup.find("div", class_="container")
    content = soup.find(id="page-content")

    ### WAIT FOR WEBPAGE LOADING ###
    time.sleep(2) # if your connection is slow, add more time

    # Check if the page is loaded correctly
    if  page is None:
        print("The current CVE webpage is unavailable!")
        return

    ### CVE ID
    h2_tag = content.find("h2")
    name = h2_tag.get_text().replace(' Detail', '')

    ### Description
    description = content.find("p").get_text()


    ### Impact
    div_impact = content.find("div", class_="row bs-callout bs-callout-success")
    if div_impact is None: 
        impact = "-"
    else:
        impact = div_impact.find("a").get_text()

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
        cwe = div_cwe.find("li").get_text()

    cve = CVE(name, description, impact, references, cwe)
    cve.write_CVE()


### Main ###

if __name__ == '__main__':

    browser = webdriver.Firefox()

### Browse the website in order to display the CVE list ####
    open_NIST(browser)

### Create the CSV file to save the results
    f = csv.writer(open('vuln_list.csv', 'w'))
    f.writerow(['ID', 'Description', 'Impact', 'References', 'CWE'])

### Browse the webpage of each CVE ###
    open_CVE(browser)
    browser.quit()

### FINISH ###
    print("\n Your CSV has just been successfully created! :)")







