import tkinter
from PIL import ImageTk,Image

class mainWindow:
    TITLE = "Python profiler"
    def __init__(self) -> None:
        self.root = tkinter.Tk() 


        # Set title
        self.root.title=mainWindow.TITLE


        # Set logo
        logo = ImageTk.PhotoImage(file="resources/profiling_logo.png")
        self.root.iconphoto(True,logo)
        self.root.iconbitmap(default=None)


        # set buttons to move between views
        self.timeButton=tkinter.Button( self.root,text="time",command=self.time_window)
        self.timeButton.grid(row=0,column=0)

        self.memoryButton=tkinter.Button( self.root,text="memory",command=self.mem_window)
        self.memoryButton.grid(row=0,column=1)
        
        self.networkButton=tkinter.Button( self.root,text="network",command=self.network_window)
        self.networkButton.grid(row=0,column=2,columnspan=5,sticky='w')
    
    def mem_window(self):
        label = tkinter.Label(self.root,text="memory profiling")
        label.grid(row=1,column=1)
    
    def time_window(self):
        label = tkinter.Label(self.root,text="time profiling")
        label.grid(row=1,column=1)
    
    def network_window(self):
        label = tkinter.Label(self.root,text="network profiling")
        label.grid(row=1,column=1)

    def run(self):
        # Event loop 
        self.root.mainloop()