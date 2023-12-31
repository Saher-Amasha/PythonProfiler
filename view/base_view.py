from dataclasses import dataclass


@dataclass
class Baseview:
    width:int = 500
    height:int = 500
    color:str = '#FFFFFF'
    canvas_scaler:int=40
    rectange_height:int = 60
    rectange_width:int = 20
    rectange_spacing:int = 5 
    def draw_rect(self,x1,x2,y1,y2): 
        self.canvas.create_rectangle((x1,x2,y1,y2),fill='red')
    def destroy(self):
        self.frame.destroy()
