#%%
"""
Created By Daesun Lim (CIIA(R), FRM(R))
Bank Risk Quant
My Utility Module 
v1.0.1
"""
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tksheet import Sheet
# JIT은 쓰지말자
vers = "1.0.1"
recentupdate = '20251221'

#############################################################################################################
#TK GUI Tool
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

def make_listvariable_interface(frame, VariableName, MyList, listheight = 5,textfont = 12, anchor = 'w', padx = 5, pady = 2, bold = False, titlelable = False, titleName = "", defaultflag = False, defaultvalue = 0, width = 20, DefaultStringList = []) : 
    
    myfont = ("맑은 고딕", textfont) if bold == False else ("맑은 고딕", textfont)
    if titlelable == True : 
        tk.Label(frame, text = titleName, font = ("맑은 고딕", textfont, 'bold')).pack(anchor = anchor, padx = padx, pady = pady)    
    
    tk.Label(frame, text = VariableName, font = myfont).pack(anchor = anchor, padx = padx, pady = pady)    
    listbox = tk.Listbox(frame, height = listheight, exportselection = False, width = width)
    for item in MyList : 
        if "|" not in item : 
            listbox.insert(tk.END, str(item))
        else : 
            mystr = item.split("|")
            mystr1 = mystr[0]
            mystr2 = mystr[1]
            lenmystr1 = len(mystr1)
            lenmystr2 = len(mystr2)
            needstradd1 = max(0, 8 - lenmystr1)
            needstradd2 = max(0, 8 - lenmystr2)
            MyString1 = mystr1 + (" " * needstradd1)
            MyString2 = mystr2 + (" " * needstradd2)
            listbox.insert(tk.END, str(MyString1 + " | " + MyString2))            
    
    listbox.pack(anchor = anchor, padx = padx, pady = pady)
    if defaultflag == True and len(DefaultStringList) == 0: 
        listbox.selection_set(defaultvalue)
    elif defaultflag == True and len(DefaultStringList) > 0 : 
        TempList = []
        for i in range(len(DefaultStringList)) : 
            targetinstring = DefaultStringList[i]
            if ',' not in targetinstring : 
                for j in range(len(MyList)) : 
                    TotalString = MyList[j]
                    if targetinstring.lower() in TotalString.lower() : 
                        listbox.selection_set(j)
                        TempList.append(j)
                        break             
    return listbox

def make_multilistvariable_interface(frame, VariableName, MyList, listheight = 5,textfont = 12, anchor = 'w', padx = 5, pady = 2, bold = False, titlelable = False, titleName = "", defaultflag = False, defaultvalue = 0, width = 20, DefaultStringList = []) : 
    n = len(MyList)
    myfont = ("맑은 고딕", textfont) if bold == False else ("맑은 고딕", textfont)
    if titlelable == True : 
        tk.Label(frame, text = titleName, font = ("맑은 고딕", textfont, 'bold')).pack(anchor = anchor, padx = padx, pady = pady)    
    
    tk.Label(frame, text = VariableName, font = myfont).pack(anchor = anchor, padx = padx, pady = pady)    
    listbox = tk.Listbox(frame, selectmode="multiple", height = listheight, exportselection = False, width = width)
    for item in MyList : 
        if "|" not in item : 
            listbox.insert(tk.END, str(item))
        else : 
            mystr = item.split("|")
            mystr1 = mystr[0]
            mystr2 = mystr[1]
            lenmystr1 = len(mystr1)
            lenmystr2 = len(mystr2)
            needstradd1 = max(0, 8 - lenmystr1)
            needstradd2 = max(0, 8 - lenmystr2)
            MyString1 = mystr1 + (" " * needstradd1)
            MyString2 = mystr2 + (" " * needstradd2)
            listbox.insert(tk.END, str(MyString1 + " | " + MyString2))            
    
    listbox.pack(anchor = anchor, padx = padx, pady = pady)
    if defaultflag == True and '[' not in str(defaultvalue) and len(DefaultStringList) == 0: 
        listbox.selection_set(defaultvalue)
    elif defaultflag == True and '[' in str(defaultvalue) and len(DefaultStringList) == 0:         
        for i in defaultvalue : 
            if i < 0 : 
                listbox.selection_set(n + i)
            else : 
                listbox.selection_set(i)
    elif defaultflag == True and len(DefaultStringList) > 0 : 
        TempList = []
        for i in range(len(DefaultStringList)) : 
            targetinstring = DefaultStringList[i]
            if ',' not in targetinstring : 
                for j in range(len(MyList)) : 
                    TotalString = MyList[j]
                    if targetinstring.lower() in TotalString.lower() : 
                        listbox.selection_set(j)
                        TempList.append(j)
                        break                        
            else : 
                targetinstring1 = targetinstring.split(",")[0].lower()
                targetinstring2 = targetinstring.split(",")[1].lower()
                for j in range(len(MyList)) : 
                    TotalString = MyList[j]
                    if targetinstring1 in TotalString.lower() and targetinstring2 in TotalString.lower() : 
                        listbox.selection_set(j)
                        TempList.append(j)
                        break                        
                
        if len(TempList) < len(DefaultStringList) and '[' not in str(defaultvalue): 
            listbox.selection_set(defaultvalue) 
        elif len(TempList) < len(DefaultStringList) and '[' in str(defaultvalue): 
            listbox.selection_set(defaultvalue[0] if defaultvalue[0] not in TempList else defaultvalue[1])                               
            
    return listbox

