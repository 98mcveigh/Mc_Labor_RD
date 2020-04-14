import pickle
from tkinter import *
from tkinter import filedialog

class History(object):
    """docstring for History."""

    def __init__(self):
        super(History, self).__init__()
        self.histWindow = Toplevel()
        self.histWindow.geometry("400x200")
        self.histWindow.resizable(False,False)
        self.histWindow.iconbitmap("McLaborScraper/inc/McLaborIcon.ico")
