5#Import
import xml.etree.ElementTree as ET
import threading
import sys
import itertools


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
                objs = search_in.findall(tag)
                for obj in objs:
                    if("*" in attrs):
                        for value in obj.attrib.values():
                            fin.append([tag, searching, value, obj])
                        continue
                    for attr in attrs:
                        if(attr in obj.attrib.keys()):
                            fin.append([tag, searching, obj.attrib[attr], obj])

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
                    print("".join([f"[{num}] {text[pos-bef_margin:pos+aft_margin]}"]))
                    num += 1

if __name__ == "__main__":
    file = ET.parse("c1.xml")
    root = file.getroot()
    search_in = root #Search starting point
    search = {"/static/images/":{"*":["*"]},"ins":{"site":["link","text"],"text":["link","text"]}} #Debug
    f = Analizer(search, search_in, 8)
    f.print_result()

# Bugs
# Doesn't find in "*"
# Creates random threads