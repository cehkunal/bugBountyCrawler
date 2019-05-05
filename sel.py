from selenium import webdriver
import bs4
import time
import cPickle

progDir = list()

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
    for d in list(data):
	print str(d)
    f.close()

def printHackeronePrograms(programList):
    for i in programList:
    	print "\033[1;32mProgram Name:\033[1;m" + "\033[1;33m" + i['progName'] +"\033[1;m" + "                  "  + "\033[1;35m" +i['progLaunchDate'] + "\033[1;m" +  "                 " + "\033[1;36m" +i['progMinBounty'] + "\033[1;m"

def crawlHackerone(driver):
    driver.get('https://hackerone.com/directory?order_direction=DESC') 
    time.sleep(10)
    #ele = driver.execute_script('return document.body.innerHTML')
    #driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
    #time.sleep(10)
    #driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
    #time.sleep(10)
    
    SCROLL_PAUSE_TIME = 5
    
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
    
    
    #x=driver.find_element_by_css_selector('.daisy-link spec-profile-name')
    #print x,type(x)
    ele=driver.execute_script('return document.body.innerHTML')
    #print ele
    root=bs4.BeautifulSoup(ele,"lxml")
    #print dir(root)
    #print type(root)
    #programs = root.find_all('a',{'class':'daisy-link spec-profile-name'})
    #for p in programs:
    #    progDir.append(str(p).split(">")[1].split("<")[0])
    #program_set =set(progDir)
    #dump_dump('programs_orig',program_set)
    # driver.click..
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
	



# Option 1 - with ChromeOptions
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-application-cache')
chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors. 
driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options,service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])

# Option 2 - with pyvirtualdisplay
#from pyvirtualdisplay import Display 
#display = Display(visible=0, size=(1024, 768)) 
#display.start() 
#driver = webdriver.Chrome(driver_path='/home/dev/chromedriver', 
#          service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])

# Log path added via service_args to see errors if something goes wrong (always a good idea - many of the errors I encountered were described in the logs)

# And now you can add your website / app testing functionality: 
crawlHackerone(driver)
#dump_load('programs_orig')
printHackeronePrograms(progDir)
driver_stop(driver)
