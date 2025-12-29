#%%
"""
Created By Daesun Lim (CIIA(R), FRM(R))
Bank Risk Quant
My Pricing Module 
v1.0.1
"""
import numpy as np
import pandas as pd
from Utility import Linterp, Linterp2D, DayCountAtoB, YYYYMMDDToExcelDate, ExcelDateToYYYYMMDD, DayCountFractionAtoB, MappingCouponDates, EDate_YYYYMMDD, malloc_cpn_date_holiday, DayPlus, MonthCountAtoB, KoreaHolidaysFromStartToEnd, USHolidaysFromStartToEnd, BusinessDateArrayFromAtoB, ReadCSV, NBusinessCountFromEndToPay, ParseBusinessDateIfHoliday, NextNthBusinessDate, MapProductType, Calc_ZeroRate_FromDiscFactor, CalcZeroRateFromSwapPoint, Generate_OptionDate
from RiskModule import MapGIRRDeltaGreeks, MapCSRDeltaGreeks, MapEquityRiskWeight, EQDeltaRWMappingDF, Calc_GIRRDeltaNotCorrelated_FromGreeks, Calc_CSRDeltaNotCorrelated_FromGreeks, Calc_FXRDelta, HighLiquidCurrency, PreProcessingMyData, PreProcessingBankData, AggregatedFRTB_RiskCharge, Calc_GIRRDeltaNotCorrelated_FromGreeks_PreProcessing, GIRR_DeltaRiskWeight, Calc_GIRRVega, MapGIRRVegaGreeks
import os
# JIT은 쓰지말자
#from numba import jit
#from scipy.sparse import diags
vers = "1.0.1"
recentupdate = '20251221'

def Calc_Forward_Rate_ForSOFR(TermArray, RateArray, T1, T2, DeltaT):
    LengthArray = min(len(TermArray), len(RateArray))
    EXP_APPROX = 2.718281828459045
    # Linear Interpolation
    if TermArray[0] < T1 < TermArray[LengthArray - 1]:
        DFT1 = np.exp(-Linterp(TermArray, RateArray, T1) * T1)
        DFT2 = np.exp(-Linterp(TermArray, RateArray, T2) * T2)
        FRate = (1.0 / DeltaT) * (DFT1 / DFT2 - 1.0)
    elif T1 <= TermArray[0]:
        DFT1 = np.exp(-RateArray[0] * T1)
        DFT2 = np.exp(-Linterp(TermArray, RateArray, T2) * T2)
        FRate = (1.0 / DeltaT) * (DFT1 / DFT2 - 1.0)
    else:
        DFT1 = np.exp(-RateArray[LengthArray - 1] * T1)
        DFT2 = np.exp(-RateArray[LengthArray - 1] * T2)
        FRate = (1.0 / DeltaT) * (DFT1 / DFT2 - 1.0)    
    return FRate

def SOFR_ForwardRate_Compound(
    PriceDate,
    RefCrvTerm,
    RefCrvRate, 
    ForwardStartYYYYMMDD,
    ForwardEndYYYYMMDD,
    LockOutDays,
    LookBackDays,
    ObservShift,
    HolidayFlag,
    NotHoliday,
    DayCountNotHoliday,
    RefHistoryDate,
    RefHistory,
    denominator,
    SOFRUseFlag
):
    
    nday = DayCountAtoB(ForwardStartYYYYMMDD, ForwardEndYYYYMMDD)
    N_NotHoliday = len(NotHoliday)
    AverageFlag = 1 if SOFRUseFlag == 3 else 0
    dt = 1.0 / 365.0
    deltat = 1.0 / denominator
    PrevForwardRate = Calc_Forward_Rate_ForSOFR(RefCrvTerm, RefCrvRate, 0.0, dt, deltat)
    ForwardRate = PrevForwardRate
    PI_0 = 1.0
    
    EstStart = ForwardStartYYYYMMDD
    if ((ForwardStartYYYYMMDD in NotHoliday)) :
        EstStart = ForwardStartYYYYMMDD
    else : 
        for i in range(N_NotHoliday - 1) : 
            if (NotHoliday[i] < ForwardStartYYYYMMDD and NotHoliday[i + 1] > ForwardStartYYYYMMDD) :
                EstStart = NotHoliday[i + 1]
                break
    
    EstEnd = ForwardEndYYYYMMDD
    if ((ForwardEndYYYYMMDD in NotHoliday)) :
        EstEnd = ForwardEndYYYYMMDD
    else : 
        for i in range(N_NotHoliday - 1) : 
            if (NotHoliday[i] < ForwardEndYYYYMMDD and NotHoliday[i + 1] > ForwardEndYYYYMMDD) :
                EstEnd = NotHoliday[i + 1]
                break
    
    if EstStart in NotHoliday : 
        EstStartIdx = list(NotHoliday).index(EstStart)
    else : 
        EstStartIdx = 0
        for i in range(N_NotHoliday - 1) : 
            if (NotHoliday[i] < EstStart and NotHoliday[i + 1] > EstStart) :
                EstStartIdx = i
                break

    if EstEnd in NotHoliday : 
        EstEndIdx = list(NotHoliday).index(EstEnd)
    else : 
        EstEndIdx = 0
        for i in range(N_NotHoliday - 1) : 
            if (NotHoliday[i] < EstEnd and NotHoliday[i + 1] > EstEnd) :
                EstEndIdx = i
                break
    
    T = DayCountAtoB(EstStart, EstEnd) / denominator    
    ObservShiftFlag = 1 if LookBackDays > 0 and ObservShift > 0 else 0    
    NCumpound = 0
    AverageRate = 0.0    
    LockOutDay = NotHoliday[max(0, EstEndIdx - LockOutDays)] if LockOutDays > 0 else EstEnd
    
    for i in range(EstStartIdx, EstEndIdx):
        DayYYYYMMDD = NotHoliday[i]
        T1Est = DayCountAtoB(PriceDate, NotHoliday[max(0, i - LookBackDays)]) / 365.0
        T2Est = DayCountAtoB(PriceDate, NotHoliday[max(0, i - LookBackDays + 1)]) / 365.0
        
        if (ObservShiftFlag == 0) :
            Delta_T1_T2 = (float(DayCountNotHoliday[i])) / denominator
        else :
            Delta_T1_T2 = (float(DayCountNotHoliday[max(0, i - LookBackDays)])) / denominator
        
        if T1Est < 0.0:
            HistDayIdx = -1
            if NotHoliday[max(0, i - LookBackDays)] in RefHistoryDate : 
                HistDayIdx = list(RefHistoryDate).index(NotHoliday[max(0, i - LookBackDays)])
            ForwardRate = RefHistory[HistDayIdx] if HistDayIdx >= 0 else PrevForwardRate
        else:
            if DayYYYYMMDD < LockOutDay:
                if HolidayFlag == 0:
                    ForwardRate = Calc_Forward_Rate_ForSOFR(RefCrvTerm, RefCrvRate, T1Est, T2Est, Delta_T1_T2)
                else:
                    T3Est = DayCountAtoB(PriceDate, NotHoliday[max(0, min(N_NotHoliday - 1, i - LookBackDays + 2))]) / 365.0
                    ForwardRate = Calc_Forward_Rate_ForSOFR(RefCrvTerm, RefCrvRate, T2Est, T3Est, Delta_T1_T2)
            else:
                ForwardRate = PrevForwardRate
        
        PI_0 *= 1.0 + ForwardRate * Delta_T1_T2
        AverageRate += ForwardRate
        PrevForwardRate = ForwardRate
        NCumpound += 1
    
    if AverageFlag == 1:
        AverageRate /= NCumpound
        PI_0 = (1.0 + AverageRate / denominator) ** nday
    
    AnnualizedOISRate = (PI_0 - 1.0) / T
    return PI_0 - 1.0, AnnualizedOISRate, EstStartIdx, EstEndIdx

def istermtype(termlist) : 
    term = np.array(termlist, dtype = np.float64)
    if term.min() >= 19000101 : 
        return "YYYYMMDD"
    elif term.min() > 30.0 : 
        return "ExcelDate"
    else : 
        return "Term"

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

def Preprocessing_EQVol(ParityArray, TermArray, Vols2D, PriceDate, StockPrice) : 
    if len(TermArray) > 0 : 
        istermtype_ZeroTerm = istermtype(TermArray)
        if istermtype_ZeroTerm == "YYYYMMDD" : 
            for i in range(len(TermArray)) : 
                TermArray[i] = (DayCountAtoB(PriceDate, TermArray[i])/365)
        elif istermtype_ZeroTerm == "ExcelDate" :
            ExcelPriceDate = YYYYMMDDToExcelDate(PriceDate) if int(PriceDate) >= 19000101 else PriceDate
            for i in range(len(TermArray)) : 
                TermArray[i] = ((TermArray[i] - ExcelPriceDate)/365)
        
    if np.array(Vols2D).max() > 2.0 :
        for i in range(Vols2D.shape[0]) : 
            for j in range(Vols2D.shape[1]) : 
                Vols2D[i][j] /= 100
                
    if np.array(ParityArray).max() > 5.0 : 
        for i in range(len(ParityArray)) : 
            ParityArray[i] = ParityArray[i]/StockPrice

def Calc_Discount_Factor(Term, Rate, T) : 
    r = Linterp(Term, Rate, T)
    return np.exp(-r * T)

def Calc_ForwardDiscount_Factor(Term, Rate, t, T) : 
    r1 = np.interp(t, Term, Rate)
    r2 = np.interp(T, Term, Rate)
    return np.exp(-r2 * T)/np.exp(-r1 * t)

def FSR(PricingDate, SwapStartDate, SwapMaturity, NCPN_Ann, DayCountFlag,
        Holiday, Term, Rate, TermDisc, RateDisc) :
    if PricingDate < 19000101 : 
        PricingDate = ExcelDateToYYYYMMDD(PricingDate)
    if SwapStartDate < 19000101 : 
        SwapStartDate = ExcelDateToYYYYMMDD(SwapStartDate)
    if SwapMaturity < 19000101 : 
        SwapMaturity = ExcelDateToYYYYMMDD(SwapMaturity)
    if NCPN_Ann == 0 : 
        T1 = DayCountAtoB(PricingDate, SwapStartDate)/365
        T2 = DayCountAtoB(PricingDate, SwapMaturity)/365
        DeltaT = DayCountFractionAtoB(SwapStartDate, SwapMaturity, DayCountFlag)
        return Calc_Forward_Rate_ForSOFR(Term, Rate, T1, T2, DeltaT)
    Preprocessing_ZeroTermAndRate(Term, Rate, PricingDate)
    Preprocessing_ZeroTermAndRate(TermDisc, RateDisc, PricingDate)
    NHoliday = len(Holiday)
    NTerm = len(Term)
    NTermDisc = len(TermDisc)
    FixingDate, CpnDate, PayDate, NBD = MappingCouponDates(1,SwapStartDate,SwapMaturity, 0, NCPN_Ann,1,Holiday,Holiday,1)
    NCpnDate = len(CpnDate)
    t = DayCountAtoB(PricingDate, SwapStartDate) / 365.0
    P0T = [0] * (NCpnDate + 1)
    P0T[0] = Calc_Discount_Factor(Term, Rate, t)
    
    for i in range(1, NCpnDate + 1):
        t = DayCountAtoB(PricingDate, CpnDate[i - 1]) / 365.0
        P0T[i] = Calc_Discount_Factor(Term, Rate,  t)
    
    a = P0T[0] - P0T[NCpnDate]
    b = 0.0
    
    for i in range(NCpnDate):
        t = DayCountAtoB(PricingDate, CpnDate[i]) / 365.0
        
        if i == 0:
            dt = DayCountFractionAtoB(SwapStartDate, CpnDate[i], DayCountFlag)
        else:
            dt = DayCountFractionAtoB(CpnDate[i - 1], CpnDate[i], DayCountFlag)
        
        b += dt * Calc_Discount_Factor(TermDisc, RateDisc, t)
    
    Swap_Rate = a / b
    return Swap_Rate

def Calc_CMS_Maturity(StartingDate, RefSwap_Maturity_T_Year = 0.25) : 
    MatDate = EDate_YYYYMMDD(StartingDate, int(RefSwap_Maturity_T_Year * 12 + 1e-9))
    return MatDate

def GPrimePrime_Over_GPrime(CpnRate, YTM, PriceDate, SwapMaturityT, NumCpnOneYear):
    if SwapMaturityT < 19000101 : 
        SwapEndDate = Calc_CMS_Maturity(PriceDate, SwapMaturityT)
    else : 
        SwapEndDate = SwapMaturityT        
    CpnDates, FirstCpnDate = malloc_cpn_date_holiday(PriceDate, SwapEndDate, NumCpnOneYear)
    Gp = 0.0
    Gpp = 0.0
    
    for i in range(len(CpnDates)):
        T = DayCountFractionAtoB(PriceDate, CpnDates[i], 3)
        if i == 0:
            Deltat = DayCountFractionAtoB(PriceDate, CpnDates[i], 3)
        else:
            Deltat = DayCountFractionAtoB(CpnDates[i - 1], CpnDates[i], 3)
        
        Gp -= CpnRate * Deltat * T * (1.0 + YTM)**(-T)
        Gpp += CpnRate * Deltat * T * T * (1.0 + YTM)**(-T)
        
        if i == len(CpnDates) - 1:
            Gp -= T * (1.0 + YTM)**(-T)
            Gpp += T * T * (1.0 + YTM)**(-T)
    
    return (Gpp / 100.0) / Gp

def CDF_N(x) : 
    y = abs(x)
    if (y > 37.0) : 
        value = 0.
    else :
        Exponential = np.exp(-y * y / 2)
        if (y < 7.07106781186547) :
            S = 3.52624965998911E-02 * y + 0.700383064443688
            S = S * y + 6.37396220353165
            S = S * y + 33.912866078383
            S = S * y + 112.079291497871
            S = S * y + 221.213596169931
            S = S * y + 220.206867912376
            S2 = 8.83883476483184E-02 * y + 1.75566716318264
            S2 = S2 * y + 16.064177579207
            S2 = S2 * y + 86.7807322029461
            S2 = S2 * y + 296.564248779674
            S2 = S2 * y + 637.333633378831
            S2 = S2 * y + 793.826512519948
            S2 = S2 * y + 440.413735824752
            value = Exponential * S / S2
        else :
            S = y + 0.65
            S = y + 4.0 / S
            S = y + 3.0 / S
            S = y + 2.0 / S
            S = y + 1.0 / S
            value = Exponential / (S * 2.506628274631)

    if (x > 0.0) :
        value = 1.0 - value

    return value

def BS_Option(PriceDate, MaturityDate, S0, X, TermDisc, 
              RateDisc, DivTerm, DivRate, Volatility, QuantoCorr = 0, 
              FXVolTerm = [], FXVol = [], DivFlag = 0, EstTerm = [], EstRate = [], 
              ForwardPrice = 0, LoggingFlag = 0, LoggingDir = "", VolTerm = [0], VolParity = [0],TypeFlag = 'c', ATMVolFlag = False, ATMVol = []) :
    
    if len(EstTerm) == 0 and ForwardPrice == 0 : 
        EstTerm = TermDisc
        EstRate = RateDisc
    elif ForwardPrice > 0 :
        EstTerm = [0]
        EstRate = [0]
    
    if PriceDate < 19000101 : 
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    if MaturityDate < 19000101 : 
        MaturityDate = ExcelDateToYYYYMMDD(MaturityDate)
        
    Preprocessing_ZeroTermAndRate(TermDisc, RateDisc, PriceDate)
    Preprocessing_ZeroTermAndRate(EstTerm, EstRate, PriceDate)
    TimeToMaturity = DayCountAtoB(PriceDate, MaturityDate)/365
    StockLevel = X/S0 if np.array(VolParity).max() < 3.0 else X
    v = 0.001
    try : 
        if isinstance(Volatility, float) : 
            v = Volatility
        elif ATMVolFlag == False : 
            v = Linterp2D(VolTerm, VolParity, Volatility, TimeToMaturity, StockLevel)
        else : 
            v = np.interp(TimeToMaturity, VolTerm, ATMVol)
    except TypeError : 
        if isinstance(Volatility, float) : 
            v = Volatility
        elif ATMVolFlag == False : 
            v = Volatility
        else : 
            v = np.interp(TimeToMaturity, VolTerm, ATMVol)
                
    d1, d2 = 0, 0
    fxvol = Linterp(FXVolTerm, FXVol, TimeToMaturity) if len(FXVolTerm) > 0 else 0
    r_est = Linterp(EstTerm, EstRate, TimeToMaturity) - fxvol * v * QuantoCorr 
    r_disc = Linterp(TermDisc, RateDisc, TimeToMaturity)
    DivPV, F = 0, S0
    if DivFlag < 2 : 
        Preprocessing_ZeroTermAndRate(DivTerm, DivRate, PriceDate)
        Dv = Linterp(DivTerm, DivRate, TimeToMaturity) if len(DivTerm) > 0 else 0
        F = S0 * np.exp((r_est - Dv) * TimeToMaturity) if ForwardPrice == 0 else ForwardPrice
    else : 
        for i in range(len(DivTerm)) : 
            if DivTerm[i] < 30 : 
                DivTerm[i] = DayPlus(PriceDate, int(DivTerm[i] * 365.0 + 0.00001)) 
            elif DivTerm[i] < 19000101 : 
                DivTerm[i] = ExcelDateToYYYYMMDD(int(DivTerm[i]))
            
            if DivTerm[i] < MaturityDate and DivTerm[i] > PriceDate : 
                t = DayCountAtoB(PriceDate, DivTerm[i])/365
                r = Linterp(TermDisc, RateDisc, t)
                DivPV += DivRate[i] * np.exp(-r * t)
        S0 = S0 - DivPV
        F = S0 * np.exp((r_est) * TimeToMaturity) if ForwardPrice == 0 else ForwardPrice
    DiscountFactor = np.exp(-r_disc * TimeToMaturity)
    Price, Delta, Gamma, Vega, Theta, Rho = 0, 0, 0, 0, 0, 0
    if TimeToMaturity < 0.0000001 or PriceDate == MaturityDate : 
        if TypeFlag in [1,'1','c','C'] : 
            Price = max(S0 - X, 0)
            Delta = 1 if S0 - X > 0 else 0
        else : 
            Price = max(-S0 + X, 0)
            Delta = 1 if -S0+X < 0 else 0
        Gamma = Vega = Theta = Rho = 0
    else : 
        d1 = (np.log(F/X) + (0.5 * v * v) * TimeToMaturity)/(v * np.sqrt(TimeToMaturity))       
        d2 = d1 - v * np.sqrt(TimeToMaturity)
        if TypeFlag in [1,'1','c','C'] : 
            Price = (F * CDF_N(d1) - X * CDF_N(d2)) * DiscountFactor
            exp_minusdivt = F / S0 * np.exp(-r_est * TimeToMaturity)
            Delta = exp_minusdivt * CDF_N(d1)
            PDF_Nd1 = np.exp(-d1 * d1/2.0) / np.sqrt(2.0 * np.pi)
            Gamma = exp_minusdivt * PDF_Nd1/(S0 * v * np.sqrt(TimeToMaturity))
            Vega = exp_minusdivt * PDF_Nd1 * S0 * np.sqrt(TimeToMaturity)
            Theta = -exp_minusdivt * 0.5 * S0 * PDF_Nd1 * v / np.sqrt(TimeToMaturity) - r_disc * X * np.exp(-r_disc * TimeToMaturity) * CDF_N(d2)
            Rho = X * TimeToMaturity * np.exp(-r_disc * TimeToMaturity) * CDF_N(d2)
        else : 
            Price = (-F * CDF_N(-d1) + X * CDF_N(-d2)) * DiscountFactor
            exp_minusdivt = F / S0 * np.exp(-r_est * TimeToMaturity)
            Delta = exp_minusdivt * (CDF_N(d1)-1)
            PDF_Nd1 = np.exp(-d1 * d1/2.0) / np.sqrt(2.0 * np.pi)
            Gamma = exp_minusdivt * PDF_Nd1/(S0 * v * np.sqrt(TimeToMaturity))
            Vega = exp_minusdivt * PDF_Nd1 * S0 * np.sqrt(TimeToMaturity)
            Theta = exp_minusdivt * 0.5 * S0 * PDF_Nd1 * v / np.sqrt(TimeToMaturity) + r_disc * X * np.exp(-r_disc * TimeToMaturity) * CDF_N(d2)
            Rho = -X * TimeToMaturity * np.exp(-r_disc * TimeToMaturity) * CDF_N(d2)
    
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[TimeToMaturity, S0, X, r_disc, r_est,ForwardPrice, v, d1, d2, Price, Delta, Gamma, Vega, Theta, Rho]], 
                               columns = ["TimeToMaturity", "S0", "X", "r_disc","r_est","ForwardPrice", "Volatility", "d1", "d2", "Price", "Delta", "Gamma", "Vega", "Theta", "Rho"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)
    return Price, Delta, Gamma, Vega, Theta, Rho, v

def BS_Price_To_ImpliedVolatility(PriceDate, MaturityDate, MoneynessPercent, TermDisc, RateDisc, DivTerm, DivRate, TargetPrice, minvol = 0.00001, maxvol = 2.5, TypeFlag = 'c', ForwardFlag = False) : 

    S0 = 1/MoneynessPercent # if 0.5 is Exercise Price S is 1.0
    X = 1
    TargetVol = maxvol    
    maxvolprice = BS_Option(PriceDate, MaturityDate, S0, X, TermDisc, 
              RateDisc, DivTerm, DivRate, TargetVol, QuantoCorr = 0, 
              FXVolTerm = [], FXVol = [], DivFlag = 0, EstTerm = [], EstRate = [], 
              ForwardPrice = 0 if ForwardFlag == False else S0, LoggingFlag = 0, LoggingDir = "", VolTerm = [0], VolParity = [0],
              TypeFlag = TypeFlag, ATMVolFlag = False, ATMVol = [])[0]
    if maxvolprice < TargetPrice : 
        return BS_Price_To_ImpliedVolatility(PriceDate, MaturityDate, MoneynessPercent, TermDisc, RateDisc, DivTerm, DivRate, TargetPrice, maxvol = 2 * maxvol)
    else : 

        maxvolprice = BS_Option(PriceDate, MaturityDate, S0, X, TermDisc, 
                    RateDisc, DivTerm, DivRate, TargetVol, QuantoCorr = 0, 
                    FXVolTerm = [], FXVol = [], DivFlag = 0, EstTerm = [], EstRate = [], 
                    ForwardPrice = 0 if ForwardFlag == False else S0, LoggingFlag = 0, LoggingDir = "", VolTerm = [0], VolParity = [0],
                    TypeFlag = TypeFlag, ATMVolFlag = False, ATMVol = [])[0]
        minvolprice = BS_Option(PriceDate, MaturityDate, S0, X, TermDisc, 
                    RateDisc, DivTerm, DivRate, minvol, QuantoCorr = 0, 
                    FXVolTerm = [], FXVol = [], DivFlag = 0, EstTerm = [], EstRate = [], 
                    ForwardPrice = 0 if ForwardFlag == False else S0, LoggingFlag = 0, LoggingDir = "", VolTerm = [0], VolParity = [0],
                    TypeFlag = TypeFlag, ATMVolFlag = False, ATMVol = [])[0]

        for i in range(500) : 
            ResultPrice = BS_Option(PriceDate, MaturityDate, S0, X, TermDisc, 
                RateDisc, DivTerm, DivRate, TargetVol, QuantoCorr = 0, 
                FXVolTerm = [], FXVol = [], DivFlag = 0, EstTerm = [], EstRate = [], 
                ForwardPrice = 0 if ForwardFlag == False else S0, LoggingFlag = 0, LoggingDir = "", VolTerm = [0], VolParity = [0],
                TypeFlag = TypeFlag, ATMVolFlag = False, ATMVol = [])[0]
            Err = ResultPrice - TargetPrice

            if abs(Err) < 0.000001 :
                # if error lower than 0.01bp break 
                break

            if Err > 0 : 
                maxvol = TargetVol
                TargetVol = (minvol + TargetVol)/2.0
            else : 
                minvol = TargetVol
                TargetVol = (TargetVol + maxvol)/2.0 
        if i == 500 : 
            raise ValueError("Can't Find Solution")
        return TargetVol

def BSDigitalOption(TypeFlag, PriceDate, Maturity, PayDate, S0, X, DiscTerm, DiscRate, RefTerm, RefRate, DivTerm, DivRate, VolTerm, VolParity, Vols2D, QuantoCorr, FXVolTerm, FXVol, DivType, ForwardPrice = 0, LoggingFlag = 0, LoggingDir = os.getcwd()) : 
    T = max(0.00001, DayCountAtoB(PriceDate, Maturity)/365)
    TEnd = T
    TPay = DayCountAtoB(PriceDate, PayDate)/365
    TPay = max(T, TPay)
    Preprocessing_ZeroTermAndRate(DiscTerm, DiscRate, PriceDate)
    Preprocessing_ZeroTermAndRate(RefTerm, RefRate, PriceDate)
    Preprocessing_Term(DivTerm, PriceDate)
    df_tmat_to_pay = Calc_ForwardDiscount_Factor(DiscTerm,DiscRate, T, TPay) if T != TPay else 1
    if (DivType == 0) : 
        dvd = DivRate[0] if ForwardPrice <= 0 else 0
    elif (DivType == 1) : 
        dvd = np.interp(TEnd, DivTerm, DivRate) if ForwardPrice <= 0 else 0
    else : 
        td = np.array(DivTerm)
        dr = np.array(DivRate)
        idx = td <= TEnd
        dvd = 1/TEnd * dr[idx].sum() / S0 if ForwardPrice <= 0 else 0
        
    if isinstance(Vols2D, float) : 
        vol = Vols2D
    else : 
        vol = Linterp2D(VolTerm, VolParity, Vols2D, TEnd, X/S0 if np.array(VolParity).max() < 2.0 else S0)
    
    fxv = np.interp(TEnd, FXVolTerm, FXVol) if len(FXVolTerm) > 0 else 0
    rd = np.interp(TEnd, DiscTerm, DiscRate)
    if ForwardPrice > 0 : 
        rf = 1/TEnd * np.log(ForwardPrice/S0)
    else : 
        if len(RefTerm) > 0 :
            rf = np.interp(TEnd, RefTerm, RefRate)
        else : 
            rf = rd

    DiscreteDivFlag = 0 if DivType != 2 else 1  
    if DiscreteDivFlag == 1 : 
        S0 = S0 - dvd * np.exp(-rd * T)
        dvd = 0

    Rf_Quanto = rf - fxv * vol * QuantoCorr     
    d1 = (np.log(S0 / X) + (Rf_Quanto - dvd + 0.5 * vol * vol) * T) / (vol * np.sqrt(T)) 
    d2 = d1 - vol * np.sqrt(T)
    theta_d2 = -(Rf_Quanto - dvd - 0.5 * vol * vol) / (vol * np.sqrt(T)) + 0.5 * d2 / T
    PDF_ND2 = np.exp(-d2 * d2/2.0) / np.sqrt(2.0 * np.pi)
    if (TypeFlag == 1) : 
        if (X <= 0.0) : 
            Price = np.exp(-rd * T)
            Delta = 0.0
            Gamma = 0.0
            Vega = 0.0
            Theta = dvd * S0 * np.exp(-dvd * T) - rd * X * np.exp(-rd * T)
            Rho = X * T * np.exp(-rd * T)
        else : 
            Price = np.exp(-rd * T) * CDF_N(d2) 
            Delta = np.exp(-rd * T) * PDF_ND2 / (vol * np.sqrt(T) * S0)
            Gamma = -np.exp(-rd * T) * PDF_ND2 / (vol * vol * (T)*S0 * S0) * (d2 + (vol * np.sqrt(T)))
            Vega = -np.exp(-rd * T) * PDF_ND2 * (np.sqrt(T) + d2 / vol)
            Theta = np.exp(-rd * T) * (Rf_Quanto * CDF_N(d2) + PDF_ND2 * theta_d2)
            Rho = -np.exp(-rd * T) * (T * CDF_N(d2) - PDF_ND2 * np.sqrt(T) / vol)
    else : 
        if X <= 0.0 : 
            Price = 0.0
            Delta = 0.0
            Gamma = 0.0
            Vega = 0.0
            Theta = 0.0
            Rho = 0.0         
        else :
            Price = np.exp(-rd * T) * CDF_N(-d2)
            Delta = -np.exp(-rd * T) * PDF_ND2 / (vol * np.sqrt(T) * S0)
            Gamma = np.exp(-rd * T) * PDF_ND2 / (vol * vol * (T)*S0 * S0) * (d2 + (vol * np.sqrt(T)))
            Vega = np.exp(-rd * T)* PDF_ND2* (np.sqrt(T) + d2 / vol)
            Theta = np.exp(-rd * T) * (Rf_Quanto * CDF_N(-d2) - PDF_ND2 * theta_d2)
            Rho = -((np.exp(-rd * T) * (PDF_ND2 * np.sqrt(T) / vol - T * CDF_N(-1.0 * d2))))
    Price *= df_tmat_to_pay
    Delta *= df_tmat_to_pay
    Gamma *= df_tmat_to_pay
    Vega *= df_tmat_to_pay
    Theta *= df_tmat_to_pay
    Rho *= df_tmat_to_pay
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[T, S0, X, rd, Rf_Quanto,ForwardPrice, vol, d1, d2, Price, Delta, Gamma, Vega, Theta, Rho]], 
                               columns = ["TimeToMaturity", "S0", "X", "r_disc","r_est","ForwardPrice", "Volatility", "d1", "d2", "Price", "Delta", "Gamma", "Vega", "Theta", "Rho"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)

    return Price, Delta, Gamma, Vega, Theta, Rho, vol

def Sumation_Beta(StartIDX, EndIDX, ForwardArray, WeightArray) : 
    return (ForwardArray[StartIDX:EndIDX+1] * WeightArray[StartIDX:EndIDX+1]).sum()

def Arithmetic_Asian_Opt_m1(N, WeightArray, ForwardArray) : 
    return Sumation_Beta(0, N-1, ForwardArray, WeightArray)

def Arithmetic_Asian_Opt_m2(n, Forward, Weight, T, TermVol, Vol):
    TauAry = T[:n]
    SigAry = np.interp(TauAry, TermVol, Vol)
    eAry = np.exp(SigAry * SigAry * TauAry)
    BetaAry = Forward[:n] * Weight[:n]
    SumBetaFunc = np.vectorize(lambda i : Sumation_Beta(i, n - 1, Forward[:n], Weight[:n]))
    SumBetaAry = SumBetaFunc(np.arange(0,n))
    value1 = 2.0 * (BetaAry * eAry * SumBetaAry).sum()
    value2 = (BetaAry * BetaAry * eAry).sum()
    m2 = value1 - value2
    return m2

def Arithmetic_Asian_Opt_m3(n, Forward, Weight, T, TermVol, Vol):
    m3 = 0.0
    TauAry = T[:n]
    SigAry = np.interp(TauAry, TermVol, Vol)
    eAry = np.exp(SigAry * SigAry * TauAry)
    BetaAry = Forward[:n] * Weight[:n]
    SumBetaFunc = np.vectorize(lambda i : Sumation_Beta(i, n - 1, Forward[:n], Weight[:n]))
    SumBetaAry = SumBetaFunc(np.arange(0,n))
    V1Ary = (BetaAry * BetaAry * eAry)
    V2Ary = 3.0 * (BetaAry * eAry * SumBetaAry)
    for i in range(n):
        e_i = eAry[i]
        b_i = BetaAry[i]
        V1 = V1Ary[i]
        V2 = V2Ary[i]
        j_ary = np.arange(i, n)
        V3 = 3.0 * (BetaAry[j_ary] * BetaAry[j_ary] * eAry[j_ary]).sum()
        SumBetaAry2 = SumBetaFunc(j_ary)
        V4 = 6.0 * (BetaAry[j_ary] * eAry[j_ary] * SumBetaAry2).sum()        
        m3 += 2.0 * b_i * e_i * e_i * (V1 - V2 - V3 + V4)

    return m3

