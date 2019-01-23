import xml.etree.ElementTree as ET
import threading
import sys

class Search_thread(threading.Thread):
    def __init__(self, search:str, search_in:dict, analizer):
        threading.Thread.__init__(self)
        self.search = search
        self.search_in = list(search_in.values())
        self.search_name = list(search_in.keys())
        self.analizer = analizer

    def run(self):
        for num in range(len(self.search_in)):
            position = self.search_in[num].find(self.search)
            print(position) #Delete debug
            result = []
            while (position >= 0):
                result.append(position)
                position = self.search_in[num].find(self.search,position+1)
            self.analizer.add_to_result(self.search_name[num],result)

class Analizer(object):
    def __init__(self, search:str, search_in:dict, threads:int=1):
        print("Analizer initing")
        if(len(search_in)<threads):
            threads = len(search_in)
        part_size = len(search_in)/threads
        search_in_part = dict([search_in.items()[int(part_size*thread_num):int(part_size*(thread_num+1))] for thread_num in range(threads)])
        threads_list = [Search_thread(search,search_in_part.items()[thread_num],self) for thread_num in range(threads)]
        self.result = {}
        print(f"Starting threads {threads_list}")
        for thread in threads_list: 
            thread.start()
            thread.join()

    def add_to_result(self, key:str, to_add):
        self.result[key] = to_add
        
    def get_result(self):
        return self.result

if __name__ == "__main__":
    file = ET.parse("c1.xml")
    root = file.getroot()
    search_in = root.attrib
    search_in_keys = ["link","text"]
    if(len(search_in_keys)):
        search_in = dict([(in_key, in_val) for (in_key, in_val) in root.])
    #I need to think in a way to pass the key, value and obj

    #print(Analizer("long", open("test.txt","r").read(), 1).get_result())