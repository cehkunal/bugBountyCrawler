from selenium import webdriver
import bs4
import time
import cPickle
import requests
import sqlite3

progDir = list()
progDirBugCrowd = list()
def get_token(fname):
    with open(fname,'r') as f:
        data=f.read().strip().split(',')
    f.close()
    return data
tk=get_token('/etc/mytk')
TOKEN=tk[0]
CHAT_ID2=tk[1]
URL="https://api.telegram.org/bot"+TOKEN+"/sendMessage"

def send_tele(CHAT_ID,MESSAGE):
        resp = requests.post(URL,data={'chat_id':CHAT_ID,'text':MESSAGE})

def syncToDatabase():
	conn = sqlite3.connect('bugBounty.db')
	conn.execute('''CREATE TABLE IF NOT EXISTS PROGRAMS(
	        PROG_NAME TEXT NOT NULL PRIMARY KEY,
	        PROG_LAUNCH_DATE TEXT,
	        PROG_MIN_BOUNTY TEXT,
	        PROG_SOURCE TEXT,
        	PROG_IN_SCOPE TEXT
        	);
	''')


	#Synch Bugcrowd Programs
	with open('program_bugcrowd') as f:
	    data = cPickle.load(f)
	f.close()
	for p in data:
	    conn.execute('''REPLACE INTO PROGRAMS (PROG_NAME, PROG_LAUNCH_DATE, PROG_MIN_BOUNTY, PROG_SOURCE) VALUES(?,?,?,?);''', (p,'','','BugCrowd'))

	#Sync Hackerone Programs
	with open('program_h1') as f:
	    data = cPickle.load(f)
	f.close()
	#Parse Data
	for p in data:
	    name = p['progName']
	    ldate = p['progLaunchDate']
	    minb = p['progMinBounty']
	    conn.execute('''REPLACE INTO PROGRAMS (PROG_NAME, PROG_LAUNCH_DATE, PROG_MIN_BOUNTY, PROG_SOURCE) VALUES(?,?,?,?);''', (name,ldate,minb,'HackerOne'))
        conn.commit()
	#cur = conn.execute('SELECT * FROM PROGRAMS;')
	#for a in cur:
	#    print str(a)


def notifyNewPrograms():
    h1diff = checkh1difference()
    bcdiff = checkbugcrowddifference()
    #if len(h1diff) > 0:
        #sendsms(['8010533210','8770766532','8660477425'],",".join(list(h1diff)),'Hackerone')    
    #if len(bcdiff) > 0:
        #sendsms(['8010533210','8770766532','8660477425'],",".join(list(bcdiff)),'Bugcrowd')
    hck="\n".join(list(h1diff))
    bug = "\n".join(list(bcdiff))
    msg1="HackerAlert-->"+hck
    msg2="BugAlert-->"+bug
    if(hck!=""):
        send_tele(CHAT_ID2,msg1)
        #print "from hck1"
    if(bug!=""):
        send_tele(CHAT_ID2,msg2)
        #print "from bug"
    if(hck=="" and bug==""):

        send_tele(CHAT_ID2,"Kuch ni Aaya Abtk to..")


def checkh1difference():
    tmpProg1 = []
    tmpProg2 = []
    h1Progs = dump_load('program_h1')
    for prog in h1Progs:
        tmpProg1.append(prog['progName'])
    for prog in progDir:
        tmpProg2.append(prog['progName'])
    diff = set(tmpProg2) - set(tmpProg1)
    return diff

def checkbugcrowddifference():
    bugcrowdPrograms_old = dump_load('program_bugcrowd')
    bugcrowdprograms_new = progDirBugCrowd
    diff = set(bugcrowdprograms_new) - set(bugcrowdPrograms_old)
    return diff


def getsmstoken():
    with open('/etc/fast2sms','rb') as f:
        data = f.readlines()
        apiStr = data[2]
        apiToken = str(apiStr).split(":")[1].strip()
        return apiToken

