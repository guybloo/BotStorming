import time
import urllib
import random

import speech_recognition as sr
from gensim.models import KeyedVectors
import requests

from tkinter import *
import threading
import urllib.request

import tkinter as tk
from PIL import Image, ImageTk

file = 'wiki-news-300d-1M.vec'

# model = KeyedVectors.load_word2vec_format(file)
# model.save("DS.model")
model = KeyedVectors.load("DS.model")

photos = [[]]
newSentence = [False]


# get sentence with speech recognition
def getSentence():
    r = sr.Recognizer()
    mic = sr.Microphone()
    s = 0
    while s == 0:
        with mic as source:
            print("wait")
            r.adjust_for_ambient_noise(source)
            print("talk")
            audio = r.listen(source)
            print("stop")
            try:
                s = r.recognize_google(audio)
                print(s)
                return s
            except:
                print("get sentence error")
                s = 0
            print(s)


# search images in Quant search engine
def getImagesFromQuant(query):
    r = requests.get("https://api.qwant.com/api/search/images",
                     params={
                         'count': 3,
                         'q': query,
                         't': 'images',
                         'safesearch': 1,
                         'locale': 'en_US',
                         'uiv': 4,
                         'color': 'monochrome',
                         # 'license': 'public',
                         'size': 'medium'
                     },
                     headers={
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
                     }
                     )

    try:
        response = r.json().get('data').get('result').get('items')
        urls = [r.get('media') for r in response]
        print(urls)
        return urls
    except:
        print("images search error")
        pass


# load image from url
def getImageFromUrl(url):
    try:
        return Image.open(urllib.request.urlopen(url))
    except:
        print("image read fail")
        return []


##################################################

# slideshow class with tkinter
class MySlideShow:

    # constructor
    def __init__(self):
        self.parent = tk.Tk()

        self.persistent_image = None
        self.pixNum = 0
        self.label = tk.Label(self.parent)
        self.parent.geometry("500x500")

        scr_w, scr_h = self.parent.winfo_width(), self.parent.winfo_height()

        self.canvas = Canvas(self.parent, bg="white", height=scr_h, width=scr_w)
        self.canvas.pack(side="top", expand=YES, fill=BOTH)
        self.canvas.image = []
        self.prevImage = []
        self.newImage = []

    # open and config slideshow
    def open(self):
        self.startSlideShow(2000)
        self.parent.mainloop()

    # start slideshow
    def startSlideShow(self, delay=3000):  # delay in seconds

        if newSentence[0]:
            newSentence[0] = False
            print("change")

        if photos[0]:
            self.pixNum = (self.pixNum) % len(photos[0])
            try:
                myimage = photos[0][self.pixNum].copy()
                self.showImage(myimage)
                self.pixNum = (self.pixNum + 1) % len(photos[0])

            except:
                pass
        self.parent.after(delay, self.startSlideShow)

    # show the new image
    def showImage(self, image):
        image = image.convert("RGB")
        scr_w, scr_h = self.parent.winfo_width(), self.parent.winfo_height()

        if not self.canvas.image:
            self.fadeIn(image)
            self.prevImage = image.copy()
            return

        self.fadeOut(self.prevImage)
        self.prevImage = image.copy()
        self.fadeIn(image)

    # show fade in animation
    def fadeIn(self, image):
        alpha = 0
        while 255 >= alpha:
            timage = image.copy()
            timage.putalpha(alpha)
            self.showImageOnCanvas(timage)
            alpha = alpha + 5
            time.sleep(0.001)
            self.parent.update()

    # show fade out animation
    def fadeOut(self, image):
        alpha = 255
        while 0 <= alpha:
            timage = image.copy()
            timage.putalpha(alpha)
            self.showImageOnCanvas(timage)
            alpha = alpha - 5
            time.sleep(0.001)
            self.parent.update()

    # display image on UI
    def showImageOnCanvas(self, image):
        scr_w, scr_h = self.parent.winfo_width(), self.parent.winfo_height()
        image.thumbnail((scr_w / 2, scr_h / 2), Image.ANTIALIAS)

        self.canvas.image = ImageTk.PhotoImage(image)
        self.canvas.create_image(scr_w / 2, scr_h / 2, image=self.canvas.image, anchor=CENTER)


# class represents the gui thread
class GUIThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    # run process
    def run(self):
        slideShow = MySlideShow()
        slideShow.open()


# class represents sentence and images read
class ReadThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    # run process
    def run(self):
        while True:
            words = getSentence()

            similar = model.most_similar(positive=words.split(), topn=20)
            tsimilar = random.choices(similar[10:20], k=2)
            while tsimilar[0][0] == tsimilar[1][0]:
                tsimilar = random.choices(similar[10:20], k=2)
            similar = tsimilar
            print(similar)
            tempPhotos = []

            for w in similar:
                print(w)
                res = getImagesFromQuant(w[0] + " sketch")
                if res:
                    for p in res:
                        img = getImageFromUrl(p)
                        if img:
                            tempPhotos.append(img)
                            photos[0] = tempPhotos
                            print("length of photos " + str(len(tempPhotos)))

            newSentence[0] = True

            for s in similar:
                print(s)


# main script - run threads
thread1 = ReadThread(1, "Thread-1", 1)
thread2 = GUIThread(2, "Thread-2", 2)

thread1.start()
thread2.start()
