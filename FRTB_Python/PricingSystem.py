#%%
"""
Created By Daesun Lim (CIIA(R), FRM(R))
Bank Risk Quant
My FRTB Module 
v1.2.2
"""
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tksheet import Sheet
from packaging import version
import requests
# JIT은 쓰지말자
#from numba import jit
import warnings
import os

def Linterp(x, y, targetx, extrapolateflag = 0) : 
    if extrapolateflag == 0 or len(x) == 1: 
        return np.interp(targetx, np.array(x), np.array(y))
    else : 
        if targetx < x[0] : 
            return (y[1] - y[0]) / (x[1] - x[0]) * (targetx - x[0]) + y[0]
        elif targetx > x[len(x) - 1] : 
            return (y[len(x) - 1] - y[len(x) - 2]) / (x[len(x) - 1] - x[len(x) - 2]) * (targetx - x[len(x) - 1]) + y[len(x) - 1]
        else : 
            return np.interp(targetx, np.array(x), np.array(y))

def Linterp2D(XCol, YInd, Values2D, TargetX, TargetY) : 
    XCol = np.array(XCol)
    YInd = np.array(YInd)    
    try : 
        if len(TargetX) == 1 and len(TargetY) == 1 : 
            TargetX, TargetY = TargetX[0], TargetY[0]
            if TargetX <= XCol[0] and TargetY <= YInd[0] : 
                return Values2D[0][0]
            elif TargetX >= XCol[-1] and TargetY >= YInd[-1] : 
                return Values2D[-1][-1]
            idxX2 = np.where(XCol - TargetX > 0)[0][0] if TargetX < XCol[-1] else len(XCol) - 1
            idxX1 = max(0, idxX2 - 1)
            idxY2 = np.where(YInd - TargetY > 0)[0][0] if TargetY < YInd[-1] else len(YInd) - 1
            idxY1 = max(0, idxY2 - 1)
            SlopeX = (Values2D[idxY1, idxX2] - Values2D[idxY1, idxX1])/(XCol[idxX2]-XCol[idxX1]) if idxX2 != idxX1 else 0
            SlopeY = (Values2D[idxY2, idxX1] - Values2D[idxY1, idxX1])/(YInd[idxY2]-YInd[idxY1]) if idxY2 != idxY1 else 0
            return Values2D[idxY1, idxX1] + SlopeX * (TargetX - XCol[idxX1]) + SlopeY * (TargetY - YInd[idxY1])
        else :
            def TempFunction(TargetX, TargetY) : 
                if TargetX <= XCol[0] and TargetY <= YInd[0] : 
                    return Values2D[0][0]
                elif TargetX >= XCol[-1] and TargetY >= YInd[-1] : 
                    return Values2D[-1][-1]
                idxX2 = np.where(XCol - TargetX > 0)[0][0] if TargetX < XCol[-1] else len(XCol) - 1
                idxX1 = max(0, idxX2 - 1)
                idxY2 = np.where(YInd - TargetY > 0)[0][0] if TargetY < YInd[-1] else len(YInd) - 1
                idxY1 = max(0, idxY2 - 1)
                SlopeX = (Values2D[idxY1, idxX2] - Values2D[idxY1, idxX1])/(XCol[idxX2]-XCol[idxX1]) if idxX2 != idxX1 else 0
                SlopeY = (Values2D[idxY2, idxX1] - Values2D[idxY1, idxX1])/(YInd[idxY2]-YInd[idxY1]) if idxY2 != idxY1 else 0
                return Values2D[idxY1, idxX1] + SlopeX * (TargetX - XCol[idxX1]) + SlopeY * (TargetY - YInd[idxY1])
            return np.vectorize(TempFunction)(TargetX, TargetY)        
    except TypeError : 
        if TargetX <= XCol[0] and TargetY <= YInd[0] : 
            return Values2D[0][0]
        elif TargetX >= XCol[-1] and TargetY >= YInd[-1] : 
            return Values2D[-1][-1]
        idxX2 = np.where(XCol - TargetX > 0)[0][0] if TargetX < XCol[-1] else len(XCol) - 1
        idxX1 = max(0, idxX2 - 1)        
        idxY2 = np.where(YInd - TargetY > 0)[0][0] if TargetY < YInd[-1] else len(YInd) - 1
        idxY1 = max(0, idxY2 - 1)
        SlopeX = (Values2D[idxY1, idxX2] - Values2D[idxY1, idxX1])/(XCol[idxX2]-XCol[idxX1]) if idxX2 != idxX1 else 0
        SlopeY = (Values2D[idxY2, idxX1] - Values2D[idxY1, idxX1])/(YInd[idxY2]-YInd[idxY1]) if idxY2 != idxY1 else 0
        return Values2D[idxY1, idxX1] + SlopeX * (TargetX - XCol[idxX1]) + SlopeY * (TargetY - YInd[idxY1])        

