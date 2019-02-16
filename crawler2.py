#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import 
import getpass
import time
import os
import xml.etree.ElementTree as ET
# import imageio Save as file
from skimage import img_as_float, data
from skimage.io import imread
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium import webdriver
from image_manager import Image_manager
#import _thread
from sys import argv

class Crawler(object):
    """
    Despite its name, the crawler object is a browser site manager, with
    the ability to crawl from any site it's allowed
    """
    def __init__(self, crawler_name:str, output:str=None,timeout:float=20, time_wait:float=1.5, 
                info_as_node_xml:bool=False, tabs_per_window:int=1000, images_to_find:list=[],
                http_proxy:str=None, ftp_proxy:str=None, ssl_proxy:str=None, socks_proxy:str=None,
                load_images:bool=True, headless:bool=False, rem=False):
        try:
            
            firefox_capabilities = DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True
            firefox_capabilities["dom.popup_maximum"] = tabs_per_window

            options = webdriver.firefox.options.Options()
            options.set_preference("browser.popups.showPopupBlocker",False)
            if(headless):
                options.set_headless()
            
            binary = FirefoxBinary()

            profile = webdriver.FirefoxProfile()
            del profile.DEFAULT_PREFERENCES['frozen']["browser.link.open_newwindow"]
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
            profile.set_preference("browser.display.use_system_colors", True)
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

            if(not load_images):
                profile.set_preference("permissions.default.image", 2)

            if(not http_proxy is None): 
                webdriver.DesiredCapabilities.FIREFOX['proxy']['httpProxy'] = http_proxy
            if(not ftp_proxy is None): 
                webdriver.DesiredCapabilities.FIREFOX['proxy']['ftpProxy'] = ftp_proxy
            if(not ssl_proxy is None): 
                webdriver.DesiredCapabilities.FIREFOX['proxy']['sslProxy'] = ssl_proxy
            if(not socks_proxy is None):
                profile.set_preference("network.proxy.type", 1)
                profile.set_preference("network.proxy.socks", socks_proxy[:socks_proxy.find(":")])
                profile.set_preference("network.proxy.socks_port", int(socks_proxy[socks_proxy.find(":")+1:]))

            self.driver = webdriver.Firefox(executable_path=(
                    __file__).replace("crawler2.py", "geckodriver"),
                    options=options, firefox_binary=binary, firefox_profile=profile)
        except Exception as ex:
            print("\n")
            print(ex)
            print("\n")
            self.driver = webdriver.Firefox()

        self.directory = (__file__)[:-len("crawler2.py")]
        os.chdir(self.directory)

        self.name = str(crawler_name)

        if(output is None): output = crawler_name
        self.output = output

        self.visited_sites = {}
        self.visited_domain = {}

        self.data_tree = ET.ElementTree()
        self.data_root = None

        self.timeoutsec = timeout
        self.time_wait_load = time_wait

        self.tabs_per_window = tabs_per_window

        self.removelater = rem

        self.processing_tabs = []
        self.loaded_sites = []
        self.sites = {}

        self.info_as_node = info_as_node_xml

        self.images_to_find = dict([(name,img_as_float(imread(name))) for name in images_to_find])
        
        print(f"New crawler ({self.name}) created.")

    def __repr__(self) -> str:
        return f"<class '__main__'.Crawler, name='{self.name}', loaded {len(self.loaded_sites)} sites>"

    # Loads a new site in the current tab
    def get_website(self, site=None, parent=None, depth:int=0) -> None:
        if(site):
            self.driver.get(site)
            if(parent is None):
                parent = self.store(
                    type="site", data=self.driver.current_url, dataname="link", root=True)
            self.processing_tabs.append(Site(link=site, tab=self.driver.current_window_handle,
                                             hrefs=self.get_new_sites(), depth=depth, parent=parent, timeout=-1))
            self.sites[self.processing_tabs[-1]] = depth

        print(f"Trying to get site: {site}")
        if(not self.removelater and False):
            self.removelater = input()
        self.current_domain = self.exec_js("return document.domain")

        if(self.driver.current_url in self.visited_sites.keys()):
            self.visited_sites[self.driver.current_url] += 1
        else:
            self.visited_sites[self.driver.current_url] = 1

        if(self.current_domain in self.visited_domain.keys()):
            self.visited_domain[self.current_domain] += 1
        else:
            self.visited_domain[self.current_domain] = 1

        print("[+]Site opened successfully!")

    # Loads and manages recursivelly all sites it can find
    def crawl(self, site=None, max_depth:int=1, load_amount:int=-1, max_tabs:int=5,
            record_text:bool=False, record_img:bool=False, record_source:bool=False,
            condition:str=None, do_if_condition:str=None, recrawl:bool=False, 
            autosave:bool=False, record_depth:bool=True) -> None:

        if(site):
            self.get_website(site)

        if(max_tabs > max_depth):
            #num tabs must be at least equal to max depth being opened
            #but max_depth starts at 0.
            try:
                while(len(self.processing_tabs)):
                    # Open needed tabs
                    while(len(self.driver.window_handles) < max_tabs and len([site_value for (site_key, site_value) in self.sites.items() if site_value < max_depth and len(site_key.get_hrefs()) and not site_key in self.loaded_sites])):
                        site = [site_key for (site_key, site_value) in sorted(self.sites.items(), key=lambda x: x[1], reverse=True) if site_value < max_depth and len(site_key.get_hrefs())][0]
                        
                        self.driver.switch_to.window(site.get_tab())
                        
                        site.set_hrefs([new for new in self.get_new_sites() if not new.get_attribute("href") in self.visited_sites.keys()])
                        link = site.get_hrefs()[0]
                        link_href = link.get_attribute("href")
                        if(not link_href in self.visited_sites.keys()):
                            self.visited_sites[link_href] = 1  # Just in case redirect
                            site.remove_from_hrefs(link)  # Only useful when last href
                        
                        parent = self.store(
                            type="site", data=link_href, dataname="link", root=False, parent=site.get_parent())
                        
                        self.goto_new_site(
                            link=link_href, depth=site.get_depth(), parent=parent)
                        
                        print(f"Loaded tab number {len(self.driver.window_handles)}")
                    try:  # To free up memory IF went into the while
                        del link, link_href, site, parent
                    except: pass


                    # Load all tabs
                    if(load_amount >= 0):
                        to_remove = []
                        
                        for site in self.processing_tabs:  # Last tab opened does not load
                            if(not site.get_timeout() >= self.timeoutsec):
                                
                                self.driver.switch_to.window(site.get_tab())
                                
                                loaded_before = site.get_removed_scroll()[:]
                                loaded = self.load_site(
                                    removed_scroll=loaded_before, deep=load_amount)
                                
                                if(loaded.__class__.__name__ == "list" and site.get_timeout() < self.timeoutsec):
                                    if(len(loaded) > len(loaded_before) and not site.get_depth == max_tabs):
                                        print("Restarted timeout!")
                                        site.set_timeout(0)
                                    
                                    site.set_removed_scroll(loaded[:])
                                elif(not len(site.get_hrefs()) or (site.get_depth() == max_depth and site.get_timeout() > 0)):
                                    # Has the site loaded entirely? If the site depth is max_depth
                                    # the amount of href will never go down
                                    to_remove.append(site)
                                
                                site.set_timeout(site.get_timeout()+1)
                            
                                del loaded, loaded_before

                            if(not site in self.loaded_sites and (not len(site.get_hrefs()) or site.get_timeout() >= self.timeoutsec)):
                                if(not site in to_remove):
                                    to_remove.append(site)
                            # dont delete if got all links but not loaded
                            elif(site in self.loaded_sites and (not len(site.get_hrefs()) or site.get_depth() == max_depth or site.get_timeout() >= self.timeoutsec)):
                                # Actually delete marked tabs
                                if(site.get_timeout() >= self.timeoutsec):  # Remove later debug purpose
                                    print("Timeout >.<")
                                else:
                                    print("Site full loaded")
                                
                                if(condition and do_if_condition):
                                    if(eval(condition)):
                                        print("Do_if_condition: ", end="")
                                        print(eval(do_if_condition))
                                
                                self.processing_tabs.remove(site)
                                
                                self.driver.switch_to.window(site.get_tab())
                                
                                self.exec_js("window.close();")
                                
                                print(f"Closed depth {self.sites[site]} num {len(self.processing_tabs)} site \""
                                f"{site.get_link()}\" ({site.get_tab()}) with unopened {len(site.get_hrefs())} links")
                                
                                if(site in to_remove):
                                    to_remove.remove(site)
                                del self.sites[site]
                        
                        time.sleep(self.time_wait_load)
                    # Mark to remove loaded unnecessary tabs
                    if(len(to_remove) > 0):
                        for removing in to_remove:
                            try:  # Sometimes tab is closed but not removed form list
                                self.driver.switch_to.window(removing.get_tab())
                                
                                if(record_text):
                                    self.get_text(parent=removing.get_parent())
                                if(record_img):
                                    self.get_images(parent=removing.get_parent())
                                if(record_source):
                                    self.get_source(parent=removing.get_parent())
                                if(record_depth):
                                    if(self.info_as_node):
                                        type = "depth"
                                    else: type = None
                                    self.store(type=type, data=removing.get_depth(), dataname="depth", root=False, parent=removing.get_parent())
                                    del type

                                if(removing.get_depth()==max_depth):
                                    for link in removing.get_hrefs():
                                        try:
                                            self.store(type="site", data=link.get_attribute("href"), dataname="link", root=False, parent=removing.get_parent())
                                        except: continue

                                self.loaded_sites.append(removing)
                                
                                del removing
                            
                            except Exception as err:
                                print(err)
                    
                    if(autosave): self.data_to_xml(self.data_root)
            
            except Exception as err:
                print(err)
            
            self.data_to_xml(self.data_root)

    # Runs loads a new site and returns its hrefs
    def get_new_sites(self, site:str=None) -> list:
        # Later it will not only get hrefs
        if(site):
            self.get_website(site)

        final = self.find_in_website(["//a[@href]"], By.XPATH)
        return final

    # Given a list of buttons determines if it may cause data loss
    def classify_buttons(self) -> dict:
        print("Crawler.classify_buttons(self)")

        last = self.driver.current_window_handle

        self.goto_new_site(self.driver.current_url)

        a = self.find_in_website(["button"]) #"li","div"

        b = self.exec_js("return arguments[0].click",a)

        buttons = [self.exec_js("return 'click' in arguments[0]",button) for button in 
                    self.find_in_website(["button","li","div"])]

        classifies = {"loss":[],"kept":[],"links":[]}
        for button in range(len(buttons)-1): 
            clink = self.driver.current_url #click+link
            try:
                buttons[button].click()
                if(button):
                    classifies["kept"].append(buttons[button-1])
            except:
                if(button):
                    classifies["loss"].append(buttons[button-1])
                    classifies["links"].append(clink)
                self.driver.back()
                buttons[button].click()
        try:
            buttons[0].get_attribute("class")
            classifies["kept"].append(buttons[button])
        except:
            classifies["loss"].append(buttons[button])
        
        self.exec_js("window.close();")
        self.driver.switch_to.window(last)

        return classifies

    # Opens a new tab if possible and loads link
    def goto_new_site(self, link:str, depth:int=0, parent:object=None) -> None:
        # Later new tab and same tab buttons

        if(len(self.driver.window_handles) >= self.tabs_per_window):
            print("Multi-threading in a later version")
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
        
        final = []
        for searching in search:
            try:
                final += self.driver.find_elements(tag, searching)
            except:
                print(f"No element {searching} found")
        return final

    def store(self, type:str=None, data:str=None, dataname:str=None,
                parent:object=None, root:object=False) -> object:
        #print(f"Stored: \"{data}\"")
        if(type):
            if(parent is None):
                parent = ET.Element(type)
            else:
                parent = ET.SubElement(parent, str(type))
            
            if(data and dataname):
                parent.set(str(dataname), str(data))
        else:
            if(data and dataname):
                parent.set(str(dataname), str(data))
        
        if(root):
            self.data_root = parent
        
        return parent

    def clear_log(self):
        open(self.output+".xml", "w")

    # Stores data in self.name".xml"
    def data_to_xml(self, data_root:object) -> None:
        os.chdir(self.directory)
        
        for site_key, site_value in self.sites.items():
            self.store(data=site_value, dataname="times_visited", parent=site_key.get_parent())
        
        if(not data_root is None):
            self.data_tree._setroot(data_root)
            self.data_tree.write(f"{self.name}.xml", short_empty_elements=False)

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
                        print("Scroll None")
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
                    else:
                        print("Scroll loaded")
                        removed_scroll.append(scroll)
            except Exception as err:
                print(err)
        
        if (not "Main" in removed_scroll and deep >= 0):
            loaded["Main"] = -1
            if(self.exec_js("return window.scrollY+window.innerHeight!=this.document.body.scrollHeight;")):
                self.exec_js("window.scrollTo(0, document.body.scrollHeight);")
            else:
                removed_scroll.append("Main")
                loaded["Main"] = 0
        
        print(loaded)
        if(len(loaded) and any(loaded.values())):
            return removed_scroll
        return True

    # Runs script as a script in the current tab
    def exec_js(self, script:str, args:list=None):
        return self.driver.execute_script(script, args)

    ### GET (from site)

    def get_text(self, parent, site=None, dataname="text", info_as_node=False) -> None:
        if(site):
            self.get_website(site)

        if(self.info_as_node or info_as_node): type = dataname
        else: type = None
        
        for txt in self.find_in_website(["body"], By.TAG_NAME, site):
            self.store(type=type, data=txt.text, dataname=dataname, parent=parent)

    def get_images(self, parent, site=None, dataname="img", info_as_node=False) -> None:
        #I do write various functions so that people can run them in the do_if_condition
        if(site):
            self.get_website(site)
        
        if(self.info_as_node or info_as_node): type = dataname
        else: type = None
        
        images = self.find_in_website(["img"], By.TAG_NAME, site)
        
        if(len(self.images_to_find)):
            print("Starting image comparison; This will take some time.")
            
            images_data = [img_as_float(imread(image.get_attribute("src")))for image in images]
            comparison = Image_manager().compare_images(self.images_to_find, images_data)
            
            if(type is None): datype = None 
            else: datype = "Img_analysis"
            
            print("[+] Done")
        
        for image_num in range(len(images)):
            image_parent = self.store(type=type, data=images[image_num].get_attribute("src"), dataname=f"{dataname}_{image_num}", parent=parent)
            
            if(len(self.images_to_find)):
                for file_name,comp in comparison.items():
                    image_parent = self.store(type=datype, dataname=f"{file_name}_ssim", data=comp[image_num][0], parent=image_parent)
                    self.store(type=None, dataname=f"{file_name}_mse", data=comp[image_num][1], parent=image_parent)

    def get_source(self, parent:object, site=None, info_as_node:bool=False) -> None:
        if(site): self.get_website(site)
        
        if(self.info_as_node or info_as_node): type = "Source"
        else: type = None
        
        self.store(type=type, data=self.driver.page_source, dataname="code", parent=parent)

    # Close the browser
    def close(self) -> None:
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


# TESTS
crawler1 = Crawler("c1", timeout=10, time_wait=1.5, info_as_node_xml=True#,
                    ,images_to_find=[])#"test.jpg"
crawler1.clear_log()

#crawler1.get_website("https://www.skyscanner.net/transport/flights-from/vlc/190212/190219/?adults=1&children=0&adultsv2=1&childrenv2=&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home",)
#crawler1.classify_buttons()
crawler1.crawl(max_depth=0, load_amount=1, max_tabs=35, autosave=True,
            record_text=True, record_img=True, record_source=False,
            site="https://www.instagram.com/instagram")  
# ,condition="True",do_if_condition="""while(True): self.exec_js(\"\"\"document.querySelector("[class='browse-list-category']").click()\"\"\")""")
# ,condition="'https://www.instagram.com/p/' in self.driver.current_url", do_if_condition="self.exec_js(\"\"\"document.querySelector(\"[class=\'dCJp8 afkep coreSpriteHeartOpen _0mzm-\']\").click();\"\"\")")
crawler1.close()