def Arithmetic_Asian_Option_Delta(n, Forward, Weight, T, TermVol, Vol, r, y1, y11, d1):
    delta = 0.0
    PDF_ND1 = np.exp(-d1 * d1/2.0) / np.sqrt(2.0 * np.pi)
    for i in range(n):
        sumaFe = 0.0
        for k in range(i) :
            v = np.interp(T[k], TermVol, Vol)
            sumaFe += Weight[k] * Forward[k] * np.exp(v * v * T[k])

        v = np.interp(T[i], TermVol, Vol)
        sumaF = 0.0
        for k in range(i, n):
            sumaF += Weight[k] * Forward[k] * np.exp(v * v * T[i])

        sqrt_log_term = np.sqrt(np.log(y11 / (y1 * y1)))
        delta_i = Weight[i] * np.exp(-r * T[n - 1]) * (CDF_N(d1) + y1 * PDF_ND1 * y1 * y1 / (sqrt_log_term * y11) * ((sumaFe + sumaF) / y11 - 1.0 / y1))
        delta += delta_i
    return delta

def Arithmetic_Asian_Option_Vega(n, Forward, Weight, T, TermVol, Vol, r, y1, y11, d1):
    vega = 0.0
    PDF_ND1 = np.exp(-d1 * d1/2.0) / np.sqrt(2.0 * np.pi)
    for i in range(n):
        sumaF = 0.0
        for j in range(i + 1, n):
            sumaF += 2.0 * Weight[j] * Forward[j]

        aF_i = Weight[i] * Forward[i]
        v = np.interp(T[i], TermVol, Vol) 
        sqrt_log_term = np.sqrt(np.log(y11 / (y1 * y1)))
        vega_i = ((sumaF + aF_i) * Weight[i] * Forward[i] * np.exp(v * v * T[i]) * v * T[i]* np.exp(-r * T[n - 1]) * (PDF_ND1 / ((y11 / y1) * sqrt_log_term)))
        vega += vega_i
    return vega

def Arithmetic_Asian_Opt_Pricing(
    n, Forward, Weight, T, TermVol, Vol,
    PrevCummulative_Weight, Strike, PrevAverage,
    Call0Put1, T_Option, TermRate, Rate
):
    m1 = Arithmetic_Asian_Opt_m1(n, Weight, Forward)
    m2 = Arithmetic_Asian_Opt_m2(n, Forward, Weight, T, TermVol, Vol)
    m3 = Arithmetic_Asian_Opt_m3(n, Forward, Weight, T, TermVol, Vol)

    mu1 = m1
    mu2 = m2 - mu1 * mu1
    mu3 = m3 - 3.0 * mu1 * mu2 - mu1 ** 3

    z = (0.5 * mu3 + 0.5 * np.sqrt(mu3 * mu3 + 4.0 * mu2 ** 3)) ** (1.0 / 3.0)
    y1 = mu1  # original comment: mu2 / (z - mu2 / z)
    y11 = mu2 + y1 * y1
    E = mu1 - y1

    r_disc = np.interp(T_Option, TermRate, Rate)
    intrinsic = Strike - PrevCummulative_Weight * PrevAverage - E

    if intrinsic <= 0:
        if Call0Put1 == 0:  # Call
            value = np.exp(-r_disc * T_Option) * (y1 - intrinsic)
        else:  # Put
            value = 0.0
    else:
        d1 = np.log(np.sqrt(y11) / intrinsic) / np.sqrt(np.log(y11 / (y1 * y1)))
        d2 = d1 - np.sqrt(np.log(y11 / (y1 * y1)))

        if Call0Put1 == 0:  # Call
            value = np.exp(-r_disc * T_Option) * (y1 * CDF_N(d1) - intrinsic * CDF_N(d2))
        else:  # Put
            value = np.exp(-r_disc * T_Option) * (intrinsic * CDF_N(-d2) - y1 * CDF_N(-d1))

    delta = Arithmetic_Asian_Option_Delta(n, Forward, Weight, T, TermVol, Vol, r_disc, y1, y11, d1)
    vega = Arithmetic_Asian_Option_Vega(n, Forward, Weight, T, TermVol, Vol, r_disc, y1, y11, d1)
    return value, delta, vega

def Arithmetic_Asian_Opt_Pricing_Preprocessing(Long0Short1, Call0Put1, PriceDate, AverageStartDate, AverageEndDate, OptionMaturityDate, S, K, PrevAverage, DiscTerm, DiscRate, DivTerm, DivRate, QuantoCorr, FXVolTerm, FXVol, VolTerm, VolParity, Vols2D, DivTypeFlag, Holidays, ForwardTerm = [], ForwardPrice = []) : 
    T_Opt = DayCountAtoB(PriceDate, OptionMaturityDate)/365
    PrevCummulativeWeight = 0
    NDays = DayCountAtoB(AverageStartDate, AverageEndDate) + 1
    StartDateExcel = YYYYMMDDToExcelDate(AverageStartDate)
    N_BD_Avg = 0
    for i in range(NDays) : 
        MOD7 = (StartDateExcel + i) % 7
        YYYYMMDD = ExcelDateToYYYYMMDD(StartDateExcel + i)
        isHolidayFlag = YYYYMMDD in Holidays
        if ((MOD7 == 1 or MOD7 == 0) or isHolidayFlag == 1) :
            SaturSundayFlag = 1
        else : 
            SaturSundayFlag = 0
        
        if SaturSundayFlag != 1 : 
            N_BD_Avg += 1
    
    AvgDate = np.zeros(max(1, NDays))
    j = 0
    for i in range(NDays) : 
        MOD7 = (StartDateExcel + i) % 7
        YYYYMMDD = ExcelDateToYYYYMMDD(StartDateExcel + i)
        isHolidayFlag = YYYYMMDD in Holidays
        if ((MOD7 == 1 or MOD7 == 0) or isHolidayFlag == 1) :
            SaturSundayFlag = 1
        else : 
            SaturSundayFlag = 0
        
        if SaturSundayFlag != 1 : 
            AvgDate[j] = YYYYMMDD
            j += 1
            
    NPrev, NForward = 0, 0
    for i in range(N_BD_Avg) : 
        if AvgDate[i] <= PriceDate : 
            NPrev += 1
        else : 
            NForward += 1
    
    ForwardDate = np.zeros(max(1, NForward))
    j = 0
    for i in range(N_BD_Avg) : 
        if AvgDate[i] > PriceDate : 
            ForwardDate[j] = AvgDate[i]
            j += 1    
    
    w = 1/N_BD_Avg
    Weight = np.array([w] * NForward)
    PrevCummulativeWeight = NPrev/N_BD_Avg
    TimeAry = np.vectorize(DayCountAtoB)([PriceDate],ForwardDate)/365
    if len(ForwardTerm) == 0 : 
        R_Ref = np.interp(TimeAry, DiscTerm, DiscRate)
    else : 
        Preprocessing_Term(ForwardTerm, PriceDate)
        RefTerm = ForwardTerm
        RefRate = (TimeAry[i] > 0) * np.log(np.array(ForwardPrice)/S)/ForwardTerm 
        R_Ref = np.interp(TimeAry, RefTerm, RefRate)       
         
    DivAry = np.interp(TimeAry, DivTerm, DivRate)
    FXVolAry = np.interp(TimeAry, FXVolTerm, FXVol) if len(FXVolTerm) > 0 else 0

    if isinstance(Vols2D, float) :
        Vol = np.array([Vols2D] * NForward)
    else : 
        TempFunc = np.vectorize(lambda Times : Linterp2D(VolTerm, VolParity, Vols2D, Times, K/S))
        Vol = TempFunc(TimeAry)
    Forward = S * np.exp((R_Ref - DivAry - (abs(QuantoCorr) > 0.0001) * QuantoCorr * FXVolAry * Vol) * TimeAry)
    price, delta, vega = Arithmetic_Asian_Opt_Pricing(NForward, Forward, Weight, TimeAry, TimeAry, Vol, PrevCummulativeWeight, K, PrevAverage, Call0Put1, T_Opt, DiscTerm, DiscRate)
    priceu, deltau, vegau = Arithmetic_Asian_Opt_Pricing(NForward, Forward * 1.01, Weight, TimeAry, TimeAry, Vol, PrevCummulativeWeight, K, PrevAverage, Call0Put1, T_Opt, DiscTerm, DiscRate)
    gamma = (deltau - delta) / (S * 0.01)
    if Long0Short1 == 0 : 
        return price, delta, gamma, vega, 0, 0, Vol.mean()        
    else : 
        return -price, -delta, -gamma, -vega, 0, 0, Vol.mean()        
        
def BS_Swaption(PriceDate, StartDate, SwapTenorT, NCpnOneYear, Notional, Vol, StrikePrice, Term, Rate, DayCountFracFlag = 0, VolFlag = 0, HolidaysFixing = [], HolidaysPay = [], NBDayFromEndDateToPay = 0, FixedPayer0Receiver1 = 0) : 
    FixedPayerFlag = FixedPayer0Receiver1
    if StrikePrice > 1.0 : 
        StrikePrice /= 100
    
    if (PriceDate < 19000101) :
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    
    if (StartDate < 19000101) : 
        StartDate = ExcelDateToYYYYMMDD(StartDate)

    Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)

    T_Option = float(DayCountAtoB(PriceDate, StartDate))/365
    if (SwapTenorT < 10000) : 
        SwapMaturity = EDate_YYYYMMDD(StartDate, int(SwapTenorT * 12 + 0.00001))
    elif (SwapTenorT < 19000101) : 
        SwapMaturity = ExcelDateToYYYYMMDD(SwapTenorT)
    else : 
        SwapMaturity = SwapTenorT
     
    Start, End, Pay, NBD = MappingCouponDates(1,StartDate,SwapMaturity,NBDayFromEndDateToPay, NCpnOneYear,1,HolidaysFixing,HolidaysPay,1) 
    T_Option = max(0.0000285388, T_Option)
    ForwardSwapRate = FSR(PriceDate, StartDate,SwapMaturity, NCpnOneYear, DayCountFracFlag, HolidaysFixing, Term, Rate, Term, Rate)        
    annuity = 0
    for i in range(len(End)) : 
        if i == 0 : 
            dt = DayCountFractionAtoB(StartDate, End[i], DayCountFracFlag, HolidaysPay)
        else : 
            dt = DayCountFractionAtoB(End[i-1], End[i], DayCountFracFlag, HolidaysPay)
        t_pay = (float(DayCountAtoB(PriceDate, Pay[i] if NBDayFromEndDateToPay > 0 else End[i]))) / 365.0
        annuity += dt * Calc_Discount_Factor(Term, Rate, t_pay)
    
    value, value_atm = 0,0
    if (VolFlag == 0) : 
        d1 = (np.log(ForwardSwapRate / StrikePrice) + 0.5 * Vol * Vol * T_Option) / (Vol * np.sqrt(T_Option))
        d2 = d1 - Vol * np.sqrt(T_Option)

        d1_atm = 0.5 * Vol * np.sqrt(T_Option)
        d2_atm = -0.5 * Vol * np.sqrt(T_Option)
        if (PriceDate != StartDate) :
            if (FixedPayerFlag == 0) : 
                value = max(annuity * (ForwardSwapRate * CDF_N(d1) - StrikePrice * CDF_N(d2)), 0.0)
                value_atm = annuity * (ForwardSwapRate * CDF_N(d1_atm) - ForwardSwapRate * CDF_N(d2_atm))
            else :                 
                value = max(annuity * (-ForwardSwapRate * CDF_N(-d1) + StrikePrice * CDF_N(-d2)), 0.0)
                value_atm = annuity * (-ForwardSwapRate * CDF_N(-d1_atm) + ForwardSwapRate * CDF_N(-d2_atm))
        else : 
            if (FixedPayerFlag == 0) : 
                value = annuity * max(ForwardSwapRate - StrikePrice, 0.0)
                value_atm = 0.0
            else :
                value = annuity * max(-ForwardSwapRate + StrikePrice, 0.0)
                value_atm = 0.0
    else : 
        d1 = (ForwardSwapRate - StrikePrice) / (Vol * np.sqrt(T_Option))
        d1_atm = 0.0
        if (PriceDate != StartDate) :
            if (FixedPayerFlag == 0) : 
                value = max(annuity * ((ForwardSwapRate - StrikePrice) * CDF_N(d1) + Vol * np.sqrt(T_Option) * (np.exp(-d1 * d1 / 2.0) / 2.506628274631)), 0.0)
                value_atm = annuity * Vol * np.sqrt(T_Option) * (np.exp(-d1_atm * d1_atm / 2.0) / 2.506628274631)
            else :                 
                c_value = max(annuity * ((ForwardSwapRate - StrikePrice) * CDF_N(d1) + Vol * np.sqrt(T_Option) * (np.exp(-d1 * d1 / 2.0) / 2.506628274631)), 0.0)
                value_atm = annuity * Vol * np.sqrt(T_Option) * (np.exp(-d1_atm * d1_atm / 2.0) / 2.506628274631)
                value = max(0.0 , annuity * (StrikePrice - ForwardSwapRate) + c_value)
        else : 
            if (FixedPayerFlag == 0) : 
                value = annuity * max(ForwardSwapRate - StrikePrice, 0.0)
            else :             
                value = annuity * max(-ForwardSwapRate + StrikePrice, 0.0)
            value_atm = 0

    ExerciseValue = (ForwardSwapRate - StrikePrice) * annuity
    MyDict = {"Price":Notional * value,"Value":Notional*(value - value_atm), "ForwardSwapRate":ForwardSwapRate,"ExerciseValue":ExerciseValue}
    return MyDict

def calc_mu(b, sigma):
    return (b - 0.5 * sigma ** 2) / (sigma ** 2)

def calc_lambda(mu, r, sigma):
    return np.sqrt(mu ** 2 + 2.0 * r / (sigma ** 2))

def calc_z(H, K, sigma, T, Lambda):
    return np.log(H / K) / (sigma * np.sqrt(T)) + Lambda * sigma * np.sqrt(T)

def calc_x1(S, K, sigma, T, mu):
    return np.log(S / K) / (sigma * np.sqrt(T)) + (1.0 + mu) * sigma * np.sqrt(T)

def calc_x2(S, H, sigma, T, mu):
    return np.log(S / H) / (sigma * np.sqrt(T)) + (1.0 + mu) * sigma * np.sqrt(T)

def calc_y1(S, H, K, sigma, T, mu):
    return np.log(H * H / (S * K)) / (sigma * np.sqrt(T)) + (1.0 + mu) * sigma * np.sqrt(T)

def calc_y2(S, H, sigma, T, mu):
    return np.log(H / S) / (sigma * np.sqrt(T)) + (1.0 + mu) * sigma * np.sqrt(T)

def calc_A(phi, S, b, T, x1, X, r, sigma):
    return phi * S * np.exp((b - r) * T) * CDF_N(phi * x1) - phi * X * np.exp(-r * T) * CDF_N(phi * x1 - phi * sigma * np.sqrt(T))

def calc_B(phi, S, b, T, x2, K, r, sigma):
    return phi * S * np.exp((b - r) * T) * CDF_N(phi * x2) - phi * K * np.exp(-r * T) * CDF_N(phi * x2 - phi * sigma * np.sqrt(T))

def calc_C(phi, S, b, T, H, mu, n, y1, K, r, sigma):
    return phi * S * np.exp((b - r) * T) * (H / S) ** (2 * (mu + 1.0)) * CDF_N(n * y1) - phi * K * np.exp(-r * T) * (H / S) ** (2 * mu) * CDF_N(n * y1 - n * sigma * np.sqrt(T))

def calc_D(phi, S, b, T, H, mu, n, y2, K, r, sigma):
    return phi * S * np.exp((b - r) * T) * (H / S) ** (2 * (mu + 1.0)) * CDF_N(n * y2) - phi * K * np.exp(-r * T) * (H / S) ** (2 * mu) * CDF_N(n * y2 - n * sigma * np.sqrt(T))

def calc_E(Reb, r, T, n, x2, sigma, H, S, mu, y2):
    return Reb * np.exp(-r * T) * (CDF_N(n * x2 - n * sigma * np.sqrt(T)) - (H / S) ** (2.0 * mu) * CDF_N(n * y2 - n * np.sqrt(T)))

def calc_F(Reb, H, S, mu, Lambda, n, z, sigma, T):
    return Reb * ((H / S) ** (mu + Lambda) * CDF_N(n * z) + (H / S) ** (mu - Lambda) * CDF_N(n * z - 2.0 * n * Lambda * sigma * np.sqrt(T)))

def C_out(n, x1, x2, y1, y2, A, B, C, D, S, X, H):
    if n == 1:
        return A - C if X > H else B - D
    else:
        return 0.0 if X > H else A - B + C - D

def P_out(n, x1, x2, y1, y2, A, B, C, D, S, X, H):
    if n == 1:
        return A - B + C - D if X > H else 0.0
    else:
        return B - D if X > H else A - C

def SimpleBSCall(S, K, b, T, q, r, sigma):
    d1 = (np.log(S / K) + (b + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * np.exp((b - r - q) * T) * CDF_N(d1) - K * np.exp(-r * T) * CDF_N(d2)

def SimpleBSPut(S, K, b, T, q, r, sigma):
    d1 = (np.log(S / K) + (b + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * CDF_N(-d2) - S * np.exp((b - r - q) * T) * CDF_N(-d1)

def Call_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb = 0, LoggingFlag = 0, LoggingDir = ''):
    Sigma, r, phi, n = sig, r_disc, 1, 1
    b = r_ref - rho_fx * fxvol * sig - (0 if DiscreteDivFlag == 1 else div)
    if DiscreteDivFlag == 1:
        S -= div

    mu = calc_mu(b, Sigma)
    lambda_ = calc_lambda(mu, r, Sigma)
    z = calc_z(H, X, Sigma, T, lambda_)
    x1, x2 = calc_x1(S, X, Sigma, T, mu), calc_x2(S, H, Sigma, T, mu)
    y1, y2 = calc_y1(S, H, X, Sigma, T, mu), calc_y2(S, H, Sigma, T, mu)

    A = calc_A(phi, S, b, T, x1, X, r, Sigma)
    B = calc_B(phi, S, b, T, x2, X, r, Sigma)
    C = calc_C(phi, S, b, T, H, mu, n, y1, X, r, Sigma)
    D = calc_D(phi, S, b, T, H, mu, n, y2, X, r, Sigma)
    E = calc_E(Reb, r, T, n, x2, Sigma, H, S, mu, y2) if Reb != 0 else 0
    F = calc_F(Reb, H, S, mu, lambda_, n, z, Sigma, T) if Reb != 0 else 0

    c_do = A - C + F if X > H else B - D + F
    c_di = SimpleBSCall(S, X, b, T, div if DiscreteDivFlag == 0 else 0, r, Sigma) - c_do
    Price = c_di if in0out1flag == 0 else c_do 
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[Price, T, S, X, b, sig, A,B,C,D,E,F]], 
                               columns = ["Price","T", "S", "X", "b", "sig", "A","B","C","D","E","F"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)

    return c_di if in0out1flag == 0 else c_do

def Put_Down(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb = 0, LoggingFlag = 0, LoggingDir = ''):
    Sigma, r, phi, n = sig, r_disc, -1, 1
    b = r_ref - rho_fx * fxvol * sig - (0 if DiscreteDivFlag == 1 else div)
    if DiscreteDivFlag == 1:
        S -= div

    mu = calc_mu(b, Sigma)
    lambda_ = calc_lambda(mu, r, Sigma)
    z = calc_z(H, X, Sigma, T, lambda_)
    x1, x2 = calc_x1(S, X, Sigma, T, mu), calc_x2(S, H, Sigma, T, mu)
    y1, y2 = calc_y1(S, H, X, Sigma, T, mu), calc_y2(S, H, Sigma, T, mu)

    A = calc_A(phi, S, b, T, x1, X, r, Sigma)
    B = calc_B(phi, S, b, T, x2, X, r, Sigma)
    C = calc_C(phi, S, b, T, H, mu, n, y1, X, r, Sigma)
    D = calc_D(phi, S, b, T, H, mu, n, y2, X, r, Sigma)
    E = calc_E(Reb, r, T, n, x2, Sigma, H, S, mu, y2) if Reb != 0 else 0
    F = calc_F(Reb, H, S, mu, lambda_, n, z, Sigma, T) if Reb != 0 else 0

    p_do = A - B + C - D + F if X > H else F
    p_di = SimpleBSPut(S, X, b, T, div if DiscreteDivFlag == 0 else 0, r, Sigma) - p_do
    Price = p_di if in0out1flag == 0 else p_do
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[Price, T, S, X, b, sig, A,B,C,D,E,F]], 
                               columns = ["Price","T", "S", "X", "b", "sig", "A","B","C","D","E","F"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)

    return p_di if in0out1flag == 0 else p_do

def Call_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb = 0, LoggingFlag = 0, LoggingDir = ''):
    Sigma, r, phi, n = sig, r_disc, 1, -1
    b = r_ref - rho_fx * fxvol * sig - (0 if DiscreteDivFlag == 1 else div)
    if DiscreteDivFlag == 1:
        S -= div

    mu = calc_mu(b, Sigma)
    lambda_ = calc_lambda(mu, r, Sigma)
    z = calc_z(H, X, Sigma, T, lambda_)
    x1, x2 = calc_x1(S, X, Sigma, T, mu), calc_x2(S, H, Sigma, T, mu)
    y1, y2 = calc_y1(S, H, X, Sigma, T, mu), calc_y2(S, H, Sigma, T, mu)

    A = calc_A(phi, S, b, T, x1, X, r, Sigma)
    B = calc_B(phi, S, b, T, x2, X, r, Sigma)
    C = calc_C(phi, S, b, T, H, mu, n, y1, X, r, Sigma)
    D = calc_D(phi, S, b, T, H, mu, n, y2, X, r, Sigma)
    E = calc_E(Reb, r, T, n, x2, Sigma, H, S, mu, y2) if Reb != 0 else 0
    F = calc_F(Reb, H, S, mu, lambda_, n, z, Sigma, T) if Reb != 0 else 0

    c_uo = F if X > H else A - B + C - D + F
    c_ui = SimpleBSCall(S, X, b, T, div if DiscreteDivFlag == 0 else 0, r, Sigma) - c_uo
    Price = c_ui if in0out1flag == 0 else c_uo
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[Price, T, S, X, b, sig, A,B,C,D,E,F]], 
                               columns = ["Price","T", "S", "X", "b", "sig", "A","B","C","D","E","F"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)
    
    return c_ui if in0out1flag == 0 else c_uo

def Put_Up(in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb = 0, LoggingFlag = 0, LoggingDir = ''):
    Sigma, r, phi, n = sig, r_disc, -1, -1
    b = r_ref - rho_fx * fxvol * sig - (0 if DiscreteDivFlag == 1 else div)
    if DiscreteDivFlag == 1:
        S -= div

    mu = calc_mu(b, Sigma)
    lambda_ = calc_lambda(mu, r, Sigma)
    z = calc_z(H, X, Sigma, T, lambda_)
    x1, x2 = calc_x1(S, X, Sigma, T, mu), calc_x2(S, H, Sigma, T, mu)
    y1, y2 = calc_y1(S, H, X, Sigma, T, mu), calc_y2(S, H, Sigma, T, mu)

    A = calc_A(phi, S, b, T, x1, X, r, Sigma)
    B = calc_B(phi, S, b, T, x2, X, r, Sigma)
    C = calc_C(phi, S, b, T, H, mu, n, y1, X, r, Sigma)
    D = calc_D(phi, S, b, T, H, mu, n, y2, X, r, Sigma)
    E = calc_E(Reb, r, T, n, x2, Sigma, H, S, mu, y2) if Reb != 0 else 0
    F = calc_F(Reb, H, S, mu, lambda_, n, z, Sigma, T) if Reb != 0 else 0

    p_uo = B - D + F if X > H else A - C + F
    p_ui = SimpleBSPut(S, X, b, T, div if DiscreteDivFlag == 0 else 0, r, Sigma) - p_uo
    Price = p_ui if in0out1flag == 0 else p_uo
    if LoggingFlag > 0 : 
        LogData = pd.DataFrame([[Price, T, S, X, b, sig, A,B,C,D,E,F]], 
                               columns = ["Price","T", "S", "X", "b", "sig", "A","B","C","D","E","F"])
        LogData.to_csv(LoggingDir + "\\LoggingFilesOption.csv",encoding = "cp949", index = False)
    
    return p_ui if in0out1flag == 0 else p_uo

