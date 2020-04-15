import pickle
from tkinter import *
from tkinter import filedialog
from datetime import date


class History(object):
    """docstring for History."""

    def __init__(self):
        super(History, self).__init__()

    def runWindow(self):
        self.histWindow = Toplevel()
        self.histWindow.bind("<MouseWheel>",self.onScroll)
        self.width = 450
        self.histWindow.geometry(str(self.width) + "x400")
        self.histWindow.resizable(False,False)
        self.histWindow.iconbitmap("McLaborScraper/inc/McLaborIcon.ico")


        self.histLabel = Label(self.histWindow,relief = GROOVE,anchor=CENTER,text="Search History:",bg="#eaeaea",font=("Franklin Gothic Medium",9))
        self.histLabel.pack(fill="x")
        self.histFrame = Frame(self.histWindow,bg="#f4f4f4")
        self.histFrame.pack(fill="both")
        self.histCanvas = Canvas(self.histFrame,bg="#f4f4f4")
        self.scrollFrame=Frame(self.histCanvas,bg="#f4f4f4",borderwidth=0)
        self.histScrollbar=Scrollbar(self.histFrame,orient="vertical",command=self.histCanvas.yview)
        self.histCanvas.configure(yscrollcommand=self.histScrollbar.set)
        self.histScrollbar.pack(side="right",fill="y")
        self.histCanvas.pack(fill="both")
        self.histCanvas.create_window((0,0),window=self.scrollFrame,anchor='nw',width=self.width)
        self.showHistory()
        self.histWindow.update_idletasks()
        self.configScroll()

    def resetHistory(self):
        settingsFile = open("McLaborScraper/history.dat","wb")
        pickle.dump({},settingsFile)
        settingsFile.close()

    def addToHistory(self,search,group):
        saveFile = open("McLaborScraper/history.dat","rb")
        historyDict = pickle.load(saveFile)
        saveFile.close()
        newKey = len(historyDict.keys())
        historyDict[newKey] = []
        historyDict[newKey].append(date.today().strftime("%m/%d/%Y"))
        historyDict[newKey].append(search)
        historyDict[newKey].append(group)
        saveFile = open("McLaborScraper/history.dat","wb")
        pickle.dump(historyDict,saveFile)
        saveFile.close()

    def showHistory(self):
        saveFile = open("McLaborScraper/history.dat","rb")
        historyDict = pickle.load(saveFile)
        saveFile.close()
        for key in historyDict:
            dateLabel = Label(self.scrollFrame,relief = RIDGE,justify = CENTER,anchor=CENTER,width = 11, text=historyDict[key][0],bg="#f4f4f4",font=("Franklin Gothic Medium",9))
            dateLabel.grid(row=key,column=0)
            searchLabel = Label(self.scrollFrame,relief = RIDGE,justify = CENTER,anchor=CENTER,width = 30, text=historyDict[key][1],bg="#f4f4f4",font=("Franklin Gothic Medium",9))
            searchLabel.grid(row=key,column=1)
            groupLabel = Label(self.scrollFrame,relief = RIDGE,justify = CENTER,anchor=CENTER,width = 30, text=historyDict[key][2],bg="#f4f4f4",font=("Franklin Gothic Medium",9))
            groupLabel.grid(row=key,column=2)

    def configScroll(self):
        self.histCanvas.configure(scrollregion=self.histCanvas.bbox("all"),height=400,width=50)

    def onScroll(self, e):
        self.histCanvas.yview_scroll(int(-1*(e.delta/120)), "units")
