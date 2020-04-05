#Import necessary modules - tkinter for gui,siteScraping for scraping functionality
from tkinter import *
from tkinter import messagebox
import McLaborScraper.siteScraping as siteScraping
import threading
import McLaborScraper.settings as settings


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
        self.image1 = PhotoImage(file = "McLaborScraper/inc/McLaborCropped2.png")
        self.window.iconphoto(False,self.image1)
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
        self.midFrame = Frame(self.window,bg="black")
        self.midFrame.place(relx=0.5,rely=0.45,anchor="n")

        #place search entry and button in the frame
        self.searchEntry = Entry(self.midFrame,width = 30,insertwidth=1,relief = "flat",justify=CENTER,font=("Franklin Gothic Medium",12))
        self.searchEntry.grid(row=0,columnspan=2,sticky="ns")
        self.searchButton = Button(self.midFrame,text="Individual Search",bg="#f4f4f4",command=self.runScraping,width=15)
        self.searchButton.configure(activebackground = "#bbbbbb",relief="flat",font=("Franklin Gothic Medium",10))
        self.searchButton.grid(row=1,column=0,sticky="ew")

        #Establish frame for status label and place it 3/4 down in the middle
        self.bottomFrame = Frame(self.window)
        self.bottomFrame.place(relx=0.5,rely=0.9,anchor=CENTER)
        self.statusLabel = Label(self.bottomFrame,text="",bg="#f4f4f4",font=("Franklin Gothic Medium",12))
        self.statusLabel.pack(fill="x")

        #call functions to make search button darker when cursor is over it
        self.searchButton.bind("<Enter>", self.on_enter)
        self.searchButton.bind("<Leave>", self.on_leave)

        #create and place more options button to pull up new window for settings
        self.moreOptionsButton = Button(self.window,bg="#f4f4f4",activebackground = "#bbbbbb",relief = "flat",text="Settings",font=("Times New Roman",8),command=self.changeSettings)
        self.moreOptionsButton.bind("<Enter>", self.on_enter)
        self.moreOptionsButton.bind("<Leave>", self.on_leave)
        self.moreOptionsButton.pack(side="bottom")

        self.queueButton = Button(self.midFrame,text="Add Search To Queue",bg="#f4f4f4",command=self.addToQueue,width=15)
        self.queueButton.configure(activebackground = "#bbbbbb",relief="flat",font=("Franklin Gothic Medium",10))
        self.queueButton.bind("<Enter>", self.on_enter)
        self.queueButton.bind("<Leave>", self.on_leave)
        self.queueButton.grid(row=1,column=1,sticky="ew")

        self.queueFrame = Frame(self.midFrame,bg="#f4f4f4")
        self.queueFrame.grid(row=2,columnspan=2,sticky="ew")

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
        self.startStopQueueButton.grid(row=3,columnspan=2,sticky="ew")
        self.startStopQueueButton.bind("<Enter>", self.on_enter)
        self.startStopQueueButton.bind("<Leave>", self.on_leave)

        try:
            open("settings.dat")
        except FileNotFoundError:
            settings.getInitialSettings()
        self.window.mainloop()


    #make it so search button appears darker when cursor is over it
    def on_enter(self,e):
        e.widget['background'] = "#dddddd"

    def on_leave(self,e):
        e.widget['background'] = "#f4f4f4"

    #call site scraping function when search button is clicked
    def runScraping(self):
        #create new thread so gui can be responsive during search
        if self.searchEntry.get() == "":
            messagebox.showerror("Not Allowed","Please enter a valid search.")
        else:
            if self.searchIsRunning[0]:
                messagebox.showerror("Not Allowed","Multiple searches can not be run at the same time.")
            else:
                scraperThread = threading.Thread(target=siteScraping.scrape,args=[self.window,self.statusLabel,self.searchEntry.get(),self.searchIsRunning])
                scraperThread.start()

    def changeSettings(self):
        if self.searchIsRunning[0]:
            messagebox.showerror("Not Allowed","Must change settings in between searches.")
        else:
            settings.changeSettings()

    def addToQueue(self):
        if self.searchEntry.get() == "":
            messagebox.showerror("Not Allowed","Please enter a valid search.")
        else:
            self.queue.append(self.searchEntry.get())
            self.queueLabels.append(Label(self.scrollFrame,anchor=CENTER,text=self.searchEntry.get(),bg="#f4f4f4",font=("Franklin Gothic Medium",8)))
            self.queueLabels[len(self.queueLabels)-1].pack(fill="x")
            self.searchEntry.delete(0,'end')
            self.configScroll()

    def runOrPauseQueue(self):
        if self.startStopQueueButton["text"] == "Begin Queue":
            if self.searchIsRunning[0]:
                messagebox.showerror("Not Allowed","Can not start queue while another search is running.")
            else:
                self.startStopQueueButton["text"] = "Pause Queue"
                scraperThread = threading.Thread(target=siteScraping.runScrapingLoop,args=[self.window,self.statusLabel,self.searchEntry,self.startStopQueueButton,self.queueLabels,self.searchIsRunning])
                scraperThread.start()
        else:
            self.startStopQueueButton["text"] = "Begin Queue"

    def configScroll(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),height=100,width=50)

def beginScraper():
    scraperGui()