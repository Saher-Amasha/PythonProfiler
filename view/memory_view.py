from datetime import timedelta
from tkinter import *
from controller import Model

from view.base_view import Baseview


class MemoryView(Baseview):

    def __init__(self,root) -> None:
        self.root=root
        self.frame=Frame(self.root,width=self.width,height=self.height)
        self.frame.pack(fill=X)
        label = Label(self.frame,text="memory profiling",)
        label.pack()
        label2 = Label(self.frame,text="scaler")
        label2.pack()
        self.scaler= IntVar(value=50) 
        self.scaler_backup=self.scaler.get()
        s2 = Scale( self.frame, 
                   variable = self.scaler, 
           from_ = 1, to = 5000, 
           orient = HORIZONTAL,
           length=400)  
        s2.pack()

        label3 = Label(self.frame,text="min_mem kb")
        label3.pack()
        self.min_mem= IntVar(value=1) 
        self.min_time_backup=self.min_mem.get()
        s3 = Scale( self.frame, 
                   variable = self.min_mem, 
           from_ = 0, to = 100, 
           orient = HORIZONTAL,
           length=400)  
        s3.pack()
        self.canvas=Canvas(self.frame,bg=self.color,width=self.width,height=self.height,scrollregion=(0,0,self.width*self.canvas_scaler,self.height*self.canvas_scaler))

        self.data_cleared=False
        self.clear_button=Button( self.frame,text="clear",command=self.clear_data)
        self.clear_button.pack()

        # Create Dropdown menu 
        self.added_threads = False
        self.options = [ 
            Baseview.ALL_THREADS
        ] 
        
        self.thread_id = StringVar() 
        self.thread_id_back_up = self.thread_id.get()
        self.thread_id.set( Baseview.ALL_THREADS) 

        self.drop = OptionMenu( self.frame , self.thread_id , *self.options ) 
        self.drop.pack() 
        
        self.drawn= 0
    def clear_data(self):
        Model.clear_memory_stamps()
        self.data_cleared=True
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
    def __clear(self):
        self.canvas.delete("all")
    def clear(self):
        if (self.min_mem.get() != self.min_time_backup
             or self.scaler_backup != self.scaler.get() 
             or self.thread_id_back_up != self.thread_id.get()
             or self.added_threads
             or self.data_cleared):
            self.__clear()
            self.min_time_backup = self.min_mem.get()
            self.scaler_backup = self.scaler.get()
            self.thread_id_back_up = self.thread_id.get()
            self.added_threads = False
            self.data_cleared = False
            self.drop.pack_forget()
            self.drop = OptionMenu( self.frame , self.thread_id , *self.options ) 
            self.drop.pack(before=self.canvas,fill=X)
            return True
        return False 
    def update(self):
        if self.clear():
             self.drawn = 0
        copy = Model.MEMORY_STAMPS.copy()
        if len(copy) <=0:
            return
        scaler = self.scaler.get()
        mlist = list(copy.values())
        mlist_sorted= sorted(mlist,reverse=True)
        max_mlist = mlist_sorted[-1]
        pushback = 0 
        for index,memory_stamp in enumerate(mlist_sorted):
            memory_leaked = (memory_stamp.end_memory -  memory_stamp.start_memory) / 1000000

            if memory_stamp.thread_id not in self.options:
                     self.drop.option_add(memory_stamp.thread_id,memory_stamp.thread_id)
                     self.options.append(memory_stamp.thread_id)
                     self.added_threads = True

            if memory_leaked <self.min_mem.get() or (memory_stamp.thread_id != self.thread_id.get() and self.thread_id.get() != Baseview.ALL_THREADS):
                     pushback +=1
                     continue

            x = (index- pushback) * (self.rectange_width + self.rectange_spacing)
            y = 0
            width =self.rectange_width
            height = memory_leaked *scaler# it is in kb
            self.draw_rect( x ,y ,x + width ,y + height,hash(memory_stamp.name))    
            self.canvas.create_text(x  + width/2 ,height/2 -height/3 , text=memory_stamp.name , fill="white")
            self.canvas.create_text(x  + width/2 ,height/2 , text='memory_leaked: '+str(memory_leaked), fill="white")
            self.canvas.create_text(x  + width/2 ,height/2 +height/3, text=memory_stamp.id, fill="white")
            if self.added_threads:
                 return False