def make_variable_interface(frame, VariableName, textfont = 12, anchor = 'w', padx = 5, pady = 2, bold = False, titlelable = False, titleName = "", defaultflag = False, defaultvalue = None) : 
    
    myfont = ("맑은 고딕", textfont) if bold == False else ("맑은 고딕", textfont, 'bold')
    if titlelable == True : 
        tk.Label(frame, text = titleName, font = ("맑은 고딕", textfont, 'bold')).pack(anchor = anchor, padx = padx, pady = pady)    
        
    tk.Label(frame, text = VariableName, font = myfont).pack(anchor = anchor, padx = padx, pady = pady)    
    entry = tk.Entry(frame)
    if defaultflag == True : 
        entry.insert(0, defaultvalue)
    entry.pack(anchor = anchor, padx = padx, pady = pady)
    return entry


def AddVariableSheet(frame, nindexs, ncolumns, targetcolumns = [], defaultvalues = (), VariableName = "TempVariables", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 100, sheet_height = 30) : 
    tk.Label(frame, text = VariableName, font = myfont).pack(anchor = anchor, padx = padx, pady = pady)    

    data = [[""] * ncolumns for i in range(nindexs)]
    if len(defaultvalues) > 0 : 
        for i in range(nindexs) : 
            for j in range(min(ncolumns, len(defaultvalues))) : 
                data[i][j] = defaultvalues[j][i]
    width_ = sheet_width * (len(targetcolumns) if len(targetcolumns) > 0 else ncolumns)
    height_ = (len(data) + 1) * sheet_height + 5
    
    sheet = Sheet(
        frame,
        data=data,
        headers=targetcolumns if len(targetcolumns) == ncolumns else list(np.arange(1,ncolumns+1)),
        height=height_,
        show_x_scrollbar=True,
        show_y_scrollbar=True,
        width= width_
    )

    sheet.enable_bindings(
    "single_select",
    "row_select",
    "column_select",
    "drag_select",
    "edit_cell",
    "copy",
    "paste",
    "delete",
    "undo",
    "redo",
    "rc_select"
    )
    # 없으면 안보일 수 있음
    sheet.pack(anchor="w")
    return sheet

def get_from_sheetinterface(sheet) : 
    df = pd.DataFrame(
        sheet.get_sheet_data(),
        columns=sheet.headers()
    )  
    return df

root = tk.Tk()
root.title("Screen")
root.geometry("1500x750+30+30")
root.resizable(False, False)
left_frame = tk.Frame(root)
left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

defaultvalues = ([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], [3.5, 3.6, 3.65, 3.66, 3.71, 3.81])
targetcolumns = ["Term", "Rate", "Col3"]
nindexs = 6
ncolumns = 3
v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(20260627))

center_frame = tk.Frame(root)
center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
mysheet = AddVariableSheet(center_frame, nindexs = 100, ncolumns= 100,targetcolumns = [], defaultvalues = (), VariableName = "TempVariables", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 300, sheet_height = 300)
mysheet.set_all_column_widths(width=50)
#mysheet2 = AddVariableSheet(center_frame, ["index","Holidays"], nindexs, 1, defaultvalues = (), VariableName = "TempVariables2", myfont = 12, anchor = 'w', padx = 5, pady = 2)

Result_frame = tk.Frame(root)
Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
ResultValue = pd.DataFrame([])
ResultValue2 = pd.DataFrame([])
MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultValue, ResultValue2]
def run_function(MyArrays) : 
    PrevTreeFlag = MyArrays[0] 
    tree = MyArrays[1] 
    scrollbar = MyArrays[2]
    scrollbar2 = MyArrays[3]  
    ResultValue = MyArrays[4]
    ResultValue2 = MyArrays[5]
    df = get_from_sheetinterface(mysheet)
    #r = Linterp(df["Term"].values.astype(np.float64), df["Rate"].values.astype(np.float64), 1.5)
    output_label.config(text = f"\n결과: {np.round(1.0,4)}", font = ("맑은 고딕", 12, 'bold'))
    MyArrays[0] = PrevTreeFlag 
    MyArrays[1] = tree 
    MyArrays[2] = scrollbar
    MyArrays[3] = scrollbar2      
    MyArrays[4] = ResultValue
    MyArrays[5] = df
    df.to_excel("ResultExcel.xlsx",index = False, header=False)
temp_func = lambda : run_function(MyArrays)
tk.Button(left_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
output_label = tk.Label(left_frame, text = "", anchor = "n")
output_label.pack(padx = 5, pady = 2)
root.mainloop()     
# %%frame = left_frame 


# %%
