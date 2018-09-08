#_*_ coding: utf-8 _*_


from scrapy.selector import HtmlXPathSelector
from scrapy.spiders import Spider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
try:
    import regex
    import html2text
except:
    import sys
    import subprocess
    subprocess.check_call({sys.executable, '-m', 'pip', 'install', 'regex', 'html2text'])
    import regex
    import html2text
#from scrapyproject.items import Myitems

log_type = ["text","input","pic","url"]

def TrueFalse(text):
    user_input = str(raw_input(text))
    if user_input == "y" or user_input == "Y" or user_input == "Yes" or user_input == "YES" or user_input == "yes":
        return True
    else:
        return False

if TrueFalse("Buscar en google? "):
    DOMAIN = "www.google.com/q=" + str(raw_input("Indique la búsqueda: ")).replace(" ","+")
else:
    DOMAIN = str(raw_input("Indique la url: "))

URL = 'http://%s' % DOMAIN

try:
    limite = int(raw_input("Indique la profundidad: "))
except:
    limite = 1

if TrueFalse("Modificar registro de datos? (Todo) "):
    if not TrueFalse("Registrar texto? (Y/n) "):
        read_text = False
    else: read_text = True
    if not TrueFalse("Registrar inputs? (Y/n) "):
        read_input = False
    else: read_input = True
    if not TrueFalse("Registrar imagenes? (Y/n) "):
        read_pic = False
    else: read_pic = True
    if not TrueFalse("Registrar URLs? (Y/n) "):
        read_url = False
    else: read_url = True
else:
    read_text = True
    read_input = True
    read_pic = True
    read_url = True


if TrueFalse("Borrar registros anteriores? (Y/n) "):
    for log in log_type:
        open("log-"+str(log),"w").close()

def write_output(file, output):
    output_file = open("log-"+str(file),"a")
    output_file.write(str(output))
    output_file.close()
    print(str(file) + ": " + str(output))

class MySpider(Spider):
    name = "crawler"
    allowed_domains = []
    start_urls = [
        URL
    ]
    custom_settings = {
        'DEPTH_LIMIT':limite,
        'request_depth_max':limite,
        'ROBOTSTXT_OBEY':False
    }
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        for log in log_type:
            if not eval("read_"+str(log)): pass
            write_output(log,"")
            write_output(log,"####  " + str(response)[5:])
        if read_text:
            for text in hxs.select("//body//text()").extract():
                if not regex.match(r'^\s*$', text):
                    write_output("text",text) #value,name,id,type,disabled
        if read_input:
            for input in hxs.select('//input//@value | //input//@name | //input//@id | //input//@type | //input//@disabled').extract():
                write_output("input",input)
        if read_pic:
            for image in hxs.select('//img/@src').extract():
                write_output("pic",image)

        for url in hxs.select('//a/@href').extract():
            if( not ( url.startswith('http://') or url.startswith('https://') )):
                url = URL + url
                if read_url:
                    write_output("url", url)
            yield Request(url, callback=self.parse)
#google, img, data
