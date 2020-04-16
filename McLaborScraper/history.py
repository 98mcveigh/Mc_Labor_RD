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
        self.width = 480
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
        self.deleteButtons = []
        self.historyDict = self.loadHistory()
        self.showHistory()
        self.histWindow.update_idletasks()
        self.configScroll()

    def clearHistory(self):
        settingsFile = open("McLaborScraper/history.dat","wb")
        pickle.dump({},settingsFile)
        settingsFile.close()

    def loadHistory(self):
        saveFile = open("McLaborScraper/history.dat","rb")
        historyDict = pickle.load(saveFile)
        saveFile.close()
        return historyDict

    def saveHistory(self,histDict):
        saveFile = open("McLaborScraper/history.dat","wb")
        pickle.dump(histDict,saveFile)
        saveFile.close()

    def addToHistory(self,search,group):
        historyDict = self.loadHistory()
        newKey = len(historyDict.keys())
        historyDict[newKey] = []
        historyDict[newKey].append(date.today().strftime("%m/%d/%Y"))
        historyDict[newKey].append(search)
        historyDict[newKey].append(group)
        self.saveHistory(historyDict)

    def clearScrollFrame(self):
        for widget in self.scrollFrame.winfo_children():
            widget.destroy()
        self.deleteButtons = []

    def showHistory(self):
        num = 0
        for key in self.historyDict:
            self.deleteButtons.append(Label(self.scrollFrame,relief = FLAT,width = 2, text="X",bg="#dcc8c8",font=("Franklin Gothic Medium",9)))
            self.deleteButtons[num].grid(row=num,column=0)
            self.deleteButtons[num].bind("<Enter>",self.enterDelete)
            self.deleteButtons[num].bind("<Leave>",self.leaveDelete)
            self.deleteButtons[num].bind("<Button-1>",self.deleteHistEntry)
            dateLabel = Label(self.scrollFrame,relief = RIDGE,justify = CENTER,anchor=CENTER,width = 11, text=self.historyDict[key][0],bg="#f4f4f4",font=("Franklin Gothic Medium",9))
            dateLabel.grid(row=num,column=1,sticky="nsew")
            searchLabel = Label(self.scrollFrame,relief = RIDGE,justify = CENTER,anchor=CENTER,width = 30, text=self.historyDict[key][1],bg="#f4f4f4",font=("Franklin Gothic Medium",9))
            searchLabel.grid(row=num,column=2,sticky="nsew")
            groupLabel = Label(self.scrollFrame,relief = RIDGE,justify = CENTER,anchor=CENTER,width = 30, text=self.historyDict[key][2],bg="#f4f4f4",font=("Franklin Gothic Medium",9))
            groupLabel.grid(row=num,column=3,sticky="nsew")
            num = num + 1

    def enterDelete(self,e):
        e.widget["bg"] = "#dc9a9a"

    def leaveDelete(self,e):
        e.widget["bg"] = "#dcc8c8"

    def deleteHistEntry(self,e):
        for i,button in enumerate(self.deleteButtons):
            if e.widget == button:
                for j,key in enumerate(self.historyDict):
                     if i == j:
                        str = "Do you want to delete this history entry:\n" + self.historyDict[key][0] + " | " + self.historyDict[key][1] + " | " + self.historyDict[key][2] + "\nThis action can\'t be undone."
                        if not messagebox.askyesno("Are you sure?",str):
                            self.histWindow.focus_force()
                        else:
                            del self.historyDict[key]
                            self.saveHistory(self.historyDict)
                            self.clearScrollFrame()
                            self.showHistory()
                            self.histWindow.update_idletasks()
                            self.configScroll()
                            self.histWindow.focus_force()
                            return

    def configScroll(self):
        self.histCanvas.configure(scrollregion=self.histCanvas.bbox("all"),height=400,width=50)

    def onScroll(self, e):
        self.histCanvas.yview_scroll(int(-1*(e.delta/120)), "units")
