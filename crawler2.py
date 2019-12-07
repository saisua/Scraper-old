#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import 
import getpass
import time
import os
from random import randint, choice
from sys import argv

import logging
import xml.etree.ElementTree as ET
# import imageio Save as file
from skimage import img_as_float, data
from skimage.io import imread
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium import webdriver
from collections import defaultdict
from tldextract import extract
from datetime import datetime

try:
    from image_manager import Image_manager,img_compare_encode,img_face_encode,img_face_load
except ImportError:
    Image_manager,img_compare_encode,img_face_encode,img_face_load = [lambda *_ : []]*4
#import _thread


class Crawler(object):
    """
    Despite its name, the crawler object is a browser site manager, with
    the ability to crawl from any site it's allowed
    """
    def __init__(self, crawler_name:str, output:str=None,timeout_load:float=20, timeout_seconds:int=30,
                time_wait:float=1.5, info_as_node_xml:bool=False, tabs_per_window:int=1000, 
                images_known:list=[], find_known_img:bool=False, find_faces_known:bool=False,
                http_proxy:str=None, ftp_proxy:str=None, ssl_proxy:str=None, socks_proxy:str=None,
                load_images:bool=True, headless:bool=False, learning:bool=True, max_cache_RAM_KB:int=False,
                width_min:int=None, width_max=None, height_min:int=None, height_max:int=None):
                # 420,640 420,1280
        logging.info(f"Starting the creation of crawler {crawler_name}")

        try:
            firefox_capabilities = DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True
            firefox_capabilities["dom.popup_maximum"] = tabs_per_window

            options = webdriver.firefox.options.Options()
            options.set_preference("browser.popups.showPopupBlocker",False)

            if(headless):
                #DeprecationWarning: use setter for headless property instead of options.set_headless()
                options.set_headless()

            profile = webdriver.FirefoxProfile()
            del profile.DEFAULT_PREFERENCES['frozen']["browser.link.open_newwindow"]
            del profile.DEFAULT_PREFERENCES['frozen']["security.fileuri.origin_policy"]
            #http://kb.mozillazine.org/About:config_entries  #profile
            #http://kb.mozillazine.org/Category:Preferences
            profile.set_preference("browser.link.open_newwindow", 3)
            profile.set_preference("dom.popup_maximum", tabs_per_window)
            profile.set_preference("browser.dom.window.dump.enabled", False)
            profile.set_preference("browser.tabs.loadDivertedInBackground", True)
            profile.set_preference("browser.showPersonalToolbar", False)
            profile.set_preference("browser.preferences.defaultPerformanceSettings.enabled", False)
            profile.set_preference("privacy.trackingprotection.enabled", True)
            profile.set_preference("content.notify.interval", 500000)
            profile.set_preference("content.notify.ontimer", True)
            profile.set_preference("content.switch.threshold", 250000)
            profile.set_preference("browser.cache.memory.capacity", 65536)
            profile.set_preference("browser.startup.homepage", "about:blank")
            profile.set_preference("reader.parse-on-load.enabled", False)
            profile.set_preference("browser.pocket.enabled", False) 
            profile.set_preference("loop.enabled", False)
            profile.set_preference("browser.chrome.toolbar_style", 1)
            profile.set_preference("browser.display.show_image_placeholders", False)
            profile.set_preference("browser.display.use_document_colors", False)
            profile.set_preference("browser.display.use_document_fonts", 0)
            profile.set_preference("browser.display.use_system_colors", False)
            profile.set_preference("browser.formfill.enable", False)
            profile.set_preference("browser.helperApps.deleteTempFileOnExit", True)
            profile.set_preference("browser.shell.checkDefaultBrowser", False)
            profile.set_preference("browser.startup.homepage", "about:blank")
            profile.set_preference("browser.startup.page", 0)
            profile.set_preference("browser.tabs.forceHide", True)
            profile.set_preference("browser.urlbar.autoFill", False)
            profile.set_preference("browser.urlbar.autocomplete.enabled", False)
            profile.set_preference("browser.urlbar.showPopup", False)
            profile.set_preference("browser.urlbar.showSearch", False)
            profile.set_preference("extensions.checkCompatibility", False) 
            profile.set_preference("extensions.checkUpdateSecurity", False)
            profile.set_preference("extensions.update.autoUpdateEnabled", False)
            profile.set_preference("extensions.update.enabled", False)
            profile.set_preference("general.startup.browser", False)
            profile.set_preference("plugin.default_plugin_disabled", False)
            profile.set_preference("browser.privatebrowsing.autostart", True)
            profile.set_preference("navigator.doNotTrack", 1)
            profile.set_preference("general.useragent.override", '')
            profile.set_preference('general.platform.override','')
            profile.set_preference('general.appname.override','')
            profile.set_preference('general.appversion.override','')
            profile.set_preference("general.buildID.override", '')
            profile.set_preference("general.oscpu.override", '')
            # Not working. I think it's not possible either
            # It depends in wether useragent was modified or not
            profile.set_preference('general.webdriver.override',False)
            profile.set_preference('general.useragent.vendor', '')
            profile.set_preference("browser.search.region",choice([
                        "AF","AL","DZ","AS","AD","AO","AQ","AG","AR","AM",
                        "AW","AU","AT","AZ","BS","BH","BD","BB","BY","BE",
                        "BZ","BJ","BM","BT","BO","BA","BW","BV","BR","IO",
                        "BN","BG","BF","BI","KH","CM","CA","CV","KY","CF",
                        "CF","TD","CL","CN","CX","CC","CO","KM","CG","CD",
                        "CK","CR","CI","HR","CU","CY","CZ","DK","DJ","DM",
                        "DO","EC","EG","SV","GQ","ER","EE","ET","FK","FO",
                        "FJ","FI","FR","GF","PF","TF","GA","GM","GE","DE",
                        "GH","GI","GR","GL","GD","GP","GU","GT","GN","GW",
                        "GY","HT","HM","HK","HU","IS","IN","ID","IR","IQ",
                        "IE","IL","IT","JM","JP","JO","KZ","KE","KI","KP",
                        "KR","KW","KG","LA","LB","LS","LR","LY","LI","LT",
                        "LU","MO","MK","MG","MW","MY","MV","ML","MT","MH",
                        "MQ","MT","MU","YT","MX","FM","MD","MC","ME","MS",
                        "MA","MZ","MM","NA","NR","NP","NL","AN","NC","NZ",
                        "NI","NE","NG","NU","NF","MP","NO","OM","PK","PW",
                        "PS","PA","PG","PY","PE","PH","PN","PL","PT","PR",
                        "QA","RE","RO","RU","RW","SH","KN","LC","PM","VC",
                        "WS","SM","ST","SA","SN","RS","SC","SL","SG","SK",
                        "SI","SB","SO","ZA","GS","ES","LK","SD","SR","SJ",
                        "SZ","SE","CH","SY","TW","TJ","TZ","TH","TZ","TH",
                        "TL","TG","TK","TO","TT","TN","TR","TM","TC","TV",
                        "UG","UA","AE","GB","US","UM","UY","UZ","VU","VE",
                        "VN","VG","VI","WF","EH","YE","ZM","ZW"]))
            #profile.set_preference("browser.search.region",'')
            profile.set_preference("browser.search.defaultenginename",'')
            profile.set_preference("browser.search.order.1",'')
            profile.set_preference("security.fileuri.strict_origin_policy",False)
            profile.set_preference("security.fileuri.origin_policy",0)
            profile.set_preference("security.sandbox.content.level", 0)
            profile.set_preference("privacy.resistFingerprinting", True)
            profile.set_preference("privacy.trackingprotection.fingerprinting.enabled", True)
            profile.set_preference("privacy.trackingprotection.cryptomining.enabled", True)
            profile.set_preference("intl.accept_languages", "en")
            profile.set_preference("services.sync.prefs.sync.intl.accept_languages", False)
            profile.set_preference("browser.newtabpage.activity-stream.feeds.section.topstories.options",
                                        """{"api_key_pref":"extensions.pocket.oAuthConsumerKey","hidden":true,"provider_icon":"pocket",
                                        "provider_name":"Pocket","read_more_endpoint":"https://getpocket.com/explore/trending?src=fx_new_tab",
                                        "stories_endpoint":"https://getpocket.cdn.mozilla.net/v3/firefox/global-recs?version=3&consumer_key=
                                        $apiKey&locale_lang=en&feed_variant=default_spocs_off","stories_referrer":
                                        "https://getpocket.com/recommendations","topics_endpoint":
                                        "https://getpocket.cdn.mozilla.net/v3/firefox/trending-topics?version=2&consumer_key=$apiKey&locale_lang=en"
                                        ,"model_keys":["nmf_model_animals","nmf_model_business","nmf_model_career","nmf_model_datascience",
                                        "nmf_model_design","nmf_model_education","nmf_model_entertainment","nmf_model_environment",
                                        "nmf_model_fashion","nmf_model_finance","nmf_model_food","nmf_model_health","nmf_model_home",
                                        "nmf_model_life","nmf_model_marketing","nmf_model_politics","nmf_model_programming","nmf_model_science",
                                        "nmf_model_shopping","nmf_model_sports","nmf_model_tech","nmf_model_travel","nb_model_animals",
                                        "nb_model_books","nb_model_business","nb_model_career","nb_model_datascience","nb_model_design",
                                        "nb_model_economics","nb_model_education","nb_model_entertainment","nb_model_environment","nb_model_fashion",
                                        "nb_model_finance","nb_model_food","nb_model_game","nb_model_health","nb_model_history","nb_model_home",
                                        "nb_model_life","nb_model_marketing","nb_model_military","nb_model_philosophy","nb_model_photography",
                                        "nb_model_politics","nb_model_productivity","nb_model_programming","nb_model_psychology","nb_model_science",
                                        "nb_model_shopping","nb_model_society","nb_model_space","nb_model_sports","nb_model_tech","nb_model_travel",
                                        "nb_model_writing"],"show_spocs":false,"personalized":false,"version":1}""")
            profile.set_preference("browser.search.context.loadInBackground", True)
            profile.set_preference("geo.enabled", False)
            profile.set_preference("browser.search.geoip.url", "")
            profile.set_preference("geo.wifi.uri", "")
            profile.set_preference("services.sync.prefs.sync.layout.spellcheckDefault", False)
            profile.set_preference("services.sync.prefs.sync.spellchecker.dictionary", False)
            profile.set_preference("browser.formfill.enable", False)
            profile.set_preference("browser.microsummary.updateGenerators", False)
            profile.set_preference("browser.search.update", False)
            profile.set_preference("browser.urlbar.filter.javascript", False)
            profile.set_preference("dom.allow_scripts_to_close_windows", True)
            #profile.set_preference("dom.disable_window_status_change", False)  Not necessary
            #profile.set_preference("dom. event. contextmenu. enabled", True)
            profile.set_preference("network.cookie.enableForCurrentSessionOnly", True)
            profile.set_preference("network.http.max-connections", 10000)
            profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
            profile.set_preference("privacy.spoof_english", 2)
            profile.set_preference("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.addons", False)
            profile.set_preference("browser.newtabpage.activity-stream.asrouter.userprefs.cfr.features", False)
            profile.set_preference("browser.search.suggest.enabled", False)
            profile.set_preference("xpinstall.whitelist.required", True)
            




            #Test
            profile.set_preference("network.manage-offline-status", True)
            profile.set_preference("browser.offline", True)

            options.add_argument("--lang=en")

            # Not tested
            if(max_cache_RAM_KB): profile.set_preference("browser.cache.memory.capacity",max_cache_RAM_KB)

            self.max_cache_RAM_KB = max_cache_RAM_KB

            self.headless = headless


            if(not load_images):
                profile.set_preference("permissions.default.image", 2)

            if(not http_proxy is None): 
                webdriver.DesiredCapabilities.FIREFOX['proxy']['httpProxy'] = http_proxy
            if(not ftp_proxy is None): 
                webdriver.DesiredCapabilities.FIREFOX['proxy']['ftpProxy'] = ftp_proxy
            if(not ssl_proxy is None): 
                webdriver.DesiredCapabilities.FIREFOX['proxy']['sslProxy'] = ssl_proxy
            if(not socks_proxy is None):
                profile.set_preference("network.proxy.typ_e", 1)
                profile.set_preference("network.proxy.socks", socks_proxy[:socks_proxy.find(":")])
                profile.set_preference("network.proxy.socks_port", int(socks_proxy[socks_proxy.find(":")+1:]))
    
            self.http_proxy = http_proxy
            self.ftp_proxy = ftp_proxy
            self.ssl_proxy = ssl_proxy
            self.socks_proxy = socks_proxy

            logging.info("Configuration complete. Trying to run the drivers. This could take some time...")
            self.driver = webdriver.Firefox(executable_path=(
                    __file__).replace("crawler2.py", "geckodriver"),
                    options=options, firefox_profile=profile) #firefox_binary=binary,
            logging.info("Drivers ran succesfully!")

            # Useless
            if(width_min and width_max and height_min and height_max):
                self.driver.set_window_position(0, 0)
                self.driver.set_window_size(randint(width_min,width_max), randint(height_min, height_max))

            if(learning and False):
                listener = Listener(self)
                self.driver = EventFiringWebDriver(self.driver,listener)
                listener.new_tab_menu()

        except Exception as ex:
            logging.warning(f"Looks like something failed. Error message: {ex}")

            self.driver = webdriver.Firefox()

        self.directory = (__file__)[:-len("crawler2.py")]
        if(self.directory): os.chdir(self.directory)

        self.name = str(crawler_name)

        if(output is None): output = crawler_name
        self.output = output

        self.visited_sites = defaultdict(lambda : 0)
        self.visited_domain = defaultdict(lambda : 0)

        self.data_tree = ET.ElementTree()
        self.data_root = None

        self.timeout_load = timeout_load
        self.time_wait_load = time_wait
        self.driver.set_page_load_timeout(timeout_seconds)
        self.timeout_seconds = timeout_seconds

        self.tabs_per_window = tabs_per_window

        self.processing_tabs = []
        self.loaded_sites = []
        self.sites = {}
        self.to_remove = []

        self.info_as_node = info_as_node_xml

        self.load_images = load_images
        self.images_known = dict(zip(images_known,img_compare_encode(images_known)))
        self.find_known_img = find_known_img
        self.find_faces_known = find_faces_known

        self.time_created = datetime.now()
        
        logging.info(f"New crawler ({self.name}) created.")

    def __repr__(self) -> str:
        return f"<class '__main__'.Crawler, name='{self.name}', loaded {len(self.loaded_sites)} sites>"

    # Loads a new site in the current tab
    def get_website(self, site=None, parent=None, depth:int=0, forbidden_domains:list=[], allowed_domains:list=['*']) -> None:
        logging.debug(f"Trying to get site: {site}")
        if(not len(self.driver.window_handles)): self.__init__(self.name, self.output, self.timeout_load,
                                                        self.timeout_seconds, self.time_wait_load, self.info_as_node,
                                                        self.tabs_per_window, self.images_known, self.find_known_img,
                                                        self.find_faces_known, self.http_proxy, self.http_proxy,
                                                        self.ssl_proxy, self.socks_proxy, self.load_images,
                                                        self.headless, True, self.max_cache_RAM_KB)
        if(site):   
            try:
                self.driver.get(site)
            except TimeoutException as e:
                print(f"The site timed out. Skipping {site}")
                self.exec_js("window.close();")
                return 
            #self.exec_js("screen = new function() { this.width = 1; this.height = 2 };")
            if(parent is None):
                parent = self.store(
                    typ_e="site", data=self.driver.current_url, dataname="link", root=True)
            self.processing_tabs.append(Site(link=site, tab=self.driver.current_window_handle,
                                            hrefs=self.get_new_sites(forbidden_domains=forbidden_domains, allowed_domains=allowed_domains), 
                                            depth=depth, parent=parent, timeout=-1))
            self.sites[self.processing_tabs[-1]] = depth
            for _ in range(0):
                try: 
                    self.exec_js("return jQuery")
                    logging.info("jQuery successfully loaded")  
                    break
                except Exception as e:
                    #if(e.msg == "Cyclic object value"): break
                    # Code from https://stackoverflow.com/questions/7474354/include-jquery-in-the-javascript-console
                    self.exec_js("""javascript: (function(e, source) {
                                    e.src = source;
                                    e.onload = function() {
                                        jQuery.noConflict();
                                        console.log('jQuery loaded');
                                    };
                                    document.head.appendChild(e);
                                    //document.domain = "https://code.jquery.com";
                                })(document.createElement('script'), '//code.jquery.com/jquery-latest.min.js');""")
                    time.sleep(.5) 
                    logging.warning(f"jQuery failed with message: {e}")    
            #else: logging.warning("jQuery not loaded")                    
        
        self.current_domain = self.exec_js("return document.domain")

        self.visited_sites[self.driver.current_url] += 1

        self.visited_domain[self.current_domain] += 1

        logging.debug("[+]Site opened successfully!")

    # Loads and manages recursivelly all sites it can find
    def crawl(self, site=None, max_depth:int=1, load_amount:int=-1, max_tabs:int=5,
            record_text:bool=False, record_img:bool=False, record_source:bool=False,
            record_iframes:bool=False, forbidden_domains:list=[], allowed_domains:list=['*'],
            condition:str=None, do_if_condition:str=None, recrawl:bool=False, 
            autosave:int=False, record_depth:bool=True) -> None:

        if(site):
            self.get_website(site, forbidden_domains=forbidden_domains, allowed_domains=allowed_domains)

        if(max_tabs > max_depth):
            #num tabs must be at least equal to max depth being opened
            #but max_depth starts at 0.
            #try:
            counter = 0
            while(len(self.processing_tabs)):
                # Open needed tabs
                self.crawl_new_tab(max_depth, max_tabs, forbidden_domains=forbidden_domains, allowed_domains=allowed_domains)

                # Load all tabs
                if(load_amount >= 0):
                    self.crawl_load_remove_tabs(load_amount, max_depth, max_tabs, record_text, record_img,
                                                    record_source, record_depth, record_iframes, condition, 
                                                    do_if_condition)
                    # Treat buttons
                    #logging.info(self.classify_buttons())
                    
                if(autosave and not counter): 
                    print("Storing data... ", end='')
                    self.data_to_xml(self.data_root)
                    
                    print("Done")
                counter = (counter+1)%autosave
            
            #except Exception as err:
                #raise err
                #logging.error(err)
            
            self.data_to_xml(self.data_root)

    def crawl_new_tab(self, max_depth:int=1, max_tabs:int=5, forbidden_domains:list=[], allowed_domains:list=['*']) -> None:
        while(len(self.driver.window_handles) < max_tabs and len([site_value for (site_key, site_value) in self.sites.items() 
                        if site_value < max_depth and len(site_key.get_hrefs()) and not site_key in self.loaded_sites])):
            site = [site_key for (site_key, site_value) in sorted(self.sites.items(), key=lambda x: x[1], reverse=True) 
                        if site_value < max_depth and len(site_key.get_hrefs())][0]
            
            self.driver.switch_to.window(site.get_tab())
            
            site.set_hrefs([new for new in self.get_new_sites(forbidden_domains=forbidden_domains, allowed_domains=allowed_domains) if not new.get_attribute("href") in self.visited_sites.keys()])
            
            if(not len(site.get_hrefs())): continue

            link = site.get_hrefs()[0]
            link_href = link.get_attribute("href")
            if(not link_href in self.visited_sites.keys()):
                self.visited_sites[link_href] = 1  # Just in case redirect
                site.remove_from_hrefs(link)  # Only useful when last href
            
            parent = self.store(
                typ_e="site", data=link_href, dataname="link", root=False, parent=site.get_parent())
            
            self.goto_new_site(
                link=link_href, depth=site.get_depth(), parent=parent)
            
            logging.debug(f"Loaded tab number {len(self.driver.window_handles)}")
        try:  # To free up memory IF went into the while
            del link, link_href, site, parent
        except: pass

    def crawl_load_tabs(self, load_amount:int=-1, max_depth:int=1, max_tabs:int=5, condition:str=False, 
                        do_if_condition:str=False, record_text:bool=False, record_img:bool=False,
                            record_source:bool=False, record_depth:bool=True, record_iframes:bool=False) -> list:
        for site in self.processing_tabs:  # Last tab opened does not load
            if(site.get_timeout() < self.timeout_load):
                
                self.driver.switch_to.window(site.get_tab())
                
                loaded_before = site.get_removed_scroll()[:]
                loaded = self.load_site(
                    removed_scroll=loaded_before, deep=load_amount)
                
                if(type(loaded) == list and site.get_timeout() < self.timeout_load):
                    if(len(loaded) > len(loaded_before) and not site.get_depth == max_tabs):
                        logging.warning("Restarted timeout!")
                        site.set_timeout(0)
                    
                    site.set_removed_scroll(loaded[:])
                elif(not len(site.get_hrefs()) or (site.get_depth() == max_depth and site.get_timeout() > 0)):
                    # Has the site loaded entirely? If the site depth is max_depth
                    # the amount of href will never go down
                    self.to_remove.append(site)
                
                site.set_timeout(site.get_timeout()+1)
                logging.info(f"Site {site.get_link()} increased timeout to {site.get_timeout()}")
            
                del loaded, loaded_before

            #if(not site in self.loaded_sites and ((not len(site.get_hrefs()) and site.get_depth() < max_depth) and site.get_timeout() >= self.timeout_load)):
            # The one above was made by thinking, the one below by karnaugh     
            if((not len(site.get_hrefs()) and site in self.loaded_sites) or 
                        (not len(site.get_hrefs()) and site.get_timeout() >= self.timeout_load) or
                        (site.get_timeout() >= self.timeout_load and not site.get_depth() < max_depth) or 
                        (site in self.loaded_sites and not site.get_timeout() >= self.timeout_load and 
                        not site.get_depth() < max_depth)):
                if(not site in self.to_remove):
                    self.to_remove.append(site)
            # dont delete if got all links but not loaded
            #elif(site in self.loaded_sites and (not len(site.get_hrefs()) or site.get_depth() == max_depth or site.get_timeout() >= self.timeout_load)):
                else:
                    # Actually delete marked tabs
                    if(site.get_timeout() == self.timeout_load):  # Remove later debug purpose
                        logging.warning("Timeout >.<")
                    else:
                        logging.debug("Site full loaded")
                    
                    if(condition and do_if_condition):
                        if(eval(condition)):
                            logging.info("Do_if_condition: ", end="")
                            logging.info(eval(do_if_condition))

                    print("Gathering data... ",end='')

                    if(record_text):
                        print("text ",end='')
                        self.get_text(parent=site.get_parent(), keep_dom_nodes=False, link=site.get_link())
                    if(record_img):
                        print("images ",end='')
                        self.get_images(parent=site.get_parent(), link=site.get_link())
                    if(record_source):
                        print("source ",end='')
                        self.get_source(parent=site.get_parent(), link=site.get_link())
                    if(record_depth):
                        if(self.info_as_node):
                            typ_e = "depth"
                        else: typ_e = None
                        self.store(typ_e=typ_e, data=site.get_depth(), dataname="depth", root=False, parent=site.get_parent())
                        del typ_e
                    if(record_iframes):
                        print("iframes ",end='')
                        self.get_iframes(parent=site.get_parent(), link=site.get_link())

                    if(site.get_depth()==max_depth):
                        for link in site.get_hrefs():
                            try:
                                self.store(typ_e="site", data=link.get_attribute("href"), dataname="link", root=False, parent=site.get_parent())
                            except: continue

                    print("Done.")
                    
                    
                    logging.info(f"Closed depth {self.sites[site]} num {len(self.processing_tabs)} site \""
                    f"{site.get_link()}\" ({site.get_tab()}) with unopened {len(site.get_hrefs())} links")

                    if(len(self.driver.window_handles) == 1): 
                        self.driver.quit()
                        self.processing_tabs.clear()
                    else:
                        self.driver.switch_to.window(site.get_tab())    
                        self.exec_js("window.close();")
                        
                        self.processing_tabs.remove(site)
                    
                    if(site in self.to_remove):
                        self.to_remove.remove(site)
                    del self.sites[site]
            
        time.sleep(self.time_wait_load)

        return self.to_remove

    def crawl_remove_tabs(self, max_depth:int=1, record_text:bool=False, record_img:bool=False,
                            record_source:bool=False, record_depth:bool=True, record_iframes:bool=False) -> None:

        # iframes are not being recorded
        self.to_remove = [valid for valid in self.to_remove if not valid.get_tab() in self.driver.window_handles]
        
        if(len(self.to_remove) > 0):
            for removing in self.to_remove:
                try:  # Sometimes tab is closed but not removed form list
                    self.driver.switch_to.window(removing.get_tab())
                    
                    if(record_text):
                        self.get_text(parent=removing.get_parent(), keep_dom_nodes=False, link=removing.get_link())
                    if(record_img):
                        self.get_images(parent=removing.get_parent(), link=removing.get_link())
                    if(record_source):
                        self.get_source(parent=removing.get_parent(), link=removing.get_link())
                    if(record_depth):
                        if(self.info_as_node):
                            typ_e = "depth"
                        else: typ_e = None
                        self.store(typ_e=typ_e, data=removing.get_depth(), dataname="depth", root=False, parent=removing.get_parent())
                        del typ_e
                    if(record_iframes):
                        self.get_iframes(parent=removing.get_parent(), link=removing.get_link())

                    if(removing.get_depth()==max_depth):
                        for link in removing.get_hrefs():
                            try:
                                self.store(typ_e="site", data=link.get_attribute("href"), dataname="link", root=False, parent=removing.get_parent())
                            except: continue

                    self.loaded_sites.append(removing)
                
                except Exception as err:
                    logging.error(err)

    def crawl_load_remove_tabs(self, load_amount:int=-1, max_depth:int=1, max_tabs:int=5, record_text:bool=False,
                                record_img:bool=False, record_source:bool=False, record_depth:bool=True, record_iframes:bool=False,
                                condition:str=False, do_if_condition:str=False) -> None:
        self.crawl_load_tabs(load_amount, max_depth, max_tabs, condition, do_if_condition, record_text, record_img, record_source, record_depth, record_iframes)
        #self.crawl_remove_tabs(max_depth, record_text, record_img, record_source, record_depth, record_iframes)

    # Runs loads a new site and returns its hrefs
    def get_new_sites(self, site:str=None, forbidden_domains:list=[], allowed_domains:list=['*']) -> list:
        # Later it will not only get hrefs
        if(site):
            self.get_website(site)

        final = []
        tab = self.driver.current_window_handle
        for link in self.find_in_website(["//a[@href]"], By.XPATH):
            try: 
                domain = extract(link.get_attribute('href'))
                if(not '.'.join(domain[(1 if domain[0]=='' else 0):]) in forbidden_domains): 
                    final.append(link)
            except StaleElementReferenceException:
                logging.error("Missing element. Checking for popups")
                if(self.driver.current_window_handle != tab):
                    try:
                        self.driver.switch_to.window(tab)
                        domain = extract(link.get_attribute('href'))
                        if(not '.'.join(domain[1 if domain[0]=='' else 0:]) in forbidden_domains): 
                            final.append(link)
                    except: continue
        
        if(not '*' in allowed_domains):
            final = [link for link in final if '.'.join(extract(link.get_attribute('href'))[1 if extract(link.get_attribute('href'))[0]=='' else 0:]) in allowed_domains]

        return final

    # Given a list of buttons determines if it may cause data loss
    def classify_buttons(self) -> dict:
        logging.debug("Crawler.classify_buttons(self)")

        last = self.driver.current_window_handle

        #self.goto_new_site(self.driver.current_url) # Useful?  

        try:
            buttons = self.exec_js("return (jQuery('body, body *').contents().filter(function() {"
                                    "return jQuery._data(this, 'events') != undefined})).toArray()")
        except: return []

        if(not len(buttons)): return

        classifies = {"loss":[],"kept":[],"links":[]}
        for num, button in enumerate(buttons): 
            try:
                for event in self.exec_js("return Object.keys(jQuery._data(arguments[0], 'events'))", button):
                    clink = self.driver.current_url #click+link
                    try:
                        eval(f"button.{event}()")
                        WebDriverWait(self.driver, 10, 0.2).until(lambda _: self.exec_js(
                                        "return document.readyState == 'complete';"))
                        if(num):
                            classifies["kept"].append(buttons[num-1])
                    except:
                        if(num):
                            classifies["loss"].append(buttons[num-1])
                            classifies["links"].append(clink)
                        self.driver.back()
                        eval(f"button.{event}()")
                        WebDriverWait(self.driver, 10, 0.2).until(lambda _: self.exec_js(
                                        "return document.readyState == 'complete';"))
            except Exception as e: 
                logging.info(f"button: {button}")
                logging.error(e)
        try:
            buttons[0].get_attribute("class")
            classifies["kept"].append(button)
        except:
            classifies["loss"].append(button)
        
        self.exec_js("window.close();")
        self.driver.switch_to.window(last)

        return classifies

    # Opens a new tab if possible and loads link
    def goto_new_site(self, link:str, depth:int=0, parent:object=None) -> None:
        # Later new tab and same tab buttons

        if(len(self.driver.window_handles) >= self.tabs_per_window):
            logging.warning("Multi-threading in a later version")
            raise Exception("Version not compatible with multithreading")
        else:
            self.exec_js("window.open();")
        
        #Switch to new tab instead of next
        self.driver.switch_to.window(self.driver.window_handles[self.driver.window_handles.index(
            self.driver.current_window_handle)+1])
        
        self.get_website(site=link, depth=depth+1, parent=parent)

    # Find all elements as told by its arguments. 
    # More info search for "Selenium find_elements"
    def find_in_website(self, search:list, tag:str=By.TAG_NAME, site:str=None) -> list:
        if(site):
            self.get_website(site)
        
        if(not type(search) is list and not type(search) is tuple): search = [search] 

        final = []
        for searching in search:
            try:
                final += self.driver.find_elements(tag, searching)
            except:
                logging.warning(f"No element {searching} found")
        return final

    def store(self, typ_e:str=None, data:str=None, dataname:str=None,
                parent:object=None, root:object=False) -> object:
        logging.debug(f"Stored: \"{data}\"")
        if(typ_e):
            if(parent is None):
                parent = ET.Element(typ_e)
            else:
                parent = ET.SubElement(parent, str(typ_e))
            
            if(data and dataname):
                parent.set(str(dataname), str(data))
        else:
            if(data and dataname):
                parent.set(str(dataname), str(data))
        
        if(root):
            self.data_root = parent
        
        return parent

    def clear_log(self):
        open(self.output+".xml", "w").close()

    # Stores data in self.name".xml"
    def data_to_xml(self, data_root:object) -> None:
        if(self.directory): os.chdir(self.directory)
        
        for site_key, site_value in self.sites.items():
            self.store(data=site_value, dataname="times_visited", parent=site_key.get_parent())
        
        if(not data_root is None):
            self.data_tree._setroot(data_root)
            self.data_tree.write(f"{self.output}.xml", short_empty_elements=False)

    # Tries to interact with the tab to load dynamically-loaded data
    def load_site(self, removed_scroll:list=[], deep:int=0, first_scroll_steps:int=100) -> None:
        #Quan es passa removed_scroll?
        if(deep < 0):
            return -1 #to return true
        loaded = {}
        if (deep > 0):
            try:
                s_list = [element for element in self.find_in_website(["div", "pre"], By.TAG_NAME) if
                    element.value_of_css_property("overflow") in ["auto", "scroll", ""] and not element in removed_scroll]
                # ^ think add instead of reload
                loaded["Scrolls"] = -len(s_list)
                for scroll in s_list:  # Select & down arrow
                    if(not scroll):
                        logging.debug("Scroll None")
                        continue 

                    if(self.exec_js("if(arguments[0].scrollTop!=arguments[0].scrollTopMax "
                                    "|| arguments[0].scrollLeft!=arguments[0].scrollLeftMax)"
                                    "{return true}else{return false};", scroll)):
                        if(not self.exec_js("return arguments[0].scrollTop;", scroll)):
                            stepX_size = int(self.exec_js("return arguments[0].scrollLeftMax;", scroll)/first_scroll_steps) + 1
                            stepY_size = int(self.exec_js("return arguments[0].scrollTopMax;", scroll)/first_scroll_steps) + 1
                            for steps in range(1,first_scroll_steps+1):
                                self.exec_js(f"arguments[0].scroll({steps*stepX_size},"
                                    f"{steps*stepY_size});", scroll)
                        self.exec_js("arguments[0].scrollTo(arguments[0].scrollLeftMax,"
                                " arguments[0].scrollTopMax);", scroll)
                    elif(not scroll in removed_scroll):
                        logging.debug("Scroll loaded")
                        removed_scroll.append(scroll)
                        loaded["Scrolls"] += 1
            except Exception as err:
                logging.error(err)
        
        if (not "Main" in removed_scroll and deep >= 0):
            loaded["Main"] = -1
            if(self.exec_js("return window.scrollY+window.innerHeight!=this.document.body.scrollHeight;")):
                self.exec_js("window.scrollTo(0, document.body.scrollHeight);")
            else:
                removed_scroll.append("Main")
                loaded["Main"] = 0
        
        logging.debug(loaded)
        if(len(loaded) and any(loaded.values())):
            return removed_scroll
        return True

    # Runs script as a script in the current tab
    def exec_js(self, script:str, args:list=[None]):
        if(not type(args) is list or not type(args) is tuple): args = [args]

        return self.driver.execute_script(script, *args)

    ### GET (from site)

    def get_text(self, parent, site:str=None, dataname:str="text", info_as_node:bool=False, 
            keep_dom_nodes:bool=True, link:str=None) -> None:
        if(site):
            self.get_website(site)

        if(self.info_as_node or info_as_node): typ_e = dataname
        else: typ_e = None
        
        #time.sleep(self.time_wait_load)

        dom_nodes = self.exec_js("var el = document; var n, a=[],"
                        "walk=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,null,false);"
                        "while(n=walk.nextNode()){n = n.data.trim();if(n != '' && !n.endsWith(';') && !n.endsWith('>') "
                        "&& !n.endsWith('}')) a.push(n);} return a;")
        if(keep_dom_nodes):
            parent = self.store(typ_e=typ_e, data='', dataname=dataname, parent=parent)
            for txt_node in dom_nodes:                
                text = self.store(typ_e=f"sub{typ_e}", data=txt_node, dataname=dataname, parent=parent)
                if(link): self.store(data=link, dataname="link", parent=text)
        else:
            text = self.store(typ_e=typ_e, data='\n'.join(dom_nodes), dataname=dataname, parent=parent)
            if(link): self.store(data=link, dataname="link", parent=text)

    def get_images(self, parent, site=None, dataname="img", info_as_node=False, link:str=None) -> None:
        #I do write various functions so that people can run them in the do_if_condition
        if(site):
            self.get_website(site)
        
        if(self.info_as_node or info_as_node): typ_e = dataname
        else: typ_e = None
        
        images = self.find_in_website(["img"], By.TAG_NAME, site)
        
        if(len(self.images_known)):
            logging.info("Starting image comparison; This will take some time.")

            comparison = Image_manager().compare_images(self.images_known, 
                img_compare_encode([image.get_attribute("src") for image in images]))
            
            if(typ_e is None): datyp_e = None 
            else: datyp_e = "Img_analysis"
            
            logging.info("[+] Done")
        
        for image_num in range(len(images)):
            image_parent = self.store(typ_e=typ_e, data=images[image_num].get_attribute("src"), dataname=f"{dataname}_{image_num}", parent=parent)
            
            if(len(self.images_known)):
                for file_name,comp in comparison.items():
                    image_parent = self.store(typ_e=datyp_e, dataname=f"{file_name}_ssim", data=comp[image_num][0], parent=image_parent)
                    img = self.store(typ_e=None, dataname=f"{file_name}_mse", data=comp[image_num][1], parent=image_parent)
                    if(link): self.store(data=link, dataname="link", parent=img)

    def get_source(self, parent:object, site=None, info_as_node:bool=False, link:str=None) -> None:
        if(site): self.get_website(site)
        
        if(self.info_as_node or info_as_node): typ_e = "Source"
        else: typ_e = None

        source = self.store(typ_e=typ_e, data=self.driver.page_source, dataname="innerHTML", parent=parent)
        if(link): self.store(data=link, dataname="link", parent=source)

    def get_iframes(self, parent:object, site=None, dataname:str="iframe", info_as_node:bool=False, link:str=None) -> None:
        if(site):
            self.get_website(site)

        if(self.info_as_node or info_as_node): typ_e = dataname
        else: typ_e = None
        
        for iframe in self.find_in_website(["iframe"], By.TAG_NAME, site):
            ifr = self.store(typ_e=typ_e, data=iframe.get_attribute("src"), dataname=dataname, parent=parent)
            if(link): self.store(data=link, dataname="link", parent=ifr)

    # Close the browser
    def close(self) -> None:
        logging.info(f"Closing {self.name} (created in {self.time_created})")
        self.driver.quit()
        del self

    def test(self):
        print("do_something()")