def insert_dataframe_to_treeview(treeview, dataframe, width = 50):
    # 기존 컬럼과 데이터 제거
    treeview.delete(*treeview.get_children())
    treeview["columns"] = list(dataframe.columns)
    treeview["show"] = "headings"

    # 컬럼 헤더 설정
    for col in dataframe.columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=width, anchor="center")  # 너비 설정 가능

    # 데이터 삽입
    for _, row in dataframe.iterrows():
        treeview.insert("", tk.END, values=list(row))
    return 1

def AddVariableSheet(frame, nindexs, ncolumns, targetcolumns = [], defaultvalues = (), VariableName = "TempVariables", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 100, sheet_height = 30, titlelable = False, titleName = "", MaxHeight = 10000, headerfont = 11) : 

    if titlelable == True : 
        tk.Label(frame, text = titleName, font = ("맑은 고딕", myfont, 'bold')).pack(anchor = anchor, padx = padx, pady = pady)    

    tk.Label(frame, text = VariableName, font = ("맑은 고딕", myfont, 'bold')).pack(anchor = anchor, padx = padx, pady = pady)    
    if len(defaultvalues) > 0 : 
        s = 0
        for i in range(len(defaultvalues)) : 
            s = max(len(defaultvalues[i]), s)
        nindexs = s
        ncolumns = len(defaultvalues)
        targetcolumns = targetcolumns[:ncolumns]

    data = [[""] * ncolumns for i in range(nindexs)]
    if len(defaultvalues) > 0 : 
        for i in range(nindexs) : 
            for j in range(min(ncolumns, len(defaultvalues))) : 
                data[i][j] = defaultvalues[j][i]
    width_ = sheet_width * (len(targetcolumns) if len(targetcolumns) > 0 else ncolumns)
    height_ = max(2,min(MaxHeight, len(data))) * sheet_height + 1
    
    sheet = Sheet(
        frame,
        data=data,
        headers=targetcolumns if len(targetcolumns) == ncolumns else list(np.arange(1,ncolumns+1)),
        height=height_,
        show_x_scrollbar=True,
        show_y_scrollbar=True,
        width= width_,
        header_font=("맑은 고딕", headerfont, "bold")
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

def interface_basic_settings(Name = 'Screen', geometry = "1530x770+5+5") : 
    root = tk.Tk()
    root.title(Name)
    root.geometry(geometry)
    root.resizable(False, False)

    # Scrollbar
    v_scroll = tk.Scrollbar(root, orient="vertical", width=22)
    v_scroll.pack(side="right", fill="y")

    h_scroll = tk.Scrollbar(root, orient="horizontal", width=22)
    h_scroll.pack(side="bottom", fill="x")

    # Canvas
    canvas = tk.Canvas(
        root,
        yscrollcommand=v_scroll.set,
        xscrollcommand=h_scroll.set
    )
    canvas.pack(side="left", fill="both", expand=True)

    # Frame 크기 변경 시 scroll 영역 갱신
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    v_scroll.config(command=canvas.yview)
    h_scroll.config(command=canvas.xview)

    # 실제 컨텐츠 Frame
    main_frame = tk.Frame(canvas)

    canvas_window = canvas.create_window(
        (0, 0),
        window=main_frame,
        anchor="nw"
    )

    main_frame.bind(
        "<Configure>",
        on_frame_configure
    )
    return root, v_scroll, h_scroll, canvas, main_frame, canvas_window

def get_from_sheetinterface(sheet) : 
    df = pd.DataFrame(
        sheet.get_sheet_data(),
        columns=sheet.headers()
    )  
    return df.applymap(lambda x : np.nan if len(str(x)) == 0 else x).dropna(axis = 0, how = 'all')


if __name__ == "__main__" : 
    print("######################################\nCreated By Daesun Lim (CIIA(R), FRM(R))\nRisk Validation Quant\nMy FRTB Module \n"+vers+" (RecentUpdated :" +recentupdate + ")" + "\n######################################\n")
