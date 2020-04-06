from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import threading
from McLaborScraper.inc.zips import zips,towns,counties
# from inc.zips import zips,towns,counties
import pickle

class advancedSearchGui(object):
    """docstring for advancedSearchGui."""

    def __init__(self,scraperGui = None):
        super(advancedSearchGui, self).__init__()
        self.scraperGui = scraperGui
        self.window = Tk()
        self.window.title("Advanced Search")
        self.window.geometry("400x400")
        self.window.configure(bg="#f4f4f4")
        self.window.resizable(False,False)
        self.window.iconbitmap("McLaborScraper/inc/mclaborcropped2.ico")
        self.towns = list(dict.fromkeys(towns()))
        self.counties = counties()
        self.townsOrCounties = "Towns"
        self.settingsDict = {'saveDirectory':None,'numGoogResults':None}


        #Entry frame to hold label to enter search and toggle county
        ############################################################

        self.entryFrame = Frame(self.window,bg="#f4f4f4")
        self.entryFrame.place(relx=0.5,rely=0.1,anchor=CENTER)

        self.entryLabel = Label(self.entryFrame,text="Enter Base Search:",bg="#f4f4f4",font=("Franklin Gothic Medium",10))
        self.entryLabel.grid(row=0,columnspan=2,sticky="ew")

        self.mainEntry = Entry(self.entryFrame,borderwidth=0,relief="flat",width=30)
        self.mainEntry.configure(font=("Franklin Gothic Medium",12),insertwidth=1,justify=CENTER)
        self.mainEntry.grid(row=1,columnspan=2,sticky="ew")
        self.mainEntry.bind("<Key>", self.updateExamples)


        self.townButton = Button(self.entryFrame,borderwidth=0,relief="flat",width=15,text="Town",bg="#c8dcca")
        self.townButton.grid(row=2,column=0,sticky="ew")
        self.townButton.bind("<Enter>",self.on_enter)
        self.townButton.bind("<Leave>",self.on_leave)
        self.townButton.bind("<Button-1>",self.selectTowns)

        self.countyButton = Button(self.entryFrame,borderwidth=0,relief="flat",width=15,text="County",bg="#f4f4f4")
        self.countyButton.grid(row=2,column=1,sticky="ew")
        self.countyButton.bind("<Enter>",self.on_enter)
        self.countyButton.bind("<Leave>",self.on_leave)
        self.countyButton.bind("<Button-1>",self.selectCounties)

        #File Directory frame to save files to a specific place
        #######################################################
        self.fileFrame = Frame(self.window,bg="#f4f4f4")
        self.fileFrame.place(relx=0.5,rely=0.35,anchor=CENTER)

        self.blankLabel1 = Label(self.fileFrame,text="",bg="#f4f4f4",font=("Franklin Gothic Medium",10))
        self.blankLabel1.grid(row=0,columnspan=2,sticky="ew")

        self.fileLabel = Label(self.fileFrame,borderwidth=0,text="Folder to save results...",font=("Franklin Gothic Medium",10))
        self.fileLabel.configure(bg="#f4f4f4")
        self.fileLabel.grid(row=1,column=0,sticky="ew")

        self.fileButton = Button(self.fileFrame,borderwidth=0,text="Select Folder",bg="#f4f4f4",font=("Franklin Gothic Medium",10))
        self.fileButton.configure(command=self.getDirectory)
        self.fileButton.grid(row=1,column=1,sticky="ew")
        self.fileButton.bind("<Enter>",self.on_enter)
        self.fileButton.bind("<Leave>",self.on_leave)

        self.blankLabel2 = Label(self.fileFrame,text="",bg="#f4f4f4",font=("Franklin Gothic Medium",10))
        self.blankLabel2.grid(row=2,columnspan=2,sticky="ew")

        self.numSearchLabel = Label(self.fileFrame,bg="#f4f4f4",borderwidth=0,text="# Google results to Search",font=("Franklin Gothic Medium",10))
        self.numSearchLabel.grid(row=3,column=0,sticky="s",ipadx=5)

        self.slider = Scale(self.fileFrame,bg="#f4f4f4",from_=0,to=300,orient=HORIZONTAL)
        self.slider.configure(sliderrelief="flat",bd=0,troughcolor="#cccccc",highlightthickness=0,command=self.updateEstimate)
        self.slider.set(150)
        self.slider.grid(row=3,column=1,sticky="ew")

        self.exampleFrame = Frame(self.window)
        self.exampleFrame.place(relx=0.5,rely=0.65,anchor=CENTER)

        self.exampleLabel = Label(self.exampleFrame,bg="#f4f4f4",width=30,borderwidth=0,text="Example Searches:",font=("Franklin Gothic Medium",12))
        self.exampleLabel.pack()

        self.examples = []
        for i in range(3):
            labelText = "... " + self.towns[i] + " Ma"
            self.examples.append(Label(self.exampleFrame,bg="#f4f4f4",borderwidth=0,text=labelText,font=("Franklin Gothic Medium",9)))
            self.examples[i].pack(fill="x")

        self.timeFrame = Frame(self.window)
        self.timeFrame.place(relx=0.5,rely=0.85,anchor=CENTER)

        self.timeTitle = Label(self.timeFrame,bg="#f4f4f4",width=30,borderwidth=0,text="Estimated Time To Complete",font=("Franklin Gothic Medium",12))
        self.timeTitle.pack(fill="x")

        self.timeEstimate = Label(self.timeFrame,bg="#f4f4f4",width=30,borderwidth=0,text="14 hours 6 minutes",font=("Franklin Gothic Medium",9))
        self.timeEstimate.pack(fill="x")

        self.finalFrame = Frame(self.window)
        self.finalFrame.place(relx=0.5,rely=1,anchor="s")

        self.runButton = Button(self.finalFrame,borderwidth=0,relief="flat",width=15,text="Run",bg="#f4f4f4",command=self.addSearchToQueue)
        self.runButton.pack(side="left")
        self.runButton.bind("<Enter>",self.on_enter)
        self.runButton.bind("<Leave>",self.on_leave)

        self.cancelButton = Button(self.finalFrame,borderwidth=0,relief="flat",width=15,text="Cancel",bg="#f4f4f4")
        self.cancelButton.pack(side="right")
        self.cancelButton.bind("<Enter>",self.on_enter)
        self.cancelButton.bind("<Leave>",self.on_leave)
        self.cancelButton.bind("<Button-1>",self.cancel)


        self.window.mainloop()

    def on_enter(self,e):
        self.updateExamples()
        if e.widget["bg"] == "#c8dcca":
            return
        else:
            e.widget["bg"] = "#dddddd"

    def on_leave(self,e):
        self.updateExamples()
        if e.widget["bg"] == "#c8dcca":
            return
        else:
            e.widget["bg"] = "#f4f4f4"

    def selectTowns(self,e):
        if self.townsOrCounties == "Towns":
            return
        else:
            self.townButton["bg"] = "#c8dcca"
            self.countyButton["bg"] = "#f4f4f4"
            self.townsOrCounties = "Towns"
            self.updateExamples()
            self.updateEstimate()

    def selectCounties(self,e):
        if self.townsOrCounties == "Counties":
            return
        else:
            self.townButton["bg"] = "#f4f4f4"
            self.countyButton["bg"] = "#c8dcca"
            self.townsOrCounties = "Counties"
            self.updateExamples()
            self.updateEstimate()

    def updateExamples(self,e=None):
        if self.mainEntry.get() == "":
            string = "..."
        else:
            string = self.mainEntry.get()
        if self.townsOrCounties == "Counties":
            list = self.counties
        else:
            list = self.towns
        for i in range(3):
            labelText = string + " " + list[i] + " Ma"
            self.examples[i].destroy()
            self.examples[i] = Label(self.exampleFrame,bg="#f4f4f4",borderwidth=0,text=labelText,font=("Franklin Gothic Medium",9))
            self.examples[i].pack(fill="x")

    def cancel(self,e):
        self.window.destroy()

    def getDirectory(self):
        self.settingsDict['saveDirectory'] = filedialog.askdirectory()
        self.window.focus_force()

    def getTime(self,totalSeconds):
        days = int(totalSeconds/(3600*24))
        seconds = totalSeconds % (3600*24)
        hours = int(seconds/3600)
        seconds = seconds % (3600)
        minutes = int(seconds/60)
        if days > 0:
            return str(days) + " days " + str(hours) + " hours " + str(minutes) + " minutes "
        else:
            return str(hours) + " hours " + str(minutes) + " minutes "

    def updateEstimate(self,e=None):
        if self.townsOrCounties == "Towns":
            numSearches = len(self.towns)
        else:
            numSearches = len(self.counties)
        resultsPerSearch = self.slider.get()
        timePerResult = 1
        delayPerSearch = 15*60
        estimate = numSearches*(delayPerSearch + (timePerResult*resultsPerSearch))
        self.timeEstimate["text"] = self.getTime(estimate)

    def addSearchToQueue(self):
        self.updateExamples()
        if not self.saveSettings():
            return
        if self.mainEntry.get() == "":
            messagebox.showerror("Not Allowed","Must enter valid base search.")
            self.window.focus_force()
            return
        string = self.mainEntry.get()
        if self.townsOrCounties == "Counties":
            list = self.counties
        else:
            list = self.towns
        for location in list:
            labelText = string + " " + location + " Ma"
            self.scraperGui.addToQueue(True,labelText)
        messagebox.showinfo("Success","Search added to queue. Press \"Begin Queue\" on main screen to begin")
        self.window.destroy()

    def saveSettings(self):
        if self.settingsDict['saveDirectory'] == None:
            messagebox.showerror("Not Allowed","Must choose a file location.")
            self.window.focus_force()
            return False
        self.settingsDict['numGoogResults'] = self.slider.get()
        settingFile = open("settings.dat","wb")
        pickle.dump(self.settingsDict,settingFile)
        settingFile.close()
        return True
