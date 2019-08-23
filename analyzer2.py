#Import
import xml.etree.ElementTree as ET
import threading
import sys
import itertools
import os
from string import punctuation
from collections import defaultdict


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
            #Not working    
            elif(search[1] is True): 
                self.analizer.add_to_result("True",{search[3]:[search[2],[0]]})    
                continue
            position = search[2].find(search[1])
            result = []
            while (position >= 0):
                result.append(position)
                position = search[2].find(search[1],position+1)
            if(len(result)):
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
    def add_to_result(self, key:str, to_add) -> None:
        if(not key in self.result.keys()): self.result[key] = []
        self.result[key].append(to_add)   

    # Returns the data analized
    def get_result_raw(self) -> dict:
        return self.result

    # returns the position of the words in each found text
    # thought of to be used by a programmer
    def get_result(self) -> list:
        result = []
        for places in self.result.items():
            for place in places[1]:
                result.append(list(place.items())[0][1][1])
        return result

    # returns the result word and some next and before based on its arguments
    def get_result_word(self, words_before=1, words_after=1) -> dict:
        result = defaultdict(lambda : [])
        words_before, words_after = abs(words_before), abs(words_after)
        for search,places in self.result.items():
            if(search == "True"):
                result[search] = [place[0].split() for place_dict in places for place in place_dict.values()]
                continue

            for place_dict in places:
                for place in place_dict.values():
                    words = place[0].split()
                    word_index = str(words)[:str(words).find(search)].count(',')
                    result[search].append(words[word_index-words_before if word_index-words_before > 0 else 0 : 
                                            word_index+words_after + 1 if word_index + words_before + 1 < len(words) else len(words)])
        return result

    # {search: {obj: [text, result]}}
    def print_result(self, bef_margin:int=10, aft_margin:int=30) -> None:
        for search, places in self.result.items():
            print(f" - [{search}]")
            num = 0
            for place in places:
                found = list(place.items())[0]
                text, positions = found[1]
                for pos in positions:
                    print(f"\n[{num}] {text[pos-bef_margin:pos+aft_margin]}")
                    num += 1

    # Saves the complete info into a .txt file
    def save_result(self, file_output, words_before:int=1, words_after:int=1) -> None:
        words_dict = self.get_result_word(words_before, words_after)
        for search, places in self.result.items():
            file_output.write(f"\n\n###[{search}] \n\n")
            num = 0
            
            for place_num, place in enumerate(places):
                found = list(place.items())[0]
                text, positions = found[1]
                tag = found[0].tag
                words = words_dict[search][place_num]
                if(search != "True"):
                    word_index = str(words)[:str(words).find(search)].count(',')
                for pos in positions:
                    pos_before = text[:pos][::-1].find(words[0][::-1])+len(words[0]) if search != "True" and word_index-words_before >= 0 else 0
                    pos_after = text[pos:].find(words[-1])+len(words[-1])+1 if search != "True" and word_index+words_after < len(text) else len(text)
                    file_output.write(f"[{num}] [{tag}] "
                            f"{text[0 if pos_before < 0 else pos_before : len(text) if pos_after < 0 else pos_after]}"
                            " \n\n")
                    num += 1

    # Syntetizes the info given by save_result into a more human-friendly file
    def result_statistics(self, file_output, most_common_num:int=10, words_before:int=0, words_after:int=0) -> None:
        print("Starting file statistics")
        for search, places in self.result.items():
            file_output.write(f"\n\n###[{search}]")
            words = self.get_result_word(words_before, words_after)[search]
            places,words = zip(*[(place,word) for place,word in sorted(zip(places,words), 
                        key=lambda kw: len(kw[1]),
                        reverse=True)])
            words_freq_list = []
            words_freq = {}

            for obj_num in range(len(places)):
                words_freq_list.append({})
                for word in words[obj_num]:
                    if(not word in words_freq.keys()):
                        words_freq[word] = 1
                    else:
                        words_freq[word] += 1

                    if(not word in words_freq_list[-1].keys()):
                        words_freq_list[-1][word] = 1
                    else:
                        words_freq_list[-1][word] += 1

            file_output.write("\n   Number of coincidences\n")
            for obj_num in range(len(places)):
                tag,info = list(list(places[obj_num].keys())[0].attrib.items())[0]
                file_output.write(f" - - obj_{obj_num}({tag}:'{info[:20]}') has {len(words[obj_num])} items.\n")

            file_output.write("\n    Most frequent coincidences:\n")
            for word, times in sorted(words_freq.items(), key=lambda kv: kv[1], reverse=True)[:most_common_num]:
                file_output.write(f"     {word} : {times}\n")

            file_output.write("\n    Words:\n")
            for obj_num in range(len(places)):
                tag,info = list(list(places[obj_num].keys())[0].attrib.items())[0]
                file_output.write(f"\n - - obj_{obj_num}({tag}:'{info[:20]}'):\n")
                for word, times in sorted(words_freq_list[obj_num].items(), key=lambda kv: kv[1], reverse=True):
                    file_output.write(f"      {word} : {times}\n")

    # Using the result index info, retrieve full info from the .txt file
    def retrieve_from_code(self, search:str=None, num:int=None):
        while(search is None):
            print(f"Valid search keywords: {', '.join(self.result.keys())}")
            search = input("Please insert the search keyword: ")
            if(not search in self.result.keys()): 
                search = None

        while(num is None):
            print(f"Valid numbers: 0-{len(self.result[search])-1}")
            try:
                num = int(input("Please insert the number you want to retrieve: "))
            except: continue

            if(not abs(num) < len(self.result[search])): 
                num = None

        print(f"\n\nSelected '{search}' number {num}:\n")
        for retrieved in self.result[search][num].values():
            print(retrieved[0], end="\n\n")

if __name__ == "__main__": #I'll move this to a function to improve speed
    file_dir = __file__[:-len("analyzer2.py")]
    os.chdir(file_dir) 
    filename = "c1.xml"
    file = ET.parse(filename)
    root = file.getroot()
    search_in = root #Search starting point
    search = {"fembed":{"iframe":["*"]}} #Debug
    f = Analizer(search, search_in, 8)
    f.save_result(open(filename.replace(".xml",".txt"),"w"))
    f.result_statistics(open(filename.replace(".xml",".stats"),"w"))