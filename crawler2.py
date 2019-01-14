#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import 
import getpass
import time
import os
import xml.etree.ElementTree as ET
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver

class Crawler(object):
    def __init__(self, crawler_name, user=None, passwd=None, timeout=20, time_wait=1.5, info_as_node_xml=False, rem=False):
        try:
            firefox_capabilities = DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True
            self.driver = webdriver.Firefox(executable_path=(
                __file__).replace("crawler2.py", "")+"geckodriver")
        except Exception as ex:
            print("\n \n")
            print(ex)
            print("\n \n")
            self.driver = webdriver.Firefox()
        self.name = str(crawler_name)
        self.visited_sites = {}
        self.visited_domain = {}
        self.data_tree = ET.ElementTree()
        self.data_root = None
        self.timeoutsec = timeout
        self.time_wait_load = time_wait
        self.userdomains = {}
        self.alldom = False
        self.removelater = rem
        self.processing_tabs = []
        self.loaded_sites = []
        self.sites = {}
        self.sites_by_tab = {}
        self.info_as_node = info_as_node_xml
        # Proxy
        print(f"New crawler ({self.name}) created.")

    def __repr__(self):
        return f"<class '__main__'.Crawler, name='{self.name}', site:\"{self.driver.current_url}\", loaded {len(self.loaded_sites)} sites>"

    def get_website(self, site=None, parent=None, depth=0):
        print(f"Crawler.get_website(self, {site}, {parent}, {depth})")
        if(site):
            self.driver.get(site)
            if(parent is None):
                parent = self.store(
                    type="site", data=self.driver.current_url, dataname="link", root=True)
            self.processing_tabs.append(Site(link=site, tab=self.driver.current_window_handle,
                                            depth=depth, parent=parent, timeout=-1))
            self.sites[self.processing_tabs[-1]] = depth
            self.sites_by_tab[self.driver.current_window_handle] = self.processing_tabs[-1]

        print("Trying to get site: {site}")
        if(not self.removelater and True):
            self.removelater = input()
        self.current_domain = self.exec_js("return document.domain")
        username = self.find_in_website("username", By.ID)
        password = self.find_in_website("password", By.ID)
        if(self.current_domain in self.userdomains.keys()):
            username.send_keys(self.userdomains[self.current_domain][0])
            password.send_keys(self.userdomains[self.current_domain][1])
            self.driver.find_element_by_name("submit").click()
        elif(self.alldom):
            username.send_keys(self.userdomains["*"][0])
            password.send_keys(self.userdomains["*"][1])
        if(self.driver.current_url in self.visited_sites.keys()):
            self.visited_sites[self.driver.current_url] += 1
        else:
            self.visited_sites[self.driver.current_url] = 1
        if(self.current_domain in self.visited_domain.keys()):
            self.visited_domain[self.current_domain] += 1
        else:
            self.visited_domain[self.current_domain] = 1
        print("[+]Site loaded successfully!")

    def crawl(self, site=None, max_depth=1, load_amount=-1, max_tabs=5, save_text=False, save_img=False, save_source=False, condition=None, do_if_condition=None, recrawl=False, autosave=False):
        print(f"Crawler.crawl(self, {site}, {max_depth}, {load_amount}, {max_tabs}, {save_text}, {save_img}, {save_source}, {condition}, {do_if_condition}, {recrawl}, {autosave})")
        if(site):
            self.get_website(site)
        if(max_tabs > max_depth):
            #num tabs must be at least equal to max depth being opened
            #but max_depth starts at 0.
            try:
                while(len(self.processing_tabs)):
                    # Open needed tabs
                    while(len(self.driver.window_handles) < max_tabs and len([site_value for (site_key, site_value) in self.sites.items() if site_value < max_depth and (len(site_key.get_hrefs())or len(site_key.get_buttons())) and not site_key in self.loaded_sites])):
                        site = [site_key for (site_key, site_value) in sorted(self.sites.items(), key=lambda x: x[1], reverse=True) if site_value < max_depth and len(site_key.get_hrefs())][0]
                        self.driver.switch_to.window(site.get_tab())
                        self.get_new_sites()
                        if(len(site.get_hrefs())):
                            #Hrefs
                            link = site.get_hrefs()[0]
                            link_href = link.get_attribute("href")
                            if(not link_href in self.visited_sites.keys()):
                                self.visited_sites[link_href] = 1  # Just in case redirect
                                site.remove_from_hrefs(link)  # Only useful when last href
                            parent = self.store(
                                type="site", data=link_href, dataname="link", root=False, parent=site.get_parent())
                            self.goto_new_site(
                                obj=link, type="href", depth=site.get_depth(), parent=parent)
                        elif(len(site.get_buttons())):
                            site.set_buttons([])
                        print(f"Loaded tab number {len(self.driver.window_handles)}")
                    try:  # To free up memory IF went into the while
                        del link, link_href, site, parent
                    except:
                        pass

                    # Load all tabs
                    if(load_amount >= 0):
                        to_remove = []
                        for site in self.processing_tabs:  # Last tab opened does not load
                            if(not site.get_timeout() >= self.timeoutsec):
                                self.driver.switch_to.window(site.get_tab())
                                loaded_before = site.get_removed_scroll()
                                loaded = self.load_site(
                                    removed_scroll=loaded_before, deep=load_amount)
                                if(loaded.__class__.__name__ == "list" and site.get_timeout() < self.timeoutsec):
                                    if(len(loaded) > len(loaded_before)):
                                        print("Restarted timeout!")
                                        site.set_timeout(0)
                                    else:
                                        site.set_timeout(site.get_timeout()+1)
                                    site.set_removed_scroll(loaded)
                                elif(not len(site.get_hrefs())):
                                    to_remove.append(site)
                            if(not site in self.loaded_sites and (site.get_depth() == max_depth or site.get_timeout() >= self.timeoutsec)):
                                to_remove.append(site)
                            # dont delete if got all links but not loaded
                            elif(site in self.loaded_sites and (not len(site.get_hrefs()) or site.get_depth() == max_depth)):
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
                                f"{site.get_link()}\" with {len(site.get_hrefs())} links left")
                                del self.sites[site]
                        time.sleep(self.time_wait_load)
                    # Mark to remove loaded unnecessary tabs
                    if(len(to_remove) > 0):
                        for removing in to_remove:
                            try:  # Sometimes tab is closed but not removed form list
                                self.driver.switch_to.window(removing.get_tab())
                                if(save_text):
                                    self.get_text(parent=removing.get_parent())
                                if(save_img):
                                    self.get_images(parent=removing.get_parent())
                                if(save_source):
                                    self.get_source(parent=removing.get_parent())
                                
                                if(removing.get_depth()==max_depth):
                                    for link in removing.get_hrefs():
                                        self.store(type="site", data=link.get_attribute("href"), dataname="link", root=False, parent=removing.get_parent())
                                self.loaded_sites.append(removing)
                                del removing
                            except Exception as err:
                                print(err)
                    if(autosave): self.data_to_xml(self.data_root)
            except Exception as err: #TMP replace autosave
                print(err)
            self.data_to_xml(self.data_root)

    def get_new_sites(self, site=None):
        print(f"Crawler.get_new_sites(self, {site})")
        # Later it will get buttons 
        if(site):
            self.get_website(site)
        else:
            site = self.sites_by_tab[self.driver.current_window_handle]
        hrefs = self.find_in_website(["//a[@href]"], By.XPATH)
        hrefs = [new for new in hrefs+[added for added in site.get_hrefs() if not added in hrefs] if not new.get_attribute("href") in self.visited_sites.keys()]
        buttons = self.find_in_website(["button"],By.TAG_NAME)
        buttons = self.classify_buttons([new for new in buttons+[added for added in site.get_buttons() if not added in buttons] if not new in site.get_accessed_buttons()])
        site.set_hrefs(hrefs)
        site.set_buttons(buttons)
        return {"hrefs":hrefs, "buttons":buttons}

    def goto_new_site(self, obj, type="href", depth=0, parent=None):
        print(f"Crawler.goto_new_sites(self, {obj}, {type}, {depth}, {parent})")
        # Later new tab and same tab buttons
        # print(self.driver.current_window_handle)
        if(type in ["href",""]):
            self.exec_js("window.open();")
            self.driver.switch_to.window(self.driver.window_handles[self.driver.window_handles.index(
            self.driver.current_window_handle)+1])
            self.get_website(site=obj.get_attribute("href"), depth=depth+1, parent=parent)

    def classify_buttons(self, buttons):
        print(f"Crawler.classify_buttons(self, {buttons})")
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
        return classifies



    def set_userpass(self, user, passwd, domains=None):
        # Not tested.
        self.alldom = False
        if(user.__class__.__name__ != "list"):
            user = [user]
        if(passwd.__class__.__name__ != "list"):
            passwd = [passwd]
        if(not domains):
            self.userdomains["*"] = (user[0], passwd[0])
            self.alldom = True
            return 1
        if(len(user) != len(passwd)):
            return -1
        if(domains.__class__.__name__ == "list"):
            for num in range(len(user)):
                try:
                    self.userdomains[domains[num]] = (user[num], passwd[num])
                except:
                    self.userdomains[domains[0]] = (user[num], passwd[num])
        else:
            self.userdomains[domains[0]] = (user[0], passwd[0])

    def find_in_website(self, search, tag=By.TAG_NAME, site=None):
        print(f"Crawler.find_in_website(self, {search}, {tag}, {site})")
        if(site):
            self.get_website(site)
        final = []
        for searching in search:
            try:
                final += self.driver.find_elements(tag, searching)
            except:
                print(f"No element {searching} found")
        return final

    def store(self, type=None, data=None, dataname=None, parent=None, root=False):
        print(f"Crawler.store(self, {type}, {data}, {dataname}, {parent}, {root})")
        print("Stored: \"" + str(data) + "\"")
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
        print("Crawler.clear_log(self)")
        open(self.name+".xml", "w")

    def data_to_xml(self, data_root):
        for site_key, site_value in self.sites.items():
            self.store(data=site_value, dataname="times_visited", parent=site_key.get_parent())
        if(not data_root is None):
            self.data_tree._setroot(data_root)
            self.data_tree.write(self.name+".xml", short_empty_elements=False)
        print(f"Visited {len(self.sites.values())+1} sites.")

    def load_site(self, removed_scroll=[], deep=0):
        print(f"Crawler.load_site(self, {removed_scroll}, {deep})")
        if(deep < 0):
            return -1 #return true
        loaded = {"Main": -1}
        if (not "Main" in removed_scroll and deep >= 0):
            if(self.exec_js("return window.scrollY+window.innerHeight!=this.document.body.scrollHeight")):
                self.exec_js("window.scrollTo(0, document.body.scrollHeight)")
            else:
                print("Main Scroll loaded")
                removed_scroll.append("Main")
                loaded["Main"] = 0
        if (deep > 0):
            try:
                #print([element.get_attribute("class") for element in self.find_in_website(["div", "pre"], By.TAG_NAME)])
                s_list = [element for element in self.find_in_website(["div", "pre"], By.TAG_NAME) if(
                    element.value_of_css_property("overflow") in ["auto", "scroll", ""] and not element in removed_scroll)]
                # ^ think add instead of reload
                #print("ex1" in [e.get_attribute("class") for e in self.find_in_website(["div", "pre"], By.TAG_NAME)]) #debug
                #print(len(self.find_in_website(["div", "pre"], By.TAG_NAME)))
                #print(self.find_in_website(["ex1","ex2","ex3","ex4"],By.CLASS_NAME))
                loaded["Scrolls"] = -len(s_list)
                for scroll in s_list:  # Select & down arrow
                    if(not scroll):
                        print("Scroll None")
                        continue 
                    #print("Scroll " + str(scroll.get_attribute("class"))+ " overflow: " + str(scroll.value_of_css_property("overflow")) + " result: " + str(self.exec_js("if(arguments[0].scrollTop!=arguments[0].scrollTopMax || arguments[0].scrollLeft!=arguments[0].scrollLeftMax){return true}else{return false};", scroll)))
                    if(self.exec_js("if(arguments[0].scrollTop!=arguments[0].scrollTopMax || arguments[0].scrollLeft!=arguments[0].scrollLeftMax){return true}else{return false};", scroll)):
                        self.exec_js(
                            "arguments[0].scrollTo(arguments[0].scrollLeftMax, arguments[0].scrollTopMax)", scroll)
                    else:
                        print("Scroll loaded")
                        removed_scroll.append(scroll)
            except Exception as err:
                print(err)
        if(any(loaded.values())):
            return removed_scroll
        return True

    def get_text(self, parent, site=None, dataname="text", info_as_node=False):
        print(f"Crawler.get_text(self, {parent}, {site}, {dataname}, {info_as_node})")
        if(site):
            self.get_website(site)
        if(self.info_as_node or info_as_node): type = dataname
        else: type = None
        for txt in self.find_in_website(["body"], By.TAG_NAME, site):
            self.store(type=type, data=txt.text, dataname=dataname, parent=parent)

    def get_images(self, parent, site=None, dataname="img", info_as_node=False):
        print(f"Crawler.get_images(self, {parent}, {site}, {dataname}, {info_as_node})")
        #I do write various functions so that people can run them in the do_if_condition
        if(site):
            self.get_website(site)
        if(self.info_as_node or info_as_node): type = dataname
        else: type = None
        images = self.find_in_website(["img"], By.TAG_NAME, site)
        for image_num in range(len(images)):
            self.store(type=type, data=images[image_num].get_attribute("src"), dataname=dataname+f"_{image_num}", parent=parent)

    def get_source(self, parent, info_as_node=False):
        print(f"Crawler.get_images(self, {parent}, {info_as_node})")
        if(self.info_as_node or info_as_node): type = "Source"
        else: type = None
        self.store(type=type, data=self.driver.page_source, dataname="code", parent=parent)

    def exec_js(self, script, args=None):
        print(f"Crawler.get_images(self, {script}, {args})")
        return self.driver.execute_script(script, args)

    def close(self):
        print(f"Crawler.close({self})")
        self.driver.quit()
        del self

    def test(self):
        print("do_something()")


