#!$PREFIX/bin/python2
# -*- coding: utf-8 -*-

#Import nativos de Python

#Import descargables
tries = 0
try:
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    print("Libraries loaded successfully")
except Exception as ex:
    print("Error: " + str(ex)+"\n")
    print("Libraries missing. Installing...")
    Libraries = ["selenium"]
    if tries > 3:
        print("Libraries' (" +str(Libraries)+" install failed 5 times.")
        print("Do you have internet connection?")
        print("Exiting...")
        exit()
    import subprocess
    import sys
    #for lib in Libraries:
        #subprocess.check_call([sys.executable, "-m"-, "pip", str(lib)])
    #import_external(tries+1)


class Crawler(object):
    def __init__(self):
        if(True):
            #driver = webdriver.Firefox(FirefoxBinary('./'))
            firefox_capabilities = DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True
            firefox_capabilities['binary'] = webdriver.FirefoxProfile(
'/data/data/com.termux/files/home/Scrapy_scrapper/')
            driver = webdriver.Firefox(capabilities=firefox_capabilities,executable_path = '/data/data/com.termux/files/home/Scrapy_scarpper/geckodriver')
        #except Exception as ex:
        else:
            print("\n \n")
            print(ex)
            print("\n \n")
            driver = webdriver.Firefox()

    def create_crawler(self, crawler_name):
        self.name = str(crawler_name)
        self.visited_sites = {}
        print("New crawler ("+str(self.name)+") created.")

    def get_website(self, site):
        print("Trying to get site: " + str(site))
        self.current_site_URL = site
        self.current_site = driver.get(site)
        try:
            self.visited_sites[site] += 1
        except:
            self.visited_sites[site] = 1
        print("Site loaded successfully!")

    def find_in_website(self, search):
        Crawler.store(self, driver.find_element_by_xpath(search))

    def store(self, data):
        open(self.name,"a").write(data).close()

    #Falta depth i recursivitat


#TESTS
crawler1 = Crawler()
Crawler.create_crawler(crawler1, "c1")
Crawler.get_website(crawler1, "http://www.upv.es/")