def sendsms(to, data , source):
    #to is a LIST of recipents
    msg = "New Programs Found in " + source + ":" + data
    #print "\033[1;30mSending Alerts\033[1;m" + msg
    rcpt = ",".join(to)
    token = getsmstoken()
    url = 'https://www.fast2sms.com/dev/bulk'
    payload = 'sender_id=FSTSMS&message=' + msg + '&language=english&route=p&numbers=' + rcpt
    headers = { 'authorization':token, 'Content-Type':'application/x-www-form-urlencoded', 'Cache-Control':'no-cache', }
    response = requests.request('POST', url, data=payload, headers=headers)
    #print response

def driver_stop(driver):
    driver.close()
    driver.quit()

def dump_dump(filename,x):
    with open(filename,'wb') as f:
        cPickle.dump(x,f)
    f.close()

def dump_load(filename):
    with open(filename,'rb') as f:
        data=cPickle.load(f)
    f.close()
    return data

#def printHackeronePrograms(programList):
    #for i in programList:
    	#print "\033[1;32mProgram Name:\033[1;m" + "\033[1;33m" + i['progName'] +"\033[1;m" + "                  "  + "\033[1;35m" +i['progLaunchDate'] + "\033[1;m" +  "                 " + "\033[1;36m" +i['progMinBounty'] + "\033[1;m"

#def printBugCrowdPrograms():
	#for i in progDirBugCrowd:
		#print "\033[1;31mBugcrowd: "+"\033[1;m" + "\033[1;33m"  + i + "\033[1;m"

def crawlHackerone(driver):
    driver.get('https://hackerone.com/directory?order_direction=DESC') 
    time.sleep(10)
    
    SCROLL_PAUSE_TIME =10 
    
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
    programs = root.find_all('tr',{'class':'spec-directory-entry daisy-table__row fade fade--show'})    
    for p in programs:
	program = {}
	tableDataTags = p.find_all('td')
	progName = str(p.find_all('a',{'class':'daisy-link spec-profile-name'})).split(">")[1].split("<")[0]
	progLaunchDate = str(tableDataTags[1]).split(">")[2].split("<")[0]
	progMinBounty = str(tableDataTags[4]).split("$")
	if len(progMinBounty) == 1:
		progMinBounty="No Bounty"
	else:
		progMinBounty="$" + str(progMinBounty[1].split("<")[0])
	#Set Dict
	program['progName'] = progName
	program['progLaunchDate'] = progLaunchDate
	program['progMinBounty'] = progMinBounty
	progDir.append(program)
	program = {}




#Crawl BugCrowd
def crawlBugCrowd(driver):
    driver.get('https://bugcrowd.com/programs') 
    time.sleep(10)
    #Scroll Page By Clicking Load More
    for i in range(10):
    	button=driver.find_elements_by_xpath("//button[@class='rp-program-list__load-more__btn bc-btn bc-btn--small bc-btn--text']")
	if len(button) < 1:
		break
	button[0].click()
	time.sleep(5)
    
    ele=driver.execute_script('return document.body.innerHTML')
    root=bs4.BeautifulSoup(ele,"lxml")
    allProgramCards = root.find_all('li',{'class':'col-xs-12 col-sm-6 col-md-4 col-lg-3 col-xl-2 bc-program-card'})
    for prog in allProgramCards:
	progName = str(prog.find_all('h4',{'class':'bc-panel__title'})).split(">")[2].split("<")[0]
	progDirBugCrowd.append(progName)
	



# Option 1 - with ChromeOptions
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-application-cache')
chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors. 
driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options,service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])

crawlHackerone(driver)
#printHackeronePrograms(progDir)

crawlBugCrowd(driver)
#printBugCrowdPrograms()

#Check Difference before dumping
notifyNewPrograms()

dump_dump('program_h1',progDir)
dump_dump('program_bugcrowd',progDirBugCrowd)

driver_stop(driver)
#print "\033[1;39mSaving Results in bugBounty.db\033[1;m"
syncToDatabase()
