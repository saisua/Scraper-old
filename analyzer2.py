#Import
import xml.etree.ElementTree as ET
import threading
import sys
import itertools


# Thread create and run with treading module
class Search_thread(threading.Thread):
    # Init sets up the thread´s future work
    def __init__(self, search:str, search_tags, search_in, analizer):
        threading.Thread.__init__(self)
        self.search = search
        self.tag_obj = list(itertools.chain.from_iterable([search_in.findall(tag) for tag in search_tags]))
        self.search_tags = list(itertools.chain.from_iterable([list(find.attrib.values()) for find in self.tag_obj]))
        self.analizer = analizer

    # Run gets executed by threading when the program runs 
    # thread.start()
    def run(self):
        for search in range(len(self.search_tags)):
            position = self.search_tags[search].find(self.search)
            result = []
            while (position >= 0):
                result.append(position)
                position = self.search_tags[search].find(self.search,position+1)
            self.analizer.add_to_result(self.search,{self.tag_obj[search]:result})


# Analizer class
class Analizer(object):
    # Init Analizer object to create {threads} threads
    # and analize the ET(from .xml) file given
    def __init__(self, search:dict, search_in, threads:int=1):
        self.result = {}
        threads_list = []

        # May need improvements and to fix the max threads
        for searching in search.items():
            threads_list.append(Search_thread(searching[0],searching[1], search_in,self))
            
        print(f"Starting {len(threads_list)} threads.") 
        ended = 0
        for thread in threads_list: 
            thread.start()
            thread.join()
            ended += 1
            print(f"Ended: {ended}       ", end="\r")
        print("All threads ended sucessfully")

    # As the threads run in parallel they don't return
    # the data as it would overwritte, so i execute this
    # function and save the data asynclly
    def add_to_result(self, key:str, to_add):
        if(not key in self.result.keys()): self.result[key] = []
        self.result[key].append(to_add)   

    # Returns the data analized
    def get_result(self):
        return self.result


if __name__ == "__main__":
    file = ET.parse("c1.xml")
    root = file.getroot()
    search_in_keys = ["link","text"] #Debug
    if(len(search_in_keys)):
        search_in = root #Search starting point
        search = {"ins":["site","text"]} #Debug
        f = Analizer(search, search_in, 8).get_result()
        print(f)
        print("[R]",end=" ")
        print("\n[R] ".join([(list(c.attrib.values())[0][e-5:e+500]) for a in f.values() for b in a for c,d in b.items() for e in d]))
        # This crappy line represents what the program is supposed to do
        # It will later be a function