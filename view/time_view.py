from tkinter import *
from controller import Model
from view.base_view import Baseview

class TimeView(Baseview):
    def __init__(self,root) -> None:
        self.root=root
        self.frame=Frame(self.root,width=self.width,height=self.height)
        label = Label(self.frame,text="time profiling")
        label.pack()
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
        copy = Model.TIME_STAMPS.copy()
        if len(copy) > 0:
            start =list(copy.values())[0].start 
        for index,i in enumerate(copy):
            time_stamp = Model.TIME_STAMPS[i]
            beggening = time_stamp.start - start
            time = time_stamp.end -  time_stamp.start
            self.scaler = 50
            # x, y, x+width, y+height, fill='red'
            x = beggening.seconds *self.scaler
            y = index * (self.rectange_height + self.rectange_spacing)
            width = x + (time.seconds ) *self.scaler
            height = y + self.rectange_height
            self.draw_rect( x ,y ,width ,height)    
            
            self.canvas.create_text((x  + width )/2 ,(y +height)/2 -self.rectange_height/3 , text=time_stamp.name , fill="white")
            self.canvas.create_text((x  + width )/2 ,(y +height)/2 , text=str(time.seconds)+' seconds', fill="white")
            self.canvas.create_text((x  + width )/2 ,(y +height)/2 +self.rectange_height/3, text=time_stamp.id, fill="white")
    def draw_rect(self,x1,x2,y1,y2): 
        self.canvas.create_rectangle((x1,x2,y1,y2),fill='red')

    def destroy(self):
        self.frame.destroy()
