from dataclasses import dataclass


@dataclass
class Baseview():
    width:int = 500
    height:int = 500
    color:str = '#FFFFFF'
    canvas_scaler:int=40
    rectange_height:int = 60
    rectange_spacing:int = 5 