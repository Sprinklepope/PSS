import os
import query
import time
import re
from kivy.app import App
import subprocess
import mmap
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color



def val(url):
    invalidMessage = ""

    hasforms = False


    try:
        #checking if the url has forms
        session = HTMLSession()
        def get_all_forms(userurl):
            res = session.get(userurl)
            soup = BeautifulSoup(res.html.html, "html.parser")
            return soup.find_all("form")

        forms = get_all_forms(url)
        if forms:
            hasforms = True
        else:
            invalidMessage = "This url has no forms"

    except:
        invalidMessage = "Invalid url"

    return (hasforms, invalidMessage)

def mmap_io_find(filename, urlinput, self): #url provided without paramaters can not be tested for vulnerabilities
    with open(filename, mode="r", encoding="utf-8") as file_obj:
        s= mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ)
        if s.find(b'no parameter(s) found for testing in the provided data') != -1:
            print('string exist in a file this birch doesnt have parameters')
            invalidSearch("The url provided does not have any parameters", "no parameters")
        else:
            modQ = query.Init(urlinput)
            dumpR = bigdump(urlinput)
            show_popup(dumpR, modQ[0], modQ[1], self)

def bigdump(urlinput):
    dumpedflag = False
    result = subprocess.run("sqlmap -u " + urlinput + " --dump-all --batch --threads=5 > dumpoutput.txt ", shell=True, stdin=subprocess.PIPE)

    #check for amount of entries dumped - entries must be > 0 for dump to be successful
    mf = open((os.getcwd()+ "/dumpoutput.txt"), "r+")
    file_line = mf.readline()
    while file_line:
        try:
            m = re.search('(\d+) entries', file_line, re.IGNORECASE)
            m.group(1)
            if int(m.group(1)) > 0:
                dumpedflag = True
        except AttributeError:
            m = re.search('(\d+) entries', file_line, re.IGNORECASE)  # no entries
        file_line = mf.readline()
    mf.close()
    return dumpedflag


class MyMainWindow(Screen):
    url = ObjectProperty(None)

    def SearchBtn(self):
        urlinput = self.url.text
        res = val(urlinput)
        if res[0]:
            self.reset()
            result = subprocess.run("sqlmap -u " + urlinput + " --batch --threads=5 > preliminaryrun.txt ", shell=True,stdin=subprocess.PIPE)
            mmap_io_find(os.getcwd()+ "/preliminaryrun.txt",urlinput, self)
        else:
            invalidSearch(res[1],"Invalid URL")


    def reset(self):
        self.url.text = ""

class P(FloatLayout):
    pass

def show_popup(dumped, modified, queried, self):
    show = P() # Create a new instance of the P class
    if dumped or modified or queried:
        vulnerable = "Vulnerable"
    else:
        vulnerable = "Not Vulnerable"
    resultingString = "Status: " + vulnerable
    resultingString += "\n\n"
    resultingString += "Attacks Succeeded: \n\n"
    if dumped:
        resultingString += "Databse Dump\n"
    if modified:
        resultingString += "Database Modified\n"
    if queried:
        resultingString += "Database Queried\n"
    resultingString += "\n"

    resultingString += "Attacks Failed: \n\n"
    if not dumped:
        resultingString += "Databse Dump\n"
    if not modified:
        resultingString += "Database Modified\n"
    if not queried:
        resultingString += "Database Queried\n"


    show.ids.result.text = resultingString
    popupWindow = Popup(title="Vulnerability Report", content=show, size_hint=(.85, .6), auto_dismiss=False)
    popupWindow.open() #show the popup


class WindowManager(ScreenManager):
    pass

def invalidSearch(msg,header):
    pop = Popup(title=header, content=Label(text=msg), size_hint=(None, None), size=(400, 400))
    pop.open()

kv = Builder.load_file("mymain.kv")

sm = WindowManager()

screens = [MyMainWindow(name="PSS")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "PSS"

class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()
