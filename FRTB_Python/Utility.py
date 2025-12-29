#%%
"""
Created By Daesun Lim (CIIA(R), FRM(R))
Bank Risk Quant
My Utility Module 
v1.0.1
"""
import numpy as np
import pandas as pd
# JIT은 쓰지말자
vers = "1.0.1"
recentupdate = '20251221'

N_Info_Array  = 203
N_Info_array_raw = 203 * 12
Info_array_raw = [
    # 한국 음력 관련 하드코딩
    # 1: 평달29
    # 2: 평달30
    # 3: 평달29 윤달29
    # 4: 평달29 윤달30
    # 5: 평달30 윤달29
    # 6: 평달30 윤달30
    
    # 1841
    1, 2, 4, 1, 1, 2,   1, 2, 1, 2, 2, 1,    2, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 1,
    2, 2, 2, 1, 2, 1,   4, 1, 2, 1, 2, 1,    2, 2, 1, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 2, 1,   2, 1, 2, 1, 2, 1,    2, 1, 2, 1, 5, 2,   1, 2, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 3, 2, 1,   2, 1, 2, 1, 2, 2,    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,

    # 1851
    2, 2, 1, 2, 1, 1,   2, 1, 2, 1, 5, 2,    2, 1, 2, 2, 1, 1,   2, 1, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 2, 1, 2, 1, 2,   5, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 2,   1, 2, 2, 1, 2, 1,    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 5, 2,   1, 2, 1, 2, 2, 2,    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,    2, 1, 6, 1, 1, 2,   1, 1, 2, 1, 2, 2,

    # 1861
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 1, 2,    2, 1, 2, 1, 2, 2,   1, 2, 2, 3, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 4, 1,   2, 2, 1, 2, 2, 1,    2, 1, 1, 2, 1, 1,   2, 2, 1, 2, 2, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,    1, 2, 2, 3, 2, 1,   1, 2, 1, 2, 2, 1,
    2, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 1,    2, 2, 2, 1, 2, 1,   2, 1, 1, 5, 2, 1,

    # 1871
    2, 2, 1, 2, 2, 1,   2, 1, 2, 1, 1, 2,    1, 2, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    1, 1, 2, 1, 2, 4,   2, 1, 2, 2, 1, 2,    1, 1, 2, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,    2, 2, 1, 1, 5, 1,   2, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 4, 2, 1, 2,   1, 1, 2, 1, 2, 1,    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 1, 2,

    # 1881
    1, 2, 1, 2, 1, 2,   5, 2, 2, 1, 2, 1,    1, 2, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,    2, 1, 1, 2, 3, 2,   1, 2, 2, 1, 2, 2,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 5, 2, 1,   1, 2, 1, 2, 1, 2,    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 5, 2, 1, 2, 2,   1, 2, 1, 2, 1, 2,

    # 1891
    1, 2, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,    1, 1, 2, 1, 1, 5,   2, 2, 1, 2, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 5, 1,   2, 1, 2, 1, 2, 1,    2, 2, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,    2, 1, 5, 2, 2, 1,   2, 1, 2, 1, 2, 1,
    2, 1, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 5, 2, 2, 1, 2,

    # 1901
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 3, 2,   1, 1, 2, 2, 1, 2,    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 2, 1, 2,    1, 2, 2, 4, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,    2, 1, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    1, 5, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,

    #1911
    2, 1, 2, 1, 1, 5,   1, 2, 2, 1, 2, 2,    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,    2, 2, 1, 2, 5, 1,   2, 1, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 3, 2, 1, 2, 2,   1, 2, 2, 1, 2, 1,    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   5, 2, 2, 1, 2, 2,    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,

    #1921
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,    2, 1, 2, 2, 3, 2,   1, 1, 2, 1, 2, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 1, 2,    2, 1, 2, 1, 2, 2,   1, 2, 1, 2, 1, 1,
    2, 1, 2, 5, 2, 1,   2, 2, 1, 2, 1, 2,    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,    1, 5, 1, 2, 1, 1,   2, 2, 1, 2, 2, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,    1, 2, 2, 1, 1, 5,   1, 2, 1, 2, 2, 1,

    #1931
    2, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 1,    2, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,
    1, 2, 2, 1, 6, 1,   2, 1, 2, 1, 1, 2,    1, 2, 1, 2, 2, 1,   2, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,    2, 1, 4, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,    2, 2, 1, 1, 2, 1,   4, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,

    #1941
    2, 2, 1, 2, 2, 4,   1, 1, 2, 1, 2, 1,    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,    1, 1, 2, 4, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 1, 2,
    2, 5, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 2, 1, 2,   3, 2, 1, 2, 1, 2,    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,

    #1951
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 2, 1, 2, 4, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 1, 2, 2,   1, 2, 2, 1, 2, 2,    1, 1, 2, 1, 1, 2,   1, 2, 2, 1, 2, 2,
    2, 1, 4, 1, 1, 2,   1, 2, 1, 2, 2, 2,    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 5, 2, 1, 2, 2,    1, 2, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,    2, 1, 2, 1, 2, 5,   2, 1, 2, 1, 2, 1,

    #1961
    2, 1, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 2, 3, 2, 1,   2, 1, 2, 2, 2, 1,    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 1,    2, 2, 5, 2, 1, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 2, 1, 2,    1, 2, 2, 1, 2, 1,   5, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,    2, 1, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,

    #1971
    1, 2, 1, 1, 5, 2,   1, 2, 2, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 2, 1,    2, 2, 1, 5, 1, 2,   1, 1, 2, 2, 1, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 5, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 1,    2, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 6,   1, 2, 2, 1, 2, 1,    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,

    #1981
    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,    2, 1, 2, 3, 2, 1,   1, 2, 2, 1, 2, 2,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,    2, 1, 2, 2, 1, 1,   2, 1, 1, 5, 2, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,    1, 2, 2, 1, 2, 2,   1, 2, 1, 2, 1, 1,
    2, 1, 2, 2, 1, 5,   2, 2, 1, 2, 1, 2,    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,    1, 2, 1, 1, 5, 1,   2, 1, 2, 2, 2, 2,

    #1991
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,    1, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,
    1, 2, 5, 2, 1, 2,   1, 1, 2, 1, 2, 1,    2, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 2,   1, 5, 2, 1, 1, 2,    1, 2, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,    2, 1, 1, 2, 3, 2,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 1,

    #2001
    2, 2, 2, 3, 2, 1,   1, 2, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 1, 2, 2, 1,   2, 1, 1, 2, 1, 2,    1, 5, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 2, 1, 1,    2, 1, 2, 1, 2, 1,   5, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 5, 1,   2, 1, 2, 1, 2, 2,    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,

    #2011
    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,    2, 1, 6, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,    1, 2, 1, 2, 1, 2,   1, 2, 5, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 2, 2, 1, 2, 1,    2, 1, 2, 1, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 2, 1, 2, 3, 2,   1, 2, 1, 2, 2, 2,    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,    2, 1, 2, 5, 2, 1,   1, 2, 1, 2, 1, 2,

    # 2021
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,    2, 1, 2, 1, 2, 2,   1, 2, 1, 2, 1, 2,
    1, 5, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,    1, 2, 1, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 2, 1, 1, 5,   2, 1, 2, 2, 2, 1,    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 2,    1, 2, 2, 1, 5, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 1, 2, 2,    1, 2, 1, 2, 2, 1,   2, 1, 2, 1, 2, 1,

    # 2031
    2, 1, 5, 2, 1, 2,   2, 1, 2, 1, 2, 1,    2, 1, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 5, 2,    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,    2, 2, 1, 2, 1, 4,   1, 1, 2, 1, 2, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,    2, 2, 1, 2, 1, 2,   1, 2, 1, 1, 2, 1,
    2, 2, 1, 2, 5, 2,   1, 2, 1, 2, 1, 1,    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 2, 1,

    #2041
    2, 1, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,    1, 5, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2]

