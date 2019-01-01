# Scraper
A python selenium bot for data gathering

###### Classes
Class Crawler: 
This class is the bot itself, whose settings will be shared between different crawlings if they are done with the same object

### Functions ### Crawler

function <b>__init__</b>(self, crawler_name, user=None, passwd=None, timeout=20, time_wait=1.5, info_as_node_xml=False, rem=False):
This function is called when a new crawler is created. 

#crawler_name: (str) this is the only parameter necessary, and it will determine the name of the file .xml the info will be dumped in.

#user: At the moment untested.
#passwd: At the moment untested.

#timeout: (int) The number of times the program will try to load more parts of the site

#time_wait: (float) The amount of time (sec) the program will wait before try to load the next part of the site. It should be adjusted on the amount of bandwith and the loading weight of the sites it will access. The default value is more than what i needed while testing on instagram

#info_as_node_xml (bool) This will determine wether the info, when collected from a site will be included in the node of the site it has been collected from (False) or it will be added as a new node (True)

#rem this is a attr i will remove, I used it when debugging

function <b>__repr__</b>(self):
when printed a Crawler object, this function returns custom data I find useful.

function <b>get_website</b>(self, site=None, parent=None, depth=0):
This function marks as visited the actual site. Other functionaities if site attr is given

#site (str/None) when given this attr function will open the website it's given in a tab.

#parent (ET.Element object/ET.SubElement object/ None) when given all attr, creates a new Site object, which is added to self.sites. This attr will determine whose parent this site will be son of. If the value is None, the site will be placed as the root of the xml file.

#depth (int) when given all attr, creates a new Site object, which is added to self.sites. This attr is the depth that the crawler will get to determine how to proceed with the site. By default set to 0, as the root site where the program will begin the crawling, if that's what is meant to do.

function <b>crawl</b>(self, site=None, max_depth=1, load_amount=1, max_tabs=5, save_text=False, save_img=False, condition=None, do_if_condition=None, recrawl=False, autosave=False):
This function does a multi-tab crawling of depth max_depth, starting by site

#site (str/None) The site where the function will start to crawl. If its value is None, the function will assume the starting point the site open when executed

#max_depth (int) The depth of sites the program will open. This means the time of execution will grow huge extremely easy. It must be less than max_tabs*

#load_amount (int) What will the crawler interact with to load info that can only be accessed by scrolling/clicking on dynamically loaded sites. Now:
        >=0: Scroll the main site scroll
        >=1: Scroll all scrolls in the site
                ...Future versions

#max_tabs (int) The number of tabs the program will be allowed to open sites in. Usually browsers use high amounts of memory, so this attr is rather important in old computers. This must be more than max_depth*

*Because I use a DFS algorithm

#save_text (bool) Either save or don't the plain text found in the loaded site

#save_img (bool) Either save or don't the url of the images found in the loaded site

#condition (str) Determine, in an eval() wether or not the program should run do_if_condition

#do_if_condition (str) In case condition is True, the crawler will eval() do_if_condition once the site is full loaded

#recrawl (bool) It tells the crawler if it should reload sites that the program has alredy visited. 

#autosave (bool) Save the xml tree every crawling cycle. This should make the crawler take longer, but the data won't be lost if the crawler is interrupted in the middle of crawling



Got 55 sites' text and images (Not including those which can be accessed by a button in the dom [Future version]) in 6m10.567s 
Ref. time command Linux
