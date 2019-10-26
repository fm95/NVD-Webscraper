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

url = "https://nvd.nist.gov/vuln/search"

cookies = {
    'has_js': '1',
    'cc_cookie_accept': 'cc_cookie_accept',
}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en,it-IT;q=0.9,it;q=0.8,en-US;q=0.7',
    'If-None-Match': '"1565272073-1"',
    'If-Modified-Since': 'Thu, 26 Oct 2019 16:47:53 GMT',
}

class NoResult(Exception): pass

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


def new_window(url):
    tab = webdriver.Firefox()
    tab.set_window_size(900, 900)
    tab.get(url)

    ### EXCEPTION ### go haed

    scrape_data(tab)
    tab.quit()


def scrape_data(webpage):
    soup = BeautifulSoup(webpage.page_source, 'lxml')
    content = soup.find(id="page-content")

    ### CVE ID
    h2_tag = content.find("h2")
    name = h2_tag.get_text().replace(' Detail', '')

    ### Description
    description = content.find("p").get_text()

    ### Impact
    div_impact = content.find("div", class_="row bs-callout bs-callout-success")
    impact = div_impact.find("a").get_text()

    ### References
    ref_table = content.find("table", class_="table table-striped table-condensed table-bordered detail-table")
    ref_rows = ref_table.find_all("td")
    references = ''
    for i in range(len(ref_rows)):
        if(i%2 == 0):
            references += ref_rows[i].get_text() + "\n"

    ### CWE
    div_cwe = content.find("div", class_="technicalDetails")
    cwe = div_cwe.find("li").get_text()

    cve = CVE(name, description, impact, references, cwe)
    cve.write_CVE()

    #f.writerow([name, description, impact, references, cwe])


#################

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







