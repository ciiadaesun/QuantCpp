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
import ctypes as ct
# Windows C/C++ long = 32-bit
c_long_p = ct.POINTER(ct.c_long)
c_double_p = ct.POINTER(ct.c_double)
currdir = os.getcwd()
ReleaseFolder = currdir + "\\x64\\Release\\"    
warnings.filterwarnings('ignore')
today = pd.Timestamp.today()
TimestampToYYYYMMDD = lambda x : x.year * 10000 + x.month * 100 + x.day
today_YYYYMMDD = TimestampToYYYYMMDD(today)
YYYYMMDDToTimeStamp = lambda x : pd.to_datetime(str(x)[:-4] + "-"+str(x)[-4:-2] +"-"+str(x)[-2:])
EDate = lambda x, n : TimestampToYYYYMMDD(YYYYMMDDToTimeStamp(x) + pd.DateOffset(months = n))
MakeSchedule = lambda Start, End, nm : pd.date_range(YYYYMMDDToTimeStamp(Start), YYYYMMDDToTimeStamp(End), freq = pd.DateOffset(months=nm))

IRSdll = ct.WinDLL(ReleaseFolder + "IRS.dll")
CalcIRS = IRSdll.CalcIRS
CalcIRS.restype = ct.c_long
CalcIRS.argtypes = [ct.c_long, ct.c_long, ct.c_long, c_long_p, c_double_p,
                    ct.c_long, ct.c_long,ct.c_double,ct.c_long,ct.c_long,
                    ct.c_double,ct.c_long,ct.c_long,c_double_p,c_double_p,
                    ct.c_long,c_double_p,c_double_p,ct.c_long,c_long_p,
                    c_double_p,c_double_p,c_double_p,ct.c_long,ct.c_long,
                    ct.c_double,ct.c_long,ct.c_long,ct.c_double,ct.c_long,
                    ct.c_long,c_double_p,c_double_p,ct.c_long,c_double_p,
                    c_double_p,ct.c_long,c_long_p,c_double_p,c_double_p,
                    c_double_p,c_double_p,c_double_p,c_double_p,c_double_p,
                    c_double_p,c_double_p,c_double_p,c_long_p,c_long_p,
                    c_long_p,c_long_p,c_long_p,c_long_p,c_double_p,
                    c_double_p,c_long_p,c_long_p,c_double_p,c_double_p]

IRStructuredSwapFDMDLL = ct.WinDLL(ReleaseFolder + "IRStructuredSwapOneCurve.dll")
HWCapHWSwaptionCalib1F = IRStructuredSwapFDMDLL.HWCapHWSwaptionCalibrationForKDB
HWCapHWSwaptionCalib1F.restype = ct.c_long
HWCapHWSwaptionCalib1F.argtypes = [ct.c_long, c_double_p, c_double_p, ct.c_long, c_double_p,
                                    c_double_p, c_double_p, ct.c_double, ct.c_long, c_double_p,
                                    c_double_p, c_double_p, ct.c_long, ct.c_double, ct.c_long,
                                    c_double_p, c_double_p, c_double_p]


def LeapCheck(Year) : 
    Year = int(Year)
    return 1 if ((Year % 4 == 0 and Year % 100 != 0 ) or Year % 400 == 0) else 0

def DaysOfMonth(n) : 
    M = int(n) + 1
    if M in [1, 3, 5, 7, 8, 10, 12] : 
        return 31
    elif M in [4, 6, 9, 11] : 
        return 30
    elif M == 2 : 
        return 28
    elif M == 13 :
        return 31
    elif M == 0 : 
        return 31
    else : 
        raise ValueError("Check The Month (Whether less then 13) Month is " + str(M)) 

def DaysOfMonthLeap(n) : 
    M = int(n) + 1
    if M in [1, 3, 5, 7, 8, 10, 12] : 
        return 31
    elif M in [4, 6, 9, 11] : 
        return 30
    elif M == 2 : 
        return 29
    elif M == 13 :
        return 31
    elif M == 0 : 
        return 31
    else : 
        raise ValueError("Check The Month (Whether less then 13)Month is " + str(M)) 

def CummulativeDays(n) : 
    n = int(n) 
    return [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365][n]

def CummulativeDays_Leap(n) : 
    n = int(n) 
    return [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366][n]

