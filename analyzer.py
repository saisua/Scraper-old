#$PREFIX/usr/bin/python3
import os

log_type = ["text","input","pic","url"]

def TrueFalse(text, ask=True):
    if ask:
        user_input = str(input(text))
    else: user_input = text
    if user_input == "y" or user_input == "Y" or user_input == "Yes" or user_input == "yes":
        return True
    else:
        return False

if TrueFalse("Borrar analisis anteriores? (Y/n) "):
    open("log-search","w").close()
    open("log-names","w").close()

def write_output(file, output):
    out_file = open("log-"+str(file), "a")
    out_file.write(str(output))
    out_file.close()
    print(str(file) + ": " + str(output))

def text_finder(text, text_file, size, names=False):
    found_text = []
    text_file = open(str(text_file.name),"r")
    read_file = text_file.read()
    print(text_file)
    for ptext in permutate(text):
        letter_counter = 0
        while letter_counter <= len(read_file) and letter_counter >= 0:
            print("Searching for " + str(ptext))
            letter_counter = read_file.find(ptext, letter_counter)
            if letter_counter >= 0:
                letter_counter+=1
                found_text.append(letter_counter)
                try:
                    word = (str(letter_counter) + ": " + str(read_file[letter_counter-size:letter_counter+size]))
                except:
                    try:
                        word = (str(letter_counter) + ": " + str(read_file[letter_counter:letter_counter+size]))
                    except:
                        try:
                            word = (str(letter_counter) + ": " + str(read_file[letter_counter-size:letter_counter]))
                        except: print("Error found. Is the chosen file empty?")
                word += "\n"
                write_output("search", text_file.name[4]+str(word))
                if names:
                    write_output("names",text_file.name[4]+word)
            else:
                print("- No words '" + str(ptext) + "' found")

def text_statistics(search_file):
    word = False
    if TrueFalse("Buscar una palabra en concreto? (Y/n) "):
        word = input("Introduzca la palabra a buscar: ")
        stat_analizer(search_file, word)
    if TrueFalse("Buscar correos? (Y/n) "):
        stat_analizer(search_file, "@")

def find_different(string, list, start=None, end=None):
    final = -1
    for search in list:
        found = string.find(search, start, end)
        if found != -1:
            if found < final or final == -1:
                final = found
    return final

def permutate(string):
    final = [string]
    if len(string) == 0: return final
    if string != string.lower(): final.append(string.lower())
    if string != string.upper(): final.append(string.upper())
    first_upper = string[0].upper() + string[1:].lower()
    if string != first_upper: final.append(first_upper)
    to_find = [" ", ".", ","]
    search_num = find_different(string, to_find)
    first_search_num = search_num
    first_upper_list = list(first_upper)
    while search_num != -1:
        search_num = find_different(string, to_find, search_num) + 1
        if search_num == 0 or search_num +1 > len(first_upper): break
        if search_num != -1:
            first_upper_list[search_num] = first_upper[search_num].upper()
    if first_search_num != -1:
        first_upper = ''.join(first_upper_list)
        if string != first_upper: final.append(first_upper)
    print("Permutado " + str(final))
    return final

def stat_analizer(search_file, word):
    stats = {}
    last_line = ""
    next_line = False
    for word_perm in permutate(word):
        for line in search_file.readlines():
            line = line.replace("\n", "  ")
            if word:
                if line.find(word_perm) != -1 or next_line:
                    if line != word_perm:
                        if next_line:
                            line = last_line + line
                            print("n " + str(line))
                        try:
                            stats[str(line)] += 1
                        except:
                            stats[str(line)] = 1
                        next_line = False
                    else:
                        next_line = True
                        last_line = last_line + line
            else:
                try:
                    stats[str(line)] += 1
                except:
                    stats[str(line)] = 1
            if not next_line and line != "":
                last_line = line
    stats_values = sorted(stats.values(), reverse=True)
    stats_keys = sorted(stats, reverse=True)
    try:
        number_shown = int(input("Cuantos top-resultados mostrar? (todos=-1) "))
        if number_shown == -1:
            raise Exception()
        number_shown = range(number_shown)
    except:
        number_shown = range(len(list(stats.keys())))
    for top in number_shown:
        try:
            print(str(stats_keys[top]) + " (" +str(stats_values[top]) + ")")
        except:
            print("- Looks like there are no more stats to show")
            break
    if not TrueFalse("Cerrar estadísticas? (Y/n) "):
        stat_analizer(search_file,word)

