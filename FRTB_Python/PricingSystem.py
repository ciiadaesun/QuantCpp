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



CSRRW = [ 0.005, 0.01, 0.05, 0.03, 0.03, 0.02, 0.015, 0.025, 0.02, 0.04, 0.12, 0.07, 0.085, 0.055, 0.05, 0.12, 0.015, 0.05]

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

def Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate, CompareNumber = 0.5) : 
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
        resulttype = 'long' if 'long' in x.lower() else ('double' if 'string' not in x.lower() else 'string')
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
        elif resultmeasure == 'vector' and resulttype == 'double' : 
            startidx = x.lower().index('byref') + 6
            endidx = x.lower().index('as double')
            resultname = x[startidx:endidx].replace(" ","")
        elif resultmeasure == 'scalar' and resulttype == 'string' : 
            startidx = x.lower().index('byval') + 6
            endidx = x.lower().index('as string')
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
        elif resultmeasure + "_" + resulttype == 'vector_double' :
            return c_double_p, resultname
        elif resultmeasure + "_" +  resulttype == 'scalar_string' :
            return ct.POINTER(ct.c_char), resultname
        else : 
            return c_double_p, resultname

    Targetdll = ct.WinDLL(ReleaseFolder + TargetDllString)
    CalcFunc = eval('Targetdll.' + TargetFunctionString)
    CalcFunc.restype = ct.c_long

    VariablesFormat = [SplitVBAVariables(i) for i in StringArray]
    CalcFunc.argtypes = [v[0] for v in VariablesFormat]
    VariableNames = [v[1] for v in VariablesFormat]
    return CalcFunc, VariablesFormat, VariableNames

def HullWhite1FactorCalibration() : 
    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings('HW1F Calibration')
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
    ResultValue2 = pd.DataFrame(defaultvalues2, index = ['OptMat','SwapMat','SwaptionVol%']).T.applymap(lambda x : np.nan if str(x) == '' else x).dropna()
    ResultValue2['HWVol'] = ResultValue2['SwaptionVol%'].astype(np.float64)/100
    ResultValue2['HWKappa'] = 0.01

    DefaultZeroDF = pd.DataFrame(defaultvalues, index = ['ZeroTerm','ZeroRate']).T.applymap(lambda x : np.nan if str(x) == '' else x).dropna()
    ZeroTermList, ZeroRateList = list(DefaultZeroDF["ZeroTerm"].values), list(DefaultZeroDF["ZeroRate"].values.astype(np.float64)/100)
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultValue, ResultValue2,ZeroTermList, ZeroRateList]
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