class Site(object):
    def __init__(self, link="", tab="", removed_scroll=[], hrefs=[], buttons=[], depth=0, parent=None, timeout=0):
        self.link = link
        self.hrefs = hrefs
        self.buttons = buttons
        self.depth = depth
        self.parent = parent
        self.timeout = timeout
        self.tab = tab
        self.removed_scroll = removed_scroll
        self.accessed_buttons = []

    def __repr__(self):
        return f"<class 'main'.Site, depth={self.depth}, link='{self.link}', tab='{self.tab}'>"

    def set_removed_scroll(self, removed_scroll):
        self.removed_scroll = removed_scroll

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_hrefs(self, hrefs):
        self.hrefs = hrefs

    def set_buttons(self, buttons):
        self.buttons = buttons

    def set_parent(self, parent):
        self.parent = parent

    def set_link(self, link):
        self.link = link

    def set_accessed_buttons(self, accessed):
        self.accessed_buttons = accessed

    def get_tab(self):
        return self.tab

    def get_timeout(self):
        return self.timeout

    def get_removed_scroll(self):
        return self.removed_scroll

    def get_depth(self):
        return self.depth

    def get_parent(self):
        return self.parent

    def get_hrefs(self):
        return self.hrefs

    def get_buttons(self):
        return self.buttons

    def get_link(self):
        return self.link

    def get_accessed_buttons(self):
        return self.accessed_buttons

    def remove_from_hrefs(self, removed):
        self.hrefs.remove(removed)
        return len(self.hrefs)

    def add_to_hrefs(self, added):
        self.hrefs.append(added)

    def add_to_accessed_buttons(self, accessed):
        self.accessed_buttons.append(accessed)


# TESTS
crawler1 = Crawler("c1", timeout=10, time_wait=1.5, info_as_node_xml=True, rem=True)
crawler1.clear_log()
crawler1.crawl(max_depth=2, load_amount=1, max_tabs=50, autosave=True, save_text=False, save_img=False, save_source=False,
            site="https://www.instagram.com/instagram")  # ,condition="True",do_if_condition="""while(True): self.exec_js(\"\"\"document.querySelector("[class='browse-list-category']").click()\"\"\")""")
# ,condition="'https://www.instagram.com/p/' in self.driver.current_url", do_if_condition="self.exec_js(\"\"\"document.querySelector(\"[class=\'dCJp8 afkep coreSpriteHeartOpen _0mzm-\']\").click();\"\"\")")
# crawler1.test()
print(crawler1.get_new_sites())
input("Press any key to close: ")
crawler1.close()
