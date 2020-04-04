#Import necessary modules - tkinter for gui,main for scraping functionality
from tkinter import *
from tkinter import messagebox
import main
import threading
import settings

#Create initial window with desired size, color, title and icon
window = Tk()
window.title("Mc Labor R&D")
window.geometry("500x500")
window.configure(bg="#f4f4f4")
window.minsize(300,500)
image1 = PhotoImage(file = "inc/McLaborCropped2.png")
window.iconphoto(False,image1)

searchIsRunning = [False]
#make it so search button appears darker when cursor is over it
def on_enter(e):
    e.widget['background'] = "#dddddd"

def on_leave(e):
    e.widget['background'] = "#f4f4f4"

queue = []
queueLabels = []
#call main scraping function when search button is clicked
def runScraping():
    #create new thread so gui can be responsive during search
    if searchIsRunning[0]:
        messagebox.showerror("Not Allowed","Multiple searches can not be run at the same time.")
    else:
        thread1 = threading.Thread(target=main.main,args=[window,statusLabel,searchEntry.get(),searchIsRunning])
        thread1.start()

def changeSettings():
    if searchIsRunning[0]:
        messagebox.showerror("Not Allowed","Must change settings in between searches.")
    else:
        settings.changeSettings()

def addToQueue():
    if searchEntry.get() == "":
        messagebox.showerror("Not Allowed","Please enter a valid search.")
    else:
        queue.append(searchEntry.get())
        queueLabels.append(Label(scrollFrame,anchor=CENTER,text=searchEntry.get(),bg="#f4f4f4",font=("Franklin Gothic Medium",8)))
        queueLabels[len(queueLabels)-1].pack(fill="x")
        searchEntry.delete(0,'end')
        configScroll()

def runOrPauseQueue():
    if startStopQueueButton["text"] == "Begin Queue":
        if searchIsRunning[0]:
            messagebox.showerror("Not Allowed","Can not start queue while another search is running.")
        else:
            startStopQueueButton["text"] = "Pause Queue"
            thread1 = threading.Thread(target=main.runMainLoop,args=[window,statusLabel,searchEntry,startStopQueueButton,queueLabels,searchIsRunning])
            thread1.start()
    else:
        startStopQueueButton["text"] = "Begin Queue"

def configScroll():
    canvas.configure(scrollregion=canvas.bbox("all"),height=100,width=50)


#Create and place McLabor logo on 1/5 of the way down in the middle
topFrame = Frame(window)
topFrame.place(relx=0.5,rely=0.2,anchor=CENTER)
image = PhotoImage(file = "inc/McLaborLogo.png")
imLabel = Label(topFrame,image=image,borderwidth=0)
imLabel.pack()

#Create frame for search entry and button in middle of screen
midFrame = Frame(window,bg="black")
midFrame.place(relx=0.5,rely=0.45,anchor="n")

#place search entry and button in the frame
searchEntry = Entry(midFrame,width = 30,insertwidth=1,relief = "flat",justify=CENTER,font=("Franklin Gothic Medium",12))
searchEntry.grid(row=0,columnspan=2,sticky="ns")
searchButton = Button(midFrame,text="Individual Search",bg="#f4f4f4",command=runScraping,width=15)
searchButton.configure(activebackground = "#bbbbbb",relief="flat",font=("Franklin Gothic Medium",10))
searchButton.grid(row=1,column=0,sticky="ew")

#Establish frame for status label and place it 3/4 down in the middle
bottomFrame = Frame(window)
bottomFrame.place(relx=0.5,rely=0.9,anchor=CENTER)
statusLabel = Label(bottomFrame,text="",bg="#f4f4f4",font=("Franklin Gothic Medium",12))
statusLabel.pack(fill="x")

#call functions to make search button darker when cursor is over it
searchButton.bind("<Enter>", on_enter)
searchButton.bind("<Leave>", on_leave)

#create and place more options button to pull up new window for settings
moreOptionsButton = Button(window,bg="#f4f4f4",activebackground = "#bbbbbb",relief = "flat",text="Settings",font=("Times New Roman",8),command=changeSettings)
moreOptionsButton.bind("<Enter>", on_enter)
moreOptionsButton.bind("<Leave>", on_leave)
moreOptionsButton.pack(side="bottom")

queueButton = Button(midFrame,text="Add Search To Queue",bg="#f4f4f4",command=addToQueue,width=15)
queueButton.configure(activebackground = "#bbbbbb",relief="flat",font=("Franklin Gothic Medium",10))
queueButton.bind("<Enter>", on_enter)
queueButton.bind("<Leave>", on_leave)
queueButton.grid(row=1,column=1,sticky="ew")

queueFrame = Frame(midFrame,bg="#f4f4f4")
queueFrame.grid(row=2,columnspan=2,sticky="ew")

canvas = Canvas(queueFrame,bg="#f4f4f4")
scrollFrame=Frame(canvas,bg="#f4f4f4",borderwidth=0)
myscrollbar=Scrollbar(queueFrame,orient="vertical",command=canvas.yview)
canvas.configure(yscrollcommand=myscrollbar.set)
myscrollbar.pack(side="right",fill="y")
canvas.pack(fill="x")
canvas.create_window((0,0),window=scrollFrame,anchor='nw',width=260)
queueLabel = Label(scrollFrame,anchor=CENTER,text="SEARCH QUEUE:",bg="#eaeaea",font=("Franklin Gothic Medium",9))
queueLabel.pack(fill="x")
configScroll()

startStopQueueButton = Button(midFrame,font=("Franklin Gothic Medium",10),activebackground = "#bbbbbb",relief="flat",text="Begin Queue",bg="#f4f4f4",command=runOrPauseQueue,width=30)
startStopQueueButton.grid(row=3,columnspan=2,sticky="ew")
startStopQueueButton.bind("<Enter>", on_enter)
startStopQueueButton.bind("<Leave>", on_leave)

try:
    open("settings.dat")
except FileNotFoundError:
    settings.getInitialSettings()
window.mainloop()
