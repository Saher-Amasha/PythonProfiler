from dataclasses import dataclass


@dataclass
class Baseview:
    ALL_THREADS:str = "All_THREADS"
    width:int = 500
    height:int = 500
    color:str = '#FFFFFF'
    canvas_scaler:int=1000
    rectange_height:int = 60
    rectange_width:int = 20
    rectange_spacing:int = 5 
    def draw_rect(self,x1,x2,y1,y2,fill='red'): 
        self.canvas.create_rectangle((x1,x2,y1,y2),fill=self.num_to_color(abs(fill)))
    def destroy(self):
        self.frame.destroy()
    def num_to_color(self,number):
        match number%5:
            case 0:
                return 'red'
            case 1 :
                return 'blue'
            case 2 : 
                return 'green'
            case 3 :
                return 'brown'
            case 4 :
                return 'purple'
    @staticmethod
    def show(label,clicked): 
        label.config( text = clicked.get() ) 