class Site(object):
    """
    Site objects are all sites the crawler is visiting
    """
    def __init__(self, link:str="", tab:str="", removed_scroll:list=[],
                hrefs:list=[], buttons:list=[], depth:int=0, parent:object=None, 
                timeout:int=0):
        self.link = link
        self.hrefs = hrefs
        self.depth = depth
        self.parent = parent
        self.timeout = timeout
        self.tab = tab
        self.removed_scroll = removed_scroll
        self.buttons = buttons

    def __repr__(self) -> str:
        return f"<class 'main'.Site, depth={self.depth}, link='{self.link}', tab='{self.tab}'>"

    ### SET

    def set_removed_scroll(self, removed_scroll:list) -> None:
        self.removed_scroll = removed_scroll

    def set_timeout(self, timeout:int) -> None:
        self.timeout = timeout

    def set_hrefs(self, hrefs:list) -> None:
        self.hrefs = hrefs

    def set_parent(self, parent:object) -> None:
        self.parent = parent

    def set_link(self, link:str) -> None:
        self.link = link

    def set_buttons(self, buttons:list) -> None:
        self.buttons = buttons

    def set_tab(self, tab:str) -> str:
        self.tab = tab

    ### REMOVE
    
    def remove_from_hrefs(self, removed:str) -> int:
        self.hrefs.remove(removed)
        return len(self.hrefs)

    ### GET

    def get_tab(self) -> str:
        return self.tab

    def get_timeout(self) -> int:
        return self.timeout

    def get_removed_scroll(self) -> list:
        return self.removed_scroll

    def get_depth(self) -> int:
        return self.depth

    def get_parent(self) -> object:
        return self.parent

    def get_hrefs(self) -> list:
        return self.hrefs

    def get_link(self) -> str:
        return self.link

    def get_buttons(self) -> list:
        return self.buttons

    """buttons = property(get_buttons)
    link = property(get_link,set_link)
    hrefs = property(get_hrefs)
    parent = property(get_parent,set_parent)
    depth = property(get_depth)
    removed_scroll = property(get_removed_scroll)
    tab = property(get_tab, set_tab)
    timeout = property(get_timeout,set_timeout)"""