def YYYYMMDDToExcelDate(YYYYMMDD) : 
    YYYYMMDD = int(YYYYMMDD)
    Leap = 0
    Year = int(YYYYMMDD / 10000)
    Month = int((YYYYMMDD - Year * 10000) / 100)
    Day = int((YYYYMMDD - Year * 10000 - Month * 100))
    Leap = LeapCheck(Year) 
    
    #엑셀에서는 1900년도를 윤년 처리함
    if (Year == 1900) :
        Leap = 1     
    
    N4 = int(Year // 4)
    N100 = int(Year // 100)
    N400 = int(Year // 400)
    
    N4_To_1900 = int(1900//4)
    N100_To_1900 = int(1900//100)
    N400_To_1900 = int(1900//400)
    Result = 0
    if (Leap == 1) : 
        if (Month > 2) : 
            Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays(Month - 1) + 1 + Day
        else : 
            Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays(Month - 1) + Day
    else : 
        Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays(Month - 1) + 1 + Day
    return Result        

def ExcelDateToYYYYMMDD(ExcelDate) : 
    
    #
    LeapDaysFor4Year = [0,    366,  731,  1096, 1461, 1827, 2192, 2557, 2922, 3288, 
                        3653, 4018, 4383, 4749, 5114, 5479, 5844, 6210, 6575, 6940, 
                        7305, 7671, 8036, 8401, 8766, 9132, 9497, 9862, 10227, 10593,
                        10958, 11323, 11688, 12054, 12419, 12784, 13149, 13515, 13880, 
                        14245, 14610, 14976, 15341, 15706, 16071, 16437, 16802, 17167,
                        17532, 17898, 18263, 18628, 18993, 19359, 19724, 20089, 20454, 
                        20820, 21185, 21550, 21915, 22281, 22646, 23011, 23376, 23742,
                        24107, 24472, 24837, 25203, 25568, 25933, 26298, 26664, 27029,
                        27394, 27759, 28125, 28490, 28855, 29220, 29586, 29951, 30316,
                        30681, 31047, 31412, 31777, 32142, 32508, 32873, 33238, 33603, 
                        33969, 34334, 34699, 35064, 35430, 35795, 36160, 36525]
    LeapDaysFor4YearNot400 = [0, 365, 730, 1095, 1460, 1826, 2191, 2556, 2921, 3287,
                              3652, 4017, 4382, 4748, 5113, 5478, 5843, 6209, 6574, 6939,
                              7304, 7670, 8035, 8400, 8765, 9131, 9496, 9861, 10226, 10592,
                              10957, 11322, 11687, 12053, 12418, 12783, 13148, 13514, 13879, 14244,
                              14609, 14975, 15340, 15705, 16070, 16436, 16801, 17166, 17531, 17897,
                              18262, 18627, 18992, 19358, 19723, 20088, 20453, 20819, 21184, 21549,
                              21914, 22280, 22645, 23010, 23375, 23741, 24106, 24471, 24836, 25202,
                              25567, 25932, 26297, 26663, 27028, 27393, 27758, 28124, 28489, 28854,
                              29219, 29585, 29950, 30315, 30680, 31046, 31411, 31776, 32141, 32507,
                              32872, 33237, 33602, 33968, 34333, 34698, 35063, 35429, 35794, 36159,
                              36524]
    
    if ExcelDate - 36525 > 0 : 
        ExcelDate = ExcelDate - 36525
        Year = 2000
    else : 
        Year = 1900
    
    nDay_for_400 = 146097
    for i in range(1000) : 
        if (ExcelDate - nDay_for_400 <= 0) : 
            break
        else :
            ExcelDate -= nDay_for_400
            Year += 400
    
    nDay_for_100_400x = 36525
    nDay_for_100 = 36524
    for i in range(5) : 
        if (i % 4 == 0) : 
            if (ExcelDate - nDay_for_100_400x <= 0) : 
                break
            else :
                ExcelDate -= nDay_for_100_400x
                Year += 100
        else : 
            if (ExcelDate - nDay_for_100 <= 0) : 
                break
            else :
                ExcelDate -= nDay_for_100
                Year += 100

    Leap = 0
    
    if (ExcelDate == 0) : 
        Year -= 1
        return Year * 10000 + 1231
    else : 
        Flag_400 = 1 if (i % 4 == 0) else 0
        
        if (Flag_400 == 1) : 
            for i in range(101) : 
                if (ExcelDate - LeapDaysFor4Year[i+1] <= 0) : 
                    ExcelDate = ExcelDate - LeapDaysFor4Year[i]
                    Year += i
                    break
        else : 
            for i in range(101) : 
                if (ExcelDate - LeapDaysFor4YearNot400[i+1] <= 0) : 
                    ExcelDate = ExcelDate - LeapDaysFor4YearNot400[i]
                    Year += i
                    break
        if (ExcelDate == 0) : 
            Year -= 1
            return Year * 10000 + 1231

        Leap = 0
        Leap = LeapCheck(Year)
    
        if (Year == 1900) : 
            Leap = 1
        
        if (Leap == 1) : 
            for m in range(12) : 
                if (CummulativeDays_Leap(m+1) >= ExcelDate and CummulativeDays_Leap(m) < ExcelDate) : 
                    break
            if (m < 12) : 
                Month = m + 1
            else :
                Month = 12
            Day = ExcelDate - CummulativeDays_Leap(m)
        else :
            for m in range(12) : 
                if (CummulativeDays(m+1) >= ExcelDate and CummulativeDays(m) < ExcelDate) :
                    break
            if (m < 12) : 
                Month = m + 1
            else : 
                Month = 12
            Day = ExcelDate - CummulativeDays(m)
        return Year * 10000 + Month * 100 + Day

def istermtype(termlist) : 
    term = np.array(termlist, dtype = np.float64)
    if term.min() >= 19000101 : 
        return "YYYYMMDD"
    elif term.min() > 30.0 : 
        return "ExcelDate"
    else : 
        return "Term"

def DayCountAtoB(Day1, Day2) : 
    return YYYYMMDDToExcelDate(Day2) - YYYYMMDDToExcelDate(Day1)

def Preprocessing_Term(Term, PriceDate) : 
    if len(Term) > 0 : 
        istermtype_ZeroTerm = istermtype(Term)
        if istermtype_ZeroTerm == "YYYYMMDD" : 
            for i in range(len(Term)) : 
                Term[i] = (DayCountAtoB(PriceDate, Term[i])/365)
        elif istermtype_ZeroTerm == "ExcelDate" :
            ExcelPriceDate = YYYYMMDDToExcelDate(PriceDate) if int(PriceDate) >= 19000101 else PriceDate
            for i in range(len(Term)) : 
                Term[i] = ((Term[i] - ExcelPriceDate)/365)

def Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate, CompareNumber = 0.6) : 
    if len(ZeroTerm) > 0 : 
        istermtype_ZeroTerm = istermtype(ZeroTerm)
        if istermtype_ZeroTerm == "YYYYMMDD" : 
            for i in range(len(ZeroTerm)) : 
                ZeroTerm[i] = (DayCountAtoB(PriceDate, ZeroTerm[i])/365)
        elif istermtype_ZeroTerm == "ExcelDate" :
            ExcelPriceDate = YYYYMMDDToExcelDate(PriceDate) if int(PriceDate) >= 19000101 else PriceDate
            for i in range(len(ZeroTerm)) : 
                ZeroTerm[i] = ((ZeroTerm[i] - ExcelPriceDate)/365)
        
        if np.abs(np.array(ZeroRate)).mean() > CompareNumber : 
            for i in range(len(ZeroRate)) : 
                ZeroRate[i] = ZeroRate[i]/100

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

def make_listvariable_interface(frame, VariableName, MyList, listheight = 5,textfont = 12, anchor = 'w', padx = 5, pady = 2, bold = False, titlelable = False, titleName = "", defaultflag = False, defaultvalue = 0, width = 20, DefaultStringList = []) : 
    
    myfont = ("맑은 고딕", textfont) if bold == False else ("맑은 고딕", textfont, 'bold')
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

def get_from_sheetinterface(sheet) : 
    df = pd.DataFrame(
        sheet.get_sheet_data(),
        columns=sheet.headers()
    )  
    return df.applymap(lambda x : np.nan if len(str(x)) == 0 else x).dropna(axis = 0, how = 'all')

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

def arr_double(x):
    a = np.asarray(x, dtype=np.float64)
    return a, a.ctypes.data_as(c_double_p)

def arr_long(x):
    a = np.asarray(x, dtype=np.int32)   # C long이 Windows에서는 32bit
    return a, a.ctypes.data_as(c_long_p)

def interface_basic_settings() : 
    root = tk.Tk()
    root.title("Screen")
    root.geometry("1530x770+5+5")
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

def MainViewer(Title = 'Viewer', MyText = '사용하실 기능은?(번호입력)', MyList = ["1: Pricing 및 CSR, GIRR 간이 시뮬레이션","2: FRTB SA Risk Calculation","3: CurveGenerator","4: IR Swaption ImpliedVol Calculation","5: Cap Floor Implied Vol Calibration",'6: HW Kappa1F VolRatio Calib(미완)','7: 환포지션으로 FXDelta계산'], size = "800x450+30+30", splitby = ":", listheight = 8, textfont = 13, titlelable = False, titleName = "Name", MultiSelection = False, defaultvalue = 0, addtreeflag = False, treedata = pd.DataFrame([]), DefaultStringList = [], width = 95, expand = True) : 
    root = tk.Tk()
    root.title(Title)
    root.geometry(size)
    root.resizable(False, False)
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    if MultiSelection == False : 
        FunctionSelection = make_listvariable_interface(left_frame, MyText, MyList, listheight = listheight, textfont = textfont, defaultflag = True, defaultvalue=(len(MyList) - 1) if defaultvalue < 0 else defaultvalue, width = width, titlelable= titlelable, titleName=titleName, DefaultStringList = DefaultStringList)
    else : 
        FunctionSelection = make_multilistvariable_interface(left_frame, MyText, MyList, listheight = listheight, textfont = textfont, width = width, titlelable= titlelable, titleName=titleName, defaultflag = True, defaultvalue = defaultvalue, DefaultStringList = DefaultStringList)
    FunctionSelected = []
    PrevTreeFlag = 0
    tree, scrollbar, scrollabar2 = None, None, None
    if addtreeflag == True : 
        tree = ttk.Treeview(root)
        treedata = treedata.reset_index().applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=expand)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        PrevTreeFlag = insert_dataframe_to_treeview(tree, treedata, width = 100)
        
    def run_function(FunctionSelected) : 
        if MultiSelection == False : 
            Number = int(str(FunctionSelection.get(FunctionSelection.curselection())).split(splitby)[0]) if FunctionSelection.curselection() else 1
            FunctionSelected.append(Number)
        else : 
            selected_indices = FunctionSelection.curselection()  # 선택된 인덱스들
            selected_values = [FunctionSelection.get(i) for i in selected_indices]
            templst = []
            for v in selected_values : 
                templst.append(int(v.split(splitby)[0]))            
            if len(templst) > 0 : 
                FunctionSelected.append(str(templst).replace("[","").replace("]",""))                
            else : 
                FunctionSelected.append(0)
        if tree : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
        root.destroy()
    temp_function = lambda : run_function(FunctionSelected)
    tk.Button(left_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_function, width = 15).pack()
    root.mainloop()            
    return FunctionSelected[-1] if len(FunctionSelected) > 0 else None    

def MainViewer2(Title = "Viewer", MyText = "데이터인풋", size = "800x450+30+30", textfont = 13, defaultvalue = 0, bold = True) : 
    root = tk.Tk()
    root.title(Title)
    root.geometry(size)
    root.resizable(False, False)
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    Contents = make_variable_interface(left_frame, MyText, bold = bold, textfont = textfont, defaultflag = True, defaultvalue = defaultvalue)
    FunctionSelected = []
    def run_function(FunctionSelected) : 
        Number = str(Contents.get()) if len(str(Contents.get())) else str(defaultvalue)
        FunctionSelected.append(Number)
        root.destroy()
    temp_function = lambda : run_function(FunctionSelected)
    tk.Button(left_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_function, width = 15).pack()
    root.mainloop()            
    return FunctionSelected[-1]   

def ConvertPythonFormatfromVBAformat(VBAString) : 
    TargetDllString = VBAString.split("Lib ")[-1].split(".dll")[0].replace('"',"").replace("'","") + '.dll'
    TargetFunctionString = VBAString.split("Lib ")[0].split("Function")[-1].replace(" ","")
    StringArray = VBAString.split("(")[-1].split(")")[0].replace("\n","").split(",")

    def SplitVBAVariables(x) : 
        x = str(x)
        resultmeasure = 'scalar' if 'byval ' in x.lower() else 'vector'
        resulttype = 'long' if 'double' not in x.lower() else 'double'
        resultname = ''
        if resultmeasure == 'scalar' and resulttype == 'long' : 
            startidx = x.lower().index('byval') + 6
            endidx = x.lower().index('as long')
            resultname = x[startidx:endidx].replace(" ","")
        elif resultmeasure == 'scalar' and resulttype == 'double' :
            startidx = x.lower().index('byval') + 6
            endidx = x.lower().index('as double')
            resultname = x[startidx:endidx].replace(" ","")
        elif resultmeasure == 'vector' and resulttype == 'long' : 
            startidx = x.lower().index('byref') + 6
            endidx = x.lower().index('as long')
            resultname = x[startidx:endidx].replace(" ","")
        else : 
            startidx = x.lower().index('byref') + 6
            endidx = x.lower().index('as double')
            resultname = x[startidx:endidx].replace(" ","")

        if resultmeasure + "_" +  resulttype == 'scalar_long' : 
            return ct.c_long, resultname
        elif resultmeasure + "_" +  resulttype == 'scalar_double' :
            return ct.c_double, resultname
        elif resultmeasure + "_" +  resulttype == 'vector_long' :
            return c_long_p, resultname
        else : 
            return c_double_p, resultname

    exec("Targetdll = ct.WinDLL(ReleaseFolder + TargetDllString)")
    CalcFunc = eval('Targetdll.' + TargetFunctionString)
    CalcFunc.restype = ct.c_long
    VariablesFormat = [SplitVBAVariables(i) for i in StringArray]
    CalcFunc.argtypes = [v[0] for v in VariablesFormat]
    VariableNames = [v[1] for v in VariablesFormat]
    return CalcFunc, VariablesFormat, VariableNames

def HullWhite1FactorCalibration() : 
    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings()
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = today_YYYYMMDD)
    vb_FixedKappaFlag = make_listvariable_interface(left_frame, 'FixedKappa Flag', ["0 : kappa 추정","1 : kappa 고정"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=1, bold = True)
    v_FixedKappa = make_variable_interface(left_frame, 'FixedKappa', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 0.01)
    NMonths = (np.array([0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0]) * 12).astype(np.int64)
    DefaultTerm = [TimestampToYYYYMMDD(today + pd.DateOffset(months = i)) for i in NMonths ]
    defaultvalues = (DefaultTerm + ['']* 10, [3.5115,3.5124,3.7926,3.8730,3.9021,3.9204,3.9239,3.9116,3.8993,3.9023,3.9025,3.9081,3.9138,3.9223,3.9337]+ ['']* 10)
    targetcolumns = ["Term", "Rate"]

    nindexs = 7
    ncolumns = 2
    sht_DiscCurveLeg = AddVariableSheet(left_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "ZeroCurve", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 88, sheet_height = 30, MaxHeight=18)
    sht_DiscCurveLeg.set_all_column_widths(width=60)

    center_frame = tk.Frame(main_frame)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_VolFlag = make_listvariable_interface(center_frame, 'Vol Flag', ["0 : Black Vol","1 : Normal Vol"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=1, bold = True)
    vb_SwaptionFreq = make_listvariable_interface(center_frame, 'Payment Frequency', ["0 : 3","1 :6","2: 12"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)

    defaultvalues2 = ([0.25, 0.50, 0.75, 1.0, 2.0, 3.0, 5.0] + [""] * 10, [1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0] + [""] * 10, [0.9189,0.9372,0.9486,0.9636,0.8618,0.7529,0.6824] + [""] * 10)
    targetcolumns2 = ["OptMat", "SwapMat",'SwaptionVol%']
    sht_Swptn = AddVariableSheet(center_frame, nindexs = nindexs, ncolumns= 3,targetcolumns = targetcolumns2, defaultvalues = defaultvalues2, VariableName = "Swaption Vol %", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 115, sheet_height = 30, MaxHeight=40)
    sht_Swptn.set_all_column_widths(width=105)

    right_frame = tk.Frame(main_frame)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    targetcolumns3 = ["Term", "initvol(%)"]
    v_initkappa = make_variable_interface(right_frame, 'InitialKappa', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 0.01, titlelable= True, titleName= "HW Initial Param")
    initvalues = ([0.25, 0.50, 0.75, 1.0, 2.0, 3.0, 5.0] + [""] * 10, [1.0,1.0,1.0,1.0,1.0,1.0,1.0] + [""] * 10)
    sht_HW_InitialVol = AddVariableSheet(right_frame, nindexs = len(initvalues[0]), ncolumns= len(initvalues),targetcolumns = targetcolumns3, defaultvalues = initvalues, VariableName = "initial HWVol", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 120, sheet_height = 30, MaxHeight=18)
    sht_HW_InitialVol.set_all_column_widths(width=98)

    Result_frame = tk.Frame(main_frame)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    ResultValue = []
    ResultValue2 = pd.DataFrame([])
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultValue, ResultValue2,DefaultTerm, defaultvalues]
    exitgui = lambda : root.destroy()

    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        ResultValue = MyArrays[4]
        ResultValue2 = MyArrays[5]
        ZeroTermList = MyArrays[6]
        ZeroRateList = MyArrays[7]
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else today_YYYYMMDD
        FixedKappaFlag = int(str(vb_FixedKappaFlag.get(vb_FixedKappaFlag.curselection())).split(":")[0]) if vb_FixedKappaFlag.curselection() else 1
        FixedKappa = float(v_FixedKappa.get()) if len(str(v_FixedKappa.get())) > 0 else 0.01

        print(PriceDate)
        print(FixedKappaFlag)
        print(FixedKappa)

        DiscLeg = get_from_sheetinterface(sht_DiscCurveLeg)
        DiscLeg["Term"] = DiscLeg["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        DiscLeg["Rate"] = DiscLeg["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        ZeroTerm = list(DiscLeg["Term"].values)
        NZero = len(ZeroTerm)
        ZeroRate = list(DiscLeg["Rate"].values)
        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
        print(ZeroTerm)
        print(ZeroRate)

        lognormalvol0normalvol1 = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 1
        FreqMonthSwaption = float(str(vb_SwaptionFreq.get(vb_SwaptionFreq.curselection())).split(":")[1]) if vb_SwaptionFreq.curselection() else 3.0
        print(lognormalvol0normalvol1)
        print(FreqMonthSwaption)

        Swptn = get_from_sheetinterface(sht_Swptn)
        Swptn["OptMat"] = Swptn["OptMat"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        Swptn["SwaptionVol%"] = Swptn["SwaptionVol%"].apply(lambda x : str(x).replace("-","")).astype(np.float64)

        T_OptMaturity = Swptn["OptMat"].values.astype(np.float64)
        quotient = (T_OptMaturity // 0.25).astype(np.int64)
        myary = quotient * 0.25
        T_OptMaturity = np.r_[myary[myary < 0.25] * 0 + 0.25, myary[myary >= 0.25]]
        Term_SwapMat = Swptn["SwapMat"].values.astype(np.float64)
        SwaptionVol = Swptn["SwaptionVol%"].values.astype(np.float64) if Swptn["SwaptionVol%"].values.astype(np.float64).max() < 0.45 else Swptn["SwaptionVol%"].values.astype(np.float64)/100
        NSwaption = len(SwaptionVol)
        Preprocessing_Term(T_OptMaturity, PriceDate)
        Preprocessing_Term(Term_SwapMat, PriceDate)
        print(T_OptMaturity)
        print(Term_SwapMat)
        print(SwaptionVol)

        initial_kappa = np.array([float(v_initkappa.get()) if len(str(v_initkappa.get())) > 0 else 0.01], dtype = np.float64)
        HW_InitialVol = get_from_sheetinterface(sht_HW_InitialVol)
        HW_InitialVol["Term"] = HW_InitialVol["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        HW_InitialVol["initvol(%)"] = HW_InitialVol["initvol(%)"].apply(lambda x : str(x).replace("-","")).astype(np.float64)

        HWTerm_initial = HW_InitialVol['Term'].values.astype(np.float64)
        Preprocessing_Term(HWTerm_initial, PriceDate)
        HWVol_initial = HW_InitialVol['initvol(%)'].values.astype(np.float64) if HW_InitialVol['initvol(%)'].values.astype(np.float64).max() < 0.45 else HW_InitialVol['initvol(%)'].values.astype(np.float64)/100
        NHW_initial = len(HWTerm_initial)
        print(HWTerm_initial)
        print(HWVol_initial)
        ResultBlackPrice = np.zeros(len(SwaptionVol), dtype = np.float64)
        ResultHWPrice = np.zeros(len(SwaptionVol), dtype = np.float64)
        ResultError = np.zeros(len(SwaptionVol), dtype = np.float64)

        NZero_c = ct.c_long(NZero)
        ZeroTerm_np, ZeroTerm_c = arr_double(ZeroTerm)
        ZeroRate_np, ZeroRate_c = arr_double(ZeroRate)
        NSwaption_c = ct.c_long(NSwaption)
        T_OptMaturity_np, T_OptMaturity_c = arr_double(T_OptMaturity)

        Term_SwapMat_np, Term_SwapMat_c = arr_double(Term_SwapMat)
        SwaptionVol_np, SwaptionVol_c = arr_double(SwaptionVol)
        FreqMonthSwaption_c = ct.c_double(FreqMonthSwaption)
        NHW_initial_c = ct.c_long(NHW_initial)
        HWTerm_initial_np, HWTerm_initial_c = arr_double(HWTerm_initial)

        HWVol_initial_np, HWVol_initial_c = arr_double(HWVol_initial)
        initial_kappa_np, initial_kappa_c = arr_double(initial_kappa)
        FixedKappaFlag_c = ct.c_long(FixedKappaFlag)
        FixedKappa_c = ct.c_double(FixedKappa)
        lognormalvol0normalvol1_c = ct.c_long(lognormalvol0normalvol1)

        ResultBlackPrice_np, ResultBlackPrice_c = arr_double(ResultBlackPrice)
        ResultHWPrice_np, ResultHWPrice_c = arr_double(ResultHWPrice)
        ResultError_np, ResultError_c = arr_double(ResultError)
        print("변수print")
        print(NZero, ZeroTerm_np, ZeroRate_np)
        print(NSwaption, T_OptMaturity_np, Term_SwapMat_np, SwaptionVol_np)    
        print(FreqMonthSwaption, NHW_initial, HWTerm_initial, HWVol_initial)    
        print(initial_kappa_np, FixedKappaFlag, FixedKappa, lognormalvol0normalvol1)    
        
        ret = HWCapHWSwaptionCalib1F(NZero_c, ZeroTerm_c, ZeroRate_c, NSwaption_c,T_OptMaturity_c,
                                    Term_SwapMat_c, SwaptionVol_c, FreqMonthSwaption_c, NHW_initial_c, HWTerm_initial_c,
                                    HWVol_initial_c, initial_kappa_c, FixedKappaFlag_c, FixedKappa_c, lognormalvol0normalvol1_c,
                                    ResultBlackPrice_c, ResultHWPrice_c, ResultError_c)    
        ResultBlack = np.ctypeslib.as_array(ResultBlackPrice_c[:NSwaption], shape = (NSwaption, ))
        ResultHW = np.ctypeslib.as_array(ResultHWPrice_c[:NSwaption], shape = (NSwaption, ))
        ResultError = np.ctypeslib.as_array(ResultError_c[:NSwaption], shape = (NSwaption, ))
        ResultHWVol = np.ctypeslib.as_array(HWVol_initial_c[:NSwaption], shape = (NSwaption, ))
        ResultFrame = Swptn
        ResultFrame["BlackPrice"] = ResultBlack
        ResultFrame["HWPrice"] = ResultHW
        ResultFrame["Error"] = ResultError
        ResultFrame["HWVol"] = ResultHWVol
        ResultFrame["HWKappa"] = initial_kappa_c[0]
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(main_frame)
            tk.Button(Result_frame, text = 'Cali완료\nPricing실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = exitgui, width = 15).pack()

        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(main_frame)

        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    

        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultFrame.reset_index(), width = 100)
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2      
        #MyArrays[4] = [NZero, ZeroTerm_np, ZeroRate_np, NSwaption, T_OptMaturity, Term_SwapMat, SwaptionVol,FreqMonthSwaption, lognormalvol0normalvol1]
        MyArrays[4] = [NZero_c, ZeroTerm_c, ZeroRate_c, NSwaption_c,T_OptMaturity_c,
                                    Term_SwapMat_c, SwaptionVol_c, FreqMonthSwaption_c, NHW_initial_c, HWTerm_initial_c,
                                    HWVol_initial_c, initial_kappa_c, FixedKappaFlag_c, FixedKappa_c, lognormalvol0normalvol1_c,
                                    ResultBlackPrice_c, ResultHWPrice_c, ResultError_c]
        MyArrays[5] = ResultFrame
        MyArrays[6] = ZeroTerm
        MyArrays[7] = ZeroRate
        messagebox.showinfo("알림","Cali 완료!!\n Pricing실행 버튼 클릭")   

    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)    
    root.mainloop()   
    return MyArrays[5], MyArrays[6], MyArrays[7]

def IRStucturedSwapOneCurve() : 
    ResultData, ZeroTerm, ZeroRate = HullWhite1FactorCalibration()

def IRSPricing() : 
    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings()

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    TempSchedule =[TimestampToYYYYMMDD(i) for i in MakeSchedule(today_YYYYMMDD, today_YYYYMMDD + 100000, 3)]
    StartSchedule = TempSchedule[:-1]
    EndSchedule = TempSchedule[1:]
    Multiple = [1] * len(StartSchedule)
    Multiple2 = [0] * len(StartSchedule)
    FixedCpnRate = [3.5] * len(StartSchedule)
    FixedCpnRate2 = [0] * len(StartSchedule)
    FixedRate = [0.0] * len(StartSchedule)
    defaultvalues = ([0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0] + ['']* 10, [3.5, 3.5, 3.5, 3.5, 3.6, 3.65, 3.66, 3.71, 3.81, 3.87, 3.87, 3.88, 3.91, 3.92, 3.95]+ ['']* 10)
    targetcolumns = ["Term", "Rate"]
    nindexs = 7
    ncolumns = 2

    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = today_YYYYMMDD)
    vb_NominalFlag = make_listvariable_interface(left_frame, 'Nominal Flag', ["0 : Nominal 교환 안함","1 : Nominal 교환"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)
    v_NominalLeg1 = make_variable_interface(left_frame, 'Nominal(Leg1)', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 10000)
    v_NominalLeg2 = make_variable_interface(left_frame, 'Nominal(Leg2)', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 10000)
    v_NominalPaymentDate = make_variable_interface(left_frame, 'Nominal 교환일', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = EDate(today_YYYYMMDD, 120))
    vb_FixFloLeg1 = make_listvariable_interface(left_frame, 'Fixed/Floating(Leg1)', ["0 : 고정금리","1 : 변동금리"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)
    vb_FixFloLeg2 = make_listvariable_interface(left_frame, 'Fixed/Floating(Leg2)', ["0 : 고정금리","1 : 변동금리"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=1, bold = True)
    vb_DayCountLeg1 = make_listvariable_interface(left_frame, 'DayCount(Leg1)', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)
    vb_DayCountLeg2 = make_listvariable_interface(left_frame, 'DayCount(Leg2)', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)
    vb_GreekFlag = make_listvariable_interface(left_frame, 'Greek Flag', ["0 : Greek 산출안함","1 : Greek 산출함"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)
    vb_TextFlag = make_listvariable_interface(left_frame, 'Text Flag', ["0 : Logging 안함","1 : Logging함"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)

    center_frame = tk.Frame(main_frame)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_DiscCurveLeg1 = AddVariableSheet(center_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "DiscZeroCurve(Leg1)", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 70, sheet_height = 30, titlelable= True, titleName = "Leg1 MarketData", MaxHeight=10)
    sht_DiscCurveLeg1.set_all_column_widths(width=50)
    sht_RefCurveLeg1 = AddVariableSheet(center_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "EstZeroCurve(Leg1)", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 70, sheet_height = 30, MaxHeight=10)
    sht_RefCurveLeg1.set_all_column_widths(width=50)

    #mysheet2 = AddVariableSheet(center_frame, ["index","Holidays"], nindexs, 1, defaultvalues = (), VariableName = "TempVariables2", myfont = 12, anchor = 'w', padx = 5, pady = 2)
    Right_frame1 = tk.Frame(main_frame)
    Right_frame1.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_RefRateTypeLeg1 = make_listvariable_interface(Right_frame1, 'Reference Type', ["0 : 추정 Start, End 직접 입력","1 : Swap 금리 등"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, width = 23, titlelable= True, titleName = "Leg1 Information", bold = True)
    vb_RefNCPN_AnnualLeg1 = make_listvariable_interface(Right_frame1, 'Reference Type이\nSwap 금리인경우\n기초금리의\n 연 이자지급수(회)', ["0: 4","1: 2","2: 1","3: 6","4: 12"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, bold = False)
    vb_RefMaturityLeg1 = make_listvariable_interface(Right_frame1, 'Reference Type이\nSwap 금리인경우\n기초금리 만기(년)', np.vectorize(lambda x, y : str(x) + " : " + str(y))(np.arange(0,200), np.arange(1, 201) * 0.25), listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, bold = False)
    sht_ConvexityAdjLeg1 = AddVariableSheet(Right_frame1, nindexs = 30, ncolumns= 2,targetcolumns = ["Term","Vol(%)"], defaultvalues = ([1.0,2.0,3.0,4.0,5.0,7.0,10.0]+ ['']* 5,[0.87,0.88,0.88,0.88,0.88,0.88,0.88]+ ['']* 5), VariableName = "Convexity\nAdjustment", myfont = 10, anchor = 'w', padx = 5, pady = 2, sheet_width = 70, sheet_height = 40, MaxHeight=10)
    sht_ConvexityAdjLeg1.set_all_column_widths(width=50)

    Right_frame2 = tk.Frame(main_frame)
    Right_frame2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_Leg1ScheduleInfo = AddVariableSheet(Right_frame2, nindexs = 10, ncolumns= 8,targetcolumns = ["Forward Start","Forward End","기산일","기말일","지급일","변동금리기울기","고정쿠폰(%)","확정된금리"], defaultvalues = (StartSchedule + ['']* 50, EndSchedule+ ['']* 50, StartSchedule+ ['']* 50, EndSchedule+ ['']* 50, EndSchedule+ ['']* 50, Multiple2+ ['']* 50, FixedCpnRate+ ['']* 50, FixedRate+ ['']* 50), VariableName = "Leg1 스케줄", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 85, sheet_height = 40, MaxHeight=20, headerfont= 9)
    sht_Leg1ScheduleInfo.set_all_column_widths(width=87)
    Right_frame3 = tk.Frame(main_frame)
    Right_frame3.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_Leg1Holiday = AddVariableSheet(Right_frame3, nindexs = 1000, ncolumns= 1,targetcolumns = ["Holidays"], defaultvalues = (), VariableName = "Leg1 Holidays", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 150, sheet_height = 300, MaxHeight=20)

    center_frame_Leg2 = tk.Frame(main_frame)
    center_frame_Leg2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_DiscCurveLeg2 = AddVariableSheet(center_frame_Leg2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "DiscZeroCurve(Leg2)", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 70, sheet_height = 30, titlelable= True, titleName = "Leg1 MarketData", MaxHeight=10)
    sht_DiscCurveLeg2.set_all_column_widths(width=50)
    sht_RefCurveLeg2 = AddVariableSheet(center_frame_Leg2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "EstZeroCurve(Leg2)", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 70, sheet_height = 30, MaxHeight=10)
    sht_RefCurveLeg2.set_all_column_widths(width=50)

    Right_frame1Leg2 = tk.Frame(main_frame)
    Right_frame1Leg2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_RefRateTypeLeg2 = make_listvariable_interface(Right_frame1Leg2, 'Reference Type', ["0 : 추정 Start, End 직접 입력","1 : Swap 금리 등"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, width = 23, titlelable= True, titleName = "Leg2 Information", bold = True)
    vb_RefNCPN_AnnualLeg2 = make_listvariable_interface(Right_frame1Leg2, 'Reference Type이\nSwap 금리인경우\n기초금리의\n 연 이자지급수(회)', ["0: 4","1: 2","2: 1","3: 6","4: 12"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, bold = False)
    vb_RefMaturityLeg2 = make_listvariable_interface(Right_frame1Leg2, 'Reference Type이\nSwap 금리인경우\n기초금리 만기(년)', np.vectorize(lambda x, y : str(x) + " : " + str(y))(np.arange(0,200), np.arange(1, 201) * 0.25), listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, bold = False)
    sht_ConvexityAdjLeg2 = AddVariableSheet(Right_frame1Leg2, nindexs = 30, ncolumns= 2,targetcolumns = ["Term","Vol(%)"], defaultvalues = ([1.0,2.0,3.0,4.0,5.0,7.0,10.0]+ ['']* 5,[0.87,0.88,0.88,0.88,0.88,0.88,0.88]+ ['']* 5), VariableName = "Convexity\nAdjustment", myfont = 10, anchor = 'w', padx = 5, pady = 2, sheet_width = 70, sheet_height = 40, MaxHeight=10)
    sht_ConvexityAdjLeg2.set_all_column_widths(width=50)

    Right_frame2Leg2 = tk.Frame(main_frame)
    Right_frame2Leg2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_Leg2ScheduleInfo = AddVariableSheet(Right_frame2Leg2, nindexs = 10, ncolumns= 8,targetcolumns = ["Forward Start","Forward End","기산일","기말일","지급일","변동금리기울기","고정쿠폰(%)","확정된금리"], defaultvalues = (StartSchedule + ['']* 50, EndSchedule + ['']* 50, StartSchedule + ['']* 50, EndSchedule + ['']* 50, EndSchedule + ['']* 50, Multiple + ['']* 50, FixedCpnRate2 + ['']* 50, FixedRate + ['']* 50), VariableName = "Leg2 스케줄", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 85, sheet_height = 40, MaxHeight=20, headerfont= 9)
    sht_Leg2ScheduleInfo.set_all_column_widths(width=87)
    Right_frame3Leg2 = tk.Frame(main_frame)
    Right_frame3Leg2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_Leg2Holiday = AddVariableSheet(Right_frame3Leg2, nindexs = 1000, ncolumns= 1,targetcolumns = ["Holidays"], defaultvalues = (), VariableName = "Leg2 Holidays", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 150, sheet_height = 300, MaxHeight=20)

    AddFrame = tk.Frame(main_frame)
    AddFrame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_FXCurve = AddVariableSheet(AddFrame, nindexs = 30, ncolumns= 3,targetcolumns = ["Term","FXRateLeg1","FXRateLeg2"], defaultvalues = ([1.0,2.0,3.0,4.0,5.0,7.0,10.0]+ ['']* 10,[1.0,1.0,1.0,1.0,1.0,1.0,1.0]+ ['']* 10,[1.0,1.0,1.0,1.0,1.0,1.0,1.0]+ ['']* 10), VariableName = "FX Rate Curve", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 85, sheet_height = 40, MaxHeight=20)
    sht_FXCurve.set_all_column_widths(width=87)

    Result_frame = tk.Frame(main_frame)
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

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else today_YYYYMMDD
        NominalFlag = int(str(vb_NominalFlag.get(vb_NominalFlag.curselection())).split(":")[0]) if vb_NominalFlag.curselection() else 0
        NominalLeg1 = float(v_NominalLeg1.get()) if len(str(v_NominalLeg1.get())) > 0 else 10000
        NominalLeg2 = float(v_NominalLeg2.get()) if len(str(v_NominalLeg2.get())) > 0 else 10000
        NominalPaymentDate = int(v_NominalPaymentDate.get()) if len(str(v_NominalPaymentDate.get())) > 0 else EDate(today_YYYYMMDD, 120)
        FixFloLeg1 = int(str(vb_FixFloLeg1.get(vb_FixFloLeg1.curselection())).split(":")[0]) if vb_FixFloLeg1.curselection() else 0
        FixFloLeg2 = int(str(vb_FixFloLeg2.get(vb_FixFloLeg2.curselection())).split(":")[0]) if vb_FixFloLeg2.curselection() else 0

        DayCountLeg1 = int(str(vb_DayCountLeg1.get(vb_DayCountLeg1.curselection())).split(":")[0]) if vb_DayCountLeg1.curselection() else 0
        DayCountLeg2 = int(str(vb_DayCountLeg2.get(vb_DayCountLeg2.curselection())).split(":")[0]) if vb_DayCountLeg2.curselection() else 0
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 1
        LoggingFlag = int(str(vb_TextFlag.get(vb_TextFlag.curselection())).split(":")[0]) if vb_TextFlag.curselection() else 0
        #print(PriceDate)
        #print(NominalFlag)
        #print(NominalLeg1)
        #print(NominalLeg2)
        #print(NominalPaymentDate)
        #print(FixFloLeg1)
        #print(FixFloLeg2)
        #print(DayCountLeg1)
        #print(DayCountLeg2)
        #print(GreekFlag)
        
        DiscLeg1 = get_from_sheetinterface(sht_DiscCurveLeg1)
        DiscTermLeg1 = DiscLeg1["Term"].values
        Disc_NTerm_Leg1 = len(DiscTermLeg1)
        DiscRateLeg1 = DiscLeg1["Rate"].values if DiscLeg1["Rate"].values.max() < 1.0 else DiscLeg1["Rate"].values/100
        RefLeg1 = get_from_sheetinterface(sht_RefCurveLeg1)
        RefTermLeg1 = RefLeg1["Term"].values
        Ref_NTerm_Leg1 = len(RefTermLeg1)
        RefRateLeg1 = RefLeg1["Rate"].values if RefLeg1["Rate"].values.max() < 1.0 else RefLeg1["Rate"].values/100
        #print(Ref_NTerm_Leg1)
        #print(DiscTermLeg1)
        #print(DiscRateLeg1)
        #print(RefTermLeg1)
        #print(RefRateLeg1)

        RefRateTypeLeg1 = int(str(vb_RefRateTypeLeg1.get(vb_RefRateTypeLeg1.curselection())).split(":")[0]) if vb_RefRateTypeLeg1.curselection() else 0
        RefNCPN_AnnualLeg1 = int(str(vb_RefNCPN_AnnualLeg1.get(vb_RefNCPN_AnnualLeg1.curselection())).split(":")[1]) if vb_RefNCPN_AnnualLeg1.curselection() else 4
        RefMaturityLeg1 = float(str(vb_RefMaturityLeg1.get(vb_RefMaturityLeg1.curselection())).split(":")[1]) if vb_RefMaturityLeg1.curselection() else 0.25
        #print(RefRateTypeLeg1)
        #print(RefNCPN_AnnualLeg1)
        #print(RefMaturityLeg1)

        ConvexAdjLeg1 = get_from_sheetinterface(sht_ConvexityAdjLeg1)
        ConvexTermLeg1 = ConvexAdjLeg1['Term'].values
        ConvexVolLeg1 = ConvexAdjLeg1['Vol(%)'].values if ConvexAdjLeg1['Vol(%)'].values.max() < 0.4 else ConvexAdjLeg1['Vol(%)'].values/100
        NConvexLeg1 = len(ConvexTermLeg1)
        #print(ConvexTermLeg1)
        #print(ConvexVolLeg1)

        ScheduleDF_Leg1 = get_from_sheetinterface(sht_Leg1ScheduleInfo)
        ScheduleData = ScheduleDF_Leg1[["Forward Start","Forward End","기산일","기말일","지급일"]]
        NCF_Leg1 = len(ScheduleData)
        Schedule_Leg1 = ScheduleData.T.values.astype(np.int64).reshape(-1)
        Slope_Leg1 = ScheduleDF_Leg1["변동금리기울기"].astype(np.float64).values
        CPN_Leg1 = ScheduleDF_Leg1["고정쿠폰(%)"].astype(np.float64).values if ScheduleDF_Leg1["고정쿠폰(%)"].astype(np.float64).values.max() < 1.0 else ScheduleDF_Leg1["고정쿠폰(%)"].astype(np.float64).values/100
        FixedRefRate_Leg1 = ScheduleDF_Leg1["확정된금리"].astype(np.float64).values if ScheduleDF_Leg1["확정된금리"].astype(np.float64).values.max() < 1.0 else ScheduleDF_Leg1["확정된금리"].astype(np.float64).values/100

        #print(Schedule_Leg1) 
        #print(Slope_Leg1)
        #print(CPN_Leg1)
        #print(FixedRefRate_Leg1)

        DiscLeg2 = get_from_sheetinterface(sht_DiscCurveLeg2)
        DiscTermLeg2 = DiscLeg2["Term"].values
        Disc_NTerm_Leg2 = len(DiscTermLeg2)
        DiscRateLeg2 = DiscLeg2["Rate"].values if DiscLeg2["Rate"].values.max() < 1.0 else DiscLeg2["Rate"].values/100
        RefLeg2 = get_from_sheetinterface(sht_RefCurveLeg2)
        RefTermLeg2 = RefLeg2["Term"].values
        Ref_NTerm_Leg2 = len(RefTermLeg2)
        RefRateLeg2 = RefLeg2["Rate"].values if RefLeg2["Rate"].values.max() < 1.0 else RefLeg2["Rate"].values/100

        #print(DiscTermLeg2)
        #print(DiscRateLeg2)
        #print(RefTermLeg2)
        #print(RefRateLeg2)

        RefRateTypeLeg2 = int(str(vb_RefRateTypeLeg2.get(vb_RefRateTypeLeg2.curselection())).split(":")[0]) if vb_RefRateTypeLeg2.curselection() else 0
        RefNCPN_AnnualLeg2 = int(str(vb_RefNCPN_AnnualLeg2.get(vb_RefNCPN_AnnualLeg2.curselection())).split(":")[1]) if vb_RefNCPN_AnnualLeg2.curselection() else 4
        RefMaturityLeg2 = float(str(vb_RefMaturityLeg2.get(vb_RefMaturityLeg2.curselection())).split(":")[1]) if vb_RefMaturityLeg2.curselection() else 0.25
        #print(RefRateTypeLeg2)
        #print(RefNCPN_AnnualLeg2)
        #print(RefMaturityLeg2)

        ConvexAdjLeg2 = get_from_sheetinterface(sht_ConvexityAdjLeg2)
        ConvexTermLeg2 = ConvexAdjLeg2['Term'].values
        ConvexVolLeg2 = ConvexAdjLeg2['Vol(%)'].values if ConvexAdjLeg2['Vol(%)'].values.max() < 0.4 else ConvexAdjLeg2['Vol(%)'].values/100
        NConvexLeg2 = len(ConvexTermLeg2)
        #print(ConvexTermLeg2)
        #print(ConvexVolLeg2)

        ScheduleDF_Leg2 = get_from_sheetinterface(sht_Leg2ScheduleInfo)
        ScheduleData = ScheduleDF_Leg2[["Forward Start","Forward End","기산일","기말일","지급일"]]
        NCF_Leg2 = len(ScheduleData)
        Schedule_Leg2 = ScheduleData.T.values.astype(np.int64).reshape(-1)
        Slope_Leg2 = ScheduleDF_Leg2["변동금리기울기"].astype(np.float64).values
        CPN_Leg2 = ScheduleDF_Leg2["고정쿠폰(%)"].astype(np.float64).values if ScheduleDF_Leg2["고정쿠폰(%)"].astype(np.float64).values.max() < 1.0 else ScheduleDF_Leg2["고정쿠폰(%)"].astype(np.float64).values/100
        FixedRefRate_Leg2 = ScheduleDF_Leg2["확정된금리"].astype(np.float64).values if ScheduleDF_Leg2["확정된금리"].astype(np.float64).values.max() < 1.0 else ScheduleDF_Leg2["확정된금리"].astype(np.float64).values/100

        #print(Schedule_Leg2) 
        #print(Slope_Leg2)
        #print(CPN_Leg2)
        #print(FixedRefRate_Leg2)

        ResultPrice = np.array([0] * 10, dtype = np.float64)
        ResultRefRate = np.array([0] * (NCF_Leg1 + NCF_Leg2 + 2), dtype = np.float64)
        ResultCPN = ResultRefRate.copy()
        ResultDF = ResultRefRate.copy()
        PV01 = ResultRefRate.copy()
        
        KeyRateLeg1PV01 = np.array([0] * (2 * (Disc_NTerm_Leg1 + Ref_NTerm_Leg1) + Disc_NTerm_Leg1 + 2), dtype = np.float64)
        KeyRateLeg2PV01 = np.array([0] * (2 * (Disc_NTerm_Leg2 + Ref_NTerm_Leg2) + Disc_NTerm_Leg2 + 2), dtype = np.float64)
        SOFRConv = np.array([0] * 6, dtype = np.int64)
        HolidayCalcFlag = np.array([0] * 2, dtype = np.int64)
        NHolidays = np.array([0] * 2, dtype = np.int64)

        Leg1Holiday = get_from_sheetinterface(sht_Leg1Holiday)
        n1 = len(Leg1Holiday["Holidays"].values)
        Leg2Holiday = get_from_sheetinterface(sht_Leg2Holiday)
        n2 = len(Leg2Holiday["Holidays"].values)
        NHolidays[0] = n1
        NHolidays[1] = n2
        Holidays = np.array(list(Leg1Holiday["Holidays"].values.astype(np.int64)) + list(Leg2Holiday["Holidays"].values.astype(np.int64)), dtype = np.int64)
        NHistory = np.array([0] * 2, dtype = np.int64)
        HistoryDate = np.array([19920627, 19920627], dtype = np.int64)
        HistoryRate = np.array([0.03, 0.03], dtype = np.float64)
        RefBondInfo = np.array([0.042, 20200627.0, 20300627.0, 0.0], dtype = np.float64)
        ConvexityFlagLeg1 = 0
        if int(RefNCPN_AnnualLeg1 * RefMaturityLeg1 + 0.001) > 1 and RefRateTypeLeg1 > 0: 
            ConvexityFlagLeg1 = 1

        ConvexityFlagLeg2 = 0
        if int(RefNCPN_AnnualLeg2 * RefMaturityLeg2 + 0.001) > 1 and RefRateTypeLeg2 > 0: 
            ConvexityFlagLeg2 = 1

        RcvPayConvexityAdjFlag = np.array([ConvexityFlagLeg1, ConvexityFlagLeg2]+ [0, 0], np.int64)
        NRcvPayConvexAdjVol = np.array([NConvexLeg1, NConvexLeg2]+ [0, 0], dtype = np.int64)
        RcvTermAndVol = np.array(list(ConvexTermLeg1) + list(ConvexVolLeg1) + [0, 0], dtype = np.float64)
        PayTermAndVol = np.array(list(ConvexTermLeg2) + list(ConvexVolLeg2) + [0, 0], dtype = np.float64)
        
        FXCurveInfo = get_from_sheetinterface(sht_FXCurve)
        CRS_Info = FXCurveInfo.astype(np.float64).T.values.reshape(-1)
        CRS_Flag = np.array([0] * 2, dtype = np.int64)
        if (FXCurveInfo["FXRateLeg1"].mean() == 1 and FXCurveInfo["FXRateLeg2"].mean() == 1) : 
            CRS_Flag[0] = 0
            CRS_Flag[1] = 0
        else : 
            CRS_Flag[1] = 1
            CRS_Flag[1] = len(FXCurveInfo)

        PriceDate = ct.c_long(PriceDate)
        GreekFlag = ct.c_long(GreekFlag)
        NominalFlag = ct.c_long(NominalFlag + 2* LoggingFlag)
        CRS_Flag_np, CRS_Flag = arr_long(CRS_Flag)

        CRS_Info_np, CRS_Info = arr_double(CRS_Info)
        RefRateTypeLeg1 = ct.c_long(RefRateTypeLeg1)
        RefNCPN_AnnualLeg1 = ct.c_long(RefNCPN_AnnualLeg1)

        RefMaturityLeg1 = ct.c_double(RefMaturityLeg1)
        FixFloLeg1 = ct.c_long(FixFloLeg1)
        DayCountLeg1 = ct.c_long(DayCountLeg1)

        NominalLeg1 = ct.c_double(NominalLeg1)
        NominalPaymentDate = ct.c_long(NominalPaymentDate)
        Disc_NTerm_Leg1 = ct.c_long(Disc_NTerm_Leg1)
        DiscTermLeg1_np, DiscTermLeg1 = arr_double(DiscTermLeg1)
        DiscRateLeg1_np, DiscRateLeg1 = arr_double(DiscRateLeg1)

        Ref_NTerm_Leg1 = ct.c_long(Ref_NTerm_Leg1)
        RefTermLeg1_np, RefTermLeg1 = arr_double(RefTermLeg1)
        RefRateLeg1_np, RefRateLeg1 = arr_double(RefRateLeg1)
        NCF_Leg1 = ct.c_long(NCF_Leg1)
        Schedule_Leg1_np, Schedule_Leg1 = arr_long(Schedule_Leg1)

        Slope_Leg1_np, Slope_Leg1 = arr_double(Slope_Leg1)
        CPN_Leg1_np, CPN_Leg1 = arr_double(CPN_Leg1)
        FixedRefRate_Leg1_np, FixedRefRate_Leg1 = arr_double(FixedRefRate_Leg1)
        RefRateTypeLeg2 = ct.c_long(RefRateTypeLeg2)
        RefNCPN_AnnualLeg2 = ct.c_long(RefNCPN_AnnualLeg2)

        RefMaturityLeg2 = ct.c_double(RefMaturityLeg2)
        FixFloLeg2 = ct.c_long(FixFloLeg2)
        DayCountLeg2 = ct.c_long(DayCountLeg2)
        NominalLeg2 = ct.c_double(NominalLeg2)
        #NominalPaymentDate = ct.c_long(NominalPaymentDate)

        Disc_NTerm_Leg2 = ct.c_long(Disc_NTerm_Leg2)
        DiscTermLeg2_np, DiscTermLeg2 = arr_double(DiscTermLeg2)
        DiscRateLeg2_np, DiscRateLeg2 = arr_double(DiscRateLeg2)
        Ref_NTerm_Leg2 = ct.c_long(Ref_NTerm_Leg2)
        RefTermLeg2_np, RefTermLeg2 = arr_double(RefTermLeg2)

        RefRateLeg2_np, RefRateLeg2 = arr_double(RefRateLeg2)
        NCF_Leg2 = ct.c_long(NCF_Leg2)
        Schedule_Leg2_np, Schedule_Leg2 = arr_long(Schedule_Leg2)
        Slope_Leg2_np, Slope_Leg2 = arr_double(Slope_Leg2)
        CPN_Leg2_np, CPN_Leg2 = arr_double(CPN_Leg2)

        FixedRefRate_Leg2_np, FixedRefRate_Leg2 = arr_double(FixedRefRate_Leg2)
        ResultPrice_np, ResultPrice = arr_double(ResultPrice)
        ResultRefRate_np, ResultRefRate = arr_double(ResultRefRate)
        ResultCPN_np, ResultCPN = arr_double(ResultCPN)
        ResultDF_np, ResultDF = arr_double(ResultDF)

        PV01_np, PV01 = arr_double(PV01)
        KeyRateLeg1PV01_np, KeyRateLeg1PV01 = arr_double(KeyRateLeg1PV01)
        KeyRateLeg2PV01_np, KeyRateLeg2PV01 = arr_double(KeyRateLeg2PV01)
        SOFRConv_np, SOFRConv = arr_long(SOFRConv)
        HolidayCalcFlag_np, HolidayCalcFlag = arr_long(HolidayCalcFlag)

        NHolidays_np, NHolidays = arr_long(NHolidays)
        Holidays_np, Holidays = arr_long(Holidays)
        NHistory_np, NHistory = arr_long(NHistory)
        HistoryDate_np, HistoryDate = arr_long(HistoryDate)
        HistoryRate_np, HistoryRate = arr_double(HistoryRate)

        RefBondInfo_np, RefBondInfo = arr_double(RefBondInfo)
        RcvPayConvexityAdjFlag_np, RcvPayConvexityAdjFlag = arr_long(RcvPayConvexityAdjFlag)
        NRcvPayConvexAdjVol_np, NRcvPayConvexAdjVol = arr_long(NRcvPayConvexAdjVol)
        RcvTermAndVol_np, RcvTermAndVol = arr_double(RcvTermAndVol)
        PayTermAndVol_np, PayTermAndVol = arr_double(PayTermAndVol)

        ret = CalcIRS(PriceDate, GreekFlag, NominalFlag, CRS_Flag, CRS_Info, 
        RefRateTypeLeg1, RefNCPN_AnnualLeg1, RefMaturityLeg1, FixFloLeg1, DayCountLeg1,
        NominalLeg1, NominalPaymentDate, Disc_NTerm_Leg1, DiscTermLeg1, DiscRateLeg1, 
        Ref_NTerm_Leg1, RefTermLeg1, RefRateLeg1, NCF_Leg1, Schedule_Leg1,
        Slope_Leg1, CPN_Leg1, FixedRefRate_Leg1, RefRateTypeLeg2, RefNCPN_AnnualLeg2, 
        RefMaturityLeg2, FixFloLeg2, DayCountLeg2,NominalLeg2, NominalPaymentDate, 
        Disc_NTerm_Leg2, DiscTermLeg2, DiscRateLeg2, Ref_NTerm_Leg2, RefTermLeg2, 
        RefRateLeg2, NCF_Leg2, Schedule_Leg2, Slope_Leg2, CPN_Leg2, 
        FixedRefRate_Leg2, ResultPrice, ResultRefRate, ResultCPN, ResultDF,
        PV01, KeyRateLeg1PV01, KeyRateLeg2PV01, SOFRConv, HolidayCalcFlag,
        NHolidays, Holidays, NHistory, HistoryDate, HistoryRate, 
        RefBondInfo, RcvPayConvexityAdjFlag, NRcvPayConvexAdjVol, RcvTermAndVol, PayTermAndVol)

        #r = Linterp(df["Term"].values.astype(np.float64), df["Rate"].values.astype(np.float64), 1.5)
        output_label.config(text = f"산출결과: \n{ret}\nSwapRate: \n{str(np.round(ResultPrice[0]*100,6))+"%"}\nValue : {ResultPrice[1] - ResultPrice[2]}\nLeg1 : \n{ResultPrice[1]}\nLeg2 : \n{ResultPrice[2]}\n", font = ("맑은 고딕", 12, 'bold'))
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(main_frame)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(main_frame)

        n1 = int(NCF_Leg1.value)
        n2 = int(NCF_Leg2.value)
        Result1_Leg1 = ScheduleDF_Leg1[["지급일"]].rename(columns = {"지급일" : "Leg1_Payment_Date"})
        Result1_Leg1["Leg1_RefRate"] = np.ctypeslib.as_array(ResultRefRate[:n1], shape = (n1, ))
        Result1_Leg1["Leg1_CashFlow"] = np.ctypeslib.as_array(ResultCPN[:n1], shape = (n1, ))
        Result1_Leg1["Leg1_DF"] = np.ctypeslib.as_array(ResultDF[:n1], shape = (n1, ))
        Result1_Leg2 = ScheduleDF_Leg2[["지급일"]].rename(columns = {"지급일" : "Leg2_Payment_Date"})
        Result1_Leg2["Leg2_RefRate"] = np.ctypeslib.as_array(ResultRefRate[n1:n1 + n2], shape = (n2, ))
        Result1_Leg2["Leg2_CashFlow"] = np.ctypeslib.as_array(ResultCPN[n1:n1 + n2], shape = (n2, ))
        Result1_Leg2["Leg2_DF"] = np.ctypeslib.as_array(ResultDF[n1:n1 + n2], shape = (n2, ))
        Result1 = pd.concat([Result1_Leg1, Result1_Leg2],axis = 1).applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        ngreek_leg1_Disc = int(Disc_NTerm_Leg1.value)
        ngreek_leg1_Ref = int(Ref_NTerm_Leg1.value)
        Leg1_SameCurveFlag = 0
        if ngreek_leg1_Disc == ngreek_leg1_Ref : 
            if (DiscTermLeg1_np == RefTermLeg1_np).sum() == ngreek_leg1_Disc and (DiscRateLeg1_np == RefRateLeg1_np).sum() == ngreek_leg1_Disc : 
                Leg1_SameCurveFlag = 1

        if Leg1_SameCurveFlag == 0 : 
            #Result2_Leg1 = pd.DataFrame([])
            PV01_Disc_Leg1 = pd.DataFrame(DiscTermLeg1_np, columns = ["Leg1 Disc Curve Term"])
            PV01_Disc_Leg1["Leg1 Disc PV01"] = np.ctypeslib.as_array(KeyRateLeg1PV01[:ngreek_leg1_Disc], shape = (ngreek_leg1_Disc, ))
            PV01_Ref_Leg1 = pd.DataFrame(RefTermLeg1_np, columns = ["Leg1 Ref Curve Term"])
            PV01_Ref_Leg1["Leg1 Ref PV01"] = np.ctypeslib.as_array(KeyRateLeg1PV01[ngreek_leg1_Disc :ngreek_leg1_Disc + ngreek_leg1_Ref], shape = (ngreek_leg1_Ref, ))
            Result2_Leg1 = pd.concat([PV01_Disc_Leg1, PV01_Ref_Leg1], axis = 1)
            Result2_Leg1["Leg1 Disc&Ref Curve Term"] = 0
            Result2_Leg1["Leg1 Disc&Ref PV01"] = 0
        else : 
            PV01_Disc_Leg1 = pd.DataFrame(DiscTermLeg1_np, columns = ["Leg1 Disc Curve Term"])
            PV01_Disc_Leg1["Leg1 Disc PV01"] = [0] * ngreek_leg1_Disc
            PV01_Ref_Leg1 = pd.DataFrame(RefTermLeg1_np, columns = ["Leg1 Ref Curve Term"])
            PV01_Ref_Leg1["Leg1 Ref PV01"] = [0] * ngreek_leg1_Ref
            PV01_DiscRef_Leg1 = pd.DataFrame(DiscTermLeg1_np, columns = ["Leg1 Disc&Ref Curve Term"])
            PV01_DiscRef_Leg1["Leg1 Disc&Ref PV01"] = np.ctypeslib.as_array(KeyRateLeg1PV01[2 * ngreek_leg1_Disc :3 * ngreek_leg1_Disc], shape = (ngreek_leg1_Ref, ))
            Result2_Leg1 = pd.concat([PV01_Disc_Leg1, PV01_Ref_Leg1, PV01_DiscRef_Leg1], axis = 1)

        ngreek_leg2_Disc = int(Disc_NTerm_Leg2.value)
        ngreek_leg2_Ref = int(Ref_NTerm_Leg2.value)
        Leg2_SameCurveFlag = 0
        if ngreek_leg2_Disc == ngreek_leg2_Ref : 
            if (DiscTermLeg2_np == RefTermLeg2_np).sum() == ngreek_leg2_Disc and (DiscRateLeg2_np == RefRateLeg2_np).sum() == ngreek_leg2_Disc : 
                Leg2_SameCurveFlag = 1

        if Leg2_SameCurveFlag == 0 : 
            #Result2_Leg2 = pd.DataFrame([])
            PV01_Disc_Leg2 = pd.DataFrame(DiscTermLeg2_np, columns = ["Leg2 Disc Curve Term"])
            PV01_Disc_Leg2["Leg2 Disc PV01"] = np.ctypeslib.as_array(KeyRateLeg2PV01[:ngreek_leg2_Disc], shape = (ngreek_leg2_Disc, ))
            PV01_Ref_Leg2 = pd.DataFrame(RefTermLeg2_np, columns = ["Leg2 Ref Curve Term"])
            PV01_Ref_Leg2["Leg2 Ref PV01"] = np.ctypeslib.as_array(KeyRateLeg2PV01[ngreek_leg2_Disc :ngreek_leg2_Disc + ngreek_leg2_Ref], shape = (ngreek_leg2_Ref, ))
            Result2_Leg2 = pd.concat([PV01_Disc_Leg2, PV01_Ref_Leg2], axis = 1)
            Result2_Leg2["Leg2 Disc&Ref Curve Term"] = 0
            Result2_Leg2["Leg2 Disc&Ref PV01"] = 0
        else : 
            PV01_Disc_Leg2 = pd.DataFrame(DiscTermLeg2_np, columns = ["Leg2 Disc Curve Term"])
            PV01_Disc_Leg2["Leg2 Disc PV01"] = [0] * ngreek_leg2_Disc
            PV01_Ref_Leg2 = pd.DataFrame(RefTermLeg2_np, columns = ["Leg2 Ref Curve Term"])
            PV01_Ref_Leg2["Leg2 Ref PV01"] = [0] * ngreek_leg2_Ref
            PV01_DiscRef_Leg2 = pd.DataFrame(DiscTermLeg2_np, columns = ["Leg2 Disc&Ref Curve Term"])
            PV01_DiscRef_Leg2["Leg2 Disc&Ref PV01"] = np.ctypeslib.as_array(KeyRateLeg2PV01[2 * ngreek_leg2_Disc :3 * ngreek_leg2_Disc], shape = (ngreek_leg2_Ref, ))
            Result2_Leg2 = pd.concat([PV01_Disc_Leg2, PV01_Ref_Leg2, PV01_DiscRef_Leg2], axis = 1)

        Result = pd.concat([Result1, Result2_Leg1, Result2_Leg2],axis = 1).applymap(lambda x : '' if 'nan' in str(x) else x)

        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    

        PrevTreeFlag = insert_dataframe_to_treeview(tree, Result.reset_index(), width = 100)
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2      
        MyArrays[4] = Result
        MyArrays[5] = pd.DataFrame(ResultPrice)
        #df.to_excel("ResultExcel.xlsx",index = False, header=False)
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()     
    return MyArrays[5]
ResultData, ZeroTerm, ZeroRate = HullWhite1FactorCalibration()
RefRateMultipleList = [str(n) + ' : R x ' + str(i) + '배 페이오프' for n, i in enumerate(np.arange(0,50,0.25))] + [str(-n) + ' : R x ' + str(-i) + '배 페이오프' for n, i in enumerate(np.arange(0,50,0.25))][1:]
root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings()

YYYY = int(today_YYYYMMDD) // 10000

left_frame = tk.Frame(main_frame)
left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=today_YYYYMMDD)
v_EffectiveDate = make_variable_interface(left_frame, 'EffectiveDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=today_YYYYMMDD - 20000)
v_MaturityDate = make_variable_interface(left_frame, 'MaturityDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=today_YYYYMMDD + 50000)
vb_NAFlag = make_listvariable_interface(left_frame, 'NA/BOND Flag', ["0: NA교환안함","1: NA교환함","-1: Callable Bond평가"], bold = True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)
vb_Phase2UseFlag = make_listvariable_interface(left_frame, 'Phase2Use Flag', ["0: Phase2 사용안함","1: Phase2 사용"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)
v_Phase2StartDate = make_variable_interface(left_frame, 'Phase2StartDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=today_YYYYMMDD + 20000)
vb_NationFlag = make_listvariable_interface(left_frame, '국가(Holiday용)', ["0: 한국","1: 미국","2: 영국","3: NYMEX","4: NYSE","-1: 그 외"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)

left_frame2 = tk.Frame(main_frame)
left_frame2.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')

vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame2, '연간 쿠폰지급수\n(CD3M = 4)', ["0","1","2","4","6"], titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3, pady = 1)
vb_L1_DayCount = make_listvariable_interface(left_frame2, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, pady = 1)
v_L1_RefSwapMaturity_T = make_listvariable_interface(left_frame2, '기초금리 만기(년)', np.vectorize(lambda x, y : str(x) + " : " + str(y))(np.arange(0,200), np.arange(1, 201) * 0.25), listheight = 3, textfont = 11, titlelable=True, titleName = "레퍼런스금리정보",defaultflag = True, defaultvalue=0, bold = False, pady = 1)
    
vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame2, '기초금리 연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=2, pady = 1)
v_L1_RCap = make_variable_interface(left_frame2, '기초금리RangeCap(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =100, pady = 1)
v_L1_RFloor = make_variable_interface(left_frame2, '기초금리RangeFloor(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =-100, pady = 1)
v_L1_RangeMultiple = make_variable_interface(left_frame2, '금리Range조건Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
v_L1_PayoffMultiple = make_listvariable_interface(left_frame2, '금리PayoffMultiple', RefRateMultipleList, listheight = 5, textfont = 11,defaultflag = True, defaultvalue=0, bold = False, pady = 1, width= 23)

left_frame3 = tk.Frame(main_frame)
left_frame3.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
v_L1_FixedCpnRate_P1 = make_variable_interface(left_frame3, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, titlelable=True, titleName='Leg1 Phase1',defaultvalue =3.19, pady = 1)
v_L1_RangeFixedRate_P1 = make_variable_interface(left_frame3, 'Range충족시금리(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
vb_L1_StructuredFlag_P1 = make_listvariable_interface(left_frame3, '구조화금리사용Flag', ["0: 구조화Payoff미사용","1: 구조화Payoff사용"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)

v_L1_FixedCpnRate_P2 = make_variable_interface(left_frame3, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, titlelable=True, titleName='Leg1 Phase2',defaultvalue =3.19, pady = 1)
v_L1_RangeFixedRate_P2 = make_variable_interface(left_frame3, 'Range충족시금리(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
vb_L1_StructuredFlag_P2 = make_listvariable_interface(left_frame3, '구조화금리사용Flag', ["0: 구조화Payoff미사용","1: 구조화Payoff사용"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)
vb_L1_NumCpnOneYear_P2 = make_listvariable_interface(left_frame3, 'PH2 연간 쿠폰지급수\n(CD3M = 4)', ["0","1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3, pady = 1)

#
left_frame4 = tk.Frame(main_frame)
left_frame4.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')

vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(left_frame4, '연간 쿠폰지급수\n(CD3M = 4)', ["0","1","2","4","6"], titlelable = True, titleName = "Leg2 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3, pady = 1)
vb_L2_DayCount = make_listvariable_interface(left_frame4, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, pady = 1)
v_L2_RefSwapMaturity_T = make_listvariable_interface(left_frame4, '기초금리 만기(년)', np.vectorize(lambda x, y : str(x) + " : " + str(y))(np.arange(0,200), np.arange(1, 201) * 0.25), listheight = 3, textfont = 11, titlelable=True, titleName = "레퍼런스금리정보",defaultflag = True, defaultvalue=0, bold = False, pady = 1)
    
vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame4, '기초금리 연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=2, pady = 1)
v_L2_RCap = make_variable_interface(left_frame4, '기초금리RangeCap(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =100, pady = 1)
v_L2_RFloor = make_variable_interface(left_frame4, '기초금리RangeFloor(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =-100, pady = 1)
v_L2_RangeMultiple = make_variable_interface(left_frame4, '금리Range조건Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
v_L2_PayoffMultiple = make_listvariable_interface(left_frame4, '금리PayoffMultiple', RefRateMultipleList, listheight = 5, textfont = 11,defaultflag = True, defaultvalue=4, bold = False, pady = 1, width= 23)

left_frame5 = tk.Frame(main_frame)
left_frame5.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
v_L2_FixedCpnRate_P1 = make_variable_interface(left_frame5, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, titlelable=True, titleName='Leg2 Phase1',defaultvalue =3.19, pady = 1)
v_L2_RangeFixedRate_P1 = make_variable_interface(left_frame5, 'Range충족시금리(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
vb_L2_StructuredFlag_P1 = make_listvariable_interface(left_frame5, '구조화금리사용Flag', ["0: 구조화Payoff미사용","1: 구조화Payoff사용"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)

v_L2_FixedCpnRate_P2 = make_variable_interface(left_frame5, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, titlelable=True, titleName='Leg2 Phase2',defaultvalue =3.19, pady = 1)
v_L2_RangeFixedRate_P2 = make_variable_interface(left_frame5, 'Range충족시금리(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
vb_L2_StructuredFlag_P2 = make_listvariable_interface(left_frame5, '구조화금리사용Flag', ["0: 구조화Payoff미사용","1: 구조화Payoff사용"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)
vb_L2_NumCpnOneYear_P2 = make_listvariable_interface(left_frame5, 'PH2 연간 쿠폰지급수\n(CD3M = 4)', ["0","1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3, pady = 1)

left_frame6 = tk.Frame(main_frame)
left_frame6.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
sht_Holiday = AddVariableSheet(left_frame6, nindexs = 1000, ncolumns= 1,targetcolumns = ["Holidays"], defaultvalues = (), VariableName = "Leg1 Holidays", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 150, sheet_height = 300, MaxHeight=20)

left_frame7 = tk.Frame(main_frame)
left_frame7.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
DefaultTermHistory = [TimestampToYYYYMMDD(today + pd.DateOffset(days = -i)) for i in range(200) ][::-1]
defaultvaluesHistoryLeg12 = (DefaultTermHistory, [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory))
RefRateHistory = AddVariableSheet(left_frame7, nindexs = len(DefaultTermHistory), ncolumns= 3,targetcolumns = ["Date","Rate(Leg1)","Rate(Leg2)"], defaultvalues = defaultvaluesHistoryLeg12, VariableName = "기초금리History", myfont = 10, anchor = 'w', padx = 4, pady = 2, sheet_width = 100, sheet_height = 100, MaxHeight=20)
RefRateHistory.set_all_column_widths(width=85)

left_frame8 = tk.Frame(main_frame)
left_frame8.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
OptStartDate =[TimestampToYYYYMMDD(i) for i in MakeSchedule(today_YYYYMMDD, today_YYYYMMDD + 40000, 12)[1:]]
OptPayDate = [TimestampToYYYYMMDD(YYYYMMDDToTimeStamp(i) + pd.DateOffset(days = 20)) for i in OptStartDate]

vb_OptionFlag = make_listvariable_interface(left_frame8, '옵션보유자', ["0 : Leg1이 옵션보유"," 1: Leg2이 옵션보유"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, pady = 1)
sht_OptScheduleInfo = AddVariableSheet(left_frame8, nindexs = len(OptStartDate) + 50, ncolumns= 2,targetcolumns = ["옵션 선언일","옵션행사일"], defaultvalues = (OptStartDate + ['']* 50, OptPayDate+ ['']* 50), VariableName = "OptionDate", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 115, sheet_height = 40, MaxHeight=20, headerfont= 9)
sht_OptScheduleInfo.set_all_column_widths(width=87)

left_frame9 = tk.Frame(main_frame)
left_frame9.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
nindexs = 7
ncolumns = 2
TargetRate = list(np.array(ZeroRate) * 100) if np.abs(np.array(ZeroRate)).max() < 0.2 else ZeroRate
defaultvalues = (ZeroTerm + ['']* 10, TargetRate + ['']* 10)
targetcolumns = ["Term", "Rate"]
sht_DiscCurve = AddVariableSheet(left_frame9, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = defaultvalues, VariableName = "ZeroCurve", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 70, sheet_height = 30, titlelable= True, titleName = "MarketData", MaxHeight=10)
sht_DiscCurve.set_all_column_widths(width=50)
v_Kappa = make_variable_interface(left_frame9, 'kappa', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultData["HWKappa"].iloc[0])
HWTerm = list(ResultData["OptMat"].values)
HWVol = list(ResultData["HWVol"].values)
defaultvalues2 = (HWTerm + ['']* 10, HWVol + ['']* 10)
sht_HWVol = AddVariableSheet(left_frame9, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','HWVol'], defaultvalues = defaultvalues2, VariableName = "HWVol", myfont = 10, anchor = 'w', padx = 5, pady = 2, sheet_width = 70, sheet_height = 30, MaxHeight=10)
sht_HWVol.set_all_column_widths(width=50)

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
    MyArrays[0] = PrevTreeFlag 
    MyArrays[1] = tree 
    MyArrays[2] = scrollbar
    MyArrays[3] = scrollbar2      
    #MyArrays[4] = Result
    #MyArrays[5] = pd.DataFrame(ResultPrice)
    #df.to_excel("ResultExcel.xlsx",index = False, header=False)
temp_func = lambda : run_function(MyArrays)
root.mainloop()    
VBAString = '''
Public Declare PtrSafe Function IRStructuredSwapFDM_Greek Lib "IRStructuredSwapOneCurve.dll" ( _
    ByVal PriceDate As Long, ByVal EffectiveDate As Long, ByVal Maturity As Long, ByVal NAFlag As Long, ByVal NA As Double, _
    ByRef NAdditionalHolidays As Long, ByRef AdditionalHolidays As Long, ByRef NationFlag As Long, ByRef NumCpnAnn As Long, ByRef MaxLossRetRcvPay As Double, _
    ByRef MultipleRatefixPayoffRcvPay As Double, ByRef DayCountRcvPay As Long, ByRef PowerSpreadFlagRcvPay As Long, ByRef RangeMaxMinRcvPay As Double, ByRef InfoRefRateRcvPay As Double, _
    ByVal RcvLegFixedRate As Double, ByVal RcvLegRangeCoupon As Double, ByVal RcvLegStructuredFlag As Long, ByVal PayLegFixedRate As Double, ByVal PayLegRangeCoupon As Double, _
    ByVal PayLegStructuredFlag As Long, ByVal Phase2UseFlag As Long, ByVal Phase2Date As Long, ByVal Phase2RcvLegFixedRate As Double, ByVal Phase2RcvLegRangeCoupon As Double, _
    ByVal Phase2RcvLegStructuredFlag As Long, ByVal Phase2PayLegFixedRate As Double, ByVal Phase2PayLegRangeCoupon As Double, ByVal Phase2PayLegStructuredFlag As Long, ByRef NumCpnAnnPhase2RcvPay As Long, _
    ByVal NOption As Long, ByRef OptionDate As Long, ByRef OptionPayDate As Long, ByVal OptionType As Long, ByVal NRcvRateHistory As Long, _
    ByRef NRcvRateHistoryDate As Long, ByRef RcvRateHistory As Double, ByVal NPayRateHistory As Long, ByRef PayRateHistoryDate As Long, ByRef PayRateHistory As Double, _
    ByVal NZeroRate As Long, ByRef ZeroTerm As Double, ByRef ZeroRate As Double, ByVal NZeroDiscRate As Long, ByRef ZeroDiscTerm As Double, _
    ByRef ZeroDiscRate As Double, ByVal HW2FFLag As Long, ByVal NHWVol As Long, ByRef HWVolTerm As Double, ByRef HWVol As Double, _
    ByRef kappa As Double, ByVal FactorCorrelation As Double, ByRef RangeAccrualFlagRcvPay As Long, ByRef InterestRateRoundingRcvPay As Long, ByRef ResultCpnDateRcv As Long, _
    ByRef ResultCpnDatePay As Long, ByRef ResultFixingRateCpn As Double, ByRef Greek As Double, ByVal GreekFlag As Long, ByVal TextFlag As Long _
) As Long
'''
CalcFunc, VariablesFormat, VariableNames = ConvertPythonFormatfromVBAformat(VBAString)
#if __name__ == '__main__' : 
#    n = MainViewer(Title = 'Viewer', MyText = '사용하실 기능은?(번호입력)', MyList = ["1: IRStructured Swap","2: IRS"], size = "800x450+30+30", splitby = ":", listheight = 8, textfont = 13, titlelable = False, titleName = "Name", MultiSelection = False, defaultvalue = 0, addtreeflag = False, treedata = pd.DataFrame([]), DefaultStringList = [], width = 95, expand = True)
#    if n == 1 : 
#        IRStucturedSwapOneCurve()
#    elif n == 2 : 
#        IRSPricing()
# %%frame = left_frame 

VBAString = '''
Public Declare PtrSafe Function Calc_BondForward Lib "BondForward.dll" ( _
    ByVal Nominal As Double, ByVal Fix0Flo1Flag As Long, ByVal PriceDate As Long, ByVal RefBondEffectiveDate As Long, ByVal RefBondMaturityDate As Long, _
    ByVal RefBondNumCpnOneYear As Long, ByVal RefBondCpnRate As Double, ByVal NDayFromBondEndToPay As Long, ByVal ForwardMaturityDate As Long, ByVal NBondZeroCurveTerm As Long, _
    ByRef BondZeroCurveTerm As Double, ByRef BondZeroCurveRate As Double, ByVal BondYTMFlag As Long, ByVal BondMarketPriceFlag As Long, ByVal BondMarketPrice As Double, _
    ByVal ForwardExercisePrice As Double, ByVal NRiskfreeCurveTerm As Long, ByRef RiskfreeCurveTerm As Double, ByRef RiskfreeCurveRate As Double, ByVal NFX As Long, _
    ByRef FXTerm As Double, ByRef FXRate As Double, ByVal DayCountFlag As Long, ByVal FixingRateFloatLeg As Double, ByVal NHolidays As Long, _
    ByRef Holidays As Long, ByVal GreekFlag As Long, ByVal TextFlag As Long, ByVal NMaxResultSchedule As Long, ByVal AccruedInterestFlag As Long, _
    ByRef ResultPriceArray As Double, ByRef ResultSchedule As Double, ByRef ResultGreek As Double _
) As Long
'''
CalcFunc, VariablesFormat, VariableNames = ConvertPythonFormatfromVBAformat(VBAString)
TempSchedule =[TimestampToYYYYMMDD(i) for i in MakeSchedule(today_YYYYMMDD, today_YYYYMMDD + 100000, 3)]
StartSchedule = TempSchedule[:-1]
EndSchedule = TempSchedule[1:]
Multiple = [1] * len(StartSchedule)
Multiple2 = [0] * len(StartSchedule)
FixedCpnRate = [3.5] * len(StartSchedule)
FixedCpnRate2 = [0] * len(StartSchedule)
FixedRate = [0.0] * len(StartSchedule)
defaultvalues = ([0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0] + ['']* 10, [3.5, 3.5, 3.5, 3.5, 3.6, 3.65, 3.66, 3.71, 3.81, 3.87, 3.87, 3.88, 3.91, 3.92, 3.95]+ ['']* 10)
targetcolumns = ["Term", "Rate"]
nindexs = 7
ncolumns = 2
k = 0
lst = []
for n, s in enumerate(VariableNames) : 
    if 'term' in s.lower() and 'n' != s.lower()[0]:
        theme = s.lower().split('term')[0]
        themeTerm = s
        idxntheme = -1
        if theme in VariableNames[n-1].lower() and ('n' == VariableNames[n-1].lower()[0] or 'num' in VariableNames[n-1].lower()) : 
            ntheme = VariableNames[n-1]
            idxntheme = n-1
        elif theme in VariableNames[n+1].lower() and ('n' == VariableNames[n+1].lower()[0] or 'num' in VariableNames[n+1].lower()) :
            ntheme = VariableNames[n+1]        
            idxntheme = n+1
        elif theme in VariableNames[n-1].lower() and ('n' != VariableNames[n-1].lower()[0] or 'num' not in VariableNames[n-1].lower()) and ('rate' in VariableNames[n-1].lower() or 'vol' in VariableNames[n-1].lower() or 'zero' in VariableNames[n-1].lower()) :
            themerate = VariableNames[n-1]
        elif theme in VariableNames[n+1].lower() and ('n' != VariableNames[n+1].lower()[0] or 'num' not in VariableNames[n+1].lower()) and ('rate' in VariableNames[n+1].lower() or 'vol' in VariableNames[n+1].lower() or 'zero' in VariableNames[n+1].lower()) :
            themerate = VariableNames[n+1]
        elif idxntheme == n - 1 : 
            themerate = VariableNames[n+1]
        break


    elif 'tenor' in s.lower() : 

        k += 1




# %%