KoreaTempHolidayList = [20020701, 20150814, 20171002, 20200817, 20220309,
                        20220601, 20231002, 20240410, 20241001, 20250127,
                        20250603]

def CalcKoreaTempHolidayList(YYYY, KoreaTempHolidayList) : 
    n = 0
    for i in range(len(KoreaTempHolidayList)) : 
        if (YYYY == int(KoreaTempHolidayList[i] // 10000)) :
            n += 1
    
    ResultKoreaTempHolidayList = [0] * n
    
    n = 0
    for i in range(len(KoreaTempHolidayList)) : 
        if (YYYY == int(KoreaTempHolidayList[i] // 10000)) :
            ResultKoreaTempHolidayList[n] = KoreaTempHolidayList[i]
            n += 1
            
    return ResultKoreaTempHolidayList                

def CalcLunarToSolar(YYYYMMDD, Leaf, ResultArray2, _info_array_raw) : 

    Year = YYYYMMDD // 10000
    Month = (YYYYMMDD - Year * 10000) // 100
    Day = (YYYYMMDD - Year * 10000 - Month * 100)
    if (Year < 1841 or 2043 < Year) :
        return -99999999
    if (Month < 1 or 12 < Month) :
        return -99999999

    info_array = np.array(Info_array_raw).reshape(N_Info_Array, 12)

    info_month = [ 31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

    lyear = Year
    lmonth = Month
    y1 = lyear - 1841
    m1 = lmonth - 1
    leapyes = 0
    mm = 0
    if (info_array[y1][m1] > 2) :
        leapyes = Leaf

    if (leapyes == 1) : 
        if (info_array[y1][m1] == 3 or info_array[y1][m1] == 5) :
            mm = 29
        elif (info_array[y1][m1] == 4 or info_array[y1][m1] == 6) :
            mm = 30
        else :
            return -99999999
    else :
        if (info_array[y1][m1] == 1 or info_array[y1][m1] == 3 or info_array[y1][m1] == 4) :
            mm = 29
        elif (info_array[y1][m1] == 2 or info_array[y1][m1] == 5 or info_array[y1][m1] == 6) :
            mm = 30
        else :
            return -99999999

    if (Day < 1 or mm < Day) :
        return -99999999

    lday = Day
    td = 0
    for i in range(y1) : 
        for j in range(12) : 
            if (info_array[i][j] == 1) :
                td += 29
            elif (info_array[i][j] == 2) : 
                td += 30
            elif (info_array[i][j] == 3) :
                td += 58            
            elif (info_array[i][j] == 4) :
                td += 59            
            elif (info_array[i][j] == 5) :
                td += 59            
            elif (info_array[i][j] == 6) :
                td += 60
            else :
                return -99999999

    for j in range(m1) : 
        if (info_array[y1][j] == 1) :
            td += 29
        elif (info_array[y1][j] == 2) :
            td += 30
        elif (info_array[y1][j] == 3) :  
            td += 58
        elif (info_array[y1][j] == 4) :
            td += 59
        elif (info_array[y1][j] == 5) :
            td += 59
        elif (info_array[y1][j] == 6) :
            td += 60
        else :
            return -99999999

    if (leapyes == 1) : 
        if (info_array[y1][m1] == 3 or info_array[y1][m1] == 4) :
            td += 29
        elif (info_array[y1][m1] == 5 or info_array[y1][m1] == 6) :
            td += 30
        else :
            return -99999999
        
    td += lday + 22
    y1 = 1840
    leap = 0
    y2 = 0
    while True : 
        y1 += 1
        leap = ((y1 % 4 == 0 and y1 % 100 != 0) or y1 % 400 == 0)

        if (leap) :
            y2 = 366
        else :
            y2 = 365

        if (td <= y2) :
            break
        td -= y2

    syear = y1
    info_month[1] = y2 - 337
    m1 = 0

    while True : 
        m1 += 1
        if (td <= info_month[m1 - 1]) :
            break
        td -= info_month[m1 - 1]

    smonth = m1
    sday = td
    y = syear - 1
    td = y * 365 + y // 4 - y // 100 + y // 400
    for i in range(smonth - 1) : 
        td += info_month[i]

    td += sday
    w = td % 7
    YYYYMMDD = syear * 10000 + smonth * 100 + sday
    ResultArray2[0] = YYYYMMDD
    ResultArray2[1] = w
    return 1

def LunarToSolar(YYYYMMDD_Lunar, Leap = 0) :
    ResultArray2 = [0,0]
    ResultCode = CalcLunarToSolar(YYYYMMDD_Lunar, Leap, ResultArray2, Info_array_raw)
    if (ResultCode < 0) :
        return ResultCode
    else :
        return ResultArray2[0]

def LeapCheck(Year) : 
    Year = int(Year)
    return 1 if ((Year % 4 == 0 and Year % 100 != 0 ) or Year % 400 == 0) else 0

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

def EDate_YYYYMMDD(YYYYMMDD, NMonths) : 
    YYYYMMDD = int(YYYYMMDD)
    NMonths = int(NMonths)

    Leap = 0
    
    Year = int(YYYYMMDD / 10000)
    Month = int((YYYYMMDD - Year * 10000) / 100)
    Day = int((YYYYMMDD - Year * 10000 - Month * 100))
    
    TargetMonth = Month + NMonths
    PlusYear = 0
    ResultMonth = 0
    ResultDay = 0
    if (TargetMonth > 12) : 
        PlusYear = int(TargetMonth // 12)
        ResultMonth = TargetMonth % 12
        Leap = LeapCheck(Year + PlusYear)
        if (Leap == 1) : 
            ResultDay = min(Day, DaysOfMonthLeap(ResultMonth - 1))
        else : 
            ResultDay = min(Day, DaysOfMonth(ResultMonth - 1))
        
        if (TargetMonth % 12 != 0) : 
            return (Year + PlusYear) * 10000 + ResultMonth * 100 + ResultDay
        else : 
            return (Year + PlusYear - 1) * 10000 + 12 * 100 + ResultDay
    elif (TargetMonth > 0) : 
        ResultMonth = TargetMonth
        Leap = LeapCheck(Year)
        if (Leap == 1) : 
            ResultDay = min(Day, DaysOfMonthLeap(ResultMonth - 1))
        else : 
            ResultDay = min(Day, DaysOfMonth(ResultMonth - 1))
        return Year * 10000 + ResultMonth * 100 + ResultDay
    else : 
        if (TargetMonth >= -12) : 
            PlusYear = -1
            ResultMonth = (12 + TargetMonth)
            Leap = LeapCheck(Year + PlusYear)
        else : 
            PlusYear = int(TargetMonth // 12)
            ResultMonth = (TargetMonth % 12)
            Leap = LeapCheck(Year + PlusYear)
        
        if (ResultMonth == 0) : 
            ResultMonth = 12
            PlusYear -= 1
            Leap = LeapCheck(Year + PlusYear)
        if (Leap == 1) : 
            ResultDay = min(Day, DaysOfMonthLeap(ResultMonth - 1))
        else : 
            ResultDay = min(Day, DaysOfMonth(ResultMonth - 1))
        return (Year + PlusYear) * 10000 + ResultMonth * 100 + ResultDay

def DayCountAtoB(Day1, Day2) : 
    return YYYYMMDDToExcelDate(Day2) - YYYYMMDDToExcelDate(Day1)

def MonthCountAtoB(YYYYMMDD1, YYYYMMDD2) : 
    Y1, Y2 = (YYYYMMDD1 // 10000) , (YYYYMMDD2 // 10000)
    M1, M2 = YYYYMMDD1//100 - Y1*100, YYYYMMDD2//100 - Y2*100
    diffY = Y2 - Y1
    diffM = M2 - M1
    return diffY * 12 + diffM

def DayPlus(cdate: int, ndays: int) -> int:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    year = cdate // 10000
    month = (cdate % 10000) // 100
    day = cdate % 100
    
    while ndays > 0:
        leap = LeapCheck(year)
        days_in_month[1] = 29 if leap else 28
        
        days_remaining = days_in_month[month - 1] - day
        
        if ndays <= days_remaining:
            day += ndays
            ndays = 0
        else:
            ndays -= (days_remaining + 1)
            day = 1
            month += 1
            
            if month > 12:
                month = 1
                year += 1
    
    if ndays < 0 : 
        return ExcelDateToYYYYMMDD(YYYYMMDDToExcelDate(cdate) + ndays)
    
    return year * 10000 + month * 100 + day

def BusinessDateArrayFromAtoB(StartY, EndY, HolidayList) : 
    StartYYYYMMDD = StartY *10000 +  101
    EndYYYYMMDD = EndY *10000 + 101
    n = DayCountAtoB(StartYYYYMMDD, EndYYYYMMDD) + 1
    BD = []
    BDExcel = []
    for d in range(n) : 
        TempDate = StartYYYYMMDD if d == 0 else DayPlus(TempDate, 1)
        ExcelDate = YYYYMMDDToExcelDate(TempDate)
        MOD7 = ExcelDate % 7
        if (MOD7 not in [0,1]) and (TempDate not in HolidayList) :         
            BD.append(TempDate)
            BDExcel.append(ExcelDate)
    return BD, BDExcel

def Calc_ChildrensDay_Korea(YYYY) :
    '''
    3.1절
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 505
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_31Day_Korea(YYYY) :
    '''
    어린이날
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 301
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)


def Calc_Gwangbok_Korea(YYYY) :
    '''
    광복절
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 815
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_GaechunJeol_Korea(YYYY) :
    '''
    개천절
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 1003
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_Hangul_Korea(YYYY) :
    '''
    한글날
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 1009
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_Christmas_Korea(YYYY) :
    '''
    크리스마스
    '''
    YYYYMMDD_Solar = YYYY * 10000 + 1225
    MOD07 = YYYYMMDDToExcelDate(YYYYMMDD_Solar) % 7
    # 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    return DayPlus(YYYYMMDD_Solar, 2) if (MOD07 == 0) else (DayPlus(YYYYMMDD_Solar, 1) if (MOD07 == 1) else YYYYMMDD_Solar)

def Calc_Budda_Korea(YYYY) :
    # 4월 8일
    YYYYMMDD_Lunar = YYYY * 10000 + 408
    ResultArray2 = [0, 0]
    ResultCode = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, Info_array_raw)
    YYYYMMDD_Solar = ResultArray2[0]
    
    # 부처님오신날이 어린이날이랑 같은 말도안되는 때가 있음 
    ChildDay = Calc_ChildrensDay_Korea(YYYY)
    if (ResultCode < 0) :
        return YYYY * 10000 + 101
    elif (ChildDay == YYYYMMDD_Solar) :
        if (ResultArray2[1] == 5) :           
            #어린이날 또는 어린이날의 대체휴일과 부처님오신날이 같고 금요일
            return DayPlus(YYYYMMDD_Solar, 3)
        else :                                
        # 그 외의 경우
            return DayPlus(ChildDay, 1)
    else :
        if (ResultArray2[1] == 0) :
            # 일요일
            return DayPlus(YYYYMMDD_Solar, 1)
        elif (ResultArray2[1] == 6) :
        # 토요일
            return DayPlus(YYYYMMDD_Solar, 2)
        else :
            return YYYYMMDD_Solar

def Calc3_newyear(YYYY):
    '''
    구정 3일
    '''
    YYYYMMDD_Lunar = YYYY * 10000 + 101
    ResultArray2 = [0, 0]
    Result = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, Info_array_raw)
    YYYYMMDD_Solar = ResultArray2[0]
    ResultCode = Result
    
    if ResultCode >= 0:
        b = ResultArray2[1]
        ResultDay3 = [
            DayPlus(YYYYMMDD_Solar, -1),
            YYYYMMDD_Solar,
            DayPlus(YYYYMMDD_Solar, 1)
        ]
        
        if b == 6:
            # 구정이 토요일인 경우 세번째 날짜가 일요일인데 그걸 월요일로 변경
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)
        elif b == 0:
            # 구정이 일요일인 경우
            ResultDay3[1] = ResultDay3[2]  # 월요일
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)  # 화요일
        elif b == 1:
            # 구정이 월요일인 경우 첫번째 날짜가 일요일인데 그걸 화요일로 변경
            ResultDay3[0] = ResultDay3[1]  # 월요일
            ResultDay3[1] = ResultDay3[2]  # 화요일
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)  # 수요일
        return ResultDay3
    else : 
        return [YYYY * 10000 + 101] * 3

def Calc3_chuseok(YYYY):
    '''
    추석 3일
    '''
    YYYYMMDD_Lunar = YYYY * 10000 + 815
    ResultArray2 = [0, 0]
    Result = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, Info_array_raw)
    YYYYMMDD_Solar = ResultArray2[0]
    ResultCode = Result
    
    if ResultCode >= 0:
        b = ResultArray2[1]
        ResultDay3 = [
            DayPlus(YYYYMMDD_Solar, -1),
            YYYYMMDD_Solar,
            DayPlus(YYYYMMDD_Solar, 1)
        ]
        
        if b == 6:
            # 추석이 토요일인 경우 세번째 날짜가 일요일인데 그걸 월요일로 변경
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)
        elif b == 0:
            # 추석이 일요일인 경우
            ResultDay3[1] = ResultDay3[2]  # 월요일
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)  # 화요일
        elif b == 1:
            # 추석이 월요일인 경우 첫번째 날짜가 일요일인데 그걸 화요일로 변경
            ResultDay3[0] = ResultDay3[1]  # 월요일
            ResultDay3[1] = ResultDay3[2]  # 화요일
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2)  # 수요일
        return ResultDay3
    else : 
        return [YYYY * 10000 + 101] * 3

def FixedHoliday_YYYYMMDD(YYYYMMDD) : 
    '''
    공휴일이 토요일이면 금요일, 일요일이면 월요일 대체공휴일
    '''
    ExcelDate = YYYYMMDDToExcelDate(YYYYMMDD)
    MOD07 = ExcelDate % 7
    return DayPlus(YYYYMMDD, -1) if MOD07 == 0 else (DayPlus(YYYYMMDD, 1) if MOD07 == 1 else YYYYMMDD)

def Nth_Date(YYYY, MM, Nth, Date) : 
    '''
    # YYYY = 년
    # MM = 월
    # Nth = n번째
    # Date = x요일 0:토 1:일 2:월 3:화 4:수 5:목 6:금    
    '''
    YYYYMMDD = YYYY * 10000 + MM * 100 + 1
    YYYYMM = YYYY * 100 + MM
    ExcelDate = YYYYMMDDToExcelDate(YYYYMMDD)
    
    n = 0
    for i in range(31) : 
        TempDate = ExcelDate + i
        MOD7 = TempDate % 7
        if (MOD7 == Date) : 
            n += 1
            nthdate = ExcelDateToYYYYMMDD(TempDate)
            if (n == Nth) : 
                nthdateYYYYMM = nthdate // 100
                if YYYYMM == nthdateYYYYMM : 
                    return nthdate
                elif (YYYYMM < nthdateYYYYMM) : 
                    return ExcelDateToYYYYMMDD(TempDate - 7)
    return nthdate                
            
def Mapping_KoreaHoliday16(YYYY) :
    '''
    공휴일 16개 매핑하기
    '''
    Array16 = []

    Jan01 = YYYY * 10000 + 101                            
    Array16.append(Jan01)
        
    Seol = Calc3_newyear(YYYY)
    Array16 += list(Seol)

    Samil = Calc_31Day_Korea(YYYY)
    Array16.append(Samil)

    Labor = YYYY * 10000 + 501
    Array16.append(Labor)

    Budda = Calc_Budda_Korea(YYYY)
    Array16.append(Budda)

    ChildrenDay = Calc_ChildrensDay_Korea(YYYY)
    Array16.append(ChildrenDay)
    Array16.append(YYYY * 10000 + 606)
    Gwangbok = Calc_Gwangbok_Korea(YYYY)
    Array16.append(Gwangbok)

    Chuseok = Calc3_chuseok(YYYY)
    Array16 += Chuseok

    GaeChun = Calc_GaechunJeol_Korea(YYYY)
    if (GaeChun == Chuseok[0] or GaeChun == Chuseok[1] or GaeChun == Chuseok[2]) : 
        # 개천절이 추석에 껴있을 경우 하루 더 대체휴일
        GaeChun = DayPlus(Chuseok[2], 1)
        if (YYYYMMDDToExcelDate(GaeChun) % 7 == 0) :
            GaeChun = DayPlus(GaeChun, 2)
        elif (YYYYMMDDToExcelDate(GaeChun) % 7 == 1) :
            GaeChun == DayPlus(GaeChun, 1)

    Array16.append(GaeChun)
    HanGul = Calc_Hangul_Korea(YYYY)
    Array16.append(HanGul)

    Christmas = Calc_Christmas_Korea(YYYY)
    Array16.append(Christmas)
    return Array16

def Mapping_USHoliday(YYYY) : 
    
    Jan01 = (YYYY * 10000 + 101)
    Jan01Excel = YYYYMMDDToExcelDate(Jan01)
    if (Jan01Excel % 7 == 1) :
        Jan01 = DayPlus(Jan01, 1)
        
    President = FixedHoliday_YYYYMMDD(YYYY * 10000 + 120)    
    Juneteenth = FixedHoliday_YYYYMMDD(YYYY * 10000 + 619)
    Independence = FixedHoliday_YYYYMMDD(YYYY * 10000 + 704)
    Veterans = FixedHoliday_YYYYMMDD(YYYY * 10000 + 1111)
    Christmas = FixedHoliday_YYYYMMDD(YYYY * 10000 + 1225)
    MartinLuther = Nth_Date(YYYY, 1, 3, 2)
    PresidentsDay = Nth_Date(YYYY, 2, 3, 2)
    MemorialDay = Nth_Date(YYYY, 5, 5, 2)
    LaborDay = Nth_Date(YYYY, 9, 1, 2)
    ColumBus = Nth_Date(YYYY, 10, 2, 2)
    Thanks = Nth_Date(YYYY, 11, 4, 5)
    Array11 = [Jan01, Juneteenth, Independence, Veterans, Christmas, 
               MartinLuther, PresidentsDay, MemorialDay, LaborDay, ColumBus, 
               Thanks]
    return Array11
        
def KoreaHolidaysFromStartToEnd(StartY : int, EndY : int) : 
    ResultList = []
    for y in range(StartY, EndY + 1) : 
        templist = Mapping_KoreaHoliday16(y)
        ResultList += templist
    return sorted(list(set(ResultList)))

def USHolidaysFromStartToEnd(StartY : int, EndY : int) : 
    ResultList = []
    for y in range(StartY, EndY + 1) : 
        templist = Mapping_USHoliday(y)
        ResultList += templist
    return sorted(list(set(ResultList)))

def LastBusinessDate(YYYYMM, HolidayArray) : 
    YYYY = int(YYYYMM // 100)
    MM = int(YYYYMM - YYYY * 100)
    Leap = LeapCheck(YYYY)
    
    LastYYYYMMDD = YYYY * 10000 + MM * 100 + 1
    if MM in [1,3,5,7,8,10,12] : 
        LastYYYYMMDD = YYYY * 10000 + MM * 100 + 31
    elif MM in [4,6,9,11] :
        LastYYYYMMDD = YYYY * 10000 + MM * 100 + 30
    else : 
        if (Leap == 1) : 
            LastYYYYMMDD = YYYY * 10000 + MM * 100 + 29
        else : 
            LastYYYYMMDD = YYYY * 10000 + MM * 100 + 28
    
    LastExcelDate = YYYYMMDDToExcelDate(LastYYYYMMDD)
    MOD07 = LastExcelDate % 7
    SaturSundayFlag = 0
    HolidayFlag = 0
    TempExcelDate = LastExcelDate
    TempYYYYMMDD = LastYYYYMMDD
    if (MOD07 == 1 or MOD07 == 0) :
        SaturSundayFlag = 1
    
    if (LastYYYYMMDD in HolidayArray) : 
        HolidayFlag = 1
    
    if (SaturSundayFlag == 0 and HolidayFlag == 0) : 
        return LastYYYYMMDD
    else : 
        for i in range(31) : 
            TempExcelDate = LastExcelDate - i
            TempYYYYMMDD = ExcelDateToYYYYMMDD(TempExcelDate)
            MOD07 = TempExcelDate % 7
            
            if (MOD07 == 1 or MOD07 == 0) : 
                SaturSundayFlag = 1
            else : 
                SaturSundayFlag = 0
            HolidayFlag = 0 
            if TempYYYYMMDD in HolidayArray : 
                HolidayFlag = 1
            
            if (SaturSundayFlag == 0 and HolidayFlag == 0) : 
                break
        return TempYYYYMMDD

def DayCountFractionAtoB(day1, day2, flag, holidays = []) : 
    holidaysarray = np.array(holidays)

    if day1 < 19000101:
        day1 = ExcelDateToYYYYMMDD(day1)
    if day2 < 19000101:
        day2 = ExcelDateToYYYYMMDD(day2)
    
    if flag == 0:
        return DayCountAtoB(day1, day2) / 365.0
    elif flag == 1:
        return DayCountAtoB(day1, day2) / 360.0
    elif flag == 2:
        year_a, month_a, day_a = day1 // 10000, (day1 % 10000) // 100, day1 % 100
        year_b, month_b, day_b = day2 // 10000, (day2 % 10000) // 100, day2 % 100
        
        next_y = day1 + 10000
        if day1 < day2 < next_y:
            div = DayCountAtoB(day1, next_y)
            return DayCountAtoB(day1, day2) / div
        else:
            tau = 0.0
            for i in range(year_b - year_a + 1):
                current_y = day1 + i * 10000
                next_y = day1 + (i + 1) * 10000
                if current_y < day2 <= next_y:
                    div = DayCountAtoB(current_y, next_y)
                    tau += DayCountAtoB(current_y, day2) / div
                    break
                else:
                    tau += 1.0
            return tau
    elif flag == 3:
        year_a, month_a = day1 // 10000, (day1 % 10000) // 100
        year_b, month_b = day2 // 10000, (day2 % 10000) // 100
        n_month = (year_b - year_a) * 12 + (month_b - month_a)
        return (30.0 * n_month) / 360.0
    else:
        day1_excel = YYYYMMDDToExcelDate(day1)
        day2_excel = YYYYMMDDToExcelDate(day2)
        for i in range(len(holidaysarray)):
            if holidaysarray[i] < 19000101:
                holidaysarray[i] = ExcelDateToYYYYMMDD(holidaysarray[i])
        
        nbd = 0
        for temp_date_excel in range(day1_excel, day2_excel):
            temp_c_date = ExcelDateToYYYYMMDD(temp_date_excel)
            mod7 = temp_date_excel % 7
            if (mod7 not in (0, 1)) and (temp_c_date not in holidaysarray):
                nbd += 1
        
        return nbd / 252.0    

def malloc_cpn_date_holiday(price_date_yyyymmdd, swap_mat_yyyymmdd, ann_cpn_one_year, holiday_yyyymmdd = [], modified_following=1):
    price_yyyy = price_date_yyyymmdd // 10000
    price_mm = (price_date_yyyymmdd % 10000) // 100
    
    swap_mat_yyyy = swap_mat_yyyymmdd // 10000
    swap_mat_mm = (swap_mat_yyyymmdd % 10000) // 100
    
    n = ((swap_mat_yyyymmdd // 10000 - price_date_yyyymmdd // 10000) + 2) * ann_cpn_one_year
    narray = 0
    first_cpn_date = None
    
    if ann_cpn_one_year == 0:
        narray = 1
        n = 1
    else:
        m = max(1, 12 // ann_cpn_one_year)
        for i in range(n):
            cpn_date = swap_mat_yyyymmdd if i == 0 else EDate_YYYYMMDD(swap_mat_yyyymmdd, -i * m)
            if DayCountAtoB(price_date_yyyymmdd, cpn_date) < 7:
                first_cpn_date = cpn_date
                break
            if cpn_date <= price_date_yyyymmdd:
                break
            narray += 1
    
    result_cpn_date = [0] * narray
    
    for i in range(n):
        cpn_date = swap_mat_yyyymmdd if i == 0 else EDate_YYYYMMDD(swap_mat_yyyymmdd, -i * m)
        
        if cpn_date <= price_date_yyyymmdd or DayCountAtoB(price_date_yyyymmdd, cpn_date) < 7:
            break
        
        cpn_date_excel = YYYYMMDDToExcelDate(cpn_date)
        mod7 = cpn_date_excel % 7
        satur_sunday_flag = 1 if (mod7 in [0, 1] or cpn_date in holiday_yyyymmdd) else 0
        
        if not satur_sunday_flag:
            result_cpn_date[narray - 1 - i] = cpn_date
        else:
            if modified_following == 1:
                for j in range(1, 15):
                    cpn_date_excel += 1
                    mod7 = cpn_date_excel % 7
                    cpn_date_temp = ExcelDateToYYYYMMDD(cpn_date_excel)
                    if (mod7 not in [0, 1]) and (cpn_date_temp not in holiday_yyyymmdd):
                        prev_date = ExcelDateToYYYYMMDD(cpn_date_excel)
                        break
                result_cpn_date[narray - 1 - i] = min(LastBusinessDate(cpn_date // 100, holiday_yyyymmdd), prev_date)
            else:
                for j in range(1, 15):
                    cpn_date_excel += 1
                    mod7 = cpn_date_excel % 7
                    cpn_date_temp = ExcelDateToYYYYMMDD(cpn_date_excel)
                    if (mod7 not in [0, 1]) and (cpn_date_temp not in holiday_yyyymmdd) :
                        cpn_date = ExcelDateToYYYYMMDD(cpn_date_excel)
                        break
                result_cpn_date[narray - 1 - i] = cpn_date
    
    if ann_cpn_one_year == 1 and price_mm != swap_mat_mm:
        target_date_yyyymmdd = result_cpn_date[0]
        for i in range(1, 13):
            target_date_yyyymmdd = EDate_YYYYMMDD(target_date_yyyymmdd, -1)
            target_date_yyyy = target_date_yyyymmdd // 10000
            target_date_mm = (target_date_yyyymmdd % 10000) // 100
            if target_date_yyyy == price_yyyy and target_date_mm == price_mm:
                first_cpn_date = target_date_yyyymmdd
                break
    
    return result_cpn_date, first_cpn_date

def ParseBusinessDateIfHoliday(YYYYMMDD, Holidays) :
    NHolidays = len(Holidays)
    if YYYYMMDD < 19000101:
        YYYYMMDD = ExcelDateToYYYYMMDD(YYYYMMDD)
    
    for i in range(NHolidays):
        if Holidays[i] < 19000101:
            Holidays[i] = ExcelDateToYYYYMMDD(Holidays[i])
    
    ResultYYYYMMDD = 0
    ExcelDate = YYYYMMDDToExcelDate(YYYYMMDD)
    IsHolidayFlag = 0
    IsSaturSundayFlag = 0
    MOD7 = ExcelDate % 7
    
    if MOD7 == 0 or MOD7 == 1:
        IsSaturSundayFlag = 1
    
    if (YYYYMMDD in Holidays):
        IsHolidayFlag = 1
    
    if IsSaturSundayFlag == 0 and IsHolidayFlag == 0:
        ResultYYYYMMDD = YYYYMMDD
    else:
        for i in range(100):
            TempExcelDate = ExcelDate + 1 + i
            TempYYYYMMDD = ExcelDateToYYYYMMDD(TempExcelDate)
            MOD7 = TempExcelDate % 7
            
            if MOD7 == 0 or MOD7 == 1:
                IsSaturSundayFlag = 1
            else:
                IsSaturSundayFlag = 0
            
            if (TempYYYYMMDD in Holidays):
                IsHolidayFlag = 1
            else:
                IsHolidayFlag = 0
            
            if IsSaturSundayFlag == 0 and IsHolidayFlag == 0:
                ResultYYYYMMDD = TempYYYYMMDD
                break
    
    return ResultYYYYMMDD

def NextNthBusinessDate(YYYYMMDD, NBDate, Holidays) : 
    if YYYYMMDD < 19000101 : 
        YYYYMMDD = ExcelDateToYYYYMMDD(YYYYMMDD)
    StartDate = ParseBusinessDateIfHoliday(YYYYMMDD, Holidays)
    StartDateExcel = YYYYMMDDToExcelDate(StartDate)
    for i in range(len(Holidays)) : 
        if (Holidays[i] < 19000101) : 
            Holidays[i] = ExcelDateToYYYYMMDD(Holidays[i])

    ResultYYYYMMDD = YYYYMMDD
    if (NBDate > 0) : 
        n = 0 
        for i in range(100) : 
            TempExcelDate = StartDateExcel + 1 + i
            TempYYYYMMDD = ExcelDateToYYYYMMDD(TempExcelDate)
            MOD7 = TempExcelDate % 7
            IsSaturSundayFlag = 1 if (MOD7 in [0, 1]) else 0
            IsHolidayFlag = 1 if TempYYYYMMDD in Holidays else 0
            if IsSaturSundayFlag == 0 and IsHolidayFlag == 0: 
                n += 1
            
            if n >= NBDate : 
                ResultYYYYMMDD = TempYYYYMMDD
                break
    elif (NBDate < 0) : 
        n = 0 
        for i in range(100) : 
            TempExcelDate = StartDateExcel - 1 - i
            TempYYYYMMDD = ExcelDateToYYYYMMDD(TempExcelDate)
            MOD7 = TempExcelDate % 7
            IsSaturSundayFlag = 1 if (MOD7 in [0, 1]) else 0
            IsHolidayFlag = 1 if TempYYYYMMDD in Holidays else 0
            if IsSaturSundayFlag == 0 and IsHolidayFlag == 0: 
                n += 1
            
            if n >= abs(NBDate) : 
                ResultYYYYMMDD = TempYYYYMMDD
                break
    return ResultYYYYMMDD                            

def NBusinessCountFromEndToPay(EndYYYYMMDD, PayYYYYMMDD, Holidays, ModifiedFollowing, ResultEndDate):
    NHolidays = len(Holidays)
    if EndYYYYMMDD < 19000101:
        EndYYYYMMDD = ExcelDateToYYYYMMDD(EndYYYYMMDD)
    if PayYYYYMMDD < 19000101:
        PayYYYYMMDD = ExcelDateToYYYYMMDD(PayYYYYMMDD)
    
    if EndYYYYMMDD > PayYYYYMMDD:
        return -NBusinessCountFromEndToPay(PayYYYYMMDD, EndYYYYMMDD, Holidays, ModifiedFollowing, ResultEndDate)
    elif EndYYYYMMDD == PayYYYYMMDD:
        ResultEndDate[0] = EndYYYYMMDD
        return 0
    
    for i in range(NHolidays):
        if Holidays[i] < 19000101:
            Holidays[i] = ExcelDateToYYYYMMDD(Holidays[i])
    
    nbd = 0
    
    EndYYYY = EndYYYYMMDD // 10000
    EndMM = (EndYYYYMMDD - EndYYYY * 10000) // 100
    EndDD = EndYYYYMMDD % 100
    EndExcelDate = YYYYMMDDToExcelDate(EndYYYYMMDD)
    
    PayYYYY = PayYYYYMMDD // 10000
    PayMM = (PayYYYYMMDD - PayYYYY * 10000) // 100
    PayDD = PayYYYYMMDD % 100
    PayExcelDate = YYYYMMDDToExcelDate(PayYYYYMMDD)
    
    if EndDD == PayDD:
        ResultEndDate[0] = PayYYYYMMDD
        return 0
    else:
        PrevTempMM, PrevTempDD = None, None
        for i in range(30):
            TempExcelDate = PayExcelDate - 1 - i
            TempDate = ExcelDateToYYYYMMDD(TempExcelDate)
            
            TempYYYY = TempDate // 10000
            TempMM = (TempDate - TempYYYY * 10000) // 100
            TempDD = TempDate % 100
            
            MOD7 = TempExcelDate % 7
            IsSaturSundayFlag = 1 if MOD7 in (0, 1) else 0
            IsHolidayFlag = 1 if TempDate in Holidays else 0
            
            if IsSaturSundayFlag == 0 and IsHolidayFlag == 0:
                nbd += 1
            
            if i > 0 and (PrevTempMM > TempMM or (PrevTempMM == 1 and TempMM == 12)):
                if ModifiedFollowing == 1:
                    LastBD = LastBusinessDate(TempYYYY * 100 + TempMM, Holidays)
                    if EndDD > LastBD % 100:
                        EndDD = LastBD % 100
            
            if TempDD == EndDD:
                break
            
            PrevTempMM = TempMM
        
        ResultEndDate[0] = ParseBusinessDateIfHoliday(TempYYYY * 10000 + TempMM * 100 + EndDD, Holidays)
    
    return nbd

def Generate_OptionDate(FirstOptionPayDate, SwapMaturity, NYearBetweenOptionPay, NBDateBetweenOptionFixToPay = 20, MaxNumberOption = -1, ModifiedFollow = 0) :
    OptionPayDateList = [FirstOptionPayDate]
    OptionFixDateList = []
    Holidays = KoreaHolidaysFromStartToEnd(2020, 2070)
    for i in range(1, 100) : 
        NextDate = EDate_YYYYMMDD(OptionPayDateList[0], i*NYearBetweenOptionPay*12)
        AdjDate = ParseBusinessDateIfHoliday(NextDate, Holidays)
        if ModifiedFollow >= 1 : 
            TargetDate = min(AdjDate, LastBusinessDate(NextDate//100, Holidays))
        else : 
            TargetDate = AdjDate
        if NextDate >= SwapMaturity or (i >= MaxNumberOption and MaxNumberOption > 0): 
            break
        else : 
            OptionPayDateList.append(TargetDate)

    if NBDateBetweenOptionFixToPay == 0 : 
        OptionFixDateList = OptionPayDateList
    else : 
        for i in range(len(OptionPayDateList)) : 
            OptionFixDateList.append(NextNthBusinessDate(OptionPayDateList[i], -NBDateBetweenOptionFixToPay,Holidays))
    OptionFixDateList = list(np.array(OptionFixDateList)[np.array(OptionFixDateList) < SwapMaturity])
    OptionPayDateList = list(np.array(OptionPayDateList)[np.array(OptionPayDateList) < SwapMaturity])
    
    return OptionFixDateList, OptionPayDateList

def Number_of_Coupons(
    ProductType,              # 상품종류 0이면 Futures, 1이면 Swap
    PriceDate,                # 평가일
    SwapMat,                  # 스왑 만기
    NumCpnOneYear,            # 연 스왑쿠폰지급수
    HolidayUseFlag,           # 공휴일 입력 사용 Flag
    Holidays,                 # 공휴일 리스트
    ModifiedFollowingFlag
):
    NHolidays = len(Holidays)
    if PriceDate < 19000000:
        PriceDateYYYYMMDD = ExcelDateToYYYYMMDD(PriceDate)
    else:
        PriceDateYYYYMMDD = PriceDate

    if SwapMat < 19000000:
        SwapMat_YYYYMMDD = ExcelDateToYYYYMMDD(SwapMat)
    else:
        SwapMat_YYYYMMDD = SwapMat

    if DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) > 366 * 2:
        ProductType = 1
    if ProductType == 0:
        return 1

    if not (19000101 <= PriceDateYYYYMMDD <= 999990101):
        return -1
    if not (19000101 <= SwapMat_YYYYMMDD <= 999990101):
        return -1
    if NumCpnOneYear > 6:
        return -1

    HolidayYYYYMMDD = [ExcelDateToYYYYMMDD(h) if 0 <= h < 19000000 else h for h in Holidays]

    PriceYYYY = PriceDateYYYYMMDD // 10000
    PriceMM = (PriceDateYYYYMMDD % 10000) // 100
    PriceDD = PriceDateYYYYMMDD % 100

    SwapMatYYYY = SwapMat_YYYYMMDD // 10000
    SwapMatMM = (SwapMat_YYYYMMDD % 10000) // 100
    SwapMatDD = SwapMat_YYYYMMDD % 100

    if DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) <= 62 and NumCpnOneYear < 6:
        return 1
    elif SwapMatYYYY - PriceYYYY <= 1:
        n = 0
        for i in range(24):
            TempYYYYMMDD = EDate_YYYYMMDD(PriceDateYYYYMMDD, i + 1)
            TempYYYY = TempYYYYMMDD // 10000
            TempMM = (TempYYYYMMDD % 10000) // 100
            n = i + 1
            if TempYYYY == SwapMatYYYY and TempMM == SwapMatMM:
                break
        
        if n < 6:
            return 1
        else:
            TempEndList = [0]
            if PriceDD >= 24 and SwapMatDD < 7:
                nbd = NBusinessCountFromEndToPay(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, ModifiedFollowingFlag, TempEndList)
                SwapMat_YYYYMMDD = TempEndList[0]

            CpnDate, firstcpndate = malloc_cpn_date_holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, NumCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)
            return len(CpnDate)
    else:
        StartDateYYYYMMDD = PriceDateYYYYMMDD
        StartYYYYMM = StartDateYYYYMMDD // 100
        StartDD = StartDateYYYYMMDD % 100
        EndYYYYMM = SwapMat_YYYYMMDD // 100
        EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD
        TempEndList = [0]
        if PriceDD >= 24 and SwapMatDD < 7:
            nbd = NBusinessCountFromEndToPay(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, ModifiedFollowingFlag, TempEndList)
            EndDateYYYYMMDD = TempEndList[0]
        
        CpnDate, firstcpndate = malloc_cpn_date_holiday(PriceDateYYYYMMDD, EndDateYYYYMMDD, NumCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)

        return len(CpnDate)

def MappingCouponDates(
    ProductType,               # 상품종류 0이면 Futures, 1이면 Swap
    StartDate,                 # 시작일
    SwapMat,                   # 스왑 만기
    NBDayFromEndDate,          # N영업일 뒤 지급(만약 -1일 경우 EndDate To PayDate 자동 계산)
    NumCpnOneYear,             # 연 스왑쿠폰지급수
    HolidayUseFlag,            # 공휴일 입력 사용 Flag    
    Holidays,                  # Fixing 공휴일
    HolidaysPayDate,           # Payment 공휴일
    ModifiedFollowingFlag) : 
    
    StartDateYYYYMMDD = ExcelDateToYYYYMMDD(StartDate) if (StartDate < 19000000) else StartDate
    SwapMat_YYYYMMDD = ExcelDateToYYYYMMDD(SwapMat) if (SwapMat < 19000000) else SwapMat

    ResultIsExcelType = 0
    if (StartDate < 19000000 and SwapMat < 19000000) :
        ResultIsExcelType = 1

    StartYYYYMM = int(StartDateYYYYMMDD) // 100
    StartDD = StartDateYYYYMMDD - StartYYYYMM * 100
    SwapMat_DD = SwapMat_YYYYMMDD - (int(SwapMat_YYYYMMDD // 100)) * 100

    HolidayYYYYMMDD = [0] * max(1, len(Holidays))
    for i in range(len(Holidays)) : 
        HolidayYYYYMMDD[i] = ExcelDateToYYYYMMDD(Holidays[i]) if (Holidays[i] < 19000000) else Holidays[i]
    
    HolidayYYYYMMDDPayDate = [0] * max(1, len(HolidaysPayDate))
    for i in range(len(Holidays)) : 
        HolidayYYYYMMDDPayDate[i] = ExcelDateToYYYYMMDD(HolidaysPayDate[i]) if (HolidaysPayDate[i] < 19000000) else HolidaysPayDate[i]
    
    NumberCoupon = Number_of_Coupons(ProductType, StartDate, SwapMat, NumCpnOneYear, HolidayUseFlag, Holidays, ModifiedFollowingFlag)
    ResultForwardStart = [-1] * max(1, NumberCoupon)
    ResultForwardEnd = [-1] * max(1, NumberCoupon)
    ResultPayDate = [-1] * max(1, NumberCoupon)
    ResultNBD = [-1] * max(1, NumberCoupon)
    
    if (NumberCoupon < 0) :
        return ResultForwardStart, ResultForwardEnd, ResultPayDate, ResultNBD
    elif (NumberCoupon <= 1) : 
        if (NBDayFromEndDate == 0) :
            if (ResultIsExcelType == 1) : 
                ResultForwardStart[0] = YYYYMMDDToExcelDate(StartDateYYYYMMDD)
                ResultForwardEnd[0] = YYYYMMDDToExcelDate(SwapMat_YYYYMMDD)
                ResultPayDate[0] = ResultForwardEnd[0]
            else :
                ResultForwardStart[0] = StartDateYYYYMMDD
                ResultForwardEnd[0] = SwapMat_YYYYMMDD
                ResultPayDate[0] = ResultForwardEnd[0]
            ResultNBD[0] = NBDayFromEndDate
        elif (NBDayFromEndDate < 0) :
            # NBD Auto계산
            TempEndList = [0]
            NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, ModifiedFollowingFlag, TempEndList)
            EndDateYYYYMMDD = TempEndList[0]
            if (ResultIsExcelType == 1) : 
                ResultForwardStart[0] = YYYYMMDDToExcelDate(StartDateYYYYMMDD)
                ResultForwardEnd[0] = YYYYMMDDToExcelDate(EndDateYYYYMMDD)
                ResultPayDate[0] = YYYYMMDDToExcelDate(SwapMat_YYYYMMDD)
            else : 
                ResultForwardStart[0] = StartDateYYYYMMDD
                ResultForwardEnd[0] = EndDateYYYYMMDD
                ResultPayDate[0] = SwapMat_YYYYMMDD      
            ResultNBD[0] = NBDayFromEndDate  
        else :
            if ((SwapMat_DD < 7 and StartDD >= 24) or NBDayFromEndDate < 0 ):
                ##########################################
                ## If PayDate is next month of EndDate  ##
                ##########################################
                TempEndList = [0]
                NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, ModifiedFollowingFlag, TempEndList)
                EndDateYYYYMMDD = TempEndList[0]
                if (ResultIsExcelType == 1) :
                    ResultForwardStart[0] = YYYYMMDDToExcelDate(StartDateYYYYMMDD)
                    ResultForwardEnd[0] = YYYYMMDDToExcelDate(EndDateYYYYMMDD)
                    ResultPayDate[0] = YYYYMMDDToExcelDate(SwapMat_YYYYMMDD)
                else :
                    ResultForwardStart[0] = StartDateYYYYMMDD
                    ResultForwardEnd[0] = EndDateYYYYMMDD
                    ResultPayDate[0] = SwapMat_YYYYMMDD
                ResultNBD[0] = NBDayFromEndDate
            else : 
                n = 0
                ResultForwardStart[0] = StartDate if (ResultIsExcelType == 1) else StartDateYYYYMMDD
                ResultNBD[0] = NBDayFromEndDate
                # PayDate결정
                PayDateYYYYMMDD = SwapMat_YYYYMMDD
                PayDateExcelType = YYYYMMDDToExcelDate(PayDateYYYYMMDD)
                MOD7 = PayDateExcelType % 7
                for i in range(1, 35) : 
                    if (MOD7 in [0,1]) or (PayDateYYYYMMDD in HolidayYYYYMMDDPayDate) : 
                        # 휴일이면 n+=1
                        PayDateExcelType += 1
                        PayDateYYYYMMDD = ExcelDateToYYYYMMDD(PayDateExcelType)
                    else :
                        break

                ResultPayDate[0] = PayDateExcelType if (ResultIsExcelType == 1) else PayDateYYYYMMDD

                EndDateYYYYMMDD = PayDateYYYYMMDD
                EndDateExcel = PayDateExcelType
                for i in range(1, 35) : 
                    EndDateExcel = EndDateExcel - 1
                    EndDateYYYYMMDD = ExcelDateToYYYYMMDD(EndDateExcel)
                    MOD7 = EndDateExcel % 7
                    if ((MOD7 not in [0, 1]) and (EndDateYYYYMMDD not in HolidayYYYYMMDDPayDate)) : 
                        # 영업일이면 n+=1
                        n += 1

                    if (n == NBDayFromEndDate) :
                        ResultForwardEnd[0] = EndDateExcel if (ResultIsExcelType == 1) else EndDateYYYYMMDD
                        break
    else :
        TempYYYYMMDD = StartDateYYYYMMDD
        EndYYYYMM = (int)(SwapMat_YYYYMMDD // 100)
        TempEndList = [0]
        if ( (SwapMat_DD < 7 and StartDD >= 24) or NBDayFromEndDate < 0 ): 
            ##########################################
            ## If PayDate is next month of EndDate  ##
            ##########################################
            NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, ModifiedFollowingFlag, TempEndList)
            EndDateYYYYMMDD = TempEndList[0]                
        else :
            EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD

        CpnDate, firstcpndate = malloc_cpn_date_holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, NumCpnOneYear, HolidayYYYYMMDD if HolidayUseFlag > 0 else [], ModifiedFollowingFlag)
        for i in range(min(NumberCoupon, len(CpnDate))) :
            if (i == 0) : 
                if (ResultIsExcelType == 1) :
                    ResultForwardStart[0] = YYYYMMDDToExcelDate(StartDateYYYYMMDD)
                    TempDateExcelType = YYYYMMDDToExcelDate(CpnDate[0])
                    ResultForwardEnd[0] = TempDateExcelType
                else :
                    ResultForwardStart[0] = StartDateYYYYMMDD
                    ResultForwardEnd[0] = CpnDate[0]
            else :
                if (ResultIsExcelType == 1) :
                    ResultForwardStart[i] = YYYYMMDDToExcelDate(CpnDate[i - 1])
                    TempDateExcelType = YYYYMMDDToExcelDate(CpnDate[i])
                    ResultForwardEnd[i] = TempDateExcelType
                else :
                    ResultForwardStart[i] = CpnDate[i - 1]
                    ResultForwardEnd[i] = CpnDate[i]
            ResultNBD[i] = NBDayFromEndDate
            if (NBDayFromEndDate == 0) : 
                ResultPayDate[i] = ResultForwardEnd[i]
            else : 
                n = 0
                for j in range(1, 35) : 
                    PayDateYYYYMMDD = DayPlus(CpnDate[i], j)
                    PayDateExcelType = YYYYMMDDToExcelDate(PayDateYYYYMMDD)
                    MOD7 = PayDateExcelType % 7
                    if ((MOD7 not in [0, 1]) and (PayDateYYYYMMDD not in HolidayYYYYMMDDPayDate)) : 
                        # 영업일이면 n+=1
                        n += 1

                    if (n == NBDayFromEndDate) :
                        ResultPayDate[i] = PayDateExcelType if (ResultIsExcelType == 1) else PayDateYYYYMMDD                        
                        break
    return ResultForwardStart, ResultForwardEnd, ResultPayDate, ResultNBD                    

def MapProductType(ProductType, DomesticEstCurveRate = [], USDEstCurveRate = []) : 
    x = str(ProductType).lower()
    if 'dp' in x or 'dg' in x : 
        return 0
    elif 'sp' in x or 'swappoint' in x: 
        return 2
    elif 'sw' in x : 
        return 1
    elif 'bs' in x : 
        return 3 
    elif len(DomesticEstCurveRate) > 0 and len(USDEstCurveRate) > 0 : 
        return 4 
    else : 
        return 5
    
def CalcZeroRateFromSwapPoint(rf, T, S, SwapPoint, SwapPointUnit) : 
    F = S + SwapPoint /SwapPointUnit
    rd = rf + 1.0 / T * np.log(F / S)
    return rd

def Calc_ZeroRate_FromDiscFactor(PriceDate, StartDate, EndDate, MarketQuote, DayCountFlag, ZeroTerm, ZeroRate) : 
    if (StartDate < 19000101) : 
        StartDate = ExcelDateToYYYYMMDD(StartDate)
    if (EndDate < 19000101) : 
        EndDate = ExcelDateToYYYYMMDD(EndDate)
    
    if (PriceDate == StartDate) : 
        r = 365/(DayCountAtoB(StartDate, EndDate)) * np.log(1.0 + MarketQuote * DayCountFractionAtoB(StartDate, EndDate, DayCountFlag))
    else : 
        t0 = DayCountAtoB(PriceDate, StartDate)/365
        DF_Start_To_EndDate = 1.0/(1.0 + MarketQuote * DayCountFractionAtoB(StartDate, EndDate, DayCountFlag))
        r0 = Linterp(ZeroTerm, ZeroRate, t0)
        DF_0_To_EndDate = np.exp(-r0 * t0) * DF_Start_To_EndDate
        r = -365.0/(DayCountAtoB(PriceDate, EndDate)) * np.log(DF_0_To_EndDate)
    return r

def MonthStringConvert(x) : 
    if len(str(x)) == 9 and '-' in str(x): 
        XX = str(x).lower()
        DD = XX[:2]
        YYYY = ('20' + XX[-2:])[-4:]
        if '-jan-' in XX : 
            return int(YYYY + '01' + DD)
        elif '-feb-' in XX : 
            return int(YYYY + '02' + DD)
        elif '-mar-' in XX : 
            return int(YYYY + '03' + DD)
        elif '-apr-' in XX : 
            return int(YYYY + '04' + DD)
        elif '-may-' in XX : 
            return int(YYYY + '05' + DD)
        elif '-jun-' in XX : 
            return int(YYYY + '06' + DD)
        elif '-jul-' in XX : 
            return int(YYYY + '07' + DD)
        elif '-aug-' in XX : 
            return int(YYYY + '08' + DD)
        elif '-sep-' in XX : 
            return int(YYYY + '09' + DD)
        elif '-oct-' in XX : 
            return int(YYYY + '10' + DD)
        elif '-nov-' in XX : 
            return int(YYYY + '11' + DD)
        elif '-dec-' in XX : 
            return int(YYYY + '12' + DD)
        else : 
            return x    
    else : 
        return x    

def ReadCSV(filedir, ParseMonthStringToInteger = False) :    
    try : 
        chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python')
    except UnicodeDecodeError : 
        try : 
            chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python', encoding = 'cp949')
        except UnicodeDecodeError : 
            chunk_list = pd.read_csv(filedir, chunksize = 5000, engine = 'python', encoding = 'utf-8')            
    
    df = pd.DataFrame()
    for i in chunk_list : 
        df = pd.concat([df,i],axis = 0)
    if ParseMonthStringToInteger == True : 
        return df.applymap(MonthStringConvert)
    else : 
        return df

if __name__ == "__main__" : 
    print("######################################\nCreated By Daesun Lim (CIIA(R), FRM(R))\nRisk Validation Quant\nMy FRTB Module \n"+vers+" (RecentUpdated :" +recentupdate + ")" + "\n######################################\n")
