#!/usr/bin/python3

from tkinter import * # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
from tkinter import messagebox

top = Tk()
top.geometry("400x500")
def hello():
    msg = messagebox.showinfo("Spotter Bot", "Live Stream")

def bye():
    msg = messagebox.showinfo("Spotter Bot", "mp4")

b = Button(top, text = "Live Stream", command = hello)
b.place(x = 75, y = 250)
c = Menubutton(top, text = "Recorded", relief = RAISED)
c.place(x = 275, y = 250)
c.menu = Menu(c, tearoff = 0)
c["menu"] = c.menu

mp4_1 = IntVar()
mp4_2 = IntVar()
c.menu.add_checkbutton ( label = "mp4_1",
                          variable = mp4_1 )
c.menu.add_checkbutton ( label = "mp4_2",
                          variable = mp4_2 )

var = StringVar()
w = Label(top, textvariable = var, pady = 50, font = ("Helvetica", 16, "bold"))
var.set("Welcome to Spotter!")
w.pack()
top.mainloop()