class Listener(AbstractEventListener):

    """ Non working user interactive browser for selecting buttons """

    def __init__(self, crawler:"Crawler"=None):
        self.recorded = []
        if(crawler is None): crawler = Crawler("learn",learning=True)
        self.crawler = crawler

    def after_click(self, element, driver):
        print(element)
        #if(self.recording): self.recorded.append(element)
        if(not driver.find_element(By.ID, "selenium_button_menu")):
            self.new_tab_menu()

    def new_tab_menu(self):
        self.crawler.exec_js(
                """var added = document.createElement('div'), place = document.body || document.getElementsByTagName('body')[0];
                added.style='position:fixed;width:200px;height:200px;top:110px;right:10px;padding:16px;border:2px solid #000000;z-index:100;background-color:#E5E4D7;'
                added.innerHTML = 'Record <label class="switch"><input typ_e="checkbox"><span class="slider round"></span></label>';
                added.id = 'selenium_button_menu'
                place.appendChild(added);""")

# TESTS
if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(levelname)s | %(message)s", level=logging.INFO)

                        #,images_known=["test.jpg"])#

    #crawler1.get_website("https://www.skyscanner.net/transport/flights-from/vlc/1905212/190219/?adults=1&children=0&adultsv2=1&childrenv2=&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home",)
    #crawler1.classify_buttons()
    for page in range(3):
        crawler1 = Crawler("c2", timeout_load=5, time_wait=1.5, info_as_node_xml=True, timeout_seconds=20)#,

        crawler1.output = f"c2_g{page}"
        try:
            crawler1.crawl(max_depth=1, load_amount=1, max_tabs=12, autosave=10, 
                    forbidden_domains=["duckduckgo.com","twitter.com","accounts.google.com", "spreadprivacy.com",
                                        "donttrack.us", "www.reddit.com", "reddit.com", "disqus.com", "facebook.com",
                                        "google.com","help.duckduckgo.com","support.google.com","www.google.com",
                                        "www.pinterest.es","www.pinterest.com","pinterest.es","pinterest.com",
                                        "translate.google.com","webcache.googleusercontent.com","about.google"
                                        "policies.google.com"],
                    record_text=True, record_img=False, record_source=False, record_iframes=False,
                    site=f"https://www.google.com/search?q=cork+material&client=firefox-b-d&ei=CczrXYqLHMOflwTUpaDIBA&start={page}0&sa=N&ved=2ahUKEwjKs-3Q86PmAhXDz4UKHdQSCEkQ8tMDegQIEBAw&biw=1366&bih=693")
                    #site="https://www.instagram.com/instagram")
        except NoSuchWindowException:    
            crawler1.data_to_xml(crawler1.data_root)

    # ,condition="True",do_if_condition="""while(True): self.exec_js(\"\"\"document.querySelector("[class='browse-list-category']").click()\"\"\")""")
    # ,condition="'https://www.instagram.com/p/' in self.driver.current_url", do_if_condition="self.exec_js(\"\"\"document.querySelector(\"[class=\'dCJp8 afkep coreSpriteHeartOpen _0mzm-\']\").click();\"\"\")")
        crawler1.close()
