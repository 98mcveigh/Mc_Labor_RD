import pickle
from tkinter import *
from tkinter import filedialog

def getInitialSettings():
    init = Tk()
    init.geometry("400x200")
    init.resizable(False,False)
    init.title("Establish Settings")
    settingDict = {'saveDirectory':None,'numGoogResults':None}
    def getDir():
        settingDict['saveDirectory'] = filedialog.askdirectory()
        init.focus_force()

    def saveSettings():
        settingDict['numGoogResults'] = slider.get()
        settingFile = open("settings.dat","wb")
        pickle.dump(settingDict,settingFile)
        settingFile.close()
        init.destroy()

    highFrame = Frame(init,width=400,height=50)
    highFrame.place(x=0,y=0)
    folderFrame = Frame(init,width=400,height=50)
    folderFrame.place(x=0,y=50)
    numSearchFrame = Frame(init,width=400,height=50)
    numSearchFrame.place(x=0,y=100)
    finishFrame = Frame(init,width=400,height=50)
    finishFrame.place(x=0,y=150)

    titleLabel = Label(highFrame,text="Establish settings. Settings can be changed later.")
    titleLabel.place(relx=0.5,rely=0.5,anchor=CENTER)

    folderLabel = Label(folderFrame,text="Select folder to store Excel files:")
    folderLabel.place(rely=0.5,relx=0.25,anchor=CENTER)

    folderButton = Button(folderFrame,text="Select Folder...",command=getDir)
    folderButton.place(rely=0.5,relx=0.75,anchor=CENTER)

    sliderLabel = Label(numSearchFrame,text="Number of Google results to search:")
    sliderLabel.place(rely=0.5,relx=0.25,anchor=CENTER)

    slider = Scale(numSearchFrame,from_=0,to=200,orient=HORIZONTAL,resolution=1)
    slider.set(100)
    slider.place(rely=0.5,relx=0.75,anchor=CENTER)

    finishButton = Button(finishFrame,text="Finish",width=12,command=saveSettings)
    finishButton.place(rely=0.5,relx=0.5,anchor=CENTER)

    init.mainloop()

def changeSettings():
    init = Tk()
    init.geometry("400x150")
    init.resizable(False,False)
    init.title("Change Settings")
    saveFile = open("settings.dat","rb")
    settingDict = pickle.load(saveFile)
    saveFile.close()

    def getDir():
        settingDict['saveDirectory'] = filedialog.askdirectory()
        init.focus_force()

    def saveSettings():
        settingDict['numGoogResults'] = slider.get()
        settingFile = open("settings.dat","wb")
        pickle.dump(settingDict,settingFile)
        settingFile.close()
        init.destroy()

    # highFrame = Frame(init,width=400,height=50)
    # highFrame.place(x=0,y=0)
    folderFrame = Frame(init,width=400,height=50)
    folderFrame.place(x=0,y=0)
    numSearchFrame = Frame(init,width=400,height=50)
    numSearchFrame.place(x=0,y=50)
    finishFrame = Frame(init,width=400,height=50)
    finishFrame.place(x=0,y=100)

    # titleLabel = Label(highFrame,text="Establish settings. Settings can be changed later.")
    # titleLabel.place(relx=0.5,rely=0.5,anchor=CENTER)

    folderLabel = Label(folderFrame,text="Select folder to store Excel files:")
    folderLabel.place(rely=0.5,relx=0.25,anchor=CENTER)

    folderButton = Button(folderFrame,text="Select Folder...",command=getDir)
    folderButton.place(rely=0.5,relx=0.75,anchor=CENTER)

    sliderLabel = Label(numSearchFrame,text="Number of Google results to search:")
    sliderLabel.place(rely=0.5,relx=0.25,anchor=CENTER)

    slider = Scale(numSearchFrame,from_=0,to=200,orient=HORIZONTAL,resolution=1)
    slider.set(settingDict['numGoogResults'])
    slider.place(rely=0.5,relx=0.75,anchor=CENTER)

    finishButton = Button(finishFrame,text="Finish",width=12,command=saveSettings)
    finishButton.place(rely=0.5,relx=0.5,anchor=CENTER)

    init.mainloop()