def IRSPricing() : 
    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings('IRS Pricing')

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
    vb_GreekFlag = make_listvariable_interface(left_frame, 'Greek Flag', ["0 : Greek 산출안함","1 : Greek 산출함"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=1, bold = True)
    vb_TextFlag = make_listvariable_interface(left_frame, 'Text Flag', ["0 : Logging 안함","1 : Logging함"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)

    center_frame = tk.Frame(main_frame)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_DiscCurveLeg1 = AddVariableSheet(center_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "DiscZeroCurve(Leg1)", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, titlelable= True, titleName = "Leg1 MarketData", MaxHeight=10)
    sht_DiscCurveLeg1.set_all_column_widths(width=50)
    sht_RefCurveLeg1 = AddVariableSheet(center_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "EstZeroCurve(Leg1)", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, MaxHeight=10)
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
    sht_DiscCurveLeg2 = AddVariableSheet(center_frame_Leg2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "DiscZeroCurve(Leg2)", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, titlelable= True, titleName = "Leg1 MarketData", MaxHeight=10)
    sht_DiscCurveLeg2.set_all_column_widths(width=50)
    sht_RefCurveLeg2 = AddVariableSheet(center_frame_Leg2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = targetcolumns, defaultvalues = defaultvalues, VariableName = "EstZeroCurve(Leg2)", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, MaxHeight=10)
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
    v_cvname_dscL1 = make_variable_interface(Result_frame, 'Leg1 할인커브명', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 'KRW IRS')
    v_cvname_estL1 = make_variable_interface(Result_frame, 'Leg1 추정커브명', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 'KRW IRS')
    v_cvname_dscL2 = make_variable_interface(Result_frame, 'Leg2 할인커브명', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 'KRW IRS')
    v_cvname_estL2 = make_variable_interface(Result_frame, 'Leg2 추정커브명', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 'KRW IRS')

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

        cvname_dscL1 = str(v_cvname_dscL1.get()) if len(str(v_cvname_dscL1.get())) > 0 else 'KRW IRS'
        cvname_estL1 = str(v_cvname_estL1.get()) if len(str(v_cvname_estL1.get())) > 0 else 'KRW IRS'
        cvname_dscL2 = str(v_cvname_dscL2.get()) if len(str(v_cvname_dscL2.get())) > 0 else 'KRW IRS'
        cvname_estL2 = str(v_cvname_estL2.get()) if len(str(v_cvname_estL2.get())) > 0 else 'KRW IRS'

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
        DiscLeg1["Term"] = DiscLeg1["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        DiscLeg1["Rate"] = DiscLeg1["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)

        DiscTermLeg1 = DiscLeg1["Term"].values
        Disc_NTerm_Leg1 = len(DiscTermLeg1)
        DiscRateLeg1 = DiscLeg1["Rate"].values if DiscLeg1["Rate"].values.max() < 1.0 else DiscLeg1["Rate"].values/100
        RefLeg1 = get_from_sheetinterface(sht_RefCurveLeg1)
        RefLeg1["Term"] = RefLeg1["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        RefLeg1["Rate"] = RefLeg1["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)

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
        CPN_Leg1 = ScheduleDF_Leg1["고정쿠폰(%)"].astype(np.float64).values/100
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
        CPN_Leg2 = ScheduleDF_Leg2["고정쿠폰(%)"].astype(np.float64).values/100
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
            PV01_Disc_Leg1['Leg1CvNameDisc'] = [cvname_dscL1] * len(DiscTermLeg1_np)
            PV01_Disc_Leg1["Leg1 Disc PV01"] = np.ctypeslib.as_array(KeyRateLeg1PV01[:ngreek_leg1_Disc], shape = (ngreek_leg1_Disc, ))
            PV01_Disc_Leg1 = PV01_Disc_Leg1[['Leg1CvNameDisc','Leg1 Disc Curve Term','Leg1 Disc PV01']]
            PV01_Ref_Leg1 = pd.DataFrame(RefTermLeg1_np, columns = ["Leg1 Ref Curve Term"])
            PV01_Ref_Leg1['Leg1CvNameRef'] = [cvname_estL1] * len(RefTermLeg1_np)
            PV01_Ref_Leg1["Leg1 Ref PV01"] = np.ctypeslib.as_array(KeyRateLeg1PV01[ngreek_leg1_Disc :ngreek_leg1_Disc + ngreek_leg1_Ref], shape = (ngreek_leg1_Ref, ))
            PV01_Ref_Leg1 = PV01_Ref_Leg1[['Leg1CvNameRef',"Leg1 Ref Curve Term","Leg1 Ref PV01"]]
            Result2_Leg1 = pd.concat([PV01_Disc_Leg1, PV01_Ref_Leg1], axis = 1)
            Result2_Leg1['Leg1 Disc&Ref CvName'] = ''
            Result2_Leg1["Leg1 Disc&Ref Curve Term"] = 0
            Result2_Leg1["Leg1 Disc&Ref PV01"] = 0
        else : 
            PV01_Disc_Leg1 = pd.DataFrame(DiscTermLeg1_np, columns = ["Leg1 Disc Curve Term"])
            PV01_Disc_Leg1['Leg1CvNameDisc'] = [cvname_dscL1] * len(DiscTermLeg1_np)
            PV01_Disc_Leg1["Leg1 Disc PV01"] = [0] * ngreek_leg1_Disc
            PV01_Disc_Leg1 = PV01_Disc_Leg1[['Leg1CvNameDisc','Leg1 Disc Curve Term','Leg1 Disc PV01']]
            PV01_Ref_Leg1 = pd.DataFrame(RefTermLeg1_np, columns = ["Leg1 Ref Curve Term"])
            PV01_Ref_Leg1['Leg1CvNameRef'] = [cvname_estL1] * len(RefTermLeg1_np)
            PV01_Ref_Leg1["Leg1 Ref PV01"] = [0] * ngreek_leg1_Ref
            PV01_Ref_Leg1 = PV01_Ref_Leg1[['Leg1CvNameRef',"Leg1 Ref Curve Term","Leg1 Ref PV01"]]
            PV01_DiscRef_Leg1 = pd.DataFrame(DiscTermLeg1_np, columns = ["Leg1 Disc&Ref Curve Term"])
            PV01_DiscRef_Leg1['Leg1 Disc&Ref CvName'] = cvname_estL1
            PV01_DiscRef_Leg1["Leg1 Disc&Ref PV01"] = np.ctypeslib.as_array(KeyRateLeg1PV01[2 * ngreek_leg1_Disc :3 * ngreek_leg1_Disc], shape = (ngreek_leg1_Ref, ))
            PV01_DiscRef_Leg1 = PV01_DiscRef_Leg1[['Leg1 Disc&Ref CvName',"Leg1 Disc&Ref Curve Term","Leg1 Disc&Ref PV01"]]
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
            PV01_Disc_Leg2['Leg2CvNameDisc'] = [cvname_dscL2] * len(DiscTermLeg2_np)
            PV01_Disc_Leg2["Leg2 Disc PV01"] = np.ctypeslib.as_array(KeyRateLeg2PV01[:ngreek_leg2_Disc], shape = (ngreek_leg2_Disc, ))
            PV01_Disc_Leg2 = PV01_Disc_Leg2[['Leg2CvNameDisc','Leg2 Disc Curve Term','Leg2 Disc PV01']]
            PV01_Ref_Leg2 = pd.DataFrame(RefTermLeg2_np, columns = ["Leg2 Ref Curve Term"])
            PV01_Ref_Leg2['Leg2CvNameRef'] = [cvname_estL2] * len(RefTermLeg2_np)
            PV01_Ref_Leg2["Leg2 Ref PV01"] = np.ctypeslib.as_array(KeyRateLeg2PV01[ngreek_leg2_Disc :ngreek_leg2_Disc + ngreek_leg2_Ref], shape = (ngreek_leg2_Ref, ))
            PV01_Ref_Leg2 = PV01_Ref_Leg2[['Leg2CvNameRef',"Leg2 Ref Curve Term","Leg2 Ref PV01"]]
            Result2_Leg2 = pd.concat([PV01_Disc_Leg2, PV01_Ref_Leg2], axis = 1)
            Result2_Leg2['Leg2 Disc&Ref CvName'] = ''
            Result2_Leg2["Leg2 Disc&Ref Curve Term"] = 0
            Result2_Leg2["Leg2 Disc&Ref PV01"] = 0
        else : 
            PV01_Disc_Leg2 = pd.DataFrame(DiscTermLeg2_np, columns = ["Leg2 Disc Curve Term"])
            PV01_Disc_Leg2['Leg2CvNameDisc'] = [cvname_dscL2] * len(DiscTermLeg2_np)
            PV01_Disc_Leg2["Leg2 Disc PV01"] = [0] * ngreek_leg2_Disc
            PV01_Disc_Leg2 = PV01_Disc_Leg2[['Leg2CvNameDisc','Leg2 Disc Curve Term','Leg2 Disc PV01']]
            PV01_Ref_Leg2 = pd.DataFrame(RefTermLeg2_np, columns = ["Leg2 Ref Curve Term"])
            PV01_Ref_Leg2['Leg2CvNameRef'] = [cvname_estL2] * len(RefTermLeg2_np)
            PV01_Ref_Leg2["Leg2 Ref PV01"] = [0] * ngreek_leg2_Ref
            PV01_Ref_Leg2 = PV01_Ref_Leg2[['Leg2CvNameRef',"Leg2 Ref Curve Term","Leg2 Ref PV01"]]
            PV01_DiscRef_Leg2 = pd.DataFrame(DiscTermLeg2_np, columns = ["Leg2 Disc&Ref Curve Term"])
            PV01_DiscRef_Leg2['Leg2 Disc&Ref CvName'] = cvname_estL2
            PV01_DiscRef_Leg2["Leg2 Disc&Ref PV01"] = np.ctypeslib.as_array(KeyRateLeg2PV01[2 * ngreek_leg2_Disc :3 * ngreek_leg2_Disc], shape = (ngreek_leg2_Ref, ))
            PV01_DiscRef_Leg2 = PV01_DiscRef_Leg2[['Leg2 Disc&Ref CvName',"Leg2 Disc&Ref Curve Term","Leg2 Disc&Ref PV01"]]
            Result2_Leg2 = pd.concat([PV01_Disc_Leg2, PV01_Ref_Leg2, PV01_DiscRef_Leg2], axis = 1)
        Leg1Sensi = (PV01_Disc_Leg1["Leg1 Disc PV01"].apply(lambda x : float(x) if str(x) != '' else 0).sum() + 
                     PV01_Ref_Leg1["Leg1 Ref PV01"].apply(lambda x : float(x) if str(x) != '' else 0).sum() +
                     PV01_DiscRef_Leg1["Leg1 Disc&Ref PV01"].apply(lambda x : float(x) if str(x) != '' else 0).sum())/0.0001
        Leg2Sensi = (PV01_Disc_Leg2["Leg2 Disc PV01"].apply(lambda x : float(x) if str(x) != '' else 0).sum() + 
                     PV01_Ref_Leg2["Leg2 Ref PV01"].apply(lambda x : float(x) if str(x) != '' else 0).sum() +
                     PV01_DiscRef_Leg2["Leg2 Disc&Ref PV01"].apply(lambda x : float(x) if str(x) != '' else 0).sum())/0.0001
        
        GIRR = np.round(abs(abs(Leg1Sensi) - abs(Leg2Sensi)) * 0.013/np.sqrt(2) * 0.75, 2)
        RWA = np.round(GIRR * 12.5, 2)
        RWA_Pct = np.round(RWA/NominalLeg1, 4)
        output_label.config(text = f"산출결과: \n{ret}\nSwapRate: \n{str(np.round(ResultPrice[0]*100,6))+"%"}\nValue : {ResultPrice[1] - ResultPrice[2]}\nLeg1 : \n{ResultPrice[1]}\nLeg2 : \n{ResultPrice[2]}\n GIRR : \n{GIRR}\n RWA : \n{RWA}({RWA_Pct * 100})%", font = ("맑은 고딕", 12, 'bold'))
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
        MyArrays[5] = pd.DataFrame(Result)
        if LoggingFlag > 0 : 
            Result.to_excel("IRS_PriceResult.xlsx")
        #df.to_excel("ResultExcel.xlsx",index = False, header=False)
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()     
    return MyArrays[5]

def IRS_Callable() : 
    ResultData, ZeroTerm, ZeroRate = HullWhite1FactorCalibration()
    RefRateMultipleList = [str(n) + ' : R x ' + str(i) + '배 페이오프' for n, i in enumerate(np.arange(0,50,0.25))] + [str(-n) + ' : R x ' + str(-i) + '배 페이오프' for n, i in enumerate(np.arange(0,50,0.25))][1:]

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

    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings('Structured Swap HW 1F FDM')
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

    vb_L1_DayCount = make_listvariable_interface(left_frame2, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, titlelable=True, titleName="Leg1 Information",defaultflag = True, defaultvalue=0, pady = 1)
    vb_L1_RefSwapMaturity_T = make_listvariable_interface(left_frame2, '기초금리 만기(년)', np.vectorize(lambda y : str(y))(np.arange(1, 201) * 0.25), listheight = 3, textfont = 11, titlelable=True, titleName = "\n레퍼런스금리정보",defaultflag = True, defaultvalue=0, bold = False, pady = 3)
        
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame2, '기초금리 연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=2, pady = 1)
    v_L1_RCap = make_variable_interface(left_frame2, '기초금리RangeCap(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =100, pady = 1)
    v_L1_RFloor = make_variable_interface(left_frame2, '기초금리RangeFloor(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =-100, pady = 1)
    v_L1_RangeMultiple = make_variable_interface(left_frame2, '금리Range조건Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
    v_L1_PayoffMultiple = make_listvariable_interface(left_frame2, '금리PayoffMultiple', RefRateMultipleList, listheight = 5, textfont = 11,defaultflag = True, defaultvalue=0, bold = False, pady = 1, width= 23)

    left_frame3 = tk.Frame(main_frame)
    left_frame3.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame3, '연간 쿠폰지급수\n(CD3M = 4)', ["0","1","2","4","6"], titlelable = True, titleName = "Leg1 Phase1", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3, pady = 1)
    v_L1_FixedCpnRate_P1 = make_variable_interface(left_frame3, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, titlelable=False, titleName='Leg1 Phase1',defaultvalue =3.19, pady = 1)
    v_L1_RangeFixedRate_P1 = make_variable_interface(left_frame3, 'Range충족시금리(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
    vb_L1_StructuredFlag_P1 = make_listvariable_interface(left_frame3, '구조화금리사용Flag', ["0: 구조화Payoff미사용","1: 구조화Payoff사용"], bold = False, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)

    vb_L1_NumCpnOneYear_P2 = make_listvariable_interface(left_frame3, 'PH2 연간 쿠폰지급수\n(CD3M = 4)', ["0","1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, titlelable=True, titleName='Leg1 Phase2', defaultvalue=3, pady = 1)
    v_L1_FixedCpnRate_P2 = make_variable_interface(left_frame3, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = False, titlelable=True, titleName='Leg1 Phase2',defaultvalue =3.19, pady = 1)
    v_L1_RangeFixedRate_P2 = make_variable_interface(left_frame3, 'Range충족시금리(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
    vb_L1_StructuredFlag_P2 = make_listvariable_interface(left_frame3, '구조화금리사용Flag', ["0: 구조화Payoff미사용","1: 구조화Payoff사용"], bold = False, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)

    #
    left_frame4 = tk.Frame(main_frame)
    left_frame4.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')

    vb_L2_DayCount = make_listvariable_interface(left_frame4, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, titlelable=True, titleName="Leg2 Information", defaultflag = True, defaultvalue=0, pady = 1)
    vb_L2_RefSwapMaturity_T = make_listvariable_interface(left_frame4, '기초금리 만기(년)', np.vectorize(lambda y : str(y))(np.arange(1, 201) * 0.25), listheight = 3, textfont = 11, titlelable=True, titleName = "\n레퍼런스금리정보",defaultflag = True, defaultvalue=0, bold = False, pady = 3)
        
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame4, '기초금리 연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=2, pady = 1)
    v_L2_RCap = make_variable_interface(left_frame4, '기초금리RangeCap(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =100, pady = 1)
    v_L2_RFloor = make_variable_interface(left_frame4, '기초금리RangeFloor(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =-100, pady = 1)
    v_L2_RangeMultiple = make_variable_interface(left_frame4, '금리Range조건Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue =1, pady = 1)
    v_L2_PayoffMultiple = make_listvariable_interface(left_frame4, '금리PayoffMultiple', RefRateMultipleList, listheight = 5, textfont = 11,defaultflag = True, defaultvalue=4, bold = False, pady = 1, width= 23)

    left_frame5 = tk.Frame(main_frame)
    left_frame5.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(left_frame5, '연간 쿠폰지급수\n(CD3M = 4)', ["0","1","2","4","6"], titlelable = True, titleName = "Leg2 Phase1", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3, pady = 1)
    v_L2_FixedCpnRate_P1 = make_variable_interface(left_frame5, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, titlelable=False, titleName='Leg2 Phase1',defaultvalue =0.0, pady = 1)
    v_L2_RangeFixedRate_P1 = make_variable_interface(left_frame5, 'Range충족시금리(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
    vb_L2_StructuredFlag_P1 = make_listvariable_interface(left_frame5, '구조화금리사용Flag', ["0: 구조화Payoff미사용","1: 구조화Payoff사용"], bold = False, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 1)

    vb_L2_NumCpnOneYear_P2 = make_listvariable_interface(left_frame5, 'PH2 연간 쿠폰지급수\n(CD3M = 4)', ["0","1","2","4","6"], listheight = 4, textfont = 11, titlelable=True, titleName='Leg2 Phase2', defaultflag = True, defaultvalue=3, pady = 1)
    v_L2_FixedCpnRate_P2 = make_variable_interface(left_frame5, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, titlelable=False, titleName='Leg2 Phase2',defaultvalue =0.0, pady = 1)
    v_L2_RangeFixedRate_P2 = make_variable_interface(left_frame5, 'Range충족시금리(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
    vb_L2_StructuredFlag_P2 = make_listvariable_interface(left_frame5, '구조화금리사용Flag', ["0: 구조화Payoff미사용","1: 구조화Payoff사용"], bold = False, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 1)

    #left_frame6 = tk.Frame(main_frame)
    #left_frame6.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    #sht_Holiday = AddVariableSheet(left_frame6, nindexs = 1000, ncolumns= 1,targetcolumns = ["Holidays"], defaultvalues = (), VariableName = "Leg1 Holidays", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 150, sheet_height = 300, MaxHeight=20)

    left_frame7 = tk.Frame(main_frame)
    left_frame7.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    DefaultTermHistory = [TimestampToYYYYMMDD(today + pd.DateOffset(days = -i)) for i in range(200) ][::-1]
    defaultvaluesHistoryLeg12 = (DefaultTermHistory, [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory))
    RefRateHistory = AddVariableSheet(left_frame7, nindexs = len(DefaultTermHistory), ncolumns= 3,targetcolumns = ["Date","Rate(Leg1)","Rate(Leg2)"], defaultvalues = defaultvaluesHistoryLeg12, VariableName = "기초금리픽싱History", myfont = 10, anchor = 'w', padx = 4, pady = 2, sheet_width = 100, sheet_height = 100, MaxHeight=20)
    RefRateHistory.set_all_column_widths(width=85)

    left_frame8 = tk.Frame(main_frame)
    left_frame8.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    OptStartDate =[TimestampToYYYYMMDD(i) for i in MakeSchedule(today_YYYYMMDD, today_YYYYMMDD + 40000, 12)[1:]]
    OptPayDate = [TimestampToYYYYMMDD(YYYYMMDDToTimeStamp(i) + pd.DateOffset(days = 20)) for i in OptStartDate]

    vb_OptionFlag = make_listvariable_interface(left_frame8, '옵션보유자', ["0 : Leg1이 옵션보유"," 1: Leg2이 옵션보유"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, pady = 1)
    sht_OptScheduleInfo = AddVariableSheet(left_frame8, nindexs = len(OptStartDate) + 50, ncolumns= 2,targetcolumns = ["옵션 선언일","옵션행사일"], defaultvalues = (OptStartDate + ['']* 50, OptPayDate+ ['']* 50), VariableName = "OptionDate", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 115, sheet_height = 40, MaxHeight=20, headerfont= 9)
    sht_OptScheduleInfo.set_all_column_widths(width=87)

    #left_frame9 = tk.Frame(main_frame)
    #left_frame9.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    nindexs = 7
    ncolumns = 2
    defaultvalues = (ZeroTerm + ['']* 10, ZeroRate + ['']* 10)
    targetcolumns = ["Term", "Rate"]
    DiscCurveTermList = [ZeroTerm]
    DiscCurveRateList = [ZeroRate]
    EstCurveTermList = [ZeroTerm]
    EstCurveRateList = [ZeroRate]
    HWKappaList = [ResultData["HWKappa"].iloc[0]]
    HWKappa2FList = [ResultData["HWKappa"].iloc[0]]
    DiscCurveName = ['KRW IRS']
    EstCurveName = ['KRW IRS']

    HWVolTermList = [list(ResultData["OptMat"].values)]
    HWVolList = [list(ResultData["HWVol"].values)]
    HWVol2FList = [[0.0] * len(list(ResultData["HWVol"].values))]
    def open_result_window(root, DiscCurveTermList, DiscCurveRateList, EstCurveTermList, EstCurveRateList, HWKappaList, HWVolTermList, HWVolList, DiscCurveName, EstCurveName):
        defaultvalues = (DiscCurveTermList[0] + ['']* 10, list(np.array(DiscCurveRateList[0], dtype = np.float64) * 100) + ['']* 10)
        defaultvalues2 = (HWVolTermList[0] + ['']* 10, list(np.array(HWVolList[0], dtype = np.float64) * 100) + ['']* 10)
    
        # 새로운 결과창
        result_window = tk.Toplevel(root)
        result_window.title("MarketData")
        result_window.geometry("1520x700+5+5")
        result_window.resizable(False, False)

        # ==========================================
        # Scrollbar
        # ==========================================

        v_scroll = tk.Scrollbar(
            result_window,
            orient="vertical",
            width=20
        )
        v_scroll.pack(side="right", fill="y")

        h_scroll = tk.Scrollbar(
            result_window,
            orient="horizontal",
            width=20
        )
        h_scroll.pack(side="bottom", fill="x")

        canvas = tk.Canvas(
            result_window,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        v_scroll.config(command=canvas.yview)
        h_scroll.config(command=canvas.xview)

        main_frame = tk.Frame(canvas)

        canvas_window = canvas.create_window(
            (0, 0),
            window=main_frame,
            anchor="nw"
        )

        # Frame 크기 변경 시 scroll 영역 갱신
        def on_frame_configure(event):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        main_frame.bind(
            "<Configure>",
            on_frame_configure
        )

        nindexs = 7
        ncolumns = 3

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        sht_DiscCurve = AddVariableSheet(left_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = defaultvalues, VariableName = "DiscZeroCurve", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 90, sheet_height = 30, titlelable= True, titleName = "ZeroCurve1", MaxHeight=10)
        sht_DiscCurve.set_all_column_widths(width=50)
        cvnm = make_variable_interface(left_frame, '할인커브명', bold = True, textfont = 11, defaultflag = True, defaultvalue=DiscCurveName[0])

        left_frame2 = tk.Frame(main_frame)
        left_frame2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        sht_RefCurve = AddVariableSheet(left_frame2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = defaultvalues, VariableName = "RefZeroCurve", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 90, sheet_height = 30, titlelable= True, titleName = "ZeroCurve2", MaxHeight=10)
        sht_RefCurve.set_all_column_widths(width=50)
        cvnm2 = make_variable_interface(left_frame2, '할인커브명', bold = True, textfont = 11, defaultflag = True, defaultvalue=EstCurveName[0])

        left_frame3 = tk.Frame(main_frame)
        left_frame3.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        v_Kappa = make_variable_interface(left_frame3, 'kappa', bold = True, textfont = 11, defaultflag = True, titlelable= True, titleName = "HW Pararm", defaultvalue=HWKappaList[0])

        sht_HWVol = AddVariableSheet(left_frame3, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','HWVol'], defaultvalues = defaultvalues2, VariableName = "HWVol", myfont = 10, anchor = 'w', padx = 5, pady = 2, sheet_width = 85, sheet_height = 30, MaxHeight=10)
        sht_HWVol.set_all_column_widths(width=60)
        ResultFrame = tk.Frame(main_frame)
        ResultFrame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        def run_func() : 
            HWV1 = HWV2 = HWV3 = pd.DataFrame([])
            DiscCurve = get_from_sheetinterface(sht_DiscCurve)
            DiscCurve["Term"] = DiscCurve["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            DiscCurve["Rate"] = DiscCurve["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            DiscCurveTerm = list(DiscCurve["Term"].values)
            DiscCurveRate = list(DiscCurve["Rate"].values)
            DiscCurveTermList[0] = DiscCurveTerm
            DiscCurveRateList[0] = list(np.array(DiscCurveRate)/100)
            
            RefCurve = get_from_sheetinterface(sht_RefCurve)
            RefCurve["Term"] = RefCurve["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            RefCurve["Rate"] = RefCurve["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            RefCurveTerm = list(RefCurve["Term"].values)
            RefCurveRate = list(RefCurve["Rate"].values)
            EstCurveTermList[0] = RefCurveTerm
            EstCurveRateList[0] = list(np.array(RefCurveRate)/100)

            Kappa1 = float(v_Kappa.get()) if len(str(v_Kappa.get())) > 0 else 0.01
            cvname1 = str(cvnm.get()) if len(str(cvnm.get())) > 0 else 'KRW IRS'
            cvname2 = str(cvnm2.get()) if len(str(cvnm2.get())) > 0 else 'KRW IRS'

            HWV1 = get_from_sheetinterface(sht_HWVol)
            HWV1["Term"] = HWV1["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            HWV1["HWVol"] = HWV1["HWVol"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            HWVT = list(HWV1["Term"].values)
            HWV = list(HWV1["HWVol"].values.astype(np.float64)/100)
            DiscCurveName[0] = cvname1
            EstCurveName[0] = cvname2
            
            HWVolTermList[0] = HWVT
            HWVolList[0] = HWV
            result_window.destroy()
        tk.Button(left_frame, text = '마켓데이터 적용', padx = 10, pady = 10, font = ("맑은 고딕",12,'bold'), command = run_func, width = 15).pack()

    #left_frame10 = tk.Frame(main_frame)
    #left_frame10.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    #v_Kappa = make_variable_interface(left_frame10, 'kappa', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultData["HWKappa"].iloc[0])
    #HWTerm = list(ResultData["OptMat"].values)
    #HWVol = list(ResultData["HWVol"].values)
    #defaultvalues2 = (HWTerm + ['']* 10, HWVol + ['']* 10)
    #sht_HWVol = AddVariableSheet(left_frame10, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','HWVol'], defaultvalues = defaultvalues2, VariableName = "HWVol", myfont = 10, anchor = 'w', padx = 5, pady = 2, sheet_width = 85, sheet_height = 30, MaxHeight=10)
    #sht_HWVol.set_all_column_widths(width=60)


    left_frame11 = tk.Frame(main_frame)
    left_frame11.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    vb_GreekFlag = make_listvariable_interface(left_frame11, 'Greek 산출여부', ["0: Greek산출안함","1: Greek산출"], bold = True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 1, pady = 2)
    vb_CSRBucket = make_listvariable_interface(left_frame11, 'CSRBucket\n(Callable Bond평가시)', ["1: 정부,중앙은행","2: 지방정부, 공공행정","3: 금융","4: 원자재","5: 소비재","6: 기술통신"], listheight = 4, textfont = 11, pady = 10, defaultflag=True, defaultvalue=0)
    vb_DRCFlag = make_listvariable_interface(left_frame11, 'DRC산출여부', ["0: 산출안함","1: 산출함"], bold = True, listheight = 3, textfont = 11, titlelable=False, titleName = "바스켓CDS여부", defaultflag = True, defaultvalue = 0, pady = 1)
    v_CRRate = make_variable_interface(left_frame11, '신용등급\n(FRTB등급 입력)', bold = False, textfont = 11, defaultflag = True, defaultvalue='AAA')
    vb_TextFlag = make_listvariable_interface(left_frame11, 'LOGGING 산출여부', ["0: Logging안함","1: Logging"], bold = True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0, pady = 2)

    Result_frame = tk.Frame(main_frame)
    Result_frame.pack(side = 'left', padx = 3, pady = 2, anchor = 'n')
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

        CRRate = str(v_CRRate.get()).replace("+","").replace("-","").replace("1","") if len(str(v_CRRate.get())) > 0 else "NR"
        DRCFlag = int(str(vb_DRCFlag.get(vb_DRCFlag.curselection())).split(":")[0]) if vb_DRCFlag.curselection() else 1                
        DRCCRDict = {'AAA' : 0.005, 'AA' : 0.02, 'A' : 0.03,'BBB' : 0.06, 'BB' : 0.15,'B' : 0.30,'CCC' : 0.50,'NR': 0.15} 
        DRCRW = 0 if DRCFlag == 0 else DRCCRDict[CRRate.upper()]
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else today_YYYYMMDD
        NominalFlag = int(str(vb_NAFlag.get(vb_NAFlag.curselection())).split(":")[0]) if vb_NAFlag.curselection() else 0
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        TextFlag = int(str(vb_TextFlag.get(vb_TextFlag.curselection())).split(":")[0]) if vb_TextFlag.curselection() else 0
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        EffectiveDate = int(v_EffectiveDate.get()) if len(str(v_EffectiveDate.get())) > 0 else today_YYYYMMDD
        MaturityDate = int(v_MaturityDate.get()) if len(str(v_MaturityDate.get())) > 0 else today_YYYYMMDD + 50000
        Phase2StartDate = int(v_Phase2StartDate.get()) if len(str(v_Phase2StartDate.get())) > 0 else today_YYYYMMDD + 10000
        Phase2UseFlag = int(str(vb_Phase2UseFlag.get(vb_Phase2UseFlag.curselection())).split(":")[0]) if vb_Phase2UseFlag.curselection() else 0
        NationFlag = int(str(vb_NationFlag.get(vb_NationFlag.curselection())).split(":")[0]) if vb_NationFlag.curselection() else 0

        CSRBucket= int(str(vb_CSRBucket.get(vb_CSRBucket.curselection())).split(":")[0]) if vb_CSRBucket.curselection() else 1
        rw_csr = CSRRW[CSRBucket-1] if NominalFlag < 0 else 0

        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        L1_NumCpnOneYear_P2 = int(vb_L1_NumCpnOneYear_P2.get(vb_L1_NumCpnOneYear_P2.curselection())) if vb_L1_NumCpnOneYear_P2.curselection() else 4
        DayCountLeg1 = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else 0    
        L1_PowerSpreadFlag = 0
        if vb_L1_RefSwapMaturity_T.curselection() :         
            if '-' in str(vb_L1_RefSwapMaturity_T.get(vb_L1_RefSwapMaturity_T.curselection())).split(":")[0] : 
                SplitedStr = str(vb_L1_RefSwapMaturity_T.get(vb_L1_RefSwapMaturity_T.curselection())).split(":")[0].split("-")
                if 'm' in SplitedStr[0].lower() :
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L1_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L1_PowerSpreadFlag = 1
            else : 
                if 'm' in str(vb_L1_RefSwapMaturity_T.get(vb_L1_RefSwapMaturity_T.curselection())).split(":")[0].lower() : 
                    L1_RefSwapMaturity_T = float(str(vb_L1_RefSwapMaturity_T.get(vb_L1_RefSwapMaturity_T.curselection())).split(":")[0].split('m')[0])/12
                elif 'y' in str(vb_L1_RefSwapMaturity_T.get(vb_L1_RefSwapMaturity_T.curselection())).split(":")[0].lower() :
                    L1_RefSwapMaturity_T = float(str(vb_L1_RefSwapMaturity_T.get(vb_L1_RefSwapMaturity_T.curselection())).split(":")[0].split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(str(vb_L1_RefSwapMaturity_T.get(vb_L1_RefSwapMaturity_T.curselection())).split(":")[0]) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25

        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RangeMultiple.get()) if len(str(v_L1_RangeMultiple.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)
        L1_PayoffMultiple_P1 = float(str(v_L1_PayoffMultiple.get(v_L1_PayoffMultiple.curselection())).split("x ")[-1].split("배")[0]) if v_L1_PayoffMultiple.curselection() else 0
        
        L1_RCap = float(v_L1_RCap.get())/100 if len(str(v_L1_RCap.get())) > 0 else 0
        L1_RFloor = float(v_L1_RFloor.get())/100 if len(str(v_L1_RFloor.get())) > 0 else 0

        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" not in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0

        if len(str(v_L1_RangeFixedRate_P1.get())) > 0 : 
            if "%" not in str(v_L1_RangeFixedRate_P1.get()) : 
                L1_RangeFixedRate_P1 = float(v_L1_RangeFixedRate_P1.get())/100
            else : 
                L1_RangeFixedRate_P1 = float(str(v_L1_RangeFixedRate_P1.get()).replace("%",""))/100
        else : 
            L1_RangeFixedRate_P1 = 0

        L1_StructuredFlag_P1 = int(str(vb_L1_StructuredFlag_P1.get(vb_L1_StructuredFlag_P1.curselection())).split(":")[0]) if vb_L1_StructuredFlag_P1.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if len(str(v_L1_FixedCpnRate_P2.get())) > 0 : 
            if "%" not in str(v_L1_FixedCpnRate_P2.get()) : 
                L1_FixedCpnRate_P2 = float(v_L1_FixedCpnRate_P2.get())/100
            else : 
                L1_FixedCpnRate_P2 = float(str(v_L1_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P2 = 0

        if len(str(v_L1_RangeFixedRate_P2.get())) > 0 : 
            if "%" not in str(v_L1_RangeFixedRate_P2.get()) : 
                L1_RangeFixedRate_P2 = float(v_L1_RangeFixedRate_P2.get())/100
            else : 
                L1_RangeFixedRate_P2 = float(str(v_L1_RangeFixedRate_P2.get()).replace("%",""))/100
        else : 
            L1_RangeFixedRate_P2 = 0

        L1_StructuredFlag_P2 = int(str(vb_L1_StructuredFlag_P2.get(vb_L1_StructuredFlag_P2.curselection())).split(":")[0]) if vb_L1_StructuredFlag_P2.curselection() else (0 if L1_NumCpnOneYear_P2 != 0 else 3)

        ##
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        L2_NumCpnOneYear_P2 = int(vb_L2_NumCpnOneYear_P2.get(vb_L2_NumCpnOneYear_P2.curselection())) if vb_L2_NumCpnOneYear_P2.curselection() else 4        
        DayCountLeg2 = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else 0    
        L2_PowerSpreadFlag = 0
        if vb_L2_RefSwapMaturity_T.curselection() :         
            if '-' in str(vb_L2_RefSwapMaturity_T.get(vb_L2_RefSwapMaturity_T.curselection())).split(":")[0] : 
                SplitedStr = str(vb_L2_RefSwapMaturity_T.get(vb_L2_RefSwapMaturity_T.curselection())).split(":")[0].split("-")
                if 'm' in SplitedStr[0].lower() :
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("m")[0])/12
                elif 'y' in SplitedStr[0].lower() : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T = float(SplitedStr[0]) 

                if 'm' in SplitedStr[1].lower() :
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("m")[0])/12
                elif 'y' in SplitedStr[1].lower() : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1].lower().split("y")[0]) 
                else : 
                    L2_RefSwapMaturity_T_PowerSpread = float(SplitedStr[1]) 
                L2_PowerSpreadFlag = 1
            else : 
                if 'm' in str(vb_L2_RefSwapMaturity_T.get(vb_L2_RefSwapMaturity_T.curselection())).split(":")[0].lower() : 
                    L2_RefSwapMaturity_T = float(str(vb_L2_RefSwapMaturity_T.get(vb_L2_RefSwapMaturity_T.curselection())).split(":")[0].split('m')[0])/12
                elif 'y' in str(vb_L2_RefSwapMaturity_T.get(vb_L2_RefSwapMaturity_T.curselection())).split(":")[0].lower() :
                    L2_RefSwapMaturity_T = float(str(vb_L2_RefSwapMaturity_T.get(vb_L2_RefSwapMaturity_T.curselection())).split(":")[0].split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(str(vb_L2_RefSwapMaturity_T.get(vb_L2_RefSwapMaturity_T.curselection())).split(":")[0]) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25

        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4

        L2_RefRateMultiple_P1 = float(v_L2_RangeMultiple.get()) if len(str(v_L2_RangeMultiple.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        L2_PayoffMultiple_P1 = float(str(v_L2_PayoffMultiple.get(v_L2_PayoffMultiple.curselection())).split("x ")[-1].split("배")[0]) if v_L2_PayoffMultiple.curselection() else 0

        L2_RCap = float(v_L2_RCap.get())/100 if len(str(v_L2_RCap.get())) > 0 else 0
        L2_RFloor = float(v_L2_RFloor.get())/100 if len(str(v_L2_RFloor.get())) > 0 else 0

        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" not in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0

        if len(str(v_L2_RangeFixedRate_P1.get())) > 0 : 
            if "%" not in str(v_L2_RangeFixedRate_P1.get()) : 
                L2_RangeFixedRate_P1 = float(v_L2_RangeFixedRate_P1.get())/100
            else : 
                L2_RangeFixedRate_P1 = float(str(v_L2_RangeFixedRate_P1.get()).replace("%",""))/100
        else : 
            L2_RangeFixedRate_P1 = 0

        L2_StructuredFlag_P1 = int(str(vb_L2_StructuredFlag_P1.get(vb_L2_StructuredFlag_P1.curselection())).split(":")[0]) if vb_L2_StructuredFlag_P1.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)

        if len(str(v_L2_FixedCpnRate_P2.get())) > 0 : 
            if "%" not in str(v_L2_FixedCpnRate_P2.get()) : 
                L2_FixedCpnRate_P2 = float(v_L2_FixedCpnRate_P2.get())/100
            else : 
                L2_FixedCpnRate_P2 = float(str(v_L2_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P2 = 0

        if len(str(v_L2_RangeFixedRate_P2.get())) > 0 : 
            if "%" not in str(v_L2_RangeFixedRate_P2.get()) : 
                L2_RangeFixedRate_P2 = float(v_L2_RangeFixedRate_P2.get())/100
            else : 
                L2_RangeFixedRate_P2 = float(str(v_L2_RangeFixedRate_P2.get()).replace("%",""))/100
        else : 
            L2_RangeFixedRate_P2 = 0

        L2_StructuredFlag_P2 = int(str(vb_L2_StructuredFlag_P2.get(vb_L2_StructuredFlag_P2.curselection())).split(":")[0]) if vb_L2_StructuredFlag_P2.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        #Holiday = get_from_sheetinterface(sht_Holiday)
        #Holiday["Holidays"] = Holiday["Holidays"].apply(lambda x : str(x).replace("-",""))
        Holidays = np.array([19000101], dtype = np.int64) #np.array(list(Holiday["Holidays"].values.astype(np.int64)), dtype = np.int64)
        NHolidays = 1#len(Holidays)
        RefRateHistoryData = get_from_sheetinterface(RefRateHistory)
        RefRateHistoryDate_L1 = list(RefRateHistoryData["Date"].apply(lambda x : str(x).replace("-","")).astype(np.int64).values)
        RefRateHistory_L1 = list(RefRateHistoryData["Rate(Leg1)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100)
        RefRateHistoryDate_L2 = list(RefRateHistoryData["Date"].apply(lambda x : str(x).replace("-","")).astype(np.int64).values)
        RefRateHistory_L2 = list(RefRateHistoryData["Rate(Leg2)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100)

        OptionFlag = int(str(vb_OptionFlag.get(vb_OptionFlag.curselection())).split(":")[0]) if vb_OptionFlag.curselection() else 0    
        OptSchd = get_from_sheetinterface(sht_OptScheduleInfo)
        OptSchd["옵션 선언일"] = OptSchd["옵션 선언일"].apply(lambda x : str(x).replace("-","").replace(".0",""))
        OptSchd["옵션행사일"] = OptSchd["옵션행사일"].apply(lambda x : str(x).replace("-","").replace(".0",""))
        OptionStartDate = np.array(list(OptSchd["옵션 선언일"].values.astype(np.int64)), dtype = np.int64)
        OptionPayDate = np.array(list(OptSchd["옵션행사일"].values.astype(np.int64)), dtype = np.int64)

        #DiscLeg = get_from_sheetinterface(sht_DiscCurve)
        #DiscLeg["Term"] = DiscLeg["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        #DiscLeg["Rate"] = DiscLeg["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        ZeroTerm = DiscCurveTermList[0]#list(DiscLeg["Term"].values)
        NZero = len(ZeroTerm)
        ZeroRate = DiscCurveRateList[0]#list(DiscLeg["Rate"].values)
        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
        Kappa = HWKappaList[0]

        #RefCurveLeg = get_from_sheetinterface(sht_RefCurve)
        #RefCurveLeg["Term"] = RefCurveLeg["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        #RefCurveLeg["Rate"] = RefCurveLeg["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        EstZeroTerm = EstCurveTermList[0]#list(RefCurveLeg["Term"].values)
        NEstZero = len(EstZeroTerm)
        EstZeroRate = EstCurveRateList[0]#list(RefCurveLeg["Rate"].values)
        Preprocessing_ZeroTermAndRate(EstZeroTerm, EstZeroRate, PriceDate)

        #HWV = get_from_sheetinterface(sht_HWVol)
        #HWV["Term"] = HWV["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        #HWV["HWVol"] = HWV["HWVol"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        #HWVAvg = HWV["HWVol"].values.mean()
        #NHWVol = len(HWV)
        HWVolTerm = HWVolTermList[0] #HWV["Term"].values.astype(np.float64)
        NHWVol = len(HWVolTerm)
        HWVol1 = list(HWVolList[0])#HWV["HWVol"].values.astype(np.float64)/100
        HWVol2 = list(HWVol2FList[0]) #HWV["HWVol"].values.astype(np.float64) * 0
        HWVol = list(HWVol1) + list(HWVol2)

        NumCpnAnn = np.array([L1_NumCpnOneYear_P1, L2_NumCpnOneYear_P1], dtype = np.int64)
        NumCpnAnnPhase2RcvPay = np.array([L1_NumCpnOneYear_P2, L2_NumCpnOneYear_P2], dtype = np.int64)
        MaxLossRetRcvPay = np.array([100.0,100.0,100.0,100.0], dtype = np.float64)
        MultipleRatefixPayoffRcvPay = np.array([L1_RefRateMultiple_P1, L1_PayoffMultiple_P1, L2_RefRateMultiple_P1, L2_PayoffMultiple_P1], dtype = np.float64)
        DayCountRcvPay = np.array([DayCountLeg1, DayCountLeg2], dtype = np.int64)    
        PowerSpreadFlag = np.array([L1_PowerSpreadFlag, L2_PowerSpreadFlag], dtype = np.int64)
        RangeMaxMinRcvPay = np.array([L1_RCap, L1_RFloor, L2_RCap, L2_RFloor], dtype = np.float64)
        InfoRefRateRcvPay = np.array([L1_RefSwapNCPNOneYear_P1, L1_RefSwapMaturity_T, L1_RefSwapMaturity_T, L1_RefSwapMaturity_T_PowerSpread,
                                    L2_RefSwapNCPNOneYear_P1, L2_RefSwapMaturity_T, L2_RefSwapMaturity_T, L2_RefSwapMaturity_T_PowerSpread], dtype = np.float64)

        PriceDate_c = ct.c_long(PriceDate)
        EffectiveDate_c = ct.c_long(EffectiveDate)
        MaturityDate_c = ct.c_long(MaturityDate)
        NAFlag_c = ct.c_long(NominalFlag)
        NA_c = ct.c_double(Nominal)

        Holidays_np, Holidays_c = arr_long(Holidays)
        NHolidays_c = ct.c_long(NHolidays)
        NationFlag_c = ct.c_long(NationFlag)
        NumCpnAnn_np, NumCpnAnn_c = arr_long(NumCpnAnn)
        MaxLossRetRcvPay_np, MaxLossRetRcvPay = arr_double(MaxLossRetRcvPay)

        MultipleRatefixPayoffRcvPay_np, MultipleRatefixPayoffRcvPay_c = arr_double(MultipleRatefixPayoffRcvPay)
        #print("지금변수",MultipleRatefixPayoffRcvPay_np, RangeMaxMinRcvPay, L2_StructuredFlag_P1, L2_StructuredFlag_P2)
        DayCountRcvPay_np, DayCountRcvPay_c = arr_long(DayCountRcvPay)
        PowerSpreadFlag_np, PowerSpreadFlag_c = arr_long(PowerSpreadFlag)
        RangeMaxMinRcvPay_np, RangeMaxMinRcvPay_c = arr_double(RangeMaxMinRcvPay)
        InfoRefRateRcvPay_np, InfoRefRateRcvPay_c = arr_double(InfoRefRateRcvPay)

        RcvLegFixedRate_c = ct.c_double(L1_FixedCpnRate_P1)
        RcvLegRangeCoupon_c = ct.c_double(L1_RangeFixedRate_P1)
        RcvLegStructuredFlag_c = ct.c_long(L1_StructuredFlag_P1)
        PayLegFixedRate_c = ct.c_double(L2_FixedCpnRate_P1)
        PayLegRangeCoupon_c = ct.c_double(L2_RangeFixedRate_P1)

        PayLegStructuredFlag_c = ct.c_long(L2_StructuredFlag_P1)
        Phase2UseFlag_c = ct.c_long(Phase2UseFlag)
        Phase2Date_c = ct.c_long(Phase2StartDate)
        Phase2RcvLegFixedRate_c = ct.c_double(L1_FixedCpnRate_P2)
        Phase2RcvLegRangeCoupon_c = ct.c_double(L1_RangeFixedRate_P2)

        Phase2RcvLegStructuredFlag_c = ct.c_long(L1_StructuredFlag_P2)
        Phase2PayLegFixedRate_c = ct.c_double(L2_FixedCpnRate_P2)
        Phase2PayLegRangeCoupon_c = ct.c_double(L2_RangeFixedRate_P2)
        Phase2PayLegStructuredFlag_c = ct.c_long(L2_StructuredFlag_P2)
        NumCpnAnnPhase2RcvPay_np, NumCpnAnnPhase2RcvPay_c = arr_long(NumCpnAnnPhase2RcvPay)

        NOption_c = ct.c_long(len(OptionStartDate))
        OptionDate_np, OptionDate_c = arr_long(OptionStartDate)
        OptionPayDate_np, OptionPayDate_c = arr_long(OptionPayDate)
        OptionType_c = ct.c_long(OptionFlag)
        NRcvRateHistory_c = ct.c_long(len(RefRateHistoryDate_L1))

        RcvRateHistoryDate_np, RcvRateHistoryDate_c = arr_long(RefRateHistoryDate_L1)
        RcvRateHistory_np, RcvRateHistory_c = arr_double(RefRateHistory_L1)
        NPayRateHistory_c = ct.c_long(len(RefRateHistoryDate_L2))
        PayRateHistoryDate_np, PayRateHistoryDate_c = arr_long(RefRateHistoryDate_L2)
        PayRateHistory_np, PayRateHistory_c = arr_double(RefRateHistory_L2)

        NZeroRate_c = ct.c_long(NEstZero)
        ZeroTerm_np, ZeroTerm_c = arr_double(EstZeroTerm) 
        ZeroRate_np, ZeroRate_c = arr_double(EstZeroRate)
        NZeroDiscRate_c = ct.c_long(NZero)
        ZeroDiscTerm_np, ZeroDiscTerm_c = arr_double(ZeroTerm)

        ZeroDiscRate_np, ZeroDiscRate_c = arr_double(ZeroRate)
        HW2FFlag_c = ct.c_long(0)
        NHWVol_c = ct.c_long(NHWVol)
        HWVolTerm_np, HWVolTerm_c = arr_double(HWVolTerm)
        HWVol_np, HWVol_c = arr_double(HWVol)

        kappa_np, kappa_c = arr_double(np.array([Kappa, Kappa],dtype =np.float64))
        FactorCorrelation_c = ct.c_double(0.0)
        RangeAccrualFlagRcvPay_np, RangeAccrualFlagRcvPay_c = arr_long(np.array([0, 0],dtype =np.int64))
        InterestRateRoundingRcvPay_np, InterestRateRoundingRcvPay_c = arr_long(np.array([0, 0],dtype =np.int64))
        ResultCpnDateRcv_np, ResultCpnDateRcv_c = arr_long(np.zeros(700, dtype = np.int64))

        ResultCpnDatePay_np, ResultCpnDatePay_c = arr_long(np.zeros(700, dtype = np.int64))
        ResultFixingRateCpn_np, ResultFixingRateCpn_c = arr_double(np.zeros(1000, dtype = np.float64))
        Greek_np, Greek_c = arr_double(np.zeros(2 * (NZero + NEstZero) + NHWVol + 40, dtype = np.float64))
        if CSRBucket > 0 and GreekFlag > 0 : 
            GreekFlag = CSRBucket
        GreekFlag_c = ct.c_long(GreekFlag)
        TextFlag_c = ct.c_long(TextFlag)
        #VariableNames[50:60]
        Res = CalcFunc(PriceDate_c, EffectiveDate_c, MaturityDate_c, NAFlag_c, NA_c,
                    NHolidays_c, Holidays_c, NationFlag_c, NumCpnAnn_c, MaxLossRetRcvPay,
                    MultipleRatefixPayoffRcvPay_c, DayCountRcvPay_c, PowerSpreadFlag_c, RangeMaxMinRcvPay_c, InfoRefRateRcvPay_c, 
                    RcvLegFixedRate_c, RcvLegRangeCoupon_c, RcvLegStructuredFlag_c, PayLegFixedRate_c, PayLegRangeCoupon_c,
                    PayLegStructuredFlag_c, Phase2UseFlag_c, Phase2Date_c, Phase2RcvLegFixedRate_c, Phase2RcvLegRangeCoupon_c,
                    Phase2RcvLegStructuredFlag_c, Phase2PayLegFixedRate_c, Phase2PayLegRangeCoupon_c, Phase2PayLegStructuredFlag_c, NumCpnAnnPhase2RcvPay_c,
                    NOption_c, OptionDate_c, OptionPayDate_c, OptionType_c, NRcvRateHistory_c, 
                    RcvRateHistoryDate_c, RcvRateHistory_c, NPayRateHistory_c, PayRateHistoryDate_c, PayRateHistory_c,
                    NZeroRate_c, ZeroTerm_c, ZeroRate_c, NZeroDiscRate_c, ZeroDiscTerm_c, 
                    ZeroDiscRate_c, HW2FFlag_c, NHWVol_c, HWVolTerm_c, HWVol_c, 
                    kappa_c, FactorCorrelation_c, RangeAccrualFlagRcvPay_c, InterestRateRoundingRcvPay_c, ResultCpnDateRcv_c,
                    ResultCpnDatePay_c, ResultFixingRateCpn_c, Greek_c, GreekFlag_c, TextFlag_c)
        
        TTM = DayCountAtoB(PriceDate, MaturityDate)/365
        v = float(ResultFixingRateCpn_c[0])
        ConditionL1 = '\n\n금리결정조건(Leg1) : \n' + str(np.round(L1_RFloor, 2)) + '<=' + str(np.round(L1_RefRateMultiple_P1,2)) + 'xRate(' + str(np.round(L1_RefSwapMaturity_T, 2)) + ')<=' + str(np.round(L1_RCap, 2))
        PayoffConditionL1P1 = '\n\n페이오프(Leg1, Phase1) : \n' + str(np.round(L1_PayoffMultiple_P1 if L1_StructuredFlag_P1 > 0 else 0,2)) + 'xR(' + str(np.round(L1_RefSwapMaturity_T,2)) + ')+' + str(np.round(L1_RangeFixedRate_P1 * 100,2)) + '%(RangeCpn)+' + str(np.round(L1_FixedCpnRate_P1 * 100,2)) + '%(고정)'
        PayoffConditionL1P2 = ('\n페이오프(Leg1, Phase2) : \n' + str(np.round(L1_PayoffMultiple_P1 if L1_StructuredFlag_P2 > 0 else 0,2)) + 'xR(' + str(np.round(L1_RefSwapMaturity_T,2)) + ')+' + str(np.round(L1_RangeFixedRate_P2 * 100,2)) + '%(RangeCpn)+' + str(np.round(L1_FixedCpnRate_P2 * 100,2)) + '%(고정)') if Phase2UseFlag > 0 else ''

        ConditionL2 = '\n\n금리결정조건(Leg2) : \n' + str(np.round(L2_RFloor, 2)) + '<=' + str(np.round(L2_RefRateMultiple_P1,2)) + 'xRate(' + str(np.round(L2_RefSwapMaturity_T, 2)) + ')<=' + str(np.round(L2_RCap, 2))
        PayoffConditionL2P1 = '\n\n페이오프(Leg2, Phase1) : \n' + str(np.round(L2_PayoffMultiple_P1 if L2_StructuredFlag_P1 > 0 else 0,2)) + 'xR(' + str(np.round(L2_RefSwapMaturity_T,2)) + ')+' + str(np.round(L2_RangeFixedRate_P1 * 100,2)) + '%(RangeCpn)+' + str(np.round(L2_FixedCpnRate_P1 * 100,2)) + '%(고정)'
        PayoffConditionL2P2 = ('\n페이오프(Leg2, Phase2) : \n' + str(np.round(L2_PayoffMultiple_P1 if L2_StructuredFlag_P2 > 0 else 0,2)) + 'xR(' + str(np.round(L2_RefSwapMaturity_T,2)) + ')+' + str(np.round(L2_RangeFixedRate_P2 * 100,2)) + '%(RangeCpn)+' + str(np.round(L2_FixedCpnRate_P2 * 100,2)) + '%(고정)') if Phase2UseFlag > 0 else ''

        Result123_L1 = np.ctypeslib.as_array(ResultCpnDateRcv_c[:700], shape = (700, ))
        Result123_L2 = np.ctypeslib.as_array(ResultCpnDatePay_c[:700], shape = (700, ))
        Greek_PV01Est = np.ctypeslib.as_array(Greek_c[:NEstZero], shape = (NEstZero, ))
        Greek_Gamma01Est = np.ctypeslib.as_array(Greek_c[NEstZero + NZero:2*NEstZero + NZero], shape = (NEstZero, ))
        Greek_PV01Disc = np.ctypeslib.as_array(Greek_c[NEstZero:NEstZero + NZero], shape = (NZero, ))
        Greek_Gamma01Disc = np.ctypeslib.as_array(Greek_c[2 * NEstZero + NZero : 2 * NEstZero + 2 * NZero], shape = (NZero, ))
        nm1 = list([EstCurveName[0]]) * len(ZeroTerm_np)
        nm2 = list([DiscCurveName[0]]) * len(ZeroDiscTerm_np)                
        pv1 = pd.DataFrame([nm1, ZeroTerm_np, Greek_PV01Est, Greek_Gamma01Est], index = ['EstCvName','EstTerm','PV01EstCrv','GammaEstCrv']).T
        pv2 = pd.DataFrame([nm2, ZeroDiscTerm_np, Greek_PV01Disc, Greek_Gamma01Disc], index = ['DiscCvName','DiscTerm','PV01DiscCrv','GammaDiscCrv']).T
        N1 = int(len(Result123_L1[Result123_L1 != 0])/3)
        N2 = int(len(Result123_L2[Result123_L2 != 0])/3)

        FixingDate_L1 = np.ctypeslib.as_array(Result123_L1[Result123_L1 != 0][:N1], shape = (N1, ))
        EndDate_L1 = np.ctypeslib.as_array(Result123_L1[Result123_L1 != 0][N1:2*N1], shape = (N1, ))
        PayDate_L1 = np.ctypeslib.as_array(Result123_L1[Result123_L1 != 0][2*N1:3*N1], shape = (N1, ))
        FixingDate_L2 = np.ctypeslib.as_array(Result123_L2[Result123_L2 != 0][:N2], shape = (N2, ))
        EndDate_L2 = np.ctypeslib.as_array(Result123_L2[Result123_L2 != 0][N2:2*N2], shape = (N2, ))
        PayDate_L2 = np.ctypeslib.as_array(Result123_L2[Result123_L2 != 0][2*N2:3*N2], shape = (N2, ))

        FixingRate_L1 = np.ctypeslib.as_array(ResultFixingRateCpn_c[3:3+N1], shape = (N1, ))
        FixingCoupon_L1 = np.ctypeslib.as_array(ResultFixingRateCpn_c[3+N1:3+2*N1], shape = (N1, ))
        FixingRate_L2 = np.ctypeslib.as_array(ResultFixingRateCpn_c[3+2*N1 : 3+2*N1 + N2], shape = (N2, ))
        FixingCoupon_L2 = np.ctypeslib.as_array(ResultFixingRateCpn_c[3+2*N1 + N2 : 3+2*N1 + 2*N2], shape = (N2, ))

        Res_L1 = pd.DataFrame([FixingDate_L1, EndDate_L1,PayDate_L1,FixingRate_L1,FixingCoupon_L1], index = ['RcvFixingDate','RcvEndDate','RcvPayDate','RcvE[FixingRate]','RcvE[Coupon]']).T
        Res_L2 = pd.DataFrame([FixingDate_L2, EndDate_L2,PayDate_L2,FixingRate_L2,FixingCoupon_L2], index = ['PayFixingDate','PayEndDate','PayPayDate','PayE[FixingRate]','PayE[Coupon]']).T

        HWVega = np.ctypeslib.as_array(Greek_c[2 * NEstZero + 2 * NZero:2 * NEstZero + 2 * NZero + NHWVol], shape = (NHWVol, ))
        RW_GIRR = 0.016/np.sqrt(2)
        Sensi = (pv1['PV01EstCrv'].astype(np.float64).sum() + pv2['PV01DiscCrv'].astype(np.float64).sum())/0.0001
        GIRRRWSensi = Sensi * RW_GIRR
        CSRRWSensi = Sensi * rw_csr if NominalFlag < 0 else 0
        GIRRCvcVu = -(float(Greek_c[NHWVol + 2 * NEstZero + 2 * NZero + 1]) - v - GIRRRWSensi)
        GIRRCvcVd = -(float(Greek_c[NHWVol + 2 * NEstZero + 2 * NZero + 2]) - v + GIRRRWSensi)
        GIRRCVR = max(0,max(GIRRCvcVu,GIRRCvcVd))
        CSRCvcVu = -(float(Greek_c[NHWVol + 2 * NEstZero + 2 * NZero + 3]) - v - CSRRWSensi)
        CSRCvcVd = -(float(Greek_c[NHWVol + 2 * NEstZero + 2 * NZero + 4]) - v + CSRRWSensi)
        CSRCVR = max(0,max(CSRCvcVu,CSRCvcVd)) if NominalFlag < 0 else 0
        GIRRVega = (np.array(HWVega)/0.0001 * HWVol_np[:NHWVol]).sum() * 0.85
        GIRRCVRDF = pd.DataFrame([GIRRCvcVu, GIRRCvcVd], columns = ['GIRRCVR'])
        CSRCVRDF = pd.DataFrame([CSRCvcVu, CSRCvcVd], columns = ['CSRCVR'])
        DRC = np.round(DRCRW * Nominal * 0.75 , 2) if DRCFlag > 0 else 0
                
        RWA = np.round((abs(GIRRRWSensi) + CSRRWSensi + GIRRCVR + GIRRCVR + CSRCVR + GIRRVega + DRC) * 12.5, 2)
        RWA_Pct = np.round(RWA/Nominal, 4)
        output_label.config(text = f"산출결과: {ConditionL1} {PayoffConditionL1P1} {PayoffConditionL1P2} {ConditionL2} {PayoffConditionL2P1} {PayoffConditionL2P2}\n\n가격 : \n{np.round(ResultFixingRateCpn_c[0],2)}\n Leg1 Price : \n{str(np.round(ResultFixingRateCpn_c[1],2))}\n Leg2 Price : \n{np.round(ResultFixingRateCpn_c[2],2)}\nGIRR, CSR 델타 : \n{np.round(abs(GIRRRWSensi),2)},{np.round(abs(CSRRWSensi),2)}\nGIRR, CSR 커버쳐\n{np.round(GIRRCVR, 2)}, {np.round(CSRCVR, 2)}\n GIRR Vega : \n{np.round(GIRRVega, 2)}\n DRC : \n{DRC}\nRWA : \n{RWA}({RWA_Pct* 100})%", font = ("맑은 고딕", 11, 'bold'))

        if len(ResultData) == NHWVol : 
            Tenor1 = list(ResultData["OptMat"].values)
            Tenor2 = list(ResultData["SwapMat"].values)
        else : 
            Tenor1 = HWVolTerm
            Tenor2 = np.maximum(0.25,TTM - np.array(HWVolTerm))
        Res_vega = pd.DataFrame([Tenor1, Tenor2, HWVega], index = ['VolTenor1','VolTenor2','HWVega']).T

        p = pd.DataFrame(np.ctypeslib.as_array(ResultFixingRateCpn_c[:3], shape = (3, )), columns = ['Price'])
        Res = pd.concat([p, Res_L1, Res_L2, pv1, pv2, Res_vega,GIRRCVRDF,CSRCVRDF],axis = 1).applymap(lambda x : '' if 'nan' in str(x).lower() else x)
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(main_frame)
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
        if TextFlag > 0 : 
            Res.to_excel("IRS_Callable_SaveFile.xlsx")
        PrevTreeFlag = insert_dataframe_to_treeview(tree, Res, width = 100)

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2      
        MyArrays[4] = Res_L1
        MyArrays[5] = Res
        #df.to_excel("ResultExcel.xlsx",index = False, header=False)
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    run_button = tk.Button(
        left_frame,
        text="MarketData확인",
        command=lambda: open_result_window(root, DiscCurveTermList, DiscCurveRateList, EstCurveTermList, EstCurveRateList, HWKappaList, HWVolTermList, HWVolList, DiscCurveName, EstCurveName),
        font = ("맑은 고딕",12,'bold')
    )
    run_button.pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop() 
    return MyArrays[5]

def HullWhite12FactorCalibration(DefaultZeroUse = False, 
                                 DefaultZeroTerm = [TimestampToYYYYMMDD(today + pd.DateOffset(months = i)) for i in (np.array([0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0]) * 12).astype(np.int64)], 
                                 DefaultZeroRate = [3.5115,3.5124,3.7926,3.8730,3.9021,3.9204,3.9239,3.9116,3.8993,3.9023,3.9025,3.9081,3.9138,3.9223,3.9337], 
                                 name = 'HW Calibration') : 

    VBAString1F = '''
    Public Declare PtrSafe Function HWCapHWSwaptionCalibrationForKDB Lib "IRPhaseStructuredSwap.dll" ( _
        ByVal NZero As Long, ByRef ZeroTerm As Double, ByRef ZeroRate As Double, ByVal NSwaption As Long, ByRef T_OptMaturity As Double, _
        ByRef Term_SwapMat As Double, ByRef SwaptionVol As Double, ByVal FreqMonthSwaption As Double, ByVal NHW_initial As Long, ByRef HWTerm_initial As Double, _
        ByRef HWVol_initial As Double, ByRef initial_kappa As Double, ByVal FixedKappaFlag As Long, ByVal Fixedkappa As Double, ByVal lognormalvol0normalvol1 As Long, _
        ByRef ResultBlackPrice As Double, ByRef ResultHWPrice As Double, ByRef ResultError As Double _
    ) As Long
    '''

    VBAString2F = '''
    Public Declare PtrSafe Function HJM2FCalibrationForKDB Lib "IRPhaseStructuredSwap.dll" ( _
        ByVal NZero As Long, ByRef ZeroTerm As Double, ByRef ZeroRate As Double, ByVal NSwaption As Long, ByRef T_OptMaturity As Double, _
        ByRef Term_SwapMat As Double, ByRef SwaptionVol As Double, ByVal FreqMonthSwaption As Double, ByRef HWVol_initial As Double, ByRef HWVol_initial2 As Double, _
        ByRef initial_kappa As Double, ByRef initial_kappa2 As Double, ByRef rho As Double, ByVal lognormalvol0normalvol1 As Long, ByRef ResultBlackPrice As Double, _
        ByRef ResultHWPrice As Double, ByRef ResultError As Double _
    ) As Long
    '''

    CalcFunc1F, VariablesFormat1F, VariableNames1F = ConvertPythonFormatfromVBAformat(VBAString1F)
    CalcFunc2F, VariablesFormat2F, VariableNames2F = ConvertPythonFormatfromVBAformat(VBAString2F)

    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings(name)
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = today_YYYYMMDD)
    vb_OneFactorFlag = make_listvariable_interface(left_frame, '1F/2F', ["0 : 1F 추정","1 : 2F 추정"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)
    vb_FixedKappaFlag = make_listvariable_interface(left_frame, 'FixedKappa Flag', ["0 : kappa 추정","1 : kappa 고정"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=1, bold = True)
    v_FixedKappa = make_variable_interface(left_frame, 'FixedKappa', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 0.01)
    NMonths = (np.array([0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0]) * 12).astype(np.int64)
    if DefaultZeroUse == False : 
        DefaultTerm = [TimestampToYYYYMMDD(today + pd.DateOffset(months = i)) for i in NMonths ]
        defaultvalues = (DefaultTerm + ['']* 10, [3.5115,3.5124,3.7926,3.8730,3.9021,3.9204,3.9239,3.9116,3.8993,3.9023,3.9025,3.9081,3.9138,3.9223,3.9337]+ ['']* 10)
    else : 
        DefaultTerm = DefaultZeroTerm
        defaultvalues = (list(DefaultTerm) + ['']* 10, list(DefaultZeroRate)+ ['']* 10)

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
    initvalues = ([0.25, 0.50, 0.75, 1.0, 2.0, 3.0, 5.0] + [""] * 10, [0.9,0.9,0.9,0.9,0.9,0.9,0.9] + [""] * 10)

    sht_HW_InitialVol = AddVariableSheet(right_frame, nindexs = len(initvalues[0]), ncolumns= len(initvalues),targetcolumns = targetcolumns3, defaultvalues = initvalues, VariableName = "initial HWVol", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 120, sheet_height = 30, MaxHeight=18)
    sht_HW_InitialVol.set_all_column_widths(width=98)
    right_frame2 = tk.Frame(main_frame)
    right_frame2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_initkappa2F = make_variable_interface(right_frame2, 'InitialKappa2F', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 0.01, titlelable= True, titleName= "HW Initial Param")
    v_rho12F = make_variable_interface(right_frame2, 'Corr12F', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = -0.30, titlelable= True, titleName= "HW Factor Corr")

    Result_frame = tk.Frame(main_frame)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    ResultValue = []
    ResultValue2 = pd.DataFrame(defaultvalues2, index = ['OptMat','SwapMat','SwaptionVol%']).T.applymap(lambda x : np.nan if str(x) == '' else x).dropna()
    ResultValue2['HWVol'] = ResultValue2['SwaptionVol%'].astype(np.float64)/100
    ResultValue2['HWKappa'] = 0.01
    ResultValue2['HWKappa2F'] = 0.00001
    ResultValue2['HWVol2F'] = 0.0000
    ResultValue2['Rho'] = 0.
    ResultValue2['PriceDate'] = today_YYYYMMDD

    DefaultZeroDF = pd.DataFrame(defaultvalues, index = ['ZeroTerm','ZeroRate']).T.applymap(lambda x : np.nan if str(x) == '' else x).dropna()
    ZeroTermList, ZeroRateList = list(DefaultZeroDF["ZeroTerm"].values), list(DefaultZeroDF["ZeroRate"].values)
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultValue, ResultValue2,ZeroTermList, ZeroRateList]
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
        OneFactorFlag = int(str(vb_OneFactorFlag.get(vb_OneFactorFlag.curselection())).split(":")[0]) if vb_OneFactorFlag.curselection() else 0
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
        initial_kappa2F = np.array([float(v_initkappa2F.get()) if len(str(v_initkappa2F.get())) > 0 else 0.01], dtype = np.float64)
        rho12F = np.array([float(v_rho12F.get())]) if len(str(v_rho12F.get())) > 0 else np.array([-0.1])

        HW_InitialVol = get_from_sheetinterface(sht_HW_InitialVol)
        HW_InitialVol["Term"] = HW_InitialVol["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        HW_InitialVol["initvol(%)"] = HW_InitialVol["initvol(%)"].apply(lambda x : str(x).replace("-","")).astype(np.float64)

        HWTerm_initial = HW_InitialVol['Term'].values.astype(np.float64)
        Preprocessing_Term(HWTerm_initial, PriceDate)
        HWVol_initial = HW_InitialVol['initvol(%)'].values.astype(np.float64) if HW_InitialVol['initvol(%)'].values.astype(np.float64).max() < 0.25 else HW_InitialVol['initvol(%)'].values.astype(np.float64)/100
        NHW_initial = len(HWTerm_initial)
        HWVol_initial2F = np.array([0.0], dtype = np.float64)
        print(HWTerm_initial)
        print('초기볼1',HWVol_initial)
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
        OneFactorFlag_c = ct.c_long(OneFactorFlag)

        HWVol_initial_np, HWVol_initial_c = arr_double(HWVol_initial)
        HWVol_initial2F_np, HWVol_initial2F_c = arr_double(HWVol_initial2F)
        initial_kappa_np, initial_kappa_c = arr_double(initial_kappa)
        initial_kappa2F_np, initial_kappa2F_c = arr_double(initial_kappa2F)
        FixedKappaFlag_c = ct.c_long(FixedKappaFlag)
        FixedKappa_c = ct.c_double(FixedKappa)
        lognormalvol0normalvol1_c = ct.c_long(lognormalvol0normalvol1)
        rho12F_np, rho12F_c = arr_double(rho12F)
        ResultBlackPrice_np, ResultBlackPrice_c = arr_double(ResultBlackPrice)
        ResultHWPrice_np, ResultHWPrice_c = arr_double(ResultHWPrice)
        ResultError_np, ResultError_c = arr_double(ResultError)
        print("변수print")
        print(NZero, ZeroTerm_np, ZeroRate_np)
        print(NSwaption, T_OptMaturity_np, Term_SwapMat_np, SwaptionVol_np)    
        print(FreqMonthSwaption, NHW_initial, HWTerm_initial, HWVol_initial)    
        print(initial_kappa_np, FixedKappaFlag, FixedKappa, lognormalvol0normalvol1)    
        if OneFactorFlag == 0 :         
            ret = CalcFunc1F(NZero_c, ZeroTerm_c, ZeroRate_c, NSwaption_c,T_OptMaturity_c,
                            Term_SwapMat_c, SwaptionVol_c, FreqMonthSwaption_c, NHW_initial_c, HWTerm_initial_c,
                            HWVol_initial_c, initial_kappa_c, FixedKappaFlag_c, FixedKappa_c, lognormalvol0normalvol1_c,
                            ResultBlackPrice_c, ResultHWPrice_c, ResultError_c)    
        else : 
            ret = CalcFunc1F(NZero_c, ZeroTerm_c, ZeroRate_c, NSwaption_c,T_OptMaturity_c,
                            Term_SwapMat_c, SwaptionVol_c, FreqMonthSwaption_c, NHW_initial_c, HWTerm_initial_c,
                            HWVol_initial_c, initial_kappa_c, ct.c_long(0), FixedKappa_c, lognormalvol0normalvol1_c,
                            ResultBlackPrice_c, ResultHWPrice_c, ResultError_c)    
            print("2Factor")
            ret = CalcFunc2F(NZero_c, ZeroTerm_c, ZeroRate_c, NSwaption_c,T_OptMaturity_c,
                             Term_SwapMat_c, SwaptionVol_c, FreqMonthSwaption_c, HWVol_initial_c, HWVol_initial2F_c,
                             initial_kappa_c, initial_kappa2F_c, rho12F_c, lognormalvol0normalvol1_c, ResultBlackPrice_c, 
                             ResultHWPrice_c, ResultError_c)
        
        ResultBlack = np.ctypeslib.as_array(ResultBlackPrice_c[:NSwaption], shape = (NSwaption, ))
        ResultHW = np.ctypeslib.as_array(ResultHWPrice_c[:NSwaption], shape = (NSwaption, ))
        ResultError = np.ctypeslib.as_array(ResultError_c[:NSwaption], shape = (NSwaption, ))
        if OneFactorFlag == 0 : 
            ResultHWVol = np.ctypeslib.as_array(HWVol_initial_c[:NSwaption], shape = (NSwaption, ))
            ResultFrame = Swptn
            ResultFrame["BlackPrice"] = ResultBlack
            ResultFrame["HWPrice"] = ResultHW
            ResultFrame["Error"] = ResultError
            ResultFrame["HWVol"] = ResultHWVol
            ResultFrame["HWKappa"] = initial_kappa_c[0]
            ResultFrame["HWKappa2F"] = 0.00001
            ResultFrame["HWVol2F"] = 0.0
            ResultFrame["Rho"] = 0.
        else : 

            ResultHWVol = np.ones(NSwaption, dtype =np.float64) * HWVol_initial_c[0] 
            ResultHWVol2F = np.ones(NSwaption, dtype =np.float64) * HWVol_initial2F_c[0] 
            ResultFrame = Swptn
            ResultFrame["BlackPrice"] = ResultBlack
            ResultFrame["HWPrice"] = ResultHW
            ResultFrame["Error"] = ResultError
            ResultFrame["HWVol"] = ResultHWVol
            ResultFrame["HWVol2F"] = ResultHWVol2F
            ResultFrame["HWKappa"] = initial_kappa_c[0]
            ResultFrame["HWKappa2F"] = initial_kappa2F_c[0]
            ResultFrame["Rho"] = rho12F_c[0]
            ResultFrame["반복수"] = ret
        ResultFrame["PriceDate"] = PriceDate

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

def HazardCali(
    DefaultZeroTerm = [TimestampToYYYYMMDD(today + pd.DateOffset(months = i)) for i in (np.array([0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0]) * 12).astype(np.int64)], 
    DefaultZeroRate = [3.5115,3.5124,3.7926,3.8730,3.9021,3.9204,3.9239,3.9116,3.8993,3.9023,3.9025,3.9081,3.9138,3.9223,3.9337],
    DefaultCDSTerm = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0],
    DefaultCDSRate = [0.30,0.71,1.18,1.31,1.38,1.48,1.58,1.70],
    name = 'HazardRate Calibration'        
) : 
    nindexs = 7
    ncolumns = 3
    VBAString2 = f'''
    Public Declare PtrSafe Function Calc_Hazard_Rate_From_CDSCurve Lib "CreditDerivatives.dll" ( _
        ByVal PricingDateYYYYMMDD As Long, _
        ByVal NPremiumCurve As Long, ByRef PremiumCurveTerm As Double, ByRef PremiumCurve As Double, _
        ByVal NProtectionCurve As Long, ByRef ProtectionCurveTerm As Double, ByRef ProtectionCurve As Double, _
        ByVal NCDSCurve As Long, ByRef CDSCurveTerm As Double, ByRef CDSCurve As Double, _
        ByVal Recovery As Double, ByVal HazardRateCalcFlag As Long, ByVal NCPN_Ann As Long, _
        ByVal NHoliday As Long, ByRef HolidayYYYYMMDD As Long, ByRef ResultHazardTerm As Double, ByRef ResultHazard As Double _
    ) As Long
    '''
    CalcHazardFunc, VariablesHazardFormat, VariableHazardNames = ConvertPythonFormatfromVBAformat(VBAString2)
    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings(name)
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_DiscCurve1 = AddVariableSheet(left_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (DefaultZeroTerm + ['']* 10, DefaultZeroRate + ['']* 10), VariableName = "Protection Buyer\n Curve", myfont = 12, anchor = 'w', padx = 5, pady = 1, sheet_width = 80, sheet_height = 30, titlelable= False, titleName = "\n커브1", MaxHeight=10)
    sht_DiscCurve1.set_all_column_widths(width=50)

    left_frame2 = tk.Frame(main_frame)
    left_frame2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_DiscCurve2 = AddVariableSheet(left_frame2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (DefaultZeroTerm + ['']* 10, DefaultZeroRate + ['']* 10), VariableName = "Protection Seller\n Curve", myfont = 12, anchor = 'w', padx = 5, pady = 1, sheet_width = 80, sheet_height = 30, titlelable= False, titleName = "\n커브1", MaxHeight=10)
    sht_DiscCurve2.set_all_column_widths(width=50)

    left_frame3 = tk.Frame(main_frame)
    left_frame3.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_CDSCurve = AddVariableSheet(left_frame3, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (DefaultCDSTerm + ['']* 10, DefaultCDSRate + ['']* 10), VariableName = "CDS Rate(%) \n Curve", myfont = 12, anchor = 'w', padx = 5, pady = 1, sheet_width = 80, sheet_height = 30, titlelable= False, titleName = "\n커브1", MaxHeight=10)
    sht_CDSCurve.set_all_column_widths(width=50)

    left_frame6 = tk.Frame(main_frame)
    left_frame6.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_Holiday = AddVariableSheet(left_frame6, nindexs = 1000, ncolumns= 1,targetcolumns = ["Holidays"], defaultvalues = ([19000101],), VariableName = "Leg1 Holidays", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 150, sheet_height = 300, MaxHeight=20)
    sht_Holiday.set_all_column_widths(width=80)

    ResultFrame = tk.Frame(main_frame)
    ResultFrame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(ResultFrame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=today_YYYYMMDD)
    v_Recovery = make_variable_interface(ResultFrame, 'CDS Recovery', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 0.4, titlelable= True, titleName= "CDS Params")
    vb_NCPN_Ann = make_listvariable_interface(ResultFrame, '연쿠폰지급수', ["0 : 2","1 : 4"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)

    vb_Calc = make_listvariable_interface(ResultFrame, '계산', ["0 : 엄밀히Calib","1 : S/(1-R)KIS식계산"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, bold = True)
    DebugFlag_c = ct.c_long(0)
    HazardRateCalcFlag_c = ct.c_long(0)
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    ResultV = pd.DataFrame(np.array(DefaultCDSRate)/(0.6*100), index = DefaultCDSTerm).reset_index().rename(columns = {'index' : 'Term',0:'HazardRate'})
    ResultV2 = pd.DataFrame([DefaultCDSTerm, DefaultCDSRate], index = ['CDSTerm','CDSRate']).T
    ResultValue = pd.concat([ResultV, ResultV2],axis = 1)
    ResultZeroTerm1 = ResultZeroTerm2 = DefaultZeroTerm
    ResultZeroRate1 = ResultZeroRate2 = DefaultZeroRate
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultValue, ResultZeroTerm1, ResultZeroRate1, ResultZeroTerm2, ResultZeroRate2]
    exitgui = lambda : root.destroy()
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        ResultValue = MyArrays[4]
        ResultZeroTerm1 = MyArrays[5]
        ResultZeroRate1 = MyArrays[6]
        ResultZeroTerm2 = MyArrays[7]
        ResultZeroRate2 = MyArrays[8]
        DiscLeg1 = get_from_sheetinterface(sht_DiscCurve1)
        DiscLeg1["Term"] = DiscLeg1["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        DiscLeg1["Rate"] = DiscLeg1["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)/100
        ZeroTerm1 = list(DiscLeg1["Term"].values)
        NZero1 = len(ZeroTerm1)
        ZeroRate1 = list(DiscLeg1["Rate"].values)

        DiscLeg2 = get_from_sheetinterface(sht_DiscCurve2)
        DiscLeg2["Term"] = DiscLeg2["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        DiscLeg2["Rate"] = DiscLeg2["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)/100
        ZeroTerm2 = list(DiscLeg2["Term"].values)
        NZero2 = len(ZeroTerm2)
        ZeroRate2 = list(DiscLeg2["Rate"].values)

        CDSCv = get_from_sheetinterface(sht_CDSCurve)
        CDSCv["Term"] = CDSCv["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        CDSCv["Rate"] = CDSCv["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)/100
        CDSCvTerm = list(CDSCv["Term"].values)
        NCDSCv = len(CDSCv)
        CDSCvRate = list(CDSCv["Rate"].values)
        ResultV2 = pd.DataFrame([CDSCvTerm, CDSCvRate], index = ['CDSTerm','CDSRate']).T
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else today_YYYYMMDD
        NCPN_Ann = int(str(vb_NCPN_Ann.get(vb_NCPN_Ann.curselection())).split(":")[1]) if vb_NCPN_Ann.curselection() else 2        
        Recovery = float(v_Recovery.get()) if len(str(v_Recovery.get())) > 0 else 0.4
        Preprocessing_Term(ZeroTerm1, PriceDate)
        Preprocessing_Term(ZeroTerm2, PriceDate)
        Preprocessing_Term(CDSCvTerm, PriceDate)
        ResultZeroTerm1 = ZeroTerm1
        ResultZeroRate1 = ZeroRate1
        ResultZeroTerm2 = ZeroTerm2
        ResultZeroRate2 = ZeroRate2

        CalcFlag = int(str(vb_Calc.get(vb_Calc.curselection())).split(":")[0]) if vb_Calc.curselection() else 0        
        LegHoliday = get_from_sheetinterface(sht_Holiday)
        Holidays = np.array(list(LegHoliday["Holidays"].values.astype(np.int64)), dtype = np.int64)
        NHolidays = len(Holidays)
        NHolidays_c = ct.c_long(NHolidays)
        Holidays_np, Holidays_c = arr_long(Holidays)
        Recovery_c = ct.c_double(Recovery)
        NCPN_Ann_c = ct.c_long(NCPN_Ann)
        PricingDateYYYYMMDD = ct.c_long(PriceDate)
        NZero1_c = ct.c_long(NZero1)
        ZeroTerm1_np, ZeroTerm1_c = arr_double(ZeroTerm1)                        
        ZeroRate1_np, ZeroRate1_c = arr_double(ZeroRate1)                        
        NZero2_c = ct.c_long(NZero2)
        ZeroTerm2_np, ZeroTerm2_c = arr_double(ZeroTerm2)                        
        ZeroRate2_np, ZeroRate2_c = arr_double(ZeroRate2)                        
        NCDS_c = ct.c_long(NCDSCv)
        CDSTerm_np, CDSTerm_c = arr_double(CDSCvTerm)                        
        CDSRate_np, CDSRate_c = arr_double(CDSCvRate)                        
        ResultHazardTerm = np.zeros(len(CDSCvTerm) * 4, dtype = np.float64)
        ResultHazard = np.zeros(len(CDSCvTerm) * 4, dtype = np.float64)
        ResultHazardTerm_np, ResultHazardTerm_c = arr_double(ResultHazardTerm)                        
        ResultHazard_np, ResultHazard_c = arr_double(ResultHazard)  
        if CalcFlag == 0 :                       
            ret = CalcHazardFunc(PriceDate, 
                                NZero1_c, ZeroTerm1_c, ZeroRate1_c,
                                NZero2_c, ZeroTerm2_c, ZeroRate2_c,
                                NCDS_c, CDSTerm_c, CDSRate_c,
                                Recovery_c, HazardRateCalcFlag_c, NCPN_Ann_c,
                                NHolidays_c, Holidays_c, ResultHazardTerm_c,ResultHazard_c)

            ResultT = np.ctypeslib.as_array(ResultHazardTerm_c[:NCDSCv], shape = (NCDSCv, ))
            ResultH = np.ctypeslib.as_array(ResultHazard_c[:NCDSCv], shape = (NCDSCv, ))
        else : 
            ret = 0
            ResultT = CDSTerm_np
            ResultH = CDSRate_np/(1-Recovery)            
        ResultValue = pd.DataFrame(ResultT, columns = ['Term'])
        ResultValue['HazardRate'] = ResultH
        ResultValue = pd.concat([ResultValue, ResultV2],axis = 1)         
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(main_frame)
            tk.Button(ResultFrame, text = 'Cali완료\nPricing실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = exitgui, width = 15).pack()

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

        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultValue.reset_index(), width = 100)

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2      
        MyArrays[4] = ResultValue
        MyArrays[5] = ResultZeroTerm1 
        MyArrays[6] = ResultZeroRate1 
        MyArrays[7] = ResultZeroTerm2 
        MyArrays[8] = ResultZeroRate2 
    temp_func = lambda : run_function(MyArrays)
    tk.Button(ResultFrame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(ResultFrame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)   
    Zero1 = pd.DataFrame([MyArrays[5], MyArrays[6]], index = ['Term','Rate']).T
    Zero2 = pd.DataFrame([MyArrays[7], MyArrays[8]], index = ['Term','Rate']).T         
    root.mainloop()   
    return Zero1, Zero2, MyArrays[4]

def CalcCDS(name = 'CDS Pricing') : 
    #DefaultZeroTerm = [TimestampToYYYYMMDD(today + pd.DateOffset(months = i)) for i in (np.array([0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0]) * 12).astype(np.int64)] 
    #DefaultZeroRate = [3.5115,3.5124,3.7926,3.8730,3.9021,3.9204,3.9239,3.9116,3.8993,3.9023,3.9025,3.9081,3.9138,3.9223,3.9337]
    TempSchedule =[TimestampToYYYYMMDD(i) for i in MakeSchedule(today_YYYYMMDD - 10000, today_YYYYMMDD + 100000, 3)]
    StartSchedule = TempSchedule[:-1]
    EndSchedule = TempSchedule[1:]
    Zero1, Zero2, HazardDF = HazardCali(
        DefaultZeroTerm = [TimestampToYYYYMMDD(today + pd.DateOffset(months = i)) for i in (np.array([0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0]) * 12).astype(np.int64)], 
        DefaultZeroRate = [3.5115,3.5124,3.7926,3.8730,3.9021,3.9204,3.9239,3.9116,3.8993,3.9023,3.9025,3.9081,3.9138,3.9223,3.9337],
        DefaultCDSTerm = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0],
        DefaultCDSRate = [0.30,0.71,1.18,1.31,1.38,1.48,1.58,1.70],
        name = 'HazardRate Calibration'        
    )
    DefaultZeroTerm1 = list(Zero1['Term'].values)
    DefaultZeroRate1 = list(Zero1['Rate'].values)
    DefaultZeroTerm2 = list(Zero2['Term'].values)
    DefaultZeroRate2 = list(Zero2['Rate'].values)
    HazardTerm = list(HazardDF['Term'].values)
    HazardRate = list(HazardDF["HazardRate"].values * 100)
    VBAString = f'''
    Public Declare PtrSafe Function Calc_OLD_CDS_Value Lib "CreditDerivatives.dll" ( _
        ByVal NPremiumCurve As Long, ByRef PremiumCurveTerm As Double, ByRef PremiumCurve As Double, _
        ByVal NProtectionCurve As Long, ByRef ProtectionCurveTerm As Double, ByRef ProtectionCurve As Double, _
        ByVal DataFlag As Long, ByVal NHazardRate As Long, ByRef HazardRateTerm As Double, ByRef HazardRate As Double, ByVal CalcQMethod As Long, _
        ByVal NRefZero As Long, ByRef RefZeroTerm As Double, ByRef ZeroRiskFree As Double, ByRef ZeroRiskyBond As Double, ByVal DefaultRateCalcMethod As Long, _
        ByVal Recovery As Double, ByVal ScheduleInputFlag As Long, ByVal NCPN_Ann As Long, ByVal Maturity As Double, ByVal NSchedule As Long, ByRef ResetDateYYYYMMDD As Long, ByRef PayDateYYYYMMDD As Long, ByVal PricingDateYYYYMMDD As Long, _
        ByVal NHoliday As Long, ByRef HolidayYYYYMMDD As Long, ByVal BasketCDSFlag As Long, ByVal BasketNTotalAsset As Long, ByVal BasketNthDefault As Long, _
        ByVal BasketAssetCorrelation As Double, ByVal OLS_CDS_Spread As Double, ByVal Protection_Position As Long, ByVal TextFlag As Long, ByVal GreekFlag As Long, ByRef Result_Value As Double, ByRef ResultHazardRate As Double, ByRef ResultGreeks As Double, ByRef Premium_Schedule As Double, ByVal NotionalAmount As Double _
    ) As Long
    '''
    CalcCDSFunc, VariablesCDSFormat, VariableCDSNames = ConvertPythonFormatfromVBAformat(VBAString)
    DataFlag_c = ct.c_long(0)
    CalcQMethod_c = ct.c_long(0)
    ScheduleInputFlag_c = ct.c_long(1)
    DefaultRateCalcMethod_c = ct.c_long(1)
    NCPN_Ann = 4
    NCPN_Ann_c = ct.c_long(NCPN_Ann)

    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings(name)
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    ZeroTermList = [DefaultZeroTerm1, DefaultZeroTerm2]
    ZeroRateList = [DefaultZeroRate1, DefaultZeroRate2]
    HazardTermList = [HazardTerm]
    HazardRateList = [HazardRate]

    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=today_YYYYMMDD)
    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_Recovery = make_variable_interface(left_frame, 'Recovery', bold = True, textfont = 11, defaultflag = True, defaultvalue=0.4)
    vb_LongShort = make_listvariable_interface(left_frame, '매수매도', ["0: 보장매수","1: 보장매도"], bold = True, listheight = 3, textfont = 11, titlelable=True, titleName = "바스켓CDS여부", defaultflag = True, defaultvalue = 0, pady = 1)
    v_CDSPremium = make_variable_interface(left_frame, 'CDS 프리미엄(%)', bold = True, textfont = 11, defaultflag = True, defaultvalue=1.5)
    vb_CSRBucket = make_listvariable_interface(left_frame, 'CSRBucket', ["1: 정부,중앙은행","2: 지방정부, 공공행정","3: 금융","4: 원자재","5: 소비재","6: 기술통신"], listheight = 4, textfont = 11, pady = 10, defaultflag=True, defaultvalue=0)
    v_CRRate = make_variable_interface(left_frame, '신용등급\n(FRTB등급 입력)', bold = False, textfont = 11, defaultflag = True, defaultvalue='AAA')

    left_frame2 = tk.Frame(main_frame)
    left_frame2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    sht_ScheduleInfo = AddVariableSheet(left_frame2, nindexs = 10, ncolumns= 3,targetcolumns = ["Reset Start","지급일"], defaultvalues = (StartSchedule + ['']* 50, EndSchedule+ ['']* 50), VariableName = "CDS 스케줄", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 115, sheet_height = 40, MaxHeight=20, headerfont= 9)
    sht_ScheduleInfo.set_all_column_widths(width=80) 

    def open_market_window(root,ZeroTermList,ZeroRateList,HazardTermList,HazardRateList):
        # 새로운 결과창
        result_window = tk.Toplevel(root)
        result_window.title("MarketData")
        result_window.geometry("1020x500+5+5")
        result_window.resizable(False, False)

        # ==========================================
        # Scrollbar
        # ==========================================

        v_scroll = tk.Scrollbar(
            result_window,
            orient="vertical",
            width=20
        )
        v_scroll.pack(side="right", fill="y")

        h_scroll = tk.Scrollbar(
            result_window,
            orient="horizontal",
            width=20
        )
        h_scroll.pack(side="bottom", fill="x")

        canvas = tk.Canvas(
            result_window,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        v_scroll.config(command=canvas.yview)
        h_scroll.config(command=canvas.xview)

        main_frame = tk.Frame(canvas)

        canvas_window = canvas.create_window(
            (0, 0),
            window=main_frame,
            anchor="nw"
        )

        # Frame 크기 변경 시 scroll 영역 갱신
        def on_frame_configure(event):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        main_frame.bind(
            "<Configure>",
            on_frame_configure
        )

        nindexs = 7
        ncolumns = 3

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        sht_DiscCurve1 = AddVariableSheet(left_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (DefaultZeroTerm1 + ['']* 10, DefaultZeroRate1 + ['']* 10), VariableName = "Protection Buyer\n Curve", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, titlelable= False, titleName = "MarketData1", MaxHeight=10)
        sht_DiscCurve1.set_all_column_widths(width=50)

        left_frame2 = tk.Frame(main_frame)
        left_frame2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        sht_DiscCurve2 = AddVariableSheet(left_frame2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (DefaultZeroTerm2 + ['']* 10, DefaultZeroRate2 + ['']* 10), VariableName = "Protection Seller\n Curve", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, titlelable= False, titleName = "MarketData1", MaxHeight=10)
        sht_DiscCurve2.set_all_column_widths(width=50)

        left_frame3 = tk.Frame(main_frame)
        left_frame3.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        sht_HazardCurve = AddVariableSheet(left_frame3, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','HazardRate'], defaultvalues = (HazardTerm + ['']* 10, HazardRate + ['']* 10), VariableName = "Protection Seller\n Curve", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, titlelable= False, titleName = "MarketData1", MaxHeight=10)
        sht_HazardCurve.set_all_column_widths(width=50)

        ResultFrame = tk.Frame(main_frame)
        ResultFrame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        def run_func() : 
            DiscCurve1 = get_from_sheetinterface(sht_DiscCurve1)
            DiscCurve1["Term"] = DiscCurve1["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            DiscCurve1["Rate"] = DiscCurve1["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            ZeroTerm1 = list(DiscCurve1["Term"].values)
            ZeroRate1 = list(DiscCurve1["Rate"].values)
            ZeroTermList[0] = ZeroTerm1
            ZeroRateList[0] = ZeroRate1            

            DiscCurve2 = get_from_sheetinterface(sht_DiscCurve2)
            DiscCurve2["Term"] = DiscCurve2["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            DiscCurve2["Rate"] = DiscCurve2["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            ZeroTerm2 = list(DiscCurve2["Term"].values)
            ZeroRate2 = list(DiscCurve2["Rate"].values)
            ZeroTermList[1] = ZeroTerm2
            ZeroRateList[1] = ZeroRate2            

            HazardCurve = get_from_sheetinterface(sht_HazardCurve)
            HazardCurve["Term"] = HazardCurve["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            HazardCurve["HazardRate"] = HazardCurve["HazardRate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            HazardTermList[0] = list(HazardCurve["Term"].values)
            HazardRateList[0] = list(HazardCurve["HazardRate"].values)

            result_window.destroy()
        tk.Button(ResultFrame, text = '마켓데이터 적용', padx = 10, pady = 10, font = ("맑은 고딕",12,'bold'), command = run_func, width = 15).pack()

    BasketCDSInput = [0, 100, 1, 0.15]
    def open_basketcds_window(root,BasketCDSInput):
        # 새로운 결과창
        result_window = tk.Toplevel(root)
        result_window.title("MarketData")
        result_window.geometry("1020x500+5+5")
        result_window.resizable(False, False)

        # ==========================================
        # Scrollbar
        # ==========================================

        v_scroll = tk.Scrollbar(
            result_window,
            orient="vertical",
            width=20
        )
        v_scroll.pack(side="right", fill="y")

        h_scroll = tk.Scrollbar(
            result_window,
            orient="horizontal",
            width=20
        )
        h_scroll.pack(side="bottom", fill="x")

        canvas = tk.Canvas(
            result_window,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        v_scroll.config(command=canvas.yview)
        h_scroll.config(command=canvas.xview)

        main_frame = tk.Frame(canvas)

        canvas_window = canvas.create_window(
            (0, 0),
            window=main_frame,
            anchor="nw"
        )

        # Frame 크기 변경 시 scroll 영역 갱신
        def on_frame_configure(event):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        main_frame.bind(
            "<Configure>",
            on_frame_configure
        )

        nindexs = 7
        ncolumns = 3

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        vb_BasketCDSFlag = make_listvariable_interface(left_frame, '바스켓CDSFlag', ["0: 바스켓CDS 적용안함","1: 바스켓CDS 적용함"], bold = True, listheight = 3, textfont = 11, titlelable=True, titleName = "바스켓CDS여부", defaultflag = True, defaultvalue = 0, pady = 1)
        vb_NAsset = make_listvariable_interface(left_frame, '바스켓 기초자산개수', [str(i) + ' : ' + str(i) for i in np.arange(1,1001)], bold = True, listheight = 3, textfont = 11, titlelable=False, titleName = "바스켓CDS여부", defaultflag = True, defaultvalue = 0, pady = 1)
        vb_NthDefault = make_listvariable_interface(left_frame, 'Nth 디폴트순위', [str(i) + ' : ' + str(i) for i in np.arange(1,1001)], bold = True, listheight = 3, textfont = 11, titlelable=False, titleName = "바스켓CDS여부", defaultflag = True, defaultvalue = 0, pady = 1)
        v_AssetCorr = make_variable_interface(left_frame, '기초자산상관계수', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 0.15)

        ResultFrame = tk.Frame(main_frame)
        ResultFrame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        def run_func() : 
            BasketCDSFlag = int(str(vb_BasketCDSFlag.get(vb_BasketCDSFlag.curselection())).split(":")[0]) if vb_BasketCDSFlag.curselection() else 0
            NAsset = int(str(vb_NAsset.get(vb_NAsset.curselection())).split(":")[0]) if vb_NAsset.curselection() else 1
            NthDefault = int(str(vb_NthDefault.get(vb_NthDefault.curselection())).split(":")[0]) if vb_NthDefault.curselection() else 1
            AssetCorr = float(v_AssetCorr.get()) if len(str(v_AssetCorr.get())) > 0 else 0
            BasketCDSInput[0] = BasketCDSFlag 
            BasketCDSInput[1] = NAsset 
            BasketCDSInput[2] = NthDefault 
            BasketCDSInput[3] = AssetCorr                    

            result_window.destroy()
        tk.Button(ResultFrame, text = '바스켓CDS여부 적용', padx = 10, pady = 10, font = ("맑은 고딕",12,'bold'), command = run_func, width = 15).pack()

    run_button = tk.Button(
        left_frame,
        text="마켓데이터 입력",
        command=lambda: open_market_window(root, ZeroTermList,ZeroRateList,HazardTermList,HazardRateList),
        font = ("맑은 고딕",12,'bold')
    )

    run_button2 = tk.Button(
        left_frame,
        text="바스켓CDS여부 입력",
        command=lambda: open_basketcds_window(root, BasketCDSInput),
        font = ("맑은 고딕",12,'bold')
    )

    Result_frame = tk.Frame(main_frame)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_TextFlag = make_listvariable_interface(Result_frame, 'TextFlag', ["0: Text 안찍음","1: Text 파일 찍음"], bold = True, listheight = 3, textfont = 11, titlelable=False, titleName = "바스켓CDS여부", defaultflag = True, defaultvalue = 0, pady = 1)
    vb_DRCFlag = make_listvariable_interface(Result_frame, 'DRC산출여부', ["0: 산출안함","1: 산출함"], bold = True, listheight = 3, textfont = 11, titlelable=False, titleName = "바스켓CDS여부", defaultflag = True, defaultvalue = 1, pady = 1)
    DRCCRDict = {'AAA' : 0.005, 'AA' : 0.02, 'A' : 0.03,'BBB' : 0.06, 'BB' : 0.15,'B' : 0.30,'CCC' : 0.50,'NR': 0.15} 

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
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        Recovery = float(v_Recovery.get()) if len(str(v_Recovery.get())) > 0 else 0.0
        LongShort = int(str(vb_LongShort.get(vb_LongShort.curselection())).split(":")[0]) if vb_LongShort.curselection() else 0                
        DRCFlag = int(str(vb_DRCFlag.get(vb_DRCFlag.curselection())).split(":")[0]) if vb_DRCFlag.curselection() else 1                
        
        Posi = 1 if LongShort == 0 else -1 
        CDSPremium = float(v_CDSPremium.get())/100 if len(str(v_CDSPremium.get())) > 0 else 0
        TextFlag = int(str(vb_TextFlag.get(vb_TextFlag.curselection())).split(":")[0]) if vb_TextFlag.curselection() else 0
        Bucket= int(str(vb_CSRBucket.get(vb_CSRBucket.curselection())).split(":")[0]) if vb_CSRBucket.curselection() else 1
        rw_csr = CSRRW[Bucket-1]
        rw_girr = 0.013/np.sqrt(2)
        CRRate = str(v_CRRate.get()).replace("+","").replace("-","").replace("1","") if len(str(v_CRRate.get())) > 0 else "NR"
        DRCRW = 0 if DRCFlag == 0 else DRCCRDict[CRRate.upper()]

        ZeroTermPremium = np.array(ZeroTermList[0], dtype = np.float64)
        ZeroRatePremium = np.array(ZeroRateList[0], dtype = np.float64)/100
        ZeroTermProtection = np.array(ZeroTermList[1], dtype = np.float64)
        ZeroRateProtection = np.array(ZeroRateList[1], dtype = np.float64)/100
        HazardTerm = np.array(HazardTermList[0], dtype = np.float64)
        HazardRate = np.array(HazardRateList[0], dtype = np.float64)/100
        NHazard = len(HazardTerm)
        RefTerm = ZeroTermPremium
        RefRate = ZeroRatePremium
        RefRiskRate = ZeroRatePremium
        Holidays = [19000101]
        NHolidays = 1

        ScheduleDF = get_from_sheetinterface(sht_ScheduleInfo)
        ScheduleData = ScheduleDF[["Reset Start","지급일"]]
        ResetDate = list(ScheduleDF["Reset Start"].apply(lambda x : str(x).replace("-","").replace(".0","")).astype(np.int64).values)
        PaymentDate = list(ScheduleDF["지급일"].apply(lambda x : str(x).replace("-","").replace(".0","")).astype(np.int64).values)
        NSchd = len(PaymentDate)
        PaymentDate_Leg1 = ScheduleData['지급일'].values
        Result_Value = np.zeros(100, dtype = np.float64)
        ResultHazardRate = np.zeros(len(HazardTerm), dtype = np.float64)
        ResultGreeks = np.zeros(10 + 3 * len(ZeroTermPremium) + 3 * len(HazardRate))
        Premium_Schedule = np.zeros(NSchd, dtype = np.float64)
        NCF_Leg1 = len(ScheduleData)
        Maturity = 0.5 * ((DayCountAtoB(ResetDate[0], PaymentDate[-1])/365 + 0.1) //0.5)
        f'''
            Public Declare PtrSafe Function Calc_OLD_CDS_Value Lib "CreditDerivatives.dll" ( _
                ByVal NPremiumCurve As Long, ByRef PremiumCurveTerm As Double, ByRef PremiumCurve As Double, _
                ByVal NProtectionCurve As Long, ByRef ProtectionCurveTerm As Double, ByRef ProtectionCurve As Double, _
                ByVal DataFlag As Long, ByVal NHazardRate As Long, ByRef HazardRateTerm As Double, ByRef HazardRate As Double, ByVal CalcQMethod As Long, _
                ByVal NRefZero As Long, ByRef RefZeroTerm As Double, ByRef ZeroRiskFree As Double, ByRef ZeroRiskyBond As Double, ByVal DefaultRateCalcMethod As Long, _
                ByVal Recovery As Double, ByVal ScheduleInputFlag As Long, ByVal NCPN_Ann As Long, ByVal Maturity As Double, ByVal NSchedule As Long, ByRef ResetDateYYYYMMDD As Long, ByRef PayDateYYYYMMDD As Long, ByVal PricingDateYYYYMMDD As Long, _
                ByVal NHoliday As Long, ByRef HolidayYYYYMMDD As Long, ByVal BasketCDSFlag As Long, ByVal BasketNTotalAsset As Long, ByVal BasketNthDefault As Long, _
                ByVal BasketAssetCorrelation As Double, ByVal OLS_CDS_Spread As Double, ByVal Protection_Position As Long, ByVal TextFlag As Long, ByVal GreekFlag As Long, ByRef Result_Value As Double, ByRef ResultHazardRate As Double, ByRef ResultGreeks As Double, ByRef Premium_Schedule As Double, ByVal NotionalAmount As Double _
            ) As Long
            '''
        Nominal_c = ct.c_double(Nominal)
        NPremiumCurve_c = ct.c_long(len(ZeroTermPremium))
        PremiumCurveTerm_np, PremiumCurveTerm_c = arr_double(ZeroTermPremium)
        PremiumCurve_np, PremiumCurve_c = arr_double(ZeroRatePremium)
        NProtectionCurve_c = ct.c_long(len(ZeroTermProtection))
        ProtectionCurveTerm_np, ProtectionCurveTerm_c = arr_double(ZeroTermProtection)
        ProtectionCurve_np, ProtectionCurve_c = arr_double(ZeroRateProtection)
        NHazardRate_c = ct.c_long(len(HazardTerm))
        HazardRateTerm_np, HazardRateTerm_c = arr_double(HazardTerm)
        HazardRate_np, HazardRate_c = arr_double(HazardRate)
        NRefZero_c = ct.c_long(len(RefTerm))
        RefZeroTerm_np, RefZeroTerm_c = arr_double(RefTerm)
        ZeroRiskFree_np, ZeroRiskFree_c = arr_double(RefRate)
        ZeroRiskyBond_np, ZeroRiskyBond_c = arr_double(RefRiskRate)
        Recovery_c = ct.c_double(Recovery)
        Maturity_c = ct.c_double(Maturity)
        NSchedule_c = ct.c_long(len(ResetDate))
        ResetDateYYYYMMDD_np, ResetDateYYYYMMDD_c = arr_long(ResetDate)
        PayDateYYYYMMDD_np, PayDateYYYYMMDD_c = arr_long(PaymentDate)
        PricingDateYYYYMMDD_c = ct.c_long(PriceDate)
        NHoliday_c = ct.c_long(NHolidays)
        Holidays_np, HolidayYYYYMMDD_c = arr_long(Holidays)
        BasketCDSFlag_c = ct.c_long(BasketCDSInput[0])
        BasketNTotalAsset_c = ct.c_long(BasketCDSInput[1])
        BasketNthDefault_c = ct.c_long(BasketCDSInput[2])
        BasketAssetCorrelation_c = ct.c_double(BasketCDSInput[3])
        OLS_CDS_Spread_c = ct.c_double(CDSPremium)
        TextFlag_c = ct.c_long(TextFlag)
        Protection_Position_c = ct.c_long(1)
        GreekFlag_c = ct.c_long(1)
        Result_Value_np, Result_Value_c = arr_double(Result_Value)
        ResultHazardRate_np, ResultHazardRate_c = arr_double(ResultHazardRate)
        ResultGreeks_np, ResultGreeks_c = arr_double(ResultGreeks)
        Premium_Schedule_np, Premium_Schedule_c = arr_double(Premium_Schedule)

        Res = CalcCDSFunc(NPremiumCurve_c,  PremiumCurveTerm_c,  PremiumCurve_c, 
                    NProtectionCurve_c,  ProtectionCurveTerm_c,  ProtectionCurve_c, 
                    DataFlag_c,  NHazardRate_c,  HazardRateTerm_c,  HazardRate_c,  CalcQMethod_c, 
                    NRefZero_c,  RefZeroTerm_c,  ZeroRiskFree_c,  ZeroRiskyBond_c,  DefaultRateCalcMethod_c, 
                    Recovery_c,  ScheduleInputFlag_c,  NCPN_Ann_c,  Maturity_c,  NSchedule_c,  ResetDateYYYYMMDD_c,  PayDateYYYYMMDD_c,  PricingDateYYYYMMDD_c, 
                    NHoliday_c,  HolidayYYYYMMDD_c,  BasketCDSFlag_c,  BasketNTotalAsset_c,  BasketNthDefault_c,
                    BasketAssetCorrelation_c,  OLS_CDS_Spread_c,  Protection_Position_c,  TextFlag_c,  GreekFlag_c,  
                    Result_Value_c,  ResultHazardRate_c,  ResultGreeks_c,   Premium_Schedule_c,  Nominal_c)
        Current_CDS_Spread = Result_Value_c[0]        
        Premium_Value = Result_Value_c[3] * (-Posi)
        Protection_Value = Result_Value_c[4] * (Posi)
        OLD_CDS_Value = Result_Value_c[5] * Posi
        ResultHazard = np.ctypeslib.as_array(ResultHazardRate_c[:NHazard], shape = (NHazard))
        ResultHazardDF = pd.DataFrame([HazardTerm, ResultHazard], index = ['Term','DefaultProb']).T
        PremiumSchedule = np.ctypeslib.as_array(Premium_Schedule_c[:NSchd], shape = (NSchd))
        ResultScheduleDF = pd.DataFrame([PaymentDate, PremiumSchedule], index = ['PayDate','E(Premium)xDF']).T
        
        HazardPV01 = ResultGreeks[3] * Posi
        IR_PV01_Premium_Value = ResultGreeks[1] * (-Posi)
        IR_PV01_Protection_Value = ResultGreeks[2] * (Posi)
        x = IR_PV01_Premium_Value/0.0001 * rw_girr
        y = IR_PV01_Protection_Value/0.0001 * rw_girr
        GIRR = np.round(np.sqrt(x**2 + y**2 + 2 * 0.8 * x * y) * 0.8, 2)
        CSR = np.round(abs(HazardPV01)/0.0001 * rw_csr * 0.8, 2)
        DRC = np.round(DRCRW * Nominal , 2)
        RWA = np.round((GIRR + CSR + DRC) * 12.5,2)
        RWA_pct = np.round(RWA/Nominal, 4)
        ResultValue = pd.concat([ResultHazardDF,ResultScheduleDF],axis = 1)
        ResultValue['Par_CDS'] = [Current_CDS_Spread] +['']*(len(ResultValue)-1)
        ResultValue['Premium_Value'] = [Premium_Value] +['']*(len(ResultValue)-1)
        ResultValue['Protection_Value'] = [Protection_Value] +['']*(len(ResultValue)-1)
        ResultValue['OLD_CDS_Value'] = [OLD_CDS_Value] +['']*(len(ResultValue)-1)
        ResultValue['HazardPV01'] = [HazardPV01] +['']*(len(ResultValue)-1)
        ResultValue['IR_PV01_Premium_Value'] = [IR_PV01_Premium_Value] +['']*(len(ResultValue)-1)
        ResultValue['IR_PV01_Protection_Value'] = [IR_PV01_Protection_Value] +['']*(len(ResultValue)-1)

        output_label.config(text = f"산출결과: \nCurrent_CDS_Spread : \n{np.round(Current_CDS_Spread* 100,5)}%\nPremium_Value : \n{np.round(Premium_Value, 2)}\nProtection_Value : \n{np.round(Protection_Value, 2)}\nOLD_CDS_Value : \n{np.round(OLD_CDS_Value, 2)}\nGIRR, CSR, DRC : \n{GIRR} |{CSR} |{DRC} \n RWA : {RWA}({RWA_pct * 100}%)", font = ("맑은 고딕", 12, 'bold'))                       

        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(main_frame)
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

        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultValue, width = 100)
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2      
        MyArrays[4] = ResultValue
        MyArrays[5] = ResultValue
        #df.to_excel("ResultExcel.xlsx",index = False, header=False)
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)


    run_button.pack()
    run_button2.pack()
    root.mainloop()   
 
def IRPhaseStructuredSwap() : 
    numc = MainViewer(Title = 'Calibration Curve', MyText = '사용 커브 개수', MyList = ["1: 1개 커브 사용","2: 2개 커브 사용","3: 3개 커브 사용"], size = "800x450+30+30", splitby = ":", listheight = 8, textfont = 13, titlelable = False, titleName = "Name", MultiSelection = False, defaultvalue = 0, addtreeflag = False, treedata = pd.DataFrame([]), DefaultStringList = [], width = 95, expand = True)

    TempSchedule =[TimestampToYYYYMMDD(i) for i in MakeSchedule(today_YYYYMMDD - 10000, today_YYYYMMDD + 100000, 3)]
    StartSchedule = TempSchedule[:-1]
    EndSchedule = TempSchedule[1:]
    Multiple = [1] * len(StartSchedule)
    Multiple2 = [0] * len(StartSchedule)
    FixedCpnRate = [3.5] * len(StartSchedule)
    FixedCpnRate2 = [0] * len(StartSchedule)
    FixedRate = [0.0] * len(StartSchedule)
    
    ResultDataList = []
    ZeroTermList = []
    ZeroRateList = []
    for i in range(numc) : 
        if i == 1 : 
            ResultData, ZeroTerm, ZeroRate = HullWhite12FactorCalibration(DefaultZeroUse = True, DefaultZeroRate = [3.956,3.998,4.04,4.0755,4.111,4.188,4.298,4.456,4.804,4.934,5.037,5.151,5.264,5.669,5.625],name = str(i+1) + '번째 커브 Calibration')                                  
        else : 
            ResultData, ZeroTerm, ZeroRate = HullWhite12FactorCalibration(name = str(i+1) + '번째 커브 Calibration')
        
        Preprocessing_Term(ZeroTerm, int(ResultData['PriceDate'].iloc[0]))
        ResultDataList.append(ResultData)
        ZeroTermList.append(ZeroTerm)
        ZeroRateList.append(ZeroRate)
    PowerSpreadFlag_L1 = [0, 0, 0]
    PowerSpreadMaturity_L1 = [0.25, 0.25, 0.25, 0.25, 0.25, 0.25]
    PowerSpreadFlag_L2 = [0, 0, 0]
    PowerSpreadMaturity_L2 = [0.25, 0.25, 0.25, 0.25, 0.25, 0.25]
    NCPNRefRate_L1 = [4, 4, 4]
    NCPNRefRate_L2 = [4, 4, 4]
    RefRateCurveNum_L1 = [1, -1, -1]
    RefRateCurveNum_L2 = [1, -1, -1]
    DiscCurveIdx_L1 = [0]
    DiscCurveIdx_L2 = [0]
    CurveCorr = ([1.0, 0.0, 0.0],[0.0, 1.0, 0.0], [0.0, 0.0, 1.0])
    CurveCorrArr = np.identity(3)
    QuantoUseFlag = [0,0,0]
    QuantoCorr = [0.0,0.0,0.0]
    QuantoFXVol = [0.0,0.0,0.0]
    CvName = ['KRW IRS','커브명','커브명']
    def open_powerspread_window(root, PowerSpreadFlag, PowerSpreadMaturity, DiscCurveIdx, NCPNRefRate, RefRateCurveNum, RefRateNum = 1):     
        
        # 새로운 결과창
        result_window = tk.Toplevel(root)

        nindexs = 7
        ncolumns = 3
        result_window.title("ReferenceRate" + " Leg" + str(RefRateNum))
        result_window.geometry("1500x750+5+5")
        result_window.resizable(False, False)

        left_frame = tk.Frame(result_window)
        left_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')        
        vb_PSFlag1 = make_listvariable_interface(left_frame, 'PowerSpread\n적용여부', ["0: 파워스프레드 적용안함","1: 파워스프레드 적용함"], bold = True, listheight = 3, textfont = 11, titlelable=True, titleName = "\n커브1\n기초금리1", defaultflag = True, defaultvalue = 0, pady = 1)
        vb_RefSwapNCPNOneYear1 = make_listvariable_interface(left_frame, '기초금리 연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=2, pady = 1)
        vb_Rate1_RefSwapMaturity_T1 = make_listvariable_interface(left_frame, '기초금리1 만기1(년)', np.vectorize(lambda y : str(y))(np.arange(1, 201) * 0.25), listheight = 7, textfont = 11, titlelable=False, titleName = "\n커브1\n기초금리1",defaultflag = True, defaultvalue=3, bold = False, pady = 1)
        vb_Rate1_RefSwapMaturity_T2 = make_listvariable_interface(left_frame, '(PowerSpread금리)\n기초금리1 만기2(년)', np.vectorize(lambda y : str(y))(np.arange(1, 201) * 0.25), listheight = 7, textfont = 11,defaultflag = True, defaultvalue=0, bold = False, pady = 1)

        left_frame2 = tk.Frame(result_window)
        left_frame2.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')        
        sht_DiscCurve1 = AddVariableSheet(left_frame2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (list(ZeroTermList[0]) + ['']* 10, list(ZeroRateList[0]) + ['']* 10), VariableName = "ZeroCurve1", myfont = 12, anchor = 'w', padx = 5, pady = 1, sheet_width = 80, sheet_height = 30, titlelable= True, titleName = "\n커브1", MaxHeight=10)
        sht_DiscCurve1.set_all_column_widths(width=50)
        vb_RefRateUseFlag1 = make_listvariable_interface(left_frame2, '해당커브를 \n 기초금리로 사용', ["0: 사용안함","1: 사용"], bold = True, listheight = 3, textfont = 11, titlelable=False, titleName = "\n커브1\n기초금리1", defaultflag = True, defaultvalue = 1, pady = 1)

        left_frame3 = tk.Frame(result_window)
        left_frame3.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')        
        left_frame4 = tk.Frame(result_window)
        left_frame4.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')        
        left_frame5 = tk.Frame(result_window)
        left_frame5.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')        
        left_frame6 = tk.Frame(result_window)
        left_frame6.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')        
        left_frame7 = tk.Frame(result_window)
        left_frame7.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')        
         
        vb_DiscCvNum = make_listvariable_interface(left_frame7, '할인금리커브번호', [str(i+1) + ": 커브" + str(i+1) for i in range(numc)], bold = True, listheight = 3, textfont = 11, titlelable=True, titleName = "\n할인커브선택", defaultflag = True, defaultvalue = 0, pady = 1)

        if numc > 1 : 
            vb_PSFlag2 = make_listvariable_interface(left_frame3, 'PowerSpread\n적용여부', ["0: 파워스프레드 적용안함","1: 파워스프레드 적용함"], bold = True, listheight = 3, textfont = 11, titlelable=True, titleName = "\n커브2\n기초금리2", defaultflag = True, defaultvalue = 0, pady = 1)
            vb_RefSwapNCPNOneYear2 = make_listvariable_interface(left_frame3, '기초금리 연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=2, pady = 1)
            vb_Rate2_RefSwapMaturity_T1 = make_listvariable_interface(left_frame3, '기초금리2 만기1(년)', np.vectorize(lambda y : str(y))(np.arange(1, 201) * 0.25), listheight = 7, textfont = 11, titlelable=False, titleName = "\n커브2\n기초금리2",defaultflag = True, defaultvalue=19, bold = False, pady = 1)
            vb_Rate2_RefSwapMaturity_T2 = make_listvariable_interface(left_frame3, '(PowerSpread금리)\n기초금리2 만기2(년)', np.vectorize(lambda y : str(y))(np.arange(1, 201) * 0.25), listheight = 7, textfont = 11,defaultflag = True, defaultvalue=0, bold = False, pady = 1)
            sht_DiscCurve2 = AddVariableSheet(left_frame4, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (list(ZeroTermList[1] if numc > 1 else ['']*10) + ['']* 10, list(ZeroRateList[1] if numc > 1 else ['']*10) + ['']* 10), VariableName = "ZeroCurve2", myfont = 12, anchor = 'w', padx = 5, pady = 1, sheet_width = 80, sheet_height = 30, titlelable= True, titleName = "\n커브2", MaxHeight=10)
            sht_DiscCurve2.set_all_column_widths(width=50)
            vb_RefRateUseFlag2 = make_listvariable_interface(left_frame4, '해당커브를 \n 기초금리로 사용', ["0: 사용안함","1: 사용"], bold = True, listheight = 3, textfont = 11, titlelable=False, titleName = "\n커브2\n기초금리2", defaultflag = True, defaultvalue = 0, pady = 1)
        else : 
            vb_Rate2_RefSwapMaturity_T1 = vb_Rate2_RefSwapMaturity_T2 = vb_PSFlag2 = sht_DiscCurve2 = None
            vb_RefSwapNCPNOneYear2 = None
            vb_RefRateUseFlag2 = None

        if numc > 2 : 
            vb_PSFlag3 = make_listvariable_interface(left_frame5, 'PowerSpread\n적용여부', ["0: 파워스프레드 적용안함","1: 파워스프레드 적용함"], bold = True, listheight = 3, textfont = 11, titlelable=True, titleName = "\n커브3\n기초금리3", defaultflag = True, defaultvalue = 0, pady = 1)
            vb_RefSwapNCPNOneYear3 = make_listvariable_interface(left_frame5, '기초금리 연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=2, pady = 1)
            vb_Rate3_RefSwapMaturity_T1 = make_listvariable_interface(left_frame5, '기초금리3 만기1(년)', np.vectorize(lambda y : str(y))(np.arange(1, 201) * 0.25), listheight = 7, textfont = 11, titlelable=False, titleName = "\n커브3\n기초금리3",defaultflag = True, defaultvalue=19, bold = False, pady = 1)
            vb_Rate3_RefSwapMaturity_T2 = make_listvariable_interface(left_frame5, '(PowerSpread금리)\n기초금리3 만기3(년)', np.vectorize(lambda y : str(y))(np.arange(1, 201) * 0.25), listheight = 7, textfont = 11,defaultflag = True, defaultvalue=0, bold = False, pady = 1)
            sht_DiscCurve3 = AddVariableSheet(left_frame6, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (list(ZeroTermList[2] if numc > 2 else ['']*10) + ['']* 10, list(ZeroRateList[2] if numc > 2 else ['']*10) + ['']* 10), VariableName = "ZeroCurve3", myfont = 12, anchor = 'w', padx = 5, pady = 1, sheet_width = 80, sheet_height = 30, titlelable= True, titleName = "\n커브3", MaxHeight=10)
            sht_DiscCurve3.set_all_column_widths(width=50)
            vb_RefRateUseFlag3 = make_listvariable_interface(left_frame6, '해당커브를 \n 기초금리로 사용', ["0: 사용안함","1: 사용"], bold = True, listheight = 3, textfont = 11, titlelable=False, titleName = "\n커브3\n기초금리3", defaultflag = True, defaultvalue = 0, pady = 1)

        else : 
            vb_Rate3_RefSwapMaturity_T1 = vb_Rate3_RefSwapMaturity_T2 = vb_PSFlag3 = sht_DiscCurve3 = None
            vb_RefSwapNCPNOneYear3 = None
            vb_RefRateUseFlag3 = None

        def run_func() : 
            PSFlag1 = int(str(vb_PSFlag1.get(vb_PSFlag1.curselection())).split(":")[0]) if vb_PSFlag1.curselection() else 0
            DiscCvNum = int(str(vb_DiscCvNum.get(vb_DiscCvNum.curselection())).split(":")[0]) if vb_DiscCvNum.curselection() else 1
            RefSwapNCPNOneYear1 = int(str(vb_RefSwapNCPNOneYear1.get(vb_RefSwapNCPNOneYear1.curselection()))) if vb_RefSwapNCPNOneYear1.curselection() else 4
            RefRateUseFlag1 = int(str(vb_RefRateUseFlag1.get(vb_RefRateUseFlag1.curselection())).split(":")[0]) if vb_RefRateUseFlag1.curselection() else 1

            DiscCurveIdx[0] = DiscCvNum
            Rate1_RefSwapMaturity_T1 = float((vb_Rate1_RefSwapMaturity_T1.get(vb_Rate1_RefSwapMaturity_T1.curselection()))) if vb_Rate1_RefSwapMaturity_T1.curselection() else 0.25
            Rate1_RefSwapMaturity_T2 = float((vb_Rate1_RefSwapMaturity_T2.get(vb_Rate1_RefSwapMaturity_T2.curselection()))) if vb_Rate1_RefSwapMaturity_T2.curselection() else 0.25
            if numc > 1 : 
                PSFlag2 = int(str(vb_PSFlag2.get(vb_PSFlag2.curselection())).split(":")[0]) if vb_PSFlag2.curselection() else 0
                RefSwapNCPNOneYear2 = int(str(vb_RefSwapNCPNOneYear2.get(vb_RefSwapNCPNOneYear2.curselection()))) if vb_RefSwapNCPNOneYear2.curselection() else 4
                RefRateUseFlag2 = int(str(vb_RefRateUseFlag2.get(vb_RefRateUseFlag2.curselection())).split(":")[0]) if vb_RefRateUseFlag2.curselection() else 0
                Rate2_RefSwapMaturity_T1 = float((vb_Rate2_RefSwapMaturity_T1.get(vb_Rate2_RefSwapMaturity_T1.curselection()))) if vb_Rate2_RefSwapMaturity_T1.curselection() else 0.25
                Rate2_RefSwapMaturity_T2 = float((vb_Rate2_RefSwapMaturity_T2.get(vb_Rate2_RefSwapMaturity_T2.curselection()))) if vb_Rate2_RefSwapMaturity_T2.curselection() else 0.25
            else : 
                PSFlag2 = 0
                Rate2_RefSwapMaturity_T1 = 0.25
                Rate2_RefSwapMaturity_T2 = 0.25
                RefSwapNCPNOneYear2 = 4
                RefRateUseFlag2 = 0

            if numc > 2 : 
                PSFlag3 = int(str(vb_PSFlag3.get(vb_PSFlag3.curselection())).split(":")[0]) if vb_PSFlag3.curselection() else 0
                RefSwapNCPNOneYear3 = int(str(vb_RefSwapNCPNOneYear3.get(vb_RefSwapNCPNOneYear3.curselection()))) if vb_RefSwapNCPNOneYear3.curselection() else 4
                RefRateUseFlag3 = int(str(vb_RefRateUseFlag3.get(vb_RefRateUseFlag3.curselection())).split(":")[0]) if vb_RefRateUseFlag3.curselection() else 0
                Rate3_RefSwapMaturity_T1 = float((vb_Rate3_RefSwapMaturity_T1.get(vb_Rate3_RefSwapMaturity_T1.curselection()))) if vb_Rate3_RefSwapMaturity_T1.curselection() else 0.25
                Rate3_RefSwapMaturity_T2 = float((vb_Rate3_RefSwapMaturity_T2.get(vb_Rate3_RefSwapMaturity_T2.curselection()))) if vb_Rate3_RefSwapMaturity_T2.curselection() else 0.25
            else : 
                PSFlag3 = 0
                Rate3_RefSwapMaturity_T1 = 0.25
                Rate3_RefSwapMaturity_T2 = 0.25
                RefSwapNCPNOneYear3 = 4
                RefRateUseFlag3 = 0
            NCPNRefRate[0] = RefSwapNCPNOneYear1
            NCPNRefRate[1] = RefSwapNCPNOneYear2
            NCPNRefRate[2] = RefSwapNCPNOneYear3
            PowerSpreadFlag[0] = PSFlag1
            PowerSpreadFlag[1] = PSFlag2
            PowerSpreadFlag[2] = PSFlag3
            PowerSpreadMaturity[0] = Rate1_RefSwapMaturity_T1
            PowerSpreadMaturity[1] = Rate1_RefSwapMaturity_T2
            PowerSpreadMaturity[2] = Rate2_RefSwapMaturity_T1
            PowerSpreadMaturity[3] = Rate2_RefSwapMaturity_T2
            PowerSpreadMaturity[4] = Rate3_RefSwapMaturity_T1
            PowerSpreadMaturity[5] = Rate3_RefSwapMaturity_T2
            if RefRateUseFlag1 == 0 and RefRateUseFlag2 == 0 and RefRateUseFlag1 == 0 : 
                RefRateCurveNum[1] = RefRateCurveNum[2] = RefRateCurveNum[3]
            else : 
                RefRateCurveNum[0] = 1 if RefRateUseFlag1 > 0 else -1
                RefRateCurveNum[1] = 2 if RefRateUseFlag2 > 0 else -1
                RefRateCurveNum[2] = 3 if RefRateUseFlag3 > 0 else -1

            result_window.destroy()
        tk.Button(left_frame, text = '레퍼런스금리 적용', padx = 10, pady = 10, font = ("맑은 고딕",12,'bold'), command = run_func, width = 15).pack()

    def open_result_window(root):
        # 새로운 결과창
        result_window = tk.Toplevel(root)
        result_window.title("MarketData")
        result_window.geometry("1520x700+5+5")
        result_window.resizable(False, False)

        # ==========================================
        # Scrollbar
        # ==========================================

        v_scroll = tk.Scrollbar(
            result_window,
            orient="vertical",
            width=20
        )
        v_scroll.pack(side="right", fill="y")

        h_scroll = tk.Scrollbar(
            result_window,
            orient="horizontal",
            width=20
        )
        h_scroll.pack(side="bottom", fill="x")

        canvas = tk.Canvas(
            result_window,
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        v_scroll.config(command=canvas.yview)
        h_scroll.config(command=canvas.xview)

        main_frame = tk.Frame(canvas)

        canvas_window = canvas.create_window(
            (0, 0),
            window=main_frame,
            anchor="nw"
        )

        # Frame 크기 변경 시 scroll 영역 갱신
        def on_frame_configure(event):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        main_frame.bind(
            "<Configure>",
            on_frame_configure
        )

        nindexs = 7
        ncolumns = 3

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        sht_DiscCurve1 = AddVariableSheet(left_frame, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (list(ZeroTermList[0]) + ['']* 10, list(ZeroRateList[0]) + ['']* 10), VariableName = "ZeroCurve1", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, titlelable= True, titleName = "MarketData1", MaxHeight=10)
        sht_DiscCurve1.set_all_column_widths(width=50)
        v_cvnm1 = make_variable_interface(left_frame, '커브명', bold = True, textfont = 11, defaultflag = CvName[0])

        left_frame2 = tk.Frame(main_frame)
        left_frame2.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        v_Kappa1 = make_variable_interface(left_frame2, 'kappa', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[0]["HWKappa"].iloc[0], titlelable= True, titleName = "MarketData1")
        sht_HWVol1 = AddVariableSheet(left_frame2, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','HWVol','HWVol2F'], defaultvalues = (list(ResultDataList[0]["OptMat"].values) + ['']* 10, list(ResultDataList[0]["HWVol"].values) + ['']* 10, list(ResultDataList[0]["HWVol2F"].values) + ['']* 10), VariableName = "HWVol", myfont = 9, anchor = 'w', padx = 2, pady = 2, sheet_width = 85, sheet_height = 25, MaxHeight=10)
        sht_HWVol1.set_all_column_widths(width=65)
        v_Kappa1_2F = make_variable_interface(left_frame2, 'kappa2F', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[0]["HWKappa2F"].iloc[0])
        v_Rho1 = make_variable_interface(left_frame2, 'Rho12F', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[0]["Rho"].iloc[0])
        vb_QuantoUse1 = make_listvariable_interface(left_frame2, 'QuantoFlag', ["0: Quanto아님","1: Quanto맞음"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)
        v_Quanto1 = make_variable_interface(left_frame2, 'QuantoCorr', bold = True, textfont = 11, defaultflag = True, defaultvalue=0)
        v_VXV1 = make_variable_interface(left_frame2, 'FXVol', bold = True, textfont = 11, defaultflag = True, defaultvalue=0.0)

        left_frame3 = tk.Frame(main_frame)
        left_frame3.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        sht_DiscCurve2 = AddVariableSheet(left_frame3, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (list(ZeroTermList[1] if numc > 1 else ['']*10) + ['']* 10, list(ZeroRateList[1] if numc > 1 else ['']*10) + ['']* 10), VariableName = "ZeroCurve2", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, titlelable= True, titleName = "MarketData2", MaxHeight=10)
        sht_DiscCurve2.set_all_column_widths(width=50)
        v_cvnm2 = make_variable_interface(left_frame3, '커브명', bold = True, textfont = 11, defaultflag = CvName[1])

        left_frame4 = tk.Frame(main_frame)
        left_frame4.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        v_Kappa2 = make_variable_interface(left_frame4, 'kappa', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[1]["HWKappa"].iloc[0] if numc > 1 else 0.01, titlelable= True, titleName = "MarketData2")
        sht_HWVol2 = AddVariableSheet(left_frame4, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','HWVol','HWVol2F'], defaultvalues = (list(ResultDataList[1]["OptMat"].values if numc > 1 else [''] * 10) + ['']* 10, list(ResultDataList[1]["HWVol"].values if numc > 1 else [''] * 10) + ['']* 10, list(ResultDataList[1]["HWVol2F"].values if numc > 1 else [''] * 10) + ['']* 10), VariableName = "HWVol", myfont = 9, anchor = 'w', padx = 2, pady = 2, sheet_width = 85, sheet_height = 25, MaxHeight=10)
        sht_HWVol2.set_all_column_widths(width=65)
        v_Kappa2_2F = make_variable_interface(left_frame4, 'kappa2F', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[1]["HWKappa2F"].iloc[0] if numc > 1 else 0.01)
        v_Rho2 = make_variable_interface(left_frame4, 'Rho12F', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[1]["Rho"].iloc[0] if numc > 1 else 0.0)
        vb_QuantoUse2 = make_listvariable_interface(left_frame4, 'QuantoFlag', ["0: Quanto아님","1: Quanto맞음"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)
        v_Quanto2 = make_variable_interface(left_frame4, 'QuantoCorr', bold = True, textfont = 11, defaultflag = True, defaultvalue=0.0)
        v_VXV2 = make_variable_interface(left_frame4, 'FXVol', bold = True, textfont = 11, defaultflag = True, defaultvalue=0.0)

        left_frame5 = tk.Frame(main_frame)
        left_frame5.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        sht_DiscCurve3 = AddVariableSheet(left_frame5, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','Rate'], defaultvalues = (list(ZeroTermList[2] if numc > 2 else ['']*10) + ['']* 10, list(ZeroRateList[2] if numc > 2 else ['']*10) + ['']* 10), VariableName = "ZeroCurve3", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 30, titlelable= True, titleName = "MarketData3", MaxHeight=10)
        sht_DiscCurve3.set_all_column_widths(width=50)
        v_cvnm3 = make_variable_interface(left_frame5, '커브명', bold = True, textfont = 11, defaultflag = CvName[2])

        left_frame6 = tk.Frame(main_frame)
        left_frame6.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        v_Kappa3 = make_variable_interface(left_frame6, 'kappa', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[2]["HWKappa"].iloc[0] if numc > 2 else 0.01, titlelable= True, titleName = "MarketData3")
        sht_HWVol3 = AddVariableSheet(left_frame6, nindexs = nindexs, ncolumns= ncolumns,targetcolumns = ['Term','HWVol',"HWVol2F"], defaultvalues = (list(ResultDataList[2]["OptMat"].values if numc > 2 else [''] * 10) + ['']* 10, list(ResultDataList[2]["HWVol"].values if numc > 2 else [''] * 10) + ['']* 10, list(ResultDataList[2]["HWVol2F"].values if numc > 2 else [''] * 10) + ['']* 10), VariableName = "HWVol", myfont = 9, anchor = 'w', padx = 2, pady = 2, sheet_width = 85, sheet_height = 25, MaxHeight=10)
        sht_HWVol3.set_all_column_widths(width=65)
        v_Kappa3_2F = make_variable_interface(left_frame6, 'kappa', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[2]["HWKappa2F"].iloc[0] if numc > 2 else 0.01)
        v_Rho3 = make_variable_interface(left_frame6, 'Rho12F', bold = True, textfont = 11, defaultflag = True, defaultvalue=ResultDataList[2]["Rho"].iloc[0] if numc > 2 else 0.0)
        vb_QuantoUse3 = make_listvariable_interface(left_frame6, 'QuantoFlag', ["0: Quanto아님","1: Quanto맞음"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)
        v_Quanto3 = make_variable_interface(left_frame6, 'QuantoCorr', bold = True, textfont = 11, defaultflag = True, defaultvalue=0)
        v_VXV3 = make_variable_interface(left_frame6, 'FXVol', bold = True, textfont = 11, defaultflag = True, defaultvalue=0.0)

        left_frame7 = tk.Frame(main_frame)
        left_frame7.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')        
        sht_CurveCorr = AddVariableSheet(left_frame7, nindexs = 3, ncolumns= 3,targetcolumns = ['커브1','커브2','커브3'], defaultvalues = CurveCorr, VariableName = "CurveCorr", myfont = 10, anchor = 'w', padx = 5, pady = 2, sheet_width = 80, sheet_height = 60, titlelable= True, titleName = "CurveCorr", MaxHeight=10)
        sht_CurveCorr.set_all_column_widths(width=45)

        ResultFrame = tk.Frame(main_frame)
        ResultFrame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')        
        def run_func() : 
            HWV1 = HWV2 = HWV3 = pd.DataFrame([])
            DiscCurve1 = get_from_sheetinterface(sht_DiscCurve1)
            DiscCurve1["Term"] = DiscCurve1["Term"].apply(lambda x : str(x).replace("-","").replace(".0","")).astype(np.float64)
            DiscCurve1["Rate"] = DiscCurve1["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            ZeroTerm1 = list(DiscCurve1["Term"].values)

            cvnm1 = str(v_cvnm1.get()) if len(str(v_cvnm1.get())) > 0 else 'KRW IRS'
            cvnm2 = str(v_cvnm2.get()) if len(str(v_cvnm2.get())) > 0 else 'KRW IRS'
            cvnm3 = str(v_cvnm3.get()) if len(str(v_cvnm3.get())) > 0 else 'KRW IRS'
            CvName[0] = cvnm1
            CvName[1] = cvnm2
            CvName[2] = cvnm3
                        
            Curve_Correlation = get_from_sheetinterface(sht_CurveCorr)
            
            for i1 in range(3) : 
                for i2 in range(3) : 
                    if i1 != i2 : 
                        vstr = Curve_Correlation.values[i1][i2]
                        CurveCorrArr[i1][i2] = float(vstr)

            QuantoUse1 = int(str(vb_QuantoUse1.get(vb_QuantoUse1.curselection())).split(":")[0]) if vb_QuantoUse1.curselection() else 0
            QuantoUse2 = int(str(vb_QuantoUse2.get(vb_QuantoUse2.curselection())).split(":")[0]) if vb_QuantoUse2.curselection() else 0
            QuantoUse3 = int(str(vb_QuantoUse3.get(vb_QuantoUse3.curselection())).split(":")[0]) if vb_QuantoUse3.curselection() else 0
            QuantoUseFlag[0] = QuantoUse1
            QuantoUseFlag[1] = QuantoUse2
            QuantoUseFlag[2] = QuantoUse3
            Quanto1 = float(v_Quanto1.get()) if len(str(v_Quanto1.get())) > 0 else 0.0
            Quanto2 = float(v_Quanto2.get()) if len(str(v_Quanto2.get())) > 0 else 0.0
            Quanto3 = float(v_Quanto3.get()) if len(str(v_Quanto3.get())) > 0 else 0.0
            QuantoCorr[0] = Quanto1
            QuantoCorr[1] = Quanto2
            QuantoCorr[2] = Quanto3
            QuantoVol1 = float(v_VXV1.get()) if len(str(v_VXV1.get())) > 0 else 0.0
            QuantoVol2 = float(v_VXV2.get()) if len(str(v_VXV2.get())) > 0 else 0.0
            QuantoVol3 = float(v_VXV3.get()) if len(str(v_VXV3.get())) > 0 else 0.0
            QuantoFXVol[0] = QuantoVol1
            QuantoFXVol[1] = QuantoVol2
            QuantoFXVol[2] = QuantoVol3

            mx1 = np.abs(DiscCurve1["Rate"].values).max()
            ZeroRate1 = list(DiscCurve1["Rate"].values/100 if mx1 > 0.3 else DiscCurve1["Rate"].values)
            Kappa1 = float(v_Kappa1.get()) if len(str(v_Kappa1.get())) > 0 else 0.01
            Kappa1_2F = float(v_Kappa1_2F.get()) if len(str(v_Kappa1_2F.get())) > 0 else 0.01
            Rho1 = float(v_Rho1.get()) if len(str(v_Rho1.get())) > 0 else 0.0
            ZeroTermList[0] = ZeroTerm1
            ZeroRateList[0] = ZeroRate1
            HWV1 = get_from_sheetinterface(sht_HWVol1)
            HWV1["OptMat"] = HWV1["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            HWV1["HWVol"] = HWV1["HWVol"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            HWV1["HWVol2F"] = HWV1["HWVol2F"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
            HWVAvg = HWV1["HWVol"].values.mean()
            if HWVAvg > 0.2 : 
                HWV1["HWVol"] = HWV1["HWVol"].values.astype(np.float64)/100
                HWV1["HWVol2F"] = HWV1["HWVol2F"].values.astype(np.float64)/100
            else : 
                HWV1["HWVol"] = HWV1["HWVol"].values.astype(np.float64)
                HWV1["HWVol2F"] = HWV1["HWVol2F"].values.astype(np.float64)
            HWV1['HWKappa'] = Kappa1
            HWV1['HWKappa2F'] = Kappa1_2F
            HWV1['Rho'] = Rho1
            ResultDataList[0] = HWV1

            if numc > 1 : 
                DiscCurve2 = get_from_sheetinterface(sht_DiscCurve2)
                DiscCurve2["Term"] = DiscCurve2["Term"].apply(lambda x : str(x).replace("-","").replace(".0","")).astype(np.float64)
                DiscCurve2["Rate"] = DiscCurve2["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                ZeroTerm2 = list(DiscCurve2["Term"].values)
                mx2 = np.abs(DiscCurve2["Rate"].values).max()
                ZeroRate2 = list(DiscCurve2["Rate"].values/100 if mx2 > 0.3 else DiscCurve2["Rate"].values)
                Kappa2 = float(v_Kappa2.get()) if len(str(v_Kappa2.get())) > 0 else 0.01
                Kappa2_2F = float(v_Kappa2_2F.get()) if len(str(v_Kappa2_2F.get())) > 0 else 0.01
                Rho2 = float(v_Rho2.get()) if len(str(v_Rho2.get())) > 0 else 0.0
                ZeroTermList[1] = ZeroTerm2
                ZeroRateList[1] = ZeroRate2
                HWV2 = get_from_sheetinterface(sht_HWVol2)
                HWV2["OptMat"] = HWV2["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                HWV2["HWVol"] = HWV2["HWVol"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                HWV2["HWVol2F"] = HWV2["HWVol2F"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                HWVAvg = HWV2["HWVol"].values.mean()
                if HWVAvg > 0.2 : 
                    HWV2["HWVol"] = HWV2["HWVol"].values.astype(np.float64)/100
                    HWV2["HWVol2F"] = HWV2["HWVol2F"].values.astype(np.float64)/100
                else : 
                    HWV2["HWVol"] = HWV2["HWVol"].values.astype(np.float64)
                    HWV2["HWVol2F"] = HWV2["HWVol2F"].values.astype(np.float64)
                HWV2['HWKappa'] = Kappa2
                HWV2['HWKappa2F'] = Kappa2_2F
                HWV2['Rho'] = Rho2            
                ResultDataList[1] = HWV2

            if numc > 2 : 
                DiscCurve3 = get_from_sheetinterface(sht_DiscCurve3)
                DiscCurve3["Term"] = DiscCurve3["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                DiscCurve3["Rate"] = DiscCurve3["Rate"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                ZeroTerm3 = list(DiscCurve3["Term"].values)
                mx3 = np.abs(DiscCurve3["Rate"].values).max()
                ZeroRate3 = list(DiscCurve3["Rate"].values/100 if mx3 > 0.3 else DiscCurve3["Rate"].values)
                Kappa3 = float(v_Kappa3.get()) if len(str(v_Kappa3.get())) > 0 else 0.01
                Kappa3_2F = float(v_Kappa3_2F.get()) if len(str(v_Kappa3_2F.get())) > 0 else 0.01
                Rho3 = float(v_Rho3.get()) if len(str(v_Rho3.get())) > 0 else 0.0
                ZeroTermList[2] = ZeroTerm3
                ZeroRateList[2] = ZeroRate3
                HWV3 = get_from_sheetinterface(sht_HWVol3)
                HWV3["OptMat"] = HWV3["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                HWV3["HWVol"] = HWV3["HWVol"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                HWV3["HWVol2F"] = HWV3["HWVol2F"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
                HWVAvg = HWV3["HWVol"].values.mean()
                if HWVAvg > 0.2 : 
                    HWV3["HWVol"] = HWV3["HWVol"].values.astype(np.float64)/100
                    HWV3["HWVol2F"] = HWV3["HWVol2F"].values.astype(np.float64)/100
                else : 
                    HWV3["HWVol"] = HWV3["HWVol"].values.astype(np.float64)
                    HWV3["HWVol2F"] = HWV3["HWVol2F"].values.astype(np.float64)
                HWV3['HWKappa'] = Kappa3
                HWV3['HWKappa2F'] = Kappa3_2F
                HWV3['Rho'] = Rho3            
                ResultDataList[2] = HWV3
            result_window.destroy()
        tk.Button(left_frame, text = '마켓데이터 적용', padx = 10, pady = 10, font = ("맑은 고딕",12,'bold'), command = run_func, width = 15).pack()
                                
    RefRateMultipleList = [str(n) + ' : R x ' + str(i) + '배 페이오프' for n, i in enumerate(np.arange(0,50,0.25))] + [str(-n) + ' : R x ' + str(-i) + '배 페이오프' for n, i in enumerate(np.arange(0,50,0.25))][1:]

    VBAString = '''
                Public Declare PtrSafe Function Pricing_IRPhaseStructuredSwap Lib "IRPhaseStructuredSwap.dll" ( _
                    ByVal PriceDateExcel As Long, ByVal NAFlag As Long, ByVal Notional As Double, ByRef PayoffStructure As Long, ByRef HolidayFlagCount As Long, ByRef Holidays_Excel As Long, _
                    ByRef RcvFlag As Long, ByRef RcvMaxLossReturn As Double, ByRef RcvRefCurveNumber As Long, ByRef RcvRefRateType As Long, ByRef RcvSwapInfo As Double, ByRef RcvDayCountFlag As Long, ByRef RcvRefCondMultiple As Double, ByRef RcvRefPowerSpreadFlag As Long, ByRef RcvRefPowerSpreadMat As Double, ByRef RcvRefRange As Double, ByRef RcvPayoffMultiple As Double, ByVal NRcvCashFlow As Long, ByRef RcvCashFlowScheduleExcelDate As Long, ByRef RcvCouponFixRate As Double, _
                    ByRef PayFlag As Long, ByRef PayMaxLossReturn As Double, ByRef PayRefCurveNumber As Long, ByRef PayRefRateType As Long, ByRef PaySwapInfo As Double, ByRef PayDayCountFlag As Long, ByRef PayRefCondMultiple As Double, ByRef PayRefPowerSpreadFlag As Long, ByRef PayRefPowerSpreadMat As Double, ByRef PayRefRange As Double, ByRef PayPayoffMultiple As Double, ByVal NPayCashFlow As Long, ByRef PayCashFlowScheduleExcelDate As Long, ByRef PayCouponFixRate As Double, _
                    ByRef NHWVolCount As Long, ByRef HWVolTermArray As Double, ByRef HWVolArray As Double, ByRef HWKappaArray As Double, ByRef NZeroRate As Long, ByRef ZeroTerm As Double, ByRef ZeroRate As Double, _
                    ByRef Corr As Double, ByRef NDayHistRcv As Long, ByRefRateHistDateRcv As Long, ByRef RateHistRcv As Double, ByRef NDayHistPay As Long, ByRef RateHistDatePay As Long, ByRef RateHistPay As Double, _
                    ByVal NSimul As Long, ByRef GreekTextFlag As Long, ByVal NOption As Long, ByRef OptionDateAndFlag As Long, ByRef OptionKAndRange As Double, ByRef ResultPrice As Double, ByRef ResultRcv As Double, _
                    ByRef ResultPay As Double, ByVal HWFactorFlag As Long, ByRef HWVolArray2 As Double, ByRef HWQuantoInfo As Double, ByVal Error As String _
                ) As Long    
                '''
    CalcFunc, VariablesFormat, VariableNames = ConvertPythonFormatfromVBAformat(VBAString)
    #pd.DataFrame(VariablesFormat).to_excel("변수.xlsx")
    root, v_scroll, h_scroll, canvas, main_frame, canvas_window = interface_basic_settings('Structured Swap HW Simulation')
    YYYY = int(today_YYYYMMDD) // 10000

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=today_YYYYMMDD)
    vb_NAFlag = make_listvariable_interface(left_frame, 'NA/BOND Flag', ["0: NA교환안함","1: NA교환함"], bold = True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    left_frame1 = tk.Frame(main_frame)
    left_frame1.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    sht_Leg1ScheduleInfo = AddVariableSheet(left_frame1, nindexs = 10, ncolumns= 8,targetcolumns = ["Reset Start","Reset End","기산일","기말일","지급일","고정쿠폰(%)","구조화금리적용","RangeCpn"], defaultvalues = (StartSchedule + ['']* 50, EndSchedule+ ['']* 50, StartSchedule+ ['']* 50, EndSchedule+ ['']* 50, EndSchedule+ ['']* 50, FixedCpnRate2+ ['']* 50,Multiple+ ['']* 50, [''] * len(Multiple2) + ['']* 50), VariableName = "Leg1 스케줄", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 95, sheet_height = 40, MaxHeight=20, headerfont= 9)
    sht_Leg1ScheduleInfo.set_all_column_widths(width=90)

    left_frame2 = tk.Frame(main_frame)
    left_frame2.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')

    vb_L1_DayCount = make_listvariable_interface(left_frame2, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, titlelable=True, titleName="Leg1 Information",defaultflag = True, defaultvalue=0, pady = 1)
    vb_L1_RAFlag = make_listvariable_interface(left_frame2, 'RangeAccrual Flag', ["0: 미사용","1: RangeAccrual","-1: Average금리"], bold = True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    run_button2 = tk.Button(
        left_frame2,
        text="레퍼런스 금리 \n 선택 및 입력",
        command=lambda: open_powerspread_window(root, PowerSpreadFlag_L1, PowerSpreadMaturity_L1, DiscCurveIdx_L1, NCPNRefRate_L1, RefRateCurveNum_L1, RefRateNum = 1),
        font = ("맑은 고딕",12,'bold')
    )
        
    v_L1_RCap = make_variable_interface(left_frame2, '기초금리RangeCap(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =100, pady = 1)
    v_L1_RFloor = make_variable_interface(left_frame2, '기초금리RangeFloor(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =-100, pady = 1)
    v_L1_RangeMultiple = make_variable_interface(left_frame2, '금리Range조건Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue =0, pady = 1)
    v_L1_PayoffMultiple = make_listvariable_interface(left_frame2, '금리PayoffMultiple', RefRateMultipleList, listheight = 5, textfont = 11,defaultflag = True, defaultvalue=4, bold = False, pady = 1, width= 23)

    #
    left_frame4 = tk.Frame(main_frame)
    left_frame4.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    sht_Leg2ScheduleInfo = AddVariableSheet(left_frame4, nindexs = 10, ncolumns= 8,targetcolumns = ["Reset Start","Reset End","기산일","기말일","지급일","고정쿠폰(%)","구조화금리적용","RangeCpn"], defaultvalues = (StartSchedule + ['']* 50, EndSchedule+ ['']* 50, StartSchedule+ ['']* 50, EndSchedule+ ['']* 50, EndSchedule+ ['']* 50, FixedCpnRate+ ['']* 50,Multiple2+ ['']* 50, [''] * len(Multiple2) + ['']* 50), VariableName = "Leg2 스케줄", myfont = 11, anchor = 'w', padx = 5, pady = 2, sheet_width = 95, sheet_height = 40, MaxHeight=20, headerfont= 9)
    sht_Leg2ScheduleInfo.set_all_column_widths(width=90)

    left_frame5 = tk.Frame(main_frame)
    left_frame5.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    vb_L2_DayCount = make_listvariable_interface(left_frame5, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, titlelable=True, titleName="Leg2 Information", defaultflag = True, defaultvalue=0, pady = 1)
    vb_L2_RAFlag = make_listvariable_interface(left_frame5, 'RangeAccrual Flag', ["0: 미사용","1: RangeAccrual","-1: Average금리"], bold = True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    run_button3 = tk.Button(
        left_frame5,
        text="레퍼런스 금리 \n 선택 및 입력",
        command=lambda: open_powerspread_window(root, PowerSpreadFlag_L2, PowerSpreadMaturity_L2, DiscCurveIdx_L2, NCPNRefRate_L2, RefRateCurveNum_L2, RefRateNum = 2),
        font = ("맑은 고딕",12,'bold')
    )    

    v_L2_RCap = make_variable_interface(left_frame5, '기초금리RangeCap(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =100, pady = 1)
    v_L2_RFloor = make_variable_interface(left_frame5, '기초금리RangeFloor(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =-100, pady = 1)
    v_L2_RangeMultiple = make_variable_interface(left_frame5, '금리Range조건Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue =1, pady = 1)
    v_L2_PayoffMultiple = make_listvariable_interface(left_frame5, '금리PayoffMultiple', RefRateMultipleList, listheight = 5, textfont = 11,defaultflag = True, defaultvalue=0, bold = False, pady = 1, width= 23)

    left_frame8 = tk.Frame(main_frame)
    left_frame8.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    DefaultTermHistory = [TimestampToYYYYMMDD(today + pd.DateOffset(days = -i)) for i in range(200) ][::-1]
    mycol = ["Date","Rate(Leg1)","Rate(Leg2)"] if numc == 1 else (["Date","Rate1(Leg1)","Rate1(Leg2)","Rate2(Leg1)","Rate2(Leg2)"] if numc == 2 else ["Date","Rate1(Leg1)","Rate1(Leg2)","Rate2(Leg1)","Rate2(Leg2)","Rate3(Leg1)","Rate3(Leg2)"])
    defaultvaluesHistoryLeg12 = (DefaultTermHistory, [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory)) if numc == 1 else ((DefaultTermHistory, [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory)) if numc == 2 else (DefaultTermHistory, [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory), [3.5115] * len(DefaultTermHistory)))
    
    RefRateHistory = AddVariableSheet(left_frame8, nindexs = len(DefaultTermHistory), ncolumns= 3,targetcolumns = mycol, defaultvalues = defaultvaluesHistoryLeg12, VariableName = "기초금리픽싱History", myfont = 9, anchor = 'w', padx = 4, pady = 2, sheet_width = 100, sheet_height = 100, MaxHeight=20)
    RefRateHistory.set_all_column_widths(width=85)

    left_frame9 = tk.Frame(main_frame)
    left_frame9.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    OptStartDate =[TimestampToYYYYMMDD(i) for i in MakeSchedule(today_YYYYMMDD, today_YYYYMMDD + 40000, 12)[1:]]

    vb_OptionFlag = make_listvariable_interface(left_frame9, '옵션보유자', ["0 : Leg1이 옵션보유"," 1: Leg2이 옵션보유"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, pady = 1)
    sht_OptScheduleInfo = AddVariableSheet(left_frame9, nindexs = len(OptStartDate) + 50, ncolumns= 1,targetcolumns = ["옵션행사일"], defaultvalues = (OptStartDate + ['']* 50, ), VariableName = "OptionDate", myfont = 12, anchor = 'w', padx = 5, pady = 2, sheet_width = 120, sheet_height = 40, MaxHeight=20, headerfont= 9)
    sht_OptScheduleInfo.set_all_column_widths(width=90)

    Result_frame = tk.Frame(main_frame)
    Result_frame.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    vb_HW2FFlag = make_listvariable_interface(Result_frame, 'HW2F Flag', ["0: 1F","1: 2F"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)
    vb_GreekFlag = make_listvariable_interface(Result_frame, 'Greek 산출여부', ["0: Greek산출안함","1: Greek산출"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 1)
    vb_TextFlag = make_listvariable_interface(Result_frame, 'LOGGING 산출여부', ["0: Logging안함","1: Logging"], bold = True, listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 0)

    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    ResultValue = pd.DataFrame([])
    ResultValue2 = pd.DataFrame([])
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultValue, ResultValue2]
    PayoffStructure = np.array([0,0], dtype = np.int64)
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        ResultValue = MyArrays[4]
        ResultValue2 = MyArrays[5]
        CorrMatrix = np.identity(4, dtype = np.float64)
        for iy in range(CurveCorrArr.shape[0]) : 
            for ix in range(CurveCorrArr.shape[1]) : 
                CorrMatrix[iy][ix] = CurveCorrArr[iy][ix]
        CorrMatrixReshaped = CorrMatrix.reshape(-1)
        splitfunc = lambda mystr : float(mystr[mystr.index('x')+1:mystr.index('배')].replace(" ",""))        
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else today_YYYYMMDD
        NominalFlag = int(str(vb_NAFlag.get(vb_NAFlag.curselection())).split(":")[0]) if vb_NAFlag.curselection() else 0
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        TextFlag = int(str(vb_TextFlag.get(vb_TextFlag.curselection())).split(":")[0]) if vb_TextFlag.curselection() else 0
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        HW2FFlag = int(str(vb_HW2FFlag.get(vb_HW2FFlag.curselection())).split(":")[0]) if vb_HW2FFlag.curselection() else 0

        HolidayFlagCount = np.array([0,0,0,0,0,0,
                                     1,1,1,1,1,1], dtype = np.int64)
        NHolidays = 6
        Holidays = np.array([19000101,19000101,19000101,19000101,19000101,19000101], dtype = np.int64)

        #L1, Leg1
        L1_RangeAccrualFlag = int(str(vb_L1_RAFlag.get(vb_L1_RAFlag.curselection())).split(":")[0]) if vb_L1_RAFlag.curselection() else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else 0
        
        L1_RCap = float(v_L1_RCap.get())/100 if len(str(v_L1_RCap.get())) > 0 else 10000
        L1_RFloor = float(v_L1_RFloor.get()) if len(str(v_L1_RFloor.get())) > 0 else -10000
        L1_RangeMultiple = float(v_L1_RangeMultiple.get()) if len(str(v_L1_RangeMultiple.get())) > 0 else 0
        L1_PayoffMultiple = splitfunc(str(v_L1_PayoffMultiple.get(v_L1_PayoffMultiple.curselection())).split(":")[1]) if v_L1_PayoffMultiple.curselection() else 0

        ScheduleDF_Leg1 = get_from_sheetinterface(sht_Leg1ScheduleInfo)
        if ScheduleDF_Leg1['기산일'].apply(lambda x : x == '').sum() == len(ScheduleDF_Leg1) : 
            ScheduleDF_Leg1['기산일'] = ScheduleDF_Leg1['Reset Start']
        if ScheduleDF_Leg1['기말일'].apply(lambda x : x == '').sum() == len(ScheduleDF_Leg1) : 
            ScheduleDF_Leg1['기말일'] = ScheduleDF_Leg1['Reset End']
        ScheduleDF_Leg1["고정쿠폰(%)"] = ScheduleDF_Leg1["고정쿠폰(%)"].apply(lambda x : 0 if str(x) == '' or 'nan' in str(x).lower() else x)
        ScheduleDF_Leg1["구조화금리적용"] = ScheduleDF_Leg1["구조화금리적용"].apply(lambda x : 0 if str(x) == '' or 'nan' in str(x).lower() else x)
        ScheduleDF_Leg1["RangeCpn"] = ScheduleDF_Leg1["RangeCpn"].apply(lambda x : 0 if str(x) == '' or 'nan' in str(x).lower() else x)

        ScheduleData_Leg1 = ScheduleDF_Leg1[["Reset Start","Reset End","기산일","기말일","지급일"]]
        PaymentDate_Leg1 = ScheduleData_Leg1['지급일'].values
        NCF_Leg1 = len(ScheduleData_Leg1)
        Schedule_Leg1 = ScheduleData_Leg1.T.values.astype(np.int64).reshape(-1)
        CPN_Leg1 = ScheduleDF_Leg1["고정쿠폰(%)"].astype(np.float64).values/100
        StructuredSlope_Leg1 = ScheduleDF_Leg1["구조화금리적용"].astype(np.float64).values
        RangeCpn_Leg1 = ScheduleDF_Leg1["RangeCpn"].astype(np.float64).values/100
        CouponFixRate_Leg1 = np.array(list(CPN_Leg1) + list(StructuredSlope_Leg1) + list(RangeCpn_Leg1), dtype = np.float64)
        L1_UsingCurveNum = np.array(RefRateCurveNum_L1)[np.array(RefRateCurveNum_L1) > 0 ]
        L1_NRefRateCurve = len(L1_UsingCurveNum)
        L1_FloatFlag = (ScheduleDF_Leg1["구조화금리적용"].astype(np.float64).values != 0).sum() > 0
        L1_MaxLoss = 100
        L1_MaxRet = 100
        L1_Flag_Ary = np.array([L1_NRefRateCurve, L1_FloatFlag, L1_RangeAccrualFlag, 0], dtype = np.int64)
        L1_MaxLossReturn_Ary = np.array([L1_MaxLoss, L1_MaxRet], dtype = np.float64)
        L1_RefCurveNumber_List = []
        L1_RefRateType_List = []
        L1_SwapInfo_List = []
        L1_DayCount_Ary = np.array([L1_DayCount, L1_DayCount, L1_DayCount, L1_DayCount],dtype = np.int64)
        L1_RefCondMultiple_Ary = np.array([L1_RangeMultiple, L1_RangeMultiple, L1_RangeMultiple], dtype = np.float64)
        L1_RefPowerSpreadFlag_List = []
        L1_RefPowerSpreadMat_List = []
        L1_RefRange_Ary = np.array([L1_RCap, L1_RFloor, L1_RCap, L1_RFloor, L1_RCap, L1_RFloor], dtype = np.float64)
        L1_PayoffMultiple_Ary = np.array([L1_PayoffMultiple, L1_PayoffMultiple, L1_PayoffMultiple])
        for i in range(4) :
            L1_RefRateType_List.append(1)
            if i > len(L1_UsingCurveNum) - 1 : 
                L1_RefCurveNumber_List.append(L1_RefCurveNumber_List[i-1])
            else : 
                L1_RefCurveNumber_List.append(L1_UsingCurveNum[i])
            if i == 3 : 
                L1_RefCurveNumber_List.append(DiscCurveIdx_L1[0])
        L1_RefCurveNumber = np.array(L1_RefCurveNumber_List, dtype = np.int64)        
        
        for i in range(3) : 
            idx = int(L1_RefCurveNumber[i]-1)
            NCPN = NCPNRefRate_L1[idx]
            T1 = PowerSpreadMaturity_L1[idx * i]
            T2 = PowerSpreadMaturity_L1[idx * i + 1]
            PS01 = PowerSpreadFlag_L1[idx]
            L1_SwapInfo_List.append(NCPN)
            L1_SwapInfo_List.append(T1)
            L1_RefPowerSpreadFlag_List.append(PS01)
            L1_RefPowerSpreadMat_List.append(T1)
            L1_RefPowerSpreadMat_List.append(T2)

        #L2, Leg2
        L2_RangeAccrualFlag = int(str(vb_L2_RAFlag.get(vb_L2_RAFlag.curselection())).split(":")[0]) if vb_L2_RAFlag.curselection() else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else 0
        
        L2_RCap = float(v_L2_RCap.get())/100 if len(str(v_L2_RCap.get())) > 0 else 10000
        L2_RFloor = float(v_L2_RFloor.get()) if len(str(v_L2_RFloor.get())) > 0 else -10000
        L2_RangeMultiple = float(v_L2_RangeMultiple.get()) if len(str(v_L2_RangeMultiple.get())) > 0 else 0
        L2_PayoffMultiple = splitfunc(str(v_L2_PayoffMultiple.get(v_L2_PayoffMultiple.curselection())).split(":")[1]) if v_L2_PayoffMultiple.curselection() else 0

        ScheduleDF_Leg2 = get_from_sheetinterface(sht_Leg2ScheduleInfo)
        if ScheduleDF_Leg2['기산일'].apply(lambda x : x == '').sum() == len(ScheduleDF_Leg2) : 
            ScheduleDF_Leg2['기산일'] = ScheduleDF_Leg2['Reset Start']
        if ScheduleDF_Leg2['기말일'].apply(lambda x : x == '').sum() == len(ScheduleDF_Leg2) : 
            ScheduleDF_Leg2['기말일'] = ScheduleDF_Leg2['Reset End']
        ScheduleDF_Leg2["고정쿠폰(%)"] = ScheduleDF_Leg2["고정쿠폰(%)"].apply(lambda x : 0 if str(x) == '' or 'nan' in str(x).lower() else x)
        ScheduleDF_Leg2["구조화금리적용"] = ScheduleDF_Leg2["구조화금리적용"].apply(lambda x : 0 if str(x) == '' or 'nan' in str(x).lower() else x)
        ScheduleDF_Leg2["RangeCpn"] = ScheduleDF_Leg2["RangeCpn"].apply(lambda x : 0 if str(x) == '' or 'nan' in str(x).lower() else x)

        ScheduleData_Leg2 = ScheduleDF_Leg2[["Reset Start","Reset End","기산일","기말일","지급일"]]
        PaymentDate_Leg2 = ScheduleData_Leg2['지급일'].values
        NCF_Leg2 = len(ScheduleData_Leg2)
        Schedule_Leg2 = ScheduleData_Leg2.T.values.astype(np.int64).reshape(-1)
        CPN_Leg2 = ScheduleDF_Leg2["고정쿠폰(%)"].astype(np.float64).values/100
        StructuredSlope_Leg2 = ScheduleDF_Leg2["구조화금리적용"].astype(np.float64).values
        RangeCpn_Leg2 = ScheduleDF_Leg2["RangeCpn"].astype(np.float64).values/100
        CouponFixRate_Leg2 = np.array(list(CPN_Leg2) + list(StructuredSlope_Leg2) + list(RangeCpn_Leg2), dtype = np.float64)
        L2_UsingCurveNum = np.array(RefRateCurveNum_L2)[np.array(RefRateCurveNum_L2) > 0 ]
        L2_NRefRateCurve = len(L2_UsingCurveNum)
        L2_FloatFlag = (ScheduleDF_Leg2["구조화금리적용"].astype(np.float64).values != 0).sum() > 0
        L2_MaxLoss = 100
        L2_MaxRet = 100
        L2_Flag_Ary = np.array([L2_NRefRateCurve, L2_FloatFlag, L2_RangeAccrualFlag, 0], dtype = np.int64)
        L2_MaxLossReturn_Ary = np.array([L2_MaxLoss, L2_MaxRet], dtype = np.float64)
        L2_RefCurveNumber_List = []
        L2_RefRateType_List = []
        L2_SwapInfo_List = []
        L2_DayCount_Ary = np.array([L2_DayCount, L2_DayCount, L2_DayCount, L2_DayCount],dtype = np.int64)
        L2_RefCondMultiple_Ary = np.array([L2_RangeMultiple, L2_RangeMultiple, L2_RangeMultiple], dtype = np.float64)
        L2_RefPowerSpreadFlag_List = []
        L2_RefPowerSpreadMat_List = []
        L2_RefRange_Ary = np.array([L2_RCap, L2_RFloor, L2_RCap, L2_RFloor, L2_RCap, L2_RFloor], dtype = np.float64)
        L2_PayoffMultiple_Ary = np.array([L2_PayoffMultiple, L2_PayoffMultiple, L2_PayoffMultiple])
        for i in range(4) :
            L2_RefRateType_List.append(1)
            if i > len(L2_UsingCurveNum) - 1 : 
                L2_RefCurveNumber_List.append(L2_RefCurveNumber_List[i-1])
            else : 
                L2_RefCurveNumber_List.append(L2_UsingCurveNum[i])
            if i == 3 : 
                L2_RefCurveNumber_List.append(DiscCurveIdx_L2[0])

        L2_RefCurveNumber = np.array(L2_RefCurveNumber_List, dtype = np.int64)        
        
        for i in range(3) : 
            idx = int(L2_RefCurveNumber[i]-1)
            NCPN = NCPNRefRate_L2[idx]
            T1 = PowerSpreadMaturity_L2[idx * i]
            T2 = PowerSpreadMaturity_L2[idx * i + 1]
            PS01 = PowerSpreadFlag_L2[idx]
            L2_SwapInfo_List.append(NCPN)
            L2_SwapInfo_List.append(T1)
            L2_RefPowerSpreadFlag_List.append(PS01)
            L2_RefPowerSpreadMat_List.append(T1)
            L2_RefPowerSpreadMat_List.append(T2)

        NHWVolCountList = []
        HWVolTermList = []
        HWVolList = []
        HWVolList2 = []
        NZeroRate = []
        ZeroTerm = []
        ZeroRate = []
        ZeroCurveName = []
        HWKappaArray = np.ones(17, dtype = np.float64) * 0.01
        HWQuantoInfo = np.ones(17, dtype = np.float64) * 0
        for i in range(4) :
            df = ResultDataList[min(i,len(ResultDataList) - 1)].applymap(lambda x : np.nan if str(x) == '' else x).dropna(axis = 0, how = 'all')
            n = len(df)
            Term = list(df["Term"].astype(np.float64).values) if "OptMat" not in df.columns else list(df["OptMat"].astype(np.float64).values)
            Preprocessing_Term(Term, PriceDate)
            NHWVolCountList.append(n)
            HWVolTermList += Term
            HWVolList += list(df["HWVol"].astype(np.float64).values)
            HWVolList2 += list(df["HWVol2F"].astype(np.float64).values)
            HWKappaArray[i] = float(df['HWKappa'].iloc[0])
            HWKappaArray[i + 4] = float(df['HWKappa2F'].iloc[0])
            HWKappaArray[i + 8] = float(df['Rho'].iloc[0])
            HWQuantoInfo[i] = QuantoUseFlag[min(i, len(QuantoUseFlag) - 1)]
            HWQuantoInfo[i + 4] = QuantoCorr[min(i, len(QuantoCorr) - 1)]
            HWQuantoInfo[i + 8] = QuantoFXVol[min(i, len(QuantoFXVol) - 1)]
            nz = len(ZeroTermList[min(i, len(ZeroTermList) - 1)])
            NZeroRate.append(nz)
            ZeroTerm += list(ZeroTermList[min(i, len(ZeroTermList) - 1)])
            ZeroRate += list(ZeroRateList[min(i, len(ZeroTermList) - 1)])
            ZeroCurveName += [str(i+1) + '번커브'] * nz

        OptionFlag = int(str(vb_OptionFlag.get(vb_OptionFlag.curselection())).split(":")[0]) if vb_OptionFlag.curselection() else 0    
        OptSchd = get_from_sheetinterface(sht_OptScheduleInfo)
        OptSchd["옵션행사일"] = OptSchd["옵션행사일"].apply(lambda x : str(x).replace("-","").replace(".0",""))
        OptionPayDate = np.array(list(OptSchd["옵션행사일"].values.astype(np.int64)), dtype = np.int64)
        NOption = len(OptionPayDate)
        OptionDateAndFlag = list(OptionPayDate) + [2] + [1 if OptionFlag == 0 else 0] + [0]
        OptionKAndRange = np.ones(7 * NOption)
        OptionKAndRange[NOption * 2 : NOption * 3] = 0
        OptionKAndRange[NOption * 4 : NOption * 5] = 0
        OptionKAndRange[NOption * 6 : NOption * 7] = 0
        RefRateHistoryData = get_from_sheetinterface(RefRateHistory)
        nhist = len(RefRateHistoryData)
        NDayHist_L1 = np.array([nhist,nhist,nhist], dtype = np.int64)
        NDayHist_L2 = np.array([nhist,nhist,nhist], dtype = np.int64)

        RateHistDate_L1 = list(RefRateHistoryData["Date"].apply(lambda x : str(x).replace("-","")).astype(np.int64).values) * 3
        RateHistDate_L2 = list(RefRateHistoryData["Date"].apply(lambda x : str(x).replace("-","")).astype(np.int64).values) * 3
        if numc <= 1 :             
            RateHist_L1 = list(RefRateHistoryData["Rate(Leg1)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100) * 3
            RateHist_L2 = list(RefRateHistoryData["Rate(Leg2)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100) * 3
        else : 
            RateHist_L1_1 = list(RefRateHistoryData["Rate1(Leg1)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100)
            RateHist_L2_1 = list(RefRateHistoryData["Rate1(Leg2)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100)
            RateHist_L1_2 = list(RefRateHistoryData["Rate2(Leg1)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100)
            RateHist_L2_2 = list(RefRateHistoryData["Rate2(Leg2)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100)
            RateHist_L1_3 = list(RefRateHistoryData["Rate3(Leg1)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100) if numc >= 3 else RateHist_L1_2
            RateHist_L2_3 = list(RefRateHistoryData["Rate3(Leg2)"].apply(lambda x : str(x).replace("-","") if len(str(x)) > 0 else '0').astype(np.float64).values/100) if numc >= 3 else RateHist_L2_2
            RateHist_L1 = RateHist_L1_1 + RateHist_L1_2 + RateHist_L1_3
            RateHist_L2 = RateHist_L2_1 + RateHist_L2_2 + RateHist_L2_3

        NSimul = 10000
        GreekTextFlag = np.array([GreekFlag, TextFlag], dtype = np.int64)
        ResultPrice = np.zeros(sum(NZeroRate) * 2 + 32 + sum(NHWVolCountList), dtype = np.float64)
        
        ResultL1 = np.zeros(7 * NCF_Leg1, dtype = np.float64)
        ResultL2 = np.zeros(7 * NCF_Leg2, dtype = np.float64)

        loggstr = []
        Error = "00000000000000000000000000000000000000000000000000"

        PriceDate_c = ct.c_long(PriceDate)
        NAFlag_c = ct.c_long(NominalFlag)
        Notional_c = ct.c_double(Nominal)
        PayoffStructure_np, PayoffStructure_c = arr_long(PayoffStructure)
        HolidayFlagCount_np, HolidayFlagCount_c = arr_long(HolidayFlagCount)

        Holidays_np, Holidays_c = arr_long(Holidays)
        RcvFlag_np, RcvFlag_c = arr_long(L1_Flag_Ary)
        RcvMaxLossReturn_np, RcvMaxLossReturn_c = arr_double(L1_MaxLossReturn_Ary)
        RcvRefCurveNumber_np, RcvRefCurveNumber_c = arr_long(L1_RefCurveNumber)
        RcvRefRateType_np, RcvRefRateType_c = arr_long(np.array(L1_RefRateType_List, dtype = np.int64))

        RcvSwapInfo_np, RcvSwapInfo_c = arr_double(np.array(L1_SwapInfo_List, dtype = np.float64))        
        RcvDayCountFlag_np, RcvDayCountFlag_c = arr_long(L1_DayCount_Ary)
        RcvRefCondMultiple_np, RcvRefCondMultiple_c = arr_double(L1_RefCondMultiple_Ary)
        RcvRefPowerSpreadFlag_np, RcvRefPowerSpreadFlag_c = arr_long(np.array(L1_RefPowerSpreadFlag_List, dtype = np.int64))
        RcvRefPowerSpreadMat_np, RcvRefPowerSpreadMat_c = arr_double(np.array(L1_RefPowerSpreadMat_List, dtype = np.float64))

        RcvRefRange_np, RcvRefRange_c = arr_double(L1_RefRange_Ary)
        RcvPayoffMultiple_np, RcvPayoffMultiple_c = arr_double(L1_PayoffMultiple_Ary)
        NRcvCashFlow_c = ct.c_long(NCF_Leg1)
        RcvCashFlowSchedule_np, RcvCashFlowSchedule_c = arr_long(Schedule_Leg1)
        RcvCouponFixRate_np, RcvCouponFixRate_c = arr_double(CouponFixRate_Leg1)

        PayFlag_np, PayFlag_c = arr_long(L2_Flag_Ary)
        PayMaxLossReturn_np, PayMaxLossReturn_c = arr_double(L2_MaxLossReturn_Ary)
        PayRefCurveNumber_np, PayRefCurveNumber_c = arr_long(L2_RefCurveNumber)
        PayRefRateType_np, PayRefRateType_c = arr_long(np.array(L2_RefRateType_List, dtype = np.int64))
        PaySwapInfo_np, PaySwapInfo_c = arr_double(np.array(L2_SwapInfo_List, dtype = np.float64))        

        PayDayCountFlag_np, PayDayCountFlag_c = arr_long(L2_DayCount_Ary)
        PayRefCondMultiple_np, PayRefCondMultiple_c = arr_double(L2_RefCondMultiple_Ary)
        PayRefPowerSpreadFlag_np, PayRefPowerSpreadFlag_c = arr_long(np.array(L2_RefPowerSpreadFlag_List, dtype = np.int64))
        PayRefPowerSpreadMat_np, PayRefPowerSpreadMat_c = arr_double(np.array(L2_RefPowerSpreadMat_List, dtype = np.float64))
        PayRefRange_np, PayRefRange_c = arr_double(L2_RefRange_Ary)

        PayPayoffMultiple_np, PayPayoffMultiple_c = arr_double(L2_PayoffMultiple_Ary)
        NPayCashFlow_c = ct.c_long(NCF_Leg2)
        PayCashFlowSchedule_np, PayCashFlowSchedule_c = arr_long(Schedule_Leg2)
        PayCouponFixRate_np, PayCouponFixRate_c = arr_double(CouponFixRate_Leg2)
        NHWVolCount_np, NHWVolCount_c = arr_long(np.array(NHWVolCountList, dtype = np.int64))

        HWVolTermArray_np, HWVolTermArray_c = arr_double(np.array(HWVolTermList, dtype = np.float64))                
        HWVolArray_np, HWVolArray_c = arr_double(np.array(HWVolList, dtype = np.float64))        
        HWKappaArray_np, HWKappaArray_c = arr_double(HWKappaArray)
        NZeroRate_np, NZeroRate_c = arr_long(NZeroRate)
        ZeroTerm_np, ZeroTerm_c = arr_double(np.array(ZeroTerm, dtype = np.float64))

        ZeroRate_np, ZeroRate_c = arr_double(np.array(ZeroRate, dtype = np.float64))
        Corr_np, Corr_c = arr_double(CorrMatrixReshaped)
        NDayHistRcv_np, NDayHistRcv_c = arr_long(NDayHist_L1)
        RateHistDateRcv_np, RateHistDateRcv_c = arr_long(RateHistDate_L1)
        RateHistRcv_np, RateHistRcv_c = arr_double(RateHist_L1)

        NDayHistPay_np, NDayHistPay_c = arr_long(NDayHist_L2)
        RateHistDatePay_np, RateHistDatePay_c = arr_long(RateHistDate_L2)
        RateHistPay_np, RateHistPay_c = arr_double(RateHist_L2)
        NSimul_c = ct.c_long(NSimul)
        GreekTextFlag_np, GreekTextFlag_c = arr_long(GreekTextFlag)
        GreekTextForGreek_np, GreekTextForGreek_c = arr_long(np.array([0,0], dtype = np.int64))

        NOption_c = ct.c_long(NOption)
        OptionDateAndFlag_np, OptionDateAndFlag_c = arr_long(OptionDateAndFlag)
        OptionKAndRange_np, OptionKAndRange_c = arr_double(OptionKAndRange)
        ResultPrice_np, ResultPrice_c = arr_double(ResultPrice)
        ResultRcv_np, ResultRcv_c = arr_double(ResultL1)

        ResultPay_np, ResultPay_c = arr_double(ResultL2)
        HWFactorFlag_c = ct.c_long(HW2FFlag)        
        HWVolArray2_np, HWVolArray2_c = arr_double(np.array(HWVolList2, dtype = np.float64))        
        HWQuantoInfo_np, HWQuantoInfo_c = arr_double(HWQuantoInfo)
        Error_c = ct.create_string_buffer(60)

        if TextFlag > 0 : 
            loggstr.append(str(PriceDate))
            loggstr.append(str(NominalFlag))
            loggstr.append(str(Nominal))
            loggstr.append(str(PayoffStructure))
            loggstr.append(str(HolidayFlagCount))

            loggstr.append(str(Holidays))
            loggstr.append(str(L1_Flag_Ary))
            loggstr.append(str(L1_MaxLossReturn_Ary))
            loggstr.append(str(L1_RefCurveNumber))
            loggstr.append(str(L1_RefRateType_List))

            loggstr.append(str(L1_SwapInfo_List))
            loggstr.append(str(L1_DayCount_Ary))
            loggstr.append(str(L1_RefCondMultiple_Ary))
            loggstr.append(str(L1_RefPowerSpreadFlag_List))
            loggstr.append(str(L1_RefPowerSpreadMat_List))

            loggstr.append(str(L1_RefRange_Ary))
            loggstr.append(str(L1_PayoffMultiple_Ary))
            loggstr.append(str(NCF_Leg1))
            loggstr.append(str(Schedule_Leg1))
            loggstr.append(str(CouponFixRate_Leg1))

            loggstr.append(str(L2_Flag_Ary))
            loggstr.append(str(L2_MaxLossReturn_Ary))
            loggstr.append(str(L2_RefCurveNumber))
            loggstr.append(str(L2_RefRateType_List))
            loggstr.append(str(L2_SwapInfo_List))

            loggstr.append(str(L2_DayCount_Ary))
            loggstr.append(str(L2_RefCondMultiple_Ary))
            loggstr.append(str(L2_RefPowerSpreadFlag_List))
            loggstr.append(str(L2_RefPowerSpreadMat_List))
            loggstr.append(str(L2_RefRange_Ary))

            loggstr.append(str(L2_PayoffMultiple_Ary))
            loggstr.append(str(NCF_Leg2))
            loggstr.append(str(Schedule_Leg2))
            loggstr.append(str(CouponFixRate_Leg2))
            loggstr.append(str(NHWVolCountList))

            loggstr.append(str(HWVolTermList))
            loggstr.append(str(HWVolList))
            loggstr.append(str(HWKappaArray))
            loggstr.append(str(NZeroRate))
            loggstr.append(str(ZeroTerm))

            loggstr.append(str(ZeroRate))
            loggstr.append(str(CorrMatrixReshaped))
            loggstr.append(str(NDayHist_L1))
            loggstr.append(str(RateHistDate_L1))
            loggstr.append(str(RateHist_L1))

            loggstr.append(str(NDayHist_L2))
            loggstr.append(str(RateHistDate_L2))
            loggstr.append(str(RateHist_L2))
            loggstr.append(str(NSimul))
            loggstr.append(str(GreekTextFlag))

            loggstr.append(str(NOption))
            loggstr.append(str(OptionDateAndFlag))
            loggstr.append(str(OptionKAndRange))
            loggstr.append(str(ResultPrice))
            loggstr.append(str(ResultL1))

            loggstr.append(str(ResultL2))
            loggstr.append(str(HW2FFlag))
            loggstr.append(str(HWVolList2))
            loggstr.append(str(HWQuantoInfo))
            loggstr.append(str(Error))
            pd.DataFrame(loggstr).to_excel("IRPhaseStructuredSwap_Variables.xlsx")
        Res = CalcFunc(PriceDate_c,NAFlag_c,Notional_c,PayoffStructure_c,HolidayFlagCount_c,
                       Holidays_c,RcvFlag_c,RcvMaxLossReturn_c,RcvRefCurveNumber_c,RcvRefRateType_c,
                       RcvSwapInfo_c,RcvDayCountFlag_c,RcvRefCondMultiple_c,RcvRefPowerSpreadFlag_c,RcvRefPowerSpreadMat_c,
                       RcvRefRange_c,RcvPayoffMultiple_c,NRcvCashFlow_c,RcvCashFlowSchedule_c,RcvCouponFixRate_c,
                       PayFlag_c,PayMaxLossReturn_c,PayRefCurveNumber_c,PayRefRateType_c,PaySwapInfo_c,
                       PayDayCountFlag_c,PayRefCondMultiple_c,PayRefPowerSpreadFlag_c,PayRefPowerSpreadMat_c,PayRefRange_c,
                       PayPayoffMultiple_c,NPayCashFlow_c,PayCashFlowSchedule_c,PayCouponFixRate_c,NHWVolCount_c,
                       HWVolTermArray_c,HWVolArray_c,HWKappaArray_c,NZeroRate_c,ZeroTerm_c,
                       ZeroRate_c,Corr_c,NDayHistRcv_c,RateHistDateRcv_c,RateHistRcv_c,
                       NDayHistPay_c,RateHistDatePay_c,RateHistPay_c,NSimul_c,GreekTextFlag_c,
                       NOption_c,OptionDateAndFlag_c,OptionKAndRange_c,ResultPrice_c,ResultRcv_c,
                       ResultPay_c,HWFactorFlag_c,HWVolArray2_c,HWQuantoInfo_c,Error_c)        
        Rcv = np.round(ResultPrice_c[0], 2)
        Pay = np.round(ResultPrice_c[1], 2)
        MTM = np.round(ResultPrice_c[2], 2)
        Opt = np.round(ResultPrice_c[3], 2)
        NRf = sum(NZeroRate)
        nmlst = []
        for i in range(len(NZeroRate)) : 
            nmlst += [CvName[min(len(CvName)-1,i)]] * NZeroRate[i]

        KeyRcvPV01 = np.ctypeslib.as_array(ResultPrice[12:12 + NRf], shape = (NRf))
        KeyPayPV01 = np.ctypeslib.as_array(ResultPrice[12 + NRf:12 + 2*NRf], shape = (NRf)) * -1        
        greek = pd.DataFrame([nmlst,ZeroTerm_np, KeyRcvPV01 + KeyPayPV01], index = ['커브명','테너','민감도']).T
        if TextFlag == 1 : 
            greek.to_excel("IRPhaseStructuredSwap_민감도산출데이터.xlsx")        
        HWVega = np.ctypeslib.as_array(ResultPrice[12 + 2*NRf:12 + 2*NRf + sum(NHWVolCountList)], shape = (sum(NHWVolCountList), ))
        RW_GIRR = 0.012020815 
        RW_CSR = 0#CSRRW[GreekFlag - 1] 
        Sensi = (KeyRcvPV01.sum() + KeyPayPV01.sum())/0.0001
        GIRRRWSensi = np.round(Sensi * RW_GIRR * 0.8)
        CSRRWSensi = np.round(Sensi * RW_CSR* 0.8)
        GIRRVega = np.round((np.array(HWVega)/0.0001 * (HWVolArray_np/2 + HWVolArray2_np/2)[:sum(NHWVolCountList)]).sum() * 0.9, 2)
        RWA = np.round((GIRRRWSensi + GIRRVega) * 12.5, 2)
        RWA_Pct = np.round(RWA/Nominal, 4)
        Res_L1 = pd.DataFrame(np.ctypeslib.as_array(ResultRcv_c, shape = (6 * NCF_Leg1, )).reshape(6, -1).T, columns = ['금리1','금리2','금리3','E(Accraul)','E(지급쿠폰)','E(DF)'])
        Res_L1['지급일'] = PaymentDate_Leg1
        Res_L1 = Res_L1[['지급일','금리1','금리2','금리3','E(Accraul)','E(지급쿠폰)','E(DF)']]
        Res_L1.columns = [['Leg1'] * len(Res_L1.columns), Res_L1.columns]
        Res_L2 = pd.DataFrame(np.ctypeslib.as_array(ResultPay_c, shape = (6 * NCF_Leg2, )).reshape(6, -1).T, columns = ['금리1','금리2','금리3','E(Accraul)','E(지급쿠폰)','E(DF)'])
        Res_L2['지급일'] = PaymentDate_Leg2
        Res_L2 = Res_L2[['지급일','금리1','금리2','금리3','E(Accraul)','E(지급쿠폰)','E(DF)']]
        Res_L2.columns = [['Leg2'] * len(Res_L2.columns), Res_L2.columns]
        ResultData = pd.concat([Res_L1, Res_L2],axis = 1)
        output_label.config(text = f"산출결과: 에러여부 : \n{Error_c.value.decode("utf-8")}\nRcv : \n{Rcv}\nPay : \n{Pay}\nNetValue : \n{MTM}\nOption : \n{Opt}\nGIRR Delta, Vega : \n{GIRRRWSensi}, {GIRRVega}\n RWA : \n{RWA}({RWA_Pct * 100})%", font = ("맑은 고딕", 12, 'bold'))                       
        Res = pd.DataFrame([])
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(main_frame)
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

        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultData, width = 100)

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2      
        MyArrays[4] = Res_L1
        MyArrays[5] = Res
        #df.to_excel("ResultExcel.xlsx",index = False, header=False)
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    run_button = tk.Button(
        left_frame,
        text="MarketData확인",
        command=lambda: open_result_window(root),
        font = ("맑은 고딕",12,'bold')
    )

    #run_button2 = tk.Button(
    #    left_frame2,
    #    text="PowerSpread 사용",
    #    command=lambda: open_powerspread_window(root, PowerSpreadFlag_L1, PowerSpreadMaturity_L1),
    #    font = ("맑은 고딕",12,'bold')
    #)

    #run_button3 = tk.Button(
    #    left_frame5,
    #    text="PowerSpread 사용",
    #    command=lambda: open_powerspread_window(root, PowerSpreadFlag_L2, PowerSpreadMaturity_L2),
    #    font = ("맑은 고딕",12,'bold')
    #)    

    run_button.pack()
    run_button2.pack()
    run_button3.pack()

    root.mainloop() 
    return MyArrays[5]

if __name__ == '__main__' : 
    for i in range(10) : 
        n = MainViewer(Title = 'Viewer', MyText = '사용하실 기능은?(번호입력)', MyList = ["1: IRStructured Swap(Callable Bond)","2: IRS", "3: Structured Swap HWSimul", "4: CDS Pricing"], size = "800x450+30+30", splitby = ":", listheight = 8, textfont = 13, titlelable = False, titleName = "Name", MultiSelection = False, defaultvalue = 0, addtreeflag = False, treedata = pd.DataFrame([]), DefaultStringList = [], width = 95, expand = True)
        if n == 1 : 
            IRS_Callable()
        elif n == 2 : 
            IRSPricing()
        elif n == 3 : 
            IRPhaseStructuredSwap()
        elif n == 4 : 
            CalcCDS()
        else : 
            break


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
