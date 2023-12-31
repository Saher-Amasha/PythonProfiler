from tkinter import *
from controller import Model

from view.base_view import Baseview


class MemoryView(Baseview):

    def __init__(self,root) -> None:
        self.root=root
        self.frame=Frame(self.root,width=self.width,height=self.height)
        label = Label(self.frame,text="Memory profiling")
        copy = Model.MEMORY_STAMPS.copy()

        mlist = list(copy.values())
        if len(copy) > 0:
            self.canvas=Canvas(self.frame,bg=self.color,width=self.width,height=self.height,scrollregion=(0,0,max(self.rectange_width*len(copy),self.width),max(max(mlist).end_memory -  max(mlist).start_memory,self.height*self.canvas_scaler)))
        else :
            self.canvas=Canvas(self.frame,bg=self.color,width=self.width,height=self.height,scrollregion=(0,0,self.width*self.canvas_scaler,self.height*self.canvas_scaler))
    def draw(self):
        self.frame.pack(expand=True, fill=BOTH)
        
        hbar=Scrollbar(self.frame,orient=HORIZONTAL)
        hbar.pack(side=BOTTOM,fill=X)
        hbar.config(command=self.canvas.xview)
        vbar=Scrollbar(self.frame,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=self.width,height=self.height)
        self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.pack(side=LEFT,expand=True,fill=BOTH)
        self.update()

    def update(self):
        copy = Model.MEMORY_STAMPS.copy()
        if len(copy) <=0:
            return
        mlist = list(copy.values())
        mlist_sorted= sorted(mlist)
        max_mlist=max(mlist)
        for index,i in enumerate(mlist_sorted):
            memory_stamp = i
            memory_leaked = memory_stamp.end_memory -  memory_stamp.start_memory
            if memory_leaked == 0 :
                continue
            self.scaler = 1/10
            x = index * (self.rectange_width + self.rectange_spacing)
            y = (max_mlist.end_memory -  max_mlist.start_memory) *self.scaler
            width = x + self.rectange_width + 50
            height = memory_leaked *self.scaler# it is in kb
            self.draw_rect( x ,y ,width ,height)    
            
            self.canvas.create_text((x  + width )/2 ,(y +height)/2 -self.rectange_height/3 , text=memory_stamp.name , fill="white")
            self.canvas.create_text((x  + width )/2 ,(y +height)/2 , text='memory_leaked: '+str(memory_leaked), fill="white")
            self.canvas.create_text((x  + width )/2 ,(y +height)/2 +self.rectange_height/3, text=memory_stamp.id, fill="white")