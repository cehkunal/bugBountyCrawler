import sqlite3
from selenium import webdriver
import time
import bs4
import requests
import sys

prog_h1 = []
prog_bc = []

def fetchProgramsFromDB():
    #Fetch and Parse data from Database
    conn = sqlite3.connect('bugBounty.db')
    cur = conn.execute('''Select * from Programs where prog_source="HackerOne";''')
    for a in cur:
        data = list(a)
        prog_h1.append(str(data[0]))
    cur = conn.execute('''Select * from Programs where prog_source="BugCrowd";''')
    for a in cur:
        data = list(a)
        prog_bc.append(str(data[0]))
    conn.close()


def createWebDriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors. 
    driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options,service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])
    return driver

def closeWebDriver(driver):
    driver.close()
    driver.quit()


#Scrape HackerOne URL's
def scapeHackerOneProgramInScope(driver, progName):

    driver.get('https://hackerone.com/'+ progName) 
    time.sleep(10)
    
    SCROLL_PAUSE_TIME =4 
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        #Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #Wait to Load page
        time.sleep(SCROLL_PAUSE_TIME)
        #Calculate new Scroll Height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    
    ele=driver.execute_script('return document.body.innerHTML')
    root=bs4.BeautifulSoup(ele,"lxml")
    #programs = root.find_all('tr',{'class':'spec-directory-entry daisy-table__row fade fade--show'})    
    assets = root.find_all('tr', {'class':'spec-asset'})
    for a in assets:
        print str(a.find_all('strong')[0]).split(">")[1].split("<")[0]



driver = createWebDriver()
scapeHackerOneProgramInScope( driver  , sys.argv[1] )
closeWebDriver(driver)