def BarrierOptionGreek(
    in0out1flag, S, X, H, T, r_disc, r_ref, rho_fx, fxvol,
    DiscreteDivFlag, div, sig, Reb, pricing_function
):
    Su = S * 1.01
    Sd = S * 0.99
    dS = S * 0.01

    Pu = pricing_function(in0out1flag, Su, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Pd = pricing_function(in0out1flag, Sd, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    P = pricing_function(in0out1flag, S, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    sigu = sig + 0.01
    sigd = max(sig - 0.01,0.00001)
    Delta = (Pu - Pd) / (2.0 * dS) 
    Gamma = (Pu + Pd -2.0 * P) / (dS * dS)
    Pvu = pricing_function(in0out1flag, S, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sigu, Reb)
    Pvd = pricing_function(in0out1flag, S, X, H, T, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sigd, Reb)
    Vega = (Pvu - Pvd) / ((sigu-sigd))
    Pru = pricing_function(in0out1flag, S, X, H, T, r_disc+0.0001, r_ref+0.0001,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Prd = pricing_function(in0out1flag, S, X, H, T, r_disc-0.0001, r_ref-0.0001,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Rho = (Pru - Prd) / (0.0001 * 2)
    T_u = T + 1.0 / 365.0
    T_d = max(T - 1.0 / 365.0,0.00001)
    Ptu = pricing_function(in0out1flag, S, X, H, T_u, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Ptd = pricing_function(in0out1flag, S, X, H, T_d, r_disc, r_ref,
                          rho_fx, fxvol, DiscreteDivFlag, div, sig, Reb)
    Theta = (Ptu - Ptd) / (T_u-T_d)
    return Delta, Gamma, Vega, Theta, Rho

def BSBarrierOption(PriceDate, Call1Put2, S0, X, H, ZeroDiscTerm, 
                    ZeroDiscRate, ZeroRefTerm, ZeroRefRate, DivTerm, DivRate, 
                    QuantoCorr, FXVolTerm, FXVol, VolTerm, VolParity, 
                    Vols2D, DivType, Maturity, PayDate, Down0Up1Flag, In0Out1Flag, Reb = 0, ForwardPrice = 0, LoggingFlag = 0, LoggingDir = os.getcwd()) : 
    Preprocessing_ZeroTermAndRate(ZeroDiscTerm, ZeroDiscRate, PriceDate)
    if isinstance(Vols2D, float) == False : 
        if len(np.array(Vols2D).shape) == 2 : 
            Preprocessing_EQVol(VolParity, VolTerm, Vols2D, PriceDate, S0)
        else : 
            Vols1D = np.array(Vols2D).reshape(-1)
            Preprocessing_ZeroTermAndRate(VolTerm, Vols1D, PriceDate, 6)
            Vols2D = Vols1D.reshape(1,-1)
            VolParity = [1]
    TEnd = DayCountAtoB(PriceDate, Maturity)/365
    TPay = max(TEnd, DayCountAtoB(PriceDate, PayDate)/365)
    
    TEnd = max(0.00001, TEnd)
    TPay = max(0.00001, TPay)
    fdf = Calc_ForwardDiscount_Factor(ZeroDiscTerm, ZeroDiscRate, TEnd, TPay) if TEnd != TPay else 1
    if (DivType == 0) : 
        dvd = DivRate[0] if ForwardPrice <= 0 else 0
    elif (DivType == 1) : 
        dvd = np.interp(TEnd, DivTerm, DivRate) if ForwardPrice <= 0 else 0
    else : 
        td = np.array(DivTerm)
        dr = np.array(DivRate)
        idx = td <= TEnd
        dvd = 1/TEnd * dr[idx].sum() / S0 if ForwardPrice <= 0 else 0
        
    if isinstance(Vols2D, float) : 
        vol = Vols2D
    else : 
        vol = Linterp2D(VolTerm, VolParity, Vols2D, TEnd, X/S0 if np.array(VolParity).max() < 2.0 else S0)
    
    fxv = np.interp(TEnd, FXVolTerm, FXVol) if len(FXVolTerm) > 0 else 0
    rd = np.interp(TEnd, ZeroDiscTerm, ZeroDiscRate)
    if ForwardPrice > 0 : 
        rf = 1/TEnd * np.log(ForwardPrice/S0)
    else : 
        if len(ZeroRefTerm) > 0 :
            rf = np.interp(TEnd, ZeroRefTerm, ZeroRefRate)
        else : 
            rf = rd

    DiscreteDivFlag = 0 if DivType != 2 else 1
    if Call1Put2 == 1 : 
        if Down0Up1Flag == 0 : 
            PricingFunction = Call_Down
        else : 
            PricingFunction = Call_Up                        
    else : 
        if Down0Up1Flag == 0 : 
            PricingFunction = Put_Down            
        else : 
            PricingFunction = Put_Up            
    P = PricingFunction(In0Out1Flag, S0, X, H, TEnd, rd, rf, QuantoCorr, fxv, DiscreteDivFlag, dvd, vol, Reb,LoggingFlag, LoggingDir)                        
    Delta, Gamma, Vega, Theta, Rho = BarrierOptionGreek(In0Out1Flag, S0, X, H, TEnd, rd, rf, QuantoCorr, fxv, DiscreteDivFlag, dvd, vol, Reb, PricingFunction)

    return P*fdf, Delta*fdf, Gamma*fdf, Vega*fdf, Theta*fdf, Rho*fdf, vol

def HW_Integral_ShortRate_Vol(t, A, kappa, tVol, Vol) : 
    '''
    Calculate Volatility of Integral ShortRate from 0 to t
    I(t) = Int_0^t sigma(s)^2 A exp(ks) ds
    '''
    NodeNumber = 10.0
    ds = t/NodeNumber
    value = 0.0
    nVol = len(tVol)
    if nVol == 1 :
        value = A * Vol[0] * Vol[0] / (kappa) * (np.exp(kappa * t) - 1.0)
    else : 
        #for i in range(nVol) : 
        #    s = float(i+1) * ds
        #    v = np.interp(s, tVol, Vol)
        #    print(v)
        #    value += v * v * A * np.exp(kappa * s) * ds
        NodeNumber = 10
        Node = np.linspace(0, t, NodeNumber+1)
        u = (Node[1:] + Node[:-1])/2
        du = Node[1:] - Node[:-1]
        MyFunc = np.vectorize(lambda t : Linterp(tVol, Vol, t, 1))
        v = MyFunc(u)
        value = (v * v * A * np.exp(kappa * u) * du).sum()        
    return value 

def B_s_to_t(s, t, kappa) : 
    return (1.0 - np.exp(-kappa * (t-s)))/kappa if kappa != 0 else 1

def V_t_T(k1, k2, t, T, v1, v2) : 
    return v1 * v2 / (k1 * k2) * (T - t + (np.exp(-k1 * (T-t)) - 1.0)/k1 + (np.exp(-k2 * (T-t)) - 1.0)/k2 - (np.exp(-(k1+k2)*(T-t))-1.0)/(k1+k2))

#def V_t_T2(k1, k2, t, T, tVol1, Vol1, tVol2, Vol2) : 
#    NInteg = 10
#    MySpace = np.linspace(0, t, NInteg + 1)
#    u = (MySpace[:-1] + MySpace[1:])/2
#    v1 = np.interp(u, tVol1, Vol1)
#    v2 = np.interp(u, tVol2, Vol2)
#    du = MySpace[1:] - MySpace[:-1]
#    Bst1 = B_s_to_t(u, t, k1)
#    Bst2 = B_s_to_t(u, t, k2)
#    BsT1 = B_s_to_t(u, T, k1)
#    BsT2 = B_s_to_t(u, T, k2)
#    RHS = (v1 * v2 * (Bst1 * Bst2 - BsT1 * BsT2) * du).sum()
#    #RHS = (v1 * v2 * (1-np.exp(-k1 * (T-u)))/k1 * (1-np.exp(-k2 * (T-u)))/k2 * du).sum()
#    return RHS

def V_t_T2(k1, k2, t, T, tVol1, Vol1, tVol2, Vol2) : 
    NInteg = 10
    MySpace = np.linspace(t, T, NInteg + 1)
    u = (MySpace[:-1] + MySpace[1:])/2
    v1 = np.interp(u, tVol1, Vol1)
    v2 = np.interp(u, tVol2, Vol2)
    du = MySpace[1:] - MySpace[:-1]
    RHS = (v1 * v2 * (1-np.exp(-k1 * (T-u)))/k1 * (1-np.exp(-k2 * (T-u)))/k2 * du).sum()
    return RHS

def hw_variance_closed_form(alpha, sigma, t, T):
    if alpha <= 0:
        raise ValueError("Alpha must be positive")

    term1 = (1 - np.exp(-alpha * t)) / alpha
    term2 = (np.exp(-alpha * (T - t)) - np.exp(-alpha * T)) / alpha
    term3 = (1 - np.exp(-2 * alpha * t)) / (2 * alpha)
    term4 = (np.exp(-2 * alpha * (T - t)) - np.exp(-2 * alpha * T)) / (2 * alpha)

    result = (sigma ** 2 / alpha ** 2) * (-2 * (term1 - term2) + (term3 - term4))
    return result

#def HWQVTerm(t, T, kappa, HWVolTerm, HWVol) : 
#    RHS = 0
#    if len(HWVol) == 1 or kappa > 0.25 : 
#        v = np.interp(t, HWVolTerm, HWVol)
#        RHS = 0.5 * (hw_variance_closed_form(kappa, VegaRiskWeight, t, T))
#    else : 
#        RHS = 0.5 * V_t_T2(kappa, kappa, t, T, HWVolTerm, HWVol, HWVolTerm, HWVol)
#    return RHS        

def HWQVTerm(t, T, kappa, HWVolTerm, HWVol) : 
    RHS = 0
    if len(HWVol) == 1 or kappa > 0.25 : 
        v = np.interp((t+T)/2, HWVolTerm, HWVol)
        V_1 = V_t_T(kappa, kappa, t, T, v, v)
        V_2 = V_t_T(kappa, kappa, 0, T, v, v)
        V_3 = V_t_T(kappa, kappa, 0, t, v, v)
        RHS = 0.5 * (V_1)
    else : 
        V_1 = V_t_T2(kappa, kappa, t, T, HWVolTerm, HWVol, HWVolTerm, HWVol)
        V_2 = V_t_T2(kappa, kappa, 0, T, HWVolTerm, HWVol, HWVolTerm, HWVol)
        V_3 = V_t_T2(kappa, kappa, 0, t, HWVolTerm, HWVol, HWVolTerm, HWVol)
        RHS = 0.5 * (V_1)
    return RHS 

def HWCrossTerm(t, T, kappa1, kappa2, HWVolTerm1, HWVol1, HWVolTerm2, HWVol2, rho) : 
    RHS = 0
    if (len(HWVol1) == 1 and len(HWVol1) == 1) or kappa1 > 0.25 : 
        v1 = np.interp((t+T)/2, HWVolTerm1, HWVol1)
        v2 = np.interp((t+T)/2, HWVolTerm2, HWVol2)
        V_1 = V_t_T(kappa1, kappa2, t, T, v1, v2)
        V_2 = V_t_T(kappa1, kappa2, 0, T, v1, v2)
        V_3 = V_t_T(kappa1, kappa2, 0, t, v1, v2)
        RHS = 2.0 * rho * 0.5 * (V_1)
    else : 
        V_1 = V_t_T2(kappa1, kappa2, t, T, HWVolTerm1, HWVol1, HWVolTerm2, HWVol2)
        V_2 = V_t_T2(kappa1, kappa2, 0, T, HWVolTerm1, HWVol1, HWVolTerm2, HWVol2)
        V_3 = V_t_T2(kappa1, kappa2, 0, t, HWVolTerm1, HWVol1, HWVolTerm2, HWVol2)
        RHS = 2.0 * rho * 0.5 * (V_1)
    return RHS     

def HullWhite_A_t_T_1F(DF_0_t_T, t, T, kappa, HWVolTerm, HWVol) : 
    return DF_0_t_T * np.exp(HWQVTerm(t, T, kappa, HWVolTerm, HWVol))        

def HullWhite1F_DiscFactor_t_T(BtT, xt, A_t_T_1F) : 
    return np.exp(-xt * BtT) * A_t_T_1F

def HullWhite2F_DiscFactor_t_T_2F(BtTxt, BtTyt, xt, yt, A_t_T_xt, A_t_T_yt, hwcross) : 
    return np.exp(-xt * BtTxt - yt * BtTyt + hwcross) *  A_t_T_xt *  A_t_T_yt

def XV(kappa, tVol, Vol, t, T) : 
    if len(tVol) == 1 : 
        time = (t+T)/2
        v = np.interp(time, tVol, Vol)
        return np.sqrt(v * v * 0.5 / kappa * (1.0 - np.exp(-2.0 * kappa * (T - t))))
    else : 
        NInteg = 10
        MySpace = np.linspace(t, T, NInteg + 1)
        u = (MySpace[:-1] + MySpace[1:])/2
        v = np.interp(u, tVol, Vol)
        du = MySpace[1:] - MySpace[:-1]
        return np.sqrt((v * v * np.exp(-2.0 * kappa * (T - u)) * du).sum(0))                

def XA(kappa, t, T) : 
    return np.exp(-kappa * (T-t))

def SimulateXt(xt, xa, xv, eps) : 
    return xt * xa + eps * xv

def HW_Swaption(NA, kappa, tVol, Vol, Term, Rate, StrikePrice, T_SwapStartDate, TArray_of_CpnDate) : 
    tVol = np.array(tVol, dtype = np.float64)
    Vol = np.array(Vol, dtype = np.float64)
    TempInterpFunc = np.vectorize(lambda x : Linterp(Term, Rate, x))
    t = np.array([T_SwapStartDate] + list(TArray_of_CpnDate), dtype = np.float64)
    r = TempInterpFunc(t)
    DF = np.exp(-r * t)

    Vol = np.maximum(0.000001, Vol)
    VT0 = np.exp(-2.0 * kappa * T_SwapStartDate) * HW_Integral_ShortRate_Vol(T_SwapStartDate, 1, 2.0 * kappa, tVol, Vol)
    deltaT = t[1:] - t[:-1]
    G = (DF[-1] + (DF[1:] * deltaT * StrikePrice).sum())/DF[0]

    TempFunction2 = np.vectorize(lambda x : B_s_to_t(T_SwapStartDate, x, kappa))
    H = (DF[-1] * B_s_to_t(T_SwapStartDate, TArray_of_CpnDate[-1], kappa) + (StrikePrice * deltaT * DF[1:] * TempFunction2(TArray_of_CpnDate)).sum())/(G * DF[0])
    d1 = -np.log(G) / (H * np.sqrt(VT0)) + 0.5 * H * np.sqrt(VT0)
    d2 = -np.log(G) / (H * np.sqrt(VT0)) - 0.5 * H * np.sqrt(VT0)

    value = DF[0] * (CDF_N(d1) - G * CDF_N(d2))
    return NA * value

def SimulateShortRateMC(NSimul, SimulationDateList, PriceDate, kappa, HWVolTerm, HWVol) : 
    np.random.seed(1)
    Rndn = np.random.normal(0,1,size = (len(SimulationDateList),NSimul))
    t1 = np.vectorize(DayCountAtoB)(PriceDate, SimulationDateList)/365
    X_A0 = XA(kappa, 0, t1[0])
    X_V0 = XV(kappa, HWVolTerm, HWVol, 0, t1[0])
    X_A = XA(kappa, t1[:-1], t1[1:])
    X_V = XV(kappa, HWVolTerm, HWVol, t1[:-1], t1[1:])
    SimulatedXt = SimulateXt(0, X_A0, X_V0, Rndn[0]).reshape(1,-1)
    for i in range(len(SimulationDateList) - 1) :
        prevx = SimulatedXt[i]
        SimulatedXt = np.concatenate([SimulatedXt, SimulateXt(prevx, X_A[i], X_V[i], Rndn[i+1]).reshape(1,-1)],axis = 0)
    return SimulatedXt

def SimulateParRateMC(PriceDate, SimulatedXt2D, SimulationDateList, RefSwapMaturity_T, RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, ZeroTerm, ZeroRate) :
    EachSwapMaturityInSimulation = np.vectorize(EDate_YYYYMMDD)(SimulationDateList, int(RefSwapMaturity_T * 12 + 0.0001))
    CpnDateListInSimul = []
    for i in range(len(SimulationDateList)) : 
        CpnDateListInSimul.append(np.array(malloc_cpn_date_holiday(SimulationDateList[i], EachSwapMaturityInSimulation[i], RefSwapNCPNOneYear)[0]).reshape(1,-1))
    CpnDateArrayForEachSimulDate = np.concatenate(CpnDateListInSimul, axis = 0)

    t1 = np.vectorize(DayCountAtoB)(PriceDate, SimulationDateList)/365
    t2 = np.vectorize(DayCountAtoB)(PriceDate, CpnDateArrayForEachSimulDate)/365
    r1 = np.interp(t1, ZeroTerm, ZeroRate)
    r2 = np.interp(t2, ZeroTerm, ZeroRate)
    df1 = np.exp(-r1 * t1)
    df2 = np.exp(-r2 * t2)
    df_t_T = df2/df1.reshape(-1,1)
    MyFunc = np.vectorize(lambda DF_0_t_T, t, T: HullWhite_A_t_T_1F(DF_0_t_T, t, T, kappa, HWVolTerm, HWVol))
    A_t_T = MyFunc(df_t_T, t1.reshape(-1,1), t2) 
    B_t_T = B_s_to_t(t1.reshape(-1,1), t2, kappa)

    deltat = np.concatenate([(t2[:,0] - t1).reshape(-1,1), (t2[:,1:] - t2[:,:-1])], axis = 1)
    
    deltat3D = deltat.reshape(deltat.shape[0], deltat.shape[1], 1)
    B_t_T3D = B_t_T.reshape(B_t_T.shape[0], B_t_T.shape[1], 1)
    A_t_T3D = A_t_T.reshape(A_t_T.shape[0], A_t_T.shape[1], 1)

    SimulatedXt3D = SimulatedXt2D.reshape(len(SimulationDateList), 1, -1)
    Disc = HullWhite1F_DiscFactor_t_T(B_t_T3D, SimulatedXt3D, A_t_T3D)

    SwapRate = (1-Disc[:,-1,:])/(Disc * deltat3D).sum(1)    
    SwapRateForwardMeasure = (1-df_t_T[:,-1])/(df_t_T * deltat).sum(1)
    
    if df_t_T.shape[1] > 1 : 
        MyFuncTemp = np.vectorize(lambda CpnRateList, YTMList, StartDateList, EndDateList : GPrimePrime_Over_GPrime(CpnRateList, YTMList, StartDateList, EndDateList, RefSwapNCPNOneYear))
        GppOvGp = MyFuncTemp(SwapRateForwardMeasure, SwapRateForwardMeasure, np.array(SimulationDateList), EachSwapMaturityInSimulation)
        v = np.interp(t1, HWVolTerm, HWVol)
        ConvAdjAmt = GppOvGp * v * v * 100. * t1 * 0.5    
    else : 
        ConvAdjAmt = t1 * 0
    return SwapRate, SwapRateForwardMeasure, ConvAdjAmt

def ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, RefSwapMaturity_T, RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag = 0, HWRho12Factor = 0) :
    EachSwapMaturityInSimulation = np.vectorize(EDate_YYYYMMDD)(SimulationDateList, int(RefSwapMaturity_T * 12 + 0.0001))
    CpnDateListInSimul = []
    for i in range(len(SimulationDateList)) : 
        CpnDateListInSimul.append(np.array(malloc_cpn_date_holiday(SimulationDateList[i], EachSwapMaturityInSimulation[i], RefSwapNCPNOneYear)[0]).reshape(1,-1))
    CpnDateArrayForEachSimulDate = np.concatenate(CpnDateListInSimul, axis = 0)

    t1 = np.vectorize(DayCountAtoB)(PriceDate, SimulationDateList)/365
    t2 = np.vectorize(DayCountAtoB)(PriceDate, CpnDateArrayForEachSimulDate)/365
    r1 = np.interp(t1, ZeroTerm, ZeroRate)
    r2 = np.interp(t2, ZeroTerm, ZeroRate)
    df1 = np.exp(-r1 * t1)
    df2 = np.exp(-r2 * t2)
    df_t_T = df2/df1.reshape(-1,1)
    MyFunc = np.vectorize(lambda DF_0_t_T, t, T: HullWhite_A_t_T_1F(DF_0_t_T, t, T, kappa, HWVolTerm, HWVol))
    if HW2FFlag == 0 : 
        A_t_T = MyFunc(df_t_T, t1.reshape(-1,1), t2) 
        B_t_T = B_s_to_t(t1.reshape(-1,1), t2, kappa)
        deltat = np.concatenate([(t2[:,0] - t1).reshape(-1,1), (t2[:,1:] - t2[:,:-1])], axis = 1)
        deltat3D = deltat.reshape(deltat.shape[0], deltat.shape[1], 1)
        B_t_T3D = B_t_T.reshape(B_t_T.shape[0], B_t_T.shape[1], 1)
        A_t_T3D = A_t_T.reshape(A_t_T.shape[0], A_t_T.shape[1], 1)

        Xt3D = xt_greed.reshape(len(SimulationDateList), 1, -1)
        Disc = HullWhite1F_DiscFactor_t_T(B_t_T3D, Xt3D, A_t_T3D)
        SwapRate = (1-Disc[:,-1,:])/(Disc * deltat3D).sum(1)    
    else : 
        MyFunc2F = np.vectorize(lambda DF_0_t_T, t, T: HullWhite_A_t_T_1F(1, t, T, kappa2, HWVolTerm2, HWVol2))
        MyFuncCrossTerm = np.vectorize(lambda t, T: HWCrossTerm(t, T, kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, HWVol2, HWRho12Factor))
        deltat = np.concatenate([(t2[:,0] - t1).reshape(-1,1), (t2[:,1:] - t2[:,:-1])], axis = 1)
        deltat3D = deltat.reshape(deltat.shape[0], deltat.shape[1], 1)

        A_t_T_Xt = MyFunc(df_t_T, t1.reshape(-1,1), t2) 
        B_t_T_Xt = B_s_to_t(t1.reshape(-1,1), t2, kappa)
        B_t_T_Xt3D = B_t_T_Xt.reshape(B_t_T_Xt.shape[0], B_t_T_Xt.shape[1], 1)
        A_t_T_Xt3D = A_t_T_Xt.reshape(A_t_T_Xt.shape[0], A_t_T_Xt.shape[1], 1)
        
        A_t_T_Yt = MyFunc2F(df_t_T, t1.reshape(-1,1), t2) 
        B_t_T_Yt = B_s_to_t(t1.reshape(-1,1), t2, kappa)
        B_t_T_Yt3D = B_t_T_Yt.reshape(B_t_T_Yt.shape[0], B_t_T_Yt.shape[1], 1)
        A_t_T_Yt3D = A_t_T_Yt.reshape(A_t_T_Yt.shape[0], A_t_T_Yt.shape[1], 1)
        
        HWCross = np.exp(MyFuncCrossTerm(t1.reshape(-1,1), t2)) 
        HWCross_4D = HWCross.reshape(HWCross.shape[0], HWCross.shape[1], 1, 1)
        Xt3D = xt_greed.reshape(len(SimulationDateList), 1, -1)
        Yt3D = yt_greed.reshape(len(SimulationDateList), 1, -1)
        Disc1 = HullWhite1F_DiscFactor_t_T(B_t_T_Xt3D, Xt3D, A_t_T_Xt3D)
        Disc2 = HullWhite1F_DiscFactor_t_T(B_t_T_Yt3D, Yt3D, A_t_T_Yt3D)
        Disc1_4D = Disc1.reshape(Disc1.shape[0], Disc1.shape[1], Disc1.shape[2], 1)
        Disc2_4D = Disc2.reshape(Disc2.shape[0], Disc2.shape[1], 1, Disc2.shape[2])
        deltat4D = deltat3D.reshape(deltat3D.shape[0], deltat3D.shape[1], 1, 1)
        Disc = Disc1_4D * Disc2_4D * HWCross_4D
        SwapRate = (1-Disc[:,-1,:,:])/(Disc * deltat4D).sum(1)    

    SwapRateForwardMeasure = (1-df_t_T[:,-1])/(df_t_T * deltat).sum(1)
    if df_t_T.shape[1] > 1 : 
        MyFuncTemp = np.vectorize(lambda CpnRateList, YTMList, StartDateList, EndDateList : GPrimePrime_Over_GPrime(CpnRateList, YTMList, StartDateList, EndDateList, RefSwapNCPNOneYear))
        GppOvGp = MyFuncTemp(SwapRateForwardMeasure, SwapRateForwardMeasure, np.array(SimulationDateList), EachSwapMaturityInSimulation)
        v = np.interp(t1, HWVolTerm, HWVol)
        ConvAdjAmt = GppOvGp * v * v * 100. * t1 * 0.5    
    else : 
        ConvAdjAmt = t1 * 0
    return SwapRate, SwapRateForwardMeasure, ConvAdjAmt

def Calc_RefRateOnFixingDate_And_ForwardDisc_FixingToPay(PriceDate, FixingDate, FixingDate2, PayDate, kappa, HWVolTerm, HWVol, ZeroTerm, ZeroRate, SimulationDateList, OptionFixDate, OptionPayDate, Leg_RefRate_Simul2DArray, SimulatedXt2D, RefRateForwardMeasure, Conv) :
    MyFunc = np.vectorize(lambda DF_0_t_T, t, T: HullWhite_A_t_T_1F(DF_0_t_T, t, T, kappa, HWVolTerm, HWVol))
    FixingIdx = np.array([list(FixingDate).index(SimulationDateList[i]) for i in range(len(SimulationDateList)) if SimulationDateList[i] in FixingDate])
    IdxSimul = np.array([i for i in range(len(SimulationDateList)) if SimulationDateList[i] in FixingDate])
    IdxSimul2 = np.array([i for i in range(len(SimulationDateList)) if SimulationDateList[i] in FixingDate2])
    RefRateOnFixingDate = Leg_RefRate_Simul2DArray[IdxSimul]
    RefRateOnFixingDate2 = Leg_RefRate_Simul2DArray[IdxSimul2]  
    RefRateOnFixingDateForwardMeasure = RefRateForwardMeasure[IdxSimul] - Conv[IdxSimul]
    RefRateOnFixingDateForwardMeasure2 = RefRateForwardMeasure[IdxSimul2] - Conv[IdxSimul2]
    tfix_ = np.vectorize(DayCountAtoB)(PriceDate, np.array(FixingDate)[FixingIdx])/365
    tpay_ = np.vectorize(DayCountAtoB)(PriceDate, np.array(PayDate)[FixingIdx])/365
    df_tfix = np.exp(-np.interp(tfix_, ZeroTerm, ZeroRate) * tfix_)
    DiscountFactorToPriceDatetoFixing = df_tfix
    df_tpay = np.exp(-np.interp(tpay_, ZeroTerm, ZeroRate) * tpay_)
    df_fix_to_pay = df_tpay/df_tfix
    A_t_T_FixedToPay = MyFunc(df_fix_to_pay,tfix_, tpay_).reshape(-1,1)    
    B_t_T_FixedToPay = B_s_to_t(tfix_,tpay_, kappa).reshape(-1,1)
    
    HWDF_tfix_tpay = HullWhite1F_DiscFactor_t_T(B_t_T_FixedToPay, SimulatedXt2D[IdxSimul], A_t_T_FixedToPay)

    OptFixingIdx = np.array([list(OptionFixDate).index(SimulationDateList[i]) for i in range(len(SimulationDateList)) if SimulationDateList[i] in OptionFixDate])
    Opttfix_ = np.vectorize(DayCountAtoB)(PriceDate, np.array(OptionFixDate)[OptFixingIdx])/365
    Opttpay_ = np.vectorize(DayCountAtoB)(PriceDate, np.array(OptionPayDate)[OptFixingIdx])/365
    Xt_Opt = SimulatedXt2D[OptFixingIdx]
    Optdf_tfix = np.exp(-np.interp(Opttfix_, ZeroTerm, ZeroRate) * Opttfix_)
    Optdf_tpay = np.exp(-np.interp(Opttpay_, ZeroTerm, ZeroRate) * Opttpay_)
    Optdf_fix_to_pay = Optdf_tpay/Optdf_tfix
    OptA_t_T_FixedToPay = MyFunc(Optdf_fix_to_pay,Optdf_tfix, Optdf_tpay).reshape(-1,1)    
    OptB_t_T_FixedToPay = B_s_to_t(Optdf_tfix,Optdf_tpay, kappa).reshape(-1,1)
    OptHWDF_tfix_tpay = HullWhite1F_DiscFactor_t_T(OptB_t_T_FixedToPay, Xt_Opt, OptA_t_T_FixedToPay)    

    return RefRateOnFixingDate, RefRateOnFixingDate2, HWDF_tfix_tpay, DiscountFactorToPriceDatetoFixing, RefRateOnFixingDateForwardMeasure, RefRateOnFixingDateForwardMeasure2, df_tpay.reshape(-1,1), SimulatedXt2D[IdxSimul], Xt_Opt, Optdf_tfix.reshape(-1,1), OptHWDF_tfix_tpay

def Calc_Payoff_Sim_and_NotSim(PriceDate, EffectiveDate, SimulatedRefRate, Nominal, Phase2StartDate, ForwardStart, ForwardEnd, PayDate, DayCount,RefSwapRate_Multiple_Phase1, RefSwapRate_Multiple_Phase2, FixedCpnRate_Phase1, FixedCpnRate_Phase2, FixingHistoryDate, FixingHistoryRate, ZeroCouponFlag, CompoundCouponFlag, RefRateForwardMeasure,ZeroTerm, ZeroRate, rounding = 11) : 
    D1 = np.array(ForwardStart)
    D2 = np.array(ForwardEnd)
    SimIdx = np.array(ForwardStart) > PriceDate
    NotSimIdx = (np.array(ForwardStart) <= PriceDate ) & (np.array(PayDate) > PriceDate)
    FixingDate_Sim = np.array(ForwardStart)[SimIdx]
    FixingDate2_Sim = np.array(ForwardEnd)[SimIdx]
    PayDate_Sim = np.array(PayDate)[SimIdx]
    
    IdxCummulativeCpn = -1
    for i in range(len(PayDate)-1) : 
        if (PriceDate >= PayDate[i] and PriceDate < PayDate[i+1]) : 
            IdxCummulativeCpn = i 
            break        
    
    if ZeroCouponFlag == True : 
        DeltaT = np.vectorize(DayCountFractionAtoB)(np.array([EffectiveDate]), D2, np.array([DayCount])).reshape(-1,1)
    else : 
        DeltaT = np.vectorize(DayCountFractionAtoB)(D1, D2, np.array([DayCount])).reshape(-1,1)
    DeltaT_NotSim = DeltaT[NotSimIdx]
    DeltaT_Sim = DeltaT[SimIdx]
    RefRateMultiple = ((np.array(PayDate) < Phase2StartDate) * RefSwapRate_Multiple_Phase1 + (np.array(PayDate) >= Phase2StartDate) * RefSwapRate_Multiple_Phase2).reshape(-1,1)
    RefRateMultiple_NotSim = RefRateMultiple[NotSimIdx]
    RefRateMultiple_Sim = RefRateMultiple[SimIdx]
    CpnRate = ((np.array(PayDate) < Phase2StartDate) * FixedCpnRate_Phase1 + (np.array(PayDate) >= Phase2StartDate) * FixedCpnRate_Phase2).reshape(-1,1)
    CpnRate_NotSim = CpnRate[NotSimIdx]
    CpnRate_Sim = CpnRate[SimIdx]
    
    if CompoundCouponFlag == False : 
        Payoff_Sim = ((SimulatedRefRate* RefRateMultiple_Sim) + CpnRate_Sim) * DeltaT_Sim * Nominal
        Payoff_ForwardMeasure = ((RefRateForwardMeasure.reshape(-1,1)* RefRateMultiple_Sim) + CpnRate_Sim) * DeltaT_Sim * Nominal
        if ZeroCouponFlag == True : 
            CummulativePrevCpn = (CpnRate[IdxCummulativeCpn]) * DeltaT[IdxCummulativeCpn] * Nominal if IdxCummulativeCpn >= 0 else [0]
        else : 
            CummulativePrevCpn = [0]
    else : 
        div = 10 ** rounding
        Payoff_Sim = np.ceil(((1+(SimulatedRefRate*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal
        Payoff_ForwardMeasure = np.ceil(((1+(RefRateForwardMeasure.reshape(-1,1)*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal
        if ZeroCouponFlag == True : 
            CummulativePrevCpn = np.ceil(((1+ CpnRate[IdxCummulativeCpn]) ** DeltaT[IdxCummulativeCpn]-1) * div)/div * Nominal if IdxCummulativeCpn >= 0 else [0]
        else : 
            CummulativePrevCpn = [0]

    PrevDate = np.array(ForwardStart)[NotSimIdx]
    PrevDate2 = np.array(ForwardEnd)[NotSimIdx]
    PrevPayDate = np.array(PayDate)[NotSimIdx]
    if len(PrevPayDate) > 0 : 
        PrevT = np.vectorize(DayCountFractionAtoB)(PriceDate, PrevPayDate, np.array([0])).reshape(-1,1)
        PrevR = np.interp(PrevT, ZeroTerm, ZeroRate)
        PrevDF = np.exp(-PrevR * PrevT)
        FixedRate1 = pd.Series(PrevDate, PrevDate).map(pd.Series(FixingHistoryRate, FixingHistoryDate)).fillna(0).values.reshape(-1,1)
        FixedRate2 = pd.Series(PrevDate2, PrevDate).map(pd.Series(FixingHistoryRate, FixingHistoryDate)).fillna(0).values.reshape(-1,1)
        Payoff_NotSim = ((FixedRate1 * RefRateMultiple_NotSim) + CpnRate_NotSim) * DeltaT_NotSim * Nominal
    else : 
        PrevPayDate = np.array([0])
        PrevDF = np.array([[1.0]])
        FixedRate1 = pd.Series([0.0])
        FixedRate2 = pd.Series([0.0])
        Payoff_NotSim = np.array([[0.0]])
    return {"FixingDate_Simul":FixingDate_Sim, "FixingDate2_Simul" :FixingDate2_Sim, "PayDate_Simul" : PayDate_Sim, "PrevFixDate" : PrevDate,"PrevFixDate2" : PrevDate2, "Payoff_Simul" : Payoff_Sim, "Payoff_Prev" : Payoff_NotSim,"FixedRate1_Prev" : FixedRate1,"FixedRate2_Prev" : FixedRate2, "PrevPayDate":PrevPayDate, "PrevDF" : PrevDF, "PrevCummulativeCpn" : CummulativePrevCpn, "Payoff_ForwardMeasure" : Payoff_ForwardMeasure}

def Calc_Payoff_FDM_ForTimeGreed(ZeroTerm, ZeroRate, PriceDate, EffectiveDate, RefRateOnFixingDate, RefRateOnFixingDate_PowerSpread, Nominal, 
                                 Phase2StartDate, ForwardStart, ForwardEnd, PayDate, DayCount,
                                 RefSwapRate_Multiple_Phase1, RefSwapRate_Multiple_Phase2, FixedCpnRate_Phase1, FixedCpnRate_Phase2, FixingHistoryDate, 
                                 FixingHistoryRate, ZeroCouponFlag, CompoundCouponFlag, RefRateForwardMeasure,RefRateForwardMeasure_PowerSpread, PowerSpreadFlag, rounding = 11, HW2FFlag = 0, MaxReturn = 1000, MaxLoss = -1000) : 
    maxi, mini = np.maximum, np.minimum
    D1 = np.array(ForwardStart)
    D2 = np.array(ForwardEnd)
    SimIdx = np.array(ForwardStart) > PriceDate
    NotSimIdx = (np.array(ForwardStart) <= PriceDate ) & (np.array(PayDate) > PriceDate)
    FixingDate_Sim = np.array(ForwardStart)[SimIdx]
    FixingDate2_Sim = np.array(ForwardEnd)[SimIdx]
    PayDate_Sim = np.array(PayDate)[SimIdx]

    IdxCummulativeCpn = -1
    for i in range(len(PayDate)-1) : 
        if (PriceDate >= PayDate[i] and PriceDate < PayDate[i+1]) : 
            IdxCummulativeCpn = i 
            break        

    if ZeroCouponFlag == True : 
        DeltaT = np.vectorize(DayCountFractionAtoB)(np.array([EffectiveDate]), D2, np.array([DayCount])).reshape(-1,1)
    else : 
        DeltaT = np.vectorize(DayCountFractionAtoB)(D1, D2, np.array([DayCount])).reshape(-1,1)
    DeltaT_NotSim = DeltaT[NotSimIdx]
    DeltaT_Sim = DeltaT[SimIdx]
    RefRateMultiple = ((np.array(PayDate) < Phase2StartDate) * RefSwapRate_Multiple_Phase1 + (np.array(PayDate) >= Phase2StartDate) * RefSwapRate_Multiple_Phase2).reshape(-1,1)
    RefRateMultiple_NotSim = RefRateMultiple[NotSimIdx]
    RefRateMultiple_Sim = RefRateMultiple[SimIdx]
    CpnRate = ((np.array(PayDate) < Phase2StartDate) * FixedCpnRate_Phase1 + (np.array(PayDate) >= Phase2StartDate) * FixedCpnRate_Phase2).reshape(-1,1)
    CpnRate_NotSim = CpnRate[NotSimIdx]
    CpnRate_Sim = CpnRate[SimIdx]

    if CompoundCouponFlag == False : 
        if PowerSpreadFlag == 0 : 
            if HW2FFlag == 0 : 
                Payoff_Sim = mini(MaxReturn, maxi((RefRateOnFixingDate* RefRateMultiple_Sim) + CpnRate_Sim, MaxLoss)) * DeltaT_Sim * Nominal
            else : 
                Multiple = RefRateMultiple_Sim[:,:,np.newaxis]
                Cpn = CpnRate_Sim[:,:,np.newaxis]
                dT = DeltaT_Sim[:,:,np.newaxis]
                Payoff_Sim = mini(MaxReturn, maxi((RefRateOnFixingDate* Multiple) + Cpn, MaxLoss)) * dT * Nominal
            Payoff_ForwardMeasure = mini(MaxReturn, maxi((RefRateForwardMeasure.reshape(-1,1)* RefRateMultiple_Sim) + CpnRate_Sim, MaxLoss)) * DeltaT_Sim * Nominal
        else : 
            if HW2FFlag == 0 : 
                Payoff_Sim = mini(MaxReturn, maxi(((RefRateOnFixingDate - RefRateOnFixingDate_PowerSpread)* RefRateMultiple_Sim) + CpnRate_Sim, MaxLoss)) * DeltaT_Sim * Nominal
            else : 
                Multiple = RefRateMultiple_Sim[:,:,np.newaxis]
                Cpn = CpnRate_Sim[:,:,np.newaxis]
                dT = DeltaT_Sim[:,:,np.newaxis]
                Payoff_Sim = mini(MaxReturn, maxi(((RefRateOnFixingDate - RefRateOnFixingDate_PowerSpread)* Multiple) + Cpn, MaxLoss)) * dT * Nominal
                
            Payoff_ForwardMeasure = mini(MaxReturn, maxi(((RefRateForwardMeasure.reshape(-1,1) - RefRateForwardMeasure_PowerSpread.reshape(-1,1))* RefRateMultiple_Sim) + CpnRate_Sim, MaxLoss)) * DeltaT_Sim * Nominal
            
        if ZeroCouponFlag == True : 
            CummulativePrevCpn = (CpnRate[IdxCummulativeCpn]) * DeltaT[IdxCummulativeCpn] * Nominal if IdxCummulativeCpn >= 0 else [0]
        else : 
            CummulativePrevCpn = [0]
    else : 
        div = 10 ** rounding
        if PowerSpreadFlag == 0 : 
            if HW2FFlag == 0 : 
                Payoff_Sim = np.ceil(((1+(RefRateOnFixingDate*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal
            else : 
                Multiple = RefRateMultiple_Sim[:,:,np.newaxis]
                Cpn = CpnRate_Sim[:,:,np.newaxis]
                dT = DeltaT_Sim[:,:,np.newaxis]
                Payoff_Sim = np.ceil(((1+(RefRateOnFixingDate*Multiple) + Cpn)**dT - 1) * div)/div * Nominal
                
            Payoff_ForwardMeasure = np.ceil(((1+(RefRateForwardMeasure.reshape(-1,1)*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal
        else : 
            if HW2FFlag == 0 :
                Payoff_Sim = np.ceil(((1+((RefRateOnFixingDate - RefRateOnFixingDate_PowerSpread)*RefRateMultiple_Sim) + CpnRate_Sim)**DeltaT_Sim - 1) * div)/div * Nominal        
            else : 
                Multiple = RefRateMultiple_Sim[:,:,np.newaxis]
                Cpn = CpnRate_Sim[:,:,np.newaxis]
                dT = DeltaT_Sim[:,:,np.newaxis]
                Payoff_Sim = np.ceil(((1+((RefRateOnFixingDate - RefRateOnFixingDate_PowerSpread)*Multiple) + Cpn)**dT - 1) * div)/div * Nominal        
                
            Payoff_ForwardMeasure = (((RefRateForwardMeasure.reshape(-1,1) - RefRateForwardMeasure_PowerSpread.reshape(-1,1))* RefRateMultiple_Sim) + CpnRate_Sim) * DeltaT_Sim * Nominal

        if ZeroCouponFlag == True : 
            CummulativePrevCpn = np.ceil(((1+ CpnRate[IdxCummulativeCpn]) ** DeltaT[IdxCummulativeCpn]-1) * div)/div * Nominal if IdxCummulativeCpn >= 0 else [0]
        else : 
            CummulativePrevCpn = [0]
        
    PrevDate = np.array(ForwardStart)[NotSimIdx]
    PrevDate2 = np.array(ForwardEnd)[NotSimIdx]
    PrevPayDate = np.array(PayDate)[NotSimIdx]
    if len(PrevPayDate) > 0 : 
        PrevT = np.vectorize(DayCountFractionAtoB)(PriceDate, PrevPayDate, np.array([0])).reshape(-1,1)
        PrevR = np.interp(PrevT, ZeroTerm, ZeroRate)
        PrevDF = np.exp(-PrevR * PrevT)
        FixedRate1 = pd.Series(PrevDate, PrevDate).map(pd.Series(FixingHistoryRate, FixingHistoryDate)).fillna(0).values.reshape(-1,1)
        FixedRate2 = pd.Series(PrevDate2, PrevDate).map(pd.Series(FixingHistoryRate, FixingHistoryDate)).fillna(0).values.reshape(-1,1)
        Payoff_NotSim = ((FixedRate1 * RefRateMultiple_NotSim) + CpnRate_NotSim) * DeltaT_NotSim * Nominal
    else : 
        PrevPayDate = np.array([0])
        PrevDF = np.array([[1.0]])
        FixedRate1 = pd.Series([0.0])
        FixedRate2 = pd.Series([0.0])
        Payoff_NotSim = np.array([[0.0]])
            
    return {"FixingDate_Simul":FixingDate_Sim, "FixingDate2_Simul" :FixingDate2_Sim, "PayDate_Simul" : PayDate_Sim, "PrevFixDate" : PrevDate,"PrevFixDate2" : PrevDate2, "Payoff_Simul" : Payoff_Sim, "Payoff_Prev" : Payoff_NotSim,"FixedRate1_Prev" : FixedRate1,"FixedRate2_Prev" : FixedRate2, "PrevPayDate":PrevPayDate, "PrevDF" : PrevDF, "PrevCummulativeCpn" : CummulativePrevCpn, "Payoff_ForwardMeasure" : Payoff_ForwardMeasure}


def HullWhiteCalibration1Factor(PriceDate, OptionTenor_ByMonth, SwapTenor_ByMonth, OptionVol, SwapFreqByMonth, BSVol0NormalVol1, Term, Rate, FixedKappa = 0, DayCountFlag = 0, KoreanHolidayFlag = True, AdditionalHolidays = [], initialkappa = 0.01, initialvol = 0.01, PrintMRSPE = False) :
    if PriceDate < 19000101 : 
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
        
    if len(OptionTenor_ByMonth) == len(SwapTenor_ByMonth) : 
        for i in range(len(OptionTenor_ByMonth)) : 
            if OptionTenor_ByMonth[i] > 2400 : 
                MC = MonthCountAtoB(PriceDate, OptionTenor_ByMonth[i])
                OptionTenor_ByMonth[i] = 3 * (MC // 3)
        
        for i in range(len(SwapTenor_ByMonth)) : 
            if SwapTenor_ByMonth[i] > 2400 :
                Start = EDate_YYYYMMDD(PriceDate, OptionTenor_ByMonth[i]) 
                MC = MonthCountAtoB(Start, SwapTenor_ByMonth[i])
                SwapTenor_ByMonth[i] = 3 * (MC // 3)
        
    Holidays = KoreaHolidaysFromStartToEnd(PriceDate//10000, PriceDate//10000 + 50) if KoreanHolidayFlag == True else AdditionalHolidays
    NCpnAnn = int(12/SwapFreqByMonth)
    OptionTenor_ByMonth = np.array(OptionTenor_ByMonth)
    SwapTenor_ByMonth = np.array(SwapTenor_ByMonth)
    FSRList, SwapStartDateList, SwapEndDateList,CpnDateArrayList,BlackPriceList = [], [], [], [],[]
    T_StartDate, T_CpnDate = [], []
    Notional = 100
    TempDayCount = np.vectorize(DayCountAtoB)
    Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)
    try : 
        Number_Of_Swaption = len(OptionVol.shape[0]) * len(OptionVol.shape[1])
        for i in range(len(SwapTenor_ByMonth)) : 
            for j in range(len(OptionTenor_ByMonth)) : 
                StartDate = EDate_YYYYMMDD(PriceDate, int(OptionTenor_ByMonth[j]))
                SwapEndDate = EDate_YYYYMMDD(StartDate, int(SwapTenor_ByMonth[i]))
                f = FSR(PriceDate, StartDate, SwapEndDate,NCpnAnn,DayCountFlag,Holidays, Term, Rate, Term, Rate)
                FSRList.append(f)
                SwapStartDateList.append(StartDate)
                SwapEndDateList.append(SwapEndDate)
                Start, End, Pay, NBD = MappingCouponDates(1,StartDate,SwapEndDate,0,int(NCpnAnn),1, Holidays, Holidays,1)
                CpnDateArrayList.append(End)
                T_StartDate.append(DayCountAtoB(PriceDate, StartDate)/365)
                T_CpnDate.append(TempDayCount([PriceDate], End)/365)
                
                P = BS_Swaption(PriceDate, StartDate, SwapEndDate, NCpnAnn, Notional, OptionVol[i][j], f, Term, Rate, DayCountFlag, BSVol0NormalVol1, Holidays, Holidays, 0, 0)
                BlackPriceList.append(P["Price"])
    except IndexError : 
        Number_Of_Swaption = min(len(OptionTenor_ByMonth), len(SwapTenor_ByMonth)) 
        for i in range(Number_Of_Swaption) : 
            StartDate = EDate_YYYYMMDD(PriceDate, int(OptionTenor_ByMonth[i]))
            SwapEndDate = EDate_YYYYMMDD(StartDate, int(SwapTenor_ByMonth[i]))
            f = FSR(PriceDate, StartDate, SwapEndDate,NCpnAnn,DayCountFlag,Holidays, Term, Rate, Term, Rate)
            FSRList.append(f)
            SwapStartDateList.append(StartDate)
            SwapEndDateList.append(SwapEndDate)
            Start, End, Pay, NBD = MappingCouponDates(1,StartDate,SwapEndDate,0,int(NCpnAnn),1, Holidays, Holidays,1)
            CpnDateArrayList.append(End)
            T_StartDate.append(DayCountAtoB(PriceDate, StartDate)/365)
            T_CpnDate.append(TempDayCount([PriceDate], End)/365)            
            P = BS_Swaption(PriceDate, StartDate, SwapEndDate, NCpnAnn, Notional, OptionVol[i], f, Term, Rate, DayCountFlag, BSVol0NormalVol1, Holidays, Holidays, 0, 0)
            BlackPriceList.append(P["Price"])                    
    except AttributeError : 
        Number_Of_Swaption = min(len(OptionTenor_ByMonth), len(SwapTenor_ByMonth)) 
        for i in range(Number_Of_Swaption) : 
            StartDate = EDate_YYYYMMDD(PriceDate, int(OptionTenor_ByMonth[i]))
            SwapEndDate = EDate_YYYYMMDD(StartDate, int(SwapTenor_ByMonth[i]))
            f = FSR(PriceDate, StartDate, SwapEndDate,NCpnAnn,DayCountFlag,Holidays, Term, Rate, Term, Rate)
            FSRList.append(f)
            SwapStartDateList.append(StartDate)
            SwapEndDateList.append(SwapEndDate)
            Start, End, Pay, NBD = MappingCouponDates(1,StartDate,SwapEndDate,0,int(NCpnAnn),1, Holidays, Holidays,1)
            CpnDateArrayList.append(End)
            T_StartDate.append(DayCountAtoB(PriceDate, StartDate)/365)
            T_CpnDate.append(TempDayCount([PriceDate], End)/365)            
            P = BS_Swaption(PriceDate, StartDate, SwapEndDate, NCpnAnn, Notional, OptionVol[i], f, Term, Rate, DayCountFlag, BSVol0NormalVol1, Holidays, Holidays, 0, 0)
            BlackPriceList.append(P["Price"])                    

    HWTenor = [1/30] + list(pd.Series(OptionTenor_ByMonth).unique())            
    Parameters = [initialkappa] + [initialvol] * (len(HWTenor)) if FixedKappa == 0 else [initialvol] * (len(HWTenor))
    Parameters = np.array(Parameters)
    TermHWVol = np.array(HWTenor,dtype = np.float64)/12
    JacovMatrix = np.zeros(shape = (Number_Of_Swaption, len(Parameters)))
    firstmu, PrevErrorSquare = 1.0, 100000
    MinErr = 100000
    dkappa, dhwvol = 0.005, 0.001
    MinVol, MaxVol = 0.0001, 0.10
    MinKap, MaxKap = 0.001, 1.5
    ArgMinParams = Parameters.copy()
    ArgMinPrice = np.array(BlackPriceList)
    ArgMinErrArray = np.array([-1] * len(BlackPriceList))
    for n in range(10) : 
        ErrorList = []
        HWPList = []
        MRSPE, errsquaresum = 0, 0
        kap = Parameters[0] if FixedKappa == 0 else FixedKappa
        usingvol = Parameters[1:] if FixedKappa == 0 else Parameters
        for i in range(Number_Of_Swaption) : 
            HWP = HW_Swaption(Notional, kap, TermHWVol, usingvol, Term, Rate, FSRList[i], T_StartDate[i], T_CpnDate[i])
            BSP = BlackPriceList[i]    
            Err = BSP - HWP
            HWPList.append(HWP)
            RSPercent = (Err * Err)/(BSP * BSP)
            ErrorList.append(Err)
            errsquaresum += (Err * Err)
            MRSPE += RSPercent/Number_Of_Swaption
        ErrorArray = np.array(ErrorList)    
        if PrintMRSPE == True : 
            print('###   iters = ' + str(n))
            print('###   RMSPE = ' + str(np.round(MRSPE*100,7)) + "%")
            print('###   HWPar = ' + str(Parameters.round(3)))
        
        if n <= 2 : 
            mu = firstmu
        elif (PrevErrorSquare > errsquaresum) : 
            mu = max(0.0001, mu * 0.5) if ((PrevErrorSquare - errsquaresum)/PrevErrorSquare > 0.1) else mu
            if errsquaresum < MinErr : 
                MinErr = errsquaresum
                ArgMinParams = Parameters.copy()
                ArgMinPrice = np.array(HWPList)
                ArgMinErrArray = ErrorArray
        else : 
            mu = min(firstmu, 10 * mu)
                
        mu = firstmu
        Iden = np.identity(len(Parameters))    
        BaseKappa = Parameters[0] if FixedKappa == 0 else FixedKappa
        BaseVol = np.array(Parameters[1:]) if FixedKappa == 0 else np.array(Parameters)
        for i in range(Number_Of_Swaption) : 
            for j in range(len(Parameters)) :    
                KappaUp, KappaDn = BaseKappa, BaseKappa
                VolUp = BaseVol.copy()
                VolDn = BaseVol.copy()
                HWT = 0
                if FixedKappa == 0 : 
                    if j == 0 :
                        KappaUp = min(MaxKap, kap + dkappa)
                        KappaDn = max(MinKap, kap - dkappa)
                        dParams = KappaUp - KappaDn
                    else : 
                        VolUp[j-1] = min(MaxVol, Parameters[j] + dhwvol)
                        VolDn[j-1] = max(MinVol, Parameters[j] - dhwvol)
                        dParams = VolUp[j-1] - VolDn[j-1]
                        HWT = TermHWVol[j-1]
                else : 
                    VolUp[j] = min(MaxVol, Parameters[j] + dhwvol)
                    VolDn[j] = max(MinVol, Parameters[j] - dhwvol)
                    dParams = VolUp[j] - VolDn[j]
                    HWT = TermHWVol[j]
                TMAX = T_CpnDate[i][-1] + 1
                #if TMAX >+ HWT : 
                HWPUP = HW_Swaption(Notional, KappaUp, TermHWVol, VolUp, Term, Rate, FSRList[i], T_StartDate[i], T_CpnDate[i])
                HWPDN = HW_Swaption(Notional, KappaDn, TermHWVol, VolDn, Term, Rate, FSRList[i], T_StartDate[i], T_CpnDate[i])
                ErrUp = BlackPriceList[i] - HWPUP
                ErrDn = BlackPriceList[i] - HWPDN        
                JacovMatrix[i][j] = (ErrUp - ErrDn) / (dParams)
                #else : 
                #    JacovMatrix[i][j] = 0                    

        JtJ = JacovMatrix.T.dot(JacovMatrix)
        NextdParams = np.linalg.inv(JtJ + mu * Iden).dot(JacovMatrix.T.dot(ErrorArray))                 
        
        Parameters = Parameters - NextdParams
        if FixedKappa == 0 : 
            k = np.minimum(np.maximum(MinKap, Parameters[:1]), MaxKap)
            v = np.minimum(np.maximum(MinVol, Parameters[1:]), MaxVol)
            Parameters = np.r_[k, v]
        else : 
            Parameters = np.minimum(np.maximum(MinVol, Parameters), MaxVol)
        PrevErrorSquare = errsquaresum
        
    BlackPriceList = np.array(BlackPriceList)
    SwapEndDateList = np.array(SwapEndDateList)
    SwapStartDateList = np.array(SwapStartDateList)
    return {"kappa" : ArgMinParams[0] if FixedKappa == 0 else FixedKappa, "HWVolTerm" : TermHWVol, "HWVol" : ArgMinParams[1:] if FixedKappa == 0 else ArgMinParams, "HWPrice": ArgMinPrice, "Error" : ArgMinErrArray, "BlackPrice": BlackPriceList, "SwapStartDate":SwapStartDateList,"SwapEndDate" : SwapEndDateList}

def FindSwaptionImpliedVolatility(PriceDate, SwapStartDate, SwapEndDate, NCpnAnn, Term, Rate, TargetPrice, DayCountFracFlag, VolFlag, Nominal = 1, HolidayFlag = "kr", SelfHolidays = [], FixedPayer0Receiver1 = 0) : 
    if 'kr' in str(HolidayFlag).lower() or str(HolidayFlag) == '0' :
        Holidays = KoreaHolidaysFromStartToEnd(SwapStartDate//10000, SwapStartDate//10000 + 40)
    elif 'us' in  str(HolidayFlag).lower() or str(HolidayFlag) == '1' :
        Holidays = USHolidaysFromStartToEnd(SwapStartDate//10000, SwapStartDate//10000 + 40)
    else : 
        Holidays = SelfHolidays
    
    if PriceDate < 19000101 : 
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    
    if SwapStartDate < 19000101 : 
        SwapStartDate = ExcelDateToYYYYMMDD(SwapStartDate)

    if SwapEndDate < 19000101 : 
        SwapEndDate = ExcelDateToYYYYMMDD(SwapEndDate)
        
    Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)
    
    StartDate, EndDate, Price = SwapStartDate, SwapEndDate, TargetPrice
    TempValue = BS_Swaption(PriceDate, StartDate, EndDate, NCpnAnn, Nominal, 0.01, 0.02, Term, Rate, DayCountFracFlag, VolFlag = VolFlag, HolidaysFixing = Holidays, HolidaysPay= Holidays, NBDayFromEndDateToPay=0, FixedPayer0Receiver1=FixedPayer0Receiver1)
    StrikePrice = TempValue["ForwardSwapRate"]
    MaxVol = 1.5
    MinVol = 0.000001
    if VolFlag == 1 : 
        MaxVol = 0.25
    TargetVol = MaxVol
    for j in range(200) : 
        v = BS_Swaption(PriceDate, StartDate, EndDate, NCpnAnn, Nominal, TargetVol, StrikePrice, Term, Rate, DayCountFracFlag, VolFlag, Holidays, Holidays, 0, FixedPayer0Receiver1 )
        Err = v["Price"] - TargetPrice
        if abs(Err) < 0.000001 : 
            break
        elif Err > 0 : 
            MaxVol = TargetVol
            TargetVol = (MaxVol + MinVol)/2
        else : 
            MinVol = TargetVol
            TargetVol = (MaxVol + MinVol)/2
        
    if j == 200 : 
        raise ValueError("Check The Price")
    return {"ImpliedVol" : TargetVol, "ForwardSwapRate" : StrikePrice}
        
def Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
              PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
              NumCpnOneYear, DayCountFlag, KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [],
              EstZeroCurveRate = [], FixingHolidayList = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False,
              LoggingFlag = 0, LoggingDir = '', ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], 
              LookBackDays = 0, ObservShift = False, DiscCurveName = "", EstCurveName = "", CMSFlag = 0, RefSwapMaturity_T = 0.25, RefSwapNCPNAnn = 4, TermVol = [], Vol = [], YTMPricing = False, AIList = [0]) :
    
    LoggingStart = []
    LoggingEnd = []
    LoggingEstStart = []
    LoggingEstEnd = []
    LoggingPayDate = []
    LoggingFraction = []
    LoggingForwardRate = []
    LoggingCpnFix = []
    LoggingCpnRate = []
    LoggingAdj = []
    LoggingRawCpn = []
    LoggingDF = []
    rawcpn = 0
    BondFlag = 0 
    if DayCountFlag >= 5 : 
        BondFlag = 1
        DayCountFlag = DayCountFlag - 5
        
    ModifiedFollow = 1
    PriceDateYYYY, MaturityYYYY = int(PriceDateYYYYMMDD // 10000), int(MaturityYYYYMMDD // 10000)
    if len(AdditionalPayHolidayList) == 0 : 
        if KoreanHoliday == True : 
            HolidayYYYYMMDD = np.array(KoreaHolidaysFromStartToEnd(PriceDateYYYY, MaturityYYYY + 1), dtype = np.int64)
        else : 
            HolidayYYYYMMDD = np.array(AdditionalPayHolidayList, dtype = np.int64)            
    else : 
        HolidayYYYYMMDD = np.array(AdditionalPayHolidayList, dtype = np.int64)
    
    FixingHolidayYYYYMMDD = HolidayYYYYMMDD if len(FixingHolidayList) == 0 else np.array(FixingHolidayList, dtype = np.int64)
    if (NumCpnOneYear >= 4 and DayCountAtoB(EffectiveDateYYYYMMDD, MaturityYYYYMMDD) < 70) or (DayCountAtoB(EffectiveDateYYYYMMDD, MaturityYYYYMMDD) < 10) : 
        Generated_CpnDate = np.array([MaturityYYYYMMDD], dtype = np.int64)
    else : 
        if EffectiveDateYYYYMMDD % 100 == MaturityYYYYMMDD % 100 : 
            # 만기 Day가 같을 때
            Generated_CpnDate, firstcpndate = malloc_cpn_date_holiday(EffectiveDateYYYYMMDD, MaturityYYYYMMDD, NumCpnOneYear, FixingHolidayYYYYMMDD, ModifiedFollow)
        else : 
            Generated_Fixing, Generated_CpnDate, Generated_Pay, NBD = MappingCouponDates(1,EffectiveDateYYYYMMDD,MaturityYYYYMMDD,0,NumCpnOneYear,1,FixingHolidayYYYYMMDD,HolidayYYYYMMDD,1)

    AccruedT, AI = 0, 0
    BondCompStart = EffectiveDateYYYYMMDD
    if PriceDateYYYYMMDD == EffectiveDateYYYYMMDD or PriceDateYYYYMMDD in Generated_CpnDate : 
        AccruedT = 0
    else : 
        if BondFlag == 1 : 
            if PriceDateYYYYMMDD > EffectiveDateYYYYMMDD and PriceDateYYYYMMDD < Generated_CpnDate[0] : 
                AccruedT = DayCountAtoB(BondCompStart, PriceDateYYYYMMDD)/DayCountAtoB(BondCompStart, Generated_CpnDate[0])/NumCpnOneYear
                AI = AccruedT * CpnRate * Nominal
            else : 
                for i in range(len(Generated_CpnDate) - 1) : 
                    if PriceDateYYYYMMDD >= Generated_CpnDate[i] and PriceDateYYYYMMDD < Generated_CpnDate[i+1] : 
                        BondCompStart = Generated_CpnDate[i]
                        AccruedT = DayCountAtoB(BondCompStart, PriceDateYYYYMMDD)/DayCountAtoB(BondCompStart, Generated_CpnDate[i+1])/NumCpnOneYear
                        AI = AccruedT * CpnRate * Nominal
                        break
    YTMRate = 0
    if YTMPricing == True :     
        t = DayCountAtoB(PriceDateYYYYMMDD, MaturityYYYYMMDD)/365
        YTMRate = np.interp(t, ZeroCurveTerm, ZeroCurveRate)
        
    BDate = []  
    DayCountBDate = []
    if FloatFlag == 2 : 
        # SOFR의 경우 BusinessDate를 Generate
        BDate, BDExcel = BusinessDateArrayFromAtoB(PriceDateYYYY - 1, MaturityYYYY + 1, FixingHolidayYYYYMMDD)
        BDate = np.array(BDate[:-1])
        BDExcel = np.array(BDExcel)
        DayCountBDate = BDExcel[1:] - BDExcel[:-1]
            
    s = 0
    for i in range(len(Generated_CpnDate)) : 
        YYYYMMDDofNextDate = Generated_CpnDate[i]
        tpay = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[i])/365
        r1 = 0.
        r2 = 0.
        if MaturityToPayDate > 0 : 
            ExcelDate = YYYYMMDDToExcelDate(Generated_CpnDate[i])
            n = 0
            for k in range(20) : 
                NextExcelDate = ExcelDate + (k + 1)
                SaturSundayFlag = 1 if NextExcelDate % 7 in [0,1] else 0
                YYYYMMDDofNextDate = ExcelDateToYYYYMMDD(NextExcelDate)
                HolidayFlag = YYYYMMDDofNextDate in HolidayYYYYMMDD
                if (HolidayFlag == 0) and (SaturSundayFlag == 0) : 
                    n += 1
                
                if (n >= MaturityToPayDate) : 
                    tpay = DayCountAtoB(PriceDateYYYYMMDD, YYYYMMDDofNextDate) / 365
                    break
        if (i > 0) : 
            tstart = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[i-1])/365
            tend = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[i])/365            
            deltat = DayCountFractionAtoB(Generated_CpnDate[i-1], Generated_CpnDate[i], DayCountFlag, HolidayYYYYMMDD)
        else : 
            tstart = DayCountAtoB(PriceDateYYYYMMDD, EffectiveDateYYYYMMDD)/365
            tend = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[i])/365            
            deltat = DayCountFractionAtoB(EffectiveDateYYYYMMDD, Generated_CpnDate[i], DayCountFlag, HolidayYYYYMMDD)
            
        LastFixingDate = EffectiveDateYYYYMMDD if i == 0 else Generated_CpnDate[i-1]
        EstStartDate = LastFixingDate
        EstEndDate = Generated_CpnDate[i]
        f = 0
        ConvAdjAmt = 0
        if LastFixingDate < PriceDateYYYYMMDD : 
            f = FirstFloatFixRate
        elif LastFixingDate >= PriceDateYYYYMMDD : 
            if len(EstZeroCurveRate) == 0 and len(EstZeroCurveTerm) == 0 :
                if FloatFlag == 2 : 
                    Start = EDate_YYYYMMDD(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, -1)
                    End = Generated_CpnDate[i]
                    BusinessDate = BDate[(BDate >= Start) & (BDate <= End)]
                    NBDCount = DayCountBDate[(BDate >= Start) & (BDate <= End)]
                    
                    CompValue, f, EstStartIdx, EstEndIdx = SOFR_ForwardRate_Compound(PriceDateYYYYMMDD,    ZeroCurveTerm,    ZeroCurveRate,     Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD,    Generated_CpnDate[i],
                                                            0,    LookBackDays,    ObservShift,    0,    BusinessDate,    NBDCount,
                                                            OverNightRateDateHistory,    OverNightRateHistory,    365 if DayCountFlag == 0 else 360,    1)
                    EstStartDate = BusinessDate[max(0, EstStartIdx - LookBackDays)]
                    EstEndDate = BusinessDate[max(0, EstEndIdx - LookBackDays)]                    
                elif CMSFlag == 1 : 
                    SwapMaturity = Calc_CMS_Maturity(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, RefSwap_Maturity_T_Year = RefSwapMaturity_T)
                    f = FSR(PriceDateYYYYMMDD, Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, SwapMaturity, RefSwapNCPNAnn,DayCountFlag, FixingHolidayYYYYMMDD, ZeroCurveTerm, ZeroCurveRate, ZeroCurveTerm, ZeroCurveRate)
                    v = Linterp(TermVol, Vol, tstart)
                    GppOvGp = GPrimePrime_Over_GPrime(f, f, Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, RefSwapMaturity_T, RefSwapNCPNAnn)
                    ConvAdjAmt = GppOvGp * v * v * 100. * tstart * 0.5
                    f = f - ConvAdjAmt;                                        
                else : 
                    r1 = Linterp(ZeroCurveTerm, ZeroCurveRate, tstart)
                    r2 = Linterp(ZeroCurveTerm, ZeroCurveRate, tend)
                    f = 1.0 / deltat * (np.exp(-r1 * tstart)/np.exp(-r2 * tend) - 1.0)
            else : 
                if FloatFlag == 2 : 
                    Start = EDate_YYYYMMDD(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, -1)
                    End = Generated_CpnDate[i]
                    BusinessDate = BDate[(BDate >= Start) & (BDate <= End)]
                    NBDCount = DayCountBDate[(BDate >= Start) & (BDate <= End)]
                    CompValue, f, EstStartIdx, EstEndIdx = SOFR_ForwardRate_Compound(PriceDateYYYYMMDD,    EstZeroCurveTerm,    EstZeroCurveRate,     Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD,    Generated_CpnDate[i],
                                                            0,    LookBackDays,    ObservShift,    0,    BusinessDate,    NBDCount,
                                                            OverNightRateDateHistory,    OverNightRateHistory,    365 if DayCountFlag == 0 else 360,    1)
                    EstStartDate = BusinessDate[max(0, EstStartIdx - LookBackDays)]
                    EstEndDate = BusinessDate[max(0, EstEndIdx - LookBackDays)]                        
                elif CMSFlag == 1 : 
                    SwapMaturity = Calc_CMS_Maturity(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, RefSwap_Maturity_T_Year = RefSwapMaturity_T)
                    f = FSR(PriceDateYYYYMMDD, Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, SwapMaturity, RefSwapNCPNAnn,DayCountFlag, FixingHolidayYYYYMMDD, EstZeroCurveTerm, EstZeroCurveRate, ZeroCurveTerm, ZeroCurveRate)
                    v = Linterp(TermVol, Vol, tstart)
                    GppOvGp = GPrimePrime_Over_GPrime(f, f, Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD, RefSwapMaturity_T, RefSwapNCPNAnn)
                    ConvAdjAmt = GppOvGp * v * v * 100. * tstart * 0.5
                    f = f - ConvAdjAmt;                                                            
                else : 
                    r1 = Linterp(EstZeroCurveTerm, EstZeroCurveRate, tstart)
                    r2 = Linterp(EstZeroCurveTerm, EstZeroCurveRate, tend)
                    f = 1.0 / deltat * (np.exp(-r1 * tstart)/np.exp(-r2 * tend) - 1.0)                    
            
        r = Linterp(ZeroCurveTerm, ZeroCurveRate, tpay)
        DF = np.exp(-r * tpay)
        if tpay > 0 : 
            if DayCountFlag != 3 and BondFlag == 0 : 
                rawcpn = (f * (FloatFlag > 0) + CpnRate) * Nominal * deltat
                cpn = rawcpn * DF
            elif BondFlag == 0 : 
                if (NumCpnOneYear == 1) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 2) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.5 * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 3) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.3333333333 * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 4) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.25 * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 6) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.166666666667 * Nominal
                    cpn = rawcpn * DF 
                elif (NumCpnOneYear == 12) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.083333333333 * Nominal
                    cpn = rawcpn * DF 
                else : 
                    raise ValueError("Check AnnCpnNum")
            else : 
                if YTMPricing == True : 
                    DF = 1/((1.0+YTMRate/NumCpnOneYear)**(NumCpnOneYear * DayCountFractionAtoB(BondCompStart, YYYYMMDDofNextDate,DayCountFlag) - AccruedT ))
                
                if (NumCpnOneYear == 1) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 2) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.5 * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 3) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.3333333333 * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 4) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.25 * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 6) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.166666666667 * Nominal
                    cpn = rawcpn * DF
                elif (NumCpnOneYear == 12) : 
                    rawcpn = (f * (FloatFlag > 0) + CpnRate) * 0.083333333333 * Nominal
                    cpn = rawcpn * DF
                else : 
                    raise ValueError("Check AnnCpnNum")                
        else : 
            cpn = 0
            rawcpn = 0
        
        s += cpn
        if LoggingFlag > 0 : 
            LoggingStart.append(Generated_CpnDate[i-1] if i > 0 else EffectiveDateYYYYMMDD)
            LoggingEnd.append(Generated_CpnDate[i])
            LoggingEstStart.append(EstStartDate)
            LoggingEstEnd.append(EstEndDate)
            LoggingPayDate.append(YYYYMMDDofNextDate)
            LoggingFraction.append(deltat)
            LoggingAdj.append(ConvAdjAmt)
            if tpay > 0 : 
                LoggingForwardRate.append(f if FloatFlag > 0 else 0)
                LoggingCpnFix.append(CpnRate)
                LoggingCpnRate.append(cpn)
                LoggingRawCpn.append(rawcpn)
                LoggingDF.append(DF)                    
            else : 
                LoggingForwardRate.append(0)
                LoggingCpnFix.append(0)
                LoggingCpnRate.append(0)
                LoggingRawCpn.append(0)
                LoggingDF.append(1.0)                
                    
    if NominalFlag == 1 : 
        if NominalDateIsNominalPayDate == True : 
            tpay = DayCountAtoB(PriceDateYYYYMMDD, Generated_CpnDate[-1])/365
            r = Linterp(ZeroCurveTerm, ZeroCurveRate, tpay)
        s += Nominal * DF
        if (LoggingFlag > 0) : 
            LoggingAdj.append(0)
            LoggingStart.append(EffectiveDateYYYYMMDD)
            LoggingEnd.append(Generated_CpnDate[-1])
            LoggingEstStart.append(EffectiveDateYYYYMMDD)
            LoggingEstEnd.append(Generated_CpnDate[-1])            
            LoggingPayDate.append(YYYYMMDDofNextDate if NominalDateIsNominalPayDate == False else Generated_CpnDate[-1])
            LoggingFraction.append(tpay)
            LoggingForwardRate.append(r)
            LoggingCpnFix.append(CpnRate)
            LoggingCpnRate.append(Nominal* DF)
            LoggingRawCpn.append(Nominal)
            LoggingDF.append(DF)             
    
    if LoggingFlag == 1 : 
        LoggingDF = pd.DataFrame([LoggingStart,LoggingEnd,LoggingEstStart,LoggingEstEnd,LoggingPayDate,LoggingFraction, LoggingForwardRate, LoggingAdj, LoggingCpnFix, LoggingCpnRate, LoggingRawCpn, LoggingDF], index = ["Start","End","EstStart","EstEnd","Pay","Frac","ForwardRate","ConvAdj","CpnFixed","Cpn","RawCpn","DF"]).T               
        if (len(DiscCurveName) > 0) : 
            LoggingDF["DiscCurve"] = DiscCurveName
            LoggingDF["EstCurve"] = "none" if FloatFlag == 0 else (DiscCurveName if FloatFlag != 0 and len(EstZeroCurveTerm) == 0 else EstCurveName)                

        LoggingDF["AccruedT"] = AccruedT
        LoggingDF["AI"] = AI
            
        LoggingDF["Price"] = s
        LoggingDF.to_csv(LoggingDir + "\\LoggingFilesBond.csv", index = False, encoding = "cp949")
    elif LoggingFlag == 2 : 
        df = ReadCSV(LoggingDir + "\\LoggingFilesBond.csv")
        ColList = ["Leg1_" + str(s) for s in df.columns]
        df.columns = ColList
        LoggingDF = pd.DataFrame([LoggingStart,LoggingEnd,LoggingEstStart, LoggingEstEnd, LoggingPayDate,LoggingFraction, LoggingForwardRate, LoggingAdj, LoggingCpnFix, LoggingCpnRate, LoggingRawCpn, LoggingDF], index = ["Start","End","EstStart","EstEnd","Pay","Frac","ForwardRate","ConvAdj","CpnFixed","Cpn","RawCpn","DF"]).T               
        if (len(DiscCurveName) > 0) : 
            LoggingDF["DiscCurve"] = DiscCurveName
            LoggingDF["EstCurve"] = DiscCurveName if len(EstZeroCurveTerm) == 0 else EstCurveName
        LoggingDF["AccruedT"] = AccruedT
        LoggingDF["AI"] = AI

        LoggingDF["Price"] = s
        ColList2 = ["Leg2_" + str(s) for s in LoggingDF.columns]
        LoggingDF.columns = ColList2
        pd.concat([df, LoggingDF],axis = 1).to_csv(LoggingDir + "\\LoggingFilesIRS.csv", index = False, encoding = "cp949")
    AIList[0] = AI
    return s                               

def Calc_Bond_PV01(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                    PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
                    NumCpnOneYear, DayCountFlag, KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [],
                    EstZeroCurveRate = [], FixingHolidayList = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False,
                    LoggingFlag = 0, LoggingDir = '', ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], 
                    LookBackDays = 0, ObservShift = False, DiscCurveName= "", EstCurveName = "", YTMPricing = False, AIList = [0]) :
    MaturityToPayDate = max(0, MaturityToPayDate)    
    Preprocessing_ZeroTermAndRate(ZeroCurveTerm, ZeroCurveRate, int(PriceDateYYYYMMDD))
    P = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
            PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
            NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
            EstZeroCurveRate , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
            LoggingFlag, LoggingDir, ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift, DiscCurveName, EstCurveName, YTMPricing = YTMPricing, AIList = AIList)

    ResultArray = np.zeros(len(ZeroCurveRate))
    for i in range(len(ZeroCurveTerm)) : 
        ZeroUp = np.array(ZeroCurveRate).copy()
        ZeroUp[i] += 0.0001
        Pu = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroUp, 
                NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
                EstZeroCurveRate , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
                0, '', ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift , YTMPricing = YTMPricing)

        ResultArray[i] = Pu - P
        
    if (len(EstZeroCurveRate) > 0 and len(EstZeroCurveTerm) > 0 and len(EstZeroCurveRate) == len(EstZeroCurveTerm)) : 
        Preprocessing_ZeroTermAndRate(EstZeroCurveTerm, EstZeroCurveRate, int(PriceDateYYYYMMDD))
        ResultArray2 = np.zeros(len(EstZeroCurveTerm))
        for i in range(len(EstZeroCurveRate)) : 
            ZeroUp = np.array(EstZeroCurveRate).copy()
            ZeroUp[i] += 0.0001            
            Pu = Calc_Bond(Nominal, NominalFlag, FloatFlag, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
                    PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
                    NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm ,
                    ZeroUp , FixingHolidayList , AdditionalPayHolidayList , NominalDateIsNominalPayDate ,
                    0, '', ModifiedFollow , OverNightRateDateHistory, OverNightRateHistory , LookBackDays , ObservShift , YTMPricing = YTMPricing)
            ResultArray2[i] = Pu - P

        df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
        df2.columns = ["PV01Term","PV01"]
        df3 = pd.Series(ResultArray2, index = EstZeroCurveTerm).reset_index()
        df3.columns = ["PV01TermEst","PVEst01"]
        if LoggingFlag > 0 : 
            df = ReadCSV(LoggingDir + "\\LoggingFilesBond.csv")
            GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
            CSR_RiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)   
            DataGIRR = MapGIRRDeltaGreeks(df2.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
            DataGIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
            DataGIRR2 = MapGIRRDeltaGreeks(df3.set_index("PV01TermEst")["PVEst01"], GIRR_DeltaRiskFactor).reset_index()
            DataGIRR2.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
            DataCSR = MapCSRDeltaGreeks(df2.set_index("PV01Term")["PV01"], CSR_RiskFactor).reset_index()
            DataCSR.columns = ["CSR_Tenor","CSR_Delta_Sensi"]       
            DataCSR2 = MapCSRDeltaGreeks(df3.set_index("PV01TermEst")["PVEst01"], CSR_RiskFactor).reset_index()
            DataCSR2.columns = ["CSR_Tenor","CSR_Delta_Sensi"]                   
            pd.concat([df, df2, df3, DataGIRR, DataGIRR2, DataCSR, DataCSR2],axis = 1).to_csv(LoggingDir + "\\LoggingFilesBond.csv", index = False, encoding = "cp949")
        return P, df2, df3

    df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
    df2.columns = ["PV01Term","PV01"]
    if LoggingFlag > 0 : 
        df = ReadCSV(LoggingDir + "\\LoggingFilesBond.csv")
        GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
        DataGIRR = MapGIRRDeltaGreeks(df2.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
        DataGIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
        CSR_RiskFactor = pd.Series([0.5, 1, 3, 5, 10], dtype = np.float64)   
        DataCSR = MapCSRDeltaGreeks(df2.set_index("PV01Term")["PV01"], CSR_RiskFactor).reset_index()
        DataCSR.columns = ["CSR_Tenor","CSR_Delta_Sensi"]       
        pd.concat([df, df2, DataGIRR, DataCSR],axis = 1).to_csv(LoggingDir + "\\LoggingFilesBond.csv", index = False, encoding = "cp949")
    return P, df2, df2           
    
def Calc_Schedule_ErrorCheck(Nominal, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, ZeroCurveTerm, 
                              ZeroCurveRate, NumCpnOneYear, DayCountFlag) : 
    ErrorFlag = 0
    ErrorString = ""
    if (Nominal < 0) :
        ErrorString += "\nCheck Nominal < 0"
        ErrorFlag = 1
        
    if (PriceDateYYYYMMDD > MaturityYYYYMMDD) :
        ErrorString += "\nCheck PriceDate > Maturity"
        ErrorFlag = 1
        
    if (EffectiveDateYYYYMMDD > MaturityYYYYMMDD) : 
        ErrorString += "\nCheck EffectiveDate > Maturity"
        ErrorFlag = 1
        
    if (len(ZeroCurveTerm) == 0 and len(ZeroCurveRate) == 0) : 
        ErrorString += "\nCheck ZeroCurveTerm Length = 0"
        ErrorFlag = 1
        
    if (PriceDateYYYYMMDD < 19000000) : 
        ErrorString += "\nPriceDate < 19000101"
        ErrorFlag = 1

    if (EffectiveDateYYYYMMDD < 19000000) : 
        ErrorString += "\nEffectiveDate < 19000101"
        ErrorFlag = 1

    if (MaturityYYYYMMDD < 19000000) : 
        ErrorString += "\nMaturity < 19000101"
        ErrorFlag = 1

    if (NumCpnOneYear < 0 ) : 
        ErrorString += "\nNumCpnOneYear < 0"
        ErrorFlag = 1

    if (DayCountFlag < 0 ) : 
        ErrorString += "\nDayCountFlag < 0"
        ErrorFlag = 1
        
    return ErrorFlag, ErrorString
    
def Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [], EstZeroCurveRate = [], FixingHolidayList = [], 
             AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], LookBackDays = 0, ObservShift = False, 
             FixedPayerFlag = 0, DiscCurveNameLeg1 = "", EstCurveNameLeg1 = "", DiscCurveNameLeg2 = "", EstCurveNameLeg2 = "", 
             CMSFlag = 0, RefSwapMaturity_T = 0.25, RefSwapNCPNAnn = 4, TermVol = [], Vol = [] ) :
    
    LoggingFlag1, LoggingFlag2 = 0,0
    if LoggingFlag > 0 : 
        LoggingFlag1, LoggingFlag2 = 1, 2 

    Preprocessing_ZeroTermAndRate(ZeroCurveTerm, ZeroCurveRate, PriceDateYYYYMMDD)
    
    FixedLeg = Calc_Bond(Nominal, 0, 0, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
              PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTerm, ZeroCurveRate, 
              NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTerm,
              EstZeroCurveRate = EstZeroCurveTerm, FixingHolidayList = FixingHolidayList, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
              LoggingFlag = LoggingFlag1, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, OverNightRateDateHistory = OverNightRateDateHistory, OverNightRateHistory = OverNightRateHistory, LookBackDays = LookBackDays, ObservShift = ObservShift, DiscCurveName = DiscCurveNameLeg1, EstCurveName = EstCurveNameLeg1)

    if len(EstZeroCurveTerm) > 0 and len(EstZeroCurveRate) > 0 : 
        Preprocessing_ZeroTermAndRate(EstZeroCurveTerm, EstZeroCurveRate, PriceDateYYYYMMDD)

    FloatLeg = Calc_Bond(Nominal, 0, 1 if LookBackDays== 0 else 2, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
            PriceDateYYYYMMDD, MaturityYYYYMMDD, 0.0, ZeroCurveTerm, ZeroCurveRate, 
            NumCpnOneYear, DayCountFlag, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTerm,
            EstZeroCurveRate = EstZeroCurveRate, FixingHolidayList = FixingHolidayList, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
            LoggingFlag = LoggingFlag2, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, OverNightRateDateHistory = OverNightRateDateHistory, OverNightRateHistory = OverNightRateHistory, LookBackDays = LookBackDays, ObservShift = ObservShift, DiscCurveName= DiscCurveNameLeg2, EstCurveName = EstCurveNameLeg2,
            CMSFlag = CMSFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNAnn, TermVol = TermVol, Vol = Vol)
    
    return FixedLeg - FloatLeg if FixedPayerFlag == 0 else FloatLeg - FixedLeg    
    
def Calc_IRS_PV01(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday = True, MaturityToPayDate = 0, EstZeroCurveTerm = [], EstZeroCurveRate = [], FixingHolidayList = [], 
             AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = False, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1, OverNightRateDateHistory = [], OverNightRateHistory = [], LookBackDays = 0, ObservShift = False, 
             FixedPayerFlag = 0, DiscCurveNameLeg1 = "", EstCurveNameLeg1 = "", DiscCurveNameLeg2 = "", EstCurveNameLeg2 = "",
             CMSFlag = 0, RefSwapMaturity_T = 0.25, RefSwapNCPNAnn = 4, TermVol = [], Vol = []) : 
    LookBackDays = max(0, LookBackDays)
    
    P = Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm , EstZeroCurveRate , FixingHolidayList , 
             AdditionalPayHolidayList , NominalDateIsNominalPayDate , LoggingFlag , LoggingDir , 
             ModifiedFollow , OverNightRateDateHistory , OverNightRateHistory , LookBackDays , ObservShift, 
             FixedPayerFlag, DiscCurveNameLeg1 = DiscCurveNameLeg1, EstCurveNameLeg1 = EstCurveNameLeg1, DiscCurveNameLeg2 = DiscCurveNameLeg2, EstCurveNameLeg2 = EstCurveNameLeg2,
             CMSFlag = CMSFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNAnn, TermVol = TermVol, Vol = Vol)

    ResultArray = np.zeros(len(ZeroCurveRate))
    for i in range(len(ZeroCurveTerm)) : 
        ZeroUp = np.array(ZeroCurveRate).copy()
        ZeroUp[i] += 0.0001
        Pu = Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroUp, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm , EstZeroCurveRate , FixingHolidayList , 
             AdditionalPayHolidayList , NominalDateIsNominalPayDate , LoggingFlag , LoggingDir , 
             ModifiedFollow , OverNightRateDateHistory , OverNightRateHistory , LookBackDays , ObservShift, 
             FixedPayerFlag, DiscCurveNameLeg1 = DiscCurveNameLeg1, EstCurveNameLeg1 = EstCurveNameLeg1, DiscCurveNameLeg2 = DiscCurveNameLeg2, EstCurveNameLeg2 = EstCurveNameLeg2,
             CMSFlag = CMSFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNAnn, TermVol = TermVol, Vol = Vol)

        ResultArray[i] = Pu - P
        
    if (len(EstZeroCurveRate) > 0 and len(EstZeroCurveTerm) > 0 and len(EstZeroCurveRate) == len(EstZeroCurveTerm)) : 
        ResultArray2 = np.zeros(len(EstZeroCurveTerm))
        for i in range(len(EstZeroCurveRate)) : 
            ZeroUp = np.array(EstZeroCurveRate).copy()
            ZeroUp[i] += 0.0001            
            Pu = Calc_IRS(Nominal, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTerm, ZeroCurveRate, NumCpnOneYear, DayCountFlag, 
             KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm , ZeroUp , FixingHolidayList , 
             AdditionalPayHolidayList , NominalDateIsNominalPayDate , LoggingFlag , LoggingDir , 
             ModifiedFollow , OverNightRateDateHistory , OverNightRateHistory , LookBackDays , ObservShift, 
             FixedPayerFlag, DiscCurveNameLeg1 = DiscCurveNameLeg1, EstCurveNameLeg1 = EstCurveNameLeg1, DiscCurveNameLeg2 = DiscCurveNameLeg2, EstCurveNameLeg2 = EstCurveNameLeg2,
             CMSFlag = CMSFlag, RefSwapMaturity_T = RefSwapMaturity_T, RefSwapNCPNAnn = RefSwapNCPNAnn, TermVol = TermVol, Vol = Vol)
            ResultArray2[i] = Pu - P

        df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
        df2.columns = ["PV01Term","PV01"]
        df3 = pd.Series(ResultArray2, index = EstZeroCurveTerm).reset_index()
        df3.columns = ["PV01TermEst","PVEst01"]
        if LoggingFlag > 0 : 
            df = ReadCSV(LoggingDir + "\\LoggingFilesIRS.csv")
            GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
            DataGIRR = MapGIRRDeltaGreeks(df2.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
            DataGIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
            DataGIRR2 = MapGIRRDeltaGreeks(df3.set_index("PV01TermEst")["PVEst01"], GIRR_DeltaRiskFactor).reset_index()
            DataGIRR2.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
            pd.concat([df, df2, df3, DataGIRR, DataGIRR2],axis = 1).to_csv(LoggingDir + "\\LoggingFilesIRS.csv", index = False, encoding = "cp949")
        return P, df2, df3

    df2 = pd.Series(ResultArray, index = ZeroCurveTerm).reset_index()
    df2.columns = ["PV01Term","PV01"]
    df3 = pd.DataFrame([], columns = ["PV01TermEst","PVEst01"], index = [0.0]).fillna(0)
    if LoggingFlag > 0 : 
        df = ReadCSV(LoggingDir + "\\LoggingFilesIRS.csv")
        GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
        DataGIRR = MapGIRRDeltaGreeks(df2.set_index("PV01Term")["PV01"], GIRR_DeltaRiskFactor).reset_index()
        DataGIRR.columns = ["GIRR_Tenor","GIRR_Delta_Sensi"] 
        pd.concat([df, df2, DataGIRR],axis = 1).to_csv(LoggingDir + "\\LoggingFilesIRS.csv", index = False, encoding = "cp949")
    return P, df2, df3          
    
def Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
             DayCountFlagForeign, KoreanHoliday = False, MaturityToPayDate = 0, EstZeroCurveTermDomestic = [], EstZeroCurveRateDomestic = [], 
             EstZeroCurveTermForeign = [], EstZeroCurveRateForeign = [], ZeroCurveTermForeign = [], ZeroCurveRateForeign = [], FixingHolidayListDomestic = [], 
             FixingHolidayListForeign = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = True, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1,LookBackDaysDomestic = 0, LookBackDaysForeign = 0, ObservShift = False, DomesticPayerFlag = 0, 
             DiscCurveName = "", EstCurveName = "", ValuationDomesticFX = 1.0, ValuationForeignFX = 1.0, SOFRFlag = False, FixFixFlag = False, FirstFloatFixRateForeign = 0, DiscCurveNameForeign = "", EstCurveNameForeign = "") :
    
    FirstFloatFixRateForeign = FirstFloatFixRate if FirstFloatFixRateForeign == 0 else FirstFloatFixRateForeign
    ValuationFlag = 1 if int(PriceDateYYYYMMDD) > int(EffectiveDateYYYYMMDD) else 0
    LoggingFlag1, LoggingFlag2 = 0,0
    if LoggingFlag > 0 : 
        LoggingFlag1, LoggingFlag2 = 1, 2 

    Preprocessing_ZeroTermAndRate(ZeroCurveTermDomestic, ZeroCurveRateDomestic, PriceDateYYYYMMDD)
    if len(EstZeroCurveTermDomestic) > 0 and len(EstZeroCurveRateDomestic) > 0 : 
        Preprocessing_ZeroTermAndRate(EstZeroCurveTermDomestic, EstZeroCurveRateDomestic, PriceDateYYYYMMDD)
        
    if len(ZeroCurveTermForeign) > 0 and len(ZeroCurveRateForeign)  : 
        Preprocessing_ZeroTermAndRate(ZeroCurveTermForeign, ZeroCurveRateForeign, PriceDateYYYYMMDD)
        
    if len(ZeroCurveTermForeign) > 0 and len(ZeroCurveRateForeign)  : 
        Preprocessing_ZeroTermAndRate(ZeroCurveTermForeign, ZeroCurveRateForeign, PriceDateYYYYMMDD)
    
    FloatFlagDomestic = 0
    FloatFlagForeign = 1 if SOFRFlag == False else 2
    if len(EstZeroCurveRateDomestic) > 0 : 
        FloatFlagDomestic = 1 if SOFRFlag == False else 2
    if FixFixFlag == True : 
        FloatFlagDomestic, FloatFlagForeign = 0, 0
                 
    FixedLeg = Calc_Bond(NominalDomestic, 1, FloatFlagDomestic, FirstFloatFixRate, EffectiveDateYYYYMMDD, 
              PriceDateYYYYMMDD, MaturityYYYYMMDD, CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, 
              NumCpnOneYear, DayCountFlagDomestic, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTermDomestic,
              EstZeroCurveRate = EstZeroCurveRateDomestic, FixingHolidayList = FixingHolidayListDomestic, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
              LoggingFlag = LoggingFlag1, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, LookBackDays = LookBackDaysDomestic, ObservShift = ObservShift, DiscCurveName = DiscCurveName, EstCurveName = EstCurveName)

    FloatLeg = Calc_Bond(NominalForeign, 1, FloatFlagForeign, FirstFloatFixRateForeign, EffectiveDateYYYYMMDD, 
            PriceDateYYYYMMDD, MaturityYYYYMMDD, 0.0, ZeroCurveTermForeign, ZeroCurveRateForeign, 
            NumCpnOneYear, DayCountFlagForeign, KoreanHoliday , MaturityToPayDate , EstZeroCurveTerm = EstZeroCurveTermForeign,
            EstZeroCurveRate = EstZeroCurveRateForeign, FixingHolidayList = FixingHolidayListForeign, AdditionalPayHolidayList  = AdditionalPayHolidayList, NominalDateIsNominalPayDate = NominalDateIsNominalPayDate,
            LoggingFlag = LoggingFlag2, LoggingDir = LoggingDir, ModifiedFollow = ModifiedFollow, LookBackDays = LookBackDaysForeign, ObservShift = ObservShift, DiscCurveName = DiscCurveNameForeign, EstCurveName = EstCurveNameForeign)
    if ValuationFlag == 0 : 
        return FixedLeg - FloatLeg * NominalDomestic/NominalForeign if DomesticPayerFlag == 0 else FloatLeg * NominalDomestic/NominalForeign - FixedLeg    
    else : 
        return FixedLeg *ValuationDomesticFX - FloatLeg *ValuationForeignFX if DomesticPayerFlag == 0 else FloatLeg *ValuationForeignFX - FixedLeg *ValuationDomesticFX    

def CalC_CRS_PV01(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
             CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
             DayCountFlagForeign, KoreanHoliday = False, MaturityToPayDate = 0, EstZeroCurveTermDomestic = [], EstZeroCurveRateDomestic = [], 
             EstZeroCurveTermForeign = [], EstZeroCurveRateForeign = [], ZeroCurveTermForeign = [], ZeroCurveRateForeign = [], FixingHolidayListDomestic = [], 
             FixingHolidayListForeign = [], AdditionalPayHolidayList  = [], NominalDateIsNominalPayDate = True, LoggingFlag = 0, LoggingDir = '', 
             ModifiedFollow = 1,LookBackDaysDomestic = 0, LookBackDaysForeign = 0, ObservShift = False, DomesticPayerFlag = 0, 
             DiscCurveName = "", EstCurveName = "", ValuationDomesticFX = 1.0, ValuationForeignFX = 1.0, SOFRFlag = False, FixFixFlag = False, FirstFloatFixRateForeign = 0, DiscCurveNameForeign = "", EstCurveNameForeign = "", DomesticParallelUp = False, ForeignParallelUp = False) : 

    P = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign )

    ResultArray = np.zeros(len(ZeroCurveTermDomestic))
    if DomesticParallelUp == False : 
        for i in range(len(ZeroCurveTermDomestic)) : 
            ZeroUp = np.array(ZeroCurveRateDomestic).copy()
            ZeroUp[i] += 0.0001
            Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                    CpnRate, ZeroCurveTermDomestic, ZeroUp, NumCpnOneYear, DayCountFlagDomestic, 
                    DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                    EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                    FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                    ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                    DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

            ResultArray[i] = Pu - P
    else : 
        ZeroUp = np.array(ZeroCurveRateDomestic).copy()
        ZeroUp = ZeroUp + 0.0001
        Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                CpnRate, ZeroCurveTermDomestic, ZeroUp, NumCpnOneYear, DayCountFlagDomestic, 
                DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

        ResultArray[0] = Pu - P

    ResultArray2 = np.zeros(len(ZeroCurveTermForeign))
    if ForeignParallelUp == False : 
        for i in range(len(ZeroCurveTermForeign)) : 
            ZeroUp = np.array(ZeroCurveRateForeign).copy()
            ZeroUp[i] += 0.0001
            Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                    CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                    DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                    EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroUp, FixingHolidayListDomestic, 
                    FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                    ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                    DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

            ResultArray2[i] = Pu - P
    else : 
        ZeroUp = np.array(ZeroCurveRateForeign).copy()
        ZeroUp = ZeroUp + 0.0001
        Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroUp, FixingHolidayListDomestic, 
                FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

        ResultArray2[0] = Pu - P

    ResultArray3 = np.zeros(len(EstZeroCurveTermDomestic))
    if len(EstZeroCurveTermDomestic) > 0 :
        for i in range(len(EstZeroCurveTermDomestic)) : 
            ZeroUp = np.array(EstZeroCurveRateDomestic).copy()
            ZeroUp[i] += 0.0001
            Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                    CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                    DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , ZeroUp, 
                    EstZeroCurveTermForeign, EstZeroCurveRateForeign, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                    FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                    ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                    DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

            ResultArray3[i] = Pu - P        

    ResultArray4 = np.zeros(len(EstZeroCurveTermForeign))
    if len(EstZeroCurveTermForeign) > 0 : 
        for i in range(len(EstZeroCurveTermForeign)) : 
            ZeroUp = np.array(EstZeroCurveRateForeign).copy()
            ZeroUp[i] += 0.0001
            Pu = Calc_CRS(NominalDomestic, NominalForeign, FirstFloatFixRate, EffectiveDateYYYYMMDD, PriceDateYYYYMMDD, MaturityYYYYMMDD, 
                    CpnRate, ZeroCurveTermDomestic, ZeroCurveRateDomestic, NumCpnOneYear, DayCountFlagDomestic, 
                    DayCountFlagForeign, KoreanHoliday, MaturityToPayDate, EstZeroCurveTermDomestic , EstZeroCurveRateDomestic, 
                    EstZeroCurveTermForeign, ZeroUp, ZeroCurveTermForeign, ZeroCurveRateForeign, FixingHolidayListDomestic, 
                    FixingHolidayListForeign, AdditionalPayHolidayList, NominalDateIsNominalPayDate, LoggingFlag, LoggingDir, 
                    ModifiedFollow,LookBackDaysDomestic, LookBackDaysForeign, ObservShift, DomesticPayerFlag, 
                    DiscCurveName, EstCurveName , ValuationDomesticFX, ValuationForeignFX, SOFRFlag, FixFixFlag, FirstFloatFixRateForeign, DiscCurveNameForeign, EstCurveNameForeign)

            ResultArray4[i] = Pu - P        
            
    df = pd.Series(ResultArray, index = ZeroCurveTermDomestic).reset_index()
    df.columns = ["PV01TermDomesticDisc","PV01DomesticDisc"]
    df2 = pd.Series(ResultArray2, index = ZeroCurveTermForeign).reset_index()
    df2.columns = ["PV01TermForeignDisc","PV01ForeignDisc"]    
    df3 = pd.Series(ResultArray3, index = EstZeroCurveTermDomestic).reset_index()
    df3.columns = ["PV01TermDomesticEst","PV01DomesticEst"]
    df4 = pd.Series(ResultArray4, index = EstZeroCurveTermForeign).reset_index()
    df4.columns = ["PV01TermForeignEst","PV01ForeignEst"]
    if LoggingFlag > 0 : 
        MyData = ReadCSV(LoggingDir + "\\LoggingFilesIRS.csv")
        GIRR_DeltaRiskFactor = pd.Series([0.25, 0.5, 1, 2, 3, 5, 10, 15, 20, 30], dtype = np.float64)
        Data_GIRR1 = MapGIRRDeltaGreeks(df.set_index("PV01TermDomesticDisc")["PV01DomesticDisc"], GIRR_DeltaRiskFactor).reset_index()
        Data_GIRR1.columns = ["Leg1Disc_GIRR_Tenor","Leg1Disc_GIRR_Delta_Sensi"]
        Data_GIRR2 = MapGIRRDeltaGreeks(df2.set_index("PV01TermForeignDisc")["PV01ForeignDisc"], GIRR_DeltaRiskFactor).reset_index()
        Data_GIRR2.columns = ["Leg2Disc_GIRR_Tenor","Leg2Disc_GIRR_Delta_Sensi"]
        Data_GIRR3 = MapGIRRDeltaGreeks(df3.set_index("PV01TermDomesticEst")["PV01DomesticEst"], GIRR_DeltaRiskFactor).reset_index()
        Data_GIRR3.columns = ["Leg1Est_GIRR_Tenor","Leg1Est_GIRR_Delta_Sensi"]
        Data_GIRR4 = MapGIRRDeltaGreeks(df4.set_index("PV01TermForeignEst")["PV01ForeignEst"], GIRR_DeltaRiskFactor).reset_index()
        Data_GIRR4.columns = ["Leg2Est_GIRR_Tenor","Leg2Est_GIRR_Delta_Sensi"]
        pd.concat([MyData, df, df2, df3, df4, Data_GIRR1, Data_GIRR2, Data_GIRR3, Data_GIRR4],axis = 1).to_csv(LoggingDir + "\\LoggingFilesIRS.csv", index = False, encoding = "cp949")
        
    return P, df, df2, df3, df4

def Calc_Current_FXForward(Spot, T, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, SpotT = 0) : 
    if SpotT == 0 :         
        rd = Linterp(DomesticTerm, DomesticRate, T)
        rf = Linterp(ForeignTerm, ForeignRate, T)
        DF_d = np.exp(-rd * T)
        DF_f = np.exp(-rf * T)
    else : 
        DF_d = Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T)
        DF_f = Calc_ForwardDiscount_Factor(ForeignTerm, ForeignRate, SpotT, T)        
    return Spot * DF_f/DF_d
    
def Calc_Value_FXSwap(Spot, T1, T2, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, long0short1, SpotT = 0, NominalForeign = 100, ForwardPrice1 = 0, ForwardPrice2 = 0) : 
    if (T1 >= 0.0) : 
        F1 = NominalForeign * Calc_ForwardDiscount_Factor(ForeignTerm, ForeignRate, SpotT, T1)
        if ForwardPrice1 == 0 : 
            D1 = NominalForeign * Calc_Current_FXForward(Spot, T1, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, SpotT) * Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T1)
        else : 
            D1 = NominalForeign * ForwardPrice1 * Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T1)
    else :
        D1, F1 = 0, 0
    F2 = NominalForeign * Calc_ForwardDiscount_Factor(ForeignTerm, ForeignRate, SpotT, T2)
    if ForwardPrice2 == 0 : 
        D2 = NominalForeign * Calc_Current_FXForward(Spot, T2, DomesticTerm, DomesticRate, ForeignTerm, ForeignRate, SpotT) * Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T2)
    else : 
        D2 = NominalForeign * ForwardPrice2 * Calc_ForwardDiscount_Factor(DomesticTerm, DomesticRate, SpotT, T2)
        
    VF = F1 - F2 if long0short1 == 0 else F2 - F1
    VD = - D1 + D2 if long0short1 == 0 else D1 - D2
    P = VF * Spot - VD if long0short1 == 0 else VF * Spot - VD
    return P, VD, VF