def __end__():
    for log in log_type:
        if log == "text": pass
        try:
            os.system("sort -o log-" + str(log) + " log-"+str(log)+" | uniq")
        except: pass
    if TrueFalse("Analizar archivos? (Y/n) "):
        try:
            tamaño = int(input("Tamaño de los log? (15) "))
        except:
            tamaño = 15
        file = input("Que archivo? (text,input,pic,url) ")
        try:
            text_file = open("log-"+str(file), "r")
        except:
            print("- Error found. Does that file really exist in this folder?")
            text_file = -1
        if text_file != -1:
            read_text = text_file.read()
            print("+ Archivo '" + str(file) + "' correctamente cargado. len:" + str(len(read_text)))
            found_text = []
            while TrueFalse("Buscar una palabra en concreto? (Y/n) "):
                busqueda = input("Introduzca el texto a buscar: ")
                text_finder(busqueda, text_file, tamaño)
            if TrueFalse("Buscar correos? (Y/n) "):
                text_finder("@", text_file, tamaño)
            if TrueFalse("Buscar nombres? (Y/n) "):
                print("Archivos:")
                try:
                    os.system("ls")
                except: pass
                name_file_path = input("Nombre de archivo de nombres (misma carpeta): ")
                name_file = open(name_file_path).readlines()
                for name in name_file:
                    text_finder(name, text_file, tamaño, True)
                try:
                    name_file.close()
                except: pass
            text_file.close()
    if TrueFalse("Revisar resultados? (Y/n) "):
        try:
            log_per_pag = int(input("Cuantas lineas mostrar por página? (10) "))
            if log_per_pag <1: raise Exception()
        except: log_per_pag = 10
        counter = 0
        file = input("Que archivo? (search, names) ")
        try:
            review_file = open("log-" + str(file), "r").readlines()
        except: review_file = []
        while counter < len(review_file):
            counter+=1
            print(str(counter) + ": " + str(review_file[counter]))
            if counter % log_per_pag == 0:
                print("Cerrar el revisado? m:mostrar mas de uno de los resultados")
                user = input("Y/n/m : ")
                if user == "m" or user == "M":
                    try:
                        number = int(input("Indique el numero de resultado: "))
                        if number > len(review_file): raise Exception()
                        length = 20
                        letter = review_file[number][0]
                        if letter == "t": file2 = "text"
                        elif letter == "i": file2 = "input"
                        elif letter == "p": file2 = "pic"
                        elif letter == "u": file2 = "url"
                        num_file = open("log-"+file2,"r").read()
                        number = int(review_file[number][1:review_file[number].find(":")])
                    except:
                        number = False
                    while number:
                        try:
                            print(num_file[number-length:number+length])
                        except:
                            start_l = number-length
                            end_l = number+length
                            if start_l < 0: start_l = 0
                            if end_l > len(num_file): end_l = len(num_file)
                            try:
                                print(num_file[start_l:end_l])
                            except: print("- An unknown error happened")
                        if TrueFalse("Acabar el visionado de " + str(number) + "? (Y/n) "): break
                        try:
                            length = int(input("Indique longitud del print (" + str(length) + ")"))
                        except: length += 2
                elif TrueFalse(user,False): break
    if TrueFalse("Iniciar estadísticas? (Y/n) "):
        text_statistics(open("log-search","r"))
    if not TrueFalse("Cerrar el programa de analisis? "):
        __end__()   #nombre, alias. img google

__end__()
