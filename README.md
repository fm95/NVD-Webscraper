# NVD-Webscraper

In brief, this python Webscraper allows you to insert as input a set of keyword (e.g. kind of devices, protocol, software, etc.) and based on these search into the NVD Vulnerability Database to find correlated vulnerabilities.
From the result that you get into the result-page, the program automatically download some key information about each CVE in CSV and JSON format.

Before running the script, we have to install the required software:
  • Python: https://www.python.org/downloads/

  • Install pip: depending on the OS
      sudo apt-get install python-pip
      sudo pacman -S python-pip
      Mac: sudo easy_install pip
      Windows: https://www.liquidweb.com/kb/install-pip-windows/
      
  • BeautifulSoup: pip install BeautifulSoup
  
  • Selenium: to use Selenium you need either Python version Python 2.6, 2.7, Python 3.3+. So
    before starting, be sure that your python --version is compatible, and then run:
      pip install selenium

  • My script uses only the Firefox browser, so it’s enough to download only the Firefox driver.
  On the link above there are detailed instruction also for Windows users, while for Linux
  user it’s enough to unzip the driver folder (zip or tar.gz) and move the driver to the /usr/bin
  folder.
https://selenium-python.readthedocs.io/installation.html#downloading-python-bindings-for-selenium

At this point you should be ready to execute the script!

---------------------------------------------

Brief explanation of the program flow

By using Selenium we are able to browse among all the links of the webpage we are interested in: after open the search page of the NIST website with Firefox, the script ask the user to insert his own keywords or to use the default value (“medical devices”) and after press enter it will navigate to the result page with the list of all the found CVEs.
At this point, for every link, the program opens a new browser window (in this way we are able to scrape more information than from the result page) of the current CVE and then call another function to scrape the information: indeed by using BeautifulSoup and HTML tag we can save all the relevant information for us, and then create a CVE object and add it to the CVE_list object, that basically it’s a list of CVEs.
Once we have scraped all the CVE’s link, we have an object (list_cve) that contains all the information about every CVE and we can call the respective function to save the information to a JSON or a CSV file, that it will be created in the same folder where the script is located.


Limitation

Currently this script scrape only the data from the links in the first result webpage. But this problem could be easily overtake by simply add a function and look the webpage url: in fact, wecan call the open_CVE function (that creates a list of all the CVE links on the current webpage) on every result page, and for every result-page simply “update” the url.
To understand this, we can look the link of the first result page:
https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&query=
sql+injection&search_type=all
Now, if the second page exists, the link will be:
https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&query=sql+inj
ection&search_type=all&startIndex=20

So, at the first iteration we can call the open_CVE function with the first result page url (e.g. saved on a variable called url); after that, we can recall the same function on the second result page by simply doing this before: url.append(&startIndex=20) and so on for the other pages (40, 60, etc.).


Improvements

  - Use Scrapy: faster and easier to configure and use ( https://scrapy.org/ );
  - Use a database to store the result (e.g. MySQL);
  - Allow the user to choose how many links scrape or let him choose the file format in which
    download the CVEs.



