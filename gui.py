#Import necessary modules - tkinter for gui,main for scraping functionality
from tkinter import *
import main
import threading
import settings

#Create initial window with desired size, color, title and icon
window = Tk()
window.title("Mc Labor R&D")
window.geometry("500x500")
window.configure(bg="#f4f4f4")
window.minsize(300,400)
image1 = PhotoImage(file = "inc/McLaborCropped2.png")
window.iconphoto(False,image1)

#make it so search button appears darker when cursor is over it
def on_enter(e):
    e.widget['background'] = "#dddddd"
    # searchButton['background'] = "#dddddd"
def on_leave(e):
    e.widget['background'] = "#f4f4f4"

#call main scraping function when search button is clicked
def runScraping():
    #create new thread so gui can be responsive during search
    # thread1 = threading.Thread(target=main.main,args=[window,statusLabel,searchEntry])
    # thread1.start()
    # statusLabel["text"] = "Please enter query"
    window.update_idletasks()

def changeSettings():
    settings.changeSettings()
    # TODO: Look into making search settings window if necessary (# sites searched etc.)

#Create and place McLabor logo on 1/5 of the way down in the middle
topFrame = Frame(window)
topFrame.place(relx=0.5,rely=0.2,anchor=CENTER)
image = PhotoImage(file = "inc/McLaborLogo.png")
imLabel = Label(topFrame,image=image,borderwidth=0)
imLabel.pack()

#Create frame for search entry and button in middle of screen
midFrame = Frame(window,bg="black")
midFrame.place(relx=0.5,rely=0.5,anchor=CENTER)

#place search entry and button in the frame
searchEntry = Entry(midFrame,width = 30,insertwidth=1,relief = "flat",justify=CENTER,font=("Franklin Gothic Medium",12))
searchEntry.grid(row=0,column=1,sticky="ns")
searchButton = Button(midFrame,text="SEARCH",bg="#f4f4f4",command=runScraping)
searchButton.configure(activebackground = "#bbbbbb",relief="flat",font=("Franklin Gothic Medium",10))
searchButton.grid(row=1,columnspan=2,sticky="we")

#Establish frame for status label and place it 3/4 down in the middle
bottomFrame = Frame(window)
bottomFrame.place(relx=0.5,rely=0.75,anchor=CENTER)
statusLabel = Label(bottomFrame,text="Enter query and click \"SEARCH\"",bg="#f4f4f4",font=("Franklin Gothic Medium",12))
statusLabel.pack(fill="x")

#call functions to make search button darker when cursor is over it
searchButton.bind("<Enter>", on_enter)
searchButton.bind("<Leave>", on_leave)

#create and place more options button to pull up new window for settings
moreOptionsButton = Button(window,bg="#f4f4f4",activebackground = "#bbbbbb",relief = "flat",text="Settings",font=("Times New Roman",8),command=changeSettings)
moreOptionsButton.bind("<Enter>", on_enter)
moreOptionsButton.bind("<Leave>", on_leave)
moreOptionsButton.pack(side="bottom")

try:
    open("settings.dat")
except FileNotFoundError:
    settings.getInitialSettings()
window.mainloop()
