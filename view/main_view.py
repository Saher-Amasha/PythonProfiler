import threading
from time import sleep
import tkinter
from PIL import ImageTk
from tkinter import *
from view.memory_view import MemoryView

from view.time_view import TimeView

class MainView():
    TITLE = "Python profiler"
    CurrentWindow = None
    def __init__(self) -> None:
        self.root = tkinter.Tk() 


        # Set title
        self.root.title=MainView.TITLE


        # Set logo
        logo = ImageTk.PhotoImage(file="resources/profiling_logo.png")
        self.root.iconphoto(True,logo)
        self.root.iconbitmap(default=None)


        self.buttotns=[]
        self.frames= [] 
        
        # set buttons to move between views
        self.time_button=tkinter.Button( self.root,text="time",command=self.time_window)
        self.time_button.pack()
        self.buttotns.append(self.time_button)
        
        
        self.memoryButton=tkinter.Button( self.root,text="memory",command=self.memory_view)
        self.memoryButton.pack()
        self.buttotns.append(self.memoryButton)
        
        # init to time view 
        self.time_window()

    def update(self):
        if MainView.CurrentWindow != None:
            MainView.CurrentWindow.update() 
    
    def memory_view(self):
        for button in self.buttotns:
            button["state"] = "active"
        for frame in self.frames:
            frame.destroy()
        
        self.memory_view = MemoryView(self.root)
        MainView.CurrentWindow = self.memory_view
        self.frames.append(self.memory_view)
        self.memoryButton["state"] = "disabled"
        self.memory_view.draw()
        
    def time_window(self):
        for button in self.buttotns:
            button["state"] = "active"
        for frame in self.frames:
            frame.destroy()
        self.time_window = TimeView(self.root)
        MainView.CurrentWindow = self.time_window
        self.frames.append(self.time_window)
        self.time_button["state"] = "disabled"
        self.time_window.draw()

    def continues_update(self):
        while True:
            sleep(1)
            self.update()


    def run(self):
        # Event loop 
        threading.Thread(target=self.continues_update).start()
        self.root.mainloop()