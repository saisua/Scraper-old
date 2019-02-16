from skimage.measure import compare_ssim as ssim
from skimage.measure import compare_mse as mse
from skimage import img_as_float, data
from skimage.io import imread
from skimage.transform import resize
import threading
import itertools

class Image_thread(threading.Thread):
    def __init__(self, manager:object, args:dict={}):
        threading.Thread.__init__(self)
        self.function = None
        self.args = args
        self.manager = manager

    def run(self):
        if(self.function is None): raise ValueError("Function is not set")
        self.function(**self.args)

            # Determines if two images are similar
    def compare_images(self, data_list) -> tuple:
        result = []
        if(None in data_list):
            data_list = data_list[:data_list.index(None)]
        for given,unknown in data_list:
            dimensions_difference = (given.shape[0]/unknown.shape[0],
                                    given.shape[1]/unknown.shape[1])
            if(dimensions_difference[0] > 1):
                unknown = resize(unknown, (unknown.shape[0]*dimensions_difference[0],unknown.shape[1]), 
                            anti_aliasing=True)
            else:
                given = resize(given, (given.shape[0]*dimensions_difference[0],given.shape[1]), 
                            anti_aliasing=True)
            if(dimensions_difference[1] > 1):
                unknown = resize(unknown, (unknown.shape[0],unknown.shape[1]*dimensions_difference[1]), 
                            anti_aliasing=True)
            else:
                given = resize(given, (given.shape[0],given.shape[1]*dimensions_difference[1]), 
                            anti_aliasing=True)
            m = mse(given, unknown)
            s = ssim(given, unknown, multichannel=True)
            result.append((abs(s-1)/2,m))
        self.manager.add_result(result)

    def set_function(self, function) -> None:
        self.function = function

    def set_args(self, args) -> None:
        self.args = args

class Image_manager(object):
    def __init__(self, threads:int=100):
        self.threads = threads
        self.result = []
        self.thread_list = []

    def format_data(self,data_list:list)->list:
        if(len(data_list)<(self.threads-1)):
            elements_per_tread = 1
        else:
            elements_per_tread = len(data_list)/(self.threads-1)

        print("[+] formatting done")
        return list(itertools.zip_longest(*[iter(data_list)]*int(elements_per_tread), fillvalue=None))

    def add_result(self, result) -> list:
        self.result.append(result)

    def reset(self) -> None:
        self.result = []
        self.thread_list = []

    def compare_images(self, given_dict:dict, unknown_list:list) -> dict:
        self.reset()
        fin = {}
        for name,given in given_dict.items():
            data = [[given,unknown] for unknown in unknown_list]
            f_data = self.format_data(data)

            #Run threads
            ended = 0
            print(f"Starting {len(f_data)} thread{'s' if len(f_data) != 1 else ''}.") 
            for d in f_data:
                self.thread_list.append(
                    Image_thread(self, {"data_list":d})
                )
                self.thread_list[-1].set_function(self.thread_list[-1].compare_images)
                self.thread_list[-1].start()
                self.thread_list[-1].join()
                ended += 1
                print(f"Ended: {ended}/{len(f_data)}       ", end="\r")
            print("All threads ended sucessfully                 ")
            fin[name] = [r[0] for r in self.result]
        return fin

    def set_threads(self, threads:int):
        self.threads = threads