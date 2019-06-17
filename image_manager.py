from skimage.measure import compare_ssim as ssim
from skimage.measure import compare_mse as mse
from skimage import img_as_float, data
from skimage.io import imread
from skimage.transform import resize
from skimage.color import rgba2rgb
import threading
import itertools
import face_recognition

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
    def compare_images(self, data_list) -> None:
        result = []
        if(None in data_list):
            data_list = data_list[:data_list.index(None)]
        for given,unknown in data_list[:]:
            if(len(given.shape) > 2 or len(unknown.shape) > 2):
                continue
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

    def extract_faces(self, images:list) -> None:
        for image in images:
            if(image is None): break
            self.manager.add_result(face_recognition.face_locations(image))

    def compare_faces(self, given_list:list, unknown_list:list) -> None:
        for unknown in unknown_list[:]:
            if(unknown is None): break
            self.manager.add_result(face_recognition.compare_faces(given_list, unknown))

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
            print("All threads ended successfully                 ")
            fin[name] = [r[0] for r in self.result]
        return fin

    def extract_faces(self, img_list:list) -> list:
        self.reset()
        f_data = self.format_data(img_list)
        ended = 0
        print(f"Starting {len(f_data)} thread{'s' if len(f_data) != 1 else ''}.") 
        for thread in f_data:
            self.thread_list.append(
                Image_thread(self, {"images":thread})
                )
            self.thread_list[-1].set_function(self.thread_list[-1].extract_faces)
            self.thread_list[-1].start()
            self.thread_list[-1].join()
            ended += 1
            print(f"Ended: {ended}/{len(f_data)}       ", end="\r")
        print("All threads ended successfully                 ")
        return self.result

    def compare_faces(self, given_list:list, unknown_list:list) -> list:
        self.reset()
        f_data = self.format_data(unknown_list)
        ended = 0
        print(f"Starting {len(f_data)} thread{'s' if len(f_data) != 1 else ''}.") 
        for thread in f_data:
            self.thread_list.append(
                Image_thread(self, {"given_list":given_list,"unknown_list":thread})
                )
            self.thread_list[-1].set_function(self.thread_list[-1].compare_faces)
            self.thread_list[-1].start()
            self.thread_list[-1].join()
            ended += 1
            print(f"Ended: {ended}/{len(f_data)}       ", end="\r")
        print("All threads ended successfully                 ")
        return self.result

    def set_threads(self, threads:int):
        self.threads = threads

def img_compare_encode(img_list:list=[]) -> list:
    return [img_as_float(imread(image)) for image in img_list]

def img_face_load(img_list:list=[]) -> list:
    return [face_recognition.load_image_file(image) for image in img_list]

def img_face_encode(img_list:list=[]) -> list:
    fin = []
    for image in img_list:
        fin.extend(face_recognition.face_encodings(face_recognition.load_image_file(image)))
        #if(not len(fin[-1])): del fin[-1]
    return fin