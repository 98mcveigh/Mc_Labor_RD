import pickle
from tkinter import *
from tkinter import filedialog

class changeSettings(object):
    """docstring for changeSettings."""

    def __init__(self,mainGui,isInitial = False):
        super(changeSettings, self).__init__()
        self.isInitial = isInitial
        self.init = Toplevel()
        self.init.geometry("400x200")
        self.init.resizable(False,False)
        self.searchResolution = 10
        self.mainGui = mainGui
        if self.isInitial:
            self.init.title("Establish Settings")
            self.settingsDict = {'saveDirectory':None,'numGoogResults':None}
            self.instructionsText = "Establish settings. Settings can be changed at anytime."
        else:
            self.init.title("Change Settings")
            saveFile = open("settings.dat","rb")
            self.settingsDict = pickle.load(saveFile)
            saveFile.close()
            self.instructionsText = "Change settings."

        self.init.iconbitmap("McLaborScraper/inc/McLaborIcon.ico")

        self.highFrame = Frame(self.init,width=400,height=50)
        self.highFrame.place(x=0,y=0)
        self.folderFrame = Frame(self.init,width=400,height=50)
        self.folderFrame.place(x=0,y=50)
        self.numSearchFrame = Frame(self.init,width=400,height=50)
        self.numSearchFrame.place(x=0,y=100)
        self.finishFrame = Frame(self.init,width=400,height=50)
        self.finishFrame.place(x=0,y=150)

        self.titleLabel = Label(self.highFrame,text=self.instructionsText)
        self.titleLabel.place(relx=0.5,rely=0.5,anchor=CENTER)

        self.folderLabel = Label(self.folderFrame,text="Select folder to store Excel files:")
        self.folderLabel.place(rely=0.5,relx=0.25,anchor=CENTER)

        self.folderButton = Button(self.folderFrame,text="Select Folder...",command=self.getDir)
        self.folderButton.place(rely=0.5,relx=0.75,anchor=CENTER)

        self.sliderLabel = Label(self.numSearchFrame,text="Number of Google results to search:")
        self.sliderLabel.place(rely=0.5,relx=0.25,anchor=CENTER)

        if self.settingsDict["numGoogResults"]:
            setpos = self.settingsDict["numGoogResults"]
        else:
            setpos = 150

        self.slider = Scale(self.numSearchFrame,from_=0,to=300,orient=HORIZONTAL,resolution=self.searchResolution)
        self.slider.set(setpos)
        self.slider.place(rely=0.5,relx=0.75,anchor=CENTER)

        self.finishButton = Button(self.finishFrame,text="Finish",width=12,command=self.saveSettings)
        self.finishButton.place(rely=0.5,relx=0.5,anchor=CENTER)

    def getDir(self):
        self.settingsDict['saveDirectory'] = filedialog.askdirectory()
        self.init.focus_force()

    def saveSettings(self):
        self.settingsDict['numGoogResults'] = self.slider.get()
        self.mainGui.settingsDict = self.settingsDict
        settingsFile = open("settings.dat","wb")
        pickle.dump(self.settingsDict,settingsFile)
        settingsFile.close()
        self.init.destroy()