def BS_Cap(
    NA,                # 액면금액
    VolFlag,           # 0: Black Vol, 1: Normal Vol
    Vol,               # 변동성
    DF,                # 할인계수 리스트 (길이: nDates + 1)
    StrikeRate,        # 행사금리
    Dates,             # 각 지급일까지의 일수 리스트 (길이: nDates)
    FirstStartDay,     # 첫 시작일
    FirstFixingRate,   # 첫 추정금리
    AverageFlag,       # 평균 계산 여부
    deltat,            # 각 기간에 대한 델타 리스트
    AllStrikeATMFlag,  # 1: F를 행사금리로 사용, 2: swaprate 사용
    swaprate           # 스왑레이트
):
    PrevT = FirstStartDay / 365.0
    value = 0.0
    nDates = len(Dates)
    
    if AverageFlag == 0:
        if VolFlag == 0:  # Black vol
            
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                F = (PrevDisc / Disc - 1.0) / delta
                if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                    F = FirstFixingRate

                if i == 0:
                    if PrevT <= 0.0:
                        if F > StrikeRate:
                            value = deltat[i] * Disc * (F - StrikeRate)
                    else:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (np.log(F / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (F * CDF_N(d1) - StrikeRate * CDF_N(d2))
                else:
                    if F > 0.0:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (np.log(F / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (F * CDF_N(d1) - StrikeRate * CDF_N(d2))
                    else:
                        value += 1e-13
                PrevT = T
        else:  # Normal vol
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                F = (PrevDisc / Disc - 1.0) / delta
                if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                    F = FirstFixingRate

                if i == 0:
                    if PrevT <= 0.0:
                        if F > StrikeRate:
                            value = deltat[i] * Disc * (F - StrikeRate)
                    else:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (F - StrikeRate) / (Vol * np.sqrt(PrevT))
                        value += deltat[i] * Disc * (
                            (F - StrikeRate) * CDF_N(d1) + Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                        )
                else:
                    if AllStrikeATMFlag == 1:
                        StrikeRate = F
                    elif AllStrikeATMFlag == 2:
                        StrikeRate = swaprate
                    d1 = (F - StrikeRate) / (Vol * np.sqrt(PrevT))
                    value += deltat[i] * Disc * (
                        (F - StrikeRate) * CDF_N(d1) + Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                    )

                PrevT = T
    else:
        F_Avg = 0.0
        for i in range(nDates):
            T = Dates[i] / 365.0
            delta = T - PrevT

            PrevDisc = DF[i]
            Disc = DF[i + 1]

            F = (PrevDisc / Disc - 1.0) / delta
            if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                F = FirstFixingRate

            F_Avg += F / nDates
            PrevT = T

        PrevT = FirstStartDay / 365.0
        for i in range(nDates):
            T = Dates[i] / 365.0
            delta = T - PrevT

            PrevDisc = DF[i]
            Disc = DF[i + 1]

            if VolFlag == 0:
                if i == 0:
                    if PrevT <= 0.0 and F_Avg > StrikeRate:
                        value = deltat[i] * Disc * (F_Avg - StrikeRate)
                    else:
                        d1 = (np.log(F_Avg / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (F_Avg * CDF_N(d1) - StrikeRate * CDF_N(d2))
                else:
                    if F_Avg > 0.0:
                        d1 = (np.log(F_Avg / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (F_Avg * CDF_N(d1) - StrikeRate * CDF_N(d2))
                    else:
                        value += 1e-13
            else:
                if i == 0:
                    if PrevT <= 0.0 and F_Avg > StrikeRate:
                        value = deltat[i] * Disc * (F_Avg - StrikeRate)
                    else:
                        d1 = (F_Avg - StrikeRate) / (Vol * np.sqrt(PrevT))
                        value += deltat[i] * Disc * (
                            (F_Avg - StrikeRate) * CDF_N(d1) + Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                        )
                else:
                    d1 = (F_Avg - StrikeRate) / (Vol * np.sqrt(PrevT))
                    value += deltat[i] * Disc * (
                        (F_Avg - StrikeRate) * CDF_N(d1) + Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                    )
            PrevT = T
    
    return NA * value    
    
def BS_Floor(
    NA,                  # 액면금액
    VolFlag,             # 0: Black Vol, 1: Normal Vol
    Vol,                 # 변동성
    DF,                  # 할인계수 리스트 (nDates + 1)
    StrikeRate,          # 행사금리
    Dates,               # 각 지급일까지의 일수 리스트 (길이: nDates)
    FirstStartDay,
    FirstFixingRate,
    AverageFlag,
    deltat,              # 기간별 델타 리스트 (길이: nDates)
    AllStrikeATMFlag,
    swaprate
):
    PrevT = FirstStartDay / 365.0
    value = 0.0
    nDates = len(Dates)

    if AverageFlag == 0:
        if VolFlag == 0:  # Black vol
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                F = (PrevDisc / Disc - 1.0) / delta
                if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                    F = FirstFixingRate

                if i == 0:
                    if PrevT <= 0.0:
                        if F < StrikeRate:
                            value = deltat[i] * Disc * (StrikeRate - F)
                    else:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (np.log(F / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (-F * CDF_N(-d1) + StrikeRate * CDF_N(-d2))
                else:
                    if F > 0.0:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (np.log(F / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (-F * CDF_N(-d1) + StrikeRate * CDF_N(-d2))
                    else:
                        value += 1e-13

                PrevT = T
        else:  # Normal vol
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                F = (PrevDisc / Disc - 1.0) / delta
                if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                    F = FirstFixingRate

                if i == 0:
                    if PrevT <= 0.0:
                        if F < StrikeRate:
                            value = deltat[i] * Disc * (StrikeRate - F)
                    else:
                        if AllStrikeATMFlag == 1:
                            StrikeRate = F
                        elif AllStrikeATMFlag == 2:
                            StrikeRate = swaprate
                        d1 = (F - StrikeRate) / (Vol * np.sqrt(PrevT))
                        value += deltat[i] * Disc * (
                            (StrikeRate - F) * CDF_N(-d1) +
                            Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                        )
                else:
                    if AllStrikeATMFlag == 1:
                        StrikeRate = F
                    elif AllStrikeATMFlag == 2:
                        StrikeRate = swaprate
                    d1 = (F - StrikeRate) / (Vol * np.sqrt(PrevT))
                    value += deltat[i] * Disc * (
                        (StrikeRate - F) * CDF_N(-d1) +
                        Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                    )

                PrevT = T
    else:
        F_Avg = 0.0
        for i in range(nDates):
            T = Dates[i] / 365.0
            delta = T - PrevT

            PrevDisc = DF[i]
            Disc = DF[i + 1]

            F = (PrevDisc / Disc - 1.0) / delta
            if abs(FirstFixingRate) > 1e-6 and (PrevT <= 0 and T > 0):
                F = FirstFixingRate

            F_Avg += F / nDates
            PrevT = T

        PrevT = FirstStartDay / 365.0
        if VolFlag == 0:
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                if i == 0:
                    if PrevT <= 0.0:
                        if F_Avg < StrikeRate:
                            value = deltat[i] * Disc * (StrikeRate - F_Avg)
                    else:
                        d1 = (np.log(F_Avg / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (-F_Avg * CDF_N(-d1) + StrikeRate * CDF_N(-d2))
                else:
                    if F_Avg > 0.0:
                        d1 = (np.log(F_Avg / StrikeRate) + 0.5 * Vol ** 2 * PrevT) / (Vol * np.sqrt(PrevT))
                        d2 = d1 - Vol * np.sqrt(PrevT)
                        value += deltat[i] * Disc * (-F_Avg * CDF_N(-d1) + StrikeRate * CDF_N(-d2))
                    else:
                        value += 1e-13

                PrevT = T
        else:  # Normal vol
            for i in range(nDates):
                T = Dates[i] / 365.0
                delta = T - PrevT

                PrevDisc = DF[i]
                Disc = DF[i + 1]

                if i == 0:
                    if PrevT <= 0.0:
                        if F_Avg < StrikeRate:
                            value = deltat[i] * Disc * (StrikeRate - F_Avg)
                    else:
                        d1 = (F_Avg - StrikeRate) / (Vol * np.sqrt(PrevT))
                        value += deltat[i] * Disc * (
                            (StrikeRate - F_Avg) * CDF_N(-d1) +
                            Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                        )
                else:
                    d1 = (F_Avg - StrikeRate) / (Vol * np.sqrt(PrevT))
                    value += deltat[i] * Disc * (
                        (StrikeRate - F_Avg) * CDF_N(-d1) +
                        Vol * np.sqrt(PrevT) * np.exp(-d1 ** 2 / 2) / 2.506628274631
                    )

                PrevT = T

    return NA * value    

def Pricing_CapFloor(
    CapFloorFlag,            # 0: Cap, 1: Floor
    PriceDate,
    StartDate,
    SwapMaturityDate,
    AnnCpnOneYear,
    NA,
    Vol,
    StrikePrice,
    UseStrikeAsAverage,
    Term,
    Rate,
    DayCountFracFlag,
    VolFlag,                # 0: Black, 1: Normal
    HolidayYYYYMMDD,
    FirstFixingRate,
    AverageFlag,
    AllStrikeATMFlag,
    ResultValue             # Output: length = 4 + NTerm (but only 2 values used)
):
    ResultCode = 0
    NHoliday = len(HolidayYYYYMMDD)
    if StrikePrice > 1 : 
        StrikePrice = StrikePrice /100
    if PriceDate < 19000000:
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    if StartDate < 19000000:
        StartDate = ExcelDateToYYYYMMDD(StartDate)
    if SwapMaturityDate < 19000000:
        SwapMaturityDate = ExcelDateToYYYYMMDD(SwapMaturityDate)
    Temp = [20000101]
    NBDayFromEndDate = NBusinessCountFromEndToPay(StartDate, SwapMaturityDate, HolidayYYYYMMDD,1, Temp)    
    StartDate = ParseBusinessDateIfHoliday(StartDate, HolidayYYYYMMDD)
    Preprocessing_ZeroTermAndRate(Term, Rate, PriceDate)
    
    EndYYYYMM = SwapMaturityDate // 100
    EndDD = StartDate % 100
    SwapMaturityDate = EndYYYYMM * 100 + EndDD

    TempDate = StartDate
    FixingDate, CpnDate, ResultPayDate, ResultNBD = MappingCouponDates(1,StartDate,SwapMaturityDate,NBDayFromEndDate,AnnCpnOneYear,1,HolidayYYYYMMDD,HolidayYYYYMMDD,1)
    NCpnDate = len(CpnDate)
    DaysCpnDate = [DayCountAtoB(PriceDate, d) for d in CpnDate]
    FirstStartDay = DayCountAtoB(PriceDate, StartDate)

    DF = [0.0] * (len(CpnDate) + 1)
    deltat = [0.0] * len(CpnDate)
    for i in range(len(CpnDate)):
        if i == 0:
            deltat[i] = DayCountFractionAtoB(StartDate, CpnDate[i], DayCountFracFlag)
        else:
            deltat[i] = DayCountFractionAtoB(CpnDate[i - 1], CpnDate[i], DayCountFracFlag)

    t = DayCountAtoB(PriceDate, StartDate) / 365.0
    r = Linterp(Term, Rate, t)
    DF[0] = np.exp(-r * t)

    for i in range(len(CpnDate)):
        t = DayCountAtoB(PriceDate, CpnDate[i]) / 365.0
        r = Linterp(Term, Rate, t)
        DF[i + 1] = np.exp(-r * t)

    if UseStrikeAsAverage > 0:
        F_Avg = 0.0
        PrevT = FirstStartDay / 365.0
        for i in range(len(CpnDate)):
            T = DaysCpnDate[i] / 365.0
            delta = T - PrevT
            PrevDisc = DF[i]
            Disc = DF[i + 1]
            F = (PrevDisc / Disc - 1.0) / delta
            if abs(FirstFixingRate) > 1e-6:
                F = FirstFixingRate
            F_Avg += F / len(CpnDate)
            PrevT = T
        StrikePrice = F_Avg

    swprate = FSR(PriceDate, StartDate, SwapMaturityDate, AnnCpnOneYear,DayCountFracFlag, HolidayYYYYMMDD, Term, Rate, Term, Rate )

    if CapFloorFlag == 0:
        swv = BS_Cap(NA, VolFlag, Vol, DF, StrikePrice,
                     DaysCpnDate, FirstStartDay,
                     FirstFixingRate, AverageFlag, deltat,
                     AllStrikeATMFlag, swprate)
    else:
        swv = BS_Floor(NA, VolFlag, Vol, DF, StrikePrice,
                       DaysCpnDate, FirstStartDay,
                       FirstFixingRate, AverageFlag, deltat,
                       AllStrikeATMFlag, swprate)

    ResultValue[0] = swv
    ResultValue[1] = swprate
    ResultValue[2] = StrikePrice if AllStrikeATMFlag != 2 else swprate

    return ResultValue

def CapFloorToImpliedVol(ZeroTerm, ZeroRate, PriceDate, StartDate, TenorYYYYMMDD, Quote, StrikePrice, NCPNOneYear = 4, CapFloorFlag = 0, NA = 100, DayCountFlag = 0, VolFlag = 0, Holidays = []) : 
    Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
    dblErrorRange = 0.00001
    ResultCapFloorImvol = []
    FwdSwpRate = []

    Calibration = True
    for i in range(len(TenorYYYYMMDD)) : 
        SwapMaturityDate = TenorYYYYMMDD[i]
        Price = float(Quote[i])
        MaxVol = 1.0
        MinVol = 0.000001
        TargetVol = MaxVol
        ResultValue = [0,0,0,0]
        for j in range(1000) : 
            Pricing_CapFloor(CapFloorFlag, PriceDate, StartDate, SwapMaturityDate, NCPNOneYear, 
                            NA, TargetVol, StrikePrice, 0, ZeroTerm, 
                            ZeroRate, DayCountFlag, VolFlag, Holidays, 0,
                            0, 2 if StrikePrice == 0 else 0, ResultValue)
            CalcRate = ResultValue[0]/NA - Price/NA
            if abs(CalcRate) < dblErrorRange : 
                break
            if (CalcRate > 0) : 
                MaxVol = TargetVol
            else : 
                MinVol = TargetVol
            TargetVol = (MinVol + MaxVol) / 2

        if j == 1000 : 
            VolRange = np.linspace(0.001, 0.101, 2001) * 10 ** (VolFlag == 0)

            Err = 100
            ResultValue2 = [0, 0, 0, 0]
            for j in range(len(VolRange)) : 
                TargetVol = VolRange[j]
                Pricing_CapFloor(CapFloorFlag, PriceDate, StartDate, SwapMaturityDate, NCPNOneYear, 
                                NA, TargetVol, StrikePrice, 0, ZeroTerm, 
                                ZeroRate, DayCountFlag, VolFlag, Holidays, 0,
                                0, 2 if StrikePrice == 0 else 0, ResultValue2)
                TempErr = ResultValue2[0]/NA - Price

                if abs(TempErr) < Err : 
                    Err = TempErr

                if Err < 0.001 : 
                    break 

        if j == 1000 :            
            print("VolCalibration Fail Tenor" + str(SwapMaturityDate))
            Calibration = False
        ResultCapFloorImvol.append(TargetVol)
        FwdSwpRate.append(ResultValue[1])
    ResultData = pd.DataFrame(ResultCapFloorImvol, index = TenorYYYYMMDD, columns = ["CapFloorVol"])
    return ResultData, ResultCapFloorImvol, FwdSwpRate, Calibration

def price_digital_forward(
    F,                  # forward rate
    K,                  # strike
    vol,                # volatility (Black vol or Normal vol)
    tau,                # time to maturity in years
    df,                 # discount factor P(t,T)
    notional,           # notional
    alpha = 1.0,        # day-count fraction
    option_type = "call",
    model = "black"
) -> float:
    """
    Price of a cash-or-nothing digital option on a forward rate under Black or Bachelier model.

    Payoff at T:
      call: notional * alpha * 1_{F_T >= K}
      put : notional * alpha * 1_{F_T <= K}

    Returns present value at t.
    """
    # sanity checks
    if tau < 0:
        raise ValueError("tau (time to maturity) must be >= 0")
    if df <= 0:
        raise ValueError("df (discount factor) must be > 0")
    if model not in ("black", "normal"):
        raise ValueError("model must be 'black' or 'normal'")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")

    # immediate expiry
    if tau == 0 or vol == 0:
        # deterministic forward at maturity:
        # tie-breaking at F==K -> 0.5 (continuous limit)
        if option_type == "call":
            ind = 1.0 if F > K else (0.0 if F < K else 0.5)
        else:
            ind = 1.0 if F < K else (0.0 if F > K else 0.5)
        return notional * alpha * df * ind

    if model == "black":
        if F <= 0 or K <= 0:
            raise ValueError("Black model requires positive F and K.")
        d1 = (np.log(F / K) + 0.5 * vol * vol * tau) / (vol * np.sqrt(tau))
        d2 = d1 - vol * np.sqrt(tau)
        prob = CDF_N(d2) if option_type == "call" else CDF_N(-d2)

    else:  # model == "normal" (Bachelier)
        d = (F - K) / (vol * np.sqrt(tau))
        prob = CDF_N(d) if option_type == "call" else CDF_N(-d)

    return notional * alpha * df * prob

def price_digital_rangeforward(
    F,                  # forward rate
    K1,                 # strike1
    K2,                 # strike2
    vol,                # volatility (Black vol or Normal vol)
    tau,                # time to maturity in years
    df,                 # discount factor P(t,T)
    notional,           # notional
    alpha = 1.0,        # day-count fraction
    model = "black"
) -> float:
    """
    Price of a cash-or-nothing digital range option on a forward rate under Black or Bachelier model.

    Payoff at T:
      notional * alpha * 1_{K2 >= F_T >= K1}

    Returns present value at t.
    """
    if K1 >= K2 : 
        raise ValueError("K2 must bigger than K1")
    tau = max(0.00001, tau)

    c1 = price_digital_forward(F,K1,vol,tau,df,notional,alpha,option_type = "call", model = model)
    c2 = -price_digital_forward(F,K2,vol,tau,df,notional,alpha,option_type = "call", model = model)
    return c1 + c2

def Gauss_Hermite_Normal(mu = 0, sigma = 1) : 
    x = np.zeros(20)    
    w = np.zeros(20)
    x[0] = 5.3874808900112328
    x[1] = 4.6036824495507442
    x[2] = 3.9447640401156252
    x[3] = 3.3478545673832163
    x[4] = 2.7888060584281305
    x[5] = 2.2549740020892757
    x[6] = 1.7385377121165861
    x[7] = 1.2340762153953231
    x[8] = 0.73747372854539428
    x[9] = 0.24534070830090124
    x[10] = -0.24534070830090124
    x[11] = -0.73747372854539428
    x[12] = -1.2340762153953231
    x[13] = -1.7385377121165861
    x[14] = -2.2549740020892757
    x[15] = -2.7888060584281305
    x[16] = -3.3478545673832163
    x[17] = -3.9447640401156252
    x[18] = -4.6036824495507442
    x[19] = -5.3874808900112328

    w[0] = 2.2293936455341523e-13
    w[1] = 4.3993409922731799e-10
    w[2] = 1.0860693707692815e-07
    w[3] = 7.8025564785320666e-06
    w[4] = 0.00022833863601635264
    w[5] = 0.0032437733422378528
    w[6] = 0.024810520887463626
    w[7] = 0.10901720602002152
    w[8] = 0.28667550536283404
    w[9] = 0.46224366960061009
    w[10] = 0.46224366960061009
    w[11] = 0.28667550536283404
    w[12] = 0.10901720602002152
    w[13] = 0.024810520887463626
    w[14] = 0.0032437733422378528
    w[15] = 0.00022833863601635264
    w[16] = 7.8025564785320666e-06
    w[17] = 1.0860693707692815e-07
    w[18] = 4.3993409922731799e-10
    w[19] = 2.2293936455341523e-13
    return (x * np.sqrt(2)) * sigma + mu, (w / np.sqrt(np.pi))

def SpreadCallOption(F1, F2, K, vol1, vol2, tau, rho, DF, mu1 = 0, mu2 = 0, kirk = True, LogNormal = False) : 
    if LogNormal == True : 
        if kirk == False : 
            v, w = Gauss_Hermite_Normal(mu = 0, sigma = 1)
            h = np.vectorize(lambda v : K + F2 * np.exp((mu2 - 0.5 * vol1 * vol1) * tau + vol2 * np.sqrt(tau) * v))
            X1 = np.vectorize(lambda v : np.log(F1/h(v)) + (mu1 + (0.5 - rho*rho)*vol1*vol1)*tau + rho * vol1 * np.sqrt(tau) * v)
            X2 = np.vectorize(lambda v : X1(v) - vol1 * np.sqrt(tau) * np.sqrt(1-rho*rho))
            C1 = np.vectorize(lambda v : -0.5 * rho*rho * vol1*vol1 * tau + rho * vol1 * np.sqrt(tau) * v)
            f = np.vectorize(lambda v : F1 * np.exp(C1(v)) * CDF_N(X1(v)) - h(v) * CDF_N(X2(v)))
            return (f(v) * w).sum() * DF
        else : 
            b = F2/(F2 + K)
            sigk = np.sqrt(vol1 * vol1 + b * b * vol2 * vol2 - 2 * b * rho * vol1 * vol2)
            d1 = (np.log(F1/(F2+K)) + 0.5 * sigk*sigk * tau)/(sigk * np.sqrt(tau))
            d2 = d1 - sigk * np.sqrt(tau)
            C = DF * (F1 * CDF_N(d1) - (F2 + K) * CDF_N(d2))
            return C
    else : 
        sig = np.sqrt(vol1 * vol1 + vol2 * vol2 - 2.0 * rho * vol1 * vol2)
        F = F1 - F2
        d = (F - K)/(sig * np.sqrt(tau))
        return DF * sig * np.sqrt(tau) * (d * CDF_N(d) + 1/np.sqrt(np.pi * 2) * np.exp(-d*d/2))

def DigitalSpreadCall(F1, F2, K, vol1, vol2, tau, rho, DF, mu1 = 0, mu2 = 0, kirk = True, LogNormal = False, dK = 0.0001, Cpn = 0.05) :
    tau = max(0.00001, tau)
    numberofoption = Cpn/dK
    K1 = K
    K2 = K + dK
    C1 = numberofoption * SpreadCallOption(F1, F2, K1, vol1, vol2, tau, rho, DF, mu1, mu2, kirk, LogNormal)
    C2 = -numberofoption * SpreadCallOption(F1, F2, K2, vol1, vol2, tau, rho, DF, mu1, mu2, kirk, LogNormal)
    return C1 + C2

def SpreadRangeAccrualAnalyticDigitalSpreadCall(F1, F2, K1, K2, vol1, vol2, tau, rho, DF, mu1 = 0, mu2 = 0, kirk = True, LogNormal = False, dK = 0.0001, Cpn = 0.05) :
    tau = max(0.00001, tau)
    if K2 <= K1 : 
        raise ValueError("K2 must bigger than K1")
    C1 = DigitalSpreadCall(F1, F2, K1, vol1, vol2, tau, rho, DF, mu1, mu2, kirk, LogNormal, dK, Cpn)
    C2 = -DigitalSpreadCall(F1, F2, K2, vol1, vol2, tau, rho, DF, mu1, mu2, kirk, LogNormal, dK, Cpn)
    return C1 + C2

def PricingRangeAccrualSinglePayoff(
    Notional,
    PriceDate,
    StartDate,
    EndDate,
    PayDate,
    RefZeroTerm,
    RefZeroRate,
    DiscZeroTerm,
    DiscZeroRate,
    K1,
    K2,
    RefSwapMaturity_T,
    RefSwapNCPNOneYear,
    voloptterm,
    volswapterm,
    vol2d,
    model = "black",
    DayCountFlag = 0,
    CpnRate = 0.01,
    PowerSpreadFlag = False,
    RefSwapMaturity_T_PowerSpread = 1.0,
    rho12 = 0.56,
    Cap = 100.0,
    Floor = -100.0
) : 
    Preprocessing_ZeroTermAndRate(RefZeroTerm, RefZeroRate,PriceDate)
    Preprocessing_ZeroTermAndRate(DiscZeroTerm, DiscZeroRate,PriceDate)
    topt = DayCountAtoB(PriceDate, StartDate)/365
    tswp = RefSwapMaturity_T
    vol = Linterp2D(voloptterm, volswapterm, vol2d, topt, tswp)
    if PowerSpreadFlag == 0 : 
        vol2 = vol
    else : 
        tswp2 = RefSwapMaturity_T_PowerSpread
        vol2 = Linterp2D(voloptterm, volswapterm, vol2d, topt, tswp2)
    NDates = DayCountAtoB(StartDate, EndDate)
    Dates = []
    for i in range(NDates) : 
        if i == 0 : 
            Today = StartDate
        else : 
            Today = DayPlus(Today, 1)
        Dates.append(Today)
    DayCountFrc = DayCountFractionAtoB(StartDate, EndDate, DayCountFlag)
    EachSwapMaturityInBDate = np.vectorize(EDate_YYYYMMDD)(Dates, int(RefSwapMaturity_T * 12 + 0.0001))
    CpnDateListInSimul = []
    for i in range(len(Dates)) : 
        CpnDateListInSimul.append(np.array(malloc_cpn_date_holiday(Dates[i], EachSwapMaturityInBDate[i], RefSwapNCPNOneYear)[0]).reshape(1,-1))
    CpnDateArrayForEachBDate = np.concatenate(CpnDateListInSimul, axis = 0)

    t1 = np.vectorize(DayCountAtoB)(PriceDate, Dates)/365
    t2 = np.vectorize(DayCountAtoB)(PriceDate, CpnDateArrayForEachBDate)/365
    r1 = np.interp(t1, RefZeroTerm, RefZeroRate)
    r2 = np.interp(t2, RefZeroTerm, RefZeroRate)
    df1 = np.exp(-r1 * t1)
    df2 = np.exp(-r2 * t2)
    df_t_T = df2/df1.reshape(-1,1)
    deltat = np.concatenate([(t2[:,0] - t1).reshape(-1,1), (t2[:,1:] - t2[:,:-1])], axis = 1)    
    SwapRateForwardMeasure = (1-df_t_T[:,-1])/(df_t_T * deltat).sum(1)
    t_to_PayDate = DayCountAtoB(PriceDate, PayDate)/365
    DF = Calc_Discount_Factor(DiscZeroTerm, DiscZeroRate, t_to_PayDate)
    if PowerSpreadFlag == 0 : 
        vect_rangeforward = np.vectorize(lambda Farray, tauarray : price_digital_rangeforward(Farray,K1,K2,vol,tauarray,1,1.0,1.0,model))
        Pct = vect_rangeforward(SwapRateForwardMeasure, t1).sum()/NDates
        Payoff = Notional *CpnRate *DayCountFrc
        EPayoff = Payoff *Pct
        Price = np.minimum(Cap,np.maximum(Floor,EPayoff)) * DF
        Result = {"Pct" : Pct, "DayCountFrc" : DayCountFrc, "Payoff" : Payoff, "EPayoff" : EPayoff, "DF" : DF, "Price" : Price}
        return Result, vol, vol2
    else : 
        EachSwapMaturityInBDate2 = np.vectorize(EDate_YYYYMMDD)(Dates, int(RefSwapMaturity_T_PowerSpread * 12 + 0.0001))
        CpnDateListInSimul2 = []
        for i in range(len(Dates)) : 
            CpnDateListInSimul2.append(np.array(malloc_cpn_date_holiday(Dates[i], EachSwapMaturityInBDate2[i], RefSwapNCPNOneYear)[0]).reshape(1,-1))
        CpnDateArrayForEachBDate2 = np.concatenate(CpnDateListInSimul2, axis = 0)
        t1_spread = np.vectorize(DayCountAtoB)(PriceDate, Dates)/365
        t2_spread = np.vectorize(DayCountAtoB)(PriceDate, CpnDateArrayForEachBDate2)/365
        r1_spread = np.interp(t1_spread, RefZeroTerm, RefZeroRate)
        r2_spread = np.interp(t2_spread, RefZeroTerm, RefZeroRate)
        df1_spread = np.exp(-r1_spread * t1_spread)
        df2_spread = np.exp(-r2_spread * t2_spread)
        df_t_T_spread = df2_spread/df1_spread.reshape(-1,1)
        deltat_spread = np.concatenate([(t2_spread[:,0] - t1_spread).reshape(-1,1), (t2_spread[:,1:] - t2_spread[:,:-1])], axis = 1)    
        SwapRateForwardMeasure_spread = (1-df_t_T_spread[:,-1])/(df_t_T_spread * deltat_spread).sum(1)
        vect_spreadrange = np.vectorize(lambda Farray1, Farray2, tauarray : SpreadRangeAccrualAnalyticDigitalSpreadCall(Farray1, Farray2, K1, K2, vol, vol2, tauarray, rho12, 1.0, mu1 = 0, mu2 = 0, kirk = True, LogNormal = (model.lower() == 'black'), dK = 0.0001, Cpn = CpnRate))
        resultcpnrate = vect_spreadrange(SwapRateForwardMeasure, SwapRateForwardMeasure_spread, t1).mean()
        EPayoff = Notional *resultcpnrate *DayCountFrc
        Price = np.minimum(Cap,np.maximum(Floor,EPayoff)) * DF
        Result = {"F1" : SwapRateForwardMeasure, "F2" : SwapRateForwardMeasure_spread, "MeanCpn" : resultcpnrate,"DayCountFrc" : DayCountFrc, "EPayoff" : EPayoff, "DF" : DF, "Price" : Price}

        return Result, vol, vol2

def Pricing_RangeAccrualBond(PriceDate, BondStartDate, BondMaturity, NCPN_Annual, Notional,
                             NotionalUseFlag, RefSwapMaturity_T, RefSwapNCPNOneYear, K1, K2,
                             CpnRate, DayCountFlag, VolatilityOptTerm, VolatilitySwpTerm, VolatilitySurf,
                             RefZeroTerm, RefZeroRate, DiscZeroTerm, DiscZeroRate, Holidays = [], 
                             RefRateHistoryDate = [], RefRateHistoryRate = [], model = "normal",PowerSpreadFlag = False, RefSwapMaturity_T_PowerSpread = 1.0, 
                             rho12= 0.76, Cap = 100, Floor = -100) : 
    '''
    Desc : Pricing Range Accrual(or Spread Range Accrual) Note
    
        PriceDate -> Pricing Date YYYYMMDD Format
        BondStartDate -> BondStartDate YYYYMMDD Format
        BondMaturity -> BondMaturityDate YYYYMMDD Format
        NCPN_Annual -> Number of Cpn in Annual (1, 2, 4, 6, ...)
        Notional -> Notional Amount
        NotionalUseFlag -> Notional Payment Use Flag
        RefSwapMaturity_T -> Reference Rate Maturity converted T (1.0, 3.0, ...)
        RefSwapNCPNOneYear -> Number of Reference Rate Annual Payment (1, 2, 4, 6, ...)
        K1 -> Range Lower
        K2 -> Range Upper
        CpnRate -> Range Coupon Rate
        DayCountFlag -> 0: Act365 1: Act360 2: ActAct 3: 30/360
        VolatilityOptTerm -> VolSurf Option Maturity Tenor Converted T List [1.0, 2.0, ...]
        VolatilitySwpTerm -> VolSurf Swap Maturity Tenor Converted T List [1.0, 2.0, ...]
        VolatilitySurf -> VolSurf Matrix Array
        RefZeroTerm -> Reference Rate Term Array
        RefZeroRate -> Reference Rate Array
        DiscZeroTerm -> Discount Rate Term Array
        DiscZeroRate -> Discount Rate Array
        Holidays -> Holidays to Generate Cpn
        RefRateHistoryDate -> Historical Reference Rate Date YYYYMMDD Array
        RefRateHistoryRate -> Historical Reference Rate
        model -> "normal or black" String
        PowerSpreadFlag -> PowerSpread Range Accrual Flag (True or False)
        RefSwapMaturity_T_PowerSpread -> PowerSpread Range Accrual Rate2 Maturity T
        rho12 -> Rate1 Rate2 Correlation

    Variables Example : 
    
    PriceDate = 20240627
    BondStartDate = 20220906
    BondMaturity = 20320906
    NCPN_Annual = 4
    Notional = 100
    NotionalUseFlag = 1
    K1 = -0.10
    K2 = 0.1
    CpnRate = 0.04
    RefSwapMaturity_T = 5
    RefSwapNCPNOneYear = 4
    DayCountFlag = 0
    VolatilityOptTerm = [1, 2]
    VolatilitySwpTerm = [1, 2]
    VolatilitySurf = [[0.02,0.022],[0.021,0.019]]
    RefZeroTerm = [1,10,15, 20]
    RefZeroRate = [3.0,3.4,3.5, 3.55]
    DiscZeroTerm = [1,10,15, 20]
    DiscZeroRate = [3.0,3.4,3.5, 3.55]
    Holidays = KoreaHolidaysFromStartToEnd(2020,2060)
    RefRateHistoryDate = [20240607, 20240608, 20240609, 20240610, 20240611, 20240612]
    RefRateHistoryRate = [0.04, 0.039, 0.0394, 0.0391, 0.0390, 0.0390]
    model = "normal"
    PowerSpreadFlag = True
    RefSwapMaturity_T_PowerSpread = 1.0
    Cap = 100.0
    Floor = -100.0
    rho12 = 0.76
    
    Result = Pricing_RangeAccrualBond(PriceDate, BondStartDate, BondMaturity, NCPN_Annual, Notional,
                                    NotionalUseFlag, RefSwapMaturity_T, RefSwapNCPNOneYear, K1, K2,
                                    CpnRate, DayCountFlag, VolatilityOptTerm, VolatilitySwpTerm, VolatilitySurf,
                                    RefZeroTerm, RefZeroRate, DiscZeroTerm, DiscZeroRate, Holidays, 
                                    RefRateHistoryDate, RefRateHistoryRate, model, PowerSpreadFlag, RefSwapMaturity_T_PowerSpread, 
                                    rho12, Cap, Floor) 
    '''
    v1, v2 = 0, 0
    NCPN_Ann = NCPN_Annual
    Preprocessing_ZeroTermAndRate(RefZeroTerm, RefZeroRate,PriceDate)
    Preprocessing_ZeroTermAndRate(DiscZeroTerm, DiscZeroRate,PriceDate)
    VolatilitySurf = np.array(VolatilitySurf)
    ResultForwardStart, ResultForwardEnd, ResultPayDate, ResultNBD  = MappingCouponDates(1, BondStartDate, BondMaturity, -1, NCPN_Ann, 1, Holidays,Holidays,1)
    EPayoffList, DFList, DCFList, v1list, v2list = [], [], [], [], []
    for i in range(len(ResultForwardEnd)) : 
        EPayoff = 0
        DF = 1.0
        RAPrice = 0
        if PriceDate > ResultForwardStart[i] and PriceDate < ResultForwardEnd[i] : 
            Frac = DayCountFractionAtoB(ResultForwardStart[i], PriceDate, DayCountFlag)
            NTotalDate = DayCountAtoB(ResultForwardStart[i], ResultForwardEnd[i])
            NDate = DayCountAtoB(ResultForwardStart[i], PriceDate) 
            NumberofDate = 0
            NumberofInDate = 0
            for j in range(NDate) : 
                if j == 0 : 
                    Today = ResultForwardStart[i]
                else : 
                    Today = DayPlus(Today, 1)
                if Today in RefRateHistoryDate : 
                    ind = list(RefRateHistoryDate).index(Today)
                    if K1 <= RefRateHistoryRate[ind] and RefRateHistoryRate[ind] <= K2 : 
                        NumberofInDate += 1
                    NumberofDate += 1
            if NumberofDate > 0 : 
                AccruedCpn = Frac * NumberofInDate/NumberofDate * CpnRate * Notional
            else : 
                AccruedCpn = 0
            t = DayCountAtoB(PriceDate, ResultPayDate[i])/365
            DF = Calc_Discount_Factor(DiscZeroTerm, DiscZeroRate, t)
            OptionPrice, v1, v2 = PricingRangeAccrualSinglePayoff(Notional,PriceDate,PriceDate,ResultForwardEnd[i],ResultPayDate[i],
                                            RefZeroTerm, RefZeroRate, DiscZeroTerm,DiscZeroRate,K1,
                                            K2,RefSwapMaturity_T,RefSwapNCPNOneYear,VolatilityOptTerm, VolatilitySwpTerm, VolatilitySurf,model,
                                            DayCountFlag,CpnRate,PowerSpreadFlag,RefSwapMaturity_T_PowerSpread,
                                            rho12)
            EPayoff = np.minimum(np.maximum(Floor * Notional,OptionPrice["EPayoff"] + AccruedCpn), Cap * Notional)
            RAPrice = EPayoff * DF
        elif PriceDate > ResultForwardEnd[i] and PriceDate < ResultPayDate[i] : 
            Frac = DayCountFractionAtoB(ResultForwardStart[i], ResultForwardEnd[i], DayCountFlag)
            NumberofDate = 0
            NumberofInDate = 0
            NDate = DayCountAtoB(ResultForwardStart[i], ResultForwardEnd[i]) 
            for j in range(NDate) : 
                if j == 0 : 
                    Today = ResultForwardStart[i]
                else : 
                    Today = DayPlus(Today, 1)
                if Today in RefRateHistoryDate : 
                    ind = list(RefRateHistoryDate).index(Today)
                    if K1 <= RefRateHistoryRate[ind] and RefRateHistoryRate[ind] <= K2 : 
                        NumberofInDate += 1
                    NumberofDate += 1
            t = DayCountAtoB(PriceDate, ResultPayDate[i])/365
            DF = Calc_Discount_Factor(DiscZeroTerm, DiscZeroRate, t)
            if NumberofDate > 0 : 
                EPayoff = np.minimum(np.maximum(Floor, Frac * NumberofInDate/NumberofDate * CpnRate),Cap) * Notional
            else : 
                EPayoff = 0
            RAPrice = EPayoff * DF
        elif PriceDate <= ResultForwardStart[i] and PriceDate < ResultPayDate[i] : 
            OptionPrice, v1, v2 = PricingRangeAccrualSinglePayoff(Notional,PriceDate,ResultForwardStart[i],ResultForwardEnd[i],ResultPayDate[i],
                                            RefZeroTerm, RefZeroRate, DiscZeroTerm,DiscZeroRate,K1,
                                            K2,RefSwapMaturity_T,RefSwapNCPNOneYear,VolatilityOptTerm, VolatilitySwpTerm, VolatilitySurf,model,
                                            DayCountFlag,CpnRate,PowerSpreadFlag,RefSwapMaturity_T_PowerSpread,
                                            rho12)
            EPayoff = OptionPrice["EPayoff"]
            RAPrice = OptionPrice["Price"]
            DF = OptionPrice["DF"]
        EPayoffList.append(EPayoff)
        DFList.append(DF)
        DCFList.append(RAPrice)
        v1list.append(v1)
        v2list.append(v2)

    if NotionalUseFlag == True : 
        EPayoffList.append(Notional)
        DFList.append(DF)
        DCFList.append(Notional * DF)
        v1list.append(v1)
        v2list.append(v2)

    Data = pd.DataFrame([ResultForwardStart + [ResultForwardStart[-1]], ResultForwardEnd + [ResultForwardEnd[-1]], ResultPayDate + [ResultPayDate[-1]], ResultNBD + [ResultNBD[-1]],EPayoffList, DFList,DCFList, v1list, v2list], index = ["ResultForwardStart", "ResultForwardEnd", "ResultPayDate", "ResultNBD","EPayoffList","DF","DiscCF","Vol1","Vol2"]).T
    ResultPrice = Data["DiscCF"].sum()
    Data["Price"] = ResultPrice
    return Data

def Pricing_IRCallableSwap_HWFDM(
    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
    Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
    NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
    Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
    ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
    kappa = 0.01, kappa2 = 0.01, HWVolTerm = [0.0001], HWVol = [0.006323], HWVolTerm2 = [0.0001], 
    HWVol2 = [0.003323], HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = 0, 
    LoggingDir = os.getcwd(), Leg1_DiscCurveName = "TempCurve", Leg1_EstCurveName = "TempCurve", Leg2_DiscCurveName = "TempCurve",
    Leg2_EstCurveName = "TempCurve", KoreanAutoHolidayFlag = True, FixHolidays = [], PayHolidays = [],
    Leg1_Phase2UseFlag = 0, NumCpnOneYear_Leg1_Phase2 = 0, Leg1_Phase2StartDate = 20280929, Leg1_RefSwapRate_Multiple_Phase2 = 0.0, Leg1_FixedCpnRate_Phase2 = 0.0237,   
    Leg2_Phase2UseFlag = 0, NumCpnOneYear_Leg2_Phase2 = 4, Leg2_Phase2StartDate = 20280929, Leg2_RefSwapRate_Multiple_Phase2 = 1.0, Leg2_FixedCpnRate_Phase2 = -0.0012,
    Leg1_PowerSpreadFlag = 0, Leg1_RefSwapMaturity_T_PowerSpread = 0.25, Leg2_PowerSpreadFlag = 0, Leg2_RefSwapMaturity_T_PowerSpread = 0.25,
    MaxReturn = 1000, MaxLoss = -1000
    ) : 
        
    '''
    Description : Pricing IRCallable Swap Using Hull White 1, 2Factor Model
    
    Variables : 
        Nominal -> Nominal Amount | <float or int>
        SwapEffectiveDate -> Swap Effective Date (YYYYMMDD) | <int>
        PriceDate -> Pricing Date (YYYYMMDD) | <int>
        SwapMaturity -> Swap Maturity (YYYYMMDD) | <int>
        NumCpnOneYear_Leg1_Phase1 -> Leg1) Number of Cpn for One Year(if ZeroCouponCallable Then input 0) | <int>
        Leg1_RefSwapMaturity_T -> Leg1) Reference Rate Maturity to Convert T (ex 0.25, 0.5, 1, ...) | <float>
        Leg1_RefSwapNCPNOneYear -> Leg1) Reference Rate Number of Swap Cpn for One Year | <int>
        Leg1_FixedCpnRate_Phase1 -> Leg1) Fixed Cpn Rate Phase1 | <float>
        Leg1_DayCount -> Leg1) DayCountFlag <int> [0: Act365 1: Act360 2: ActAct 3:30/360, ZeroCompoundCoupon = {5: Act365, 6:Act360, 7: ActAct, 8:30/360}]
        NumCpnOneYear_Leg2_Phase1 -> Leg2) Number of Cpn for One Year <int> (if ZeroCouponCallable Then input 0)
        Leg2_RefSwapMaturity_T -> Leg2) Reference Rate Maturity to Convert T (ex 0.25, 0.5, 1, ...) <float>
        Leg2_RefSwapNCPNOneYear -> Leg2) Reference Rate Number of Swap Cpn for One Year <int>
        Leg2_FixedCpnRate_Phase1 -> Leg2) Fixed Cpn Rate Phase1 <float>
        Leg2_DayCount -> Leg2) DayCountFlag <int> [0: Act365 1: Act360 2: ActAct 3:30/360, ZeroCompoundCoupon = {5: Act365, 6:Act360, 7: ActAct, 8:30/360}]
        OptionFixDate -> Option Fix Date (YYYYMMDD <int Array>)
        OptionPayDate -> Option Pay Date (YYYYMMDD <int Array>)
        OptionHolder_0Recever1Payer -> 0 if Receiver have option else 1(Payer have)
        ZeroTerm -> Zero Discount Term Array <float Array>
        ZeroRate -> Zero Discount Rate Array <float Array>
        Leg1_FixingHistoryDate -> Leg1) Fixing Rate Date History Array <int Array>
        Leg1_FixingHistoryRate -> Leg1) Fixing Rate History Array <float Array>
        Leg2_FixingHistoryDate -> Leg2) Fixing Rate Date History Array <int Array>
        Leg2_FixingHistoryRate -> Leg2) Fixing Rate History Array <float Array>
        kappa -> Mean Revert Param <float>
        kappa2 -> Mean Revert Param2 <float>
        HWVolTerm -> Hull White 1F Vol Term <float Array>
        HWVol -> Hull White 1F Vol Term <float Array> 
        HWVolTerm2 -> Hull White 2F Vol Term <float Array>
        HWVol2 -> Hull White 2F Vol Term <float Array> 
        HWRho12Factor -> Corr between 1, 2 OS Process Randomness <float>
        CpnRounding -> Coupon Rounding <int>
        HW2FFlag -> 0 if HW1F else 1
        LoggingDir -> Logging Directory <String>
        KoreanAutoHolidayFlag -> True if Korean Schedule else False
        FixHolidays -> Fixing Holiday Using Calculating Fixing Rate <int Array>
        PayHolidays -> Holiday Using FixingEndDate to Payment <int Array>
        
    SampleVariable : 
    
        Nominal = 20000
        SwapEffectiveDate, PriceDate, SwapMaturity = 20160929, 20250304, 20460929
        NumCpnOneYear_Leg1_Phase1, Leg1_RefSwapRate_Multiple_Phase1, Leg1_FixedCpnRate_Phase1, Leg1_DayCount = 0, 0.0, 0.0237,  3
        NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_FixedCpnRate_Phase1, Leg2_DayCount = 4, 1.0, -0.0012, 0
        OptionFixDate = [20190902,20200903,20210831,20220901,20230904,20240830,20250903,20260901,20270831,20280905,20290903,20300830,20310903,20320901,20330831,20340831,20350903,20360903,20370903,20380903,20390905,20400905,20410904,20420903,20430904,20440905,20450905]
        OptionPayDate = [20190930,20200929,20210929,20220929,20231004,20240930,20250929,20260929,20270929,20280929,20291001,20300930,20310929,20320929,20330929,20340929,20351001,20360929,20370929,20380929,20390929,20401001,20410930,20421001,20430929,20440929,20450929]
        OptionHolder = 1
        Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear = 0.25, 4
        Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear = 0.25, 4

        ZeroTerm = [0.00274, 0.00548, 0.25479, 0.506849, 0.756164, 1.00274, 1.512329, 2.00274, 3.00822, 4.00548, 5.00548, 6.00548, 7.008219, 8.013699, 9.010959, 10.00822, 12.01096, 15.0137, 20.01918, 25.02466, 30.02192]
        ZeroRate = [0.027989, 0.027992, 0.028394, 0.027554, 0.026807, 0.02633, 0.025806, 0.025455, 0.025154, 0.025235, 0.025264, 0.025397, 0.025531, 0.025638, 0.025719, 0.025856, 0.026049, 0.025598, 0.024243, 0.022474, 0.021085]
        kappa = -0.0133
        kappa2 = 0.01
        HWVolTerm = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52]
        HWVol = [0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368]
        HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52]
        HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2
        HWRho12Factor = -0.3
        CpnRounding = 15
        HW2FFlag = 0

        Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2 = 0, 0
        Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2= 20280929, 0.0, 0.0237
        Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2 = 0, 4
        Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2 = 20280929, 1.0, -0.0012
        Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread = 0, 0.25
        Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread = 0, 0.25

        LoggingFlag = 1
        LoggingDir = currdir
        Leg1_DiscCurveName = "TempCurve"
        Leg1_EstCurveName = "TempCurve"
        Leg2_DiscCurveName = "TempCurve"
        Leg2_EstCurveName = "TempCurve"

        Leg1_FixingHistoryDate = [DayPlus(20240102, i) for i in range(365)]
        Leg1_FixingHistoryRate = [0.0344]*len(Leg1_FixingHistoryDate)
        Leg2_FixingHistoryDate = [DayPlus(20240102, i) for i in range(365)]
        Leg2_FixingHistoryRate = [0.0344]*len(Leg2_FixingHistoryDate)
        KoreanAutoHolidayFlag = True
        
        Pricing_IRCallableSwap_HWFDM(
            20000, 20160929, 20250304, 20460929, 0,         
            0.0, 0.25, 4, 0.0237, 3, 
            4, 1.0, 0.25, 4, -0.0012, 
            0, 
            [20190902,20200903,20210831,20220901,20230904,20240830,20250903,20260901,20270831,20280905,20290903,20300830,20310903,20320901,20330831,20340831,20350903,20360903,20370903,20380903,20390905,20400905,20410904,20420903,20430904,20440905,20450905], 
            [20190930,20200929,20210929,20220929,20231004,20240930,20250929,20260929,20270929,20280929,20291001,20300930,20310929,20320929,20330929,20340929,20351001,20360929,20370929,20380929,20390929,20401001,20410930,20421001,20430929,20440929,20450929], 
            1,
            [0.00274, 0.00548, 0.25479, 0.506849, 0.756164, 1.00274, 1.512329, 2.00274, 3.00822, 4.00548, 5.00548, 6.00548, 7.008219, 8.013699, 9.010959, 10.00822, 12.01096, 15.0137, 20.01918, 25.02466, 30.02192],
            [0.027989, 0.027992, 0.028394, 0.027554, 0.026807, 0.02633, 0.025806, 0.025455, 0.025154, 0.025235, 0.025264, 0.025397, 0.025531, 0.025638, 0.025719, 0.025856, 0.026049, 0.025598, 0.024243, 0.022474, 0.021085],
            [DayPlus(20240102, i) for i in range(365)], 
            [0.0344]*365, 
            [DayPlus(20240102, i) for i in range(365)], 
            [0.0344]*365, 
            kappa = -0.0133,
            kappa2 = 0.01,
            HWVolTerm = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
            HWVol = [0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368],
            HWVolTerm2 = [0.0001, 0.0849315, 0.2520548, 0.504109, 1, 2, 3.008219, 4.005479, 5.0027, 7.0055, 10.0082, 20.5205, 50.52],
            HWVol2 = np.array([0.006323, 0.006323, 0.0059312, 0.005610373, 0.00526, 0.00516138, 0.004497, 0.0045619, 0.00432513, 0.004089, 0.003757, 0.003680, 0.00368])/2)
                
    '''
    OptionHolder = OptionHolder_0Recever1Payer

    # Error Processing
    if SwapMaturity < PriceDate : 
        raise ValueError("PriceDate > SwapMaturity")
    if SwapMaturity < SwapEffectiveDate : 
        raise ValueError("SwapMaturity < SwapEffectiveDate")        

    # Preprocessing
    if PriceDate < 19000101 : 
        PriceDate = ExcelDateToYYYYMMDD(PriceDate)
    
    if SwapEffectiveDate < 19000101 : 
        SwapEffectiveDate = ExcelDateToYYYYMMDD(SwapEffectiveDate)
        
    if SwapMaturity < 19000101 : 
        SwapMaturity = ExcelDateToYYYYMMDD(SwapMaturity)
    
    if NumCpnOneYear_Leg1_Phase2 < 0 : 
        NumCpnOneYear_Leg1_Phase2 = NumCpnOneYear_Leg1_Phase1

    if NumCpnOneYear_Leg2_Phase2 < 0 : 
        NumCpnOneYear_Leg2_Phase2 = NumCpnOneYear_Leg2_Phase1

    if KoreanAutoHolidayFlag == True : 
        FixHolidays = KoreaHolidaysFromStartToEnd(PriceDate//10000-1,SwapMaturity//10000 + 1)
        PayHolidays = FixHolidays
        
    for i in range(len(FixHolidays)) : 
        if FixHolidays[i] < 19000101 : 
            FixHolidays[i] = ExcelDateToYYYYMMDD(FixHolidays[i])
    
    for i in range(len(PayHolidays)) : 
        if PayHolidays[i] < 19000101 : 
            PayHolidays[i] = ExcelDateToYYYYMMDD(PayHolidays[i])
    
    for i in range(len(Leg1_FixingHistoryDate)) :
        if Leg1_FixingHistoryDate[i] < 19000101 : 
            Leg1_FixingHistoryDate[i] = ExcelDateToYYYYMMDD(Leg1_FixingHistoryDate[i])

    for i in range(len(Leg2_FixingHistoryDate)) :
        if Leg2_FixingHistoryDate[i] < 19000101 : 
            Leg2_FixingHistoryDate[i] = ExcelDateToYYYYMMDD(Leg2_FixingHistoryDate[i])
        
    if abs(kappa) > 1.5 : 
        kappa = kappa / 100
    if abs(kappa2) > 1.5 : 
        kappa2 = kappa2 / 100

    if (Leg1_Phase2UseFlag == 0) : 
        NumCpnOneYear_Leg1_Phase2 = NumCpnOneYear_Leg1_Phase1
        Leg1_RefSwapRate_Multiple_Phase2 = Leg1_RefSwapRate_Multiple_Phase1
        Leg1_FixedCpnRate_Phase2 = Leg1_FixedCpnRate_Phase1

    if (Leg2_Phase2UseFlag == 0) : 
        NumCpnOneYear_Leg2_Phase2 = NumCpnOneYear_Leg2_Phase1
        Leg2_RefSwapRate_Multiple_Phase2 = Leg2_RefSwapRate_Multiple_Phase1
        Leg2_FixedCpnRate_Phase2 = Leg2_FixedCpnRate_Phase1

    # Function Start
    NGreed = 100
    Preprocessing_ZeroTermAndRate(ZeroTerm, ZeroRate, PriceDate)
    Preprocessing_ZeroTermAndRate(HWVolTerm, HWVol, PriceDate, CompareNumber = 0.3)
    Preprocessing_ZeroTermAndRate(HWVolTerm2, HWVol2, PriceDate, CompareNumber = 0.3)

    IdxOpt = np.array(OptionFixDate) > PriceDate
    OptionFixDate = list(np.array(OptionFixDate)[IdxOpt])
    OptionPayDate = list(np.array(OptionPayDate)[IdxOpt])
    Leg1CompoundCouponFlag = False
    Leg2CompoundCouponFlag = False
    if Leg1_DayCount >= 5 : 
        # 복리 제로쿠폰의 경우 5번 넘는 Flag를 넣으면 됨
        Leg1_DayCount = Leg1_DayCount % 5
        Leg1CompoundCouponFlag = True

    if Leg2_DayCount >= 5 : 
        # 복리 제로쿠폰의 경우 5번 넘는 Flag를 넣으면 됨
        Leg2_DayCount = Leg2_DayCount % 5
        Leg2CompoundCouponFlag = True

    Leg1ZeroCouponFlag = (NumCpnOneYear_Leg1_Phase1 == 0) or (NumCpnOneYear_Leg1_Phase2 == 0) if Leg1_Phase2UseFlag == True else (NumCpnOneYear_Leg1_Phase1 == 0)
    Leg2ZeroCouponFlag = (NumCpnOneYear_Leg2_Phase1 == 0) or (NumCpnOneYear_Leg2_Phase2 == 0) if Leg2_Phase2UseFlag == True else (NumCpnOneYear_Leg2_Phase1 == 0)
    if Leg1ZeroCouponFlag == True : 
        NumCpnOneYear_Leg1_Phase1 = max(1, NumCpnOneYear_Leg1_Phase2)    
        NumCpnOneYear_Leg1_Phase2 = max(1, NumCpnOneYear_Leg1_Phase2)    

    if Leg2ZeroCouponFlag == True : 
        NumCpnOneYear_Leg2_Phase1 = max(1, NumCpnOneYear_Leg2_Phase2)    
        NumCpnOneYear_Leg2_Phase2 = max(1, NumCpnOneYear_Leg2_Phase2)    

    if Leg1_Phase2UseFlag > 0 : 
        #print("L1PhaseMulti",NumCpnOneYear_Leg1_Phase1,NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate)
        Leg1ForwardStart1,Leg1ForwardEnd1, Leg1PayDate1, Leg1ResultNBD1 = MappingCouponDates(1, SwapEffectiveDate, Leg1_Phase2StartDate, 0 if SwapEffectiveDate % 100 == Leg1_Phase2StartDate % 100 else -1, NumCpnOneYear_Leg1_Phase1, True, FixHolidays, PayHolidays, 1) 
        Leg1ForwardStart2,Leg1ForwardEnd2, Leg1PayDate2, Leg1ResultNBD2 = MappingCouponDates(1, Leg1ForwardEnd1[-1] if Leg1ForwardEnd1[-1] % 100 == SwapMaturity % 100 else ((Leg1ForwardEnd1[-1] // 100)*100 + SwapEffectiveDate % 100), SwapMaturity, 0 if Leg1ForwardEnd1[-1] % 100 == SwapMaturity % 100 else -1, NumCpnOneYear_Leg1_Phase2, True, FixHolidays, PayHolidays, 1) 
        Leg1ForwardStart = list(Leg1ForwardStart1) + list(Leg1ForwardStart2)
        Leg1ForwardEnd = list(Leg1ForwardEnd1) + list(Leg1ForwardEnd2)
        Leg1PayDate = list(Leg1PayDate1) + list(Leg1PayDate2)
        Leg1ResultNBD = Leg1ResultNBD1
    else : 
        Leg1ForwardStart,Leg1ForwardEnd, Leg1PayDate, Leg1ResultNBD = MappingCouponDates(1, SwapEffectiveDate, SwapMaturity, 0 if SwapEffectiveDate % 100 == SwapMaturity % 100 else -1, NumCpnOneYear_Leg1_Phase1, True, FixHolidays, PayHolidays, 1) 
    #print(Leg1ForwardEnd)

    if Leg2_Phase2UseFlag > 0 : 
        #print("L2PhaseMulti",NumCpnOneYear_Leg2_Phase1,NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate)
        Leg2ForwardStart1,Leg2ForwardEnd1, Leg2PayDate1, Leg2ResultNBD1 = MappingCouponDates(1, SwapEffectiveDate, Leg2_Phase2StartDate, 0 if SwapEffectiveDate % 100 == Leg2_Phase2StartDate % 100 else -1, NumCpnOneYear_Leg2_Phase1, True, FixHolidays, PayHolidays, 1) 
        Leg2ForwardStart2,Leg2ForwardEnd2, Leg2PayDate2, Leg2ResultNBD2 = MappingCouponDates(1, Leg2ForwardEnd1[-1] if Leg2ForwardEnd1[-1] % 100 == SwapMaturity % 100 else ((Leg2ForwardEnd1[-1] // 100)*100 + SwapEffectiveDate % 100) , SwapMaturity, 0 if Leg2ForwardEnd1[-1] % 100 == SwapMaturity % 100 else -1, NumCpnOneYear_Leg2_Phase2, True, FixHolidays, PayHolidays, 1) 
        Leg2ForwardStart = list(Leg2ForwardStart1) + list(Leg2ForwardStart2)
        Leg2ForwardEnd = list(Leg2ForwardEnd1) + list(Leg2ForwardEnd2)
        Leg2PayDate = list(Leg2PayDate1) + list(Leg2PayDate2)
        Leg2ResultNBD = Leg2ResultNBD1
    else : 
        Leg2ForwardStart,Leg2ForwardEnd, Leg2PayDate, Leg2ResultNBD = MappingCouponDates(1, SwapEffectiveDate, SwapMaturity, 0 if SwapEffectiveDate % 100 == SwapMaturity % 100 else -1, NumCpnOneYear_Leg2_Phase1, True, FixHolidays, PayHolidays, 1) 
    
    #print(Leg2ForwardEnd)
    if (PriceDate in Leg1ForwardStart) and (PriceDate not in Leg1_FixingHistoryDate):             
        Sm_Add = EDate_YYYYMMDD(PriceDate, int(Leg1_RefSwapMaturity_T * 12 + 0.000001))
        if Leg1_PowerSpreadFlag == 0 : 
            Leg1_RHistAdd = FSR(PriceDate, PriceDate, Sm_Add, Leg1_RefSwapNCPNOneYear, Leg1_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Leg1_FixingHistoryDate.append(PriceDate)
            Leg1_FixingHistoryRate.append(Leg1_RHistAdd)            
        else : 
            Leg1_RHistAdd = FSR(PriceDate, PriceDate, Sm_Add, Leg1_RefSwapNCPNOneYear, Leg1_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Sm_Add_PowerSpread = EDate_YYYYMMDD(PriceDate, int(Leg1_RefSwapMaturity_T_PowerSpread * 12 + 0.000001))
            Leg1_RHistAdd_PowerSpread = FSR(PriceDate, PriceDate, Sm_Add_PowerSpread, Leg1_RefSwapNCPNOneYear, Leg1_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Leg1_FixingHistoryDate.append(PriceDate)
            Leg1_FixingHistoryRate.append(Leg1_RHistAdd - Leg1_RHistAdd_PowerSpread)            

    if (PriceDate in Leg2ForwardStart) and (PriceDate not in Leg2_FixingHistoryDate):             
        Sm_Add = EDate_YYYYMMDD(PriceDate, int(Leg2_RefSwapMaturity_T * 12 + 0.000001))
        if Leg2_PowerSpreadFlag == 0 : 
            Leg2_RHistAdd = FSR(PriceDate, PriceDate, Sm_Add, Leg2_RefSwapNCPNOneYear, Leg2_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Leg2_FixingHistoryDate.append(PriceDate)
            Leg2_FixingHistoryRate.append(Leg2_RHistAdd)            
        else : 
            Leg2_RHistAdd = FSR(PriceDate, PriceDate, Sm_Add, Leg2_RefSwapNCPNOneYear, Leg2_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Sm_Add_PowerSpread = EDate_YYYYMMDD(PriceDate, int(Leg2_RefSwapMaturity_T_PowerSpread * 12 + 0.000001))
            Leg2_RHistAdd_PowerSpread = FSR(PriceDate, PriceDate, Sm_Add_PowerSpread, Leg2_RefSwapNCPNOneYear, Leg2_DayCount, FixHolidays, ZeroTerm, ZeroRate, ZeroTerm, ZeroRate)
            Leg2_FixingHistoryDate.append(PriceDate)
            Leg2_FixingHistoryRate.append(Leg2_RHistAdd - Leg2_RHistAdd_PowerSpread)            
            
    TotalDateList = np.sort(np.array(pd.Series([PriceDate] + Leg1ForwardStart + Leg1ForwardEnd + Leg1PayDate + Leg2ForwardStart + Leg2ForwardEnd + Leg2PayDate + OptionFixDate + OptionPayDate).unique()))    
    SimulationDateList = TotalDateList[TotalDateList > PriceDate]

    xt_min, xt_max = -0.1, 0.4
    yt_min, yt_max = -0.1, 0.4
    dxt = (xt_max - xt_min) / float(NGreed)
    dyt = (yt_max - yt_min) / float(NGreed)
    xt = np.linspace(xt_min, xt_max, NGreed+1)[:-1]
    yt = np.linspace(yt_min, yt_max, NGreed+1)[:-1]
    xt_greed = xt.reshape(1,-1) * np.ones(len(SimulationDateList)).reshape(-1,1)
    yt_greed = yt.reshape(1,-1) * np.ones(len(SimulationDateList)).reshape(-1,1)

    Leg1SwapRate, Leg1SwapRateForwardMeasure, Leg1ConvAdj = ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag, HWRho12Factor = HWRho12Factor)
    if Leg1_PowerSpreadFlag == 0 : 
        Leg1SwapRate_PowerSpread, Leg1SwapRateForwardMeasure_PowerSpread, Leg1ConvAdj_PowerSpread = Leg1SwapRate, Leg1SwapRateForwardMeasure, Leg1ConvAdj
    else : 
        Leg1SwapRate_PowerSpread, Leg1SwapRateForwardMeasure_PowerSpread, Leg1ConvAdj_PowerSpread = ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, Leg1_RefSwapMaturity_T_PowerSpread, Leg1_RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag, HWRho12Factor = HWRho12Factor)
        
    Leg2SwapRate, Leg2SwapRateForwardMeasure, Leg2ConvAdj = ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag, HWRho12Factor = HWRho12Factor)
    if Leg2_PowerSpreadFlag == 0 : 
        Leg2SwapRate_PowerSpread, Leg2SwapRateForwardMeasure_PowerSpread, Leg2ConvAdj_PowerSpread = Leg2SwapRate, Leg2SwapRateForwardMeasure, Leg2ConvAdj
    else : 
        Leg2SwapRate_PowerSpread, Leg2SwapRateForwardMeasure_PowerSpread, Leg2ConvAdj_PowerSpread = ParRateForFDMGreed(PriceDate, xt_greed, yt_greed, SimulationDateList, Leg2_RefSwapMaturity_T_PowerSpread, Leg2_RefSwapNCPNOneYear, kappa, HWVolTerm, HWVol, kappa2, HWVolTerm2, HWVol2, ZeroTerm, ZeroRate, HW2FFlag, HWRho12Factor = HWRho12Factor)

    IdxSimul = np.array([i for i in range(len(SimulationDateList)) if SimulationDateList[i] in Leg1ForwardStart])
    Leg1RefRateOnFixingDate = Leg1SwapRate[IdxSimul]
    Leg1RefRateOnFixingDate_PowerSpread = Leg1SwapRate_PowerSpread[IdxSimul]
    Leg1RefRateOnFixingDateForwardMeasure = Leg1SwapRateForwardMeasure[IdxSimul] - Leg1ConvAdj[IdxSimul]
    Leg1RefRateOnFixingDateForwardMeasure_PowerSpread = Leg1SwapRateForwardMeasure_PowerSpread[IdxSimul] - Leg1ConvAdj_PowerSpread[IdxSimul]
    IdxSimul = np.array([i for i in range(len(SimulationDateList)) if SimulationDateList[i] in Leg2ForwardStart])
    Leg2RefRateOnFixingDate = Leg2SwapRate[IdxSimul]
    Leg2RefRateOnFixingDate_PowerSpread = Leg2SwapRate_PowerSpread[IdxSimul]
    Leg2RefRateOnFixingDateForwardMeasure = Leg2SwapRateForwardMeasure[IdxSimul] - Leg2ConvAdj[IdxSimul]
    Leg2RefRateOnFixingDateForwardMeasure_PowerSpread = Leg2SwapRateForwardMeasure_PowerSpread[IdxSimul] - Leg2ConvAdj_PowerSpread[IdxSimul]

    Leg1_ResultData = Calc_Payoff_FDM_ForTimeGreed(ZeroTerm, ZeroRate, PriceDate, SwapEffectiveDate, Leg1RefRateOnFixingDate, Leg1RefRateOnFixingDate_PowerSpread, Nominal, 
                                    Leg1_Phase2StartDate, Leg1ForwardStart, Leg1ForwardEnd, Leg1PayDate, Leg1_DayCount,
                                    Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase1, Leg1_FixedCpnRate_Phase2, Leg1_FixingHistoryDate, 
                                    Leg1_FixingHistoryRate, Leg1ZeroCouponFlag, Leg1CompoundCouponFlag, Leg1RefRateOnFixingDateForwardMeasure,Leg1RefRateOnFixingDateForwardMeasure_PowerSpread, Leg1_PowerSpreadFlag, CpnRounding, HW2FFlag, MaxReturn = MaxReturn, MaxLoss = MaxLoss)
    Leg2_ResultData = Calc_Payoff_FDM_ForTimeGreed(ZeroTerm, ZeroRate, PriceDate, SwapEffectiveDate, Leg2RefRateOnFixingDate, Leg2RefRateOnFixingDate_PowerSpread, Nominal, 
                                    Leg2_Phase2StartDate, Leg2ForwardStart, Leg2ForwardEnd, Leg2PayDate, Leg2_DayCount,
                                    Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase1, Leg2_FixedCpnRate_Phase2, Leg2_FixingHistoryDate, 
                                    Leg2_FixingHistoryRate, Leg2ZeroCouponFlag, Leg2CompoundCouponFlag, Leg2RefRateOnFixingDateForwardMeasure,Leg2RefRateOnFixingDateForwardMeasure_PowerSpread, Leg2_PowerSpreadFlag, CpnRounding, HW2FFlag, MaxReturn = MaxReturn, MaxLoss = MaxLoss)
    DeltaTime = np.vectorize(DayCountAtoB)(SimulationDateList[:-1],SimulationDateList[1:])/365
    FDMTime = np.vectorize(DayCountAtoB)([PriceDate],SimulationDateList)/365
    r = np.interp(FDMTime, ZeroTerm, ZeroRate)
    DF_TimeGreed = np.exp(-r * FDMTime)
    if HW2FFlag == 0 : 
        Leg1PayoffAccum = np.r_[Leg1_ResultData["Payoff_Prev"][-1] * np.ones((1,NGreed)), Leg1_ResultData["Payoff_Simul"][:-1]]
        Leg2PayoffAccum = np.r_[Leg2_ResultData["Payoff_Prev"][-1] * np.ones((1,NGreed)), Leg2_ResultData["Payoff_Simul"][:-1]]
    else : 
        Leg1PayoffAccum = np.r_[Leg1_ResultData["Payoff_Prev"][-1] * np.ones((1,NGreed, NGreed)), Leg1_ResultData["Payoff_Simul"][:-1]]
        Leg2PayoffAccum = np.r_[Leg2_ResultData["Payoff_Prev"][-1] * np.ones((1,NGreed, NGreed)), Leg2_ResultData["Payoff_Simul"][:-1]]

    OptionExerciseOX = np.zeros(Leg1_ResultData["Payoff_Simul"][-1].shape)
    nextoptidx = len(OptionPayDate) - 1

    FDMValueAtGreedMax0Min = np.zeros((len(SimulationDateList),3))
    PayoffGreedMax0Min = np.zeros((len(SimulationDateList),2))
    Leg1SwapRateMax0Min = np.zeros((len(SimulationDateList),3))
    Leg2SwapRateMax0Min = np.zeros((len(SimulationDateList),3))
    if HW2FFlag == 0 : 
        Leg1SwapRateMax0Min[:,0] = Leg1SwapRate[:,0] if Leg1_PowerSpreadFlag == 0 else Leg1SwapRate[:,0] - Leg1SwapRate_PowerSpread[:, 0]
        Leg1SwapRateMax0Min[:,-1] = Leg1SwapRate[:,-1] if Leg1_PowerSpreadFlag == 0 else Leg1SwapRate[:,-1] - Leg1SwapRate_PowerSpread[:, -1]
        Leg2SwapRateMax0Min[:,0] = Leg2SwapRate[:,0] if Leg2_PowerSpreadFlag == 0 else Leg2SwapRate[:,0] - Leg2SwapRate_PowerSpread[:, 0]
        Leg2SwapRateMax0Min[:,-1] = Leg2SwapRate[:,-1] if Leg2_PowerSpreadFlag == 0 else Leg2SwapRate[:,-1] - Leg2SwapRate_PowerSpread[:, -1]
    else : 
        Leg1SwapRateMax0Min[:,0] = Leg1SwapRate[:,0,0] if Leg1_PowerSpreadFlag == 0 else Leg1SwapRate[:,0,0] - Leg1SwapRate_PowerSpread[:, 0, 0]
        Leg1SwapRateMax0Min[:,-1] = Leg1SwapRate[:,-1,-1] if Leg1_PowerSpreadFlag == 0 else Leg1SwapRate[:,-1,-1] - Leg1SwapRate_PowerSpread[:, -1, -1]
        Leg2SwapRateMax0Min[:,0] = Leg2SwapRate[:,0,0] if Leg2_PowerSpreadFlag == 0 else Leg2SwapRate[:,0,0] - Leg2SwapRate_PowerSpread[:, 0,0]
        Leg2SwapRateMax0Min[:,-1] = Leg2SwapRate[:,-1,-1] if Leg2_PowerSpreadFlag == 0 else Leg2SwapRate[:,-1,-1] - Leg2SwapRate_PowerSpread[:, -1, -1]
        
    for i in range(len(SimulationDateList)) : 
        FDMDate = SimulationDateList[::-1][i]
        T = FDMTime[::-1][i]
        if i == 0 : 
            FDMValue = Leg1_ResultData["Payoff_Simul"][-1] - Leg2_ResultData["Payoff_Simul"][-1]
            if HW2FFlag == 0 : 
                PayoffGreedMax0Min[-(i+1)][0] = np.interp(0, xt, Leg1_ResultData["Payoff_Simul"][-1])
                PayoffGreedMax0Min[-(i+1)][1] = np.interp(0, xt, Leg2_ResultData["Payoff_Simul"][-1])
            else : 
                PayoffGreedMax0Min[-(i+1)][0] = Linterp2D(xt, yt, Leg1_ResultData["Payoff_Simul"][-1], 0, 0)
                PayoffGreedMax0Min[-(i+1)][1] = Linterp2D(xt, yt, Leg2_ResultData["Payoff_Simul"][-1], 0, 0)
                
            if (FDMDate <= PriceDate) : 
                break
            
        else :         
            TPrev = FDMTime[::-1][i-1]
            deltat = DeltaTime[::-1][i-1]        
            df_t2 = DF_TimeGreed[::-1][i-1]
            df_t1 = DF_TimeGreed[::-1][i]
            PtT =  df_t2 / df_t1
            if HW2FFlag == 0 : 
                vol1 = np.interp((T+TPrev)/2, HWVolTerm, HWVol)
                an = -deltat * 0.5 * (kappa * xt / dxt + vol1 * vol1 / (dxt * dxt))
                bn = np.ones(len(an)) * (1.0 + deltat * vol1 * vol1 / (dxt * dxt)) + (1.0 / PtT - 1.0)
                cn = deltat * 0.5 * (kappa * xt / dxt - vol1 * vol1 / (dxt * dxt))
                a0 , b0 , c0 = an[0], bn[0], cn[0]
                aN , bN , cN = an[-1],bn[-1],cn[-1]
                bn[0] = 2*a0 + b0
                cn[0] = c0-a0
                bn[-1] = bN +2*cN
                an[-1] = aN - cN 
                k = np.array([an[1:], bn, cn[:-1]], dtype = object)
                n = len(bn)
                tdiag = np.zeros((n,n), dtype=bn.dtype)
                tdiag[np.arange(n), np.arange(n)] = bn
                tdiag[np.arange(1, n), np.arange(n-1)] = an[1:]
                tdiag[np.arange(n-1), np.arange(1, n)] = cn[:-1]                
                #offset = [-1,0,1]
                #tdiag = diags(k,offset).toarray()
                inv_tdiag = np.linalg.inv(tdiag)
                FDMValue = inv_tdiag.dot(FDMValue)
            else : 
                vol1 = np.interp((T+TPrev)/2, HWVolTerm, HWVol)
                vol2 = np.interp((T+TPrev)/2, HWVolTerm2, HWVol2)
                s2F = 0.5 * vol1 * vol2 * HWRho12Factor * deltat / (4.0 * dxt * dyt)
                
                #################
                # x tridiagonal #
                #################

                an1F = -deltat * 0.5 * (kappa * xt / dxt + vol1 * vol1 / (dxt * dxt))
                bn1F = np.ones(len(an1F)) * (1.0 + deltat * vol1 * vol1 / (dxt * dxt)) + (1.0 / PtT - 1.0) * 0.5
                cn1F = deltat * 0.5 * (kappa * xt / dxt - vol1 * vol1 / (dxt * dxt))
                a01F , b01F , c01F = an1F[0], bn1F[0], cn1F[0]
                aN1F , bN1F, cN1F = an1F[-1],bn1F[-1],cn1F[-1]
                bn1F[0] = 2*a01F + b01F
                cn1F[0] = c01F-a01F
                bn1F[-1] = bN1F +2*cN1F
                an1F[-1] = aN1F - cN1F 
                
                n = len(bn1F)
                tdiag1F = np.zeros((n,n), dtype=bn.dtype)
                tdiag1F[np.arange(n), np.arange(n)] = bn1F
                tdiag1F[np.arange(1, n), np.arange(n-1)] = an1F[1:]
                tdiag1F[np.arange(n-1), np.arange(1, n)] = cn1F[:-1]                  
                #k1F = np.array([an1F[1:], bn1F, cn1F[:-1]], dtype = object)
                #offset1F = [-1,0,1]
                #tdiag1F = diags(k1F,offset1F).toarray()
                inv_tdiag1F = np.linalg.inv(tdiag1F)

                ################
                # x implicited #
                ################
                
                adj1F = np.zeros((FDMValue.shape[0]+2,FDMValue.shape[1]+2))
                adj1F[1:-1,1:-1] = FDMValue
                adj1F[:,0] = adj1F[:,1] * 2 - adj1F[:,2]
                adj1F[:,-1] = adj1F[:,-2] * 2 - adj1F[:,-3]
                adj1F[0,:] = adj1F[1,:] * 2 - adj1F[2,:]
                adj1F[-1,:] = adj1F[-2,:] * 2 - adj1F[-3,:]
                RHSxt = s2F * (adj1F[2:,2:] + adj1F[:-2,:-2] - adj1F[2:,:-2] - adj1F[:-2, 2:]) + FDMValue              
                FDMValue = inv_tdiag1F.dot(RHSxt).T

                #################
                # y tridiagonal #
                #################

                an2F = -deltat * 0.5 * (kappa * yt / dyt + vol1 * vol1 / (dyt * dyt))
                bn2F = np.ones(len(an2F)) * (1.0 + deltat * vol1 * vol1 / (dyt * dyt)) + (1.0 / PtT - 1.0) * 0.5
                cn2F = deltat * 0.5 * (kappa * yt / dyt - vol1 * vol1 / (dyt * dyt))
                a02F , b02F , c02F = an2F[0], bn2F[0], cn2F[0]
                aN2F , bN2F, cN2F = an2F[-1],bn2F[-1],cn2F[-1]
                bn2F[0] = 2*a02F + b02F
                cn2F[0] = c02F-a02F
                bn2F[-1] = bN2F +2*cN2F
                an2F[-1] = aN2F - cN2F 

                n = len(bn2F)
                tdiag2F = np.zeros((n,n), dtype=bn.dtype)
                tdiag2F[np.arange(n), np.arange(n)] = bn2F
                tdiag2F[np.arange(1, n), np.arange(n-1)] = an2F[1:]
                tdiag2F[np.arange(n-1), np.arange(1, n)] = cn2F[:-1]  
                #k2F = np.array([an2F[1:], bn2F, cn2F[:-1]], dtype = object)
                #offset2F = [-1,0,1]
                #tdiag2F = diags(k2F,offset2F).toarray()
                inv_tdiag2F = np.linalg.inv(tdiag2F)

                ################
                # y implicited #
                ################

                adj2F = np.zeros((FDMValue.shape[0]+2,FDMValue.shape[1]+2))
                adj2F[1:-1,1:-1] = FDMValue
                adj2F[:,0] = adj2F[:,1] * 2 - adj2F[:,2]
                adj2F[:,-1] = adj2F[:,-2] * 2 - adj2F[:,-3]
                adj2F[0,:] = adj2F[1,:] * 2 - adj2F[2,:]
                adj2F[-1,:] = adj2F[-2,:] * 2 - adj2F[-3,:]
                RHSyt = s2F * (adj2F[2:,2:] + adj2F[:-2,:-2] - adj2F[2:,:-2] - adj2F[:-2, 2:]) + FDMValue              
                FDMValue = inv_tdiag2F.dot(RHSyt).T        
                
            if (FDMDate <= PriceDate) : 
                break
                    
            if (FDMDate in Leg1_ResultData["PayDate_Simul"]) and (Leg1ZeroCouponFlag == False) : 
                idx = list(Leg1_ResultData["PayDate_Simul"]).index(FDMDate)
                FDMValue += Leg1_ResultData["Payoff_Simul"][idx]
                PayoffGreedMax0Min[-(i+1)][0] = np.interp(0, xt, Leg1_ResultData["Payoff_Simul"][idx]) if HW2FFlag == 0 else Linterp2D(xt, yt, Leg1_ResultData["Payoff_Simul"][idx], 0, 0)            
            elif (FDMDate in Leg1_ResultData["PrevPayDate"]) and (Leg1ZeroCouponFlag == False) : 
                FDMValue += np.ones(FDMValue.shape) * Leg1_ResultData["Payoff_Prev"][-1]
                PayoffGreedMax0Min[-(i+1)][0] = float(Leg1_ResultData["Payoff_Prev"][-1])            

            if (FDMDate in Leg2_ResultData["PayDate_Simul"]) and (Leg2ZeroCouponFlag == False) : 
                idx = list(Leg2_ResultData["PayDate_Simul"]).index(FDMDate)
                FDMValue -= Leg2_ResultData["Payoff_Simul"][idx]
                PayoffGreedMax0Min[-(i+1)][1] = np.interp(0, xt, Leg2_ResultData["Payoff_Simul"][idx]) if HW2FFlag == 0 else Linterp2D(xt, yt, Leg2_ResultData["Payoff_Simul"][idx], 0, 0)            
            elif (FDMDate in Leg2_ResultData["PrevPayDate"]) and (Leg2ZeroCouponFlag == False) : 
                FDMValue -= np.ones(FDMValue.shape) * Leg2_ResultData["Payoff_Prev"][-1]
                PayoffGreedMax0Min[-(i+1)][1] = float(Leg2_ResultData["Payoff_Prev"][-1])            
        
        if i != 0 and len(OptionPayDate) > 0 and (FDMDate <= OptionPayDate[nextoptidx] and FDMDate >= OptionFixDate[nextoptidx]) : 
            if FDMDate == OptionPayDate[nextoptidx] : 
                OptionExerciseOX = OptionExerciseOX * 0
            FixDateOpt = OptionFixDate[nextoptidx]
            PayDateOpt = OptionPayDate[nextoptidx]
            t1 = DayCountAtoB(PriceDate, FDMDate)/365
            t2 = DayCountAtoB(PriceDate, PayDateOpt)/365
            tmat_Leg1 = DayCountAtoB(PriceDate, Leg1_ResultData["PayDate_Simul"][-1])/365
            tmat_Leg2 = DayCountAtoB(PriceDate, Leg2_ResultData["PayDate_Simul"][-1])/365
            df_t1 = Calc_Discount_Factor(ZeroTerm, ZeroRate, t1)
            df_t2 = Calc_Discount_Factor(ZeroTerm, ZeroRate, t2)
            df_tmat_Leg1 = Calc_Discount_Factor(ZeroTerm, ZeroRate, tmat_Leg1)
            df_tmat_Leg2 = Calc_Discount_Factor(ZeroTerm, ZeroRate, tmat_Leg2)
            
            Leg1_Idx = (FixDateOpt <= Leg1_ResultData["PayDate_Simul"]) & (PayDateOpt > Leg1_ResultData["FixingDate_Simul"])
            Leg2_Idx = (FixDateOpt <= Leg2_ResultData["PayDate_Simul"]) & (PayDateOpt > Leg2_ResultData["FixingDate_Simul"])

            if FDMDate <= Leg1_ResultData["PrevPayDate"][-1] : 
                Leg1_Acc = np.ones(FDMValue.shape) * Leg1_ResultData["PrevCummulativeCpn"][-1]
                Leg1_OptPayoff = np.ones(FDMValue.shape) *Leg1_ResultData["Payoff_Prev"][-1] - Leg1_Acc
            else : 
                Leg1_Acc = Leg1PayoffAccum[Leg1_Idx][-1] * float(Leg1ZeroCouponFlag == True)
                Leg1_OptPayoff = Leg1_ResultData["Payoff_Simul"][Leg1_Idx][-1] - Leg1_Acc
            
            if FDMDate <= Leg2_ResultData["PrevPayDate"][-1] : 
                Leg2_Acc = np.ones(FDMValue.shape) * Leg2_ResultData["PrevCummulativeCpn"][-1]
                Leg2_OptPayoff = np.ones(FDMValue.shape) *Leg2_ResultData["Payoff_Prev"][-1] - Leg2_Acc
            else : 
                Leg2_Acc = Leg2PayoffAccum[Leg2_Idx][-1] * float(Leg2ZeroCouponFlag == True)
                Leg2_OptPayoff = Leg2_ResultData["Payoff_Simul"][Leg2_Idx][-1] - Leg2_Acc
            
            NPV_ExerciseValue_Leg1 = Leg1_Acc * df_tmat_Leg1/df_t1 + Leg1_OptPayoff * df_t2/df_t1
            NPV_ExerciseValue_Leg2 = Leg2_Acc * df_tmat_Leg2/df_t1 + Leg2_OptPayoff * df_t2/df_t1
            NPV_ExerciseValue = NPV_ExerciseValue_Leg1 - NPV_ExerciseValue_Leg2
            if FDMDate == max(OptionPayDate[nextoptidx], OptionFixDate[nextoptidx]) : 
                if OptionHolder == 0 : 
                    OptionExerciseOX = NPV_ExerciseValue > FDMValue
                else : 
                    OptionExerciseOX = NPV_ExerciseValue < FDMValue
            FDMValue = (OptionExerciseOX == True) * NPV_ExerciseValue + (OptionExerciseOX == False) * FDMValue

            if FDMDate == min(OptionFixDate[nextoptidx], OptionPayDate[nextoptidx]) : 
                nextoptidx = max(0, nextoptidx - 1)
                
        if HW2FFlag == 0 : 
            ResultValue = np.interp(0, xt, FDMValue)
        else : 
            ResultValue = Linterp2D(xt, yt, FDMValue, 0, 0)

        FDMValueAtGreedMax0Min[-(i+1)][0] = np.round(FDMValue[0], 2) if HW2FFlag == 0 else FDMValue[0, 0]
        FDMValueAtGreedMax0Min[-(i+1)][1] = np.round(ResultValue, 2) 
        FDMValueAtGreedMax0Min[-(i+1)][2] = np.round(FDMValue[-1], 2) if HW2FFlag == 0 else FDMValue[-1, -1]
        if HW2FFlag == 0 : 
            Leg1SwapRateMax0Min[-(i+1)][1] = np.interp(0, xt, Leg1SwapRate[-(i+1)]) if Leg1_PowerSpreadFlag == 0 else np.interp(0, xt, Leg1SwapRate[-(i+1)]) - np.interp(0, xt, Leg1SwapRate_PowerSpread[-(i+1)])
            Leg2SwapRateMax0Min[-(i+1)][1] = np.interp(0, xt, Leg2SwapRate[-(i+1)]) if Leg2_PowerSpreadFlag == 0 else np.interp(0, xt, Leg2SwapRate[-(i+1)]) - np.interp(0, xt, Leg2SwapRate_PowerSpread[-(i+1)])
        else : 
            Leg1SwapRateMax0Min[-(i+1)][1] = Linterp2D(xt, yt, Leg1SwapRate[-(i+1)], 0, 0) if Leg1_PowerSpreadFlag == 0 else Linterp2D(xt, yt, Leg1SwapRate[-(i+1)], 0, 0) - Linterp2D(xt, yt, Leg1SwapRate_PowerSpread[-(i+1)], 0, 0)
            Leg2SwapRateMax0Min[-(i+1)][1] = Linterp2D(xt, yt, Leg2SwapRate[-(i+1)], 0, 0) if Leg2_PowerSpreadFlag == 0 else Linterp2D(xt, yt, Leg2SwapRate[-(i+1)], 0, 0) - Linterp2D(xt, yt, Leg2SwapRate_PowerSpread[-(i+1)], 0, 0)
            
    if HW2FFlag == 0 : 
        ResultPrice = np.interp(0, xt, FDMValue)
        ResultPriceXu = np.interp(0.01, xt, FDMValue)
        ResultPriceXd = np.interp(-0.01, xt, FDMValue)
        dPdx = (ResultPriceXu - ResultPriceXd)/(2.0 * 0.01)
        dPdy = 0
    else : 
        ResultPrice = Linterp2D(xt, yt, FDMValue, 0, 0)
        ResultPriceXu = Linterp2D(xt, yt, FDMValue, 0.01, 0)
        ResultPriceYu = Linterp2D(xt, yt, FDMValue, 0, 0.01)
        dPdx = (ResultPriceXu - ResultPrice)/(0.01)
        dPdy = (ResultPriceYu - ResultPrice)/(0.01)

    OptionExerciseDeclare = ["OptionExerciseDeclare" if i in OptionFixDate else '' for i in SimulationDateList] 
    OptionExercisePayment = ["OptionExercisePayment" if i in OptionPayDate else '' for i in SimulationDateList] 
    
    Result2 = pd.DataFrame(FDMValueAtGreedMax0Min, index = SimulationDateList, columns = ["V(xt("+str(np.round(xt[0],2))+"))","V(xt(0))","V(xt("+str(np.round(xt[-1],2))+"))"])
    Result3 = pd.DataFrame(Leg1SwapRateMax0Min, index = SimulationDateList, columns = ["Leg1Rate(xt("+str(np.round(xt[0],2))+"))","Leg1Rate(xt(0))","Leg1Rate(xt("+str(np.round(xt[-1],2))+"))"])
    Result4 = pd.DataFrame(Leg2SwapRateMax0Min, index = SimulationDateList, columns = ["Leg2Rate(xt("+str(np.round(xt[0],2))+"))","Leg2Rate(xt(0))","Leg2Rate(xt("+str(np.round(xt[-1],2))+"))"])
    Result1 = pd.DataFrame(PayoffGreedMax0Min, index = SimulationDateList, columns = ["Leg1CF","Leg2CF"])
    Result = pd.concat([Result1, Result2, Result3, Result4],axis = 1)

    Leg1FwdPayoff = [(Leg1_ResultData["Payoff_ForwardMeasure"][list(Leg1_ResultData["PayDate_Simul"]).index(i), 0]) if i in Leg1_ResultData["PayDate_Simul"] else 0 for i in SimulationDateList]
    Leg2FwdPayoff = [(Leg2_ResultData["Payoff_ForwardMeasure"][list(Leg2_ResultData["PayDate_Simul"]).index(i), 0]) if i in Leg2_ResultData["PayDate_Simul"] else 0 for i in SimulationDateList]
    if Leg1_ResultData["PrevPayDate"][-1] in SimulationDateList : 
        Leg1FwdPayoff[list(SimulationDateList).index(Leg1_ResultData["PrevPayDate"][-1])] = float(Leg1_ResultData["Payoff_Prev"][-1])
    if Leg2_ResultData["PrevPayDate"][-1] in SimulationDateList : 
        Leg2FwdPayoff[list(SimulationDateList).index(Leg2_ResultData["PrevPayDate"][-1])] = float(Leg2_ResultData["Payoff_Prev"][-1])
    Result["Leg1_Payoff_FwdMsr"] = Leg1FwdPayoff
    Result["Leg2_Payoff_FwdMsr"] = Leg2FwdPayoff
    Result["DiscountFactor"] = DF_TimeGreed
    Result["ResultPrice"] = ResultPrice
    Result["Leg1_DiscCurveName"] = Leg1_DiscCurveName
    Result["Leg1_EstCurveName"] = Leg1_EstCurveName
    Result["Leg2_DiscCurveName"] = Leg2_DiscCurveName
    Result["Leg2_EstCurveName"] = Leg2_EstCurveName
    Result["OptionDeclare"] = OptionExerciseDeclare
    Result["OptionPayment"] = OptionExercisePayment
    Result["dPdx"] = dPdx
    Result["dPdy"] = dPdy
            
    if LoggingFlag > 0 :                                 
        Result.to_csv(LoggingDir + "\\LoggingIRStructuredSwap.csv", index = True, encoding = "cp949")

    return Result            

def Pricing_IRCallableSwap_HWFDM_Greek(
    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
    Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
    NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
    Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
    ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
    kappa = 0.01, kappa2 = 0.01, HWVolTerm = [0.0001], HWVol = [0.006323], HWVolTerm2 = [0.0001], 
    HWVol2 = [0.003323], HWRho12Factor = -0.3, CpnRounding = 15, HW2FFlag = 0, LoggingFlag = 0, 
    LoggingDir = os.getcwd(), Leg1_DiscCurveName = "TempCurve", Leg1_EstCurveName = "TempCurve", Leg2_DiscCurveName = "TempCurve",
    Leg2_EstCurveName = "TempCurve", KoreanAutoHolidayFlag = True, FixHolidays = [], PayHolidays = [],
    Leg1_Phase2UseFlag = 0, NumCpnOneYear_Leg1_Phase2 = 0, Leg1_Phase2StartDate = 20280929, Leg1_RefSwapRate_Multiple_Phase2 = 0.0, Leg1_FixedCpnRate_Phase2 = 0.0237,   
    Leg2_Phase2UseFlag = 0, NumCpnOneYear_Leg2_Phase2 = 4, Leg2_Phase2StartDate = 20280929, Leg2_RefSwapRate_Multiple_Phase2 = 1.0, Leg2_FixedCpnRate_Phase2 = -0.0012,
    Leg1_PowerSpreadFlag = 0, Leg1_RefSwapMaturity_T_PowerSpread = 0.25, Leg2_PowerSpreadFlag = 0, Leg2_RefSwapMaturity_T_PowerSpread = 0.25,
    GreekFlag = 0) :
    
    ResultDict = {}
    RealLoggingFlag = LoggingFlag
    LoggingFlag = 0
    PInfo = Pricing_IRCallableSwap_HWFDM(
            Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
            Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
            NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
            Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
            ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
            kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, 
            HWVol2, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
            LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
            Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
            Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
            Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
            Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)

    P = PInfo["ResultPrice"].values[0]
    ResultDict["Price"] = P
    PV01Array = np.zeros(len(ZeroTerm))
    PVGammaArray = np.zeros(len(ZeroTerm))
    for i in range(len(ZeroTerm)) : 
        ZeroUp = np.array(ZeroRate).copy()
        ZeroUp[i] = ZeroUp[i] + 0.0001
        PuInfo = Pricing_IRCallableSwap_HWFDM(
                Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
                Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
                NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
                Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
                ZeroUp, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
                kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, 
                HWVol2, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
                LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
                Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
                Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
                Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
                Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)
        Pu = PuInfo["ResultPrice"].values[0]

        ZeroDn = np.array(ZeroRate).copy()
        ZeroDn[i] = ZeroUp[i] - 0.0001
        PdInfo = Pricing_IRCallableSwap_HWFDM(
                Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
                Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
                NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
                Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
                ZeroDn, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
                kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, 
                HWVol2, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
                LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
                Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
                Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
                Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
                Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)
        Pd = PdInfo["ResultPrice"].values[0]

        PV01 = (Pu - Pd)/2
        PV01Array[i] = PV01
        PVGammaArray[i] = (Pu + Pd - 2.0 * P)
    ResultDict["PV01"] = PV01Array
    ResultDict["PVGamma"] = PVGammaArray
    
    if GreekFlag > 1 :
        VegaArray = np.zeros(len(HWVolTerm)) 
        for i in range(len(HWVolTerm)) : 
            VUp = np.array(HWVol).copy()
            VUp[i] = VUp[i] + 0.0001    
            PVuInfo = Pricing_IRCallableSwap_HWFDM(
                    Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
                    Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
                    NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
                    Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
                    ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
                    kappa, kappa2, HWVolTerm, VUp, HWVolTerm2, 
                    HWVol2, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
                    LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
                    Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
                    Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
                    Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
                    Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)  
            Vega = PVuInfo["ResultPrice"].values[0] - P
            VegaArray[i] = Vega
        ResultDict["Vega"] = VegaArray
        ResultDict["VegaFRTB"] = VegaArray/0.0001 * np.array(HWVol)
        ResultDict["VegaTerm"] = HWVolTerm
        if HW2FFlag > 0 : 
            VegaArray2 = np.zeros(len(HWVolTerm2)) 
            for i in range(len(HWVolTerm2)) : 
                VUp = np.array(HWVol2).copy()
                VUp[i] = VUp[i] + 0.0001    
                PVuInfo = Pricing_IRCallableSwap_HWFDM(
                        Nominal, SwapEffectiveDate, PriceDate, SwapMaturity, NumCpnOneYear_Leg1_Phase1, 
                        Leg1_RefSwapRate_Multiple_Phase1, Leg1_RefSwapMaturity_T, Leg1_RefSwapNCPNOneYear, Leg1_FixedCpnRate_Phase1, Leg1_DayCount, 
                        NumCpnOneYear_Leg2_Phase1, Leg2_RefSwapRate_Multiple_Phase1, Leg2_RefSwapMaturity_T, Leg2_RefSwapNCPNOneYear, Leg2_FixedCpnRate_Phase1, 
                        Leg2_DayCount, OptionFixDate, OptionPayDate, OptionHolder_0Recever1Payer, ZeroTerm, 
                        ZeroRate, Leg1_FixingHistoryDate, Leg1_FixingHistoryRate, Leg2_FixingHistoryDate, Leg2_FixingHistoryRate, 
                        kappa, kappa2, HWVolTerm, HWVol, HWVolTerm2, 
                        VUp, HWRho12Factor, CpnRounding, HW2FFlag, LoggingFlag, 
                        LoggingDir, Leg1_DiscCurveName, Leg1_EstCurveName, Leg2_DiscCurveName,
                        Leg2_EstCurveName, KoreanAutoHolidayFlag, FixHolidays, PayHolidays,
                        Leg1_Phase2UseFlag, NumCpnOneYear_Leg1_Phase2, Leg1_Phase2StartDate, Leg1_RefSwapRate_Multiple_Phase2, Leg1_FixedCpnRate_Phase2,   
                        Leg2_Phase2UseFlag, NumCpnOneYear_Leg2_Phase2, Leg2_Phase2StartDate, Leg2_RefSwapRate_Multiple_Phase2, Leg2_FixedCpnRate_Phase2,
                        Leg1_PowerSpreadFlag, Leg1_RefSwapMaturity_T_PowerSpread, Leg2_PowerSpreadFlag, Leg2_RefSwapMaturity_T_PowerSpread)  
                Vega = PVuInfo["ResultPrice"].values[0] - P
                VegaArray2[i] = Vega
            ResultDict["Vega2"] = VegaArray2
            ResultDict["VegaTerm2"] = HWVolTerm2
            ResultDict["VegaFRTB2"] = VegaArray2/0.0001 * np.array(HWVol2)
    Result = PInfo
    if RealLoggingFlag > 0 : 
        T = DayCountAtoB(PriceDate, SwapMaturity)/365
        VegaT1 = list(np.array(HWVolTerm).astype(np.float64))
        VegaT2 = list(T - np.array(VegaT1))
        if len(PInfo) > len(ZeroTerm) : 
            DeltaTerm = list(ZeroTerm) + [0] * (len(PInfo) - len(ZeroTerm))
            DeltaPV01 = list(ResultDict["PV01"]) + [0] * (len(PInfo) - len(ZeroTerm))
            DeltaPV01Gamma = list(ResultDict["PVGamma"]) + [0] * (len(PInfo) - len(ZeroTerm))
        else : 
            DeltaTerm = list(ZeroTerm) 
            DeltaPV01 = list(ResultDict["PV01"])
            DeltaPV01Gamma = list(ResultDict["PVGamma"]) + [0] * (len(PInfo) - len(ZeroTerm))
        DeltaGamma = pd.DataFrame([DeltaTerm,DeltaPV01,DeltaPV01Gamma], index = ["DeltaTerm","DeltaPV01","DeltaPV01Gamma"]).T
        VegaHW = pd.DataFrame([])
        if GreekFlag > 1 :
            VegaHW = pd.DataFrame([VegaT1,VegaT2,list(ResultDict["Vega"]), list(ResultDict["VegaFRTB"])], index = ["VegaT1","VegaT2","VegaHW1","VegaFRTBHW1"]).T
            if HW2FFlag > 0 :
                VegaHW2 = pd.DataFrame([VegaT1,VegaT2,list(ResultDict["Vega2"]), list(ResultDict["VegaFRTB2"])], index = ["VegaT1","VegaT2","VegaHW2","VegaFRTBHW2"]).T
                VegaHW = pd.concat([VegaHW, VegaHW2],axis = 1)
        GreekDF = pd.concat([DeltaGamma, VegaHW],axis = 1)
        Result = pd.concat([PInfo.reset_index(), GreekDF],axis = 1)
        Result.to_csv(LoggingDir + "\\LoggingIRStructuredSwap.csv", index = False, encoding = "cp949")
        
    return ResultDict, Result

if __name__ == "__main__" : 
    print("######################################\nCreated By Daesun Lim (CIIA(R), FRM(R))\nRisk Validation Quant\nMy FRTB Module \n"+vers+" (RecentUpdated :" +recentupdate + ")" + "\n######################################\n")                


# %%
