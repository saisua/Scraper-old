#!/usr/bin/python3
# -*- coding: utf-8 -*-

#Import nativos de Python
print("\n\n\n")
#Import descargables
tries = 0
while(True):
    try:
        from selenium import webdriver
        from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        from selenium.webdriver.common.by import By
        import os
        del tries
        print("[+]Libraries loaded successfully")
        break
    except Exception as ex:
        print("[-]Error: " + str(ex)+"\n")
        print("Libraries missing. Installing...")
        Libraries = ["selenium"]
        if tries > 3:
            print("[-]Libraries' (" +str(Libraries)+" install failed "+str(tries)+" times.")
            print("Do you have internet connection?")
            print("Exiting...")
            exit()
        import subprocess
        import sys
        for lib in Libraries:
            subprocess.check_call([sys.executable, "-m", "pip", str(lib)])
        tries+=1



class Crawler(object):
    def __init__(self):
        try:
            firefox_capabilities = DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True
            self.driver = webdriver.Firefox(executable_path=(__file__).replace("crawler2.py","")+"geckodriver")
        except Exception as ex:
            print("\n \n")
            print(ex)
            print("\n \n")
            self.driver = webdriver.Firefox()

    def create_crawler(self, crawler_name):
        self.name = str(crawler_name)
        self.visited_sites = {}
        print("New crawler ("+str(self.name)+") created.")

    def get_website(self, site):
        print("Trying to get site: " + str(site))
        self.current_site_URL = site
        self.driver.get(site)
        if(site in self.visited_sites.keys()):
            self.visited_sites[site] += 1
        else:
            self.visited_sites[site] = 1
        print("Site loaded successfully!")

    def find_in_website(self, search, tag=By.TAG_NAME):
        try:
            return self.driver.find_elements(tag,search)
        except: print("No element found")

    def store(self, data):
        open(self.name,"a").write(data).close()

    def crawl(self, site, actual_depth=1, max_depth=1):
        self.get_website(site)
        link_list = self.find_in_website("//a[@href]",By.XPATH)
        for link_obj in link_list:
            try:
                link = link_obj.get_attribute("href")
            except: continue
            print(str(actual_depth),link)
            if actual_depth <= max_depth:
                self.crawl(link,actual_depth+1, max_depth)

#TESTS
crawler1 = Crawler()
crawler1.create_crawler("c1")
crawler1.crawl("https://duckduckgo.com/?q=ver+piratas+del+caribe+2+online&t=ffab&ia=web",1,2)
if(False):
    inu = 1
    while(inu):
        inu = input("> ")
        try:
            exec(inu)
        except Exception as e: print("[-] Error: " + str(e))
