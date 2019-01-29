5#Import
import xml.etree.ElementTree as ET
import threading
import sys
import itertools
import os


# Thread create and run with treading module
class Search_thread(threading.Thread):
    # Init sets up the thread´s future work
    def __init__(self, search_list:list, analizer:object):
        threading.Thread.__init__(self)
        self.search_list = search_list
        self.analizer = analizer

    # Run gets executed by threading when the program runs 
    # thread.start()
    def run(self):
        # search = [tag, search, text, obj]
        for search in self.search_list:
            if(search is None): break
            position = search[2].find(search[1])
            result = []
            while (position >= 0):
                result.append(position)
                position = search[2].find(search[1],position+1)
            self.analizer.add_to_result(search[1],{search[3]:[search[2],result]})
            # {search: {obj: [text, result]}}


# Analizer class
class Analizer(object):
    # Init Analizer object to create {threads} threads
    # and analize the ET(from .xml) file given
    def __init__(self, search:dict, search_in, threads:int=1):
        self.result = {}
        threads_list = []

        # May need improvements and to fix the max threads
        for searching in self.format_data(search,search_in,threads):
            threads_list.append(Search_thread(searching,analizer=self))
            
        print(f"Starting {len(threads_list)} thread{'s' if len(threads_list) != 1 else ''}.") 
        ended = 0

        # Run threads
        for thread in threads_list:
            thread.start()
            thread.join()
            ended += 1
            print(f"Ended: {ended}/{len(threads_list)}       ", end="\r")
        print("All threads ended sucessfully")

    # Basically finds all strings in tag&attr
    # and returns the tag, the what's being searched,
    # the string itself and the object containing it,
    # splitting it in {threads} parts
    def format_data(self, search:dict, search_in, threads:int):
        fin = []
        for (searching,search_dict) in search.items():
            for (tag,attrs) in search_dict.items():
                objs = []
                if(tag == "*"):
                    objs = search_in.findall(".//*")
                else:
                    if("*" in attrs):
                        objs = search_in.findall(f".//{tag}")
                    else:
                        for attr in attrs:
                            objs.extend(search_in.findall(f".//{tag}[@{attr}]"))
                for obj in objs:
                    for value in obj.attrib.values():
                        fin.append([tag, searching, value, obj])

        return itertools.zip_longest(*[iter(fin)]*threads, fillvalue=None)

    # As the threads run in parallel they don't returnlen(threads_list)
    # the data as it would overwritte, so i execute this
    # function and save the data asynclly
    def add_to_result(self, key:str, to_add):
        if(not key in self.result.keys()): self.result[key] = []
        self.result[key].append(to_add)   

    # Returns the data analized
    def get_result_raw(self):
        return self.result

    def get_result(self):
        return 

    # {search: {obj: [text, result]}}
    def print_result(self, bef_margin=10, aft_margin=30):
        for search, places in self.result.items():
            print(f" - [{search}]")
            num = 0
            for place in places:
                found = list(place.items())[0]
                text, positions = found[1]
                for pos in positions:
                    print(f"[{num}] {text[pos-bef_margin:pos+aft_margin]} \n")
                    num += 1

    def save_result(self, file, bef_margin=20, aft_margin=40):
        for search, places in self.result.items():
            file.write(f" - [{search}]")
            num = 0
            for place in places:
                found = list(place.items())[0]
                text, positions = found[1]
                tag = found[0].tag
                for pos in positions:
                    file.write(f"[{num}] [{tag}] {text[pos-bef_margin:pos+aft_margin]} \n")
                    num += 1

if __name__ == "__main__": #I'll move this to a function to improve speed
    file_dir = __file__[:-len("analyzer2.py")]
    os.chdir(file_dir) 
    filename = "c1.xml"
    file = ET.parse(filename)
    root = file.getroot()
    search_in = root #Search starting point
    search = {"fvlc":{"img":["*"]},"ins":{"site":["link","text"],"text":["link","text"]},"@":{"*":["text"]}} #Debug
    f = Analizer(search, search_in, 8)
    f.save_result(open(filename.replace(".xml",".txt"),"a"))

# Bugs
# Doesn't find in "*"
# Creates random threads