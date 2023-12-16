from tkinter import *

from view.base_view import Baseview


class MemoryView(Baseview):

    def __init__(self,root) -> None:
        self.root=root
        self.frame=Frame(self.root,width=self.width,height=self.height)
        label = Label(self.frame,text="Memory profiling")
        label.pack()

    def draw(self):
        self.frame.pack(expand=True, fill=BOTH)
        canvas=Canvas(self.frame,bg=self.color,width=self.width,height=self.height,scrollregion=(0,0,self.width*self.canvas_scaler,self.height*self.canvas_scaler))
        hbar=Scrollbar(self.frame,orient=HORIZONTAL)
        hbar.pack(side=BOTTOM,fill=X)
        hbar.config(command=canvas.xview)
        vbar=Scrollbar(self.frame,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=canvas.yview)
        canvas.config(width=self.width,height=self.height)
        canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        canvas.pack(side=LEFT,expand=True,fill=BOTH)

    def draw_rect(self,x1,x2,y1,y2):
        self.canvas.create_rectangle((x1,x2,y1,y2))
        
    def destroy(self):
        self.frame.destroy()