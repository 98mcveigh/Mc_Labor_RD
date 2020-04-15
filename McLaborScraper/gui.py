#Import necessary modules - tkinter for gui,siteScraping for scraping functionality
from tkinter import *
from tkinter import messagebox
import McLaborScraper.siteScraping as siteScraping
import threading
import McLaborScraper.history as history
import McLaborScraper.settings as settings
import McLaborScraper.advancedSearch as advancedSearch
import McLaborScraper.Search as Search
import pickle

class scraperGui(object):
    """docstring for scraperGui."""

    def __init__(self):
        super(scraperGui, self).__init__()
        #Create initial window with desired size, color, title and icon
        self.window = Tk()
        self.window.title("Mc Labor R&D")
        self.window.geometry("500x500")
        self.window.configure(bg="#f4f4f4")
        self.window.minsize(300,500)
        self.window.iconbitmap("McLaborScraper/inc/McLaborIcon.ico")
        self.window.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.history = history.History()
        self.searchIsRunning = [False]
        self.queue = []
        self.queueLabels = []

        #Create and place McLabor logo on 1/5 of the way down in the middle
        self.topFrame = Frame(self.window)
        self.topFrame.place(relx=0.5,rely=0.2,anchor=CENTER)
        self.image = PhotoImage(file = "McLaborScraper/inc/McLaborLogo.png")
        self.imLabel = Label(self.topFrame,image=self.image,borderwidth=0)
        self.imLabel.pack()

        #Create frame for search entry and button in middle of screen
        self.midFrame = Frame(self.window)
        self.midFrame.place(relx=0.5,rely=0.4,anchor="n")


        #place search entry and button in the frame
        self.searchEntry = Entry(self.midFrame,width = 30,insertwidth=1,relief = "flat",justify=CENTER,font=("Franklin Gothic Medium",12))
        self.searchEntry.grid(row=1,columnspan=2,sticky="ns")
        self.searchButton = Button(self.midFrame,text="Individual Search",bg="#f4f4f4",command=self.runScraping,width=15)
        self.searchButton.configure(activebackground = "#bbbbbb",relief="flat",font=("Franklin Gothic Medium",10))
        self.searchButton.grid(row=2,column=0,sticky="ew")

        #call functions to make search button darker when cursor is over it
        self.searchButton.bind("<Enter>", self.onEnter)
        self.searchButton.bind("<Leave>", self.onLeave)

        #Establish frame for status label and place it 3/4 down in the middle
        self.bottomFrame = Frame(self.window)
        self.bottomFrame.place(relx=0.5,rely=0.85,anchor=CENTER)
        self.currentSearch = Label(self.bottomFrame,text="",bg="#f4f4f4",font=("Franklin Gothic Medium",10))
        self.currentSearch.pack(fill="x")
        self.statusLabel = Label(self.bottomFrame,text="",bg="#f4f4f4",font=("Franklin Gothic Medium",10))
        self.statusLabel.pack(fill="x")


        self.advancedFrame = Frame(self.window)
        self.advancedFrame.place(relx=0.5,rely=1,anchor="s")
        #create and place more options button to pull up new window for settings
        self.settingsButton = Button(self.advancedFrame,text="Settings",font=("Times New Roman",8),command=self.changeSettings)
        self.settingsButton.configure(bg="#f4f4f4",activebackground = "#bbbbbb",relief = "flat",width=15)
        self.settingsButton.bind("<Enter>", self.onEnter)
        self.settingsButton.bind("<Leave>", self.onLeave)
        self.settingsButton.pack(side="left")

        self.advancedSearchButton = Button(self.advancedFrame,text="Advanced Search",font=("Times New Roman",8),command=self.advancedSearch)
        self.advancedSearchButton.configure(bg="#f4f4f4",activebackground = "#bbbbbb",relief = "flat",width=15)
        self.advancedSearchButton.bind("<Enter>", self.onEnter)
        self.advancedSearchButton.bind("<Leave>", self.onLeave)
        self.advancedSearchButton.pack(side="right")

        self.historyButton = Button(self.advancedFrame,text="History",font=("Times New Roman",8),command=self.openHistoryWindow)
        self.historyButton.configure(bg="#f4f4f4",activebackground = "#bbbbbb",relief = "flat",width=15)
        self.historyButton.bind("<Enter>", self.onEnter)
        self.historyButton.bind("<Leave>", self.onLeave)
        self.historyButton.pack(side="right")


        self.queueButton = Button(self.midFrame,text="Add Search To Queue",bg="#f4f4f4",command=self.addToQueue,width=15)
        self.queueButton.configure(activebackground = "#bbbbbb",relief="flat",font=("Franklin Gothic Medium",10))
        self.queueButton.bind("<Enter>", self.onEnter)
        self.queueButton.bind("<Leave>", self.onLeave)
        self.queueButton.grid(row=2,column=1,sticky="ew")

        self.queueFrame = Frame(self.midFrame,bg="#f4f4f4")
        self.queueFrame.grid(row=3,columnspan=2,sticky="ew")
        self.canvas = Canvas(self.queueFrame,bg="#f4f4f4")
        self.scrollFrame=Frame(self.canvas,bg="#f4f4f4",borderwidth=0)
        self.myscrollbar=Scrollbar(self.queueFrame,orient="vertical",command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.myscrollbar.set)
        self.myscrollbar.pack(side="right",fill="y")
        self.canvas.pack(fill="x")
        self.canvas.create_window((0,0),window=self.scrollFrame,anchor='nw',width=260)
        self.queueLabel = Label(self.scrollFrame,anchor=CENTER,text="SEARCH QUEUE:",bg="#eaeaea",font=("Franklin Gothic Medium",9))
        self.queueLabel.pack(fill="x")
        self.configScroll()

        self.startStopQueueButton = Button(self.midFrame,font=("Franklin Gothic Medium",10),activebackground = "#bbbbbb",relief="flat",text="Begin Queue",bg="#f4f4f4",command=self.runOrPauseQueue,width=30)
        self.startStopQueueButton.grid(row=4,columnspan=2,sticky="ew")
        self.startStopQueueButton.bind("<Enter>", self.onEnter)
        self.startStopQueueButton.bind("<Leave>", self.onLeave)
        self.settingsDict = None
        try:
            file = open("settings.dat","rb")
            self.settingsDict = pickle.load(file)
            file.close()
        except FileNotFoundError:
            settings.changeSettings(self,True)
        self.window.mainloop()


    #make it so search button appears darker when cursor is over it
    def onEnter(self,e):
        e.widget['background'] = "#dddddd"

    def onLeave(self,e):
        e.widget['background'] = "#f4f4f4"

    def onClosing(self):
        if self.searchIsRunning[0]:
            messagebox.showerror("Not Allowed","Can\'t close while search is running.")
        elif len(self.queue) > 0:
            if messagebox.askyesno("Are you sure you want to quit?","There are items in your queue. If you quit, these items will be deleted."):
                self.window.destroy()
        else:
            self.window.destroy()

    def queueEnter(self,e):
        for i,item in enumerate(self.queue):
            if e.widget["text"] == item.entry:
                widget = e.widget
                while widget["text"] == item.entry:
                    self.queueLabels[i]["background"] = "#dcc8c8"
                    try:
                        i = i + 1
                        widget = self.queueLabels[i]
                    except:
                        return
                return

    def openHistoryWindow(self):
        self.history.runWindow()

    def queueClick(self,e):
        for i,label in enumerate(self.queueLabels):
            if label['background'] == "#dcc8c8":
                if self.queue[i].isIndividual:
                    self.queueLabels[i].destroy()
                    self.queueLabels.pop(i)
                    self.queue.pop(i)
                    return
                keyLabel = label
                while keyLabel['background'] == "#dcc8c8":
                    self.queueLabels[i].destroy()
                    self.queueLabels.pop(i)
                    self.queue.pop(i)
                    try:
                        keyLabel = self.queueLabels[i]
                    except:
                        self.updateQueue()
                        return
                self.updateQueue()
                return
            else:
                continue

    def queueLeave(self,e):
        for i,label in enumerate(self.queueLabels):
            if label["background"] == "#dcc8c8":
                redLabel = self.queueLabels[i]
                while redLabel["background"] == "#dcc8c8":
                    self.queueLabels[i]['background'] = "#f4f4f4"
                    try:
                        i = i + 1
                        redLabel = self.queueLabels[i]
                    except:
                        return
                return

    #call site scraping function when search button is clicked
    def runScraping(self):
        #create new thread so gui can be responsive during search
        if self.searchEntry.get() == "":
            messagebox.showerror("Not Allowed","Please enter a valid search.")
        else:
            if self.searchIsRunning[0]:
                messagebox.showerror("Not Allowed","Multiple searches can not be run at the same time.")
            else:
                searchObj = Search.Search(self.searchEntry.get(),0,True)
                scraperThread = threading.Thread(target=siteScraping.scrape,args=[self,searchObj])
                scraperThread.start()
                self.searchEntry.delete(0,'end')

    def changeSettings(self):
        if self.searchIsRunning[0]:
            messagebox.showerror("Not Allowed","Must change settings in between searches.")
        else:
            settings.changeSettings(self)

    def addToQueue(self,fromAdvanced = False,entry = None,iter = 0,resolution = 0):
        if not fromAdvanced:
            if self.searchEntry.get() == "":
                messagebox.showerror("Not Allowed","Please enter a valid search.")
                return
            else:
                self.queueLabels.append(Label(self.scrollFrame,anchor=CENTER,text=self.searchEntry.get(),bg="#f4f4f4",font=("Franklin Gothic Medium",8)))
                self.queue.append(Search.Search(self.searchEntry.get(),0,False))
                self.searchEntry.delete(0,'end')
        else:
            self.queueLabels.append(Label(self.scrollFrame,anchor=CENTER,text=entry,bg="#f4f4f4",font=("Franklin Gothic Medium",8)))
            self.queue.append(Search.Search(entry,((iter)*resolution + 1),False,iter))
        self.updateQueue()


    def updateQueue(self):
        if len(self.queueLabels) < 50:
            seenNum = len(self.queueLabels)
        else:
            seenNum = 50
        for i in range(seenNum):
            self.queueLabels[i].pack(fill="x")
            self.queueLabels[i].bind("<Enter>", self.queueEnter)
            self.queueLabels[i].bind("<Leave>", self.queueLeave)
            self.queueLabels[i].bind("<Button-1>", self.queueClick)
            self.configScroll()
        if len(self.queueLabels) == 0:
            self.queueLabel["text"] = "SEARCH QUEUE:"
        else:
            self.queueLabel["text"] = "SEARCH QUEUE (" + str(len(self.queueLabels)) + "):"



    def runOrPauseQueue(self):
        if len(self.queueLabels) < 1:
            messagebox.showerror("Not Allowed","Please add searches to queue.")
            return
        if self.startStopQueueButton["text"] == "Begin Queue":
            if self.searchIsRunning[0]:
                messagebox.showerror("Not Allowed","Can not start queue while another search is running.")
            else:
                self.startStopQueueButton["text"] = "Pause Queue"
                scraperThread = threading.Thread(target=siteScraping.runScrapingLoop,args=[self])
                scraperThread.start()
        else:
            if self.checkToPauseQueue():
                self.startStopQueueButton["text"] = "Begin Queue"

    def configScroll(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),height=100,width=50)

    def advancedSearch(self):
        guiThread = threading.Thread(target=advancedSearch.advancedSearchGui,args=[self])
        guiThread.start()

    def checkToPauseQueue(self):
        result = messagebox.askyesno("Are you sure?","Are you sure you would like to pause the Queue?")
        return result


def beginScraper():
    scraperGui()
