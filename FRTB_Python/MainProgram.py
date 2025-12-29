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
from packaging import version
from Utility import Linterp, Linterp2D, DayCountAtoB, YYYYMMDDToExcelDate, ExcelDateToYYYYMMDD, DayCountFractionAtoB, MappingCouponDates, EDate_YYYYMMDD, malloc_cpn_date_holiday, DayPlus, MonthCountAtoB, KoreaHolidaysFromStartToEnd, USHolidaysFromStartToEnd, BusinessDateArrayFromAtoB, ReadCSV, NBusinessCountFromEndToPay, ParseBusinessDateIfHoliday, NextNthBusinessDate, MapProductType, Calc_ZeroRate_FromDiscFactor, CalcZeroRateFromSwapPoint, Generate_OptionDate
from RiskModule import MapGIRRDeltaGreeks, MapCSRDeltaGreeks, MapEquityRiskWeight, EQDeltaRWMappingDF, Calc_GIRRDeltaNotCorrelated_FromGreeks, Calc_CSRDeltaNotCorrelated_FromGreeks, Calc_FXRDelta, HighLiquidCurrency, PreProcessingMyData, PreProcessingBankData, AggregatedFRTB_RiskCharge, Calc_GIRRDeltaNotCorrelated_FromGreeks_PreProcessing, GIRR_DeltaRiskWeight, Calc_GIRRVega, MapGIRRVegaGreeks
from Pricing import Preprocessing_Term, Preprocessing_ZeroTermAndRate, BS_Option, BSBarrierOption, BSDigitalOption, Arithmetic_Asian_Opt_Pricing_Preprocessing, Pricing_CapFloor, BS_Swaption, Calc_Schedule_ErrorCheck, Calc_Bond_PV01, Calc_IRS_PV01, Calc_Value_FXSwap, CalC_CRS_PV01, Calc_CRS, Calc_IRS, FindSwaptionImpliedVolatility, B_s_to_t, Calc_ForwardDiscount_Factor, HullWhiteCalibration1Factor, Pricing_IRCallableSwap_HWFDM, Pricing_IRCallableSwap_HWFDM_Greek, Pricing_RangeAccrualBond, CapFloorToImpliedVol, BS_Price_To_ImpliedVolatility
from GraphicInterface import make_variable_interface, make_listvariable_interface, make_multilistvariable_interface, insert_dataframe_to_treeview
import requests
# JIT은 쓰지말자
#from numba import jit
import warnings
import os

PrevTreeFlag = 0
tree = None
currdir = os.getcwd()
warnings.filterwarnings('ignore')
vers = "1.2.2"
recentupdate = '20251221'
print("######################################\nCreated By Daesun Lim (CIIA(R), FRM(R))\nRisk Validation Quant\nMy FRTB Module \n"+vers+" (RecentUpdated :" +recentupdate + ")" + "\n######################################\n")
BASE_URL = "https://finance.naver.com/marketindex/exchangeDailyQuote.nhn" # 환율 크롤링주소
HEADERS = {"User-Agent": "Mozilla/5.0"}
URLIRS = "https://www.kmbco.com/kor/rate/deri_rate.do"
HEADERSIRS = {"User-Agent": "Mozilla/5.0"}
BASECD = "https://finance.naver.com/marketindex/interestDailyQuote.nhn"
HEADERSCD = {"User-Agent": "Mozilla/5.0"}

def termratestr(term, rate) : 
    lst = []
    for x, y in zip(term, rate) : 
        TempString = (str(np.round(x,6)) + '   ')[:7] + '|' + (str(np.round(float(y),7)) + '000')[:6]
        lst.append(TempString[-20:])
    #return [str(np.round(x,4)) + '|' + str(y) for x, y in zip(term, rate)]
    return lst

def FileListPrint(currdir) : 
    files = os.listdir(currdir)
    FileList = np.array(files)[np.vectorize(lambda x : True if ("raw" in str(x).lower()) or ("girr" in str(x).lower()) or ("csr" in str(x).lower()) or ("fxr" in str(x).lower())or ("eqr" in str(x).lower())or ("comr" in str(x).lower()) else False)(files)]
    filenum, filenames, filenamesprint = [], [], []
    k = 1
    for name in FileList : 
        if '.' not in name : 
            newdir = currdir + '\\' + name 
            files2 = os.listdir(newdir)
            FileList2 = np.array(files2)[np.vectorize(lambda x : True if ("raw" in str(x).lower()) or ("girr" in str(x).lower()) or ("csr" in str(x).lower()) or ("fxr" in str(x).lower())or ("eqr" in str(x).lower())or ("comr" in str(x).lower()) else False)(files2)]
            for name2 in FileList2 : 
                if '.pia' not in name2 : 
                    filenum.append(k)
                    filenames.append(newdir + '\\' + name2)
                    filenamesprint.append(str(k) + '. ' + newdir + '\\' + name2)
                    k += 1
        else : 
            if '.pia' not in name : 
                filenum.append(k)
                filenames.append(currdir + '\\' + name)
                filenamesprint.append(str(k) + '. ' + currdir + '\\' + name)
                k += 1
    return pd.DataFrame([filenum,filenames,filenamesprint],index = ["Number","Directory","DirectoryPrint"]).T   

def MarketDataFileListPrint(currdir, namein = "", namenotin = "", namenotin2 = "") : 
    files = os.listdir(currdir) 
    YYYYMMDD, filenum, folder, filenames, filenamesprint = [], [], [], [], []
    k = 1
    for name in files : 
        if "." not in name : 
            newdir = currdir + '\\' + name
            files2 = os.listdir(newdir)
            for name2 in files2 : 
                if '.pia' not in str(name2) : 
                    if '.' not in name : 
                        newdir2 = newdir + '\\' + name2
                        files3 = os.listdir(newdir2)
                        for name3 in files3 : 
                            if len(str(namein)) == 0 and len(str(namenotin)) == 0: 
                                filenum.append(k)
                                folder.append(newdir2)
                                filenames.append(newdir2 + '\\' + name3)
                                filenamesprint.append(str(k) + ". " + newdir2 + "\\" + name3)
                                YYYYMMDD.append(name)
                                k += 1
                            elif len(str(namein)) == 0 and len(str(namenotin)) > 0 : 
                                if len(str(namenotin2)) == 0 : 
                                    if str(namenotin).lower() not in name3.lower() : 
                                        filenum.append(k)
                                        folder.append(newdir2)
                                        filenames.append(newdir2 + '\\' + name3)
                                        filenamesprint.append(str(k) + ". " + newdir2 + "\\" + name3)
                                        YYYYMMDD.append(name)
                                        k += 1    
                                else :
                                    if str(namenotin).lower() not in name3.lower() and str(namenotin2).lower() not in name3.lower() : 
                                        filenum.append(k)
                                        folder.append(newdir2)
                                        filenames.append(newdir2 + '\\' + name3)
                                        filenamesprint.append(str(k) + ". " + newdir2 + "\\" + name3)
                                        YYYYMMDD.append(name)
                                        k += 1    
                            else : 
                                if str(namein).lower() in name3.lower() : 
                                    filenum.append(k)
                                    folder.append(newdir2)
                                    filenames.append(newdir2 + '\\' + name3)
                                    filenamesprint.append(str(k) + ". " + newdir2 + "\\" + name3)
                                    YYYYMMDD.append(name)
                                    k += 1                                
                    else : 
                        if len(str(namein)) == 0 and len(str(namenotin)) == 0:                         
                            filenum.append(k)
                            folder.append(newdir)
                            filenames.append(newdir + '\\' + name2)
                            filenamesprint.append(str(k) + ". " + newdir + '\\' + name2)
                            YYYYMMDD.append(name)
                            k += 1
                        elif len(str(namein)) == 0 and len(str(namenotin)) > 0:
                            if len(str(namenotin2)) == 0 : 
                                if str(namenotin).lower() not in name2.lower() : 
                                    filenum.append(k)
                                    folder.append(newdir)
                                    filenames.append(newdir + '\\' + name2)
                                    filenamesprint.append(str(k) + ". " + newdir + '\\' + name2)
                                    YYYYMMDD.append(name)
                                    k += 1                                                            
                            else :
                                if str(namenotin).lower() not in name2.lower() and str(namenotin2).lower() not in name2.lower(): 
                                    filenum.append(k)
                                    folder.append(newdir)
                                    filenames.append(newdir + '\\' + name2)
                                    filenamesprint.append(str(k) + ". " + newdir + '\\' + name2)
                                    YYYYMMDD.append(name)
                                    k += 1                                                            
                        else : 
                            if str(namein).lower() in name2.lower() : 
                                filenum.append(k)
                                folder.append(newdir)
                                filenames.append(newdir + '\\' + name2)
                                filenamesprint.append(str(k) + ". " + newdir + '\\' + name2)
                                YYYYMMDD.append(name)
                                k += 1                            
    Result = pd.DataFrame([YYYYMMDD, filenum, folder, filenames, filenamesprint], index = ["YYYYMMDD","Number","Folder","Directory","DirectoryPrint"]).T
    return Result

def UsedMarketDataSetToPricing(MarketDataDir, FixedDate = "TEMPSTRING", namein = "", namenotin = "", Comments = "", MainComments = "", MultiSelection = True, defaultvalue = 0, DefaultStringList = [], namenotin2 = "") : 
    Data = MarketDataFileListPrint(MarketDataDir, namein ,namenotin , namenotin2).sort_values(by = "YYYYMMDD")[-50:]
    
    GroupbyYYYYMMDD = Data.groupby("YYYYMMDD").first().reset_index()
    PrintDate = MainComments + "\n 다음 중 사용하실 MarketData 날짜를 고르세요. (번호선택)\n"
    FixedDateInFlag = 0
    n = 0
    for x, y in zip(GroupbyYYYYMMDD["Number"], GroupbyYYYYMMDD["YYYYMMDD"]) : 
        PrintDate += str(n+1) + ": " + str(y) + "\n"
        if FixedDate in str(y).lower() : 
            FixedDateInFlag = n
            break
        n = n + 1
    #if FixedDateInFlag == 0 : 
    #    DateMarketDataIdx = input(PrintDate + "-> ")
    #else : 
    #    DateMarketDataIdx = FixedDateInFlag + 1

    YYYYMMDD = MainViewer(Title = 'MarketData:Date', MyText = '사용하실 마켓데이터 날짜는?(번호입력)', MyList = list(GroupbyYYYYMMDD["YYYYMMDD"]), size = "800x450+30+30", splitby = ".", listheight = 8, textfont = 13, titlelable = False, titleName = "Name", defaultvalue=-1)        
    YYYYMMDD = str(YYYYMMDD)
    #YYYYMMDD = GroupbyYYYYMMDD["YYYYMMDD"].isin([TargetDate, str(TargetDate)])
    TargetFiles = Data[Data["YYYYMMDD"].isin([YYYYMMDD, int(YYYYMMDD)])].groupby("Directory").first().reset_index()

    if len(Comments) == 0 : 
        PrintMarketData = "\n 다음 중 사용하실 MarketData를 고르세요.(example : 1 || example2 : 1, 2, 3 와 같은 여러개 선택가능)\n"
        PrintComments = "다음 중 사용하실 MarketData를 고르세요." + ("\n(example : 1 || example2 : 1, 2, 3 와 같은 여러개 선택가능" if MultiSelection == True else "")
    else : 
        PrintMarketData = "\n" + Comments + "\n"
        PrintComments = Comments + "\n"
    TargetList = []
    for idxx, x in enumerate(TargetFiles["Directory"]) : 
        PrintMarketData += ' ' + str(idxx+1) +". "+ str(x) + "\n"
    DataMarketData = MainViewer(Title = 'Viewer', MyText = PrintComments, MyList = TargetFiles["DirectoryPrint"], size = "800x450+30+30", splitby = ".", listheight = 6, textfont = 13, titlelable = False, titleName = "Name", MultiSelection = MultiSelection, defaultvalue = defaultvalue, DefaultStringList = DefaultStringList)#input(PrintMarketData + '->')
    DataMarketData = str(DataMarketData)
    MarketDataList = []
    MarketDataName = []
    
    if len(DataMarketData) == 1 : 
        NumberList = DataMarketData.replace(" ","").split(",")
        idx = TargetFiles["Number"].astype(str).isin(NumberList)
        MarketDataList.append(ReadCSV(TargetFiles["Directory"][idx].iloc[0], True).dropna(how = 'all'))
        MarketDataName.append(TargetFiles["Directory"][idx].iloc[0])
    else : 
        NumberList = DataMarketData.replace(" ","").split(",")
        #for n in NumberList : 
            #TargetList.append(TargetFiles["Number"].iloc[int(n)-1])
        #    TargetFiles[TargetFiles["Number"].isin([int(n), str(n)])]
        #TargetFiles2 = TargetFiles[TargetFiles["Number"].astype(np.int64).isin(TargetList)]
        TargetFiles2 = TargetFiles[TargetFiles["Number"].astype(str).isin(NumberList)]
        for idx in range(len(TargetFiles2)) : 
            MarketDataList.append(ReadCSV(TargetFiles2["Directory"].iloc[idx], True))
            MarketDataName.append(TargetFiles2["Directory"].iloc[idx])
    
    for i in range(len(MarketDataList)) : 
        MarketDataList[i] = MarketDataList[i].dropna(how = 'all')#.applymap(lambda x : str(x).replace("-",""))
        if "Rate" in MarketDataList[i].columns and "Term" in MarketDataList[i].columns : 
            Term = list(MarketDataList[i]["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64))
            Rate = list(MarketDataList[i]["Rate"].astype(np.float64))
            PriceDate = int(str(MarketDataList[i]["PriceDate"].iloc[0]).replace("-",""))
            Preprocessing_Term(Term, int(PriceDate))
            MarketDataList[i]["Term"] = Term
            MarketDataList[i]["Rate"] = Rate
        elif "rate" in MarketDataList[i].columns and "term" in MarketDataList[i].columns : 
            Term = list(MarketDataList[i]["term"].apply(lambda x : str(x).replace("-","")).astype(np.float64))
            Rate = list(MarketDataList[i]["rate"].astype(np.float64))
            PriceDate = int(str(MarketDataList[i]["PriceDate"].iloc[0]).replace("-",""))
            Preprocessing_Term(Term, int(PriceDate))
            MarketDataList[i]["term"] = Term
            MarketDataList[i]["rate"] = Rate
        if "StartDate" in MarketDataList[i].columns : 
            MarketDataList[i]["StartDate"] = MarketDataList[i]["StartDate"].apply(lambda x : int(str(x).replace("-","")) if type(x) == str else (ExcelDateToYYYYMMDD(int(x)) if int(x) < 19000101 else int(x)))
        if "Maturity" in MarketDataList[i].columns : 
            MarketDataList[i]["Maturity"] = MarketDataList[i]["Maturity"].apply(lambda x : int(str(x).replace("-","")) if type(x) == str else (ExcelDateToYYYYMMDD(int(x)) if int(x) < 19000101 else int(x)))
        if "MarketQuote" in MarketDataList[i].columns : 
            MarketDataList[i]["MarketQuote"] = MarketDataList[i]["MarketQuote"].apply(lambda x : str(x).replace(",","")).astype(np.float64)
            
    return YYYYMMDD, MarketDataName, MarketDataList

def LoggingUsedFileNames(MyFiles, MyClass = 'FRTB') : 
    PrintStr = '\n'+MyClass+' 계산에 필요한 RAW 데이터 파일은 다음 중 무엇입니까?(번호입력)\n'
    n = 0
    for i in MyFiles["DirectoryPrint"] : 
        if MyClass.lower() in i.lower() : 
            PrintStr += i + str("\n")
            n += 1
    if n == 0 : 
        return ''
    else : 
        return PrintStr
    
def MainFunction(currdir = os.getcwd()) : 
    MyFiles = FileListPrint(currdir)
    MyFiles["RiskClass"] = MyFiles["DirectoryPrint"].apply(lambda x : 'girr' if 'girr' in x.lower() else (
                                                            'csr' if 'csr' in x.lower() else (
                                                                'fxr' if 'fx' in x.lower() else (
                                                                    'eqr' if 'eq' in x.lower() else (
                                                                        'comr' if 'com' in x.lower() else (
                                                                            'frtb' if 'frtb' in x.lower() else "None"))))))
    GIRRFiles = MyFiles[MyFiles["RiskClass"] == 'girr']
    CSRFiles = MyFiles[MyFiles["RiskClass"] == 'csr']
    EQRFiles = MyFiles[MyFiles["RiskClass"] == 'eqr']
    FXRFiles = MyFiles[MyFiles["RiskClass"] == 'fxr']
    COMRFiles = MyFiles[MyFiles["RiskClass"] == 'comr']
    FRTBTotalFiles = MyFiles[MyFiles["RiskClass"] == 'frtb']
    
    root = tk.Tk()
    root.title("FRTB Files")
    root.geometry("1000x750+30+30")
    root.resizable(False, False)
    GIRRFileSelection, CSRFileSelection, EQRFileSelection, FXRFileSelection, COMRFileSelection, FRTBFileSelection = None, None, None, None, None, None
    if len(FRTBTotalFiles) > 0 : 
        FRTBFilesLen = len(FRTBTotalFiles)
        left_frame = tk.Frame(root)
        left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
        FRTBFileSelection = make_listvariable_interface(left_frame, 'FRTB FileName\n(리스트에서 선택)', list(FRTBTotalFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if FRTBFilesLen > 0 else None
    else : 
        GIRRFilesLen = len(GIRRFiles)
        CSRFilesLen = len(CSRFiles)
        EQRFilesLen = len(EQRFiles)
        FXRFilesLen = len(FXRFiles)
        COMRFilesLen = len(COMRFiles)
        left_frame = tk.Frame(root)
        left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
        GIRRFileSelection = make_listvariable_interface(left_frame, 'GIRR FileName\n(리스트에서 선택)', list(GIRRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if GIRRFilesLen > 0 else None
        CSRFileSelection = make_listvariable_interface(left_frame, 'CSR FileName\n(리스트에서 선택)', list(CSRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if CSRFilesLen > 0 else None
        EQRFileSelection = make_listvariable_interface(left_frame, 'EQR FileName\n(리스트에서 선택)', list(EQRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if EQRFilesLen > 0 else None
        FXRFileSelection = make_listvariable_interface(left_frame, 'FXR FileName\n(리스트에서 선택)', list(FXRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if FXRFilesLen > 0 else None
        COMRFileSelection = make_listvariable_interface(left_frame, 'COMR FileName\n(리스트에서 선택)', list(COMRFiles["DirectoryPrint"]), listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, width = 90) if COMRFilesLen > 0 else None

    PrevTreeFlag = 0
    tree, scrollbar, scrollbar2 = None, None, None
    GIRRNumberArray = []
    CSRNumberArray = []
    EQRNumberArray = []
    FXRNumberArray = []
    COMRNumberArray = []
    FRTBNumberArray = []
    MyArray = [tree, PrevTreeFlag, scrollbar, scrollbar2]
    def run_function(GIRRNumberArray, CSRNumberArray, EQRNumberArray, FXRNumberArray, COMRNumberArray, FRTBNumberArray,MyArray) :
        if len(FRTBTotalFiles) > 0 : 
            FRTBNumber = int(str(FRTBFileSelection.get(FRTBFileSelection.curselection())).split(".")[0]) if FRTBFileSelection.curselection() else 0
            FRTBNumberArray.append(FRTBNumber)
        else : 
            GIRRNumber = int(str(GIRRFileSelection.get(GIRRFileSelection.curselection())).split(".")[0]) if GIRRFileSelection.curselection() else 0
            GIRRNumberArray.append(GIRRNumber)
            CSRNumber = int(str(CSRFileSelection.get(CSRFileSelection.curselection())).split(".")[0]) if CSRFileSelection.curselection() else 0
            CSRNumberArray.append(CSRNumber)
            EQRNumber = int(str(EQRFileSelection.get(EQRFileSelection.curselection())).split(".")[0]) if EQRFileSelection.curselection() else 0
            EQRNumberArray.append(EQRNumber)
            FXRNumber = int(str(FXRFileSelection.get(FXRFileSelection.curselection())).split(".")[0]) if FXRFileSelection.curselection() else 0
            FXRNumberArray.append(FXRNumber)
            COMRNumber = int(str(COMRFileSelection.get(COMRFileSelection.curselection())).split(".")[0]) if COMRFileSelection.curselection() else 0
            COMRNumberArray.append(COMRNumber)
        root.destroy()
    temp_function = lambda : run_function(GIRRNumberArray, CSRNumberArray, EQRNumberArray, FXRNumberArray, COMRNumberArray, FRTBNumberArray, MyArray)
    tk.Button(left_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_function, width = 15).pack()
    root.mainloop()            
    if len(FRTBTotalFiles) > 0 : 
        Data = ReadCSV(MyFiles[MyFiles["Number"] == FRTBNumberArray[-1]]["Directory"].iloc[0])
    else : 
        Data1 = ReadCSV(MyFiles[MyFiles["Number"] == GIRRNumberArray[-1]]["Directory"].iloc[0])
        Data2 = ReadCSV(MyFiles[MyFiles["Number"] == CSRNumberArray[-1]]["Directory"].iloc[0])
        Data3 = ReadCSV(MyFiles[MyFiles["Number"] == EQRNumberArray[-1]]["Directory"].iloc[0])
        Data4 = ReadCSV(MyFiles[MyFiles["Number"] == FXRNumberArray[-1]]["Directory"].iloc[0])
        Data5 = ReadCSV(MyFiles[MyFiles["Number"] == COMRNumberArray[-1]]["Directory"].iloc[0])
        Data = pd.concat([Data1, Data2, Data3, Data4, Data5],axis = 0)
    return Data

def ViewFRTB(Data) : 
    root = tk.Tk()
    root.title("FRTB Result")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    tree = ttk.Treeview(root)
    DataDF = Data.reset_index().applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
    tree.pack(padx=5, pady=5, fill="both", expand=True)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.configure(xscrollcommand=scrollbar2.set)
    scrollbar.pack(side="right", fill="y")    
    scrollbar2.pack(side="bottom", fill="x")    
    PrevTreeFlag = insert_dataframe_to_treeview(tree, DataDF, width = 100)
    root.mainloop()    

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

def CalcFXRateToKRW(FXData, Currency = "USD", BaseDate = "20250627") :    
    if "-" in str(FXData.index[0]) :
        FXData = FXData.copy()
        FXData.index = np.vectorize(lambda x : str(x).replace("-","").split(" ")[0])(pd.to_datetime(FXData.index))
    elif int(FXData.index[0]) < 19000101 : 
        FXData = FXData.copy()
        NewIndex = [ExcelDateToYYYYMMDD(int(s)) for s in FXData.index]
        FXData.index = NewIndex
         
    if Currency.upper() == "KRW" : 
        return 1
    
    if len(FXData.shape) == 1 : 
        #Series
        NewIndex = pd.Series(FXData.index).apply(lambda x : x.split("-")[0].upper() + "/" + x.split("-")[1].upper() if "-" in str(x) else str(x).upper())
        NewSeries = pd.Series(FXData.values, NewIndex)
    else :
        if int(BaseDate) > FXData.index[-1] : 
            NewSeries = FXData.loc[FXData.index[FXData.index <= int(BaseDate)]].iloc[-1]
        else : 
            NewSeries = FXData.loc[FXData.index[FXData.index >= int(BaseDate)]].iloc[0]
            
    if Currency.upper() == "USD" : 
        return NewSeries.loc["USD/KRW"]

    if Currency + "/KRW" in NewSeries.index :
        return NewSeries.loc[Currency + "/KRW"]
    elif Currency + "/USD" in NewSeries.index: 
        return NewSeries.loc[Currency + "/USD"] * NewSeries.loc["USD/KRW"]
    elif Currency + "/EUR" in NewSeries.index : 
        return NewSeries.loc[Currency + "/EUR"] * NewSeries.loc["EUR/KRW"]        
    else : 
        return -1

def PrintingMarketDataInformation(YYYYMMDD, NameList, MyMarketDataList) : 
    print("\n##########################################################################################\n\n     세팅된 커브는 다음과 같습니다. \n     평가날짜 : " + YYYYMMDD)
    curvename = ''
    for i in range(len(NameList)) : 
        if "Rate" in MyMarketDataList[i].columns or 'rate' in MyMarketDataList[i].columns : 
            curvename += '\n\n     ' + str(i+1) + '. ' + NameList[i].split('\\')[-1] + '\n'
            Term = list(MyMarketDataList[i]["Term" if "Term" in MyMarketDataList[i].columns else "term"].round(5))[:10]
            PrintTerm = [DayPlus(int(YYYYMMDD), int(t * 365 + 1e-9)) for t in Term]
            Rate = list(MyMarketDataList[i]["Rate" if "Rate" in MyMarketDataList[i].columns else "rate"].round(5))[:10]
            curvename += '\n     Term = ' + str(PrintTerm).split(']')[0] + ', ...]'
            curvename += '\n     Rate = ' + str(Rate).split(']')[0] + ', ...]'
        elif "Moneyness/Tenor" in MyMarketDataList[i].columns :             
            curvename += '\n\n     ' + str(i+1) + '. ' + NameList[i].split('\\')[-1] + '\n'
            Term = ["parity/tenor"] + [np.round(float(i), 3) for i in MyMarketDataList[i].columns[1:]]
            curvename += '\n '+str(Term)+'\n'
            curvename += '           '+str(np.round(MyMarketDataList[i].values, 3)).replace("\n","\n           ") 
        elif "SwapMat/OptMat" in MyMarketDataList[i].columns :
            curvename += '\n\n     ' + str(i+1) + '. ' + NameList[i].split('\\')[-1] + '\n'
            myind = MyMarketDataList[i].values[:,0]
            values = (MyMarketDataList[i].values[:,1:] * 100000).astype(np.int64)/1000
            Term = ["SwapMat/OptMat"] + [int(i) for i in MyMarketDataList[i].columns[1:]]
            curvename += '\n '+str(Term).replace(',',',  ') +'\n'
            for j in range(len(values)) : 
                curvename += '            [' + str(myind[j]) + ' | '
                curvename += str(values[j]).replace("  "," ").replace("\n","\n  ").replace('[','')  + '\n'
        elif "스왑만기/옵션만기" in MyMarketDataList[i].columns :
            curvename += '\n\n     ' + str(i+1) + '. ' + NameList[i].split('\\')[-1] + '\n'
            values = np.concatenate([MyMarketDataList[i].values[:,0:1],(MyMarketDataList[i].values[:,1:] *100).round(2)],axis=1)
            Term = ["스왑만기/옵션만기"] + [np.round(float(i), 4) for i in MyMarketDataList[i].columns[1:]]
            curvename += '\n '+str(Term)+'\n'
            curvename += '           '+str(values).replace("\n","\n           ") 
            
    PrintingContents = curvename
    return PrintingContents    

def HullWhiteCalibrationProgram(CurveDirectory, PriceDate, CurveTerm, CurveRate, HolidayDate) : 
    Result = {"CalibrationFlag":False,"HWTerm":np.array([]),"HWVol":np.array([])}
    ZeroCurveName = CurveDirectory.split("\\")[-1].replace(".csv","")  
    Currency = CurveDirectory.split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique())
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namein = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('KOSPI' in str(x).upper() or ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False))] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == str(PriceDate)]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))            
    if len(GroupbyYYYYMMDD) == 0 :
        return Result
     
    root = tk.Tk()
    root.title("Hull White Calibration")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(PriceDate))
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=int(PriceDate) + 100000)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], titlelable = True, titleName = "Swption Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_L1_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11)
    vb_VolFlag = make_listvariable_interface(left_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    vb_FixedKappaFlag = make_listvariable_interface(left_frame, 'FixedKappaFlag', ["0: Kappa도 Calib","1: Kappa 고정"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0)
    v_FixedKappa = make_variable_interface(left_frame, 'FixedKappa', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = 0.01)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(right_frame, ZeroCurveName, termratestr(CurveTerm, CurveRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    vb_SelectedCurve_P1 = make_listvariable_interface(right_frame, 'Swaption Vol 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "Swaption Info", defaultflag = True, defaultvalue = 0, width = 50)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    PrevTreeFlag, tree, scrollbar, scrollbar2, tree2, tree3 = 0, None, None, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, Result, tree2, tree3]
    def run_function(MyArrays) :     

        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        CalcResult = MyArrays[4] 
        tree2 = MyArrays[5]     
        tree3 = MyArrays[6]
        SelectedNumber = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(PriceDate)
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (int(PriceDate) + 100000)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        SwapFreqByMonth = 12/L1_NumCpnOneYear_P1
        DayCountFlag = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else 0    
        BSVol0NormalVol1 = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 1
        FixedKappaFlag = int(str(vb_FixedKappaFlag.get(vb_FixedKappaFlag.curselection())).split(":")[0]) if vb_FixedKappaFlag.curselection() else 0
        if FixedKappaFlag == 0 : 
            FixedKappa = 0
        else : 
            FixedKappa = float(v_FixedKappa.get()) if len(str(v_PriceDate.get())) > 0 else 0
            
        VolRawData = ReadCSV(GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == SelectedNumber]['Directory'].iloc[0])
        VolRawDataIndexSet = VolRawData.set_index(VolRawData.columns[0])
        XCol = VolRawDataIndexSet.columns.astype(np.float64)
        YInd = VolRawDataIndexSet.index.astype(np.float64)
        Values = VolRawDataIndexSet.values.astype(np.float64)
        tf = np.vectorize(lambda x, y : Linterp2D(XCol, YInd, Values, x, y))
        x = np.r_[np.array([3,6,9]) , np.arange(12,132, 12)].reshape(1,-1)
        y = np.r_[np.array([3,6,9]) , np.arange(12,132, 12)].reshape(-1,1)
        InterpolatedVols = tf(x, y)
        SwaptionVolData = pd.DataFrame(InterpolatedVols, columns = x.reshape(-1), index = y.reshape(-1))        

        OptionTenor = SwaptionVolData.columns.astype(np.float64)
        SwapTenor = SwaptionVolData.index.astype(np.float64)
        OptionVolMatrix = SwaptionVolData.values.astype(np.float64)
        if OptionVolMatrix.max() > 0.25 :
            OptionVolMatrix = OptionVolMatrix / 100 
            
        OptionTenor_ByMonth = []
        SwapTenor_ByMonth = []
        OptionVol = []
        for i in range(len(SwapTenor)) : 
            for j in range(len(OptionTenor)) : 
                StartDate = EDate_YYYYMMDD(PriceDate, OptionTenor[j]) 
                EndDate = EDate_YYYYMMDD(StartDate, SwapTenor[i])
                if EndDate < EDate_YYYYMMDD(int(SwapMaturity),3) and EndDate >= int(SwapMaturity) : 
                    OptionTenor_ByMonth.append(OptionTenor[j])
                    SwapTenor_ByMonth.append(SwapTenor[i])
                    OptionVol.append(OptionVolMatrix[i][j])                
        
        if len(OptionVol) <= 4 : 
            OptionTenor_ByMonth = []
            SwapTenor_ByMonth = []
            OptionVol = []
            if DayCountAtoB(PriceDate, SwapMaturity)/365 > (SwapTenor[-1] + OptionTenor[-1])/12 - 1: 
                for i in range(len(SwapTenor)) : 
                    for j in range(len(OptionTenor)) : 
                        if ((i == len(SwapTenor) - 1) or (j == len(OptionTenor) - 1)) : 
                            StartDate = EDate_YYYYMMDD(PriceDate, OptionTenor[j]) 
                            EndDate = EDate_YYYYMMDD(StartDate, SwapTenor[i])
                            OptionTenor_ByMonth.append(OptionTenor[j])
                            SwapTenor_ByMonth.append(SwapTenor[i])
                            OptionVol.append(OptionVolMatrix[i][j])                                    
            else :
                for i in range(len(SwapTenor)) : 
                    for j in range(len(OptionTenor)) : 
                        StartDate = EDate_YYYYMMDD(PriceDate, OptionTenor[j]) 
                        EndDate = EDate_YYYYMMDD(StartDate, SwapTenor[i])
                        OptionTenor_ByMonth.append(OptionTenor[j])
                        SwapTenor_ByMonth.append(SwapTenor[i])
                        OptionVol.append(OptionVolMatrix[i][j])                
                    
        Preprocessing_ZeroTermAndRate(CurveTerm, CurveRate, int(PriceDate))
        MyDict = HullWhiteCalibration1Factor(PriceDate, OptionTenor_ByMonth, SwapTenor_ByMonth, OptionVol, SwapFreqByMonth, BSVol0NormalVol1, CurveTerm, CurveRate, FixedKappa = FixedKappa, DayCountFlag = DayCountFlag, KoreanHolidayFlag = False, AdditionalHolidays = Holidays, initialkappa = 0.01, initialvol = 0.005 if BSVol0NormalVol1== 0 else np.array(OptionVol).mean(), PrintMRSPE=True)
        if len(MyDict["Error"]) == int(np.abs(MyDict["Error"]).sum() + 0.00001) : 
            print("Calibration 실패")
            Calibration = False
        else : 
            Calibration = True
        CalcResult["CalibrationFlag"] = Calibration
        ResultHW = pd.concat([pd.Series(MyDict["HWVolTerm"]), pd.Series(MyDict["HWVol"])],axis = 1)
        ResultHW.columns = ["HWTerm","HWVol"]
        ResultHW = ResultHW.sort_values(by = "HWTerm")
        ResultHW["HWKappa"] = MyDict["kappa"]
        CalcResult["kappa"] = MyDict["kappa"]
        CalcResult["HWTerm"] = ResultHW["HWTerm"].round(8)
        CalcResult["HWVol"] = ResultHW["HWVol"].round(8)
        A = pd.Series(MyDict["SwapStartDate"], name = "SwapStartDate")
        B = pd.Series(MyDict["SwapEndDate"], name = "SwapEndDate")
        C = pd.Series(MyDict["BlackPrice"], name = "BlackPrice").round(4)
        D = pd.Series(MyDict["HWPrice"], name = "HWPrice").round(4)
        E = pd.concat([A,B,C,D],axis = 1)

        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
            tree2 = ttk.Treeview(root)
            tree3 = ttk.Treeview(root)
        else : 
            tree.destroy()
            tree2.destroy()
            tree3.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
            tree2 = ttk.Treeview(root)
            tree3 = ttk.Treeview(root)
        ResultHW = ResultHW.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        InputVol = VolRawData.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree3.pack(padx=5, pady=5, fill="both", expand=False)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        tree2.pack(padx=5, pady=5, fill="both", expand=False)
        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultHW, width = 90)
        PrevTreeFlag2 = insert_dataframe_to_treeview(tree2, E, width = 90)
        PrevTreeFlag3 = insert_dataframe_to_treeview(tree3, InputVol, width = 90)

        MyArrays[0] = PrevTreeFlag
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2  
        MyArrays[4] = CalcResult  
        MyArrays[5] = tree2
        MyArrays[6] = tree3

    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()

    root.mainloop()
    return MyArrays[4]

def PricingIRStructuredSwapProgram(HolidayData, currdir) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                    namenotin = "vol",
                                                                    Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.",
                                                                    MultiSelection = False,
                                                                    DefaultStringList=["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    PriceDateDefault = int(YYYYMMDD)
    Curve = MyMarketDataList[0]
    UsedCurveName = Name[0].split("\\")[-1].split(".")[0]
    Curr = Name[0].split("\\")[-2].upper()
    CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    CalibrationResult = HullWhiteCalibrationProgram(Name[0], int(YYYYMMDD), CurveTerm1, CurveRate1, HolidayData)
    CalibrationFlag = CalibrationResult['CalibrationFlag']
    defaultkappa = 0.01
    if CalibrationFlag == True : 
        defaultkappa = CalibrationResult['kappa']

    YYYY = int(YYYYMMDD) // 10000
    root = tk.Tk()
    root.title("Callable Swap Pricer(Single Phase)")
    root.geometry("1520x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+21) * 10000 + 929)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["0","1","2","4","6"], titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3)
    v_L1_FixedCpnRate_P1 = make_variable_interface(left_frame, 'Leg1 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =2.19)
    v_L1_RefSwapMaturity_T = make_variable_interface(left_frame, 'Leg1 변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11)
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame, 'Leg1 변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11)
    v_L1_RefRateMultiple_P1 = make_variable_interface(left_frame, 'Leg1 변동금리Multiple', bold = False, textfont = 11)
    vb_L1_DayCount = make_listvariable_interface(left_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = PriceDateDefault)
    vb_Holiday = make_listvariable_interface(center_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 4, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)

    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(center_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["0","1","2","4","6"], titlelable = True, titleName = "Leg2 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue = 3)
    v_L2_FixedCpnRate_P1 = make_variable_interface(center_frame, 'Leg2 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = -0.1)
    v_L2_RefSwapMaturity_T = make_variable_interface(center_frame, 'Leg2 변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, defaultflag = True ,defaultvalue = 0.25)
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, 'Leg2 변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_L2_RefRateMultiple_P1 = make_variable_interface(center_frame, 'Leg2 변동금리Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue = 1.0)
    vb_L2_DayCount = make_listvariable_interface(center_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_OptionHolder = make_listvariable_interface(right_frame, 'OptionHolder', ["0: Leg1 Hold Option","1: Leg2 Hold Option"], titleName = "Option Information", titlelable= True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue= 0)
    v_FirstOptPayDate = make_variable_interface(right_frame, '첫 옵션행사일\n(지급일기준)', bold = False, textfont = 11, defaultflag = True, defaultvalue = (YYYY-6) * 10000 + 929)
    vb_NYearBetweenOptionPay = make_listvariable_interface(right_frame, '옵션행사간격', ["6M","12M","24M","36M","60M"], listheight = 5, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_NBDateBetweenOptionFixToPay = make_variable_interface(right_frame, '옵션행사선언일과\n옵션지급일사이의\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 20)
    v_MaxNumOpt = make_variable_interface(right_frame, '최대옵션개수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_L1FirstFixing = make_variable_interface(right_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_L2FirstFixing = make_variable_interface(right_frame, 'Leg2)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_GreekFlag = make_listvariable_interface(right_frame, 'Greek산출', ["0: Pricing만","1: Delta,Gamma","2: Delta,Gamma,Vega"], listheight = 3, textfont = 11)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(rightright_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    v_hwkappa = make_variable_interface(rightright_frame, 'HullWhite Kappa', bold = False, textfont = 11, titleName = "\nHull White Params", titlelable = True, defaultflag = True, defaultvalue = defaultkappa)
    defaulthwterm = "0.25, 0.5, 1" if CalibrationFlag == False else str(list(CalibrationResult["HWTerm"].round(5))).replace("[","").replace("]","")
    defaulthwvol = "0.87, 0.98, 0.89" if CalibrationFlag == False else str(list(CalibrationResult["HWVol"])).replace("[","").replace("]","")
    v_hwvolterm = make_variable_interface(rightright_frame, 'HullWhite Vol Tenor\n[0.25, 0.5, 1.0, ...] 등의\n포멧으로 입력', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaulthwterm)
    v_hwvol = make_variable_interface(rightright_frame, 'HullWhite Volatility(%)\n[0.87, 0.88, 0.91, ...] 등의\n포멧으로 입력', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaulthwvol)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)
    vb_Book = make_listvariable_interface(Result_frame, 'Book', ["0: Book 안함","1: Booking"], listheight = 2, textfont = 11, pady = 10)
    vb_FRTBRaw = make_listvariable_interface(Result_frame, 'BookFRTB', ["0: FRTB RAW 저장X","1: FRTB RAW 저장O"], listheight = 2, textfont = 11, pady = 10)
    vb_FRTBRawDepart = make_variable_interface(Result_frame, '부서명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Derivatives Dept')
    vb_FRTBRawPort = make_variable_interface(Result_frame, '포트명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Structured')
    
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0
        
        L1_PowerSpreadFlag = 0
        if len(str(v_L1_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L1_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L1_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_L1_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L1_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_L1_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25
            
        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RefRateMultiple_P1.get()) if len(str(v_L1_RefRateMultiple_P1.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0
        
        L2_PowerSpreadFlag = 0
        if len(str(v_L2_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L2_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L2_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_L2_RefSwapMaturity_T.get()).lower() : 
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L2_RefSwapMaturity_T.get()).lower() :
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(v_L2_RefSwapMaturity_T.get()) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25
            
        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4
            
        L2_RefRateMultiple_P1 = float(v_L2_RefRateMultiple_P1.get()) if len(str(v_L2_RefRateMultiple_P1.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L2ResultPayoff = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        Holiday = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayData.columns : 
                HolidaysForSwap = HolidayData[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []
                            
        OptionHolder = int(str(vb_OptionHolder.get(vb_OptionHolder.curselection())).split(":")[0]) if vb_OptionHolder.curselection() else 0    
        FirstOptPayDate = int(v_FirstOptPayDate.get()) if len(str(v_FirstOptPayDate.get())) > 0 else SwapEffectiveDate + 10000
        NYearBetweenOptionPay = float(str(vb_NYearBetweenOptionPay.get(vb_NYearBetweenOptionPay.curselection())).split("M")[0])/12 if vb_NYearBetweenOptionPay.curselection() else 1    
        MaxNumOpt = int(v_MaxNumOpt.get()) if len(str(v_MaxNumOpt.get())) > 0 else -1
        NBDateBetweenOptionFixToPay = int(v_NBDateBetweenOptionFixToPay.get()) if len(str(v_NBDateBetweenOptionFixToPay.get())) > 0 else 0
        
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        
        hwkappa = float(v_hwkappa.get()) if len(str(v_hwkappa.get())) > 0 else 0.001
        if len(str(v_hwvolterm.get())) > 0 : 
            if '(' in str(v_hwvolterm.get()) or ')' in str(v_hwvolterm.get()) : 
                tenorstr = str(v_hwvolterm.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvolterm.get()) or ']' in str(v_hwvolterm.get()) :
                tenorstr = str(v_hwvolterm.get()).replace("[","").replace("]","").split(',')
            else : 
                tenorstr = str(v_hwvolterm.get()).split(',')
            hwvolterm = list(np.vectorize(lambda x : float(x))(tenorstr))
        else : 
            hwvolterm = [1.0]

        if len(str(v_hwvol.get())) > 0 : 
            if '(' in str(v_hwvol.get()) or ')' in str(v_hwvol.get()) : 
                volstr = str(v_hwvol.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol.get()) or ']' in str(v_hwvol.get()) :
                volstr = str(v_hwvol.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol.get()).split(',')
            hwvol = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol = [0.001]
        BookFlag = int(str(vb_Book.get(vb_Book.curselection())).split(":")[0]) if vb_Book.curselection() else 0
        FRTBRawFlag = int(str(vb_FRTBRaw.get(vb_FRTBRaw.curselection())).split(":")[0]) if vb_FRTBRaw.curselection() else 0
        FRTBDepart = str(vb_FRTBRawDepart.get()) if len(str(vb_FRTBRawDepart.get())) > 0 else "TempDepart"
        FRTBPort = str(vb_FRTBRawPort.get()) if len(str(vb_FRTBRawPort.get())) > 0 else "TempPort"
        GreekFlag = 2 if FRTBRawFlag != 0 else GreekFlag                         
        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        L2FirstFixing = float(v_L2FirstFixing.get())/100 if str(v_L2FirstFixing.get()) else 0.0
        
        L1_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(365)]
        L1_FixingHistoryRate = [L1FirstFixing] * len(L1_FixingHistoryDate)    
        L2_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(366)] 
        L2_FixingHistoryRate = [L2FirstFixing] * len(L2_FixingHistoryDate)    
        Pu = Pd = 0.0
        V = pd.DataFrame([])
        OptionFixDate, OptionPayDate = Generate_OptionDate(FirstOptPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay, MaxNumOpt, ModifiedFollow = 0)
        if GreekFlag == 0 and BookFlag == 0 and FRTBRawFlag == 0: 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            GIRRDelta = 0
            GIRRCurvature = 0
            GIRRVega = 0
            
        else : 
            Result, resultframe = Pricing_IRCallableSwap_HWFDM_Greek(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread,
                    GreekFlag = GreekFlag)
            resultprice = resultframe["ResultPrice"].iloc[0]
            
            DeltaGreek = pd.Series(Result["PV01"], index = CurveTerm1).reset_index()
            DeltaGreek.columns = ["PV01Term","PV01"]
            resultframe["PV01Term"] = list(DeltaGreek["PV01Term"]) + [np.nan] * (len(resultframe) - len(DeltaGreek))
            resultframe["PV01"] = list(DeltaGreek["PV01"]) + [np.nan] * (len(resultframe) - len(DeltaGreek))      

            GIRRDelta = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(DeltaGreek, "PV01Term","PV01"), 4)
            Cvup = list(np.array(CurveRate1) + 0.012)
            Pu = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvup, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = False, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            Cvdn = list(np.array(CurveRate1) - 0.012)
            Pd = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvdn, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = False, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            GammaGreek = DeltaGreek.copy()
            GammaGreek.columns = ["Tenor","DeltaSensi"]
            GammaGreek["DeltaSensi"] = GammaGreek["DeltaSensi"] * 10000
            GammaGreek["Bucket"] ="KRW"
            GammaGreek["RiskWeight"] = GIRR_DeltaRiskWeight(list(DeltaGreek["PV01Term"].values), ["KRW"] * len(DeltaGreek), ["IRS"] * len(DeltaGreek))
            CVR_Plus = -(Pu - Result["Price"] - (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            CVR_Minus = -(Pd - Result["Price"] + (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            GIRRCurvature = max(abs(CVR_Plus), abs(CVR_Minus))
            T = DayCountAtoB(int(YYYYMMDD), SwapMaturity)/365
            if GreekFlag > 1 : 
                V = pd.Series(Result["VegaFRTB"], Result["VegaTerm"]).reset_index()
                V.columns = ["Tenor1","VegaSensi"]
                V["Tenor2"] = T - V["Tenor1"]
                V["Risk_Type"] = "Vega"
                V["Curve"] = UsedCurveName
                V["Risk_Class"] = "GIRR"
                V["Bucket"] = Curr
                GIRRVega = Calc_GIRRVega(V, SensitivityColumnName = "VegaSensi")["KB_M"].iloc[0]
            else : 
                V = pd.DataFrame([[1,0, 1.0, 0.0,'Vega',UsedCurveName,"GIRR",Curr]],columns = ['Tenor1','Tenor2','VegaSensi','Risk_Type','Curve','Risk_Class','Bucket'])
                GIRRVega = 0
 
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        resultframe = resultframe.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultframe.reset_index(), width = 100)
        if GreekFlag > 0 : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\nLeg1 Payoff: \n{L1ResultPayoff}\nLeg2 Payoff: \n{L2ResultPayoff}\nGIRR Delta: {np.round(GIRRDelta,4)}\nGIRR Curvature: {np.round(GIRRCurvature,4)}\nGIRR Vega: {np.round(GIRRVega,4)} ", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff}\n\nLeg2 Payoff: \n{L2ResultPayoff}", font = ("맑은 고딕", 12, 'bold'))

        if BookFlag != 0 : 
            now = pd.Timestamp.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:03d}"
            resultframe.to_csv(currdir + "\\Book\\StructuredSwap\\StructuredSwap_" + str(timestamp) + ".csv", index = False, encoding = "cp949")
            messagebox.showinfo("알림","Booking 완료!!")   

        if FRTBRawFlag != 0 : 
            FRTBRaw = ReadCSV(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv')
            DeltaFRTB = Calc_GIRRDeltaNotCorrelated_FromGreeks_PreProcessing(DeltaGreek, "PV01Term","PV01", Curvename = UsedCurveName, Type = "Rate", Bucket = Curr)
            DeltaFRTB['Depart'] = FRTBDepart
            DeltaFRTB['Portfolio'] = FRTBPort
            DeltaFRTB['RiskFactor1'] = UsedCurveName.replace(" ZeroCurve","")
            DeltaFRTB['RiskFactor2'] = DeltaFRTB["Tenor"]
            DeltaFRTB['RiskFactor3'] = DeltaFRTB["Type"]
            DeltaFRTB = DeltaFRTB[['Depart','Risk_Class','Risk_Type','Portfolio','Bucket',
                                   'RiskFactor1','RiskFactor2','RiskFactor3','Delta_Sensi']]
            GammaFRTB = DeltaFRTB.copy()
            GammaFRTB["Risk_Type"] = "Curvature"
            GammaFRTB["Value_Up"] = Pu
            GammaFRTB["Value_Dn"] = Pd
            GammaFRTB["Value"] = resultprice
            V['Vega_Sensi'] = V['VegaSensi']
            VolName = ''
            if 'KRW' in Curr : 
                VolName = 'KRW SWAPTION VOL'
            elif 'USD' in Curr : 
                VolName = 'USD SOFR SWAPTION'
            else : 
                VolName += Curr + ' SWAPTION VOL'
            V['RiskFactor1'] = VolName
            V['Depart'] = FRTBDepart
            V['Portfolio'] = FRTBPort            
            VegaFRTB = MapGIRRVegaGreeks(V, "Tenor1","Tenor2","Vega_Sensi","RiskFactor1")            
            FRTBRaw = pd.concat([FRTBRaw, DeltaFRTB,GammaFRTB,VegaFRTB],axis = 0)
            FRTBRaw.to_csv(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv', index = False, encoding = "cp949")
            messagebox.showinfo("알림","FRTB Raw 추가 완료!!")   

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, 1, 1, 1


def PricingIRStructuredSwapProgram2F(HolidayData, currdir) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                    namenotin = "vol",
                                                                    Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.",
                                                                    MultiSelection = False,
                                                                    DefaultStringList=["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    PriceDateDefault = int(YYYYMMDD)
    Curve = MyMarketDataList[0]
    UsedCurveName = Name[0].split("\\")[-1].split(".")[0]
    Curr = Name[0].split("\\")[-2].upper()
    CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    CalibrationFlag = False
    defaultkappa = 0.01
    defaultkappa2 = 0.01        

    YYYY = int(YYYYMMDD) // 10000
    root = tk.Tk()
    root.title("Callable Swap 2F Pricer(Single Phase)")
    root.geometry("1560x780+5+5")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+21) * 10000 + 929)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수', ["0","1","2","4","6"], titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3)
    v_L1_FixedCpnRate_P1 = make_variable_interface(left_frame, 'Leg1 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =1.69)
    v_L1_RefSwapMaturity_T = make_variable_interface(left_frame, 'Leg1 변동금리 만기\n(3M-> 0.25, 5Y-> 5, \n5Y-1Y -> 5-1)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11)
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame, 'Leg1 변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11)
    v_L1_RefRateMultiple_P1 = make_variable_interface(left_frame, 'Leg1 변동금리Multiple', bold = False, textfont = 11)
    vb_L1_DayCount = make_listvariable_interface(left_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = PriceDateDefault)
    vb_Holiday = make_listvariable_interface(center_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 4, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)

    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(center_frame, '연 쿠폰지급수', ["0","1","2","4","6"], titlelable = True, titleName = "Leg2 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue = 3)
    v_L2_FixedCpnRate_P1 = make_variable_interface(center_frame, 'Leg2 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.2)
    v_L2_RefSwapMaturity_T = make_variable_interface(center_frame, 'Leg2 변동금리 만기\n(3M-> 0.25, 5Y-> 5, \n5Y-1Y -> 5-1)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, defaultflag = True ,defaultvalue = '5 - 1')
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, 'Leg2 변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_L2_RefRateMultiple_P1 = make_variable_interface(center_frame, 'Leg2 변동금리Multiple', bold = False, textfont = 11, defaultflag = True, defaultvalue = 5.0)
    vb_L2_DayCount = make_listvariable_interface(center_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')
    vb_OptionHolder = make_listvariable_interface(right_frame, 'OptionHolder', ["0: Leg1 Hold Option","1: Leg2 Hold Option"], titleName = "Option Information", titlelable= True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue= 0)
    v_FirstOptPayDate = make_variable_interface(right_frame, '첫 옵션행사일\n(지급일기준)', bold = False, textfont = 11, defaultflag = True, defaultvalue = (YYYY-6) * 10000 + 929)
    vb_NYearBetweenOptionPay = make_listvariable_interface(right_frame, '옵션행사간격', ["6M","12M","24M","36M","60M"], listheight = 5, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_NBDateBetweenOptionFixToPay = make_variable_interface(right_frame, '옵션행사선언일과\n옵션지급일사이의\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 20)
    v_MaxNumOpt = make_variable_interface(right_frame, '최대옵션개수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_L1FirstFixing = make_variable_interface(right_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_L2FirstFixing = make_variable_interface(right_frame, 'Leg2)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_GreekFlag = make_listvariable_interface(right_frame, 'Greek산출', ["0: Pricing만","1: Delta,Gamma","2: Delta,Gamma,Vega"], listheight = 3, textfont = 11)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(rightright_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 12, textfont = 10)
    v_hwkappa = make_variable_interface(rightright_frame, 'Kappa', bold = False, textfont = 11, titleName = "\nHull White Params", titlelable = True, defaultflag = True, defaultvalue = defaultkappa)
    v_hwkappa2 = make_variable_interface(rightright_frame, 'Kappa2', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaultkappa2)
    v_hwvol = make_variable_interface(rightright_frame, 'Volatility1(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.99)
    v_hwvol2 = make_variable_interface(rightright_frame, 'Volatility2(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.66)
    v_hwfactorcorr = make_variable_interface(rightright_frame, 'Factor Corr(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = -0.1)
    vb_Logging = make_listvariable_interface(rightright_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 2, pady = 5, anchor = 'n')
    vb_FRTBRaw = make_listvariable_interface(Result_frame, 'BookFRTB', ["0: FRTB RAW 저장X","1: FRTB RAW 저장O"], listheight = 2, textfont = 11, pady = 10)
    vb_FRTBRawDepart = make_variable_interface(Result_frame, '부서명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Derivatives Dept')
    vb_FRTBRawPort = make_variable_interface(Result_frame, '포트명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Structured')
    
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0
        
        L1_PowerSpreadFlag = 0
        if len(str(v_L1_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L1_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L1_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_L1_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L1_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_L1_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25
            
        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RefRateMultiple_P1.get()) if len(str(v_L1_RefRateMultiple_P1.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0
        
        L2_PowerSpreadFlag = 0
        if len(str(v_L2_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L2_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L2_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_L2_RefSwapMaturity_T.get()).lower() : 
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L2_RefSwapMaturity_T.get()).lower() :
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(v_L2_RefSwapMaturity_T.get()) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25
            
        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4
            
        L2_RefRateMultiple_P1 = float(v_L2_RefRateMultiple_P1.get()) if len(str(v_L2_RefRateMultiple_P1.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L2ResultPayoff = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        Holiday = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayData.columns : 
                HolidaysForSwap = HolidayData[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []
                            
        OptionHolder = int(str(vb_OptionHolder.get(vb_OptionHolder.curselection())).split(":")[0]) if vb_OptionHolder.curselection() else 0    
        FirstOptPayDate = int(v_FirstOptPayDate.get()) if len(str(v_FirstOptPayDate.get())) > 0 else SwapEffectiveDate + 10000
        NYearBetweenOptionPay = float(str(vb_NYearBetweenOptionPay.get(vb_NYearBetweenOptionPay.curselection())).split("M")[0])/12 if vb_NYearBetweenOptionPay.curselection() else 1    
        MaxNumOpt = int(v_MaxNumOpt.get()) if len(str(v_MaxNumOpt.get())) > 0 else -1
        NBDateBetweenOptionFixToPay = int(v_NBDateBetweenOptionFixToPay.get()) if len(str(v_NBDateBetweenOptionFixToPay.get())) > 0 else 0
        
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        
        hwkappa = float(v_hwkappa.get()) if len(str(v_hwkappa.get())) > 0 else 0.001
        hwvolterm = [1.0]
        hwkappa2 = float(v_hwkappa2.get()) if len(str(v_hwkappa2.get())) > 0 else 0.001
        hwvolterm2 = [1.0]
        hwfactorcorr = float(v_hwfactorcorr.get()) if len(str(v_hwfactorcorr.get())) > 0 else -0.001
        
        if len(str(v_hwvol.get())) > 0 : 
            if '(' in str(v_hwvol.get()) or ')' in str(v_hwvol.get()) : 
                volstr = str(v_hwvol.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol.get()) or ']' in str(v_hwvol.get()) :
                volstr = str(v_hwvol.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol.get()).split(',')
            hwvol = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol = [0.001]

        if len(str(v_hwvol2.get())) > 0 : 
            if '(' in str(v_hwvol2.get()) or ')' in str(v_hwvol2.get()) : 
                volstr = str(v_hwvol2.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol2.get()) or ']' in str(v_hwvol2.get()) :
                volstr = str(v_hwvol2.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol2.get()).split(',')
            hwvol2 = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol2 = [0.001]

        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        L2FirstFixing = float(v_L2FirstFixing.get())/100 if str(v_L2FirstFixing.get()) else 0.0
        
        L1_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(365)]
        L1_FixingHistoryRate = [L1FirstFixing] * len(L1_FixingHistoryDate)    
        L2_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(366)] 
        L2_FixingHistoryRate = [L2FirstFixing] * len(L2_FixingHistoryDate)    

        FRTBRawFlag = int(str(vb_FRTBRaw.get(vb_FRTBRaw.curselection())).split(":")[0]) if vb_FRTBRaw.curselection() else 0
        FRTBDepart = str(vb_FRTBRawDepart.get()) if len(str(vb_FRTBRawDepart.get())) > 0 else "TempDepart"
        FRTBPort = str(vb_FRTBRawPort.get()) if len(str(vb_FRTBRawPort.get())) > 0 else "TempPort"
        GreekFlag = 2 if FRTBRawFlag != 0 else GreekFlag                         

        Pu = Pd = 0.0
        V = pd.DataFrame([])        
        OptionFixDate, OptionPayDate = Generate_OptionDate(FirstOptPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay, MaxNumOpt, ModifiedFollow = 0)
        if GreekFlag == 0 and FRTBRawFlag == 0 : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            GIRRDelta = 0
            GIRRCurvature = 0
            GIRRVega = 0
            
        else : 
            Result, resultframe = Pricing_IRCallableSwap_HWFDM_Greek(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread,
                    GreekFlag = GreekFlag)
            resultprice = resultframe["ResultPrice"].iloc[0]
            
            DeltaGreek = pd.Series(Result["PV01"], index = CurveTerm1).reset_index()
            DeltaGreek.columns = ["PV01Term","PV01"]
            resultframe["PV01Term"] = list(DeltaGreek["PV01Term"]) + [np.nan] * (len(resultframe) - len(DeltaGreek))
            resultframe["PV01"] = list(DeltaGreek["PV01"]) + [np.nan] * (len(resultframe) - len(DeltaGreek))                        
            GIRRDelta = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(DeltaGreek, "PV01Term","PV01"), 4)
            Cvup = list(np.array(CurveRate1) + 0.012)
            Pu = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvup, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False,
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            Cvdn = list(np.array(CurveRate1) - 0.012)
            Pd = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvdn, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False,
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            GammaGreek = DeltaGreek.copy()
            GammaGreek.columns = ["Tenor","DeltaSensi"]
            GammaGreek["DeltaSensi"] = GammaGreek["DeltaSensi"] * 10000
            GammaGreek["Bucket"] ="KRW"
            GammaGreek["RiskWeight"] = GIRR_DeltaRiskWeight(list(DeltaGreek["PV01Term"].values), ["KRW"] * len(DeltaGreek), ["IRS"] * len(DeltaGreek))
            CVR_Plus = -(Pu - Result["Price"] - (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            CVR_Minus = -(Pd - Result["Price"] + (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            GIRRCurvature = max(abs(CVR_Plus), abs(CVR_Minus))
            T = DayCountAtoB(int(YYYYMMDD), SwapMaturity)/365
            if GreekFlag > 1 : 
                V = pd.Series(Result["VegaFRTB"], Result["VegaTerm"]).reset_index()
                V.columns = ["Tenor1","VegaSensi"]
                V["Tenor2"] = T - V["Tenor1"]
                V["Risk_Type"] = "Vega"
                V["Curve"] = UsedCurveName
                V["Risk_Class"] = "GIRR"
                V["Bucket"] = "KRW"
                GIRRVega = Calc_GIRRVega(V, SensitivityColumnName = "VegaSensi")["KB_M"].iloc[0]
            else : 
                V = pd.DataFrame([[1,0, 1.0, 0.0,'Vega',UsedCurveName,"GIRR",Curr]],columns = ['Tenor1','Tenor2','VegaSensi','Risk_Type','Curve','Risk_Class','Bucket'])
                GIRRVega = 0
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        resultframe = resultframe.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultframe.reset_index(), width = 100)
        if GreekFlag > 0 : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff}\n\nLeg2 Payoff: \n{L2ResultPayoff}\n\nGIRR Delta: {np.round(GIRRDelta,4)}\n\nGIRR Curvature: {np.round(GIRRCurvature,4)}\n\nGIRR Vega: {np.round(GIRRVega,4)} ", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff}\n\nLeg2 Payoff: \n{L2ResultPayoff}", font = ("맑은 고딕", 12, 'bold'))

        if FRTBRawFlag != 0 : 
            FRTBRaw = ReadCSV(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv')
            DeltaFRTB = Calc_GIRRDeltaNotCorrelated_FromGreeks_PreProcessing(DeltaGreek, "PV01Term","PV01", Curvename = UsedCurveName, Type = "Rate", Bucket = Curr)
            DeltaFRTB['Depart'] = FRTBDepart
            DeltaFRTB['Portfolio'] = FRTBPort
            DeltaFRTB['RiskFactor1'] = UsedCurveName.replace(" ZeroCurve","")
            DeltaFRTB['RiskFactor2'] = DeltaFRTB["Tenor"]
            DeltaFRTB['RiskFactor3'] = DeltaFRTB["Type"]
            DeltaFRTB = DeltaFRTB[['Depart','Risk_Class','Risk_Type','Portfolio','Bucket',
                                   'RiskFactor1','RiskFactor2','RiskFactor3','Delta_Sensi']]
            GammaFRTB = DeltaFRTB.copy()
            GammaFRTB["Risk_Type"] = "Curvature"
            GammaFRTB["Value_Up"] = Pu
            GammaFRTB["Value_Dn"] = Pd
            GammaFRTB["Value"] = resultprice
            V['Vega_Sensi'] = V['VegaSensi']
            VolName = ''
            if 'KRW' in Curr : 
                VolName = 'KRW SWAPTION VOL'
            elif 'USD' in Curr : 
                VolName = 'USD SOFR SWAPTION'
            else : 
                VolName += Curr + ' SWAPTION VOL'
            V['RiskFactor1'] = VolName
            V['Depart'] = FRTBDepart
            V['Portfolio'] = FRTBPort            
            VegaFRTB = MapGIRRVegaGreeks(V, "Tenor1","Tenor2","Vega_Sensi","RiskFactor1")            
            FRTBRaw = pd.concat([FRTBRaw, DeltaFRTB,GammaFRTB,VegaFRTB],axis = 0)
            FRTBRaw.to_csv(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv', index = False, encoding = "cp949")
            messagebox.showinfo("알림","FRTB Raw 추가 완료!!")   

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(rightright_frame, text = '실행', padx = 3, pady = 3, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 12).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 3, pady = 2)

    root.mainloop()
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, 1, 1, 1

def PricingIRStructuredSwapProgramDoublePhase(HolidayData, currdir) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                    namenotin = "vol",
                                                                    Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.",
                                                                    MultiSelection = False,
                                                                    DefaultStringList=["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    PriceDateDefault = int(YYYYMMDD)
    Curve = MyMarketDataList[0]
    UsedCurveName = Name[0].split("\\")[-1].split(".")[0]
    Curr = Name[0].split("\\")[-2].upper()
    CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    CalibrationResult = HullWhiteCalibrationProgram(Name[0], int(YYYYMMDD), CurveTerm1, CurveRate1, HolidayData)
    CalibrationFlag = CalibrationResult['CalibrationFlag']
    defaultkappa = 0.01
    if CalibrationFlag == True : 
        defaultkappa = CalibrationResult['kappa']

    YYYY = int(YYYYMMDD) // 10000
    root = tk.Tk()
    root.title("Callable Swap Pricer(Double Phase)")
    root.geometry("1550x790+2+2")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = PriceDateDefault)
    vb_Holiday = make_listvariable_interface(left_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 4, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 929)
    v_Phase2StartDate = make_variable_interface(left_frame, 'Phase2StartDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 100000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+21) * 10000 + 929)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 1, pady = 3, anchor = 'n')
    vb_L1_PhaseUseFlag = make_listvariable_interface(center_frame, 'Phase2사용Flag', ["0: False","1: True"], titlelable = True, titleName = "Leg1 Information", listheight = 2, textfont = 10, defaultflag = True, defaultvalue=1)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(center_frame, '연 쿠폰지급수(P1)', ["0","1","2","4","6"], listheight = 4, textfont = 11, pady = 1, defaultflag = True, defaultvalue=3)
    vb_L1_NumCpnOneYear_P2 = make_listvariable_interface(center_frame, '연 쿠폰지급수(P2)', ["0","1","2","4","6"], listheight = 4, textfont = 10, pady = 1, defaultflag = True, defaultvalue=3)
    v_L1_FixedCpnRate_P1 = make_variable_interface(center_frame, '고정쿠폰(%)(P1)', bold = False, textfont = 11, pady = 1, defaultflag = True, defaultvalue =2.19)
    v_L1_FixedCpnRate_P2 = make_variable_interface(center_frame, '고정쿠폰(%)(P2)', bold = False, textfont = 10, pady = 1, defaultflag = True, defaultvalue =2.19)
    v_L1_RefSwapMaturity_T = make_variable_interface(center_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, pady = 1)
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, '변동금리 연쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, pady = 1)
    v_L1_RefRateMultiple_P1 = make_variable_interface(center_frame, '변동금리Multiple(P1)', bold = False, textfont = 11, pady = 1)
    v_L1_RefRateMultiple_P2 = make_variable_interface(center_frame, '변동금리Multiple(P2)', bold = False, textfont = 10, pady = 1)
    vb_L1_DayCount = make_listvariable_interface(center_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 1, pady = 3, anchor = 'n')
    vb_L2_PhaseUseFlag = make_listvariable_interface(right_frame, 'Phase2사용Flag', ["0: False","1: True"], titlelable = True, titleName = "Leg2 Information", listheight = 2, textfont = 10, defaultflag = True, defaultvalue=0)
    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(right_frame, '연 쿠폰지급수(P1)', ["0","1","2","4","6"], listheight = 4, textfont = 11, pady = 1, defaultflag = True, defaultvalue = 3)
    vb_L2_NumCpnOneYear_P2 = make_listvariable_interface(right_frame, '연 쿠폰지급수(P2)', ["0","1","2","4","6"], listheight = 4, textfont = 10, pady = 1, defaultflag = True, defaultvalue=3)
    v_L2_FixedCpnRate_P1 = make_variable_interface(right_frame, '고정쿠폰(%)(P1)', bold = False, textfont = 11, pady = 1, defaultflag = True, defaultvalue = -0.1)
    v_L2_FixedCpnRate_P2 = make_variable_interface(right_frame, '고정쿠폰(%)(P2)', bold = False, textfont = 10, pady = 1, defaultflag = True, defaultvalue = 0.15)
    v_L2_RefSwapMaturity_T = make_variable_interface(right_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, defaultflag = True ,defaultvalue = 0.25, pady = 1)
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(right_frame, '변동금리 연쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, pady = 1, defaultflag = True, defaultvalue = 2)
    v_L2_RefRateMultiple_P1 = make_variable_interface(right_frame, '변동금리Multiple(P1)', bold = False, textfont = 11, pady = 1, defaultflag = True, defaultvalue = 1.0)
    v_L2_RefRateMultiple_P2 = make_variable_interface(right_frame, '변동금리Multiple(P2)', bold = False, textfont = 10, pady = 1)
    vb_L2_DayCount = make_listvariable_interface(right_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_OptionHolder = make_listvariable_interface(rightright_frame, 'OptionHolder', ["0: Leg1 Hold Option","1: Leg2 Hold Option"], titleName = "Option Information", titlelable= True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue= 0)
    v_FirstOptPayDate = make_variable_interface(rightright_frame, '첫 옵션행사일\n(지급일기준)', bold = False, textfont = 11, defaultflag = True, defaultvalue = (YYYY-6) * 10000 + 929)
    vb_NYearBetweenOptionPay = make_listvariable_interface(rightright_frame, '옵션행사간격', ["6M","12M","24M","36M","60M"], listheight = 5, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_NBDateBetweenOptionFixToPay = make_variable_interface(rightright_frame, '옵션행사선언일과\n옵션지급일사이의\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 20)
    v_MaxNumOpt = make_variable_interface(rightright_frame, '최대옵션개수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_L1FirstFixing = make_variable_interface(rightright_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_L2FirstFixing = make_variable_interface(rightright_frame, 'Leg2)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_GreekFlag = make_listvariable_interface(rightright_frame, 'Greek산출', ["0: Pricing만","1: Delta,Gamma","2: Delta,Gamma,Vega"], listheight = 3, textfont = 11)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(Result_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 13, textfont = 11)
    v_hwkappa = make_variable_interface(Result_frame, 'HullWhite Kappa', bold = False, textfont = 11, titleName = "\nHull White Params", titlelable = True, defaultflag = True, defaultvalue = defaultkappa)
    defaulthwterm = "0.25, 0.5, 1" if CalibrationFlag == False else str(list(CalibrationResult["HWTerm"].round(5))).replace("[","").replace("]","")
    defaulthwvol = "0.87, 0.98, 0.89" if CalibrationFlag == False else str(list(CalibrationResult["HWVol"])).replace("[","").replace("]","")
    v_hwvolterm = make_variable_interface(Result_frame, 'HullWhite Vol Tenor\n[0.25, 0.5, 1.0, ...] 등의\n포멧으로 입력', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaulthwterm)
    v_hwvol = make_variable_interface(Result_frame, 'HullWhite Volatility(%)\n[0.87, 0.88, 0.91, ...] 등의\n포멧으로 입력', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaulthwvol)
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 10, pady = 5)

    Result_frame2 = tk.Frame(root)
    Result_frame2.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_FRTBRaw = make_listvariable_interface(Result_frame2, 'BookFRTB', ["0: FRTB RAW 저장X","1: FRTB RAW 저장O"], listheight = 2, textfont = 11, pady = 10)
    vb_FRTBRawDepart = make_variable_interface(Result_frame2, '부서명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Derivatives Dept')
    vb_FRTBRawPort = make_variable_interface(Result_frame2, '포트명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Structured')
    
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        Phase2StartDate = int(v_Phase2StartDate.get()) if len(str(v_Phase2StartDate.get())) > 0 else (20200627 + 50000)
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        L1_PhaseUseFlag = int(str(vb_L1_PhaseUseFlag.get(vb_L1_PhaseUseFlag.curselection())).split(":")[0]) if vb_L1_PhaseUseFlag.curselection() else 0
        
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0

        L1_NumCpnOneYear_P2 = int(vb_L1_NumCpnOneYear_P2.get(vb_L1_NumCpnOneYear_P2.curselection())) if vb_L1_NumCpnOneYear_P2.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P2.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P2.get()) : 
                L1_FixedCpnRate_P2 = float(v_L1_FixedCpnRate_P2.get())/100
            else : 
                L1_FixedCpnRate_P2 = float(str(v_L1_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P2 = 0
        
        L1_PowerSpreadFlag = 0
        if len(str(v_L1_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L1_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L1_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_L1_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L1_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_L1_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25
            
        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RefRateMultiple_P1.get()) if len(str(v_L1_RefRateMultiple_P1.get())) > 0 else 0
        L1_RefRateMultiple_P2 = float(v_L1_RefRateMultiple_P2.get()) if len(str(v_L1_RefRateMultiple_P2.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff_P2 = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P2) + " + " +str(np.round(L1_FixedCpnRate_P2*100,4)) + "%"
        else : 
            L1ResultPayoff_P2 = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P2) + " + " +str(np.round(L1_FixedCpnRate_P2*100,4)) + "%"
        
        L2_PhaseUseFlag = int(str(vb_L2_PhaseUseFlag.get(vb_L2_PhaseUseFlag.curselection())).split(":")[0]) if vb_L2_PhaseUseFlag.curselection() else 0        
        
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0
        
        L2_NumCpnOneYear_P2 = int(vb_L2_NumCpnOneYear_P2.get(vb_L2_NumCpnOneYear_P2.curselection())) if vb_L2_NumCpnOneYear_P2.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P2.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P2.get()) : 
                L2_FixedCpnRate_P2 = float(v_L2_FixedCpnRate_P2.get())/100
            else : 
                L2_FixedCpnRate_P2 = float(str(v_L2_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P2 = 0        
        
        L2_PowerSpreadFlag = 0
        if len(str(v_L2_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L2_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L2_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_L2_RefSwapMaturity_T.get()).lower() : 
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L2_RefSwapMaturity_T.get()).lower() :
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(v_L2_RefSwapMaturity_T.get()) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25
            
        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4
            
        L2_RefRateMultiple_P1 = float(v_L2_RefRateMultiple_P1.get()) if len(str(v_L2_RefRateMultiple_P1.get())) > 0 else 0
        L2_RefRateMultiple_P2 = float(v_L2_RefRateMultiple_P2.get()) if len(str(v_L2_RefRateMultiple_P2.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L2ResultPayoff = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"

        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff_P2 = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P2) + " + " +str(np.round(L2_FixedCpnRate_P2*100,4)) + "%"
        else : 
            L2ResultPayoff_P2 = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P2) + " + " +str(np.round(L2_FixedCpnRate_P2*100,4)) + "%"

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        Holiday = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayData.columns : 
                HolidaysForSwap = HolidayData[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []
                            
        OptionHolder = int(str(vb_OptionHolder.get(vb_OptionHolder.curselection())).split(":")[0]) if vb_OptionHolder.curselection() else 0    
        FirstOptPayDate = int(v_FirstOptPayDate.get()) if len(str(v_FirstOptPayDate.get())) > 0 else SwapEffectiveDate + 10000
        NYearBetweenOptionPay = float(str(vb_NYearBetweenOptionPay.get(vb_NYearBetweenOptionPay.curselection())).split("M")[0])/12 if vb_NYearBetweenOptionPay.curselection() else 1    
        MaxNumOpt = int(v_MaxNumOpt.get()) if len(str(v_MaxNumOpt.get())) > 0 else -1
        NBDateBetweenOptionFixToPay = int(v_NBDateBetweenOptionFixToPay.get()) if len(str(v_NBDateBetweenOptionFixToPay.get())) > 0 else 0
        
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0

        FRTBRawFlag = int(str(vb_FRTBRaw.get(vb_FRTBRaw.curselection())).split(":")[0]) if vb_FRTBRaw.curselection() else 0
        FRTBDepart = str(vb_FRTBRawDepart.get()) if len(str(vb_FRTBRawDepart.get())) > 0 else "TempDepart"
        FRTBPort = str(vb_FRTBRawPort.get()) if len(str(vb_FRTBRawPort.get())) > 0 else "TempPort"
        GreekFlag = 2 if FRTBRawFlag != 0 else GreekFlag                         

        hwkappa = float(v_hwkappa.get()) if len(str(v_hwkappa.get())) > 0 else 0.001
        if len(str(v_hwvolterm.get())) > 0 : 
            if '(' in str(v_hwvolterm.get()) or ')' in str(v_hwvolterm.get()) : 
                tenorstr = str(v_hwvolterm.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvolterm.get()) or ']' in str(v_hwvolterm.get()) :
                tenorstr = str(v_hwvolterm.get()).replace("[","").replace("]","").split(',')
            else : 
                tenorstr = str(v_hwvolterm.get()).split(',')
            hwvolterm = list(np.vectorize(lambda x : float(x))(tenorstr))
        else : 
            hwvolterm = [1.0]

        if len(str(v_hwvol.get())) > 0 : 
            if '(' in str(v_hwvol.get()) or ')' in str(v_hwvol.get()) : 
                volstr = str(v_hwvol.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol.get()) or ']' in str(v_hwvol.get()) :
                volstr = str(v_hwvol.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol.get()).split(',')
            hwvol = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol = [0.001]

        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        L2FirstFixing = float(v_L2FirstFixing.get())/100 if str(v_L2FirstFixing.get()) else 0.0
        
        L1_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(365)]
        L1_FixingHistoryRate = [L1FirstFixing] * len(L1_FixingHistoryDate)    
        L2_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(366)] 
        L2_FixingHistoryRate = [L2FirstFixing] * len(L2_FixingHistoryDate)    
        Pu = Pd = 0
        OptionFixDate, OptionPayDate = Generate_OptionDate(FirstOptPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay, MaxNumOpt, ModifiedFollow = 0)
        if GreekFlag == 0 : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            GIRRDelta = 0
            GIRRCurvature = 0
            GIRRVega = 0
            
        else : 

            Result, resultframe = Pricing_IRCallableSwap_HWFDM_Greek(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread,
                    GreekFlag = GreekFlag)
            resultprice = resultframe["ResultPrice"].iloc[0]
            
            DeltaGreek = pd.Series(Result["PV01"], index = CurveTerm1).reset_index()
            DeltaGreek.columns = ["PV01Term","PV01"]
            resultframe["PV01Term"] = list(DeltaGreek["PV01Term"]) + [np.nan] * (len(resultframe) - len(DeltaGreek))
            resultframe["PV01"] = list(DeltaGreek["PV01"]) + [np.nan] * (len(resultframe) - len(DeltaGreek))                        
            GIRRDelta = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(DeltaGreek, "PV01Term","PV01"), 4)
            Cvup = list(np.array(CurveRate1) + 0.012)
            Pu = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvup, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            Cvdn = list(np.array(CurveRate1) - 0.012)
            Pd = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvdn, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    0.01,
                    hwvolterm, hwvol, HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
                    HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2,
                    HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag= L1_PhaseUseFlag,NumCpnOneYear_Leg1_Phase2=L1_NumCpnOneYear_P2,Leg1_Phase2StartDate= Phase2StartDate,Leg1_RefSwapRate_Multiple_Phase2=L1_RefRateMultiple_P2,Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,
                    Leg2_Phase2UseFlag= L2_PhaseUseFlag,NumCpnOneYear_Leg2_Phase2=L2_NumCpnOneYear_P2,Leg2_Phase2StartDate= Phase2StartDate,Leg2_RefSwapRate_Multiple_Phase2=L2_RefRateMultiple_P2,Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            GammaGreek = DeltaGreek.copy()
            GammaGreek.columns = ["Tenor","DeltaSensi"]
            GammaGreek["DeltaSensi"] = GammaGreek["DeltaSensi"] * 10000
            GammaGreek["Bucket"] ="KRW"
            GammaGreek["RiskWeight"] = GIRR_DeltaRiskWeight(list(DeltaGreek["PV01Term"].values), ["KRW"] * len(DeltaGreek), ["IRS"] * len(DeltaGreek))
            CVR_Plus = -(Pu - Result["Price"] - (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            CVR_Minus = -(Pd - Result["Price"] + (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            GIRRCurvature = max(abs(CVR_Plus), abs(CVR_Minus))
            T = DayCountAtoB(int(YYYYMMDD), SwapMaturity)/365
            if GreekFlag > 1 : 
                V = pd.Series(Result["VegaFRTB"], Result["VegaTerm"]).reset_index()
                V.columns = ["Tenor1","VegaSensi"]
                V["Tenor2"] = T - V["Tenor1"]
                V["Risk_Type"] = "Vega"
                V["Curve"] = UsedCurveName
                V["Risk_Class"] = "GIRR"
                V["Bucket"] = "KRW"
                GIRRVega = Calc_GIRRVega(V, SensitivityColumnName = "VegaSensi")["KB_M"].iloc[0]
            else : 
                V = pd.DataFrame([[1,0, 1.0, 0.0,'Vega',UsedCurveName,"GIRR",Curr]],columns = ['Tenor1','Tenor2','VegaSensi','Risk_Type','Curve','Risk_Class','Bucket'])
                GIRRVega = 0
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        resultframe = resultframe.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultframe.reset_index(), width = 100)
        if GreekFlag > 0 : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\nLeg1 Payoff: \n{L1ResultPayoff} (Ph1)\n{L1ResultPayoff_P2} (Ph2)\nLeg2 Payoff: \n{L2ResultPayoff} (Ph1)\n{L2ResultPayoff_P2} (Ph2)\nGIRR Delta: {np.round(GIRRDelta,4)}\nGIRR Curvature: {np.round(GIRRCurvature,4)}\nGIRR Vega: {np.round(GIRRVega,4)} ", font = ("맑은 고딕", 11, 'bold'))
        else : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\nLeg1 Payoff: \n{L1ResultPayoff} (Ph1)\n{L1ResultPayoff_P2} (Ph2)\nLeg2 Payoff: \n{L2ResultPayoff} (Ph1)\n{L2ResultPayoff_P2} (Ph2)", font = ("맑은 고딕", 11, 'bold'))

        #if BookFlag != 0 : 
        #    now = pd.Timestamp.now()
        #    timestamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:03d}"
        #    resultframe.to_csv(currdir + "\\Book\\StructuredSwap\\StructuredSwap_" + str(timestamp) + ".csv", index = False, encoding = "cp949")
        #    messagebox.showinfo("알림","Booking 완료!!")   

        if FRTBRawFlag != 0 : 
            FRTBRaw = ReadCSV(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv')
            DeltaFRTB = Calc_GIRRDeltaNotCorrelated_FromGreeks_PreProcessing(DeltaGreek, "PV01Term","PV01", Curvename = UsedCurveName, Type = "Rate", Bucket = Curr)
            DeltaFRTB['Depart'] = FRTBDepart
            DeltaFRTB['Portfolio'] = FRTBPort
            DeltaFRTB['RiskFactor1'] = UsedCurveName.replace(" ZeroCurve","")
            DeltaFRTB['RiskFactor2'] = DeltaFRTB["Tenor"]
            DeltaFRTB['RiskFactor3'] = DeltaFRTB["Type"]
            DeltaFRTB = DeltaFRTB[['Depart','Risk_Class','Risk_Type','Portfolio','Bucket',
                                   'RiskFactor1','RiskFactor2','RiskFactor3','Delta_Sensi']]
            GammaFRTB = DeltaFRTB.copy()
            GammaFRTB["Risk_Type"] = "Curvature"
            GammaFRTB["Value_Up"] = Pu
            GammaFRTB["Value_Dn"] = Pd
            GammaFRTB["Value"] = resultprice
            V['Vega_Sensi'] = V['VegaSensi']
            VolName = ''
            if 'KRW' in Curr : 
                VolName = 'KRW SWAPTION VOL'
            elif 'USD' in Curr : 
                VolName = 'USD SOFR SWAPTION'
            else : 
                VolName += Curr + ' SWAPTION VOL'
            V['RiskFactor1'] = VolName
            V['Depart'] = FRTBDepart
            V['Portfolio'] = FRTBPort            
            VegaFRTB = MapGIRRVegaGreeks(V, "Tenor1","Tenor2","Vega_Sensi","RiskFactor1")            
            FRTBRaw = pd.concat([FRTBRaw, DeltaFRTB,GammaFRTB,VegaFRTB],axis = 0)
            FRTBRaw.to_csv(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv', index = False, encoding = "cp949")
            messagebox.showinfo("알림","FRTB Raw 추가 완료!!")   

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 2, pady = 5, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 11).pack()
    output_label = tk.Label(Result_frame2, text = "", anchor = "n")
    output_label.pack(padx = 2, pady = 2)

    root.mainloop()
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, 1, 1, 1


def PricingIRStructuredSwapProgram2FDoublePhase(HolidayData, currdir) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                    namenotin = "vol",
                                                                    Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.",
                                                                    MultiSelection = False,
                                                                    DefaultStringList=["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    PriceDateDefault = int(YYYYMMDD)
    Curve = MyMarketDataList[0]
    UsedCurveName = Name[0].split("\\")[-1].split(".")[0]
    Curr = Name[0].split("\\")[-2].upper()
    CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    CalibrationFlag = False
    defaultkappa = 0.01
    defaultkappa2 = 0.01        

    YYYY = int(YYYYMMDD) // 10000
    root = tk.Tk()
    root.title("Callable Swap 2F Pricer(Single Phase)")
    root.geometry("1560x787+5+5")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 929)
    vb_Phase2Flag = make_listvariable_interface(left_frame, 'Phase2UseFlag', ["0: False","1: Phase2 USE"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_Phase2StartDate = make_variable_interface(left_frame, 'Phase2StartDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-9) * 10000 + 80000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'MaturityDate\n(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+21) * 10000 + 929)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = PriceDateDefault)
    vb_Holiday = make_listvariable_interface(left_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 4, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(center_frame, '연쿠폰지급수(Phase1)', ["0","1","2","4","6"], pady = 2, titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3)
    vb_L1_NumCpnOneYear_P2 = make_listvariable_interface(center_frame, '연쿠폰지급수(Phase2)', ["0","1","2","4","6"], pady = 2, listheight = 4, textfont = 10, defaultflag = True, defaultvalue=3)
    v_L1_FixedCpnRate_P1 = make_variable_interface(center_frame, '고정쿠폰(%)(Phase1)', bold = False, textfont = 11, pady = 2, defaultflag = True, defaultvalue =1.69)
    v_L1_FixedCpnRate_P2 = make_variable_interface(center_frame, '고정쿠폰(%)(Phase2)', bold = False, textfont = 10, pady = 2, defaultflag = True, defaultvalue =1.69)
    v_L1_RefSwapMaturity_T = make_variable_interface(center_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5, \n5Y-1Y -> 5-1)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11)
    vb_L1_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, '변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11)
    v_L1_RefRateMultiple_P1 = make_variable_interface(center_frame, '변동금리Multiple(Phase1)', bold = False, textfont = 11, pady = 2)
    v_L1_RefRateMultiple_P2 = make_variable_interface(center_frame, '변동금리Multiple(Phase2)', bold = False, textfont = 10, pady = 2)
    vb_L1_DayCount = make_listvariable_interface(center_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_L2_NumCpnOneYear_P1 = make_listvariable_interface(right_frame, '연쿠폰지급수(Phase1)', ["0","1","2","4","6"], pady = 2, titlelable = True, titleName = "Leg2 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue = 3)
    vb_L2_NumCpnOneYear_P2 = make_listvariable_interface(right_frame, '연쿠폰지급수(Phase2)', ["0","1","2","4","6"], pady = 2, listheight = 4, textfont = 10, defaultflag = True, defaultvalue = 3)
    v_L2_FixedCpnRate_P1 = make_variable_interface(right_frame, '고정쿠폰(%)(Phase1)', bold = False, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0.2)
    v_L2_FixedCpnRate_P2 = make_variable_interface(right_frame, '고정쿠폰(%)(Phase2)', bold = False, textfont = 10, pady = 2, defaultflag = True, defaultvalue = 0.2)
    v_L2_RefSwapMaturity_T = make_variable_interface(right_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5, \n5Y-1Y -> 5-1)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11, defaultflag = True ,defaultvalue = '5 - 1')
    vb_L2_RefSwapNCPNOneYear_P1 = make_listvariable_interface(right_frame, '변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_L2_RefRateMultiple_P1 = make_variable_interface(right_frame, '변동금리Multiple(Phase1)', bold = False, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 5.0)
    v_L2_RefRateMultiple_P2 = make_variable_interface(right_frame, '변동금리Multiple(Phase2)', bold = False, textfont = 10, pady = 2, defaultflag = True, defaultvalue = 5.0)
    vb_L2_DayCount = make_listvariable_interface(right_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_OptionHolder = make_listvariable_interface(rightright_frame, 'OptionHolder', ["0: Leg1 Hold Option","1: Leg2 Hold Option"], titleName = "Option Information", titlelable= True, listheight = 3, textfont = 11, defaultflag = True, defaultvalue= 0)
    v_FirstOptPayDate = make_variable_interface(rightright_frame, '첫 옵션행사일\n(지급일기준)', bold = False, textfont = 11, defaultflag = True, defaultvalue = (YYYY-6) * 10000 + 929)
    vb_NYearBetweenOptionPay = make_listvariable_interface(rightright_frame, '옵션행사간격', ["6M","12M","24M","36M","60M"], listheight = 5, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_NBDateBetweenOptionFixToPay = make_variable_interface(rightright_frame, '옵션행사선언일과\n옵션지급일사이의\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 20)
    v_MaxNumOpt = make_variable_interface(rightright_frame, '최대옵션개수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    v_L1FirstFixing = make_variable_interface(rightright_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_L2FirstFixing = make_variable_interface(rightright_frame, 'Leg2)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_GreekFlag = make_listvariable_interface(rightright_frame, 'Greek산출', ["0: Pricing만","1: Delta,Gamma","2: Delta,Gamma,Vega"], listheight = 3, textfont = 11)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(Result_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 12, textfont = 10)
    v_hwkappa = make_variable_interface(Result_frame, 'Kappa', bold = False, textfont = 11, titleName = "\nHull White Params", titlelable = True, defaultflag = True, defaultvalue = defaultkappa)
    v_hwkappa2 = make_variable_interface(Result_frame, 'Kappa2', bold = False, textfont = 11, defaultflag = True, defaultvalue = defaultkappa2)
    v_hwvol = make_variable_interface(Result_frame, 'Volatility1(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.99)
    v_hwvol2 = make_variable_interface(Result_frame, 'Volatility2(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0.66)
    v_hwfactorcorr = make_variable_interface(Result_frame, 'Factor Corr(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue = -0.1)
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)

    Result_frame2 = tk.Frame(root)
    Result_frame2.pack(side = 'left', padx = 1, pady = 5, anchor = 'n')
    vb_FRTBRaw = make_listvariable_interface(Result_frame2, 'BookFRTB', ["0: FRTB RAW 저장X","1: FRTB RAW 저장O"], listheight = 2, textfont = 11, pady = 10)
    vb_FRTBRawDepart = make_variable_interface(Result_frame2, '부서명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Derivatives Dept')
    vb_FRTBRawPort = make_variable_interface(Result_frame2, '포트명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Structured')
        
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]      
        Phase2Flag = int(str(vb_Phase2Flag.get(vb_Phase2Flag.curselection())).split(":")[0]) if vb_Phase2Flag.curselection() else 0            
        Phase2StartDate = int(v_Phase2StartDate.get()) if len(str(v_Phase2StartDate.get())) > 0 else (20200627 + 50000)  
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        L1_NumCpnOneYear_P2 = int(vb_L1_NumCpnOneYear_P2.get(vb_L1_NumCpnOneYear_P2.curselection())) if vb_L1_NumCpnOneYear_P2.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0

        if len(str(v_L1_FixedCpnRate_P2.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P2.get()) : 
                L1_FixedCpnRate_P2 = float(v_L1_FixedCpnRate_P2.get())/100
            else : 
                L1_FixedCpnRate_P2 = float(str(v_L1_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P2 = 0
        
        L1_PowerSpreadFlag = 0
        if len(str(v_L1_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L1_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L1_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_L1_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L1_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_L1_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_L1_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25
            
        L1_RefSwapNCPNOneYear_P1 = int(vb_L1_RefSwapNCPNOneYear_P1.get(vb_L1_RefSwapNCPNOneYear_P1.curselection())) if vb_L1_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        L1_RefRateMultiple_P1 = float(v_L1_RefRateMultiple_P1.get()) if len(str(v_L1_RefRateMultiple_P1.get())) > 0 else 0
        L1_RefRateMultiple_P2 = float(v_L1_RefRateMultiple_P2.get()) if len(str(v_L1_RefRateMultiple_P2.get())) > 0 else 0
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P1) + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"

        if L1_PowerSpreadFlag == True : 
            L1ResultPayoff_P2 = "(R(T=" + str(L1_RefSwapMaturity_T)+") - R(T=" + str(L1_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L1_RefRateMultiple_P2) + " + " +str(np.round(L1_FixedCpnRate_P2*100,4)) + "%"
        else : 
            L1ResultPayoff_P2 = "R(T=" + str(L1_RefSwapMaturity_T)+") x "+ str(L1_RefRateMultiple_P2) + " + " +str(np.round(L1_FixedCpnRate_P2*100,4)) + "%"
        
        L2_NumCpnOneYear_P1 = int(vb_L2_NumCpnOneYear_P1.get(vb_L2_NumCpnOneYear_P1.curselection())) if vb_L2_NumCpnOneYear_P1.curselection() else 4
        L2_NumCpnOneYear_P2 = int(vb_L2_NumCpnOneYear_P2.get(vb_L2_NumCpnOneYear_P2.curselection())) if vb_L2_NumCpnOneYear_P2.curselection() else 4
        if len(str(v_L2_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P1.get()) : 
                L2_FixedCpnRate_P1 = float(v_L2_FixedCpnRate_P1.get())/100
            else : 
                L2_FixedCpnRate_P1 = float(str(v_L2_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P1 = 0

        if len(str(v_L2_FixedCpnRate_P2.get())) > 0 : 
            if "%" in str(v_L2_FixedCpnRate_P2.get()) : 
                L2_FixedCpnRate_P2 = float(v_L2_FixedCpnRate_P2.get())/100
            else : 
                L2_FixedCpnRate_P2 = float(str(v_L2_FixedCpnRate_P2.get()).replace("%",""))/100
        else : 
            L2_FixedCpnRate_P2 = 0
        
        L2_PowerSpreadFlag = 0
        if len(str(v_L2_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_L2_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_L2_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_L2_RefSwapMaturity_T.get()).lower() : 
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_L2_RefSwapMaturity_T.get()).lower() :
                    L2_RefSwapMaturity_T = float(str(v_L2_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L2_RefSwapMaturity_T = float(v_L2_RefSwapMaturity_T.get()) 
                L2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T
        else : 
            L2_RefSwapMaturity_T = 0.25
            L2_RefSwapMaturity_T_PowerSpread = 0.25
            
        L2_RefSwapNCPNOneYear_P1 = int(vb_L2_RefSwapNCPNOneYear_P1.get(vb_L2_RefSwapNCPNOneYear_P1.curselection())) if vb_L2_RefSwapNCPNOneYear_P1.curselection() else 4
        if L2_RefSwapMaturity_T == 0.25 : 
            L2_RefSwapNCPNOneYear_P1 = 4
            
        L2_RefRateMultiple_P1 = float(v_L2_RefRateMultiple_P1.get()) if len(str(v_L2_RefRateMultiple_P1.get())) > 0 else 0
        L2_RefRateMultiple_P2 = float(v_L2_RefRateMultiple_P2.get()) if len(str(v_L2_RefRateMultiple_P2.get())) > 0 else 0
        L2_DayCount = int(str(vb_L2_DayCount.get(vb_L2_DayCount.curselection())).split(":")[0]) if vb_L2_DayCount.curselection() else (0 if L2_NumCpnOneYear_P1 != 0 else 3)
        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L2ResultPayoff = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P1) + " + " +str(np.round(L2_FixedCpnRate_P1*100,4)) + "%"

        if L2_PowerSpreadFlag == True : 
            L2ResultPayoff_P2 = "(R(T=" + str(L2_RefSwapMaturity_T)+") - R(T=" + str(L2_RefSwapMaturity_T_PowerSpread)+ ")) x "+ str(L2_RefRateMultiple_P2) + " + " +str(np.round(L2_FixedCpnRate_P2*100,4)) + "%"
        else : 
            L2ResultPayoff_P2 = "R(T=" + str(L2_RefSwapMaturity_T)+") x "+ str(L2_RefRateMultiple_P2) + " + " +str(np.round(L2_FixedCpnRate_P2*100,4)) + "%"

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        Holiday = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayData.columns : 
                HolidaysForSwap = HolidayData[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []
                            
        OptionHolder = int(str(vb_OptionHolder.get(vb_OptionHolder.curselection())).split(":")[0]) if vb_OptionHolder.curselection() else 0    
        FirstOptPayDate = int(v_FirstOptPayDate.get()) if len(str(v_FirstOptPayDate.get())) > 0 else SwapEffectiveDate + 10000
        NYearBetweenOptionPay = float(str(vb_NYearBetweenOptionPay.get(vb_NYearBetweenOptionPay.curselection())).split("M")[0])/12 if vb_NYearBetweenOptionPay.curselection() else 1    
        MaxNumOpt = int(v_MaxNumOpt.get()) if len(str(v_MaxNumOpt.get())) > 0 else -1
        NBDateBetweenOptionFixToPay = int(v_NBDateBetweenOptionFixToPay.get()) if len(str(v_NBDateBetweenOptionFixToPay.get())) > 0 else 0
        
        GreekFlag = int(str(vb_GreekFlag.get(vb_GreekFlag.curselection())).split(":")[0]) if vb_GreekFlag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0

        FRTBRawFlag = int(str(vb_FRTBRaw.get(vb_FRTBRaw.curselection())).split(":")[0]) if vb_FRTBRaw.curselection() else 0
        FRTBDepart = str(vb_FRTBRawDepart.get()) if len(str(vb_FRTBRawDepart.get())) > 0 else "TempDepart"
        FRTBPort = str(vb_FRTBRawPort.get()) if len(str(vb_FRTBRawPort.get())) > 0 else "TempPort"
        GreekFlag = 2 if FRTBRawFlag != 0 else GreekFlag                    

        hwkappa = float(v_hwkappa.get()) if len(str(v_hwkappa.get())) > 0 else 0.001
        hwvolterm = [1.0]
        hwkappa2 = float(v_hwkappa2.get()) if len(str(v_hwkappa2.get())) > 0 else 0.001
        hwvolterm2 = [1.0]
        hwfactorcorr = float(v_hwfactorcorr.get()) if len(str(v_hwfactorcorr.get())) > 0 else -0.001
        
        if len(str(v_hwvol.get())) > 0 : 
            if '(' in str(v_hwvol.get()) or ')' in str(v_hwvol.get()) : 
                volstr = str(v_hwvol.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol.get()) or ']' in str(v_hwvol.get()) :
                volstr = str(v_hwvol.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol.get()).split(',')
            hwvol = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol = [0.001]

        if len(str(v_hwvol2.get())) > 0 : 
            if '(' in str(v_hwvol2.get()) or ')' in str(v_hwvol2.get()) : 
                volstr = str(v_hwvol2.get()).replace("(","").replace(")","").split(',')
            elif '[' in str(v_hwvol2.get()) or ']' in str(v_hwvol2.get()) :
                volstr = str(v_hwvol2.get()).replace("[","").replace("]","").split(',')
            else : 
                volstr = str(v_hwvol2.get()).split(',')
            hwvol2 = list(np.vectorize(lambda x : float(x))(volstr))
        else : 
            hwvol2 = [0.001]

        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        L2FirstFixing = float(v_L2FirstFixing.get())/100 if str(v_L2FirstFixing.get()) else 0.0
        
        L1_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(365)]
        L1_FixingHistoryRate = [L1FirstFixing] * len(L1_FixingHistoryDate)    
        L2_FixingHistoryDate = [DayPlus(int(PriceDate) - 10000, i) for i in range(366)] 
        L2_FixingHistoryRate = [L2FirstFixing] * len(L2_FixingHistoryDate)  
        Pu = Pd = 0  
        OptionFixDate, OptionPayDate = Generate_OptionDate(FirstOptPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay, MaxNumOpt, ModifiedFollow = 0)
        if GreekFlag == 0 : 
            resultframe = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag = (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)
            resultprice = resultframe["ResultPrice"].iloc[0]
            GIRRDelta = 0
            GIRRCurvature = 0
            GIRRVega = 0
            
        else : 
            Result, resultframe = Pricing_IRCallableSwap_HWFDM_Greek(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,CurveRate1, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = LoggingFlag, 
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread,
                    GreekFlag = GreekFlag)
            resultprice = resultframe["ResultPrice"].iloc[0]
            
            DeltaGreek = pd.Series(Result["PV01"], index = CurveTerm1).reset_index()
            DeltaGreek.columns = ["PV01Term","PV01"]
            resultframe["PV01Term"] = list(DeltaGreek["PV01Term"]) + [np.nan] * (len(resultframe) - len(DeltaGreek))
            resultframe["PV01"] = list(DeltaGreek["PV01"]) + [np.nan] * (len(resultframe) - len(DeltaGreek))                        
            GIRRDelta = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(DeltaGreek, "PV01Term","PV01"), 4)
            Cvup = list(np.array(CurveRate1) + 0.012)
            Pu = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvup, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False,
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            Cvdn = list(np.array(CurveRate1) - 0.012)
            Pd = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, L1_NumCpnOneYear_P1,         
                    L1_RefRateMultiple_P1, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, L1_FixedCpnRate_P1, L1_DayCount, 
                    L2_NumCpnOneYear_P1, L2_RefRateMultiple_P1, L2_RefSwapMaturity_T, L2_RefSwapNCPNOneYear_P1, L2_FixedCpnRate_P1, 
                    L2_DayCount, OptionFixDate,OptionPayDate,OptionHolder,
                    CurveTerm1,Cvdn, L1_FixingHistoryDate, L1_FixingHistoryRate, L2_FixingHistoryDate, L2_FixingHistoryRate, 
                    hwkappa,
                    hwkappa2,
                    hwvolterm, hwvol, HWVolTerm2 = hwvolterm2, HWVol2 = hwvol2,
                    HWRho12Factor = hwfactorcorr, CpnRounding = 15, HW2FFlag = 1, LoggingFlag = False,
                    LoggingDir = currdir, Leg1_DiscCurveName = UsedCurveName, Leg1_EstCurveName = UsedCurveName, Leg2_DiscCurveName = UsedCurveName,
                    Leg2_EstCurveName = UsedCurveName, KoreanAutoHolidayFlag =  (Holiday == "KRW"), FixHolidays = HolidaysForSwap, PayHolidays = HolidaysForSwap,
                    Leg1_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg1_Phase2 = L1_NumCpnOneYear_P2, Leg1_Phase2StartDate = Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2 = L1_RefRateMultiple_P2, Leg1_FixedCpnRate_Phase2 = L1_FixedCpnRate_P2,   
                    Leg2_Phase2UseFlag = Phase2Flag, NumCpnOneYear_Leg2_Phase2 = L2_NumCpnOneYear_P2, Leg2_Phase2StartDate = Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2 = L2_RefRateMultiple_P2, Leg2_FixedCpnRate_Phase2 = L2_FixedCpnRate_P2,                    
                    Leg1_PowerSpreadFlag = L1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag = L2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = L2_RefSwapMaturity_T_PowerSpread)["ResultPrice"].iloc[0]
            GammaGreek = DeltaGreek.copy()
            GammaGreek.columns = ["Tenor","DeltaSensi"]
            GammaGreek["DeltaSensi"] = GammaGreek["DeltaSensi"] * 10000
            GammaGreek["Bucket"] ="KRW"
            GammaGreek["RiskWeight"] = GIRR_DeltaRiskWeight(list(DeltaGreek["PV01Term"].values), ["KRW"] * len(DeltaGreek), ["IRS"] * len(DeltaGreek))
            CVR_Plus = -(Pu - Result["Price"] - (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            CVR_Minus = -(Pd - Result["Price"] + (GammaGreek["DeltaSensi"] * GammaGreek["RiskWeight"]).sum())
            GIRRCurvature = max(abs(CVR_Plus), abs(CVR_Minus))
            T = DayCountAtoB(int(YYYYMMDD), SwapMaturity)/365
            if GreekFlag > 1 : 
                V = pd.Series(Result["VegaFRTB"], Result["VegaTerm"]).reset_index()
                V.columns = ["Tenor1","VegaSensi"]
                V["Tenor2"] = T - V["Tenor1"]
                V["Risk_Type"] = "Vega"
                V["Curve"] = UsedCurveName
                V["Risk_Class"] = "GIRR"
                V["Bucket"] = "KRW"
                GIRRVega = Calc_GIRRVega(V, SensitivityColumnName = "VegaSensi")["KB_M"].iloc[0]
            else : 
                V = pd.DataFrame([[1,0, 1.0, 0.0,'Vega',UsedCurveName,"GIRR",Curr]],columns = ['Tenor1','Tenor2','VegaSensi','Risk_Type','Curve','Risk_Class','Bucket'])
                GIRRVega = 0

        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        resultframe = resultframe.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultframe.reset_index(), width = 100)
        if GreekFlag > 0 : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff} (Ph1)\n{L1ResultPayoff_P2} (Ph2)\nLeg2 Payoff: \n{L2ResultPayoff} (Ph1)\n{L2ResultPayoff_P2} (Ph2)\nGIRR Delta: {np.round(GIRRDelta,4)}\nGIRR Curvature: {np.round(GIRRCurvature,4)}\nGIRR Vega: {np.round(GIRRVega,4)} ", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: {np.round(resultprice,4)}\n\nLeg1 Payoff: \n{L1ResultPayoff} (Ph1)\n{L1ResultPayoff_P2} (Ph2)\nLeg2 Payoff: \n{L2ResultPayoff} (Ph1)\n{L2ResultPayoff_P2} (Ph2)", font = ("맑은 고딕", 12, 'bold'))

        #if BookFlag != 0 : 
        #    now = pd.Timestamp.now()
        #    timestamp = now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond // 1000:03d}"
        #    resultframe.to_csv(currdir + "\\Book\\StructuredSwap\\StructuredSwap_" + str(timestamp) + ".csv", index = False, encoding = "cp949")
        #    messagebox.showinfo("알림","Booking 완료!!")   

        if FRTBRawFlag != 0 : 
            FRTBRaw = ReadCSV(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv')
            DeltaFRTB = Calc_GIRRDeltaNotCorrelated_FromGreeks_PreProcessing(DeltaGreek, "PV01Term","PV01", Curvename = UsedCurveName, Type = "Rate", Bucket = Curr)
            DeltaFRTB['Depart'] = FRTBDepart
            DeltaFRTB['Portfolio'] = FRTBPort
            DeltaFRTB['RiskFactor1'] = UsedCurveName.replace(" ZeroCurve","")
            DeltaFRTB['RiskFactor2'] = DeltaFRTB["Tenor"]
            DeltaFRTB['RiskFactor3'] = DeltaFRTB["Type"]
            DeltaFRTB = DeltaFRTB[['Depart','Risk_Class','Risk_Type','Portfolio','Bucket',
                                   'RiskFactor1','RiskFactor2','RiskFactor3','Delta_Sensi']]
            GammaFRTB = DeltaFRTB.copy()
            GammaFRTB["Risk_Type"] = "Curvature"
            GammaFRTB["Value_Up"] = Pu
            GammaFRTB["Value_Dn"] = Pd
            GammaFRTB["Value"] = resultprice
            V['Vega_Sensi'] = V['VegaSensi']
            VolName = ''
            if 'KRW' in Curr : 
                VolName = 'KRW SWAPTION VOL'
            elif 'USD' in Curr : 
                VolName = 'USD SOFR SWAPTION'
            else : 
                VolName += Curr + ' SWAPTION VOL'
            V['RiskFactor1'] = VolName
            V['Depart'] = FRTBDepart
            V['Portfolio'] = FRTBPort            
            VegaFRTB = MapGIRRVegaGreeks(V, "Tenor1","Tenor2","Vega_Sensi","RiskFactor1")            
            FRTBRaw = pd.concat([FRTBRaw, DeltaFRTB,GammaFRTB,VegaFRTB],axis = 0)
            FRTBRaw.to_csv(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv', index = False)
            messagebox.showinfo("알림","FRTB Raw 추가 완료!!")  

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 3, pady = 3, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 12).pack()
    output_label = tk.Label(Result_frame2, text = "", anchor = "n")
    output_label.pack(padx = 3, pady = 2)

    root.mainloop()
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, 1, 1, 1

def PricingRangeAccrualNote(HolidayDate, currdir) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\outputdata",MultiSelection=False, namenotin = "Vol", Comments="Pricing을 위한 ZeroCurve", DefaultStringList= ["IRS"])
    ZeroCurve = Data[0]
    ZeroTerm = ZeroCurve["Term"].astype(np.float64)
    ZeroRate = ZeroCurve["Rate"].astype(np.float64)

    ZeroCurveName = Name[0].split("\\")[-1].replace(".csv","")  
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namein = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False)] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))            
    root = tk.Tk()
    root.title("Range Accrual Note Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    vb_NominalFlag = make_listvariable_interface(left_frame, 'NominalFlag', ["0: Not Use","1: Use Nominal"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3))
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60))
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_SelectedCurve_P1 = make_listvariable_interface(left_frame, 'Swaption Vol 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "Swaption Info", defaultflag = True, defaultvalue = 0, width = 25, DefaultStringList=["Vol"])
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_RefSwapMaturity_T = make_variable_interface(center_frame, '기초금리 만기\n(3M-> 0.25, 5Y-> 5\n, 5Y-1Y-> 5-1)', bold = False, titlelable = True, titleName = "기초금리 정보입력", textfont = 11)
    v_CMSCorr = make_variable_interface(center_frame, 'Power Spread의 경우 \n상관계수', bold = False, textfont = 11, defaultflag = True, defaultvalue=0.87)
    vb_RefSwapNCPNOneYear_P1 = make_listvariable_interface(center_frame, '기초금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_FloorStrike = make_variable_interface(center_frame, 'Floor Strike Rate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0.00001)
    v_CapStrike = make_variable_interface(center_frame, 'Cap Strike Rate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=2.56)
    v_CpnRate = make_variable_interface(center_frame, 'CouponRate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=3.1)
    vb_VolFlag = make_listvariable_interface(center_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    vb_Holiday = make_listvariable_interface(center_frame, 'HolidayFlag', ["KRW","USD","JPY","EUR"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    vb_zerocurve = make_listvariable_interface(Result_frame, 'ZeroCurve(자동Load)', termratestr(ZeroTerm, ZeroRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    v_FixedAverage = make_variable_interface(Result_frame, 'Pre-Fixed \n Average Rate', bold = False, textfont = 11, defaultflag = True, defaultvalue=2.66)

    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    ResultDF = pd.DataFrame()
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultDF]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        DF = MyArrays[4]
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        CMSCorr = float(v_CMSCorr.get()) if len(str(v_CMSCorr.get())) > 0 else 0
        NominalFlag = int(str(vb_NominalFlag.get(vb_NominalFlag.curselection())).split(":")[0]) if vb_NominalFlag.curselection() else 1
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else (0 if NumCpnOneYear_P1 != 0 else 3)
        VolFlag = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 1
        Curr = str(vb_Holiday.get(vb_Holiday.curselection())).upper() if vb_Holiday.curselection() else "KRW"
        if 'KRW' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif "KRW" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else : 
            if Curr in HolidayDate.columns : 
                HolidaysForSwap = HolidayDate[Curr].unique().astype(np.int64)
            else : 
                HolidaysForSwap = []

        if len(str(v_CpnRate.get())) > 0 : 
            if "%" in str(v_CpnRate.get()) : 
                FixedCpnRate_P1 = float(v_CpnRate.get())/100
            else : 
                FixedCpnRate_P1 = float(str(v_CpnRate.get()).replace("%",""))/100
        else : 
            FixedCpnRate_P1 = 0

        L1_PowerSpreadFlag = 0
        if len(str(v_RefSwapMaturity_T.get())) > 0 :         
            if '-' in str(v_RefSwapMaturity_T.get()) : 
                SplitedStr = str(v_RefSwapMaturity_T.get()).split("-")
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
                if 'm' in str(v_RefSwapMaturity_T.get()).lower() : 
                    L1_RefSwapMaturity_T = float(str(v_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_RefSwapMaturity_T.get()).lower() :
                    L1_RefSwapMaturity_T = float(str(v_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    L1_RefSwapMaturity_T = float(v_RefSwapMaturity_T.get()) 
                L1_RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T
        else : 
            L1_RefSwapMaturity_T = 0.25
            L1_RefSwapMaturity_T_PowerSpread = 0.25

        L1_RefSwapNCPNOneYear_P1 = int(vb_RefSwapNCPNOneYear_P1.get(vb_RefSwapNCPNOneYear_P1.curselection())) if vb_RefSwapNCPNOneYear_P1.curselection() else 4
        if L1_RefSwapMaturity_T == 0.25 : 
            L1_RefSwapNCPNOneYear_P1 = 4

        PrevDateExl = YYYYMMDDToExcelDate(PriceDate) - 1
        PrevDate = ExcelDateToYYYYMMDD(PrevDateExl)
        RefRateHistoryDate = [PrevDate, PriceDate]

        FixedAvg = float(v_FixedAverage.get()) if len(str(v_FixedAverage.get())) > 0 else 0
        if FixedAvg > 0 : 
            FixedAvg = FixedAvg/100

        FloorStrike = float(v_FloorStrike.get()) if len(str(v_FloorStrike.get())) > 0 else 0.00001
        if FloorStrike > 0 : 
            FloorStrike = FloorStrike/100

        CapStrike = float(v_CapStrike.get()) if len(str(v_CapStrike.get())) > 0 else 1000
        if CapStrike > 0 : 
            CapStrike = CapStrike/100
        
        RefRateHistoryRate = [FixedAvg, FixedAvg]
        model = 'normal' if VolFlag == 1 else 'black'
        SelectedNumber = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        
        SwaptionVolRaw = ReadCSV(GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == SelectedNumber]["Directory"].iloc[0], True)
        SwaptionVolRawSetIndex = SwaptionVolRaw.astype(np.float64).set_index(SwaptionVolRaw.columns[0])
        SwaptionVolRawSetIndex.columns = SwaptionVolRawSetIndex.columns.astype(np.float64)
        VolatilitySurf = SwaptionVolRawSetIndex.values.astype(np.float64)
        VolatilityOptTerm = np.array(SwaptionVolRawSetIndex.columns, dtype = np.float64)/12
        VolatilitySwpTerm = np.array(SwaptionVolRawSetIndex.index, dtype = np.float64)/12
        if VolatilitySurf.min() > 0.5 : 
            VolatilitySurf = VolatilitySurf/100

        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
        DF = Pricing_RangeAccrualBond(PriceDate, SwapEffectiveDate, SwapMaturity, NumCpnOneYear_P1, Nominal,
                                NominalFlag, L1_RefSwapMaturity_T, L1_RefSwapNCPNOneYear_P1, FloorStrike, CapStrike,
                                FixedCpnRate_P1, DayCount, VolatilityOptTerm, VolatilitySwpTerm, VolatilitySurf,
                                ZeroTerm, ZeroRate, ZeroTerm, ZeroRate, Holidays = HolidaysForSwap, 
                                RefRateHistoryDate = RefRateHistoryDate, RefRateHistoryRate = RefRateHistoryRate, model = model,PowerSpreadFlag = L1_PowerSpreadFlag, RefSwapMaturity_T_PowerSpread = L1_RefSwapMaturity_T_PowerSpread, 
                                rho12= CMSCorr, Cap = 100, Floor = -100)
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        ResultDF = DF.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultDF, width = 60)
        
        #output_label.config(text = f"\n결과: {np.round(P,4)}({np.round(P/Nominal*100,4)}%)\n\nValue: \n{np.round(V)}\n\nForwardSwapRate: \n{np.round(F*100,4)}% \n사용된 변동성:\n{np.round(Vol*100,4)}%", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
        MyArrays[4] = DF

    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()     
    return 0, 0, 0, 0

def PricingEquityOptionProgram(currdir = os.getcwd(), HolidayDate = pd.DataFrame([])) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata', 
                                                                  namenotin = "waption",
                                                                  Comments = "옵션 Pricing을 위한 Zero 커브 번호 및 Volatility 번호를 입력하시오.\n  (반드시 ZeroCurve, Vol Data 2개 선택)\n ex : 1, 2",
                                                                  DefaultStringList= ["IRS","Vol"],
                                                                  namenotin2 = "Cap") 
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    print(curvename)    
    MyMarketDataList_ExceptVol = []
    NameList_ExceptVol = []
    N_EQVol = -1
    for i in range(len(Name)) : 
        if ("eq" in Name[i].lower() or "vol" in Name[i].lower()) and N_EQVol == -1: 
            N_EQVol = i
        else : 
            MyMarketDataList_ExceptVol.append(MyMarketDataList[i])
            NameList_ExceptVol.append(Name[i])

    VolData = MyMarketDataList[N_EQVol].set_index(MyMarketDataList[N_EQVol].columns[0])
    TermVol = np.array(VolData.columns, dtype = np.float64)
    ParityVol = np.array(VolData.index, dtype = np.float64)
    Vols2D = VolData.values.astype(np.float64)

    if len(NameList_ExceptVol) == 1 : 
        DiscTerm = MyMarketDataList_ExceptVol[0]["Term"]
        DiscRate = MyMarketDataList_ExceptVol[0]["Rate"]
        EstTerm = []
        EstRate = []
    else : 
        mystr = ""
        mystr += "  기초자산의 할인커브는 " + NameList_ExceptVol[0].split('\\')[-1] + ","
        mystr += "\n  레퍼런스커브는 " + NameList_ExceptVol[1].split('\\')[-1] + '\n 와 같이 세팅합니다. 맞습니까?(Y/N)\n->'
        myinput = input(mystr)
        if len(myinput) == 0 or myinput.lower() == 'y' : 
            DiscTerm = MyMarketDataList_ExceptVol[0]["Term"]
            DiscRate = MyMarketDataList_ExceptVol[0]["Rate"]
            EstTerm = MyMarketDataList_ExceptVol[1]["Term"]
            EstRate = MyMarketDataList_ExceptVol[1]["Rate"]            
        else :        
            DiscTerm = MyMarketDataList_ExceptVol[1]["Term"]
            DiscRate = MyMarketDataList_ExceptVol[1]["Rate"]
            EstTerm = MyMarketDataList_ExceptVol[0]["Term"]
            EstRate = MyMarketDataList_ExceptVol[0]["Rate"]            
             
    Preprocessing_ZeroTermAndRate(DiscTerm, DiscRate, int(YYYYMMDD))
    Preprocessing_ZeroTermAndRate(EstTerm, EstRate, int(YYYYMMDD))
    
    root = tk.Tk()
    root.title("Equity Option Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_StockOrForward = make_listvariable_interface(left_frame, '기초자산가격/선도가격여부\n(리스트에서 선택)', ["0: 기초자산가격","1: 선도가격"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    v_S = make_variable_interface(left_frame, '기초자산가격', bold = False, textfont = 11, defaultflag = True, defaultvalue=250)
    v_F = make_variable_interface(left_frame, '선도가격(사용할경우)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0)
    v_X = make_variable_interface(left_frame, '행사가격', bold = False, textfont = 11, defaultflag = True, defaultvalue=240)
    v_Maturity = make_variable_interface(left_frame, '옵션만기(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=int(YYYYMMDD)+10000)
    v_QuantoCorr = make_variable_interface(left_frame, 'QuantoCorr', bold = False, textfont = 11, titlelable= True, titleName = "QuantoInfo", defaultflag = True, defaultvalue=0)
    v_FXVol = make_variable_interface(left_frame, 'FXVol', bold = False, textfont = 11, defaultflag = True, defaultvalue=0)
    v_AvgStartDate = make_variable_interface(left_frame, '평균시작일\n(아시안옵션의경우입력)', bold = False, textfont = 11, defaultflag = True,titleName = "아시안옵션평가시입력", titlelable=True,defaultvalue=int(YYYYMMDD))
    v_AvgEndDate = make_variable_interface(left_frame, '평균종료일\n(아시안옵션의경우입력)', bold = False, textfont = 11, defaultflag = True,defaultvalue=int(YYYYMMDD)+10000)
    v_MeanPrice = make_variable_interface(left_frame, 'Fixed과거평균가격\n(아시안옵션의경우입력)', bold = False, textfont = 11, defaultflag = True, defaultvalue=250)
    
    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_Div = make_variable_interface(center_frame, '배당수익률(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0)
    v_c_or_p = make_listvariable_interface(center_frame, '콜(C)/풋(P)\n(리스트에서 선택)', ["C: Call","P: Put"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0)
    v_ATMVolFlag = make_listvariable_interface(center_frame, 'ATMVolFlag', ["0: Surface","1: ATMVol","2: 자체입력"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    v_SelfVol = make_variable_interface(center_frame, '자체입력Vol(%)', bold = True, textfont = 11, defaultflag = True, defaultvalue = 20)
    vb_zerocurve = make_listvariable_interface(center_frame, 'ZeroCurve(자동Load)', termratestr(DiscTerm, DiscRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    
    Right_frame = tk.Frame(root)
    Right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Plain0Barrier1Digital2 = make_listvariable_interface(Right_frame, '배리어옵션여부', ["0: 배리어사용X","1: 배리어옵션","2: 디지털옵션","3: AsianOption"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0, titlelable=True, titleName="배리어사용시입력")
    v_H = make_variable_interface(Right_frame, '배리어', bold = False, textfont = 11, defaultflag = True, defaultvalue=250)
    vb_Down0Up1Flag = make_listvariable_interface(Right_frame, 'Down0Up1Flag', ["0: Down","1: Up"], listheight = 2, textfont = 11,defaultflag = 0, defaultvalue = 0)
    vb_In0Out1Flag = make_listvariable_interface(Right_frame, 'In0Out1Flag', ["0: In","1: Out"], listheight = 2, textfont = 11,defaultflag = 0, defaultvalue = 0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)
    vb_FRTBRaw = make_listvariable_interface(Result_frame, 'BookFRTB', ["0: FRTB RAW 저장X","1: FRTB RAW 저장O"], listheight = 2, textfont = 11, pady = 10)
    vb_FRTBRawDepart = make_variable_interface(Result_frame, '부서명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Derivatives Dept')
    vb_FRTBRawPort = make_variable_interface(Result_frame, '포트명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'Structured')
    vb_FRTBStockName = make_variable_interface(Result_frame, '종목명', bold = False, textfont = 11, defaultflag = True, defaultvalue = 'KOSPI 200')
    vb_FRTBBucket = make_variable_interface(Result_frame, 'FRTB Bucket', bold = False, textfont = 11, defaultflag = True, defaultvalue=13)

    Value = 0
    Price, Delta, Gamma = None, None, None
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]   

        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        SelfVol = float(v_SelfVol.get())/100 if len(str(v_SelfVol.get())) > 0 else 0.2
        ForwardUseFlag = int(str(v_StockOrForward.get(v_StockOrForward.curselection())).split(":")[0]) if v_StockOrForward.curselection() else 0
        if ForwardUseFlag == 0 : 
            ForwardPrice = 0
        else : 
            ForwardPrice = float(v_F.get()) if len(str(v_F.get())) > 0 else 0 
        MeanPrice = float(v_MeanPrice.get()) if len(str(v_MeanPrice.get())) > 0 else 0
        AvgStartDate = int(v_AvgStartDate.get()) if len(str(v_AvgStartDate.get())) > 0 else int(YYYYMMDD)
        AvgEndDate = int(v_AvgEndDate.get()) if len(str(v_AvgEndDate.get())) > 0 else int(YYYYMMDD)+10000        
        
        S = float(v_S.get())
        X = float(v_X.get())
        H = float(v_H.get()) if len(str(v_H.get())) > 0 else 0.0001
        Maturity = float(v_Maturity.get()) if len(str(v_Maturity.get())) > 0 else (int(YYYYMMDD) + 10000)
        DivTerm = [0]
        if ForwardPrice > 0 : 
            DivRate = [0]
        else : 
            DivRate = [float(v_Div.get())/100] if len(str(v_Div.get())) > 0 else [0]
        QuantoCorr = float(v_QuantoCorr.get()) if len(str(v_QuantoCorr.get())) else 0
        FX_Vol = float(v_FXVol.get()) if len(str(v_FXVol.get())) else 0
        c_or_p = str(v_c_or_p.get(v_c_or_p.curselection())).split(":")[0] if v_c_or_p.curselection() else 'C'
        ATMVolFlag = int(str(v_ATMVolFlag.get(v_ATMVolFlag.curselection())).split(":")[0]) if v_ATMVolFlag.curselection() else 0
        VolsATM = []
        if ATMVolFlag == 1 : 
            if np.abs(ParityVol).max() < 10 : 
                for i in range(Vols2D.shape[1]) : 
                    VolsATM.append(np.interp(1, ParityVol, Vols2D[:,i]))
            else : 
                for i in range(Vols2D.shape[1]) : 
                    VolsATM.append(np.interp(S, ParityVol, Vols2D[:,i]))

        if c_or_p in ['c','C'] : 
            TypeFlag = 'c'
        else :
            TypeFlag = 'p'    
        VolsATMAry = np.array(VolsATM).reshape(1,-1)
        VolsATMParity = [1]    
        
        BarrierCall1Put2 = 1 if c_or_p == "C" else 2 
        Plain0Barrier1 = int(str(v_Plain0Barrier1Digital2.get(v_Plain0Barrier1Digital2.curselection())).split(":")[0]) if v_Plain0Barrier1Digital2.curselection() else 0
        Down0Up1Flag = int(str(vb_Down0Up1Flag.get(vb_Down0Up1Flag.curselection())).split(":")[0]) if vb_Down0Up1Flag.curselection() else 0
        In0Out1Flag = int(str(vb_In0Out1Flag.get(vb_In0Out1Flag.curselection())).split(":")[0]) if vb_In0Out1Flag.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        FRTBRawFlag = int(str(vb_FRTBRaw.get(vb_FRTBRaw.curselection())).split(":")[0]) if vb_FRTBRaw.curselection() else 0
        FRTBDepart = str(vb_FRTBRawDepart.get()) if len(str(vb_FRTBRawDepart.get())) > 0 else "TempDepart"
        FRTBPort = str(vb_FRTBRawPort.get()) if len(str(vb_FRTBRawPort.get())) > 0 else "TempPort"
        FRTBStockName = str(vb_FRTBStockName.get()) if len(str(vb_FRTBStockName.get())) > 0 else "StockA"
        FRTBBucket = int(vb_FRTBBucket.get()) if len(str(vb_FRTBBucket.get())) > 0 else 13
        Pu = 0
        PU_Curvature = PD_Curvature = 0
        v = Vega = 0.01
        risktype = ["price"]
        riskbucket = [str(FRTBBucket)]
        df = pd.DataFrame([risktype,riskbucket], index = ["Type","Bucket"]).T        
        EQRW = MapEquityRiskWeight(df, EQDeltaRWMappingDF, TypeColName = "Type", BucketColName = "Bucket").iloc[0]

        if Plain0Barrier1 == 0 : 
            Price, Delta, Gamma, Vega, Theta, Rho, v = BS_Option(int(PriceDate), int(Maturity), S, X, DiscTerm, 
                    DiscRate, DivTerm, DivRate, Vols2D if ATMVolFlag != 2 else SelfVol, QuantoCorr = QuantoCorr, 
                    FXVolTerm = [0], FXVol = [FX_Vol], DivFlag = 0, EstTerm = EstTerm, EstRate = EstRate, 
                    ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir, VolTerm = TermVol, VolParity = ParityVol,TypeFlag = TypeFlag, ATMVolFlag = ATMVolFlag, ATMVol = VolsATM)
            if FRTBRawFlag != 0 : 
                Pu, Delta_U, Gamma_U, Vega_U, Theta_U, Rho_U, v_U = BS_Option(int(PriceDate), int(Maturity), S * 1.01, X, DiscTerm, 
                        DiscRate, DivTerm, DivRate, Vols2D if ATMVolFlag != 2 else SelfVol, QuantoCorr = QuantoCorr, 
                        FXVolTerm = [0], FXVol = [FX_Vol], DivFlag = 0, EstTerm = EstTerm, EstRate = EstRate, 
                        ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir, VolTerm = TermVol, VolParity = ParityVol,TypeFlag = TypeFlag, ATMVolFlag = ATMVolFlag, ATMVol = VolsATM)
                PU_Curvature = BS_Option(int(PriceDate), int(Maturity), S * (1+EQRW), X, DiscTerm, 
                        DiscRate, DivTerm, DivRate, Vols2D if ATMVolFlag != 2 else SelfVol, QuantoCorr = QuantoCorr, 
                        FXVolTerm = [0], FXVol = [FX_Vol], DivFlag = 0, EstTerm = EstTerm, EstRate = EstRate, 
                        ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir, VolTerm = TermVol, VolParity = ParityVol,TypeFlag = TypeFlag, ATMVolFlag = ATMVolFlag, ATMVol = VolsATM)[0]
                PD_Curvature = BS_Option(int(PriceDate), int(Maturity), S * (1-EQRW), X, DiscTerm, 
                        DiscRate, DivTerm, DivRate, Vols2D if ATMVolFlag != 2 else SelfVol, QuantoCorr = QuantoCorr, 
                        FXVolTerm = [0], FXVol = [FX_Vol], DivFlag = 0, EstTerm = EstTerm, EstRate = EstRate, 
                        ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir, VolTerm = TermVol, VolParity = ParityVol,TypeFlag = TypeFlag, ATMVolFlag = ATMVolFlag, ATMVol = VolsATM)[0]

        elif Plain0Barrier1 == 1 : 
            Price, Delta, Gamma, Vega, Theta, Rho, v = BSBarrierOption(int(PriceDate), BarrierCall1Put2, S, X, H, DiscTerm, 
                                DiscRate, DiscTerm, DiscRate, DivTerm, DivRate, 
                                QuantoCorr, [0], [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, 
                                Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, int(Maturity), int(Maturity), 
                                Down0Up1Flag, In0Out1Flag, Reb = 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)
            if FRTBRawFlag != 0 : 
                Pu, Delta_U, Gamma_U, Vega_U, Theta_U, Rho_U, v_U = BSBarrierOption(int(PriceDate), BarrierCall1Put2, S * 1.01, X, H, DiscTerm, 
                                    DiscRate, DiscTerm, DiscRate, DivTerm, DivRate, 
                                    QuantoCorr, [0], [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, 
                                    Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, int(Maturity), int(Maturity), 
                                    Down0Up1Flag, In0Out1Flag, Reb = 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)
                PU_Curvature = BSBarrierOption(int(PriceDate), BarrierCall1Put2, S * (1+EQRW), X, H, DiscTerm, 
                                    DiscRate, DiscTerm, DiscRate, DivTerm, DivRate, 
                                    QuantoCorr, [0], [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, 
                                    Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, int(Maturity), int(Maturity), 
                                    Down0Up1Flag, In0Out1Flag, Reb = 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)[0]
                PD_Curvature = BSBarrierOption(int(PriceDate), BarrierCall1Put2, S * (1-EQRW), X, H, DiscTerm, 
                                    DiscRate, DiscTerm, DiscRate, DivTerm, DivRate, 
                                    QuantoCorr, [0], [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, 
                                    Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, int(Maturity), int(Maturity), 
                                    Down0Up1Flag, In0Out1Flag, Reb = 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)[0]

        elif Plain0Barrier1 == 2 : 
            Price, Delta, Gamma, Vega, Theta, Rho, v = BSDigitalOption(BarrierCall1Put2, int(PriceDate), int(Maturity), int(Maturity), S,
                                                                       X, DiscTerm, DiscRate, DiscTerm, DiscRate, 
                                                                       DivTerm, DivRate, TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 
                                                                       QuantoCorr, [0], [FX_Vol], 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)            
            if FRTBRawFlag != 0 : 
                Pu, Delta_U, Gamma_U, Vega_U, Theta_U, Rho_U, v_U = BSDigitalOption(BarrierCall1Put2, int(PriceDate), int(Maturity), int(Maturity), S * 1.01,
                                                                        X, DiscTerm, DiscRate, DiscTerm, DiscRate, 
                                                                        DivTerm, DivRate, TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 
                                                                        QuantoCorr, [0], [FX_Vol], 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)            
                PU_Curvature = BSDigitalOption(BarrierCall1Put2, int(PriceDate), int(Maturity), int(Maturity), S * (1+EQRW),
                                                                        X, DiscTerm, DiscRate, DiscTerm, DiscRate, 
                                                                        DivTerm, DivRate, TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 
                                                                        QuantoCorr, [0], [FX_Vol], 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)[0]            
                PD_Curvature = BSDigitalOption(BarrierCall1Put2, int(PriceDate), int(Maturity), int(Maturity), S * (1-EQRW),
                                                                        X, DiscTerm, DiscRate, DiscTerm, DiscRate, 
                                                                        DivTerm, DivRate, TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 
                                                                        QuantoCorr, [0], [FX_Vol], 0, ForwardPrice = ForwardPrice, LoggingFlag = LoggingFlag, LoggingDir = currdir)[0]            

        else : 
            Price, Delta, Gamma, Vega, Theta, Rho, v = Arithmetic_Asian_Opt_Pricing_Preprocessing(0, 0 if TypeFlag == 'c' else 1, int(PriceDate), AvgStartDate, AvgEndDate, 
                                                                                                  int(Maturity), S, X, MeanPrice, DiscTerm, 
                                                                                                  DiscRate, DivTerm, DivRate, QuantoCorr, [0], 
                                                                                                  [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, 
                                                                                                  Holidays = Holidays, ForwardTerm = [] if ForwardPrice == 0 else [1], ForwardPrice = [ForwardPrice])            
            if FRTBRawFlag != 0 : 
                Pu, Delta_U, Gamma_U, Vega_U, Theta_U, Rho_U, v_U = Arithmetic_Asian_Opt_Pricing_Preprocessing(0, 0 if TypeFlag == 'c' else 1, int(PriceDate), AvgStartDate, AvgEndDate, 
                                                                                                    int(Maturity), S*1.01, X, MeanPrice, DiscTerm, 
                                                                                                    DiscRate, DivTerm, DivRate, QuantoCorr, [0], 
                                                                                                    [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, 
                                                                                                    Holidays = Holidays, ForwardTerm = [] if ForwardPrice == 0 else [1], ForwardPrice = [ForwardPrice])            
                PU_Curvature = Arithmetic_Asian_Opt_Pricing_Preprocessing(0, 0 if TypeFlag == 'c' else 1, int(PriceDate), AvgStartDate, AvgEndDate, 
                                                                                                    int(Maturity), S*(1+EQRW), X, MeanPrice, DiscTerm, 
                                                                                                    DiscRate, DivTerm, DivRate, QuantoCorr, [0], 
                                                                                                    [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, 
                                                                                                    Holidays = Holidays, ForwardTerm = [] if ForwardPrice == 0 else [1], ForwardPrice = [ForwardPrice])[0]            
                PD_Curvature = Arithmetic_Asian_Opt_Pricing_Preprocessing(0, 0 if TypeFlag == 'c' else 1, int(PriceDate), AvgStartDate, AvgEndDate, 
                                                                                                    int(Maturity), S*(1-EQRW), X, MeanPrice, DiscTerm, 
                                                                                                    DiscRate, DivTerm, DivRate, QuantoCorr, [0], 
                                                                                                    [FX_Vol], TermVol, ParityVol if ATMVolFlag != 1 else VolsATMParity, Vols2D if ATMVolFlag == 0 else (VolsATMAry if ATMVolFlag != 2 else SelfVol), 0, 
                                                                                                    Holidays = Holidays, ForwardTerm = [] if ForwardPrice == 0 else [1], ForwardPrice = [ForwardPrice])[0]            
            
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        VolDF = VolData.reset_index().applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    

        PrevTreeFlag = insert_dataframe_to_treeview(tree, VolDF, width = 100)

        output_label.config(text = f"\n결과: {np.round(Price,4)}\nDelta: {np.round(Delta,4)}\nGamma: {np.round(Gamma,4)}\nVega: {np.round(Vega,4)}\nTheta: {np.round(Theta,4)}\nRho: {np.round(Rho,4)}\nFRTB EQ Delta:{np.round(Price*0.25,2)}\nFRTB EQ Vega:{np.round(np.array(Vols2D).mean() * Vega * 0.25,2)}\nFRTB EQ Curvature:{np.round(abs(Gamma * (S * 0.25 * S * 0.25 * 0.5) - Price*0.25),2)}\n변동성:\n{np.round(v*100,4)}%", font = ("맑은 고딕", 12, 'bold'))
        if FRTBRawFlag != 0 : 
            DeltaSensi = (Pu - Price)/0.01
            DeltaDF = pd.DataFrame([DeltaSensi], columns = ['Delta_Sensi'])
            DeltaDF["RiskFactor1"] = 'price'
            DeltaDF["RiskFactor2"] = FRTBStockName
            DeltaDF["RiskFactor3"] = FRTBStockName
            DeltaDF["Risk_Type"] = "Delta"
            GammaDF = pd.DataFrame([[DeltaSensi, PU_Curvature,PD_Curvature, Price]], columns = ["Delta_Sensi","Value_Up","Value_Dn","Value"])
            GammaDF["RiskFactor1"] = 'price'
            GammaDF["RiskFactor2"] = FRTBStockName
            GammaDF["RiskFactor3"] = FRTBStockName
            GammaDF["Risk_Type"] = "Curvature"
            VegaDF = pd.DataFrame([Vega * v], columns = ['Vega_Sensi'])
            tempf = lambda x : 0.5 if x < 0.51 else (1.0 if x < 1.01 else (3.0 if x < 3.01 else (5.0 if x < 5.01 else 10.00)))
            T = DayCountAtoB(int(PriceDate), int(Maturity))/365
            VegaDF["RiskFactor1"] = 'price'
            VegaDF["RiskFactor3"] = FRTBStockName
            VegaDF["RiskFactor2"] = tempf(T)            
            VegaDF["Risk_Type"] = "Vega"
            FRTBTarget = pd.concat([DeltaDF, GammaDF, VegaDF],axis = 0)
            FRTBTarget["Depart"] = FRTBDepart 
            FRTBTarget["Risk_Class"] = "EQR"
            FRTBTarget["Portfolio"] = FRTBPort 
            FRTBTarget["Bucket"] = FRTBBucket
            FRTBRaw = ReadCSV(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv')
            FRTBResult = pd.concat([FRTBRaw, FRTBTarget],axis = 0)
            FRTBResult.to_csv(currdir + '\\FRTBRAWFILE\\FRTB_RAW.csv', index = False)
            messagebox.showinfo("알림","FRTB Raw 추가 완료!!")   
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 15, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()            
            
    MainFlag2 = ""#input("\n종료하시겠습니까? (Y/N)\n->")

    return MainFlag2, Price, Delta, Gamma

def BS_CapFloor_Program(HolidayDate, currdir) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\outputdata",MultiSelection=False, namenotin = "Vol", Comments="Pricing을 위한 ZeroCurve", DefaultStringList=["IRS"])
    ZeroCurve = Data[0]
    ZeroTerm = ZeroCurve["Term"].astype(np.float64)
    ZeroRate = ZeroCurve["Rate"].astype(np.float64)
    
    ZeroCurveName = Name[0].split("\\")[-1].replace(".csv","")  
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    root = tk.Tk()
    root.title("Cap Floor Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3))
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60))
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_zerocurve = make_listvariable_interface(left_frame, 'ZeroCurve(자동Load)', termratestr(ZeroTerm, ZeroRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_DayCount = make_listvariable_interface(center_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)
    vb_CapFloorFlag = make_listvariable_interface(center_frame, 'Cap:0,Floor:1', ["0: Cap","1: Floor"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    vb_StrikeFlag = make_listvariable_interface(center_frame, '행사가격Flag', ["0: 직접입력","1: ATM","2: SwapRate"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    v_StrikePrice = make_variable_interface(center_frame, '(직접입력)\nStrike Rate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=2.56)
    vb_VolFlag = make_listvariable_interface(center_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    v_Vol = make_variable_interface(center_frame, '변동성(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0.99)
    v_FirstFixingRate = make_variable_interface(center_frame, '최근 Fixing Rate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=0)
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    Result = [0,0,0,0]
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, Result]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else EDate_YYYYMMDD(int(YYYYMMDD), 3)
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else 0
        CapFloorFlag = int(str(vb_CapFloorFlag.get(vb_CapFloorFlag.curselection())).split(":")[0]) if vb_CapFloorFlag.curselection() else 0    
        StrikeFlag = int(str(vb_StrikeFlag.get(vb_StrikeFlag.curselection())).split(":")[0]) if vb_StrikeFlag.curselection() else 0    
        StrikePrice = float(v_StrikePrice.get())/100 if len(str(v_StrikePrice.get())) > 0 else 0
        VolFlag = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 0    
        Vol = float(v_Vol.get())/100 if len(str(v_Vol.get())) > 0 else 0.01
        FirstFixingRate = 0 
        if PriceDate > SwapEffectiveDate : 
            FirstFixingRate = float(v_FirstFixingRate.get()) if len(str(v_FirstFixingRate.get())) > 0 else 0
        ResultValue = [0,0,0,0]
        Pricing_CapFloor(CapFloorFlag,PriceDate,SwapEffectiveDate,SwapMaturity,L1_NumCpnOneYear_P1,
                        Nominal,Vol,StrikePrice,0,ZeroTerm,
                        ZeroRate,DayCount,VolFlag,Holidays,FirstFixingRate,
                        0,StrikeFlag,ResultValue)  
        OptPrice = ResultValue[0]
        SwapRate = ResultValue[1]      
        output_label.config(text = f"\n결과: {np.round(OptPrice/Nominal*100,6)}%\nSwapRate: \n{np.round(SwapRate*100,6)}%\n행사가격:\n{np.round(StrikePrice*100,6)}%", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2     
        MyArrays[4] = ResultValue 
          
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()     
    return 0,0,0,0

def CapFloorCalibrationProgram(currdir) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\inputdata",MultiSelection=False, Comments="제너레이터를 위한 Cap데이터", DefaultStringList= ["Cap"])
    try : 
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
    except FileNotFoundError : 
        HolidayDate = []
    MyData = Data[0].astype(np.float64)
    Tenor = MyData["Tenor"]
    Quote = MyData["QuotePercent"].astype(np.float64)
    ZeroCurveName = Name[0]
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namenotin = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False)] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))                 
        
    Currency = Name[0].split("\\")[-2]
    ZeroCurveRawData = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Currency"] == Currency]

    root = tk.Tk()
    root.title("Swaption Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = False, textfont = 11, defaultflag = True, defaultvalue=int(YYYYMMDD))    
    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=100)    
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)    
    vb_CapFloorFlag = make_listvariable_interface(left_frame, 'CapFloorFlag', ["0: Cap","1: Floor"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    vb_Logging = make_listvariable_interface(left_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, pady = 10)
    v_SaveName = make_variable_interface(left_frame, '저장할 커브볼 명\n(ex: KRW Cap Vol)', bold = True, textfont = 11, defaultflag = True, defaultvalue="")

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_SelectedCurve_P1 = make_listvariable_interface(center_frame, 'ZeroCurve 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "MarketData Info", defaultflag = True, defaultvalue = 0, width = 50, DefaultStringList=["IRS"])
    vb_VolFlag = make_listvariable_interface(center_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    Result = [0,0,0,0]
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2,Result]

    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        NCPNOneYear = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCountFlag = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else 0
        CapFloorFlag = int(str(vb_CapFloorFlag.get(vb_CapFloorFlag.curselection())).split(":")[0]) if vb_CapFloorFlag.curselection() else 0
        VolFlag = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 0
        StrikeFlag = 2
        StrikePrice = 0
        NSelectedCurve = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        Holidays = HolidayDate[Currency].dropna() if Currency in HolidayDate.columns else []
        StartDate = NextNthBusinessDate(PriceDate, 1, Holidays)
        TenorYYYYMMDD = Tenor.apply(lambda x : EDate_YYYYMMDD(StartDate, int(x)) if float(x) < 1200 else (ExcelDateToYYYYMMDD(x) if float(x) < 19000101 else float(x)))
        CurveDirectory = ZeroCurveRawData[ZeroCurveRawData["Number"] == NSelectedCurve]["Directory"].iloc[0]
        CurveInfo = ReadCSV(CurveDirectory, True)
        ZeroTerm = CurveInfo["Term"].apply(lambda x : str(x).replace("-","")).astype(np.float64)
        ZeroRate = CurveInfo["Rate"].astype(np.float64)
        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
        NA = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 100
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        SaveName = str(v_SaveName.get()) if len(str(v_SaveName.get())) > 0 else "TempCapVol"

        ResultData, ResultCapFloorImvol, FwdSwpRate, Calibration = CapFloorToImpliedVol(ZeroTerm, ZeroRate, PriceDate, StartDate, TenorYYYYMMDD, 
                                                        Quote, StrikePrice, NCPNOneYear, CapFloorFlag, NA, 
                                                        DayCountFlag, VolFlag, Holidays)

        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        ResultData["FwdSwpRate"] = FwdSwpRate
        ResultData = ResultData.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, (ResultData*100).round(4).reset_index(), width = 80)
        SaveYN, SaveDir = 0, ""
        if LoggingFlag > 0 : 
            if YYYYMMDD not in os.listdir(currdir + "\\MarketData\\outputdata") : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(PriceDate))
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(PriceDate) + "\\" + Currency)    
                    
            cvname = SaveName
            targetdir = currdir + "\\MarketData\\outputdata\\" + str(PriceDate) + "\\" + str(Currency)
            print("\n저장시도\n")
            try : 
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultData.to_csv(TheName, index = True, encoding = "cp949")
                    SaveYN = 1
                    SaveDir = TheName
                    print("\n저장완료\n")
            except FileNotFoundError : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(PriceDate) + "\\" + Currency)    
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultData.to_csv(TheName, index = True, encoding = "cp949")
                    SaveYN = 1
                    SaveDir = TheName
                    print("\n저장완료\n")

        output_label.config(text = f"\n결과: {Calibration}\n저장:{SaveYN}\n저장경로:\n{SaveDir}", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
        MyArrays[4] = ResultCapFloorImvol
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()     
    return 0,0,0,0        

def BS_Swaption_Program(HolidayDate, currdir) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\outputdata",MultiSelection=False, namenotin = "Vol", Comments="Pricing을 위한 ZeroCurve", DefaultStringList= ["IRS"])
    ZeroCurve = Data[0]
    ZeroTerm = ZeroCurve["Term"].astype(np.float64)
    ZeroRate = ZeroCurve["Rate"].astype(np.float64)
    
    ZeroCurveName = Name[0].split("\\")[-1].replace(".csv","")  
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namein = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False)] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))            

    root = tk.Tk()
    root.title("Swaption Pricer")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3))
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60))
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_SelectedCurve_P1 = make_listvariable_interface(center_frame, 'Swaption Vol 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "Swaption Info", defaultflag = True, defaultvalue = 0, width = 50, DefaultStringList=["Vol"])
    vb_DayCount = make_listvariable_interface(center_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)
    vb_FixedPayer0Receiver1 = make_listvariable_interface(center_frame, 'FixedPayer:0,Receiver:1', ["0: Fixed Payer Swaption","1: Fixed Receive Swaption"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0)
    v_StrikePrice = make_variable_interface(center_frame, 'Strike Rate(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue=2.56)
    vb_VolFlag = make_listvariable_interface(center_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=1)
    
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    vb_zerocurve = make_listvariable_interface(Result_frame, 'ZeroCurve(자동Load)', termratestr(ZeroTerm, ZeroRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)

    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else EDate_YYYYMMDD(int(YYYYMMDD), 3)
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else EDate_YYYYMMDD(int(YYYYMMDD), 3 + 60)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)
        FixedPayer0Receiver1 = int(str(vb_FixedPayer0Receiver1.get(vb_FixedPayer0Receiver1.curselection())).split(":")[0]) if vb_FixedPayer0Receiver1.curselection() else 0    
        StrikePrice = float(v_StrikePrice.get())/100 if len(str(v_StrikePrice.get())) > 0 else 0
        SelectedNumber = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        BSVol0NormalVol1 = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 1
        
        NMonthOpt = DayCountAtoB(PriceDate, SwapEffectiveDate)/365*12
        NMonthSwap = DayCountAtoB(SwapEffectiveDate, SwapMaturity)/365*12
        SwaptionVolRaw = ReadCSV(GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == SelectedNumber]["Directory"].iloc[0], True)
        SwaptionVolRawSetIndex = SwaptionVolRaw.astype(np.float64).set_index(SwaptionVolRaw.columns[0])
        SwaptionVolRawSetIndex.columns = SwaptionVolRawSetIndex.columns.astype(np.float64)
        SwaptionVolArray = SwaptionVolRawSetIndex.values.astype(np.float64)
        Vol = Linterp2D(list(SwaptionVolRawSetIndex.columns), list(SwaptionVolRawSetIndex.index), SwaptionVolArray,NMonthOpt, NMonthSwap)

        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)

        ResultDict = BS_Swaption(PriceDate, SwapEffectiveDate, SwapMaturity, L1_NumCpnOneYear_P1, Nominal, Vol, StrikePrice, ZeroTerm, ZeroRate, DayCountFracFlag = DayCount, VolFlag = BSVol0NormalVol1, HolidaysFixing = Holidays, HolidaysPay = Holidays, NBDayFromEndDateToPay = 0, FixedPayer0Receiver1 = FixedPayer0Receiver1)
        P = ResultDict["Price"]
        V = ResultDict["Value"]
        F = ResultDict["ForwardSwapRate"]
        X = ResultDict["ExerciseValue"]        
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        SwaptionVolRawSetIndex = SwaptionVolRawSetIndex.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, (SwaptionVolRawSetIndex*100).round(2).reset_index(), width = 80)

        output_label.config(text = f"\n결과: {np.round(P,4)}({np.round(P/Nominal*100,4)}%)\n\nValue: \n{np.round(V)}\n\nForwardSwapRate: \n{np.round(F*100,4)}% \n사용된 변동성:\n{np.round(Vol*100,4)}%", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()     
    return 0,0,0,0

def PricingBondProgram(HolidayDate = pd.DataFrame([]), currdir = os.getcwd()) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata', 
                                                                  namenotin = "vol",
                                                                  Comments = "채권 Pricing을 위한 커브 번호를 입력하시오.",
                                                                  MultiSelection = False, defaultvalue=-1, DefaultStringList=["CORP"]) 
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    print(curvename)    
    if len(MyMarketDataList) == 1 : 
        Curve = MyMarketDataList[0]
        UsedCurveName = Name[0]
    elif len(MyMarketDataList) == 0 : 
        MainFlag2 = MainViewer(Title = 'Continue', MyText = '해당 폴더에 MarketData가 없습니다\n종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+30+30", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        return MainFlag2, "","",""
    else : 
        print("\n     채권을 평가하기 위해 사용할 커브 번호를 입력하세요.\n")        
        n = int(input())
        Curve = MyMarketDataList[n-1]
        UsedCurveName = Name[n-1]
    Curr = UsedCurveName.split("\\")[-2].lower()
    HolidaysForSwap = []
    YYYY = int(YYYYMMDD) // 10000
    if 'krw' in Curr : 
        HolidaysForSwap = KoreaHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
    elif "usd" in Curr : 
        HolidaysForSwap = USHolidaysFromStartToEnd(YYYY-1, YYYY + 60)            
    else : 
        if Curr.upper() in HolidayDate.columns : 
            HolidaysForSwap = list(HolidayDate[Curr.upper()].values)
        else : 
            HolidaysForSwap = []
        
    CurveTerm = list(Curve["Term" if "Term" in Curve.columns else "term"])
    CurveRate = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
    
    root = tk.Tk()
    root.title("Bond Pricer(Single Phase)")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Nominal = make_variable_interface(left_frame, 'Nominal Amount', bold = False, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-1) * 10000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+19) * 10000 + 929)
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], titlelable = True, titleName = "Leg1 Information", listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    v_SwapMaturityToPayDate = make_variable_interface(left_frame, '기말일TO지급일까지영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 2)
    v_L1_FixedCpnRate_P1 = make_variable_interface(left_frame, 'Leg1 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =2.79)
    v_FloatFlag = make_variable_interface(left_frame, '변동금리채여부(0 or 1)', bold = False, textfont = 11, defaultflag = True, defaultvalue = 0)
    vb_L1_DayCount = make_listvariable_interface(left_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_L1FirstFixing = make_variable_interface(center_frame, 'Leg1)최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_zerocurve = make_listvariable_interface(center_frame, 'ZeroCurve(자동Load)', termratestr(CurveTerm, CurveRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    v_YTMRate = make_variable_interface(center_frame, 'YTM금리(%)\n(YTM평가시 입력)', bold = False, textfont = 11)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)
    vb_Book = make_listvariable_interface(Result_frame, 'Book', ["0: Book 안함","1: Booking"], listheight = 2, textfont = 11, pady = 10)
    vb_CSRBucket = make_listvariable_interface(Result_frame, 'CSRBucket', ["1: 정부,중앙은행","2: 지방정부, 공공행정","3: 금융","4: 원자재","5: 소비재","6: 기술통신"], listheight = 4, textfont = 11, pady = 10)

    Value = 0
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        SwapMaturityToPayDate = int(v_SwapMaturityToPayDate.get()) if len(str(v_SwapMaturityToPayDate.get())) > 0 else 0
        FloatFlag= int(v_FloatFlag.get()) if len(str(v_FloatFlag.get())) > 0 else 0
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_L1_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_L1_FixedCpnRate_P1.get()) : 
                L1_FixedCpnRate_P1 = float(v_L1_FixedCpnRate_P1.get())/100
            else : 
                L1_FixedCpnRate_P1 = float(str(v_L1_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            L1_FixedCpnRate_P1 = 0
        if FloatFlag > 0 :
            L1ResultPayoff = "R(T) x 1" + " + " +str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
        else : 
            L1ResultPayoff = str(np.round(L1_FixedCpnRate_P1*100,4)) + "%"
            
        L1_DayCount = int(str(vb_L1_DayCount.get(vb_L1_DayCount.curselection())).split(":")[0]) if vb_L1_DayCount.curselection() else 0
        
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20240627
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        BookFlag = int(str(vb_Book.get(vb_Book.curselection())).split(":")[0]) if vb_Book.curselection() else 0
        Bucket= int(str(vb_CSRBucket.get(vb_CSRBucket.curselection())).split(":")[0]) if vb_CSRBucket.curselection() else 1
        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0
        YTMRate = float(v_YTMRate.get())/100 if str(v_YTMRate.get()) else 0.0
        YTMFlag = YTMRate > 0
        T = DayCountFractionAtoB(int(PriceDate),SwapMaturity, L1_DayCount)
        ErrorFlag, ErrorString = Calc_Schedule_ErrorCheck(Nominal, SwapEffectiveDate, int(PriceDate), SwapMaturity, CurveTerm, 
                              CurveRate, L1_NumCpnOneYear_P1, L1_DayCount)
        AIList = [0]
        if ErrorFlag == 0 : 
            Value, PV01, TempPV01 = Calc_Bond_PV01(Nominal, 1, FloatFlag, L1FirstFixing, SwapEffectiveDate, 
                    int(PriceDate), SwapMaturity, L1_FixedCpnRate_P1, CurveTerm if YTMFlag == 0 else [T], CurveRate if YTMFlag == 0 else [YTMRate], 
                    L1_NumCpnOneYear_P1, L1_DayCount+5, KoreanHoliday = False, MaturityToPayDate = SwapMaturityToPayDate, EstZeroCurveTerm = [],
                    EstZeroCurveRate = [], FixingHolidayList = HolidaysForSwap, AdditionalPayHolidayList  = HolidaysForSwap, NominalDateIsNominalPayDate = False,
                    LoggingFlag = LoggingFlag, LoggingDir = currdir, ModifiedFollow = 1, DiscCurveName = UsedCurveName, YTMPricing=YTMFlag, AIList = AIList)         
            GIRRRisk = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01, "PV01Term","PV01"), 2 if Value > 10000 else 4)
            CSRRisk, BKT = Calc_CSRDeltaNotCorrelated_FromGreeks(PV01, "PV01Term","PV01", Bucket)
            CSRRisk = np.round(CSRRisk, 2 if Value > 10000 else 4)
            if PrevTreeFlag == 0 : 
                tree = ttk.Treeview(root)
            else : 
                tree.destroy()
                scrollbar.destroy()
                scrollbar2.destroy()
                tree = ttk.Treeview(root)
            PV01 = PV01.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
            tree.pack(padx=5, pady=5, fill="both", expand=True)
            scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
            scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.configure(xscrollcommand=scrollbar2.set)
            scrollbar.pack(side="right", fill="y")    
            scrollbar2.pack(side="bottom", fill="x")    
            
            PrevTreeFlag = insert_dataframe_to_treeview(tree, PV01.reset_index(), width = 100)
            if BookFlag in ["y","Y","1",1] : 
                GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
                Data_GIRR = MapGIRRDeltaGreeks(PV01.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                GIRR = pd.DataFrame([list(Data_GIRR["GIRR_Delta_Sensi"])], columns = list(Data_GIRR["GIRR_Tenor"].apply(lambda x : "GIRR1_" + str(x))))
                CSR_RiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)
                Data_CSR = MapCSRDeltaGreeks(PV01.set_index("PV01Term")["PV01"], CSR_RiskFactor).reset_index()
                Data_CSR.columns = ["CSR_Tenor","CSR_Delta_Sensi"]
                CSR = pd.DataFrame([list(Data_CSR["CSR_Delta_Sensi"])], columns = list(Data_CSR["CSR_Tenor"].apply(lambda x : "CSR1_" + str(x))))
                
                df_pre = ReadCSV(currdir + "\\Book\\Bond\\Bond.csv")
                MyCol = ["Nominal","FloatFlag","FixingRate","EffectiveDate","EndDate",
                        "NBDFromEndDateToPayDate","CpnRate","NumCpnOneYear","DayCountFlag","ModifiedFollowing",
                        "DiscCurveName","EstCurveName","Currency","Holiday","MTM","PriceDate","CsrBucket"]
                Contents = [Nominal, FloatFlag, L1FirstFixing, SwapEffectiveDate, SwapMaturity, 
                            SwapMaturityToPayDate, L1_FixedCpnRate_P1, L1_NumCpnOneYear_P1, L1_DayCount, 1, 
                            UsedCurveName.split("\\")[-1], UsedCurveName.split("\\")[-1], UsedCurveName.split("\\")[-2], UsedCurveName.split("\\")[-2], Value, YYYYMMDD, str(BKT)]
                data2 = pd.DataFrame([Contents], columns = MyCol)
                data2 = pd.concat([data2, GIRR, CSR],axis = 1)
                df = pd.concat([df_pre, data2],axis = 0)
                df.index = np.arange(len(df))
                df.to_csv(currdir + "\\Book\\Bond\\Bond.csv", index = False, encoding = "cp949")    
                messagebox.showinfo("알림","Booking 완료!!")        
            output_label.config(text = f"\n결과: {np.round(Value,4)}\nAccrued Interest: \n{np.round(AIList[0],4)}\nLeg1 Payoff: \n{L1ResultPayoff}\nGIRR: \n{GIRRRisk}\nCSR: \n{CSRRisk}\nBooking = {bool(BookFlag)}", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: \n{ErrorString}", font = ("맑은 고딕", 12, 'bold'))
            
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()
    
    MainFlag2 = 0
    return MainFlag2, Value, PV01, TempPV01

def PricingIRSProgram(HolidayData = pd.DataFrame([]), FXData = pd.DataFrame([]) , ComplexIRSFlag = 0, CMSUseFlag = 0) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                  namenotin = "vol",
                                                                  Comments = "IRS Pricing을 위한 커브 번호를 입력하시오.\n(Estimation Curve와 Discount Curve가 다른 경우 1, 2 등 두개 입력)",DefaultStringList = ["IRS"])     
    curvename = PrintingMarketDataInformation(YYYYMMDD, Name, MyMarketDataList)
    print(curvename)  
    HolidaysForSwap = []
    Curr, UsedCurveName1 = "", ""
    YYYY = int(YYYYMMDD) // 10000
    if len(MyMarketDataList) == 1 : 
        Curve = MyMarketDataList[0]
        UsedCurveName1 = Name[0]
        Curr = Name[0].split("\\")[-2].lower()
        if 'krw' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
        elif "usd" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
        CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
        CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
        CurveTerm2, CurveRate2 = CurveTerm1, CurveRate1     
        UsedCurveName2 = UsedCurveName1
    else : 
        Curve, Curve2 = MyMarketDataList[0], MyMarketDataList[1]
        UsedCurveName1, UsedCurveName2 = Name[0], Name[1]
        if "STD" not in Name[0].upper() and "IRS" not in Name[0].upper() and "OIS" not in Name[0].upper() :
            Curve, Curve2 = MyMarketDataList[1], MyMarketDataList[0]
            UsedCurveName1, UsedCurveName2 = Name[1], Name[0]
             
        Curr = Name[0].split("\\")[-2].lower()
        if 'krw' in Curr : 
            HolidaysForSwap = KoreaHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
        elif "usd" in Curr : 
            HolidaysForSwap = USHolidaysFromStartToEnd(YYYY-1, YYYY + 60)
        CurveTerm1 = list(Curve["Term" if "Term" in Curve.columns else "term"])
        CurveRate1 = list(Curve["Rate" if "Rate" in Curve.columns else "rate"])
        CurveTerm2 = list(Curve2["Term" if "Term" in Curve2.columns else "term"]) 
        CurveRate2 = list(Curve2["Rate" if "Rate" in Curve2.columns else "rate"])
        
    if len(HolidayData) > 0 : 
        if Curr.upper() in HolidayData.columns : 
            HolidaysForSwap = list(HolidayData[Curr.upper()].dropna().unique())    
    if CMSUseFlag == True : 
        YYYYMMDD2, Name2, MyMarketDataList2 = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',
                                                                        namein = "tion",
                                                                        Comments = "Convexity Adjustment를 위한 Swaption Vol Curve를 선택하시오\n->",
                                                                        MainComments = "\nCMS, CMT Pricing을 위해 Volatility 마켓데이터를 선택해야합니다.",MultiSelection=False,DefaultStringList=["Vol"])     
    else : 
        YYYYMMDD2, Name2, MyMarketDataList2 = YYYYMMDD, Name, MyMarketDataList                    

    root = tk.Tk()
    root.title("IRS Pricer(Single Phase)")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-1)*10000+929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+19)*10000+929)
    vb_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    v_SwapMaturityToPayDate = make_variable_interface(left_frame, '기말일TO지급일까지영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 2)
    vb_FixedPayer = make_listvariable_interface(left_frame, '변동금리 수취여부', ["0: 고정수취, 변동지급","1: 변동수취, 고정지급"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue = 1)
    v_FixedCpnRate_P1 = make_variable_interface(left_frame, '고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =2.427565)
    if CMSUseFlag == True : 
        v_RefSwapMaturity_T = make_variable_interface(left_frame, '변동금리 만기\n(3M-> 0.25, 5Y-> 5)', bold = False, titlelable = True, titleName = "변동금리 사용의 경우\n아래 데이터 입력", textfont = 11)
        vb_RefSwapNCPNOneYear_P1 = make_listvariable_interface(left_frame, '변동금리의 \n연 쿠폰지급수', ["1","2","4","6"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 2)
    else : 
        v_RefSwapMaturity_T, vb_RefSwapNCPNOneYear_P1 = None, None        
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Nominal = make_variable_interface(center_frame, 'Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(center_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_L1FirstFixing = make_variable_interface(center_frame, '최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    vb_zerocurve = make_listvariable_interface(center_frame, 'ZeroDiscCurve(자동Load)', termratestr(CurveTerm1, CurveRate1), titleName = "MARKET DATA INFO", titlelable= True, listheight = 11, textfont = 11)
    vb_zerocurve2 = make_listvariable_interface(center_frame, 'ZeroEstCurve(자동Load)', termratestr(CurveTerm2, CurveRate2), listheight = 11, textfont = 11)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_LookBackDays = make_variable_interface(right_frame, 'LookBackDays', bold = False, textfont = 11, titleName = "SOFR설정(필요시입력)", titlelable= True, defaultflag = True, defaultvalue = 0)
    vb_ObservShift = make_listvariable_interface(right_frame, 'ObservShift', ["0: FALSE","1: TRUE"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue= 0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, titleName="Pricing Result",titlelable=True, pady = 10)
    vb_Book = make_listvariable_interface(Result_frame, 'Book', ["0: Book 안함","1: Booking"], listheight = 2, textfont = 11, pady = 10)
    Value = 0
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        VolSearch = 0
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        SwapMaturityToPayDate = int(v_SwapMaturityToPayDate.get()) if len(str(v_SwapMaturityToPayDate.get())) > 0 else 0

        FixedPayer = int(str(vb_FixedPayer.get(vb_FixedPayer.curselection())).split(":")[0]) if vb_FixedPayer.curselection() else 1
        NumCpnOneYear_P1 = int(vb_NumCpnOneYear_P1.get(vb_NumCpnOneYear_P1.curselection())) if vb_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_FixedCpnRate_P1.get()) : 
                FixedCpnRate_P1 = float(v_FixedCpnRate_P1.get())/100
            else : 
                FixedCpnRate_P1 = float(str(v_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            FixedCpnRate_P1 = 0
            
        if CMSUseFlag == True : 
            if len(str(v_RefSwapMaturity_T.get())) > 0 :         
                if 'm' in str(v_RefSwapMaturity_T.get()).lower() : 
                    RefSwapMaturity_T = float(str(v_RefSwapMaturity_T.get()).split('m')[0])/12
                elif 'y' in str(v_RefSwapMaturity_T.get()).lower() :
                    RefSwapMaturity_T = float(str(v_RefSwapMaturity_T.get()).split('y')[0])
                else :
                    RefSwapMaturity_T = float(v_RefSwapMaturity_T.get()) 
            else : 
                RefSwapMaturity_T = 0.25
            RefSwapNCPNOneYear_P1 = int(vb_RefSwapNCPNOneYear_P1.get(vb_RefSwapNCPNOneYear_P1.curselection())) if vb_RefSwapNCPNOneYear_P1.curselection() else 4
        else : 
            RefSwapMaturity_T = 0.25
            RefSwapNCPNOneYear_P1 = 4
        if FixedPayer == 1 : 
            if CMSUseFlag == True  : 
                ResultPayoff = "R(T="+ str(np.round(RefSwapMaturity_T, 2))+") x 1" + " - " +str(np.round(FixedCpnRate_P1*100,4)) + "%"
            else : 
                ResultPayoff = "R(T) x 1" + " - " +str(np.round(FixedCpnRate_P1*100,4)) + "%"
        else : 
            ResultPayoff = str(np.round(FixedCpnRate_P1*100,4)) + "% - R(T) x 1"
            
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else 0
        
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        LookBackDays = int(v_LookBackDays.get()) if len(str(v_LookBackDays.get())) > 0 else 0
        ObservShift = int(str(vb_Logging.get(vb_ObservShift.curselection())).split(":")[0]) if vb_ObservShift.curselection() else 0
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        BookFlag = int(str(vb_Book.get(vb_Book.curselection())).split(":")[0]) if vb_Book.curselection() else 0
        L1FirstFixing = float(v_L1FirstFixing.get())/100 if str(v_L1FirstFixing.get()) else 0.0              
        VolArray, TermVol = [], []            
        if CMSUseFlag == True : 
            OptionData = pd.DataFrame([])
            for i in range(len(Name2)) :
                if "SwapMat/OptMat" in MyMarketDataList2[i].columns or "스왑만기/옵션만기" in MyMarketDataList2[i].columns :
                    OptData = MyMarketDataList2[i].set_index(MyMarketDataList2[i].columns[0])
                    MyInd = OptData.index.astype(np.float64)/12
                    MyCol = OptData.columns.astype(np.float64)/12
                    OptionData = pd.DataFrame(OptData.values, columns = MyCol, index = MyInd)
                    break        
            if i == len(Name) : 
                VolSearch = 0
            else : 
                VolSearch = 1                    
            t = DayCountAtoB(int(PriceDate), SwapMaturity)/365

            if VolSearch == 1 : 
                x = np.array(OptionData.index)
                TermVol = list(OptionData.columns)
                for i in range(len(OptionData.columns)) : 
                    y = OptionData.values[:,i]
                    v = Linterp(x, y, t)
                    VolArray.append(v)               
            else : 
                TermVol = [1]
                VolArray = [0.01]
        ErrorFlag, ErrorString = Calc_Schedule_ErrorCheck(Nominal, SwapEffectiveDate, int(PriceDate), SwapMaturity, CurveTerm1, 
                              CurveRate1, NumCpnOneYear_P1, DayCount)
        if ErrorFlag == 0 : 
            Value, PV01, TempPV01 = Calc_IRS_PV01(Nominal, L1FirstFixing, SwapEffectiveDate, 
                    int(PriceDate), SwapMaturity, FixedCpnRate_P1, CurveTerm1, CurveRate1, 
                    NumCpnOneYear_P1, DayCount, KoreanHoliday = False, MaturityToPayDate = SwapMaturityToPayDate, EstZeroCurveTerm = CurveTerm2,
                    EstZeroCurveRate = CurveRate2, FixingHolidayList = HolidaysForSwap, AdditionalPayHolidayList  = HolidaysForSwap, NominalDateIsNominalPayDate = False,
                    LoggingFlag = LoggingFlag, LoggingDir = currdir, ModifiedFollow = 1, FixedPayerFlag = FixedPayer, 
                    DiscCurveNameLeg1 = UsedCurveName1, EstCurveNameLeg1 = UsedCurveName2, DiscCurveNameLeg2 = UsedCurveName1, EstCurveNameLeg2 = UsedCurveName2, LookBackDays = LookBackDays,
                    ObservShift = ObservShift, CMSFlag = CMSUseFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNOneYear_P1, TermVol = TermVol, Vol = VolArray)         
            GIRRRisk1 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01, "PV01Term","PV01"), 4 if Value > 10000 else 2)
            GIRRRisk2 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(TempPV01, "PV01TermEst","PVEst01"), 4 if Value > 10000 else 2)
            GIRRRisk = np.round(GIRRRisk1 + GIRRRisk2, 4)
            if PrevTreeFlag == 0 : 
                tree = ttk.Treeview(root)
            else : 
                tree.destroy()
                scrollbar.destroy()
                scrollbar2.destroy()
                tree = ttk.Treeview(root)
            PV01 = pd.concat([PV01, TempPV01],axis = 1).applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
            tree.pack(padx=5, pady=5, fill="both", expand=True)
            scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
            scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.configure(xscrollcommand=scrollbar2.set)
            scrollbar.pack(side="right", fill="y")    
            scrollbar2.pack(side="bottom", fill="x")    
            
            PrevTreeFlag = insert_dataframe_to_treeview(tree, PV01.reset_index(), width = 100)        
            
            if BookFlag in ["y","Y","1",1] : 
                GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
                Data_GIRR = MapGIRRDeltaGreeks(PV01.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR2 = MapGIRRDeltaGreeks(TempPV01.set_index("PV01TermEst")["PVEst01"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                Data_GIRR2.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                GIRR = pd.DataFrame([list(Data_GIRR["GIRR_Delta_Sensi"])], columns = list(Data_GIRR["GIRR_Tenor"].apply(lambda x : "GIRR1_" + str(x))))
                GIRR2 = pd.DataFrame([list(Data_GIRR2["GIRR_Delta_Sensi"])], columns = list(Data_GIRR2["GIRR_Tenor"].apply(lambda x : "GIRR2_" + str(x))))
                GIRR = pd.concat([GIRR, GIRR2],axis = 1)
                df_pre = ReadCSV(currdir + "\\Book\\IRS\\IRS.csv")
                MyCol = ["Nominal","FixingRate","EffectiveDate","EndDate",
                        "NBDFromEndDateToPayDate","CpnRate","NumCpnOneYear","DayCountFlag","ModifiedFollowing",
                        "DiscCurveNameLeg1","EstCurveNameLeg1","DiscCurveNameLeg2","EstCurveNameLeg2",
                        "Currency","Holiday","MTM","PriceDate","GirrBucket", "FixedPayer"]
                
                Contents = [Nominal, L1FirstFixing, SwapEffectiveDate, SwapMaturity, 
                            SwapMaturityToPayDate, FixedCpnRate_P1, NumCpnOneYear_P1, DayCount, 1, 
                            UsedCurveName1.split("\\")[-1], UsedCurveName2.split("\\")[-1], UsedCurveName1.split("\\")[-1], UsedCurveName2.split("\\")[-1],
                            UsedCurveName1.split("\\")[-2], UsedCurveName1.split("\\")[-2], Value , YYYYMMDD, Curr.upper(), FixedPayer]
                data2 = pd.DataFrame([Contents], columns = MyCol)
                data2 = pd.concat([data2, GIRR],axis = 1)
                df = pd.concat([df_pre, data2],axis = 0)
                df.index = np.arange(len(df))
                df.to_csv(currdir + "\\Book\\IRS\\IRS.csv", index = False, encoding = "cp949")
                messagebox.showinfo("알림","Booking 완료!!")        

            output_label.config(text = f"\n결과: {np.round(Value,4)}\nPayoff: \n{ResultPayoff}\n\nGIRR: {GIRRRisk}\n\nBooking = {bool(BookFlag)}\n\nVolSearch ={bool(VolSearch)}", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"\n결과: \n{ErrorString}", font = ("맑은 고딕", 12, 'bold'))
            
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()
                
    MainFlag2 = 0
    return MainFlag2, Value, PV01, TempPV01

def PricingFXSwapProgram(HolidayDate = pd.DataFrame([]), SpotData = pd.DataFrame([]), currdir = os.getcwd()) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',namenotin = "vol", Comments = "FX Swap을 평가하기 위해서는 최소 두가지 커브를 선택해야 합니다.\n", defaultvalue=[0, 1], DefaultStringList = ["CRS","USD"]) 
    if len(Name) == 1 : 
        print("\n FX Swap을 평가하기 위해서는 최소 두가지 커브가 필요하므로 종료합니다.\n")
    CurveNameShort = np.vectorize(lambda x : x.split("\\")[-1].replace(".csv",""))(Name)
    CurveNameShortList = [str(n) + ": " + i for n, i in enumerate(CurveNameShort)]       
    Curr = np.vectorize(lambda x : x.split("\\")[-2].replace(".csv","") + "/" + "KRW")(Name)
    Spotidx = list(SpotData.index).index(YYYYMMDD) if YYYYMMDD in SpotData.index else -1
    fx1temp = SpotData[Curr[0]].iloc[Spotidx] if Curr[0] in SpotData.columns else 1
    fx2temp = SpotData[Curr[-1]].iloc[Spotidx] if Curr[-1] in SpotData.columns else 1
    root = tk.Tk()
    root.title("FX Swap Pricer")
    root.geometry("1000x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_BuySellFlag = make_listvariable_interface(left_frame, 'Swap구분', ["0: 외화Buy/Sell","1: 외화Sell/Buy"], pady = 3, listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0)
    vb_LDHoliday = make_listvariable_interface(left_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)
    v_Nominal = make_variable_interface(left_frame, 'Nominal(외화기준)', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue = int(YYYYMMDD))
    v_SpotDate = make_variable_interface(left_frame, 'SpotDate', bold = True, textfont = 11, defaultflag = True, defaultvalue = NextNthBusinessDate(int(YYYYMMDD), 2,[]))
    v_SpotPrice = make_variable_interface(left_frame, 'Spot 환율', bold = True, textfont = 11, defaultflag = True, defaultvalue = fx1temp if fx1temp != 1 else fx2temp)
    v_NearDate = make_variable_interface(left_frame, 'NearDate', bold = True, textfont = 11, defaultflag = True, defaultvalue = NextNthBusinessDate(int(YYYYMMDD), 2,[]))
    v_NearPrice = make_variable_interface(left_frame, 'Near 환율', bold = True, textfont = 11, defaultflag = True, defaultvalue = fx1temp if fx1temp != 1 else fx2temp)
    v_FarDate = make_variable_interface(left_frame, 'FarDate', bold = True, textfont = 11, defaultflag = True, defaultvalue = EDate_YYYYMMDD(NextNthBusinessDate(int(YYYYMMDD), 2,[]), 12))
    v_FarPrice = make_variable_interface(left_frame, 'Far 환율', bold = True, textfont = 11, defaultflag = True, defaultvalue = fx1temp if fx1temp != 1 else fx2temp)
    
    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')    
    vb_SelectedCurve_D = make_listvariable_interface(right_frame, 'DomesticCurve 선택', CurveNameShortList, listheight = 5, textfont = 11, titlelable = True, titleName = "Domestic INFO", defaultflag = True, defaultvalue = 0, pady = 10, width = 50)
    vb_SelectedCurve_F = make_listvariable_interface(right_frame, 'ForeignCurve 선택', CurveNameShortList, listheight = 5, textfont = 11, titlelable = True, titleName = "Foreign INFO", defaultflag = True, defaultvalue = 1, width = 50)
    
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')    
    Variables = []
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, Variables]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        long0short1 = int(str(vb_BuySellFlag.get(vb_BuySellFlag.curselection())).split(":")[0]) if vb_BuySellFlag.curselection() else 0
        HolidayCurr = vb_LDHoliday.get(vb_LDHoliday.curselection()) if vb_LDHoliday.curselection() else "KRW"
        Holidays = HolidayDate[HolidayCurr].dropna() if HolidayCurr in HolidayDate.columns else []
        Nominal = float(v_Nominal.get()) if len(str(v_Nominal.get())) > 0 else 10000
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        CalculatedSpotDate = NextNthBusinessDate(PriceDate, 2, Holidays)
        SpotDate = int(v_SpotDate.get()) if len(str(v_SpotDate.get())) > 0 else CalculatedSpotDate
        SpotPrice = float(v_SpotPrice.get()) if len(str(v_SpotPrice.get())) > 0 else (fx1temp if fx1temp != 1 else fx2temp)
        NearDate = int(v_NearDate.get()) if len(str(v_NearDate.get())) > 0 else CalculatedSpotDate
        NearPrice = float(v_NearPrice.get()) if len(str(v_NearPrice.get())) > 0 else (fx1temp if fx1temp != 1 else fx2temp)
        FarDate = int(v_FarDate.get()) if len(str(v_FarDate.get())) > 0 else EDate_YYYYMMDD(CalculatedSpotDate, 12)
        FarPrice = float(v_FarPrice.get()) if len(str(v_FarPrice.get())) > 0 else (fx1temp if fx1temp != 1 else fx2temp)
        NSelectedCurve_D = int(str(vb_SelectedCurve_D.get(vb_SelectedCurve_D.curselection())).split(":")[0]) if vb_SelectedCurve_D.curselection() else 0
        NSelectedCurve_F = int(str(vb_SelectedCurve_F.get(vb_SelectedCurve_F.curselection())).split(":")[0]) if vb_SelectedCurve_F.curselection() else 0
        DomesticTerm = MyMarketDataList[NSelectedCurve_D]["Term"].astype(np.float64)
        DomesticRate = MyMarketDataList[NSelectedCurve_D]["Rate"].astype(np.float64)
        ForeignTerm = MyMarketDataList[NSelectedCurve_F]["Term"].astype(np.float64)
        ForeignRate = MyMarketDataList[NSelectedCurve_F]["Rate"].astype(np.float64)
        Preprocessing_ZeroTermAndRate(DomesticTerm, DomesticRate, PriceDate)            
        Preprocessing_ZeroTermAndRate(ForeignTerm, ForeignRate, PriceDate)           
        SpotT = DayCountAtoB(PriceDate, SpotDate)/365 if SpotDate > 0 else DayCountAtoB(PriceDate, CalculatedSpotDate)/365
        T1, T2 = DayCountAtoB(PriceDate, NearDate)/365, DayCountAtoB(PriceDate, FarDate)/365 
        F1, F2 = NearPrice, FarPrice
        v, vD, vF = Calc_Value_FXSwap(SpotPrice, T1, T2, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, long0short1, SpotT, Nominal, F1, F2)
        VariableList = [SpotPrice, T1, T2, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, long0short1, SpotT, Nominal, F1, F2]
        v1 = format(np.round(v, 4), ",f")
        v2 = format(np.round(vD, 4), ",f")
        v3 = format(np.round(vF, 4), ",f")
        output_label.config(text = f"NPV: \n{v1}\nDomestic NPV: \n{v2}\nForeign NPV: \n{v3}", font = ("맑은 고딕", 12, 'bold'))
            
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
        MyArrays[4] = VariableList        

    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop() 
    return 0, 0, 0, 0
        
def PricingCRSProgram(HolidayData = pd.DataFrame([]), SpotData = pd.DataFrame([])) : 
    YYYYMMDD, Name, MyMarketDataList = UsedMarketDataSetToPricing(currdir + '\\MarketData\\outputdata',namenotin = "vol", Comments = "Currency Swap을 평가하기 위해서는 최소 두가지 커브를 선택해야 합니다.\n", defaultvalue=[0, 1], DefaultStringList=["CRS","USD,IRS"]) 

    if len(Name) == 1 : 
        print("\n Currency Swap을 평가하기 위해서는 최소 두가지 커브가 필요하므로 종료합니다.\n")
        return "", 0, pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([])
    CurveNameShort = np.vectorize(lambda x : x.split("\\")[-1].replace(".csv",""))(Name)
    CurveNameShortList = [str(n) + ": " + i for n, i in enumerate(CurveNameShort)]       
    Curr = np.vectorize(lambda x : x.split("\\")[-2].replace(".csv","") + "/" + "KRW")(Name)
    YYYY = int(YYYYMMDD) // 10000
    Spotidx = list(SpotData.index).index(YYYYMMDD) if YYYYMMDD in SpotData.index else -1
    fx1temp = SpotData[Curr[0]].iloc[Spotidx] if Curr[0] in SpotData.columns else 1
    fx2temp = SpotData[Curr[-1]].iloc[Spotidx] if Curr[-1] in SpotData.columns else 1
    root = tk.Tk()
    root.title("CRS Pricer(Single Phase)")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Nominal1 = make_variable_interface(left_frame, 'Leg1 Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000)
    v_Nominal2 = make_variable_interface(left_frame, 'Leg2 Nominal Amount', bold = True, textfont = 11, defaultflag = True, defaultvalue=10000/1400)
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int(YYYYMMDD))

    v_SwapEffectiveDate = make_variable_interface(left_frame, 'EffectiveDate(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY-1) * 10000 + 929)
    v_SwapMaturity = make_variable_interface(left_frame, 'Maturity(YYYYMMDD)', bold = False, textfont = 11, defaultflag = True, defaultvalue=(YYYY+19) * 10000 + 929)
    v_SwapMaturityToPayDate = make_variable_interface(left_frame, '기말일TO지급일까지\n영업일수', bold = False, textfont = 11, defaultflag = True, defaultvalue = 2)
    vb_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["0","1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=3)
    vb_FixedPayer = make_listvariable_interface(left_frame, 'Fixed PayerFlag', ["0: Leg1 수취 \nLeg2 지급","1: Leg1 지급 \nLeg2 수취"], listheight = 2, textfont = 11, defaultflag = True, defaultvalue=0, width = 20)
    vb_Logging = make_listvariable_interface(left_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, pady = 10)
    vb_Book = make_listvariable_interface(left_frame, 'Book', ["0: Book 안함","1: Booking"], listheight = 2, textfont = 11, pady = 10)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_DomeDiscNum = make_listvariable_interface(right_frame, 'Discount Curve \n(리스트에서 선택)', CurveNameShortList, listheight = 3, textfont = 11, titlelable = True, titleName = "(Leg1)MarketDataSet", defaultflag = True, defaultvalue=0, width = 30)
    vb_DomeEstNum = make_listvariable_interface(right_frame, 'Estimation Curve', ["-1: EstimationCurve 미사용"] + CurveNameShortList, listheight = 3, textfont = 11, defaultflag = True, defaultvalue=0, width = 30)
    v_FixedCpnRate_P1 = make_variable_interface(right_frame, 'Leg1 고정쿠폰(%)', bold = False, textfont = 11, defaultflag = True, defaultvalue =2.19)
    vb_LD_DayCount = make_listvariable_interface(right_frame, 'Leg1 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag=True, defaultvalue=0)
    v_LDFirstFixing = make_variable_interface(right_frame, '최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_LDPricingFXRate = make_variable_interface(right_frame, 'Leg1 Pricing 환율', bold = False, textfont = 11, defaultflag = True, defaultvalue = fx1temp)
    vb_LDHoliday = make_listvariable_interface(right_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 0)
    v_LD_LookBackDays = make_variable_interface(right_frame, 'LookBackDays', bold = False, textfont = 11, titleName = "SOFR설정(필요시입력)", titlelable= True, defaultflag = True, defaultvalue = 0)

    rightright_frame = tk.Frame(root)
    rightright_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_ForeDiscNum = make_listvariable_interface(rightright_frame, 'Discount Curve \n(리스트에서 선택)', CurveNameShortList, listheight = 3, textfont = 11, titlelable = True, titleName = "(Leg2)MarketDataSet", defaultflag = True, defaultvalue=1, width = 30)
    vb_ForeEstNum = make_listvariable_interface(rightright_frame, 'Estimation Curve', CurveNameShortList, listheight = 3, textfont = 11, defaultflag = True, defaultvalue=1, width = 30)
    vb_LF_DayCount = make_listvariable_interface(rightright_frame, 'Leg2 DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag=True, defaultvalue=1)
    v_LFFirstFixing = make_variable_interface(rightright_frame, '최근Fixing금리(%)\n(Fixing이후 평가시 입력)', bold = False, textfont = 11)
    v_LFPricingFXRate = make_variable_interface(rightright_frame, 'Leg2 Pricing 환율', bold = False, textfont = 11, defaultflag = True, defaultvalue = fx2temp)
    vb_LFHoliday = make_listvariable_interface(rightright_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 1)
    v_LF_LookBackDays = make_variable_interface(rightright_frame, 'LookBackDays', bold = False, textfont = 11, titleName = "SOFR설정(필요시입력)", titlelable= True, defaultflag = True, defaultvalue = 0)

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    
    for i in range(len(Name)) : 
        vb_zerocurve = make_listvariable_interface(center_frame, CurveNameShortList[i], termratestr(MyMarketDataList[i]["Term"], MyMarketDataList[i]["Rate"]), titleName = "MARKET DATA INFO", titlelable= (i == 0), listheight = 11, textfont = 11)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    Value = 0
    PV01, PV01DomesticDisc, PV01ForeignDisc, PV01DomesticEst, PV01ForeignEst = None, None, None, None, None 
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        Nominal1 = float(v_Nominal1.get()) if len(str(v_Nominal1.get())) > 0 else 10000
        Nominal2 = float(v_Nominal2.get()) if len(str(v_Nominal2.get())) > 0 else 10000
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)
        SwapEffectiveDate = int(v_SwapEffectiveDate.get()) if len(str(v_SwapEffectiveDate.get())) > 0 else 20200627
        SwapMaturity = int(v_SwapMaturity.get()) if len(str(v_SwapMaturity.get())) > 0 else (SwapEffectiveDate + 100000)
        SwapMaturityToPayDate = int(v_SwapMaturityToPayDate.get()) if len(str(v_SwapMaturityToPayDate.get())) > 0 else 0

        FixedPayer = int(str(vb_FixedPayer.get(vb_FixedPayer.curselection())).split(":")[0]) if vb_FixedPayer.curselection() else 1
        NumCpnOneYear_P1 = int(vb_NumCpnOneYear_P1.get(vb_NumCpnOneYear_P1.curselection())) if vb_NumCpnOneYear_P1.curselection() else 4
        if len(str(v_FixedCpnRate_P1.get())) > 0 : 
            if "%" in str(v_FixedCpnRate_P1.get()) : 
                FixedCpnRate_P1 = float(v_FixedCpnRate_P1.get())/100
            else : 
                FixedCpnRate_P1 = float(str(v_FixedCpnRate_P1.get()).replace("%",""))/100
        else : 
            FixedCpnRate_P1 = 0

        DomeDiscNum = int(str(vb_DomeDiscNum.get(vb_DomeDiscNum.curselection())).split(":")[0]) if vb_DomeDiscNum.curselection() else 0
        DomeEstNum = int(str(vb_DomeEstNum.get(vb_DomeEstNum.curselection())).split(":")[0]) if vb_DomeEstNum.curselection() else -1
        
        DomeDiscTerm = MyMarketDataList[DomeDiscNum]["Term"]
        DomeDiscRate = MyMarketDataList[DomeDiscNum]["Rate"]
        if DomeEstNum == -1 : 
            DomeEstTerm = []
            DomeEstRate = []
            DomeEstName = Name[DomeDiscNum]
        else : 
            DomeEstTerm = MyMarketDataList[DomeEstNum]["Term"]
            DomeEstRate = MyMarketDataList[DomeEstNum]["Rate"]
            DomeEstName = Name[DomeEstNum]
        DomeDiscName = Name[DomeDiscNum]
        
        LD_DayCount = int(str(vb_LD_DayCount.get(vb_LD_DayCount.curselection())).split(":")[0]) if vb_LD_DayCount.curselection() else 0
        LDFirstFixing = float(v_LDFirstFixing.get())/100 if len(str(v_LDFirstFixing.get())) > 0 else 0.0              
        LDPricingFXRate = float(v_LDPricingFXRate.get()) if len(str(v_LDPricingFXRate.get())) > 0 else 0.0              
        LD_LookBackDays = int(v_LD_LookBackDays.get()) if len(str(v_LD_LookBackDays.get())) > 0 else 0
        LD_Holiday_Curr = vb_LDHoliday.get(vb_LDHoliday.curselection()) if vb_LDHoliday.curselection() else "KRW"
        if LD_Holiday_Curr.upper() in HolidayData.columns : 
            LD_HolidaysForSwap = list(HolidayData[LD_Holiday_Curr.upper()].dropna().unique())  
        elif LD_Holiday_Curr.upper() == 'KRW' : 
            LD_HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif LD_Holiday_Curr.upper() == 'USD' :
            LD_HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else :
            LD_HolidaysForSwap = []

        ForeDiscNum = int(str(vb_ForeDiscNum.get(vb_ForeDiscNum.curselection())).split(":")[0]) if vb_ForeDiscNum.curselection() else 0
        ForeEstNum = int(str(vb_ForeEstNum.get(vb_ForeEstNum.curselection())).split(":")[0]) if vb_ForeEstNum.curselection() else 0
        ForeDiscTerm = MyMarketDataList[ForeDiscNum]["Term"]
        ForeDiscRate = MyMarketDataList[ForeDiscNum]["Rate"]
        ForeEstTerm = MyMarketDataList[ForeEstNum]["Term"]
        ForeEstRate = MyMarketDataList[ForeEstNum]["Rate"]
        ForeDiscName = Name[ForeDiscNum]
        ForeEstName = Name[ForeEstNum]
        if FixedPayer == 0 : 
            ResultPayoff = ("R(Leg1, T) x 1 + " if DomeEstNum >= 0 else "") + str(np.round(FixedCpnRate_P1*100,4)) + "%" + " - R(Leg2, T)"
        else :
            ResultPayoff = "R(Leg2, T) x 1" + " - " + ("R(Leg1, T) x 1 - " if DomeEstNum >= 0 else "") + str(np.round(FixedCpnRate_P1*100,4)) + "%"
             
        LF_DayCount = int(str(vb_LF_DayCount.get(vb_LF_DayCount.curselection())).split(":")[0]) if vb_LF_DayCount.curselection() else 0
        LFFirstFixing = float(v_LFFirstFixing.get())/100 if len(str(v_LFFirstFixing.get())) > 0 else 0.0              
        LFPricingFXRate = float(v_LFPricingFXRate.get()) if len(str(v_LFPricingFXRate.get())) > 0 else 0.0              
        LF_LookBackDays = int(v_LF_LookBackDays.get()) if len(str(v_LF_LookBackDays.get())) > 0 else 0
        LF_Holiday_Curr = vb_LFHoliday.get(vb_LFHoliday.curselection()) if vb_LFHoliday.curselection() else "KRW"
        if LF_Holiday_Curr.upper() in HolidayData.columns : 
            LF_HolidaysForSwap = list(HolidayData[LF_Holiday_Curr.upper()].dropna().unique())  
        elif LF_Holiday_Curr.upper() == 'KRW' : 
            LF_HolidaysForSwap = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif LF_Holiday_Curr.upper() == 'USD' :
            LF_HolidaysForSwap = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else :
            LF_HolidaysForSwap = []
        HolidaysForSwap = sorted(list(set(list(LD_HolidaysForSwap) + list(LF_HolidaysForSwap))))
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        BookFlag = int(str(vb_Book.get(vb_Book.curselection())).split(":")[0]) if vb_Book.curselection() else 0
        ErrorFlag, ErrorString = Calc_Schedule_ErrorCheck(Nominal1*Nominal2, SwapEffectiveDate, int(PriceDate), SwapMaturity, DomeDiscTerm, 
                        DomeDiscRate, NumCpnOneYear_P1, LD_DayCount)
        if ErrorFlag == 0 : 
            CRSFlagDomestic = ('FX' in DomeDiscName.upper()) or ('BASIS' in DomeDiscName.upper()) or ('CRS' in DomeDiscName.upper())
            CRSFlagForeign = ('FX' in ForeDiscName.upper()) or ('BASIS' in ForeDiscName.upper()) or ('CRS' in ForeDiscName.upper())
            Value, PV01DomesticDisc, PV01ForeignDisc, PV01DomesticEst, PV01ForeignEst = CalC_CRS_PV01(
                    Nominal1, Nominal2, LDFirstFixing, SwapEffectiveDate, int(PriceDate), SwapMaturity, 
                    FixedCpnRate_P1, DomeDiscTerm, DomeDiscRate, NumCpnOneYear_P1, LD_DayCount, 
                    LF_DayCount, KoreanHoliday = False, MaturityToPayDate = SwapMaturityToPayDate, EstZeroCurveTermDomestic = DomeEstTerm, EstZeroCurveRateDomestic = DomeEstRate, 
                    EstZeroCurveTermForeign = ForeEstTerm, EstZeroCurveRateForeign = ForeEstRate, ZeroCurveTermForeign = ForeDiscTerm, ZeroCurveRateForeign = ForeDiscRate, FixingHolidayListDomestic = LD_HolidaysForSwap, 
                    FixingHolidayListForeign = LF_HolidaysForSwap, AdditionalPayHolidayList = HolidaysForSwap, NominalDateIsNominalPayDate = True, LoggingFlag = LoggingFlag, LoggingDir = currdir, 
                    ModifiedFollow = 1,LookBackDaysDomestic = LD_LookBackDays, LookBackDaysForeign = LF_LookBackDays, ObservShift = False, DomesticPayerFlag = FixedPayer, 
                    DiscCurveName = DomeDiscName, EstCurveName = DomeEstName, ValuationDomesticFX = LDPricingFXRate, ValuationForeignFX = LFPricingFXRate, SOFRFlag = False, 
                    FixFixFlag = False, FirstFloatFixRateForeign= LFFirstFixing, DiscCurveNameForeign = ForeDiscName, EstCurveNameForeign = ForeEstName, DomesticParallelUp = CRSFlagDomestic, ForeignParallelUp= CRSFlagForeign)    

            GIRRRisk1 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01DomesticDisc.fillna(0), "PV01TermDomesticDisc","PV01DomesticDisc"), 4 if Value > 10000 else 2)
            GIRRRisk2 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01DomesticEst.fillna(0), "PV01TermDomesticEst","PV01DomesticEst"), 4 if Value > 10000 else 2)
            GIRRRisk3 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01ForeignDisc.fillna(0), "PV01TermForeignDisc","PV01ForeignDisc"), 4 if Value > 10000 else 2)
            GIRRRisk4 = np.round(Calc_GIRRDeltaNotCorrelated_FromGreeks(PV01ForeignEst.fillna(0), "PV01TermForeignEst","PV01ForeignEst"), 4 if Value > 10000 else 2)
            GIRRRisk = np.round(np.abs(GIRRRisk1 + GIRRRisk2 - GIRRRisk3 - GIRRRisk4), 4)

            if PrevTreeFlag == 0 : 
                tree = ttk.Treeview(root)
            else : 
                tree.destroy()
                scrollbar.destroy()
                scrollbar2.destroy()
                tree = ttk.Treeview(root)
            PV01 = pd.concat([PV01DomesticDisc, PV01ForeignDisc, PV01DomesticEst, PV01ForeignEst],axis = 1).fillna(0)
            PV01 = PV01.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
            tree.pack(padx=5, pady=5, fill="both", expand=True)
            scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
            scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.configure(xscrollcommand=scrollbar2.set)
            scrollbar.pack(side="right", fill="y")    
            scrollbar2.pack(side="bottom", fill="x")    
            
            PrevTreeFlag = insert_dataframe_to_treeview(tree, PV01.reset_index(), width = 100)    
            if BookFlag in ["y","Y","1",1] : 
                GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
                Data_GIRR1 = MapGIRRDeltaGreeks(PV01DomesticDisc.fillna(0).set_index("PV01TermDomesticDisc")["PV01DomesticDisc"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR2 = MapGIRRDeltaGreeks(PV01DomesticEst.fillna(0).set_index("PV01TermDomesticEst")["PV01DomesticEst"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR3 = MapGIRRDeltaGreeks(PV01ForeignDisc.fillna(0).set_index("PV01TermForeignDisc")["PV01ForeignDisc"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR4 = MapGIRRDeltaGreeks(PV01ForeignEst.fillna(0).set_index("PV01TermForeignEst")["PV01ForeignEst"], GIRR_DeltaRiskFactor).reset_index()
                Data_GIRR1.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                Data_GIRR2.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                Data_GIRR3.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                Data_GIRR4.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"]
                GIRR1 = pd.DataFrame([list(Data_GIRR1["GIRR_Delta_Sensi"])], columns = list(Data_GIRR1["GIRR_Tenor"].apply(lambda x : "GIRR1_" + str(x))))
                GIRR2 = pd.DataFrame([list(Data_GIRR2["GIRR_Delta_Sensi"])], columns = list(Data_GIRR2["GIRR_Tenor"].apply(lambda x : "GIRR2_" + str(x))))            
                GIRR3 = pd.DataFrame([list(Data_GIRR3["GIRR_Delta_Sensi"])], columns = list(Data_GIRR3["GIRR_Tenor"].apply(lambda x : "GIRR3_" + str(x))))            
                GIRR4 = pd.DataFrame([list(Data_GIRR4["GIRR_Delta_Sensi"])], columns = list(Data_GIRR4["GIRR_Tenor"].apply(lambda x : "GIRR4_" + str(x))))            
                GIRR = pd.concat([GIRR1, GIRR2, GIRR3, GIRR4],axis = 1)
                df_pre = ReadCSV(currdir + "\\Book\\IRS\\CRS.csv")
                MyCol = ["Nominal1","Nominal2","LDFixingRate","LFFixingRate","EffectiveDate",
                         "SwapMaturity","LDFixedCpnRate","LFFixedCpnRate","LDNumCpnOneYear_P1","LFNumCpnOneYear_P1",
                         "LD_DayCount","LF_DayCount","KoreanHoliday","NBDFromEndDateToPayDate","NominalDateIsNominalPayDate",
                         "ModifiedFollow","LD_LookBackDays","LF_LookBackDays","LDPayer","LDPricingFXRate",
                         "LFPricingFXRate","DiscCurveNameLeg1","EstCurveNameLeg1","DiscCurveNameLeg2","EstCurveNameLeg2",
                         "Currency1","Currency2","Holiday","MTM","PriceDate","GirrBucket1","GirrBucket2","ProductType"]
                cname1 = DomeDiscName.split("\\")[-1].replace(".csv","")
                cname2 = DomeEstName.split("\\")[-1].replace(".csv","")
                cname3 = ForeDiscName.split("\\")[-1].replace(".csv","")
                cname4 = ForeEstName.split("\\")[-1].replace(".csv","")
                Contents = [Nominal1, Nominal2, LDFirstFixing, LFFirstFixing, SwapEffectiveDate, 
                            SwapMaturity, FixedCpnRate_P1, 0, NumCpnOneYear_P1, NumCpnOneYear_P1, 
                            LD_DayCount, LF_DayCount, 0, SwapMaturityToPayDate, 1, 
                            1, LD_LookBackDays, LF_LookBackDays, FixedPayer, LDPricingFXRate,
                            LFPricingFXRate, cname1, cname2, cname3, cname4,
                            LD_Holiday_Curr, LF_Holiday_Curr, LD_Holiday_Curr+LF_Holiday_Curr,Value,int(PriceDate), LD_Holiday_Curr, LF_Holiday_Curr,"CRS"]  
                data2 = pd.DataFrame([Contents], columns = MyCol)
                data2 = pd.concat([data2, GIRR],axis = 1)
                df = pd.concat([df_pre, data2],axis = 0)
                df.index = np.arange(len(df))
                df.to_csv(currdir + "\\Book\\IRS\\CRS.csv", index = False, encoding = "cp949")
                messagebox.showinfo("알림","Booking 완료!!")                                  
                
            output_label.config(text = f"Payoff: \n{ResultPayoff}\n\n결과: {np.round(Value,4)}\n\nGIRR: {GIRRRisk}\n\nBooking = {bool(BookFlag)}", font = ("맑은 고딕", 12, 'bold'))
        else : 
            output_label.config(text = f"Payoff: \n{ErrorString}", font = ("맑은 고딕", 12, 'bold'))
            
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop() 
    
    MainFlag2 = 0#input("종료하시겠습니까? (Y/N)\n->")
    return MainFlag2, Value, PV01DomesticDisc, PV01ForeignDisc, PV01DomesticEst, PV01ForeignEst

def ZeroCurveMaker(MyData, currdir, YYYYMMDD, HolidayDate, FXSpot, CurveName = "") : 
    MyData["Type"] = MyData["Type"].apply(lambda x : str(x).lower())
    ForeignCurveNeeded = 1 if 'sp' in list(MyData["Type"]) else 0
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namenotin = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))
    Currency = CurveName.split("\\")[-2]

    DefaultSpot = 1.0
    if ('krw' in Currency.lower()) and (int(YYYYMMDD) in FXSpot.index) : 
        DefaultSpot = FXSpot.loc[int(YYYYMMDD)]["USD/KRW"]
    elif Currency + "/KRW" in FXSpot.columns : 
        DefaultSpot = FXSpot.iloc[-1][Currency + "/KRW"]
        
    DomesticCurveData = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Currency"] == Currency]
    ForeignCurveData = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Currency"] != Currency]
    
    c1 = DomesticCurveData["DirectoryPrint"].iloc[0].split("\\")[-2] if len(DomesticCurveData) > 0 else Currency 
    c2 = ForeignCurveData["DirectoryPrint"].iloc[0].split("\\")[-2] if len(ForeignCurveData) > 0 else '' 
    
    root = tk.Tk()
    root.title("ZeroMaker")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_DomesticEst_P1 = make_listvariable_interface(left_frame, 'Domestic Estimation Curve \n(-1: Fix - Flo Swap의 경우)', ["-1. Domestic Estimation 필요없음"] + list(DomesticCurveData["ListName"]), listheight = 4, textfont = 11, titlelable = True, titleName = "Domestic Leg INFO", defaultflag = True, defaultvalue = 0, pady = 10, width = 30)
    vb_LDHoliday = make_listvariable_interface(left_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = (1 if c1 == 'USD' else 0))
    vb_LD_DayCount = make_listvariable_interface(left_frame, 'Domestic DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"], listheight = 3, textfont = 11, defaultflag=True, defaultvalue=1 if c1 == "USD" else 0)

    right_frame = tk.Frame(root)
    right_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_Foreign_P1 = make_listvariable_interface(right_frame, 'Foreign Estimation Curve \n', list(ForeignCurveData["ListName"]) if ForeignCurveNeeded else ["-1. 미사용"], listheight = 4, textfont = 11, titlelable = True, titleName = "Foreign Leg INFO", defaultflag = True, defaultvalue = 1 if len(ForeignCurveData) >= 2 else 0, pady = 10)
    vb_LFHoliday = make_listvariable_interface(right_frame, 'HolidayFlag', ["KRW","USD","GBP","JPY"] if ForeignCurveNeeded else ["-1: 미사용"], listheight = 3, textfont = 11, pady = 2, defaultflag = True, defaultvalue = (1 if c2 == 'USD' else 0))
    vb_LF_DayCount = make_listvariable_interface(right_frame, 'Foreign DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360","5: Cmp ACT/365","6: Cmp ACT/360","7: Cmp ACT/ACT","8: Cmp 30/360"] if ForeignCurveNeeded else ["-1: 미사용"], listheight = 3, textfont = 11, defaultflag=True, defaultvalue=1 if c2 == "USD" else 0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(Result_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=int(YYYYMMDD))
    v_Spot = make_variable_interface(Result_frame, 'Spot 환율\n(외화1단위당 국내통화)' if ForeignCurveNeeded else "미사용변수", bold = True, textfont = 11, defaultflag = True, defaultvalue=DefaultSpot)
    v_SwapPointUnit = make_variable_interface(Result_frame, 'SwapPointUnit' if ForeignCurveNeeded else "미사용변수", bold = True, textfont = 11, defaultflag = True, defaultvalue=100)
    vb_NumCpnOneYear_P1 = make_listvariable_interface(Result_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0 if c1 == "USD" else 2)
    vb_Logging = make_listvariable_interface(Result_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, pady = 10)
    v_SaveName = make_variable_interface(Result_frame, '저장할 커브명\n(ex: KRW IRS ZeroCurve)', bold = True, textfont = 11, defaultflag = True, defaultvalue="")

    newtree = ttk.Treeview(root, height = 30)
    newtree.pack(side = 'left', padx=5, pady=10, expand=False, anchor = 'n')        
    NewTreeFlag = insert_dataframe_to_treeview(newtree, MyData, width = 75)       
    PrevTreeFlag, tree, scrollbar, scrollbar2, ResultDF = 0, None, None, None, pd.DataFrame([])
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultDF]    
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        ResultDF = MyArrays[4]
        
        N_DomesticEst_P1 = int(str(vb_DomesticEst_P1.get(vb_DomesticEst_P1.curselection())).split(".")[0]) if vb_DomesticEst_P1.curselection() else -1
        if N_DomesticEst_P1 >= 0 :
            DomesticEstCurveDirectory = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == N_DomesticEst_P1]["Directory"].iloc[0]
            DomesticEstCurve = ReadCSV(DomesticEstCurveDirectory, True).applymap(lambda x : str(x).replace("-","") if "-" in str(x) else x)
            DomesticEstTerm = DomesticEstCurve["Term"].astype(np.float64)
            DomesticEstRate = DomesticEstCurve["Rate"].astype(np.float64)
        else : 
            DomesticEstTerm, DomesticEstRate = [], []
        
        LD_Holiday_Curr = vb_LDHoliday.get(vb_LDHoliday.curselection()) if vb_LDHoliday.curselection() else "KRW"
        if LD_Holiday_Curr.upper() in HolidayDate.columns : 
            HolidayDomestic = list(HolidayDate[LD_Holiday_Curr.upper()].dropna().unique())  
        elif LD_Holiday_Curr.upper() == 'KRW' : 
            HolidayDomestic = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif LD_Holiday_Curr.upper() == 'USD' :
            HolidayDomestic = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else :
            HolidayDomestic = []

        N_DomesticEst_P1 = int(str(vb_DomesticEst_P1.get(vb_DomesticEst_P1.curselection())).split(".")[0]) if vb_DomesticEst_P1.curselection() else -1
        if N_DomesticEst_P1 >= 0 :
            DomesticEstCurveDirectory = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == N_DomesticEst_P1]["Directory"].iloc[0]
            DomesticEstCurve = ReadCSV(DomesticEstCurveDirectory, True).applymap(lambda x : str(x).replace("-","") if "-" in str(x) else x)
            DomesticEstTerm = DomesticEstCurve["Term"].astype(np.float64)
            DomesticEstRate = DomesticEstCurve["Rate"].astype(np.float64)
        else : 
            DomesticEstTerm, DomesticEstRate = [], []

        DayCountFlag = int(str(vb_LD_DayCount.get(vb_LD_DayCount.curselection())).split(":")[0]) if vb_LD_DayCount.curselection() else 0
        
        LF_Holiday_Curr = vb_LFHoliday.get(vb_LFHoliday.curselection()) if vb_LFHoliday.curselection() else "KRW"
        if LF_Holiday_Curr.upper() in HolidayDate.columns : 
            HolidayForeign = list(HolidayDate[LF_Holiday_Curr.upper()].dropna().unique())  
        elif LF_Holiday_Curr.upper() == 'KRW' : 
            HolidayForeign = KoreaHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        elif LF_Holiday_Curr.upper() == 'USD' :
            HolidayForeign = USHolidaysFromStartToEnd(int(YYYYMMDD)//10000-1, int(YYYYMMDD)//10000 + 60)
        else :
            HolidayForeign = []
        HolidayPay = sorted(list(set(HolidayDomestic + HolidayForeign)))
        
        N_Foreign_P1 = int(str(vb_Foreign_P1.get(vb_Foreign_P1.curselection())).split(".")[0]) if vb_Foreign_P1.curselection() else 0
        if N_Foreign_P1 >= 0 and ForeignCurveNeeded == 1:
            ForeignCurveDirectory = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == N_Foreign_P1]["Directory"].iloc[0]
            ForeignCurve = ReadCSV(ForeignCurveDirectory, True).applymap(lambda x : str(x).replace("-","") if "-" in str(x) else x)
            ForeignTerm = ForeignCurve["Term"].astype(np.float64)
            ForeignRate = ForeignCurve["Rate"].astype(np.float64)
        else : 
            ForeignTerm, ForeignRate = [], []            

        if ForeignCurveNeeded == 0 : 
            ForeignTerm, ForeignRate = [], []

        DayCountFlagForeign = int(str(vb_LF_DayCount.get(vb_LF_DayCount.curselection())).split(":")[0]) if vb_LF_DayCount.curselection() else 0
            
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)            
        Spot = float(v_Spot.get()) if len(str(v_Spot.get())) > 0 else -1
        if Spot < 0 : 
            raise ValueError("Check Spot Price")            
        SwapPointUnit = float(v_SwapPointUnit.get()) if len(str(v_SwapPointUnit.get())) > 0 else 100
        NumCpnOneYear = int(vb_NumCpnOneYear_P1.get(vb_NumCpnOneYear_P1.curselection())) if vb_NumCpnOneYear_P1.curselection() else 4
        Preprocessing_ZeroTermAndRate(ForeignTerm, ForeignRate, PriceDate)
        ZeroTermForeign = ForeignTerm 
        ZeroRateForeign = ForeignRate
        ForeignEstCurveTerm = ForeignTerm
        ForeignEstCurveRate = ForeignRate
        DomesticEstCurveTerm = DomesticEstTerm
        DomesticEstCurveRate = DomesticEstRate
        Preprocessing_ZeroTermAndRate(DomesticEstCurveTerm, DomesticEstCurveRate, PriceDate)
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        SaveName = str(v_SaveName.get()) if len(str(v_SaveName.get())) > 0 else "TempCurve"          
        
        NBDList, ZeroTerm, ZeroRate, ScheduleStart, ScheduleEnd, SchedulePay, MktQuote = [], [], [], [], [], [], []
        if len(MyData[MyData["Type"].isin(['sp','Sp'])]) == 0 : 
            tstartdate = 0
            dffo = 1
        else : 
            try : 
                SwapStartDate = MyData[MyData["Type"].isin(["sw","Sw","Bs","bs"])]["StartDate"].iloc[0]
            except IndexError : 
                SwapStartDate = MyData[MyData["Type"].isin(["sp","Sp"])]["StartDate"].iloc[0]
                
            tstartdate = DayCountAtoB(int(PriceDate), SwapStartDate)/365
            rfo = Linterp(ZeroTermForeign, ZeroRateForeign, tstartdate)
            dffo = np.exp(-rfo * tstartdate)
        
        for i in range(len(MyData)) : 
            ResultEndDate = [0]
            ProductTypeString = str(MyData["Type"].iloc[i].replace(" ",""))
            ProductType = MapProductType(ProductTypeString, DomesticEstCurveRate, ZeroRateForeign)
            StartDate = int(MyData["StartDate"].iloc[i])
            SwapMat = int(MyData["Maturity"].iloc[i])
            DayAtoB = DayCountAtoB(StartDate, SwapMat)
            MarketQuote = float(MyData["MarketQuote"].iloc[i])
            ScheduleStart.append(StartDate)
            
            if ProductType == 0: 
                ScheduleEnd.append(SwapMat)
                SchedulePay.append(SwapMat)
                NBDList.append(0)
            elif ProductType == 1 or ProductType >= 3: 
                if DayAtoB < 7 : 
                    #1일 스왑
                    EndDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, 1), HolidayPay)
                    NBD = NBusinessCountFromEndToPay(EndDate, SwapMat, HolidayPay, 1, ResultEndDate)
                elif DayAtoB < 14 : 
                    #7일 스왑
                    EndDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, 7), HolidayPay)
                    NBD = NBusinessCountFromEndToPay(EndDate, SwapMat, HolidayPay, 1, ResultEndDate)
                elif DayAtoB < 21 : 
                    #14일 스왑
                    EndDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, 14), HolidayPay)
                    NBD = NBusinessCountFromEndToPay(EndDate, SwapMat, HolidayPay, 1, ResultEndDate)
                elif DayAtoB < 28 : 
                    #21일 스왑
                    EndDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, 21), HolidayPay)
                    NBD = NBusinessCountFromEndToPay(EndDate, SwapMat, HolidayPay, 1, ResultEndDate)
                else : 
                    NBD = NBusinessCountFromEndToPay(StartDate, SwapMat, HolidayPay, 1, ResultEndDate)
                    if ((i > 5) and (MyData["Type"].iloc[i] == MyData["Type"].iloc[i-1])) : 
                        NBD = NBDList[i-1]
                    EndDate = (ResultEndDate[0])//100 * 100 + (StartDate - (StartDate//100) * 100)
                    
                ScheduleEnd.append(EndDate)
                SchedulePay.append(SwapMat)
                NBDList.append(NBD)
            elif ProductType == 2 : 
                ScheduleEnd.append(SwapMat)
                SchedulePay.append(SwapMat)
                NBDList.append(0)
            
            if (ProductTypeString.lower() in ['dp','dg','deposit']) : 
                r = Calc_ZeroRate_FromDiscFactor(PriceDate, StartDate, SwapMat, MarketQuote/100, DayCountFlag, ZeroTerm, ZeroRate)
                ZeroTerm.append(DayCountAtoB(PriceDate, SwapMat)/365)
                ZeroRate.append(r)
                
            elif (ProductTypeString.lower().replace(" ","") in ['sp','swappoint']) : 
                T = DayCountAtoB(PriceDate, SwapMat)/365
                rf = Linterp(ZeroTermForeign, ZeroRateForeign, T)
                #print(rf, T, Spot, MarketQuote, SwapPointUnit)
                r = CalcZeroRateFromSwapPoint(rf, T, Spot, MarketQuote, SwapPointUnit)
                ZeroTerm.append(T)
                ZeroRate.append(r)
            elif (ProductTypeString.lower() in ['bs','sw','swap']) :
                T = DayCountAtoB(PriceDate, SwapMat)/365
                ZeroArray = np.r_[np.array(ZeroRate), 0.0]
                MaxRate = max(0.3, np.array(ZeroRate).mean() * 4)
                MinRate = min(-0.04, np.array(ZeroRate).min() - 0.03)
                TargetRate = MaxRate
                FloatFloatFlag = True if (len(DomesticEstCurveTerm) > 0 and len(ForeignEstCurveTerm) > 0) else False
                DF_to_StartDate = np.exp(-Linterp(ZeroTerm, ZeroRate, tstartdate) * tstartdate)
                ZeroTerm.append(T)
                for j in range(500) : 
                    ZeroArray[-1] = TargetRate
                    if len(ZeroTermForeign) > 0 : 
                        if FloatFloatFlag == False : 
                            Err = Calc_CRS(100, 100, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArray, NumCpnOneYear, DayCountFlag, DayCountFlagForeign, False, NBDList[i], DomesticEstCurveTerm, DomesticEstCurveRate, ForeignEstCurveTerm, ForeignEstCurveRate, ZeroTermForeign, ZeroRateForeign, HolidayDomestic, HolidayForeign, HolidayPay )
                        else : 
                            Err = Calc_CRS(100, 100 * dffo/DF_to_StartDate, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArray, NumCpnOneYear, DayCountFlag, DayCountFlagForeign, False, NBDList[i], [], [], [], [], ZeroTermForeign, ZeroRateForeign, HolidayDomestic, HolidayForeign, HolidayPay )
                    else : 
                        Err = Calc_IRS(100, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArray, NumCpnOneYear, DayCountFlag, True if Currency == "KRW" else False, NBDList[i], [], [], HolidayDomestic, HolidayDomestic )
                    
                    if abs(Err) < 0.000001 : 
                        break
                    elif Err < 0 : 
                        MaxRate = TargetRate
                        TargetRate = (MaxRate + MinRate)/2
                    else : 
                        MinRate = TargetRate
                        TargetRate = (MaxRate + MinRate)/2

                if j == 499 : 
                    RateRange = np.linspace(0.001, 0.101, 2001)
                    ZeroArrayCopy = ZeroArray.copy()
                    Err = 100
                    for j in range(len(RateRange)) : 
                        TempRate = RateRange[j]
                        ZeroArrayCopy[-1] = TempRate
                        if len(ZeroTermForeign) > 0 : 
                            if FloatFloatFlag == False : 
                                TempErr = Calc_CRS(100, 100, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArrayCopy, NumCpnOneYear, DayCountFlag, DayCountFlagForeign, False, NBDList[i], DomesticEstCurveTerm, DomesticEstCurveRate, ForeignEstCurveTerm, ForeignEstCurveRate, ZeroTermForeign, ZeroRateForeign, HolidayDomestic, HolidayForeign, HolidayPay )
                            else : 
                                TempErr = Calc_CRS(100, 100 * dffo/DF_to_StartDate, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArrayCopy, NumCpnOneYear, DayCountFlag, DayCountFlagForeign, False, NBDList[i], [], [], [], [], ZeroTermForeign, ZeroRateForeign, HolidayDomestic, HolidayForeign, HolidayPay )
                        else : 
                            TempErr = Calc_IRS(100, 0.0, ScheduleStart[i], PriceDate, ScheduleEnd[i], MarketQuote/100, ZeroTerm, ZeroArray, NumCpnOneYear, DayCountFlag, True if Currency == "KRW" else False, NBDList[i], [], [], HolidayDomestic, HolidayDomestic )

                        if abs(TempErr) < Err : 
                            Err = TempErr

                        if Err < 0.0001 : 
                            TargetRate = TempRate
                            break

                    if j == len(RateRange) - 1 : 
                        raise ValueError("Error")
                ZeroRate.append(TargetRate)
            else : 
                raise ValueError("Check the Product Type")
        for i in range(len(ZeroRate)) : 
            ZeroRate[i] *= 100
            
        ResultDF = pd.DataFrame(ZeroRate, ZeroTerm).reset_index()
        ResultDF.columns = ["Term","Rate"]
        ResultDF["PriceDate"] = [PriceDate] * len(ResultDF)  # pylint: disable=unsupported-assignment-operation
        ResultDF["NBD"] = NBDList                            # pylint: disable=unsupported-assignment-operation
        ResultDF["StartDate"] = ScheduleStart                # pylint: disable=unsupported-assignment-operation
        ResultDF["EndDate"] = ScheduleEnd                    # pylint: disable=unsupported-assignment-operation
        ResultDF["PayDate"] = SchedulePay                    # pylint: disable=unsupported-assignment-operation
        CurrencyName = Currency if ForeignCurveNeeded == 0 else str(Currency).replace(" ","").split(",")[0]
        SavePrint = ""
        if LoggingFlag > 0 : 
            if YYYYMMDD not in os.listdir(currdir + "\\MarketData\\outputdata") : 
                print("경로생성")
                os.makedirs(currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD), exist_ok=True)
                os.makedirs(currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD) + "\\" + CurrencyName, exist_ok=True)    
                    
            cvname = SaveName
            targetdir = currdir + "\\MarketData\\outputdata\\" + str(YYYYMMDD) + "\\" + str(CurrencyName)
            try : 
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultDF.to_csv(TheName, index = False, encoding = "cp949")
                    SavePrint = ("\n" + TheName + "저장 완료\n")
            except FileNotFoundError : 
                os.makedirs(currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD) + "\\" + CurrencyName)    
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultDF.to_csv(TheName, index = False, encoding = "cp949")
                    SavePrint = ("\n" + TheName + "저장 완료\n")        
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)

        ResultDF = ResultDF.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultDF, width = 100)          
        output_label.config(text = f"저장: \n{SavePrint}", font = ("맑은 고딕", 12, 'bold'))

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2 
        MyArrays[4] = ResultDF 
               
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
                
    root.mainloop()
    return MyArrays[4]

def PriceToSwaptionVolProgram(YYYYMMDD, Name, Data, currdir, HolidayFile) : 
    MyData = Data[0].set_index("스왑만기/옵션만기" if "스왑만기/옵션만기" in Data[0].columns else "SwapMat/OptMat")
    ZeroCurveName = Name[0]    
    Currency = ZeroCurveName.split("\\")[-2]
    Holidays = list(HolidayFile[Currency].dropna().unique())
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namenotin = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))

    root = tk.Tk()
    root.title("ZeroMaker")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)
    
    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_SelectedCurve_P1 = make_listvariable_interface(left_frame, 'ZeroCurve', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "ZeroCurve INFO", defaultflag = True, defaultvalue = 0, pady = 10, DefaultStringList=["IRS"])
    v_PriceDate = make_variable_interface(left_frame, 'PriceDate', bold = True, textfont = 11, defaultflag = True, defaultvalue=int(YYYYMMDD))
    vb_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=0 if Currency == "USD" else 2)
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCountFlag', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 4, textfont = 11, defaultflag=True, defaultvalue=1 if Currency == "USD" else 0)
    vb_VolFlag = make_listvariable_interface(left_frame, 'VolFlag', ["0: Black Vol","1: Normal Vol"], listheight = 2, textfont = 11, pady = 2, defaultflag = True, defaultvalue = 1)
    vb_Logging = make_listvariable_interface(left_frame, 'CSVLogging', ["0: Logging안함","1: CSVLogging"], listheight = 2, textfont = 11, pady = 10)
    v_SaveName = make_variable_interface(left_frame, '저장할 커브볼 명\n(ex: KRW IRS Swaption Vol)', bold = True, textfont = 11, defaultflag = True, defaultvalue="")
        
    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 3, pady = 5, anchor = 'n')

    newtree = ttk.Treeview(root, height = 30)
    newtree.pack(side = 'left', padx=5, pady=10, expand=False, anchor = 'n')        
    NewTreeFlag = insert_dataframe_to_treeview(newtree, (MyData*100).round(2).reset_index(), width = 50)       
    PrevTreeFlag, tree, tree2, scrollbar, scrollbar2, ResultDF = 0, None, None, None, None, pd.DataFrame([])
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, ResultDF, tree2]    
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        ResultDF = MyArrays[4]
        tree2 = MyArrays[5]
        
        N_Curve_P1 = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 0
        CurveDirectory = GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == N_Curve_P1]["Directory"].iloc[0]
        MyData2 = ReadCSV(CurveDirectory, True).applymap(lambda x : str(x).replace("-","") if "-" in str(x) else x)
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else int(YYYYMMDD)  
        if PriceDate < 19000101 : 
            PriceDate = ExcelDateToYYYYMMDD(PriceDate)          
        elif PriceDate < 1 : 
            raise ValueError("Check PriceDate")
        NCPN_Ann = int(vb_NumCpnOneYear_P1.get(vb_NumCpnOneYear_P1.curselection())) if vb_NumCpnOneYear_P1.curselection() else 4
        DayCountFlag = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else 0
        VolFlag = int(str(vb_VolFlag.get(vb_VolFlag.curselection())).split(":")[0]) if vb_VolFlag.curselection() else 0
        Term = MyData2["Term"].astype(np.float64).values
        Rate = MyData2["Rate"].astype(np.float64).values
        Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)
        LoggingFlag = int(str(vb_Logging.get(vb_Logging.curselection())).split(":")[0]) if vb_Logging.curselection() else 0
        SaveName = str(v_SaveName.get()) if len(str(v_SaveName.get())) > 0 else "TempSwaptionVolCurve"
        ResultValues = np.zeros(shape = MyData.shape)
        ResultValues2 = np.zeros(shape = MyData.shape)
        CurrencyName = Currency
        for i in range((MyData.shape[0])) : 
            for j in range((MyData.shape[1])) : 
                TargetPrice = MyData.values[i][j]
                StartDate = EDate_YYYYMMDD(PriceDate, int(MyData.columns[j])) 
                EndDate = EDate_YYYYMMDD(StartDate, int(MyData.index[i])) 
                v = FindSwaptionImpliedVolatility(PriceDate, StartDate, EndDate, NCPN_Ann, Term, Rate, TargetPrice, DayCountFlag, VolFlag, Nominal = 1, HolidayFlag = 'kr' if 'KRW' == CurrencyName else '', SelfHolidays= Holidays, FixedPayer0Receiver1=0)
                ResultValues[i][j] = v["ImpliedVol"]
                ResultValues2[i][j] = v["ForwardSwapRate"]
        SaveYN, SaveDir = 0, ""
        ResultDF = pd.DataFrame(ResultValues, index = MyData.index, columns = MyData.columns)
        ResultDF2 = pd.DataFrame(ResultValues2, index = MyData.index, columns = MyData.columns)
        if LoggingFlag > 0 : 
            if YYYYMMDD not in os.listdir(currdir + "\\MarketData\\outputdata") : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD))
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD) + "\\" + CurrencyName)    
                    
            cvname = SaveName
            targetdir = currdir + "\\MarketData\\outputdata\\" + str(YYYYMMDD) + "\\" + str(CurrencyName)
            print("\n저장시도\n")
            try : 
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultDF.to_csv(TheName, index = True, encoding = "cp949")
                    SaveYN = 1
                    SaveDir = TheName
                    print("\n저장완료\n")
            except FileNotFoundError : 
                os.system('mkdir ' + currdir + '\\MarketData\\outputdata\\' + str(YYYYMMDD) + "\\" + CurrencyName)    
                if cvname + ".csv" not in os.listdir(targetdir) : 
                    TheName = targetdir + "\\" + cvname + ".csv"
                    ResultDF.to_csv(TheName, index = True, encoding = "cp949")
                    SaveYN = 1
                    SaveDir = TheName
                    print("\n저장완료\n")
        
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
            tree2 = ttk.Treeview(root)
        else : 
            tree.destroy()
            tree2.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
            tree2 = ttk.Treeview(root)

        ResultDF = ResultDF.applymap(lambda x : np.round(x, 6) if isinstance(x, float) else x)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        tree2.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, (ResultDF*100).round(4).reset_index(), width = 50)
        PrevTreeFlag2 = insert_dataframe_to_treeview(tree2, (ResultDF2*100).round(4).reset_index(), width = 50)          
        output_label.config(text = f"저장: \n{SaveYN}\n저장위치:\n{SaveDir}", font = ("맑은 고딕", 12, 'bold'))

        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2 
        MyArrays[4] = ResultDF 
        MyArrays[5] = tree2
               
    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 10, pady = 10, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 10).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2) 
    root.mainloop()    
    return 1    
    
def Calc_dSdx(t, PriceDate, SwapStart, ResultForwardEnd, ZeroTerm, ZeroRate, DayCountFlag, kappa) : 
    T0 = DayCountAtoB(PriceDate, SwapStart)/365
    T_i = np.vectorize(DayCountAtoB)([PriceDate], ResultForwardEnd)/365
    T = np.r_[[T0],T_i]
    FwdDscFunc = np.vectorize(lambda Time : Calc_ForwardDiscount_Factor(ZeroTerm, ZeroRate, t, Time))
    DF = FwdDscFunc(T)
    DateList = np.r_[[SwapStart],ResultForwardEnd]
    Deltat = np.vectorize(DayCountFractionAtoB)(DateList[:-1],DateList[1:], [DayCountFlag])
    Annuity = DF[1:] * Deltat
    ForwardSwapRate = (DF[0] - DF[-1])/(Annuity.sum())
    BtT = np.vectorize(lambda t1, t2: B_s_to_t(t1, t2, kappa))([t],T)
    dSdx = -1/(Annuity.sum()) * (DF[0] * BtT[0] - DF[-1] * BtT[-1]) + ForwardSwapRate / (Annuity.sum()) * (Annuity * BtT[1:]).sum()
    return dSdx

def Calc_SwaptionNormalVolatilityAnalytic(kappa, swaptionvol, PriceDate, SwapStart, SwapMat, ZeroTerm, ZeroRate, NumCpnOneYear = 4, DayCountFlag = 0, Holidays = []) : 
    ResultForwardStart, ResultForwardEnd, ResultPayDate, ResultNBD = MappingCouponDates(1,SwapStart,SwapMat,0,NumCpnOneYear,1,Holidays,Holidays,1)
    f = np.vectorize(lambda t : Calc_dSdx(t, PriceDate, SwapStart, ResultForwardEnd, ZeroTerm, ZeroRate, DayCountFlag, kappa))
    tstart = DayCountAtoB(PriceDate, SwapStart)/365
    tarray = np.linspace(0, tstart, 5)
    dtarray = tarray[1:] - tarray[:-1]
    dSdXArray = f(tarray[1:]) 
    normalv = np.sqrt(1/tstart * (dSdXArray * dSdXArray * swaptionvol * swaptionvol * dtarray).sum())
    return normalv

def ErrorVolatilityRatio(kappa, PriceDate, SwapStartArray, SwapMaturity1Array, SwapMaturity2Array, SwaptionVol1Array, SwaptionVol2Array, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, KoreanHolidayFlag = True, AddHolidays = []) : 
    if KoreanHolidayFlag == True : 
        Holidays = KoreaHolidaysFromStartToEnd(SwapStartArray[0]//10000, SwapMaturity2Array[-1]//10000)
    else : 
        Holidays = AddHolidays
    f = np.vectorize(lambda k, Start, Mat, v: Calc_SwaptionNormalVolatilityAnalytic(k, v, PriceDate, Start, Mat, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, Holidays))
    v1model = f([kappa], SwapStartArray, SwapMaturity1Array, SwaptionVol1Array)
    v2model = f([kappa], SwapStartArray, SwapMaturity2Array, SwaptionVol2Array)
    VRatioModel = v2model/v1model
    vRatioMarket = np.array(SwaptionVol2Array)/np.array(SwaptionVol1Array)
    ErrSquare = ((VRatioModel - vRatioMarket)**2).sum()
    return np.maximum(0.00001,np.minimum(1000000000,ErrSquare))

def CalibrationKappaFromSwapRatio(PriceDate, SwapStartArray, SwapMaturity1Array, SwapMaturity2Array, SwaptionVol1Array, SwaptionVol2Array, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, KoreanHolidayFlag = False, AddHolidays = [], KAPPAMIN = -0.05, KAPPAMAX = 0.15) : 
    if KoreanHolidayFlag == True : 
        Holidays = KoreaHolidaysFromStartToEnd(SwapStartArray[0]//10000, SwapMaturity2Array[-1]//10000)
    else : 
        Holidays = AddHolidays
    kappamin = min(KAPPAMIN, KAPPAMAX)    
    kappamax = max(KAPPAMIN, KAPPAMAX)
    kappas = np.linspace(kappamin, kappamax, 41)
    kappas = kappas[kappas != 0]
    f = np.vectorize(lambda k : ErrorVolatilityRatio(k, PriceDate, SwapStartArray, SwapMaturity1Array, SwapMaturity2Array, SwaptionVol1Array, SwaptionVol2Array, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, KoreanHolidayFlag = False, AddHolidays = Holidays))
    errs = f(kappas)
    kappamin = kappas[errs.argmin()] - 0.02
    kappamax = kappas[errs.argmin()] + 0.02
    kappas = np.linspace(kappamin, kappamax, 21)
    kappas = kappas[kappas != 0]
    errs = f(kappas)
    calibratedkappa = kappas[errs.argmin()]
    f = np.vectorize(lambda k, Start, Mat, v: Calc_SwaptionNormalVolatilityAnalytic(k, v, PriceDate, Start, Mat, ZeroTerm, ZeroRate, NumCpnOneYear, DayCountFlag, Holidays))
    v1model = f([calibratedkappa], SwapStartArray, SwapMaturity1Array, SwaptionVol1Array)
    v2model = f([calibratedkappa], SwapStartArray, SwapMaturity2Array, SwaptionVol2Array)
    VRatioModel = v2model/v1model
    vRatioMarket = np.array(SwaptionVol2Array)/np.array(SwaptionVol1Array)
    ErrSquare = ((VRatioModel - vRatioMarket)**2).sum()    
    Err = VRatioModel - vRatioMarket
    return {'kappa':calibratedkappa, 'v1market':SwaptionVol1Array,'v2market':SwaptionVol2Array,'v1model':v1model, 'v2model':v2model, 'VRatioModel':VRatioModel,'vRatioMarket':vRatioMarket, 'ErrSquare':ErrSquare, 'Err': Err}

def KappaCalibration(HolidayDate, currdir = os.getcwd()) : 
    YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\outputdata",MultiSelection=False, namenotin = "Vol", Comments="Pricing을 위한 ZeroCurve", DefaultStringList= ["IRS"])
    ZeroCurve = Data[0]
    ZeroTerm = ZeroCurve["Term"].astype(np.float64)
    ZeroRate = ZeroCurve["Rate"].astype(np.float64)
    ZeroCurveName = Name[0].split("\\")[-1].replace(".csv","")  
    Currency = Name[0].split("\\")[-2]
    Holidays = list(HolidayDate[Currency].dropna().unique()) if Currency in HolidayDate.columns else []
    Data = MarketDataFileListPrint(currdir + '\\MarketData\\outputdata', namein = 'vol').sort_values(by = "YYYYMMDD")[-50:]
    Data = Data[Data['DirectoryPrint'].apply(lambda x : ('EQ' in str(x).upper() and 'VOL' in str(x).upper()) == False)] #Out EQ Vol 
    GroupbyYYYYMMDD = Data[Data["YYYYMMDD"] == YYYYMMDD]
    GroupbyYYYYMMDD["Currency"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split("\\")[-2])
    GroupbyYYYYMMDD["ListName"] = GroupbyYYYYMMDD["DirectoryPrint"].apply(lambda x : x.split(".")[0] + '. ' + x.split("\\")[-1].replace(".csv",""))            

    root = tk.Tk()
    root.title("Kappa Calibration")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    vb_zerocurve = make_listvariable_interface(left_frame, 'ZeroCurve(자동Load)', termratestr(ZeroTerm, ZeroRate), titleName = "MARKET DATA INFO", titlelable= True, listheight = 15, textfont = 11)
    vb_SelectedCurve_P1 = make_listvariable_interface(left_frame, 'Swaption Vol 선택', list(GroupbyYYYYMMDD["ListName"]), listheight = 5, textfont = 11, titlelable = True, titleName = "Swaption Info", defaultflag = True, defaultvalue = 0, width = 40, DefaultStringList=["Vol"])
    vb_L1_NumCpnOneYear_P1 = make_listvariable_interface(left_frame, '연 쿠폰지급수 \n(리스트에서 선택)', ["1","2","4","6"], listheight = 4, textfont = 11, defaultflag = True, defaultvalue=2)
    vb_DayCount = make_listvariable_interface(left_frame, 'DayCount', ["0: ACT/365","1: ACT/360","2: ACT/ACT","3: 30/360"], listheight = 3, textfont = 11, defaultflag = True, defaultvalue = 0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')

    Result = {'CalibrationTrue':False}
    PrevTreeFlag, tree, scrollbar, scrollbar2, tree2, tree3 = 0, None, None, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2, Result, tree2, tree3]
    def run_function(MyArrays) :     

        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]  
        CalcResult = MyArrays[4] 
        tree2 = MyArrays[5]     
        tree3 = MyArrays[6]
        PriceDate = int(YYYYMMDD)
        L1_NumCpnOneYear_P1 = int(vb_L1_NumCpnOneYear_P1.get(vb_L1_NumCpnOneYear_P1.curselection())) if vb_L1_NumCpnOneYear_P1.curselection() else 4
        DayCount = int(str(vb_DayCount.get(vb_DayCount.curselection())).split(":")[0]) if vb_DayCount.curselection() else (0 if L1_NumCpnOneYear_P1 != 0 else 3)
        SelectedNumber = int(str(vb_SelectedCurve_P1.get(vb_SelectedCurve_P1.curselection())).split(".")[0]) if vb_SelectedCurve_P1.curselection() else 1
        VolRawData = ReadCSV(GroupbyYYYYMMDD[GroupbyYYYYMMDD["Number"] == SelectedNumber]['Directory'].iloc[0])
        voldf = VolRawData.set_index(VolRawData.columns[0])
        SwapStartList = []
        SwapMaturity1List = []
        SwapMaturity2List = []
        v1List = []
        v2List = []
        i = 0
        j1 = 0
        j2 = -1
        for i in range(len(voldf.columns)) : 
            SwapStartDate = EDate_YYYYMMDD(PriceDate, int(voldf.columns[i]))
            SwapMaturityDate1 = EDate_YYYYMMDD(SwapStartDate, int(voldf.index[j1]))
            SwapMaturityDate2 = EDate_YYYYMMDD(SwapStartDate, int(voldf.index[j2]))
            v1 = voldf[voldf.columns[i]].iloc[j1]
            v2 = voldf[voldf.columns[i]].iloc[j2]
            SwapStartList.append(SwapStartDate)
            SwapMaturity1List.append(SwapMaturityDate1)
            SwapMaturity2List.append(SwapMaturityDate2)
            v1List.append(v1)
            v2List.append(v2)    
        Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
        CalibResult = CalibrationKappaFromSwapRatio(PriceDate, SwapStartList, SwapMaturity1List, SwapMaturity2List, v1List, v2List, ZeroTerm, ZeroRate, L1_NumCpnOneYear_P1, DayCount, KoreanHolidayFlag = False, AddHolidays = Holidays)
        CalcResult['CalibrationTrue'] = True
        CalcResult['kappa'] = CalibResult['kappa']
        CalcResult['v1market'] = CalibResult['v1market']
        CalcResult['v2market'] = CalibResult['v2market']    
        CalcResult['v1model'] = CalibResult['v1model']
        CalcResult['v2model'] = CalibResult['v2model']
        CalcResult['VRatioModel'] = CalibResult['VRatioModel']
        CalcResult['vRatioMarket'] = CalibResult['vRatioMarket']
        CalcResult['ErrSquare'] = CalibResult['ErrSquare']
        CalcResult['Err'] = CalibResult['Err']
        
        v1mar = pd.Series(CalibResult["v1market"], name = "v1market") * 100
        v2mar = pd.Series(CalibResult["v2market"], name = "v2market") * 100
        v1mod = pd.Series(CalibResult["v1model"], name = "v1model") * 100
        v2mod = pd.Series(CalibResult["v2model"], name = "v2model") * 100
        VRatioModel = pd.Series(CalibResult["VRatioModel"], name = "VRatioModel")
        vRatioMarket = pd.Series(CalibResult["vRatioMarket"], name = "vRatioMarket")
        resultdf = pd.concat([v1mar, v2mar, v1mod, v2mod, VRatioModel, vRatioMarket],axis = 1)
        resultdf['kappa'] = CalibResult['kappa']
        resultdf['ErrSquareSum'] = CalibResult['ErrSquare']
        resultdf['Err'] = CalibResult['Err']
        
        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        tree.pack(padx=5, pady=5, fill="both", expand=False)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        
        PrevTreeFlag = insert_dataframe_to_treeview(tree, resultdf.round(6), width = 80)

        output_label.config(text = f"\n결과: \nkappa ={np.round(float(resultdf['kappa'].iloc[0]),6)}", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree 
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2        
    temp_func = lambda : run_function(MyArrays)            
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)

    root.mainloop()      
    return 0, 0, 0, 0    
    
def CalcFXDeltaProgram_FromFXPosition(FXSpot) : 

    root = tk.Tk()
    root.title("FX Delta Calculator(from FX Position)")
    root.geometry("1500x750+30+30")
    root.resizable(False, False)

    left_frame = tk.Frame(root)
    left_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Currency1 = make_variable_interface(left_frame, 'CurrencyName1', bold = False, textfont = 11, defaultflag = True, defaultvalue='USD')
    v_Currency2 = make_variable_interface(left_frame, 'CurrencyName2', bold = False, textfont = 11, defaultflag = True, defaultvalue='JPY')
    v_Currency3 = make_variable_interface(left_frame, 'CurrencyName3', bold = False, textfont = 11, defaultflag = True, defaultvalue='CNH')
    v_Currency4 = make_variable_interface(left_frame, 'CurrencyName4', bold = False, textfont = 11, defaultflag = True, defaultvalue='BRL')
    v_Currency5 = make_variable_interface(left_frame, 'CurrencyName5', bold = False, textfont = 11, defaultflag = True, defaultvalue='EUR')
    v_Currency6 = make_variable_interface(left_frame, 'CurrencyName6', bold = False, textfont = 11, defaultflag = True, defaultvalue='CHF')
    v_Currency7 = make_variable_interface(left_frame, 'CurrencyName7', bold = False, textfont = 11, defaultflag = True, defaultvalue='AUD')
    v_Currency8 = make_variable_interface(left_frame, 'CurrencyName8', bold = False, textfont = 11, defaultflag = True, defaultvalue='THB')
    v_Currency9 = make_variable_interface(left_frame, 'CurrencyName9', bold = False, textfont = 11, defaultflag = True, defaultvalue='GBP')

    center_frame = tk.Frame(root)
    center_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_Position1 = make_variable_interface(center_frame, 'CurrencyPosition1', bold = False, textfont = 11, defaultflag = True, defaultvalue=100)
    v_Position2 = make_variable_interface(center_frame, 'CurrencyPosition2', bold = False, textfont = 11, defaultflag = False, defaultvalue=0)
    v_Position3 = make_variable_interface(center_frame, 'CurrencyPosition3', bold = False, textfont = 11, defaultflag = True, defaultvalue=-10)
    v_Position4 = make_variable_interface(center_frame, 'CurrencyPosition4', bold = False, textfont = 11, defaultflag = False, defaultvalue=0)
    v_Position5 = make_variable_interface(center_frame, 'CurrencyPosition5', bold = False, textfont = 11, defaultflag = False, defaultvalue=3.4)
    v_Position6 = make_variable_interface(center_frame, 'CurrencyPosition6', bold = False, textfont = 11, defaultflag = False, defaultvalue=0)
    v_Position7 = make_variable_interface(center_frame, 'CurrencyPosition7', bold = False, textfont = 11, defaultflag = False, defaultvalue=0)
    v_Position8 = make_variable_interface(center_frame, 'CurrencyPosition8', bold = False, textfont = 11, defaultflag = False, defaultvalue=0)
    v_Position9 = make_variable_interface(center_frame, 'CurrencyPosition9', bold = False, textfont = 11, defaultflag = False, defaultvalue=0)

    Result_frame = tk.Frame(root)
    Result_frame.pack(side = 'left', padx = 5, pady = 5, anchor = 'n')
    v_PriceDate = make_variable_interface(Result_frame, 'PriceDate', bold = True, textfont = 11, pady = 3, defaultflag = True, defaultvalue = int('20250102'))
    Value = 0
    PV01, TempPV01 = None, None
    PrevTreeFlag, tree, scrollbar, scrollbar2 = 0, None, None, None
    MyArrays = [PrevTreeFlag, tree, scrollbar, scrollbar2]
    def run_function(MyArrays) : 
        PrevTreeFlag = MyArrays[0] 
        tree = MyArrays[1] 
        scrollbar = MyArrays[2]
        scrollbar2 = MyArrays[3]        
        PriceDate = int(v_PriceDate.get()) if len(str(v_PriceDate.get())) > 0 else 20250102
        Position1 = float(v_Position1.get()) if len(str(v_Position1.get())) > 0 else 0
        Position2 = float(v_Position2.get()) if len(str(v_Position2.get())) > 0 else 0
        Position3 = float(v_Position3.get()) if len(str(v_Position3.get())) > 0 else 0
        Position4 = float(v_Position4.get()) if len(str(v_Position4.get())) > 0 else 0
        Position5 = float(v_Position5.get()) if len(str(v_Position5.get())) > 0 else 0
        Position6 = float(v_Position6.get()) if len(str(v_Position6.get())) > 0 else 0
        Position7 = float(v_Position7.get()) if len(str(v_Position7.get())) > 0 else 0
        Position8 = float(v_Position8.get()) if len(str(v_Position8.get())) > 0 else 0
        Position9 = float(v_Position9.get()) if len(str(v_Position9.get())) > 0 else 0

        Currency1 = str(v_Currency1.get()) if len(str(v_Currency1.get())) > 0 else "NAN"
        Currency2 = str(v_Currency2.get()) if len(str(v_Currency2.get())) > 0 else "NAN"
        Currency3 = str(v_Currency3.get()) if len(str(v_Currency3.get())) > 0 else "NAN"
        Currency4 = str(v_Currency4.get()) if len(str(v_Currency4.get())) > 0 else "NAN"
        Currency5 = str(v_Currency5.get()) if len(str(v_Currency5.get())) > 0 else "NAN"
        Currency6 = str(v_Currency6.get()) if len(str(v_Currency6.get())) > 0 else "NAN"
        Currency7 = str(v_Currency7.get()) if len(str(v_Currency7.get())) > 0 else "NAN"
        Currency8 = str(v_Currency8.get()) if len(str(v_Currency8.get())) > 0 else "NAN"
        Currency9 = str(v_Currency9.get()) if len(str(v_Currency9.get())) > 0 else "NAN"
        MyListPos = [Position1, Position2, Position3, Position4, Position5, 
                    Position6, Position7, Position8, Position9]
        MyListCur = [Currency1, Currency2, Currency3, Currency4, Currency5, 
                    Currency6, Currency7, Currency8, Currency9]
        CurrencyList , CurrencyPosition = [], []
        for i in range(len(MyListPos)) : 
            if MyListPos[i] != 0 : 
                CurrencyList.append(MyListCur[i])
                CurrencyPosition.append(MyListPos[i])

        FXPosKRWV = []
        FXPosCurr = []
        FXRateList = []
        ErrorCheck = False
        ErrorString = ''
        for c, p in zip(CurrencyList, CurrencyPosition) : 
            FXRate = CalcFXRateToKRW(FXSpot, c, str(PriceDate))
            Pos = FXRate * float(p)
            if FXRate >= 0 : 
                FXPosKRWV.append(Pos)
                FXPosCurr.append(c + "/KRW")
                FXRateList.append(FXRate)
            else : 
                ErrorCheck = True
                ErrorString += c+'/KRW,\n'
        
        FXRateSeries = pd.Series(FXRateList + [1], index = FXPosCurr + ['Total'])
        ErrorStringResult = ErrorString[:-1] + '\nmust in FXSpot.csv File' if ErrorCheck else "Calculated\nSuccessfully"
        
        Bucket = pd.Series(FXPosCurr, name = 'Bucket')
        Delta = pd.Series(FXPosKRWV, name = 'Delta')
        InputData = pd.DataFrame([Bucket, Delta]).T
        InputData["Risk_Type"] = "Delta"
        ResultData = Calc_FXRDelta(InputData, HighLiquidCurrency, "Delta")

        if PrevTreeFlag == 0 : 
            tree = ttk.Treeview(root)
        else : 
            tree.destroy()
            scrollbar.destroy()
            scrollbar2.destroy()
            tree = ttk.Treeview(root)
        ResultData = ResultData.applymap(lambda x : np.round(x, 4) if isinstance(x, float) else x)
        ResultData["Bucket"] = ResultData['Bucket'].apply(lambda x : 'Total' if '99999' in str(x) else x)
        ResultData["FXRate"] = ResultData["Bucket"].map(FXRateSeries)
        tree.pack(padx=5, pady=5, fill="both", expand=True)    
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        scrollbar2 = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.configure(xscrollcommand=scrollbar2.set)
        scrollbar.pack(side="right", fill="y")    
        scrollbar2.pack(side="bottom", fill="x")    
        PrevTreeFlag = insert_dataframe_to_treeview(tree, ResultData, width = 100)
        output_label.config(text = f"\n에러메시지:\n{ErrorStringResult}", font = ("맑은 고딕", 12, 'bold'))
        MyArrays[0] = PrevTreeFlag 
        MyArrays[1] = tree
        MyArrays[2] = scrollbar
        MyArrays[3] = scrollbar2

    temp_func = lambda : run_function(MyArrays)
    tk.Button(Result_frame, text = '실행', padx = 20, pady = 20, font = ("맑은 고딕",12,'bold'), command = temp_func, width = 15).pack()
    output_label = tk.Label(Result_frame, text = "", anchor = "n")
    output_label.pack(padx = 5, pady = 2)
    root.mainloop()

def PreprocessingFXSpotData(DataDirectory) :     
    try : 
        FXSpot = ReadCSV(DataDirectory).dropna(how = 'all').fillna(method = 'ffill').applymap(lambda x : str(x).replace(",","").replace("-","")).astype(np.float64)
        FXSpot["Date"] = FXSpot["Date"].astype(np.int64)
        FXSpot = FXSpot.set_index("Date")
        if FXSpot.index[0] < 19000101 : 
            MyList = []
            for i in range(len(FXSpot.index)) : 
                MyList.append(ExcelDateToYYYYMMDD(FXSpot.index[i]))
            FXSpot.index = MyList
    except FileNotFoundError : 
        FXSpot = pd.DataFrame([])
    return FXSpot    
    

def CurveNamePreprocessingBankStyle(cvname) : 
    if "ZeroCurve" in cvname : 
        cvname = cvname.replace("ZeroCurve","")
    elif "Zero" in cvname : 
        cvname = cvname.replace("Zero","")
    
    if "IRS" in cvname : 
        cvname = cvname.replace("IRS",":Std")
    elif "CRS" in cvname : 
        cvname = cvname.replace("CRS","FX")        
    return cvname

VectorizedCurveNamePreprocessing = np.vectorize(CurveNamePreprocessingBankStyle)

def AddFRTB_BookedPosition(currdir, RAWData, RAWFORMAT) : 
    ResultAddData = pd.DataFrame([])    
    
    try : 
        Bond = ReadCSV(currdir + '\\Book\\Bond\\Bond.csv')
        Bond["ProductType"] = "Bond"
        IRS = ReadCSV(currdir + '\\Book\\IRS\\IRS.csv')
        IRS["ProductType"] = "IRS"
        if 'CRS.csv' in os.listdir(currdir + '\\Book\\IRS') : 
            CRS = ReadCSV(currdir + '\\Book\\IRS\\CRS.csv')
            CRS["Nominal"] = CRS["Nominal1"]
            CRS["EndDate"] = CRS["SwapMaturity"]
            CRS["CpnRate"] = CRS["LDFixedCpnRate"]
        else : 
            CRS = pd.DataFrame([])
        concatdata = pd.concat([Bond, IRS, CRS],axis = 0)
        concatdata.index = np.arange(len(concatdata))
        FXSpot = PreprocessingFXSpotData(currdir + "\\MarketData\\spot\\FXSpot.csv")                
        if RAWFORMAT == 1 : 
            PriceDate = RAWData["기준일자"].iloc[0]
            if len(Bond) + len(IRS) + len(CRS)> 0 : 
                #AddBookedPosition = input("\nBooking된 " + str(len(Bond) + len(IRS)) + "건의 포지션을 FRTB SA 계산에 추가하겠습니까?(Y/N)\n->").lower()
                AddBookedPosition = MainViewer(Title = 'Continue', MyText = currdir + "\\Book\n에 Booking된 " + str(len(Bond) + len(IRS) + len(CRS)) + "건의 포지션을\n FRTB SA 계산에 추가하겠습니까?", MyList = ["0: 추가안함", "1: 추가함"], size = "1550x450+5+5", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name", addtreeflag=True, treedata = concatdata, width = 60)
                if AddBookedPosition == 1 :
                    Depart = MainViewer2(Title = "Department Name",MyText = "부점명을 입력하시오",size = "800x450+30+30", textfont = 14, defaultvalue = "TempDepart")#input("\n 부점명을 입력하시오. (ex : 자금운용실)\n-> ")
                    for i in range(len(Bond)) : 
                        cvname = Bond["DiscCurveName"].iloc[i].replace(".csv","")
                        girrcol = [s for s in Bond.columns if "girr1_" in s.lower()]                    
                        girrtenor = [float(s.replace("GIRR1_","")) for s in girrcol]
                        csrcol = [s for s in Bond.columns if "csr1_" in s.lower()]
                        csrtenor = [float(s.replace("CSR1_","")) for s in csrcol]
                        cvname = CurveNamePreprocessingBankStyle(cvname)

                        # GIRR Mapping
                        TempData = pd.DataFrame(Bond[girrcol].iloc[i].values, columns = ["델타민감도"]).fillna(0)
                        fxrate = CalcFXRateToKRW(FXSpot, Bond["Currency"].iloc[i], PriceDate)
                        TempData["델타민감도"] = TempData["델타민감도"].astype(np.float64) * fxrate 
                        TempData["기준일자"] = PriceDate
                        TempData["계정구분코드"] = 10
                        TempData["계정명"] = "은행"
                        TempData["부점코드"] = 12345
                        TempData["부점명"] = Depart
                        TempData["팀코드"] = 12345
                        TempData["팀명"] = "TempTeam"
                        TempData["데스크코드"] = 12345
                        TempData["데스크명"] = "TempDesk"
                        TempData["포트폴리오"] = "TempPort"
                        TempData["리스크군"] = "일반금리(GIRR)"
                        TempData["민감도유형"] = "델타"
                        TempData["포지션 ID"] = 12345
                        TempData["뮤렉스 ID"] = 12345
                        TempData["버킷"] = Bond["Currency"].iloc[i]
                        
                        TempData["리스크요소1"] = cvname
                        TempData["리스크요소2"] = girrtenor
                        TempData["리스크요소3"] = "RATE"
                        TempData["베가민감도"] = 0
                        TempData["상향커버쳐"] = 0
                        TempData["하향커버쳐"] = 0
                        TempData = TempData[TempData["델타민감도"] != 0]

                        # CSR Mapping
                        TempData2 = pd.DataFrame(Bond[csrcol].iloc[i].values, columns = ["델타민감도"]).fillna(0)
                        TempData2["델타민감도"] = TempData2["델타민감도"].astype(np.float64) * fxrate
                        
                        TempData2["기준일자"] = PriceDate
                        TempData2["계정구분코드"] = 10
                        TempData2["계정명"] = "은행"
                        TempData2["부점코드"] = 12345
                        TempData2["부점명"] = Depart
                        TempData2["팀코드"] = 12345
                        TempData2["팀명"] = "TempTeam"
                        TempData2["데스크코드"] = 12345
                        TempData2["데스크명"] = "TempDesk"
                        TempData2["포트폴리오"] = "TempPort"
                        TempData2["리스크군"] = "신용스프레드(CSR)"
                        TempData2["민감도유형"] = "델타"
                        TempData2["포지션 ID"] = 12345
                        TempData2["뮤렉스 ID"] = 12345
                        TempData2["버킷"] = "[" + ('0' + str(Bond["CsrBucket"].iloc[i]))[-2:] + "]"
                        TempData2["리스크요소1"] = "TempIssuer" + str(Bond["CsrBucket"].iloc[i])
                        TempData2["리스크요소2"] = cvname
                        TempData2["리스크요소3"] = csrtenor
                        TempData2["베가민감도"] = 0
                        TempData2["상향커버쳐"] = 0
                        TempData2["하향커버쳐"] = 0                        
                        ResultAddData = pd.concat([ResultAddData, TempData, TempData2],axis = 0)

                    for i in range(len(IRS)) : 
                        cvnamedsc1 = str(IRS["DiscCurveNameLeg1"].iloc[i]).replace(".csv","")
                        cvnameest1 = str(IRS["EstCurveNameLeg1"].iloc[i]).replace(".csv","")
                        cvnamedsc2 = str(IRS["DiscCurveNameLeg2"].iloc[i]).replace(".csv","")
                        cvnameest2 = str(IRS["EstCurveNameLeg2"].iloc[i]).replace(".csv","")                        
                        girrcol1 = [s for s in IRS.columns if "girr1_" in s.lower()]
                        girrcol2 = [s for s in IRS.columns if "girr2_" in s.lower()]
                        girrcol3 = [s for s in IRS.columns if "girr3_" in s.lower()]
                        girrcol4 = [s for s in IRS.columns if "girr4_" in s.lower()]
                        girrcol = girrcol1 + girrcol2 + girrcol3 + girrcol4
                        cvnamelist = [cvnamedsc1] * len(girrcol1) + [cvnameest1] * len(girrcol2) + [cvnamedsc2] * len(girrcol3) + [cvnameest2] * len(girrcol4)
                        cvname = VectorizedCurveNamePreprocessing(cvnamelist)
                        girrtenor1 = [float(s.replace("GIRR1_","")) for s in girrcol1]
                        girrtenor2 = [float(s.replace("GIRR2_","")) for s in girrcol2]
                        girrtenor3 = [float(s.replace("GIRR3_","")) for s in girrcol3]
                        girrtenor4 = [float(s.replace("GIRR4_","")) for s in girrcol4]
                        girrtenor = girrtenor1 + girrtenor2 + girrtenor3 + girrtenor4                        
                        
                        TempData = pd.DataFrame(IRS[girrcol].iloc[i].values, columns = ["델타민감도"]).fillna(0)
                        fxrate = CalcFXRateToKRW(FXSpot, IRS["Currency"].iloc[i], PriceDate)
                        TempData["델타민감도"] = TempData["델타민감도"].astype(np.float64) * fxrate
                                                
                        TempData["기준일자"] = PriceDate
                        TempData["계정구분코드"] = 10
                        TempData["계정명"] = "은행"
                        TempData["부점코드"] = 12345
                        TempData["부점명"] = Depart
                        TempData["팀코드"] = 12345
                        TempData["팀명"] = "TempTeam"
                        TempData["데스크코드"] = 12345
                        TempData["데스크명"] = "TempDesk"
                        TempData["포트폴리오"] = "TempPort"
                        TempData["리스크군"] = "일반금리(GIRR)"
                        TempData["민감도유형"] = "델타"
                        TempData["포지션 ID"] = 12345
                        TempData["뮤렉스 ID"] = 12345
                        TempData["버킷"] = IRS["GirrBucket"].iloc[i]
                        TempData["리스크요소1"] = cvname
                        TempData["리스크요소2"] = girrtenor
                        TempData["리스크요소3"] = "RATE"
                        TempData["베가민감도"] = 0
                        TempData["상향커버쳐"] = 0
                        TempData["하향커버쳐"] = 0            
                        TempData = TempData[TempData["델타민감도"] != 0]
                               
                        ResultAddData = pd.concat([ResultAddData, TempData],axis = 0)
                                             
                    for i in range(len(CRS)) : 
                        cvnamedsc1 = str(CRS["DiscCurveNameLeg1"].iloc[i]).replace(".csv","")
                        cvnameest1 = str(CRS["EstCurveNameLeg1"].iloc[i]).replace(".csv","")
                        crsdomeflag = ('FX' in cvnamedsc1.upper()) or ('BASIS' in cvnamedsc1.upper()) or ('CRS' in cvnamedsc1.upper())
                        cvnamedsc2 = str(CRS["DiscCurveNameLeg2"].iloc[i]).replace(".csv","")
                        cvnameest2 = str(CRS["EstCurveNameLeg2"].iloc[i]).replace(".csv","")                             
                        crsforeflag = ('FX' in cvnamedsc2.upper()) or ('BASIS' in cvnamedsc2.upper()) or ('CRS' in cvnamedsc2.upper())
                        girrcol1 = [s for s in CRS.columns if "girr1_" in s.lower()]
                        girrcol2 = [s for s in CRS.columns if "girr2_" in s.lower()]
                        girrcol3 = [s for s in CRS.columns if "girr3_" in s.lower()]
                        girrcol4 = [s for s in CRS.columns if "girr4_" in s.lower()]                        
                        girrcol = girrcol1 + girrcol2 + girrcol3 + girrcol4
                        TypeD = ['XCCY' if crsdomeflag else 'Rate'] * (len(girrcol1) + len(girrcol2))
                        TypeF = ['XCCY' if crsforeflag else 'Rate'] * (len(girrcol3) + len(girrcol4))
                        Type = TypeD + TypeF
                        cvname = [cvnamedsc1] * len(girrcol1) + [cvnameest1] * len(girrcol2) + [cvnamedsc2] * len(girrcol3) + [cvnameest2] * len(girrcol4)
                        girrtenor1 = [float(s.replace("GIRR1_","")) for s in girrcol1]
                        girrtenor2 = [float(s.replace("GIRR2_","")) for s in girrcol2]
                        girrtenor3 = [float(s.replace("GIRR3_","")) for s in girrcol3]
                        girrtenor4 = [float(s.replace("GIRR4_","")) for s in girrcol4]
                        girrtenor = girrtenor1 + girrtenor2 + girrtenor3 + girrtenor4
                        TempData = pd.DataFrame(CRS[girrcol].iloc[i].values, columns = ["델타민감도"])
                        fxrate1 = CalcFXRateToKRW(FXSpot, CRS["Currency1"].iloc[i], CRS["PriceDate"].iloc[i])
                        fxrate2 = CalcFXRateToKRW(FXSpot, CRS["Currency2"].iloc[i], CRS["PriceDate"].iloc[i])
                        FXRate = np.array([fxrate1] * (len(girrcol1) + len(girrcol2)) + [fxrate2] * (len(girrcol3) + len(girrcol4)))
                        TempData["델타민감도"] = TempData["델타민감도"].values.astype(np.float64) * FXRate

                        TempData["기준일자"] = PriceDate
                        TempData["계정구분코드"] = 10
                        TempData["계정명"] = "은행"
                        TempData["부점코드"] = 12345
                        TempData["부점명"] = Depart
                        TempData["팀코드"] = 12345
                        TempData["팀명"] = "TempTeam"
                        TempData["데스크코드"] = 12345
                        TempData["데스크명"] = "TempDesk"
                        TempData["포트폴리오"] = "TempPort"
                        TempData["리스크군"] = "일반금리(GIRR)"
                        TempData["민감도유형"] = "델타"
                        TempData["포지션 ID"] = 12345
                        TempData["뮤렉스 ID"] = 12345
                        TempData["버킷"] = np.array([CRS["GirrBucket1"].iloc[i]] * (len(girrcol1) + len(girrcol2)) + [CRS["GirrBucket2"].iloc[i]] * (len(girrcol3) + len(girrcol4)))
                        TempData["리스크요소1"] = cvname
                        TempData["리스크요소2"] = girrtenor
                        TempData["리스크요소3"] = Type
                        TempData["베가민감도"] = 0
                        TempData["상향커버쳐"] = 0
                        TempData["하향커버쳐"] = 0                                  
                        TempData = TempData[(TempData["델타민감도"] >= 1e-10) | (TempData["델타민감도"] <= -1e-10)]
                        ResultAddData = pd.concat([ResultAddData, TempData],axis = 0)

        else : 
            if len(Bond) + len(IRS) + len(CRS) > 0 : 
                #AddBookedPosition = input("\nBooking된 " + str(len(Bond) + len(IRS)) + "건의 포지션을 FRTB SA 계산에 추가하겠습니까?(Y/N)\n->").lower()
                AddBookedPosition = MainViewer(Title = 'Continue', MyText = currdir + "\\Book\n에 Booking된 " + str(len(Bond) + len(IRS) + len(CRS)) + "건의 포지션을\n FRTB SA 계산에 추가하겠습니까?", MyList = ["0: 추가안함", "1: 추가함"], size = "1550x450+5+5", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name", addtreeflag=True, treedata = concatdata, width = 60)
                if AddBookedPosition == 1 :
                    Depart = MainViewer2(Title = "Department Name",MyText = "부점명을 입력하시오",size = "800x450+30+30", textfont = 14, defaultvalue = "TempDepart")#input("\n 부점명을 입력하시오. (ex : 자금운용실)\n-> ")
                    for i in range(len(Bond)) : 
                        cvname = Bond["DiscCurveName"].iloc[i].replace(".csv","")
                        girrcol = [s for s in Bond.columns if "girr1_" in s.lower()]
                        girrtenor = [float(s.replace("GIRR1_","")) for s in girrcol]
                        csrcol = [s for s in Bond.columns if "csr1_" in s.lower()]
                        csrtenor = [float(s.replace("CSR1_","")) for s in csrcol]
                        
                        #GIRR Mapping
                        TempData = pd.DataFrame(Bond[girrcol].iloc[i].values, columns = ["Delta_Sensi"])
                        fxrate = CalcFXRateToKRW(FXSpot, Bond["Currency"].iloc[i], Bond["PriceDate"].iloc[i])
                        TempData["Delta_Sensi"] = TempData["Delta_Sensi"].astype(np.float64) * fxrate * 10000
                        TempData["Depart"] = Depart
                        TempData["Risk_Class"] = "GIRR"
                        TempData["Risk_Type"] = "Delta"
                        TempData["Portfolio"] = "TempPort"
                        TempData["Bucket"] = Bond["Currency"].iloc[i]
                        TempData["RiskFactor1"] = cvname
                        TempData["RiskFactor2"] = girrtenor
                        TempData["RiskFactor3"] = "Rate"
                        TempData["Vega_Sensi"] = 0
                        TempData["CVR_Plus"] = 0
                        TempData["CVR_Minus"] = 0                        
                        TempData = TempData[TempData["Delta_Sensi"] != 0]

                        #CSR Mapping
                        TempData2 = pd.DataFrame(Bond[csrcol].iloc[i].values, columns = ["Delta_Sensi"]).fillna(0)
                        TempData2["Delta_Sensi"] = TempData2["Delta_Sensi"].astype(np.float64) * fxrate * 10000
                        TempData2["Depart"] = Depart
                        TempData2["Risk_Class"] = "CSR"
                        TempData2["Risk_Type"] = "Delta"
                        TempData2["Portfolio"] = "TempPort"
                        TempData2["Bucket"] = str(Bond["CsrBucket"].iloc[i])
                        TempData2["RiskFactor1"] = cvname
                        TempData2["RiskFactor2"] = csrtenor
                        TempData2["RiskFactor3"] = "TempIssuer" + str(Bond["CsrBucket"].iloc[i])
                        TempData2["Vega_Sensi"] = 0
                        TempData2["CVR_Plus"] = 0
                        TempData2["CVR_Minus"] = 0 
                        TempData2 = TempData2[TempData2["Delta_Sensi"] != 0]                          
                        ResultAddData = pd.concat([ResultAddData, TempData, TempData2],axis = 0)
                                             
                    for i in range(len(IRS)) : 
                        cvnamedsc1 = str(IRS["DiscCurveNameLeg1"].iloc[i]).replace(".csv","")
                        cvnameest1 = str(IRS["EstCurveNameLeg1"].iloc[i]).replace(".csv","")
                        cvnamedsc2 = str(IRS["DiscCurveNameLeg2"].iloc[i]).replace(".csv","")
                        cvnameest2 = str(IRS["EstCurveNameLeg2"].iloc[i]).replace(".csv","")                             
                        girrcol1 = [s for s in IRS.columns if "girr1_" in s.lower()]
                        girrcol2 = [s for s in IRS.columns if "girr2_" in s.lower()]
                        girrcol3 = [s for s in IRS.columns if "girr3_" in s.lower()]
                        girrcol4 = [s for s in IRS.columns if "girr4_" in s.lower()]                        
                        girrcol = girrcol1 + girrcol2 + girrcol3 + girrcol4
                        cvname = [cvnamedsc1] * len(girrcol1) + [cvnameest1] * len(girrcol2) + [cvnamedsc2] * len(girrcol3) + [cvnameest2] * len(girrcol4)
                        girrtenor1 = [float(s.replace("GIRR1_","")) for s in girrcol1]
                        girrtenor2 = [float(s.replace("GIRR2_","")) for s in girrcol2]
                        girrtenor3 = [float(s.replace("GIRR3_","")) for s in girrcol3]
                        girrtenor4 = [float(s.replace("GIRR4_","")) for s in girrcol4]
                        girrtenor = girrtenor1 + girrtenor2 + girrtenor3 + girrtenor4
                        TempData = pd.DataFrame(IRS[girrcol].iloc[i].values, columns = ["Delta_Sensi"])
                        fxrate = CalcFXRateToKRW(FXSpot, IRS["Currency"].iloc[i], IRS["PriceDate"].iloc[i])
                        TempData["Delta_Sensi"] = TempData["Delta_Sensi"].astype(np.float64) * fxrate * 10000
                        
                        TempData["Depart"] = Depart
                        TempData["Risk_Class"] = "GIRR"
                        TempData["Risk_Type"] = "Delta"
                        TempData["Portfolio"] = "TempPort"
                        TempData["Bucket"] = IRS["GirrBucket"].iloc[i]
                        TempData["RiskFactor1"] = cvname
                        TempData["RiskFactor2"] = girrtenor
                        TempData["RiskFactor3"] = "Rate"
                        TempData["Vega_Sensi"] = 0
                        TempData["CVR_Plus"] = 0
                        TempData["CVR_Minus"] = 0                        
                        TempData = TempData[(TempData["Delta_Sensi"] >= 1e-10) | (TempData["Delta_Sensi"] <= -1e-10)]
                        ResultAddData = pd.concat([ResultAddData, TempData],axis = 0)
                                             
                    for i in range(len(CRS)) : 
                        cvnamedsc1 = str(CRS["DiscCurveNameLeg1"].iloc[i]).replace(".csv","")
                        cvnameest1 = str(CRS["EstCurveNameLeg1"].iloc[i]).replace(".csv","")
                        crsdomeflag = ('FX' in cvnamedsc1.upper()) or ('BASIS' in cvnamedsc1.upper()) or ('CRS' in cvnamedsc1.upper())
                        cvnamedsc2 = str(CRS["DiscCurveNameLeg2"].iloc[i]).replace(".csv","")
                        cvnameest2 = str(CRS["EstCurveNameLeg2"].iloc[i]).replace(".csv","")                             
                        crsforeflag = ('FX' in cvnamedsc2.upper()) or ('BASIS' in cvnamedsc2.upper()) or ('CRS' in cvnamedsc2.upper())
                        girrcol1 = [s for s in CRS.columns if "girr1_" in s.lower()]
                        girrcol2 = [s for s in CRS.columns if "girr2_" in s.lower()]
                        girrcol3 = [s for s in CRS.columns if "girr3_" in s.lower()]
                        girrcol4 = [s for s in CRS.columns if "girr4_" in s.lower()]                        
                        girrcol = girrcol1 + girrcol2 + girrcol3 + girrcol4
                        TypeD = ['XCCY' if crsdomeflag else 'Rate'] * (len(girrcol1) + len(girrcol2))
                        TypeF = ['XCCY' if crsforeflag else 'Rate'] * (len(girrcol3) + len(girrcol4))
                        Type = TypeD + TypeF
                        cvname = [cvnamedsc1] * len(girrcol1) + [cvnameest1] * len(girrcol2) + [cvnamedsc2] * len(girrcol3) + [cvnameest2] * len(girrcol4)
                        girrtenor1 = [float(s.replace("GIRR1_","")) for s in girrcol1]
                        girrtenor2 = [float(s.replace("GIRR2_","")) for s in girrcol2]
                        girrtenor3 = [float(s.replace("GIRR3_","")) for s in girrcol3]
                        girrtenor4 = [float(s.replace("GIRR4_","")) for s in girrcol4]
                        girrtenor = girrtenor1 + girrtenor2 + girrtenor3 + girrtenor4
                        TempData = pd.DataFrame(CRS[girrcol].iloc[i].values, columns = ["Delta_Sensi"])
                        fxrate1 = CalcFXRateToKRW(FXSpot, CRS["Currency1"].iloc[i], CRS["PriceDate"].iloc[i])
                        fxrate2 = CalcFXRateToKRW(FXSpot, CRS["Currency2"].iloc[i], CRS["PriceDate"].iloc[i])
                        FXRate = np.array([fxrate1] * (len(girrcol1) + len(girrcol2)) + [fxrate2] * (len(girrcol3) + len(girrcol4)))
                        TempData["Delta_Sensi"] = TempData["Delta_Sensi"].values.astype(np.float64) * FXRate * 10000

                        TempData["Depart"] = Depart
                        TempData["Risk_Class"] = "GIRR"
                        TempData["Risk_Type"] = "Delta"
                        TempData["Portfolio"] = "TempPort"
                        TempData["Bucket"] = np.array([CRS["GirrBucket1"].iloc[i]] * (len(girrcol1) + len(girrcol2)) + [CRS["GirrBucket2"].iloc[i]] * (len(girrcol3) + len(girrcol4)))
                        TempData["RiskFactor1"] = cvname
                        TempData["RiskFactor2"] = girrtenor
                        TempData["RiskFactor3"] = Type
                        TempData["Vega_Sensi"] = 0
                        TempData["CVR_Plus"] = 0
                        TempData["CVR_Minus"] = 0                        
                        TempData = TempData[(TempData["Delta_Sensi"] >= 1e-10) | (TempData["Delta_Sensi"] <= -1e-10)]
                        ResultAddData = pd.concat([ResultAddData, TempData],axis = 0)

    except FileNotFoundError : 
        None
    return ResultAddData

def _flatten_columns(cols):
    # MultiIndex면 마지막 레벨(실제 컬럼명)을 사용
    if isinstance(cols, pd.MultiIndex):
        return [str(c[-1]).strip() for c in cols]
    return [str(c).strip() for c in cols]

def fetch_fx_daily(marketindex_cd: str, max_pages: int = 300, sleep: float = 0.2) -> pd.DataFrame:
    rows = []

    with requests.Session() as s:
        s.headers.update(HEADERS)

        for page in range(1, max_pages + 1):
            params = {"marketindexCd": marketindex_cd, "page": page}
            r = s.get(BASE_URL, params=params, timeout=10)
            r.raise_for_status()

            tables = pd.read_html(r.text)
            if not tables:
                break

            df = tables[0].copy()
            df.columns = _flatten_columns(df.columns)

            # 한글 컬럼명이 있으면 우선 사용, 없으면 첫 2개 컬럼 사용
            date_col = "날짜" if "날짜" in df.columns else df.columns[0]
            rate_col = "매매기준율" if "매매기준율" in df.columns else df.columns[1]

            df = df[[date_col, rate_col]].dropna(subset=[date_col])
            if df.empty:
                break

            df = df.rename(columns={date_col: "date", rate_col: "rate"})
            rows.append(df)


    if not rows:
        return pd.DataFrame(columns=["date", "rate", "marketindex_cd"])

    out = pd.concat(rows, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["rate"] = out["rate"].astype(str).str.replace(",", "", regex=False).astype(float)
    out["marketindex_cd"] = marketindex_cd

    out = out.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return out

def is_internet_connected(
    test_url: str = "https://www.google.com",
    timeout: float = 3.0
) -> bool:
    try:
        requests.get(test_url, timeout=timeout)
        return True
    except requests.RequestException:
        return False

def fetch_fx_daily_safe(
    marketindex_cd: str,
    max_pages: int = 300,
    sleep: float = 0.2
):
    if not is_internet_connected():
        print("인터넷이 연결되어 있지 않습니다.")
        return None

    print("인터넷 연결 확인됨 → 환율 데이터 수집 시작(" + marketindex_cd + ")")
    return fetch_fx_daily(
        marketindex_cd=marketindex_cd,
        max_pages=max_pages,
        sleep=sleep
    )    

def UpdateFXSpotRateNaverFinance(currdir : str) : 
    UpdateList = ["USDKRW","EURKRW","CNYKRW","JPYKRW","HKDKRW","GBPKRW","CADKRW","BRLKRW","THBKRW"]
    SpotData = PreprocessingFXSpotData(currdir + "\\MarketData\\spot\\FXSpot.csv")        
    tempf = np.vectorize(lambda x : str(x)[:-4] + '-' + str(x)[-4:-2] + '-' + str(x)[-2:])
    LastDate = int(SpotData.index[-1])
    LastDate_DT = pd.to_datetime(str(LastDate)[:-4] + '-' + str(LastDate)[-4:-2] + '-' + str(LastDate)[-2:])
    TodayDate = int(f"{pd.Timestamp.now().date():%Y%m%d}")
    NextBDate = NextNthBusinessDate(LastDate, 1, KoreaHolidaysFromStartToEnd(LastDate//10000,LastDate//10000 + 1))
    deltatime = DayCountAtoB(LastDate, TodayDate)
    if is_internet_connected() : 
        if NextBDate <= TodayDate : 
            data_fx = pd.DataFrame([])
            for i in UpdateList : 
                df_fx = fetch_fx_daily_safe("FX_" + i, max_pages = 200 if deltatime > 500 else 60).set_index('date')[['rate']]
                df_fx = df_fx.rename(columns = {"rate" : i[:3] + '/' + i[-3:]})
                if df_fx.columns[0] == 'JPY/KRW' : 
                    df_fx /= 100
                data_fx = pd.concat([data_fx, df_fx],axis = 1)
            data_fx = data_fx.astype(np.float64).fillna(method = 'ffill')
            
            mycol = data_fx.columns.difference(["USD/KRW"])
            USDFXRate = data_fx[mycol]/data_fx[["USD/KRW"]].values
            USDFXRate.columns = np.vectorize(lambda x : x.replace('/KRW','/USD'))(mycol)
            FXTimeSeries = pd.concat([data_fx, USDFXRate],axis = 1)
            NewData = FXTimeSeries.loc[FXTimeSeries.index.difference([LastDate_DT])][LastDate_DT:]
            NewData.index.name = SpotData.index.name
            SpotData.index = pd.to_datetime(tempf(SpotData.index))
            UpdatedData = pd.concat([SpotData, NewData],axis = 0).fillna(method = 'ffill')
            UpdatedData.index.name = "Date"
            UpdatedData.to_csv(currdir + "\\MarketData\\spot\\FXSpot.csv", encoding = "cp949")
            print("환율 업데이트 완료")
        else : 
            print("현재 환율데이터는 최근일자입니다.")

def fetch_krw_irs_kmb_simple() -> pd.DataFrame:
    """
    KMB(한국자금중개) 파생금리 페이지에서
    KRW IRS(1Y~10Y) '현재 노출된 테이블'만 수집
    - re 미사용
    - time.sleep 미사용
    """

    r = requests.get(URLIRS, headers=HEADERSIRS, timeout=10)
    r.raise_for_status()

    tables = pd.read_html(r.text)

    target = None
    for t in tables:
        cols = [str(c).strip() for c in t.columns]
        if "전송일" in cols and "1Y" in cols and "10Y" in cols:
            target = t.copy()
            break

    if target is None:
        raise RuntimeError("KRW IRS 테이블을 찾지 못했습니다 (페이지 구조 변경 가능)")

    # 컬럼 정리
    target = target.rename(columns={target.columns[0]: "date"})
    target["date"] = pd.to_datetime(target["date"], errors="coerce")

    for c in target.columns:
        if c != "date":
            target[c] = (
                target[c]
                .astype(str)
                .str.replace(",", "", regex=False)
                .astype(float)
            )

    return (
        target
        .dropna(subset=["date"])
        .sort_values("date")
        .reset_index(drop=True)
    ).set_index("date")

def fetch_naver_interest_daily_quote(marketindex_cd: str, max_pages: int = 50) -> pd.DataFrame:
    """
    네이버금융 금리 '일별시세' 크롤링
    예) IRR_CALL(콜금리), IRR_CD91(CD 91일)
    """
    rows = []

    with requests.Session() as s:
        s.headers.update(HEADERSCD)

        for page in range(1, max_pages + 1):
            r = s.get(BASECD, params={"marketindexCd": marketindex_cd, "page": page}, timeout=10)
            r.raise_for_status()

            # 네이버 금융은 EUC-KR인 경우가 있어 안전하게 디코딩
            if r.encoding is None or r.encoding.lower() == "iso-8859-1":
                r.encoding = "euc-kr"

            tables = pd.read_html(r.text)
            if not tables:
                break

            df = tables[0].copy()
            cols = [str(c).strip() for c in df.columns]
            df.columns = cols

            # 보통: 날짜 / 종가 / 전일대비
            if "날짜" not in df.columns:
                break

            # '종가'가 없으면 첫 숫자 컬럼을 rate로 사용
            rate_col = "종가" if "종가" in df.columns else df.columns[1]

            df = df.dropna(subset=["날짜"])
            if df.empty:
                break

            df = df[["날짜", rate_col]].rename(columns={"날짜": "date", rate_col: "rate"})
            rows.append(df)

    if not rows:
        return pd.DataFrame(columns=["date", "rate", "marketindex_cd"])

    out = pd.concat(rows, ignore_index=True)
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["rate"] = out["rate"].astype(str).str.replace(",", "", regex=False).astype(float)
    out["marketindex_cd"] = marketindex_cd
    return out.dropna(subset=["date"]).sort_values("date").set_index('date').rename(columns = {'rate': marketindex_cd})[[marketindex_cd]]

def Update_KRWIRSData(currdir : str) : 
    DataLastDate = int(sorted(os.listdir(currdir + '\\MarketData\\inputdata'))[-1])
    UpDatedDateList = []
    UpDatedZeroList = []
    if is_internet_connected() : 
        df_call = fetch_naver_interest_daily_quote("IRR_CALL")   # 콜금리
        df_cd91 = fetch_naver_interest_daily_quote("IRR_CD91")   # CD(91일)
        if df_call.index[-1] < df_cd91.index[-1] : 
            df_call.loc[df_cd91.index[-1]] = df_call["IRR_CALL"].iloc[-1]
        df_krw_irs = fetch_krw_irs_kmb_simple()
        myindex = df_krw_irs.index.intersection(df_call.index).intersection(df_cd91.index)
        IRSData = pd.concat([df_call.loc[myindex], df_cd91.loc[myindex], df_krw_irs.loc[myindex]],axis = 1)

        MinUpdateDate = int(IRSData.index[-1].strftime("%Y%m%d"))
        TodayDate = int(f"{pd.Timestamp.now().date():%Y%m%d}")
        if DataLastDate < MinUpdateDate and DayCountAtoB(DataLastDate, TodayDate) >= 1 :     
            tempf = np.vectorize(lambda x : str(x)[:-4] + '-' + str(x)[-4:-2] + '-' + str(x)[-2:])
            for i in range(len(IRSData.index)) :
                Today = IRSData.index[i].strftime("%Y%m%d")
                Todayint = int(Today)
                Holidays = KoreaHolidaysFromStartToEnd(int(Today[:-4]), int(Today[:-4]) + 30)
                CallDate = NextNthBusinessDate(Todayint, 1,Holidays)
                Rates = IRSData.iloc[i]
                Types = ['dg']
                StartDate = [Todayint] + [CallDate] * (len(Rates)-1)
                Maturitys = [CallDate]
                MarketQuote = list(Rates.values)
                if Today not in os.listdir(currdir + '\\MarketData\\inputdata') : 
                    for n in Rates.index[1:] : 
                        if 'cd' in n.lower() : 
                            nm = 3
                        elif 'm' in n.lower() : 
                            nm = int(n.lower().split('m')[0])
                        else : 
                            nm = int(n.lower().split('y')[0]) * 12
                        ty = 'dg' if nm <= 9 else 'sw'
                        TempDate = ParseBusinessDateIfHoliday(EDate_YYYYMMDD(CallDate, nm),Holidays)
                        Maturitys.append(TempDate)
                        Types.append(ty)
                                        
                    df = pd.DataFrame([Types, tempf(StartDate), tempf(Maturitys), MarketQuote], index = ['Type','StartDate','Maturity','MarketQuote']).T
                    
                    os.makedirs(currdir + '\\MarketData\\inputdata' + '\\' + Today , exist_ok=True) 
                    os.makedirs(currdir + '\\MarketData\\inputdata' + '\\' + Today + "\\KRW", exist_ok=True) 
                    df.to_csv(currdir + '\\MarketData\\inputdata' + '\\' + Today + "\\KRW"+ '\\KRW IRS Quote.csv', index = False, encoding = "cp949")
                    print("IRS" + Today + "저장완료")
                    UpDatedDateList.append(Today)
                    ZeroTerm = []
                    ZeroRate = []
                    for n in range(len(Types)) : 
                        if (Types[n].lower() in ['dp','dg','deposit']) : 
                            r = Calc_ZeroRate_FromDiscFactor(Todayint, StartDate[n], Maturitys[n], MarketQuote[n]/100, 0, ZeroTerm, ZeroRate)
                            ZeroTerm.append(DayCountAtoB(Today, Maturitys[n])/365)
                            ZeroRate.append(r)
                        else :
                            T = DayCountAtoB(Today, Maturitys[n])/365
                            ZeroArray = np.r_[np.array(ZeroRate), 0.0]
                            MaxRate = max(0.3, np.array(ZeroRate).mean() * 4)
                            MinRate = min(-0.04, np.array(ZeroRate).min() - 0.03)
                            TargetRate = MaxRate
                            ZeroTerm.append(T)
                            for j in range(500) : 
                                ZeroArray[-1] = TargetRate
                                Err = Calc_IRS(100, 0.0, StartDate[n], Todayint, Maturitys[n], MarketQuote[n]/100, ZeroTerm, ZeroArray, 4, 0, True, 0, [], [], [], [])
                                
                                if abs(Err) < 0.000001 : 
                                    break
                                elif Err < 0 : 
                                    MaxRate = TargetRate
                                    TargetRate = (MaxRate + MinRate)/2
                                else : 
                                    MinRate = TargetRate
                                    TargetRate = (MaxRate + MinRate)/2

                            if j == 499 : 
                                RateRange = np.linspace(0.001, 0.101, 2001)
                                ZeroArrayCopy = ZeroArray.copy()
                                Err = 100
                                for j in range(len(RateRange)) : 
                                    TempRate = RateRange[j]
                                    ZeroArrayCopy[-1] = TempRate
                                    TempErr = Calc_IRS(100, 0.0, StartDate[n], Todayint, Maturitys[n], MarketQuote[n]/100, ZeroTerm, ZeroArray, 4, 0, True, 0, [], [], [], [] )

                                    if abs(TempErr) < Err : 
                                        Err = TempErr

                                    if Err < 0.0001 : 
                                        TargetRate = TempRate
                                        break

                                #if j == len(RateRange) - 1 : 
                                #    raise ValueError("Error")
                            ZeroRate.append(TargetRate)
                    ResultZero = pd.DataFrame([ZeroTerm, ZeroRate],index = ['Term','Rate']).T
                    ResultZero["Rate"] = ResultZero["Rate"] * 100
                    ResultZero["PriceDate"] = Todayint
                    ResultZero["NBD"] = 0
                    ResultZero["StartDate"] = StartDate
                    ResultZero["EndDate"] = Maturitys
                    ResultZero["PayDate"] = Maturitys
                    UpDatedZeroList.append(ResultZero)
                
            print("KRW IRS Input Data 업데이트 완료")
        else : 
            print("KRW IRS 데이터 이미 최근일자입니다.")
    else : 
        print("인터넷이 없습니다.")
    return DataLastDate, UpDatedDateList, UpDatedZeroList

def CalcMaturityStringFormat(Day1, Day2, HolidayData, curr) : 
    D1 = int(pd.to_datetime(Day1).date().strftime("%Y%m%d"))
    D2 = int(pd.to_datetime(Day2).date().strftime("%Y%m%d"))
    TempDate = [Day1]
    DC = DayCountAtoB(D1, D2)
    if DC < 30 : 
        NBD =  NBusinessCountFromEndToPay(D1, D2, HolidayData[curr].values,0 ,TempDate)
        if DC == 0 : 
            return 'Today'
        elif NBD == 1 or DC == 1: 
            return 'ON'
        elif NBD == 2 : 
            return 'TN'
        elif DC < 14 : 
            return '1W'
        elif DC < 21 : 
            return '2W'
        elif DC < 28 : 
            return '3W'
        else : 
            return '1M' 
    else : 
        MC = MonthCountAtoB(D1, D2)
        if int(MC) < 12 : 
            return str(MC) + 'M'
        else : 
            return str(int(MC)/12) + 'Y'

def CalcMaturityFromStringToYYYYMMDD(PriceDate, Tenor, HolidayData) : 
    Tenorlower = str(Tenor).lower()
    if 'today' in Tenorlower : 
        return PriceDate
    elif 'o' in Tenorlower and 'n' in Tenorlower : 
        return NextNthBusinessDate(PriceDate, 1, HolidayData)
    elif 't' in Tenorlower and 'n' in Tenorlower : 
        return NextNthBusinessDate(PriceDate, 2, HolidayData)
    elif '1' in Tenorlower and 'w' in Tenorlower : 
        return ParseBusinessDateIfHoliday(DayPlus(PriceDate, 7),HolidayData)
    elif '2' in Tenorlower and 'w' in Tenorlower : 
        return ParseBusinessDateIfHoliday(DayPlus(PriceDate, 14),HolidayData)
    elif '3' in Tenorlower and 'w' in Tenorlower : 
        return ParseBusinessDateIfHoliday(DayPlus(PriceDate, 21),HolidayData)
    elif 'm' in Tenorlower : 
        nm = int(float(Tenorlower.split('m')[0]))
        return ParseBusinessDateIfHoliday(EDate_YYYYMMDD(PriceDate, nm),HolidayData)
    elif 'y' in Tenorlower : 
        nm = int(float(Tenorlower.split('y')[0])) * 12
        return ParseBusinessDateIfHoliday(EDate_YYYYMMDD(PriceDate, nm),HolidayData)
    else : 
        return PriceDate

def CopyAllPreviousMarketData(currdir, inputdir, HolidayData) : 
    tempf = np.vectorize(lambda x : pd.to_datetime(str(x)[:-4] + '-' + str(x)[-4:-2] + '-' + str(x)[-2:]))
    CapFloorSwaptionNames = []
    CapFloorSwaptiondfs = []
    UpDateFileTargets = ["CRS","IRS","AAA QUOTE","AA QUOTE","A QUOTE","BBB QUOTE","BB QUOTE","B QUOTE","CCC QUOTE","CC QUOTE","C Quote"]
    CopyFileNameList = []
    CopyFiles = []
    TargetFiles = []
    EQVolFileNameList = []
    EQVoldfs = []
    for cur in os.listdir(inputdir) : 
        FileNameList = []
        FileDfList = []
        for csvname in os.listdir(inputdir + '\\' + cur) :
            if 'cap' in csvname.lower() or 'floor' in csvname.lower() or 'ption' in csvname.lower(): 
                CapFloorSwaptiondfs.append(ReadCSV(inputdir + '\\' + cur + '\\' + csvname))
                CapFloorSwaptionNames.append(cur + '\\' + csvname)
            
            if 'eq' in csvname.lower() and 'vol' in csvname.lower() : 
                EQVoldfs.append(ReadCSV(inputdir + '\\' + cur + '\\' + csvname))
                EQVolFileNameList.append(cur + '\\' + csvname)

            for i in UpDateFileTargets :
                if i in csvname.upper() : 
                    FileNameList.append(cur + '\\' + csvname)
                    FileDfList.append(ReadCSV(inputdir + '\\' + cur + '\\' + csvname).dropna(how = 'all'))
                    break
        CopyFileNameList += FileNameList
        CopyFiles += FileDfList

    for i in range(len(CopyFileNameList)) : 
        curr = CopyFileNameList[i].split("\\")[0]
        StartDates = CopyFiles[i]['StartDate']
        Maturitys = CopyFiles[i]['Maturity']
        Types = CopyFiles[i]['Type']
        MarketQuotes = CopyFiles[i]['MarketQuote']
        StartDateTenor = [CalcMaturityStringFormat(StartDates.values[0],y,HolidayData,curr) for y in StartDates.values]
        MaturitysTenor = [CalcMaturityStringFormat(x,y,HolidayData,curr) for x, y in zip(StartDates,Maturitys)]        
        TargetFile = pd.DataFrame([list(Types), StartDateTenor, MaturitysTenor, list(MarketQuotes)], index = ["Type","StartDateTenor","MaturityTenor","MarketQuote"]).T
        TargetFiles.append(TargetFile)
        
    if len(UpDatedDate) > 0 :
        for d in UpDatedDate : 
            direc = currdir + '\\MarketData\\inputdata\\' + d
            for cur in os.listdir(inputdir) : 
                if cur not in os.listdir(direc) : 
                    os.makedirs(direc + '\\' + cur, exist_ok=True) 

            for n, name in enumerate(CapFloorSwaptionNames) : 
                if name.split("\\")[-1] not in os.listdir(direc + '\\' + name.split("\\")[0]) : 
                    CapFloorSwaptiondfs[n].to_csv(direc + '\\' + name, index = False, encoding = "cp949")
            
            TodayInt = int(d) 
            for i in range(len(CopyFileNameList)) : 
                curr = CopyFileNameList[i].split("\\")[0]
                TargetFile = TargetFiles[i]
                StartDate = [CalcMaturityFromStringToYYYYMMDD(TodayInt, j, HolidayData[curr]) for j in TargetFile["StartDateTenor"].values]
                Maturity = [CalcMaturityFromStringToYYYYMMDD(k, j, HolidayData[curr]) for k, j in zip(StartDate, TargetFile["MaturityTenor"].values)]
                TargetFile['StartDate'] = tempf(StartDate)
                TargetFile['Maturity'] = tempf(Maturity)
                if 'usd' == curr.lower() : 
                    TargetFile['Maturity'] = tempf([NextNthBusinessDate(Maturity[k], 2, HolidayData[curr.upper()]) if TargetFile['Type'].iloc[k].lower() == 'sw' else Maturity[k] for k in range(len(Maturity))])
                filename = CopyFileNameList[i].split("\\")[-1]
                if filename not in os.listdir(direc + '\\'  + CopyFileNameList[i].split("\\")[0]) :
                    TargetFile[["Type","StartDate","Maturity","MarketQuote"]].to_csv(direc + '\\' +CopyFileNameList[i], index = False, encoding = "cp949")

            for i in range(len(EQVolFileNameList)) : 
                EQVoldfs[i].to_csv(direc + '\\' + EQVolFileNameList[i], index = False, encoding = "cp949")

        print("미입수 데이터 전일자 Copy완료")
    else : 
        print("데이터 이미 최신일자")

def UpDateIRImpliedVolatilityFromQuoteToVol(currdir, UpDatedDate) : 
    lstoutput = os.listdir(currdir + '\\MarketData\\outputdata')
    for i, d in enumerate(UpDatedDate) : 
        for c in os.listdir(currdir + '\\MarketData\\inputdata' + '\\' + d) : 
            filedir = currdir + '\\MarketData\\inputdata' + '\\' + d + '\\' + c
            filelist = os.listdir(filedir) 
            for f in filelist : 
                if 'cap' in f.lower() or 'floor' in f.lower(): 
                    capfloorflag, NA = 'cap' not in f.lower(), 100.0

                    df = ReadCSV(filedir + '\\' + f)
                    Tenor, QuotePercent = list(df['Tenor']), list(df["QuotePercent"])
                    zc = pd.DataFrame([[1.0,3.0]], columns = ["Term","Rate"])
                    for k in os.listdir(currdir + '\\MarketData\\outputdata\\' + d + '\\' + c) : 
                        if 'zero' in k.lower() :
                            zc = ReadCSV(currdir + '\\MarketData\\outputdata\\' + d + '\\' + c + '\\' + k)
                            break 
                    ZeroTerm = list(zc["Term"])
                    ZeroRate = list(zc["Rate"])
                    PriceDate = int(d)
                    Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
                    if 'KRW' in c.upper() : 
                        Holidays = KoreaHolidaysFromStartToEnd(PriceDate//10000, PriceDate//10000 + 30)
                        NCPNOneYear, DayCountFlag = 4, 0
                    elif 'USD' in c.upper() : 
                        Holidays = USHolidaysFromStartToEnd(PriceDate//10000, PriceDate//10000 + 30)
                        NCPNOneYear, DayCountFlag = 1, 1
                    else : 
                        Holidays = []
                        NCPNOneYear, DayCountFlag = 4, 0
                    StartDate = NextNthBusinessDate(PriceDate, 1, Holidays)
                    Maturity = [EDate_YYYYMMDD(StartDate, int(i)) for i in Tenor]
                    ResultData, ResultCapFloorImvol, FwdSwpRate, Calibration = CapFloorToImpliedVol(ZeroTerm, ZeroRate, PriceDate, StartDate, Maturity, QuotePercent, 0, NCPNOneYear, capfloorflag, NA, DayCountFlag, 1, Holidays)
                    ResultData["FwdSwpRate"] = FwdSwpRate
                    ResultData.index.name = "Tenor"
                    if d not in lstoutput :  
                        os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d , exist_ok=True) 
                        os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c, exist_ok=True) 
                    else : 
                        curlist = os.listdir(currdir + '\\MarketData\\outputdata' + '\\' + d)
                        if c not in curlist : 
                            os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c, exist_ok=True) 
                    if f not in os.listdir(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c) : 
                        ResultData.reset_index().to_csv(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c + '\\' + f.replace("Quote","Vol"), index = False, encoding = "cp949")
                        print("Cap/Floor " + d + '일자 Implied Vol 생성완료')
                if 'ption' in f.lower() and 'eq' not in f.lower(): 
                    df = ReadCSV(filedir + '\\' + f)
                    df = df.set_index(df.columns[0])
                    ResultValues = np.zeros(shape = df.shape)
                    ResultValues2 = np.zeros(shape = df.shape)
                    zc = pd.DataFrame([[1.0,3.0]], columns = ["Term","Rate"])
                    for k in os.listdir(currdir + '\\MarketData\\outputdata\\' + d + '\\' + c) : 
                        if 'zero' in k.lower() :
                            zc = ReadCSV(currdir + '\\MarketData\\outputdata\\' + d + '\\' + c + '\\' + k)
                            break 
                    ZeroTerm = list(zc["Term"])
                    ZeroRate = list(zc["Rate"])
                    PriceDate = int(d)
                    Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)      
                    if 'KRW' in c.upper() : 
                        Holidays = KoreaHolidaysFromStartToEnd(PriceDate//10000, PriceDate//10000 + 30)
                        NCPNOneYear, DayCountFlag = 4, 0
                    elif 'USD' in c.upper() : 
                        Holidays = USHolidaysFromStartToEnd(PriceDate//10000, PriceDate//10000 + 30)
                        NCPNOneYear, DayCountFlag = 1, 1
                    else : 
                        Holidays = []
                        NCPNOneYear, DayCountFlag = 4, 0                                  
                    for i in range((df.shape[0])) : 
                        for j in range((df.shape[1])) : 
                            TargetPrice = df.values[i][j]
                            StartDate = EDate_YYYYMMDD(PriceDate, int(df.columns[j])) 
                            EndDate = EDate_YYYYMMDD(StartDate, int(df.index[i])) 
                            v = FindSwaptionImpliedVolatility(PriceDate, StartDate, EndDate, NCPNOneYear, ZeroTerm, ZeroRate, TargetPrice, DayCountFlag, VolFlag = 1, Nominal = 1, HolidayFlag = 'kr' if 'KRW' == c else '', SelfHolidays= Holidays, FixedPayer0Receiver1=0)
                            ResultValues[i][j] = v["ImpliedVol"]
                            ResultValues2[i][j] = v["ForwardSwapRate"]                    
                    ResultDF = pd.DataFrame(ResultValues, index = df.index, columns = df.columns)
                    if d not in lstoutput :  
                        os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d , exist_ok=True) 
                        os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c, exist_ok=True) 
                    else : 
                        curlist = os.listdir(currdir + '\\MarketData\\outputdata' + '\\' + d)
                        if c not in curlist : 
                            os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c, exist_ok=True) 
                    if f not in os.listdir(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c) : 
                        ResultDF.reset_index().to_csv(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c + '\\' + f.replace("Quote","Vol"), index = False, encoding = "cp949")
                        print("Swaption " + d + '일자 Implied Vol 생성완료')

def UpDateCorpBondCurveFromInputData(currdir, UpDatedDate, HolidayData) : 
    lstoutput = os.listdir(currdir + '\\MarketData\\outputdata')
    UpDateFileTargets = ["AAA QUOTE","AA QUOTE","A QUOTE","BBB QUOTE","BB QUOTE","B QUOTE","CCC QUOTE","CC QUOTE","C QUOTE", "IRS QUOTE"]
    BreakFlag = 0
    for i, d in enumerate(UpDatedDate) : 
        for c in os.listdir(currdir + '\\MarketData\\inputdata' + '\\' + d) : 
            filedir = currdir + '\\MarketData\\inputdata' + '\\' + d + '\\' + c
            filelist = os.listdir(filedir) 
            for f in filelist : 
                for taragetf in UpDateFileTargets : 
                    if taragetf in f.upper() :
                        outputlist = os.listdir(currdir + '\\MarketData\\outputdata')
                        if d in outputlist : 
                            outputlist2 = os.listdir(currdir + '\\MarketData\\outputdata\\' +d)
                            if c not in outputlist2 :
                                os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c, exist_ok=True) 
                        else : 
                            os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d , exist_ok=True) 
                            os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c, exist_ok=True) 
                        if f.replace("Quote", "ZeroCurve") not in os.listdir(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c) : 
                            df = ReadCSV(filedir + '\\' + f)
                            Today = d
                            Todayint = int(Today)
                            Holidays = list(HolidayData[c].unique())
                            Rates = df["MarketQuote"].values
                            Types = df["Type"]
                            StartDatesdt = pd.to_datetime(df["StartDate"].values)
                            Maturitysdt = pd.to_datetime(df["Maturity"].values)
                            StartDates = list(StartDatesdt.strftime("%Y%m%d").astype(np.int64))
                            Maturitys = list(Maturitysdt.strftime("%Y%m%d").astype(np.int64))
                            MarketQuote = list(Rates)
                            EndDates = []
                            ZeroTerm = []
                            ZeroRate = []
                            NBDs = []
                            TempDate = [Todayint]
                            for n in range(len(Types)) : 
                                if (Types[n].lower() in ['dp','dg','deposit']) : 
                                    r = Calc_ZeroRate_FromDiscFactor(Todayint, StartDates[n], Maturitys[n], MarketQuote[n]/100, 0, ZeroTerm, ZeroRate)
                                    ZeroTerm.append(DayCountAtoB(Today, Maturitys[n])/365)
                                    ZeroRate.append(r)
                                    EndDates.append(Maturitys[n])
                                    NBDs.append(0)
                                else :
                                    T = DayCountAtoB(Today, Maturitys[n])/365
                                    ZeroArray = np.r_[np.array(ZeroRate), 0.0]
                                    MaxRate = max(0.3, np.array(ZeroRate).mean() * 4)
                                    MinRate = min(-0.04, np.array(ZeroRate).min() - 0.03)
                                    TargetRate = MaxRate
                                    if DayCountAtoB(StartDates[n], Maturitys[n]) < 14 :                                 
                                        NBD = NBusinessCountFromEndToPay(DayPlus(StartDates[n], 7), Maturitys[n], Holidays, True, TempDate)
                                        TempDate[0] = Maturitys[n]
                                    elif DayCountAtoB(StartDates[n], Maturitys[n]) < 21 : 
                                        NBD = NBusinessCountFromEndToPay(DayPlus(StartDates[n], 14), Maturitys[n], Holidays, True, TempDate)
                                        TempDate[0] = Maturitys[n]
                                    elif DayCountAtoB(StartDates[n], Maturitys[n]) < 28 : 
                                        NBD = NBusinessCountFromEndToPay(DayPlus(StartDates[n], 21), Maturitys[n], Holidays, True, TempDate)
                                        TempDate[0] = Maturitys[n]
                                    else : 
                                        NBD = NBusinessCountFromEndToPay(StartDates[n], Maturitys[n], Holidays, True, TempDate)
                                        NBD = NBDs[n-1] if Types[n-1].lower() not in ['dp','dg','deposit'] else NBD
                                    NBDs.append(NBD)
                                    EndDates.append(TempDate[0])
                                    ZeroTerm.append(T)
                                    for j in range(500) : 
                                        ZeroArray[-1] = TargetRate
                                        Err = Calc_IRS(100, 0.0, StartDates[n], Todayint, Maturitys[n], MarketQuote[n]/100, ZeroTerm, ZeroArray, 4 if c not in ['USD'] else 1, 0 if c not in ['USD'] else 1, False, NBD, [], [], [], Holidays)
                                        
                                        if abs(Err) < 0.000001 : 
                                            break
                                        elif Err < 0 : 
                                            MaxRate = TargetRate
                                            TargetRate = (MaxRate + MinRate)/2
                                        else : 
                                            MinRate = TargetRate
                                            TargetRate = (MaxRate + MinRate)/2

                                    if j == 499 : 
                                        RateRange = np.linspace(0.001, 0.101, 2001)
                                        ZeroArrayCopy = ZeroArray.copy()
                                        Err = 100
                                        for j in range(len(RateRange)) : 
                                            TempRate = RateRange[j]
                                            ZeroArrayCopy[-1] = TempRate
                                            TempErr = Calc_IRS(100, 0.0, StartDates[n], Todayint, Maturitys[n], MarketQuote[n]/100, ZeroTerm, ZeroArray, 4 if c not in ['USD'] else 1, 0 if c not in ['USD'] else 1, False, NBD, [], [], [], Holidays)

                                            if abs(TempErr) < Err : 
                                                Err = TempErr

                                            if Err < 0.0001 : 
                                                TargetRate = TempRate
                                                break

                                        #if j == len(RateRange) - 1 : 
                                        #    raise ValueError("Error")
                                    ZeroRate.append(TargetRate)
                            ResultZero = pd.DataFrame([ZeroTerm, ZeroRate],index = ['Term','Rate']).T
                            ResultZero["Rate"] = ResultZero["Rate"] * 100
                            ResultZero["PriceDate"] = Todayint
                            ResultZero["NBD"] = NBDs
                            ResultZero["StartDate"] = StartDates
                            ResultZero["EndDate"] = EndDates
                            ResultZero["PayDate"] = Maturitys                            
                            ResultZero.to_csv(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\" + c + '\\' + f.replace("Quote", "ZeroCurve"), index = False, encoding = 'cp949')
                            print(d + '일자 ' + f.replace("Quote", "ZeroCurve") + '저장')
                        else : 
                            print(d + '일자 ' + f.replace("Quote", "ZeroCurve") + '이미있음')
                        break

def EQOptPriceToVolatility(PriceDate, currdir, currency = 'KRW') : 
    PriceDateInt = int(PriceDate)
    filelist = os.listdir(currdir + '\\MarketData\\inputdata\\' + str(PriceDate) + '\\' + currency)
    OptionPriceDirectory = ''
    for names in filelist : 
        if "EQ" in names.upper() and "OPT" in names.upper() : 
            OptionPriceDirectory += currdir + '\\MarketData\\inputdata\\' + str(PriceDate) + '\\' + currency + '\\' + names
            break

    zerodir = ''
    for names in os.listdir(currdir + '\\MarketData\\outputdata\\' + str(PriceDate) + '\\' + currency) : 
        if 'IRS' in names.upper() and 'ZERO' in names.upper() : 
            zerodir += names
            break

    if len(OptionPriceDirectory) > 0 and len(zerodir) > 0 :     
        df = ReadCSV(OptionPriceDirectory)
        rf = ReadCSV(currdir + '\\MarketData\\outputdata\\' + str(PriceDate) + '\\'+ currency+'\\' + zerodir)
        PriceData = df.set_index(df.columns[0])
        ForwardFlag = True
        TermDisc = list(rf.Term)
        RateDisc = list(rf.Rate)
        DivTerm = [1]
        DivRate = [0]    
        volvalues = np.zeros((PriceData.shape))
        for i in range(len(PriceData.columns)) : 
            for j in range(len(PriceData.index)) :  
                TargetPrice = PriceData.values[j][i]
                NM = int(float(PriceData.columns[i]) * 12 + 0.001)
                MaturityDate = EDate_YYYYMMDD(PriceDateInt, NM)
                MoneynessPercent = float(PriceData.index[j])
                S0 = 1/MoneynessPercent # if 0.5 is Exercise Price S is 1.0
                X = 1      
                if MoneynessPercent < 1.0 : 
                    TypeFlag = 'c'
                    v = BS_Price_To_ImpliedVolatility(PriceDateInt, MaturityDate, MoneynessPercent, TermDisc, RateDisc, DivTerm, DivRate, TargetPrice, minvol = 0.00001, maxvol = 2.5, TypeFlag = TypeFlag, ForwardFlag = ForwardFlag)
                elif MoneynessPercent > 1.0 : 
                    TypeFlag = 'p'  
                    v = BS_Price_To_ImpliedVolatility(PriceDateInt, MaturityDate, MoneynessPercent, TermDisc, RateDisc, DivTerm, DivRate, TargetPrice, minvol = 0.00001, maxvol = 2.5, TypeFlag = TypeFlag, ForwardFlag = ForwardFlag)
                else : 
                    v1 = BS_Price_To_ImpliedVolatility(PriceDateInt, MaturityDate, MoneynessPercent, TermDisc, RateDisc, DivTerm, DivRate, TargetPrice, minvol = 0.00001, maxvol = 2.5, TypeFlag = 'c', ForwardFlag = ForwardFlag)
                    v2 = BS_Price_To_ImpliedVolatility(PriceDateInt, MaturityDate, MoneynessPercent, TermDisc, RateDisc, DivTerm, DivRate, TargetPrice, minvol = 0.00001, maxvol = 2.5, TypeFlag = 'p', ForwardFlag = ForwardFlag)
                    v = (v1 + v2)/2
                volvalues[j][i] = v

        ResultDF = pd.DataFrame(volvalues, index = PriceData.index, columns = PriceData.columns)
        name = currency + " Equity Option Vol.csv"
        if name not in os.listdir(currdir + '\\MarketData\\outputdata\\' + str(PriceDate) + '\\' + currency) : 
            ResultDF.reset_index().to_csv(currdir + '\\MarketData\\outputdata\\' + str(PriceDate) + '\\' + currency + '\\' + name, index = False, encoding = 'cp949')
        print(str(PriceDate) + ' ' + str(currency) + ' EQVol 저장완료')
    else :
        print("오류 : " + str(PriceDate) + "자 EQVol, 제로금리가 없습니다.")

################
# Main Program #
################
MainFlag2 = 0
MainFlag = MainViewer(Title = 'Continue', MyText = 'Market Input Data Update', 
                               MyList = ["0: Data 업데이트 안함", "1: Data 업데이트함"], defaultvalue=1, 
                               size = "800x450+30+30", splitby = ":", 
                               listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
if MainFlag : 
    HolidayData = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.int64)
    UpdateFXSpotRateNaverFinance(currdir)
    LastFileDate, UpDatedDate, UpDateZeroList = Update_KRWIRSData(currdir)
    inputdir = currdir + '\\MarketData\\inputdata\\' + str(LastFileDate)
    CopyAllPreviousMarketData(currdir, inputdir, HolidayData)

    lstoutput = os.listdir(currdir + '\\MarketData\\outputdata')
    for i, d in enumerate(UpDatedDate) : 
        EQOptPriceToVolatility(d, currdir, currency = 'KRW')
        if d not in lstoutput :                         
            os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d , exist_ok=True) 
            os.makedirs(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\KRW", exist_ok=True) 
            UpDateZeroList[i].to_csv(currdir + '\\MarketData\\outputdata' + '\\' + d + "\\KRW\\KRW IRS ZeroCurve.csv", index = False)
    UpDateIRImpliedVolatilityFromQuoteToVol(currdir, UpDatedDate)
    UpDateCorpBondCurveFromInputData(currdir, UpDatedDate, HolidayData)

while True : 
    MainFlag = MainViewer(size = "800x450+50+50")
    if str(MainFlag) == 0 or len(str(MainFlag)) == 0 or (MainFlag not in [1,2,3,4,5,6,7,'1','2','3','4','5','6','7']) : 
        print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
        break
    elif MainFlag in [2,'2'] :         
        RAWFORMAT = MainViewer(Title = 'Continue', MyText = 'RawData 포멧을 선택하시오', 
                               MyList = ["0: My Raw Data", "1: KDB Raw Data"], defaultvalue=0, 
                               size = "800x450+30+30", splitby = ":", 
                               listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
        RAWData = MainFunction(currdir)
        AddedData = AddFRTB_BookedPosition(currdir, RAWData, RAWFORMAT)
        if len(AddedData) > 0 : 
            RAWData = pd.concat([RAWData, AddedData],axis = 0)
        if RAWFORMAT == 0 : 
            CSR,CSR_SecuritizedNonCTP,CSR_CTP,GIRR, FXR, EQR, COMR, DRC, RRAO = PreProcessingMyData(RAWData)
        else : 
            CSR,CSR_SecuritizedNonCTP,CSR_CTP,GIRR, FXR, EQR, COMR = PreProcessingBankData(RAWData, dataformat = 'splited') 
            DRC = pd.DataFrame([])
            RRAO = pd.DataFrame([])
        print("\n####################\n######산출중########\n####################\n")
        ResultData1 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 0, DRC = DRC, RRAO= RRAO)
        print("\n####################\n####산출중(33%)#####\n####################\n")
        ResultData2 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 1, DRC = DRC, RRAO= RRAO)
        print("\n####################\n####산출중(66%)#####\n####################\n")
        ResultData3 = AggregatedFRTB_RiskCharge(CSR, GIRR, FXR, EQR, COMR, CSR_SecuritizedNonCTP, CSR_CTP, DeltaSensiName = "Delta_Sensi",VegaSensiName = "Vega_Sensi", GroupbyFlag = 2, DRC = DRC, RRAO= RRAO)
        print("#################\n####산출완료#####\n#################\n")
        for i in range(10) : 
            ViewerFRTBFlag = MainViewer(Title = 'Continue', MyText = '산출완료되었습니다.\n 확인할 뷰어를 선택하시오.', MyList = ["0: 버킷별", "1: 부서별","2: 포트별","3: 종료"], size = "800x450+30+30", splitby = ":", listheight = 6, textfont = 13, titlelable = False, titleName = "Name")
            if ViewerFRTBFlag == 0 : 
                ViewFRTB(ResultData1) 
            elif ViewerFRTBFlag == 1 : 
                ViewFRTB(ResultData2)
            elif ViewerFRTBFlag == 2 : 
                ViewFRTB(ResultData3)
            else : 
                break
            
        SaveFlag = MainViewer(Title = 'Continue', MyText = 'FRTB Result 저장하시겠습니까(아래위치)\n' + currdir, MyList = ["0: FRTB Result 저장X", "1: FRTB Result 저장O", "2: FRTB Result 저장 및 RAWFILE저장"], size = "800x450+30+30", splitby = ":", listheight = 6, textfont = 13)
        if SaveFlag >= 1 : 
            writer = pd.ExcelWriter('ResultFRTB.xlsx') # pylint: disable=abstract-class-instantiated
            ResultData1.to_excel(writer, sheet_name = 'ByBucket')
            ResultData2.to_excel(writer, sheet_name = 'ByDepart')
            ResultData3.to_excel(writer, sheet_name = 'ByPortfolio')
            
            if version.parse(pd.__version__) < version.parse("1.6.0"):
                writer.save()   # 구버전 pandas
            else:
                pass            # 신버전 pandas            
            #writer.save()
            writer.close()
            if SaveFlag >= 2 : 
                RAWData.to_csv(currdir + "\\FRTB_RAW_INCLUDE_BOOK.csv", index = False)                
            
    elif MainFlag in [1,'1'] :                     
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
        try : 
            FXSpot = PreprocessingFXSpotData(currdir + "\\MarketData\\spot\\FXSpot.csv")        
        except FileNotFoundError : 
            FXSpot = pd.DataFrame([])
        MainFlag2 = ""
        n = MainViewer(Title = 'Pricer', MyText = 'Pricer를 선택하시오', MyList = ["1: 채권", "2: IRS", "3: CMS Swap", "4: Currency Swap","5: Equity Option", "6: IRStructuredSwap(1Factor FDM Single Phase)","7: Plain Swaption","8: Plain FX Swap","9: Cap Floor","10: IRStructuredSwap(2Factor FDM Single Phase)","11: IRStructuredSwap(1Factor FDM DoublePhase)","12: IRStructuredSwap(2Factor FDM DoublePhase)","13: Range Accrual Note"], size = "800x450+50+50", splitby = ":", listheight = 13, textfont = 13, titlelable = False, titleName = "Name")
        if int(n) == 1 or n == "채권" or str(n).lower() == "bond": 
            MainFlag2, Value, PV01, TempPV01 = PricingBondProgram(HolidayDate, currdir)
        elif int(n) == 2 or n == "IRS" or str(n).lower() == "irs" : 
            MainFlag2, Value, PV01, TempPV01 = PricingIRSProgram(HolidayDate, FXSpot)            
        elif int(n) == 3 or n == "CMS" or str(n).lower() == "cms" : 
            MainFlag2, Value, PV01, TempPV01 = PricingIRSProgram(HolidayDate, FXSpot, CMSUseFlag=1)            
        elif int(n) == 4 or n == "CRS" or str(n).lower() == "crs" : 
            MainFlag2, Value, PV01, TempPV01, TempPV01Est, TempPV01Est2 = PricingCRSProgram(HolidayDate, FXSpot)
        elif int(n) == 5 or n == "옵션" or str(n).lower() == "option" :
            MainFlag2, Value, PV01, TempPV01 = PricingEquityOptionProgram(currdir, HolidayDate)
        elif int(n) == 6 :
            MainFlag2, Value, PV01, TempPV01 = PricingIRStructuredSwapProgram(HolidayDate, currdir)             
        elif int(n) == 7 : 
            MainFlag2, Value, PV01, TempPV01 = BS_Swaption_Program(HolidayDate, currdir)
        elif int(n) == 8 : 
            MainFlag2, Value, PV01, TempPV01 = PricingFXSwapProgram(HolidayDate, FXSpot, currdir)
        elif int(n) == 9 : 
            MainFlag2, Value, PV01, TempPV01 = BS_CapFloor_Program(HolidayDate, currdir)
        elif int(n) == 10 :
            MainFlag2, Value, PV01, TempPV01 = PricingIRStructuredSwapProgram2F(HolidayDate, currdir)             
        elif int(n) == 11 :
            MainFlag2, Value, PV01, TempPV01 = PricingIRStructuredSwapProgramDoublePhase(HolidayDate, currdir)             
        elif int(n) == 12 :
            MainFlag2, Value, PV01, TempPV01 = PricingIRStructuredSwapProgram2FDoublePhase(HolidayDate, currdir)             
        elif int(n) == 13 : 
            MainFlag2, Value, PV01, TempPV01 = PricingRangeAccrualNote(HolidayDate, currdir)
        
    elif MainFlag in [3,'3'] : 
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
        FXSpot = PreprocessingFXSpotData(currdir + "\\MarketData\\spot\\FXSpot.csv")        
        YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\inputdata",MultiSelection=False, namenotin = "ption", defaultvalue=0, DefaultStringList = ["IRS"])
        MyData = Data[0]
        ZeroCurveName = Name[0]
        ResultDF = ZeroCurveMaker(MyData, currdir, YYYYMMDD, HolidayDate, FXSpot, ZeroCurveName)

    elif MainFlag in [4,'4'] : 
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
        YYYYMMDD, Name, Data = UsedMarketDataSetToPricing(currdir + "\\MarketData\\inputdata", namein = 'sw')
        PriceToSwaptionVolProgram(YYYYMMDD, Name, Data, currdir, HolidayDate)
  
    elif MainFlag in [5, '5'] : 
        CapFloorCalibrationProgram(currdir)
    
    elif MainFlag in [6, '6'] : 
        HolidayDate = ReadCSV(currdir + "\\MarketData\\holidays\\Holidays.csv").fillna("19990101").applymap(lambda x : str(x).replace("-","")).astype(np.float64)        
        KappaCalibration(HolidayDate, currdir)

    elif MainFlag in [7, '7'] :
        FXSpot = PreprocessingFXSpotData(currdir + "\\MarketData\\spot\\FXSpot.csv")        
        CalcFXDeltaProgram_FromFXPosition(FXSpot)

    MainFlag2 = MainViewer(Title = 'Continue', MyText = '종료하시겠습니까', MyList = ["0: 종료", "1: 계속 다른업무 실행"], size = "800x450+30+30", splitby = ":", listheight = 6, textfont = 13)
    if MainFlag2 == 0:
        print("\n###########################\n### 프로그램을 종료합니다.###\n###########################")
        break    


# %%

# %%

# %%
#Arithmetic_Asian_Opt_Pricing_Preprocessing(Long0Short1 = 0, Call0Put1 = 0, PriceDate = 20240627, AverageStartDate = 20240601, AverageEndDate = 20240927, OptionMaturityDate = 20240927, S = 100, K = 95, PrevAverage = 98, DiscTerm = [1, 2, 3], DiscRate = [0.03, 0.03, 0.03], DivTerm = [1], DivRate = [0.02], QuantoCorr = 0, FXVolTerm = [1], FXVol = [0], VolTerm = [0], VolParity = [0], Vols2D = 0.3, DivTypeFlag = 0, Holidays = KoreaHolidaysFromStartToEnd(2020,2040))


# %%
