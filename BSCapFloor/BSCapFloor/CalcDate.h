// 임대선 제작
// 하드코드1 = 음력 관련 연도별 하드코드 2043년까지 해놓음(이후 수정요망)
// 하드코드2 = 임시공휴일

#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#ifndef DLLEXPORT(A)
#ifdef WIN32
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A _stdcall
#elif _WIN64
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A _stdcall
#elif __linux__
#define DLLEXPORT(A) extern "C" A
#elif __hpux
#define DLLEXPORT(A) extern "C" A
#elif __unix__
#define DLLEXPORT(A) extern "C" A
#else
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A _stdcall
#endif
#endif 

#define DateFunction                   1
#define LunarDateKoreanHardCodeYear  2043
DLLEXPORT(long) CDateToExcelDate(long Cdate);               // YYYYMMDD -> ExcelDate
DLLEXPORT(long) ExcelDateToCDate(long ExlDate);             // ExcelDate -> YYYYMMDD
DLLEXPORT(long) DayCountAtoB(long Day1, long Day2);         // Day Count YYYYMMDD1 to YYYYMMDD2
DLLEXPORT(long) DayPlus(long Cdate, long NDays);            // Day Plus YYYYMMDD, NDay

#ifndef max
#define max(a,b)            (((a) > (b)) ? (a) : (b))
#endif

#ifndef min
#define min(a,b)            (((a) < (b)) ? (a) : (b))
#endif


#define N_Info_Array  203

long _info_array_raw[N_Info_Array * 12] = {
    // 한국 음력 관련 하드코딩
    // 1: 평달29
    // 2: 평달30
    // 3: 평달29 윤달29
    // 4: 평달29 윤달30
    // 5: 평달30 윤달29
    // 6: 평달30 윤달30
    
    // 1841
    1, 2, 4, 1, 1, 2,   1, 2, 1, 2, 2, 1,
    2, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 1,
    2, 2, 2, 1, 2, 1,   4, 1, 2, 1, 2, 1,
    2, 2, 1, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 2, 1,   2, 1, 2, 1, 2, 1,
    2, 1, 2, 1, 5, 2,   1, 2, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 3, 2, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,

    // 1851
    2, 2, 1, 2, 1, 1,   2, 1, 2, 1, 5, 2,
    2, 1, 2, 2, 1, 1,   2, 1, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   5, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 2,   1, 2, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 5, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,
    2, 1, 6, 1, 1, 2,   1, 1, 2, 1, 2, 2,

    // 1861
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 1, 2,
    2, 1, 2, 1, 2, 2,   1, 2, 2, 3, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 4, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 2, 1, 2, 2, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,
    1, 2, 2, 3, 2, 1,   1, 2, 1, 2, 2, 1,
    2, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 2, 1, 2, 1,   2, 1, 1, 5, 2, 1,

    // 1871
    2, 2, 1, 2, 2, 1,   2, 1, 2, 1, 1, 2,
    1, 2, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    1, 1, 2, 1, 2, 4,   2, 1, 2, 2, 1, 2,
    1, 1, 2, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,
    2, 2, 1, 1, 5, 1,   2, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 4, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 1, 2,

    // 1881
    1, 2, 1, 2, 1, 2,   5, 2, 2, 1, 2, 1,
    1, 2, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,
    2, 1, 1, 2, 3, 2,   1, 2, 2, 1, 2, 2,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 5, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 5, 2, 1, 2, 2,   1, 2, 1, 2, 1, 2,

    // 1891
    1, 2, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 5,   2, 2, 1, 2, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 5, 1,   2, 1, 2, 1, 2, 1,
    2, 2, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,
    2, 1, 5, 2, 2, 1,   2, 1, 2, 1, 2, 1,
    2, 1, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 5, 2, 2, 1, 2,

    // 1901
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 3, 2,   1, 1, 2, 2, 1, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 2, 1, 2,
    1, 2, 2, 4, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 1, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    1, 5, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,

    //1911
    2, 1, 2, 1, 1, 5,   1, 2, 2, 1, 2, 2,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,
    2, 2, 1, 2, 5, 1,   2, 1, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 3, 2, 1, 2, 2,   1, 2, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   5, 2, 2, 1, 2, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,

    //1921
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,
    2, 1, 2, 2, 3, 2,   1, 1, 2, 1, 2, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 1, 2,
    2, 1, 2, 1, 2, 2,   1, 2, 1, 2, 1, 1,
    2, 1, 2, 5, 2, 1,   2, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 5, 1, 2, 1, 1,   2, 2, 1, 2, 2, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,
    1, 2, 2, 1, 1, 5,   1, 2, 1, 2, 2, 1,

    //1931
    2, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,
    1, 2, 2, 1, 6, 1,   2, 1, 2, 1, 1, 2,
    1, 2, 1, 2, 2, 1,   2, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 4, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,
    2, 2, 1, 1, 2, 1,   4, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,

    //1941
    2, 2, 1, 2, 2, 4,   1, 1, 2, 1, 2, 1,
    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,
    1, 1, 2, 4, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 1, 2,
    2, 5, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 2, 1, 2,   3, 2, 1, 2, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,

    //1951
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 4, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 1, 2, 2,   1, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 1, 2, 2,
    2, 1, 4, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 5, 2, 1, 2, 2,
    1, 2, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,
    2, 1, 2, 1, 2, 5,   2, 1, 2, 1, 2, 1,

    //1961
    2, 1, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 2, 3, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 5, 2, 1, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 1,   5, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 1, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,

    //1971
    1, 2, 1, 1, 5, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 2, 1,
    2, 2, 1, 5, 1, 2,   1, 1, 2, 2, 1, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,
    2, 2, 1, 2, 1, 2,   1, 5, 2, 1, 1, 2,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 1,
    2, 2, 1, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 6,   1, 2, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,

    //1981
    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2,
    2, 1, 2, 3, 2, 1,   1, 2, 2, 1, 2, 2,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,
    2, 1, 2, 2, 1, 1,   2, 1, 1, 5, 2, 2,
    1, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 2,   1, 2, 1, 2, 1, 1,
    2, 1, 2, 2, 1, 5,   2, 2, 1, 2, 1, 2,
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 2, 1, 1, 5, 1,   2, 1, 2, 2, 2, 2,

    //1991
    1, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 2,
    1, 2, 2, 1, 1, 2,   1, 1, 2, 1, 2, 2,
    1, 2, 5, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 2, 1, 2, 1,   2, 1, 1, 2, 1, 2,
    1, 2, 2, 1, 2, 2,   1, 5, 2, 1, 1, 2,
    1, 2, 1, 2, 2, 1,   2, 1, 2, 2, 1, 2,
    1, 1, 2, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 1, 2, 3, 2,   2, 1, 2, 2, 2, 1,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 2, 1,
    2, 2, 1, 1, 2, 1,   1, 2, 1, 2, 2, 1,

    //2001
    2, 2, 2, 3, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 2, 1, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 2, 1, 2, 2, 1,   2, 1, 1, 2, 1, 2,
    1, 5, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   2, 1, 2, 2, 1, 1,
    2, 1, 2, 1, 2, 1,   5, 2, 2, 1, 2, 2,
    1, 1, 2, 1, 1, 2,   1, 2, 2, 2, 1, 2,
    2, 1, 1, 2, 1, 1,   2, 1, 2, 2, 1, 2,
    2, 2, 1, 1, 5, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,

    //2011
    2, 1, 2, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 1, 6, 2, 1, 2,   1, 1, 2, 1, 2, 1,
    2, 1, 2, 2, 1, 2,   1, 2, 1, 2, 1, 2,
    1, 2, 1, 2, 1, 2,   1, 2, 5, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 2, 2, 1, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 2, 2, 1, 2, 2,
    1, 2, 1, 2, 3, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 2, 1, 2, 2,
    2, 1, 2, 1, 2, 1,   1, 2, 1, 2, 1, 2,
    2, 1, 2, 5, 2, 1,   1, 2, 1, 2, 1, 2,

    // 2021
    1, 2, 2, 1, 2, 1,   2, 1, 2, 1, 2, 1,
    2, 1, 2, 1, 2, 2,   1, 2, 1, 2, 1, 2,
    1, 5, 2, 1, 2, 1,   2, 2, 1, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 2, 1, 2, 2, 1,
    2, 1, 2, 1, 1, 5,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 2, 1, 2, 2, 2,
    1, 2, 1, 2, 1, 1,   2, 1, 1, 2, 2, 2,
    1, 2, 2, 1, 5, 1,   2, 1, 1, 2, 2, 1,
    2, 2, 1, 2, 2, 1,   1, 2, 1, 1, 2, 2,
    1, 2, 1, 2, 2, 1,   2, 1, 2, 1, 2, 1,

    // 2031
    2, 1, 5, 2, 1, 2,   2, 1, 2, 1, 2, 1,
    2, 1, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 5, 2,
    1, 2, 1, 1, 2, 1,   2, 1, 2, 2, 2, 1,
    2, 1, 2, 1, 1, 2,   1, 1, 2, 2, 1, 2,
    2, 2, 1, 2, 1, 4,   1, 1, 2, 1, 2, 2,
    2, 2, 1, 2, 1, 1,   2, 1, 1, 2, 1, 2,
    2, 2, 1, 2, 1, 2,   1, 2, 1, 1, 2, 1,
    2, 2, 1, 2, 5, 2,   1, 2, 1, 2, 1, 1,
    2, 1, 2, 2, 1, 2,   2, 1, 2, 1, 2, 1,

    //2041
    2, 1, 1, 2, 1, 2,   2, 1, 2, 2, 1, 2,
    1, 5, 1, 2, 1, 2,   1, 2, 2, 2, 1, 2,
    1, 2, 1, 1, 2, 1,   1, 2, 2, 1, 2, 2
};

// 윤년Check
long LeapCheck(long Year)
{
    if ((Year % 4 == 0 && Year % 100 != 0) || Year % 400 == 0)
        return 1;
    else
        return 0;
}

// 20210627을 엑셀타입 2021-06-27(44374)로 바꿔줌
DLLEXPORT(long) CDateToExcelDate(long Cdate)
{
    long Days[12] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    long CummulativeDays[13] = { 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365 };
    long Leap = 0;

    long Year = (long)Cdate / 10000;
    long Month = (long)(Cdate - Year * 10000) / 100;
    long Day = (long)(Cdate - Year * 10000 - Month * 100);

    Leap = LeapCheck(Year);
    if (Year == 1900) Leap = 1;

    long N4 = (long)Year / 4;
    long N100 = (long)Year / 100;
    long N400 = (long)Year / 400;

    long N4_To_1900 = 1900 / 4;
    long N100_To_1900 = 1900 / 100;
    long N400_To_1900 = 1900 / 400;

    long Result;

    if (Leap == 1)
    {
        if (Month > 2)
            Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays[Month - 1] + 1 + Day;
        else
            Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays[Month - 1] + Day;
    }

    else
    {
        Result = (Year - 1900) * 365 + (N4 - N4_To_1900) - (N100 - N100_To_1900) + (N400 - N400_To_1900) + CummulativeDays[Month - 1] + 1 + Day;
    }

    return Result;
}


// 엑셀타입 2021-06-27(44374)을 20210627으로 바꿔줌
DLLEXPORT(long) ExcelDateToCDate(long ExlDate)
{
    long i, m;

    long CummulativeDays[13] = { 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365 };
    long CummulativeDays_Leap[13] = { 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366 };

    // xx00년도부터 xx99년도까지 Day수(xx는 4의 배수)
    long LeapDaysFor4Year[101] = { 0, 366, 731, 1096, 1461, 1827, 2192, 2557, 2922, 3288,
                                   3653, 4018, 4383, 4749, 5114, 5479, 5844, 6210, 6575, 6940,
                                   7305, 7671, 8036, 8401, 8766, 9132, 9497, 9862, 10227, 10593,
                                   10958, 11323, 11688, 12054, 12419, 12784, 13149, 13515, 13880, 14245,
                                   14610, 14976, 15341, 15706, 16071, 16437, 16802, 17167, 17532, 17898,
                                   18263, 18628, 18993, 19359, 19724, 20089, 20454, 20820, 21185, 21550,
                                   21915, 22281, 22646, 23011, 23376, 23742, 24107, 24472, 24837, 25203,
                                   25568, 25933, 26298, 26664, 27029, 27394, 27759, 28125, 28490, 28855,
                                   29220, 29586, 29951, 30316, 30681, 31047, 31412, 31777, 32142, 32508,
                                   32873, 33238, 33603, 33969, 34334, 34699, 35064, 35430, 35795, 36160, 36525 };

    // xx00년도부터 xx99년도까지 Day수(xx는 4의 배수가 아님)
    long LeapDaysFor4YearNot400[101] = { 0,365, 730, 1095, 1460, 1826, 2191, 2556, 2921, 3287,
                                         3652, 4017, 4382, 4748, 5113, 5478, 5843, 6209, 6574, 6939,
                                         7304, 7670, 8035, 8400, 8765, 9131, 9496, 9861, 10226, 10592,
                                         10957, 11322, 11687, 12053, 12418, 12783, 13148, 13514, 13879, 14244,
                                         14609, 14975, 15340, 15705, 16070, 16436, 16801, 17166, 17531, 17897,
                                         18262, 18627, 18992, 19358, 19723, 20088, 20453, 20819, 21184, 21549,
                                         21914, 22280, 22645, 23010, 23375, 23741, 24106, 24471, 24836, 25202,
                                         25567, 25932, 26297, 26663, 27028, 27393, 27758, 28124, 28489, 28854,
                                         29219, 29585, 29950, 30315, 30680, 31046, 31411, 31776, 32141, 32507,
                                         32872, 33237, 33602, 33968, 34333, 34698, 35063, 35429, 35794, 36159, 36524 };

    // 1900~1999.12.31까지의 Day 개수 36525(엑셀기준)
    long ExcelDate;
    long Year, Month, Day;

    if (ExlDate - 36525 > 0)
    {
        ExcelDate = ExlDate - 36525;
        Year = 2000;
    }

    else
    {
        ExcelDate = ExlDate;
        Year = 1900;
    }

    //400년동안 윤년 개수
    //long nLeap_for_400 = 400 / 4 - 400 / 100 + 1;
    //long nDay_for_400 = 365 * 400 + nLeap_for_400;
    long nDay_for_400 = 146097;

    for (i = 0; i < 1000; i++)
    {
        if (ExcelDate - nDay_for_400 <= 0) break;
        else
        {
            ExcelDate -= nDay_for_400;
            Year += 400;
        }
    }
    //400년의 배수만큼 날짜 차감 완료

    //100년동안 윤년 개수
    long nDay_for_100_400x = 36525;       //400의 배수 년도에는36525
    long nDay_for_100 = 36524;            //나머지 3년동안은 36524

    for (i = 0; i < 5; i++)
    {
        if (i % 4 == 0)
        {
            if (ExcelDate - nDay_for_100_400x <= 0) break;
            else
            {
                ExcelDate -= nDay_for_100_400x;
                Year += 100;
            }
        }
        else
        {
            if (ExcelDate - nDay_for_100 <= 0) break;
            else
            {
                ExcelDate -= nDay_for_100;
                Year += 100;
            }
        }
    }
    // 100년의 배수만큼 날짜 차감 완료

    long Flag_400;
    long Leap;

    // 이쯤에서 남은 날짜가 0인지 체크
    if (ExcelDate == 0)
    {
        Year -= 1;
        return Year * 10000 + 1231;
    }
    else
    {
        //위에서 년도 100의자리 체크할 때 사용했던 i를 사용
        //년도 백의자리가 4의 배수인지 아닌지 체크 (16xx년 일 경우 해당 100년동안은 36525일)
        Flag_400 = 0;
        if (i % 4 == 0)
        {
            Flag_400 = 1;
        }

        if (Flag_400 == 1)
        {
            for (i = 0; i < 101; i++)
            {
                if (ExcelDate - LeapDaysFor4Year[i + 1] <= 0)
                {
                    ExcelDate = ExcelDate - LeapDaysFor4Year[i];
                    Year += i;
                    break;
                }
            }
        }
        else
        {
            for (i = 0; i < 101; i++)
            {
                if (ExcelDate - LeapDaysFor4YearNot400[i + 1] <= 0)
                {
                    ExcelDate = ExcelDate - LeapDaysFor4YearNot400[i];
                    Year += i;
                    break;
                }
            }
        }

        // 이쯤에서 남은 날짜가 0인지 한번 더 체크
        if (ExcelDate == 0)
        {
            Year -= 1;
            return Year * 10000 + 1231;
        }

        Leap = 0;
        Leap = LeapCheck(Year);
        if (Year == 1900) Leap = 1;

        if (Leap == 1)
        {
            for (m = 0; m < 12; m++)
            {
                if (CummulativeDays_Leap[m + 1] >= ExcelDate && CummulativeDays_Leap[m] < ExcelDate) break;
            }
            if (m < 12) Month = m + 1;
            else Month = 12;
            Day = ExcelDate - CummulativeDays_Leap[m];
        }
        else
        {
            for (m = 0; m < 12; m++)
            {
                if (CummulativeDays[m + 1] >= ExcelDate && CummulativeDays[m] < ExcelDate) break;
            }

            if (m < 12) Month = m + 1;
            else Month = 12;

            Day = ExcelDate - CummulativeDays[m];
        }
        return Year * 10000 + Month * 100 + Day;
    }
}

DLLEXPORT(long) DayCountAtoB(long Day1, long Day2)
{
    return CDateToExcelDate(Day2) - CDateToExcelDate(Day1);
}

DLLEXPORT(long) DayPlus(long Cdate, long NDays)
{
    /////////////////////////////////////////
    // Cdate -> YYYYMMDD Format            //
    // NDays -> 1, 2,                      //
    // example :                           //
    //     DayPlus(20240627, 1) = 20240628 //
    /////////////////////////////////////////
    long i;
    long Days[13] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ,31 };
    long Days_Leap[13] = { 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ,31 };
    long CummulativeDays[14] = { 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365 ,396 };
    long CummulativeDays_Leap[14] = { 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366,397 };
    long Leap = 0;

    long Year = (long)Cdate / 10000;
    long Month = (long)(Cdate - Year * 10000) / 100;
    long Day = (long)(Cdate - Year * 10000 - Month * 100);
    long EndFlag = 1;
    long NewMonth;
    long NewDay;

    //0보다 작을 때는 귀찮으니 기존 Function 사용하자
    if (NDays < 0) return ExcelDateToCDate(CDateToExcelDate(Cdate) + NDays);
    else if (NDays == 0) return Cdate;

    Leap = LeapCheck(Year);
    if (Year == 1900) Leap = 1;

    long LeftDaysofMonth;
    if (Leap == 1) LeftDaysofMonth = Days_Leap[Month - 1] - Day;
    else LeftDaysofMonth = Days[Month - 1] - Day;

    long NDatesOfYearToday;
    long NDayCountFromJan01;
    if (NDays <= LeftDaysofMonth)
    {
        return Year * 10000 + Month * 100 + (Day + NDays);
    }
    else
    {
        //당해 중 지금까지 날짜 개수
        if (Leap == 1) // 만약 해당 날짜가 윤년이라면
        {
            NDatesOfYearToday = CummulativeDays_Leap[Month - 1] + Day;
            NDayCountFromJan01 = NDatesOfYearToday + NDays;
            if (NDayCountFromJan01 <= 366)
            {
                for (i = 0; i < 13; i++)
                {
                    if (NDayCountFromJan01 > CummulativeDays_Leap[i] && NDayCountFromJan01 < CummulativeDays_Leap[i + 1])
                    {
                        NewMonth = i + 1;
                        NewDay = NDayCountFromJan01 - CummulativeDays_Leap[i];
                        break;
                    }
                    else if (NDayCountFromJan01 == CummulativeDays_Leap[i])
                    {
                        NewMonth = i;
                        NewDay = Days_Leap[NewMonth - 1];
                        break;
                    }
                }
                return Year * 10000 + NewMonth * 100 + NewDay;
            }
            else if (NDayCountFromJan01 == 366)
            {
                return Year * 10000 + 1231;
            }
            else
            {
                Year += 1;
                return DayPlus(Year * 10000 + 1 * 100 + 1, NDayCountFromJan01 - 366 - 1);
            }
        }
        else
        {
            NDatesOfYearToday = CummulativeDays[Month - 1] + Day;
            NDayCountFromJan01 = NDatesOfYearToday + NDays;
            if (NDayCountFromJan01 <= 365)
            {
                for (i = 0; i < 13; i++)
                {
                    if (NDayCountFromJan01 > CummulativeDays[i] && NDayCountFromJan01 < CummulativeDays[i + 1])
                    {
                        NewMonth = i + 1;
                        NewDay = NDayCountFromJan01 - CummulativeDays[i];
                        break;
                    }
                    else if (NDayCountFromJan01 == CummulativeDays[i])
                    {
                        NewMonth = i;
                        NewDay = Days[NewMonth - 1];
                        break;
                    }
                }
                return Year * 10000 + NewMonth * 100 + NewDay;
            }
            else if (NDayCountFromJan01 == 365)
            {
                return Year * 10000 + 1231;
            }
            else
            {
                Year += 1;
                return DayPlus(Year * 10000 + 1 * 100 + 1, NDayCountFromJan01 - 365 - 1);
            }
        }
    }
}

DLLEXPORT(long) EDate_Cpp(long Cdate, long NMonths)
{
    long Days[13] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ,31 };
    long Days_Leap[13] = { 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ,31 };
    long CummulativeDays[14] = { 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365 ,396 };
    long CummulativeDays_Leap[14] = { 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366,397 };
    long Leap = 0;

    long Year = (long)Cdate / 10000;
    long Month = (long)(Cdate - Year * 10000) / 100;
    long Day = (long)(Cdate - Year * 10000 - Month * 100);

    long TargetMonth = Month + NMonths;
    long PlusYear;
    long ResultMonth;
    long ResultDay;

    if (TargetMonth > 12)
    {
        PlusYear = (long)(TargetMonth / 12);
        ResultMonth = TargetMonth % 12;
        Leap = LeapCheck(Year + PlusYear);
        if (Leap == 1)
        {
            if (ResultMonth == 0) ResultDay = min(Day, Days_Leap[11]);
            else ResultDay = min(Day, Days_Leap[ResultMonth - 1]);
        }
        else
        {
            if (ResultMonth == 0) ResultDay = min(Day, Days[11]);
            else ResultDay = min(Day, Days[ResultMonth - 1]);
        }
        if (TargetMonth % 12 != 0)
            return (Year + PlusYear) * 10000 + ResultMonth * 100 + ResultDay;
        else
            return (Year + PlusYear - 1) * 10000 + 12 * 100 + ResultDay;
    }
    else if (TargetMonth > 0)
    {
        ResultMonth = TargetMonth;
        Leap = LeapCheck(Year);
        if (Leap == 1)
        {
            ResultDay = min(Day, Days_Leap[ResultMonth - 1]);

        }
        else
        {
            ResultDay = min(Day, Days[ResultMonth - 1]);
        }
        return Year * 10000 + ResultMonth * 100 + ResultDay;
    }
    else
    {
        PlusYear = (long)(TargetMonth / 12 - 1);
        ResultMonth = (12 + TargetMonth % 12);
        Leap = LeapCheck(Year + PlusYear);
        if (Leap == 1)
        {
            ResultDay = min(Day, Days_Leap[ResultMonth - 1]);

        }
        else
        {
            ResultDay = min(Day, Days[ResultMonth - 1]);
        }
        return (Year + PlusYear) * 10000 + ResultMonth * 100 + ResultDay;
    }
}

long LastBusinessDate(long YYYYMM, long NHoliday, long* HolidayYYYYMMDD)
{
    long i, j;
    long YYYY = (long)(YYYYMM / 100);
    long MM = (long)(YYYYMM - YYYY * 100);

    long Leap = 0;
    if ((YYYY % 4 == 0 && YYYY % 100 != 0) || YYYY % 400 == 0) Leap = 1;
    else Leap = 0;
    long LastYYYYMMDD = YYYY * 10000 + MM * 100 + 1;
    if ((MM == 1) || (MM == 3) || (MM == 5) || (MM == 7) || (MM == 8) || (MM == 10) || (MM == 12))
    {
        // YYYYMM31
        LastYYYYMMDD = YYYY * 10000 + MM * 100 + 31;
    }
    else if ((MM == 4) || (MM == 6) || (MM == 9) || (MM == 11))
    {
        // YYYYMM31
        LastYYYYMMDD = YYYY * 10000 + MM * 100 + 30;
    }
    else
    {
        if (Leap == 1)
        {
            // YYYY0229
            LastYYYYMMDD = YYYY * 10000 + MM * 100 + 29;
        }
        else
        {
            // YYYY0228
            LastYYYYMMDD = YYYY * 10000 + MM * 100 + 28;
        }
    }
    long LastExcelDate = CDateToExcelDate(LastYYYYMMDD);
    long MOD07 = LastExcelDate % 7;
    long SaturSundayFlag = 0;
    long HolidayFlag = 0;
    long TempExcelDate = LastExcelDate;
    long TempYYYYMMDD = LastYYYYMMDD;

    if (MOD07 == 1 || MOD07 == 0) SaturSundayFlag = 1;

    for (i = 0; i < NHoliday; i++)
    {
        if (LastYYYYMMDD == HolidayYYYYMMDD[i])
        {
            HolidayFlag = 1;
            break;
        }
    }

    if (SaturSundayFlag == 0 && HolidayFlag == 0)
    {
        return LastYYYYMMDD;
    }
    else
    {
        for (i = 1; i < 31; i++)
        {
            TempExcelDate = LastExcelDate - i;
            TempYYYYMMDD = ExcelDateToCDate(TempExcelDate);
            MOD07 = TempExcelDate % 7;

            if (MOD07 == 1 || MOD07 == 0) SaturSundayFlag = 1;
            else SaturSundayFlag = 0;

            HolidayFlag = 0;
            for (j = 0; j < NHoliday; j++)
            {
                if (TempYYYYMMDD == HolidayYYYYMMDD[j])
                {
                    HolidayFlag = 1;
                    break;
                }
            }

            if (SaturSundayFlag == 0 && HolidayFlag == 0)
            {
                break;
            }
        }
        return TempYYYYMMDD;
    }
}

void febdays(long y, long* _info_month)
{
    _info_month[1] = 28;
    if ((y % 4 == 0 && y % 100 != 0) || y % 400 == 0) _info_month[1] = 29;
}

long CalcSolarToLunar(long YYYYMMDD, long* ResultArray3, long* _info_array_raw)
{
    long i, j;
    long** _info_array = (long**)malloc(sizeof(long*) * N_Info_Array);
    for (i = 0; i < N_Info_Array; i++) _info_array[i] = _info_array_raw + i * 12;

    long _info_month[12] = { 31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    long Year = YYYYMMDD / 10000;
    long Month = (YYYYMMDD - Year * 10000) / 100;
    long Day = (YYYYMMDD - Year * 10000 - Month * 100);

    if (Year < 1841 || 2043 < Year) return -99999999;
    if (Month < 1 || 12 < Month) return -99999999;

    febdays(Year, _info_month);

    long ly, lm, ld;
    long m1, m2, mm, w;
    long sy = Year;
    long sm = Month;
    long sd = Day;
    long td, td1, td2;
    long dt[N_Info_Array], k1, k2;
    long Yoon = 0;

    td1 = (1840 * 365 + 1840 / 4 - 1840 / 100 + 1840 / 400 + 23);
    td2 = ((sy - 1) * 365 + (sy - 1) / 4 - (sy - 1) / 100 + (sy - 1) / 400 + sd);

    for (i = 0; i < sm - 1; i++) td2 += _info_month[i];
    td = td2 - td1 + 1;

    for (i = 0; i <= sy - 1841; i++)
    {
        dt[i] = 0;
        for (j = 0; j < 12; j++)
        {
            if (_info_array[i][j] == 1) mm = 29;        // 평달29
            else if (_info_array[i][j] == 2) mm = 30;   // 평달30
            else if (_info_array[i][j] == 3) mm = 58;   // 평달29윤달29
            else if (_info_array[i][j] == 4) mm = 59;   // 평달29윤달30
            else if (_info_array[i][j] == 5) mm = 59;   // 평달30윤달29
            else if (_info_array[i][j] == 6) mm = 60;   // 평달30윤달30
            else return -99999999;
        }
        dt[i] += mm;
    }
    ly = 0;
    while (1)
    {
        if (td > dt[ly])
        {
            td -= dt[ly];
            ly++;
        }
        else break;
    }
    lm = 0;
    while (1)
    {
        if (_info_array[ly][lm] <= 2)
        {
            mm = _info_array[ly][lm] + 28;
            if (td > mm)
            {
                td -= mm;
                lm += 1;
            }
            else break;
        }
        else
        {
            if (_info_array[ly][lm] == 3)
            {
                m1 = 29;                // 평달 29
                m2 = 29;                // 윤달 29
            }
            else if (_info_array[ly][lm] == 4) {
                m1 = 29;                // 평달29
                m2 = 30;                // 윤달30
            }
            else if (_info_array[ly][lm] == 5) {
                m1 = 30;                // 평달30
                m2 = 29;                // 윤달29
            }
            else if (_info_array[ly][lm] == 6) {
                m1 = 30;                // 평달30
                m2 = 30;                // 윤달30
            }
            else return -99999999;

            if (td > m1)
            {
                td -= m1;
                if (td > m2)
                {
                    td -= m2;
                    lm += 1;
                }
                else
                {
                    Yoon = 1;
                    break;
                }
            }
            else break;
        }
    }
    ly += 1841;
    lm += 1;
    if (Year % 400 == 0 || Year % 100 != 0 || Year % 4 == 0)
    {
        ld = td;
    }
    else
    {
        ld = td - 1;
    }
    w = td2 % 7;
    YYYYMMDD = ly * 10000 + lm * 100 + ld;
    ResultArray3[0] = YYYYMMDD;
    ResultArray3[1] = Yoon;
    ResultArray3[2] = w;
    if (_info_array) free(_info_array);
    return 1;
}

long CalcLunarToSolar(long YYYYMMDD, long Leaf, long* ResultArray2, long* _info_array_raw)
{
    long i, j;
    long Year = YYYYMMDD / 10000;
    long Month = (YYYYMMDD - Year * 10000) / 100;
    long Day = (YYYYMMDD - Year * 10000 - Month * 100);
    if (Year < 1841 || 2043 < Year) return -99999999;
    if (Month < 1 || 12 < Month) return -99999999;

    long** _info_array = (long**)malloc(sizeof(long*) * N_Info_Array);
    for (i = 0; i < N_Info_Array; i++) _info_array[i] = _info_array_raw + i * 12;

    long _info_month[12] = { 31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };

    long lyear = Year;
    long lmonth = Month;
    long y1 = lyear - 1841;
    long m1 = lmonth - 1;
    long leapyes = 0;
    long mm;
    if (_info_array[y1][m1] > 2) leapyes = Leaf;

    if (leapyes == 1)
    {
        if (_info_array[y1][m1] == 3 || _info_array[y1][m1] == 5) mm = 29;
        else if (_info_array[y1][m1] == 4 || _info_array[y1][m1] == 6) mm = 30;
        else return -99999999;
    }
    else
    {
        if (_info_array[y1][m1] == 1 || _info_array[y1][m1] == 3 || _info_array[y1][m1] == 4) mm = 29;
        else if (_info_array[y1][m1] == 2 || _info_array[y1][m1] == 5 || _info_array[y1][m1] == 6) mm = 30;
        else return -99999999;
    }

    if (Day < 1 || mm < Day) return -99999999;

    long lday = Day;
    long td = 0;
    for (i = 0; i < y1; i++)
    {
        for (j = 0; j < 12; j++)
        {
            if (_info_array[i][j] == 1) {
                td += 29;
            }
            else if (_info_array[i][j] == 2) {
                td += 30;
            }
            else if (_info_array[i][j] == 3) {
                td += 58;
            }
            else if (_info_array[i][j] == 4) {
                td += 59;
            }
            else if (_info_array[i][j] == 5) {
                td += 59;
            }
            else if (_info_array[i][j] == 6) {
                td += 60;
            }
            else return -99999999;
        }
    }

    for (j = 0; j < m1; j++)
    {
        if (_info_array[y1][j] == 1) td += 29;
        else if (_info_array[y1][j] == 2) td += 30;
        else if (_info_array[y1][j] == 3) td += 58;
        else if (_info_array[y1][j] == 4) td += 59;
        else if (_info_array[y1][j] == 5) td += 59;
        else if (_info_array[y1][j] == 6) td += 60;
        else return -99999999;
    }

    if (leapyes == 1)
    {
        if (_info_array[y1][m1] == 3 || _info_array[y1][m1] == 4) td += 29;
        else if (_info_array[y1][m1] == 5 || _info_array[y1][m1] == 6) td += 30;
        else return -99999999;
    }
    td += lday + 22;
    y1 = 1840;
    long leap;
    long y2;
    do {
        y1 += 1;
        leap = ((y1 % 4 == 0 && y1 % 100 != 0) || y1 % 400 == 0);

        if (leap) y2 = 366;
        else y2 = 365;

        if (td <= y2) break;
        td -= y2;
    } while (1);

    long syear = y1;
    _info_month[1] = y2 - 337;
    m1 = 0;

    do {
        m1 += 1;
        if (td <= _info_month[m1 - 1]) break;
        td -= _info_month[m1 - 1];
    } while (1);

    long smonth = m1;
    long sday = td;
    long y = syear - 1;
    td = y * 365 + y / 4 - y / 100 + y / 400;
    for (i = 0; i < smonth - 1; i++) td += _info_month[i];

    td += sday;
    long w = td % 7;
    YYYYMMDD = syear * 10000 + smonth * 100 + sday;
    ResultArray2[0] = YYYYMMDD;
    ResultArray2[1] = w;
    if (_info_array) free(_info_array);
    return 1;
}

long LunarToSolar(long YYYYMMDD_Lunar, long Leap = 0)
{
    long ResultArray2[2] = { 0, };
    long ResultCode = CalcLunarToSolar(YYYYMMDD_Lunar, Leap, ResultArray2, _info_array_raw);
    if (ResultCode < 0) return ResultCode;
    else return ResultArray2[0];
}

long SolarToLunar(long YYYYMMDD_Solar)
{
    long ResultArray3[3] = { 0, };
    long ResultCode = CalcSolarToLunar(YYYYMMDD_Solar, ResultArray3, _info_array_raw);
    if (ResultCode < 0) return ResultCode;
    else return ResultArray3[0];

}

void bubble_sort_date(long* arr, long count, long ascending)
{
    long temp;
    long i, j;
    if (ascending == 1)
    {
        for (i = 0; i < count; i++)
        {
            for (j = 0; j < count - 1; j++)
            {
                if (arr[j] > arr[j + 1])          // 이전 값이 더 크면
                {                                 // 이전 값을 다음 요소로 보내고 다음 요소를 이전 요소 자리로
                    temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
    else
    {
        for (i = 0; i < count; i++)
        {
            for (j = 0; j < count - 1; j++)
            {
                if (arr[j] < arr[j + 1])
                {
                    temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
}

long isin_Longtype(long x, long* array, long narray)
{
    long i;
    long s = 0;
    for (i = 0; i < narray; i++)
    {
        if (x == array[i])
        {
            s = 1;
            break;
        }
    }
    return s;
}

long* MallocUnique(long* MyArray, long NArray, long& NUnique)
{
    long i;
    long* TempArray = (long*)malloc(sizeof(long) * NArray);
    long nu = 0;
    for (i = 0; i < NArray; i++)
    {
        if (i == 0)
        {
            TempArray[0] = MyArray[0];
            nu = 1;
        }
        else
        {
            if (isin_Longtype(MyArray[i], TempArray, nu) == 0)
            {
                TempArray[nu] = MyArray[i];
                nu += 1;
            }
        }
    }
    NUnique = nu;
    long* ResultArray = (long*)malloc(sizeof(long) * NUnique);
    for (i = 0; i < nu; i++) ResultArray[i] = TempArray[i];
    free(TempArray);
    return ResultArray;
}

///////////////////////////////////////
// 여기서부터 한국 Holiday 관련 함수 //
///////////////////////////////////////

// 임시공휴일 하드코딩
long* Calc_NTempHoliday_Korea(long YYYY, long& ArrayLength)
{
    // 특정 년도에 임시공휴일 Array를 리턴한다.
    // ArrayLength는 특정 년도 임시공휴일 개수를 리턴한다.
    // 함수 리턴으로 메모리 할당하므로 나중에 해제해야함.
    long i, k;
    const long NTempHoliday = 10;
    long TempHolidayList[NTempHoliday] =
    {

        // 더 있으면 추가하고 NTempHoliday 바꾸기
        20020701, 20150814, 20171002, 20200817, 20220309,
        20220601, 20231002, 20240410, 20241001, 20250127
    };
    ArrayLength = 0;
    for (i = 0; i < NTempHoliday; i++) if (YYYY == (long)(TempHolidayList[i] / 10000)) ArrayLength += 1;

    long* ResultArray = (long*)malloc(sizeof(long) * max(1, ArrayLength));
    k = 0;
    for (i = 0; i < NTempHoliday; i++)
    {
        if (YYYY == (long)(TempHolidayList[i] / 10000))
        {
            ResultArray[k] = TempHolidayList[i];
            k += 1;
        }
    }
    return ResultArray;
}

// 3.1절
long Calc_31Day_Korea(long YYYY)
{
    long YYYYMMDD_Solar = YYYY * 10000 + 301;
    long MOD07 = CDateToExcelDate(YYYYMMDD_Solar) % 7;

    // 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    if (MOD07 == 0) return DayPlus(YYYYMMDD_Solar, 2);
    else if (MOD07 == 1) return DayPlus(YYYYMMDD_Solar, 1);
    else return YYYYMMDD_Solar;
}

// 어린이날
long Calc_ChildrensDay_Korea(long YYYY)
{
    long YYYYMMDD_Solar = YYYY * 10000 + 505;
    long MOD07 = CDateToExcelDate(YYYYMMDD_Solar) % 7;

    // 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    if (MOD07 == 0) return DayPlus(YYYYMMDD_Solar, 2);
    else if (MOD07 == 1) return DayPlus(YYYYMMDD_Solar, 1);
    else return YYYYMMDD_Solar;

}

// 광복절
long Calc_Gwangbok_Korea(long YYYY)
{
    long YYYYMMDD_Solar = YYYY * 10000 + 815;
    long MOD07 = CDateToExcelDate(YYYYMMDD_Solar) % 7;

    // 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    if (MOD07 == 0) return DayPlus(YYYYMMDD_Solar, 2);
    else if (MOD07 == 1) return DayPlus(YYYYMMDD_Solar, 1);
    else return YYYYMMDD_Solar;

}

// 개천절
long Calc_GaechunJeol_Korea(long YYYY)
{
    long YYYYMMDD_Solar = YYYY * 10000 + 1003;
    long MOD07 = CDateToExcelDate(YYYYMMDD_Solar) % 7;

    // 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    if (MOD07 == 0) return DayPlus(YYYYMMDD_Solar, 2);
    else if (MOD07 == 1) return DayPlus(YYYYMMDD_Solar, 1);
    else return YYYYMMDD_Solar;

}

// 한글날
long Calc_Hangul_Korea(long YYYY)
{
    long YYYYMMDD_Solar = YYYY * 10000 + 1009;
    long MOD07 = CDateToExcelDate(YYYYMMDD_Solar) % 7;

    // 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    if (MOD07 == 0) return DayPlus(YYYYMMDD_Solar, 2);
    else if (MOD07 == 1) return DayPlus(YYYYMMDD_Solar, 1);
    else return YYYYMMDD_Solar;
}

// 크리스마스
long Calc_Christmas_Korea(long YYYY)
{
    long YYYYMMDD_Solar = YYYY * 10000 + 1225;
    long MOD07 = CDateToExcelDate(YYYYMMDD_Solar) % 7;

    // 토요일이라면 이틀후인 월요일, 일요일이라면 하루 뒤인 월요일로 리턴
    if (MOD07 == 0) return DayPlus(YYYYMMDD_Solar, 2);
    else if (MOD07 == 1) return DayPlus(YYYYMMDD_Solar, 1);
    else return YYYYMMDD_Solar;
}

// 부처님오신날
long Calc_Budda_Korea(long YYYY)
{
    // 4월 8일
    long YYYYMMDD_Lunar = YYYY * 10000 + 408;
    long ResultArray2[2] = { 0, };
    long ResultCode = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, _info_array_raw);
    long YYYYMMDD_Solar = ResultArray2[0];
    // 부처님오신날이 어린이날이랑 같은 말도안되는 때가 있음 
    long ChildDay = Calc_ChildrensDay_Korea(YYYY);
    if (ResultCode < 0) return ResultCode;
    else if (ChildDay == YYYYMMDD_Solar)
    {
        if (ResultArray2[1] == 5)           // 어린이날 또는 어린이날의 대체휴일과 부처님오신날이 같고 금요일
        {
            return DayPlus(YYYYMMDD_Solar, 3);
        }
        else                                // 그 외의 경우
        {
            return DayPlus(ChildDay, 1);
        }
    }
    else
    {
        if (ResultArray2[1] == 0) // 일요일
        {
            return DayPlus(YYYYMMDD_Solar, 1);
        }
        else if (ResultArray2[1] == 6) // 토요일
        {
            return DayPlus(YYYYMMDD_Solar, 2);
        }
        else
        {
            return YYYYMMDD_Solar;
        }
    }
}

// 설 3일
void Calc3_newyear(long YYYY, long* ResultDay3, long& ResultCode)
{
    // 구정 3일
    long YYYYMMDD_Lunar = YYYY * 10000 + 101;
    long ResultArray2[2] = { 0, };
    long Result = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, _info_array_raw);
    long YYYYMMDD_Solar = ResultArray2[0];
    ResultCode = Result;
    if (ResultCode >= 0)
    {
        long b = ResultArray2[1];
        long TempDate;
        ResultDay3[0] = DayPlus(YYYYMMDD_Solar, -1);
        ResultDay3[1] = YYYYMMDD_Solar + 0;
        ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 1);
        if (b == 6)
        {
            // 구정이 토요일인 경우 세번째 날짜가 일요일인데 그걸 월요일로 바꿈
            // 금, 토, 월
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2);
        }
        else if (b == 0)
        {
            // 구정이 일요일인 경우
            // 토, 월, 화
            ResultDay3[1] = ResultDay3[2];      // 월
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2);     // 화
        }
        else if (b == 1)
        {
            // 구정이 월요일인 경우 첫번째 날짜가 일요일인데 그걸 화요일로 바꿈
            ResultDay3[0] = ResultDay3[1];                  // 월
            ResultDay3[1] = ResultDay3[2];                  // 화
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2);     // 수
        }

    }
}

// 추석 3일
void Calc3_chuseok(long YYYY, long* ResultDay3, long& ResultCode)
{
    // 추석 3일
    long YYYYMMDD_Lunar = YYYY * 10000 + 815;
    long ResultArray2[2] = { 0, };
    long Result = CalcLunarToSolar(YYYYMMDD_Lunar, 0, ResultArray2, _info_array_raw);
    long YYYYMMDD_Solar = ResultArray2[0];
    ResultCode = Result;
    if (ResultCode >= 0)
    {
        long b = ResultArray2[1];
        long TempDate;
        ResultDay3[0] = DayPlus(YYYYMMDD_Solar, -1);
        ResultDay3[1] = YYYYMMDD_Solar + 0;
        ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 1);
        if (b == 6)
        {
            // 추석이 토요일인 경우 세번째 날짜가 일요일인데 그걸 월요일로 바꿈
            // 금, 토, 월
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2);
        }
        else if (b == 0)
        {
            // 추석이 일요일인 경우
            // 토, 월, 화
            ResultDay3[1] = ResultDay3[2];      // 월
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2);     // 화
        }
        else if (b == 1)
        {
            // 추석이 월요일인 경우 첫번째 날짜가 일요일인데 그걸 화요일로 바꿈
            ResultDay3[0] = ResultDay3[1];                  // 월
            ResultDay3[1] = ResultDay3[2];                  // 화
            ResultDay3[2] = DayPlus(YYYYMMDD_Solar, 2);     // 수
        }
    }
}

// 공휴일 16개 매핑하기
void Mapping_Holiday16(long YYYY, long* Array16)
{
    long i;
    long Jan01 = YYYY * 10000 + 101;                            // 1.1
    Array16[0] = Jan01;

    long ResultCode = 0;
    long* Seol = Array16 + 1;
    if (LunarDateKoreanHardCodeYear >= YYYY) Calc3_newyear(YYYY, Seol, ResultCode);                      // 설연휴
    else ResultCode = -1;

    if (ResultCode < 0) for (i = 0; i < 3; i++) Seol[i] = Jan01;// 음력 코드 갱신안해서 매핑안되면 걍 1.1일로

    long Samil = Calc_31Day_Korea(YYYY);
    Array16[4] = Samil;

    long Labor = YYYY * 10000 + 501;
    Array16[5] = Labor;

    long Budda;
    if (LunarDateKoreanHardCodeYear >= YYYY) Budda = Calc_Budda_Korea(YYYY);
    else Budda = Jan01;

    if (Budda > 0) Array16[6] = Budda;
    else Array16[6] = Jan01;

    long ChildrenDay = Calc_ChildrensDay_Korea(YYYY);
    Array16[7] = ChildrenDay;
    Array16[8] = YYYY * 10000 + 606;
    long Gwangbok = Calc_Gwangbok_Korea(YYYY);
    Array16[9] = Gwangbok;

    long* Chuseok = Array16 + 10;
    if (LunarDateKoreanHardCodeYear >= YYYY) Calc3_chuseok(YYYY, Chuseok, ResultCode);
    else ResultCode = -1;

    if (ResultCode < 0) for (i = 0; i < 3; i++) Chuseok[i] = Jan01; // 음력코드 갱신 안한 경우 이전공휴일 매핑

    long GaeChun = Calc_GaechunJeol_Korea(YYYY);
    if (GaeChun == Chuseok[0] || GaeChun == Chuseok[1] || GaeChun == Chuseok[2])
    {
        // 개천절이 추석에 껴있을 경우 하루 더 대체휴일
        GaeChun = DayPlus(Chuseok[2], 1);
        if (CDateToExcelDate(GaeChun) % 7 == 0) GaeChun = DayPlus(GaeChun, 2);
        else if (CDateToExcelDate(GaeChun) % 7 == 1) GaeChun == DayPlus(GaeChun, 1);
    }
    Array16[13] = GaeChun;

    long HanGul = Calc_Hangul_Korea(YYYY);
    Array16[14] = HanGul;

    long Christmas = Calc_Christmas_Korea(YYYY);
    Array16[15] = Christmas;

}

// 임시공휴일 + 공휴일 매핑
long* Mapping_KoreanHoliday_YYYY(long YYYY, long& NHoliday)
{
    long i, k;
    long NTempHoliday = 0;
    long* TempHoliday = Calc_NTempHoliday_Korea(YYYY, NTempHoliday);                        // 메모리 할당 1

    long NArray_Org = 16;
    long NArray = NArray_Org + NTempHoliday;

    // 원래는 16개 + 임시공휴일개수 이나 
    // 하드코드된 음력 연도보다 커지면 설, 추석, 석가탄신일 제외하자
    if (YYYY > LunarDateKoreanHardCodeYear) NArray = NArray_Org + NTempHoliday;

    long* HolidayYYYY = (long*)malloc(sizeof(long) * NArray_Org);                           // 메모리 할당 2
    Mapping_Holiday16(YYYY, HolidayYYYY);

    long* ResultArray = (long*)malloc(sizeof(long) * NArray);                               // 리턴용 할당
    k = 0;
    for (i = 0; i < NArray_Org; i++)
    {
        if (HolidayYYYY[i] > 0)
        {
            ResultArray[k] = HolidayYYYY[i];
            k += 1;
        }
    }

    for (i = 0; i < NTempHoliday; i++)
    {
        ResultArray[k] = TempHoliday[i];
        k += 1;
    }

    NHoliday = NArray;
    free(TempHoliday);                                                                      // 메모리할당해제1
    free(HolidayYYYY);                                                                      // 메모리할당해제2
    return ResultArray;
}

long* Malloc_KoreaHolidayArray(long Start_YYYY, long End_YYYY, long& NHolidayArray)
{
    long i, j, k;
    long** Holidays = (long**)malloc(sizeof(long*) * max(1, (End_YYYY - Start_YYYY + 1)));          // 메모리할당1
    long* nholidays = (long*)malloc(sizeof(long) * max(1, (End_YYYY - Start_YYYY + 1)));            // 메모리할당2
    long n = 0;
    long nh = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        Holidays[i] = Mapping_KoreanHoliday_YYYY(Start_YYYY + i, nh);
        nholidays[i] = nh;
        bubble_sort_date(Holidays[i], nholidays[i], 1);
        n += nh;
    }

    NHolidayArray = n;
    long* ResultArray = (long*)malloc(sizeof(long) * max(1, n));                                    // 리턴용할당
    k = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        for (j = 0; j < nholidays[i]; j++)
        {
            ResultArray[k] = Holidays[i][j];
            k += 1;
        }
    }

    for (i = 0; i < max(1, (End_YYYY - Start_YYYY + 1)); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2
    return ResultArray;
}

///////////////////////////////////////
// 여기서부터 미국 Holiday 관련 함수 //
///////////////////////////////////////

// YYYY = 년
// MM = 월
// Nth = n번째
// Date = x요일 0:토 1:일 2:월 3:화 4:수 5:목 6:금
long Nth_Date(long YYYY, long MM, long Nth, long Date)
{
    // N번째 x요일 계산
    // Variables : YYYY, MM, Nth, WhatDate
    long i;
    long YYYYMMDD = YYYY * 10000 + MM * 100 + 1;
    long YYYYMM = YYYY * 100 + MM;
    long ExcelDate = CDateToExcelDate(YYYYMMDD);
    long MOD7;
    long n = 0;
    long TempDate;
    long nthdate;
    long nthdateYYYYMM;

    for (i = 0; i < 31; i++)
    {
        TempDate = ExcelDate + i;
        MOD7 = TempDate % 7;
        if (MOD7 == Date)
        {
            n += 1;
            nthdate = ExcelDateToCDate(TempDate);
            if (n == Nth)
            {
                nthdateYYYYMM = nthdate / 100;
                if (YYYYMM == nthdateYYYYMM) return nthdate;
                else if (YYYYMM < nthdateYYYYMM)
                {
                    // 다음달로 넘어갔으면 7일 전 리턴
                    return ExcelDateToCDate(TempDate - 7);
                }
            }
        }
    }

    return nthdate;
}

// 날짜가 고정된 공휴일 -> 대체공휴일 또는 당일 산출
long FixedHoliday_YYYYMMDD_US(long YYYYMMDD)
{
    long i;
    long ExcelDate = CDateToExcelDate(YYYYMMDD);
    long MOD7 = ExcelDate % 7;
    if (MOD7 == 0)
    {
        // 공휴일이 토요일이면 전날
        return DayPlus(YYYYMMDD, -1);
    }
    else if (MOD7 == 1)
    {
        // 공휴일이 일요일이면 다음날
        return DayPlus(YYYYMMDD, 1);
    }
    else
    {
        return YYYYMMDD;
    }
}

// 미국 대통령 취임식 연도인지 리턴
long IsPresidentYear(long YYYY)
{
    if (YYYY % 4 == 1) return 1;
    else return 0;
}

long CalcFullMoonDay(long YYYY)
{
    long i;
    long StartDate = YYYY * 10000 + 321;

    long Day1 = LunarToSolar(YYYY * 10000 + 115);
    long Day2 = LunarToSolar(YYYY * 10000 + 215);
    long Day2p5 = LunarToSolar(YYYY * 10000 + 215, 1);
    long Day3 = LunarToSolar(YYYY * 10000 + 315);
    long FullMoonDay = Day1;
    long Days[4] = { Day1, Day2, Day2p5, Day3 };
    for (i = 0; i < 4; i++)
    {
        if (Days[i] > StartDate)
        {
            FullMoonDay = Days[i];
            break;
        }
    }
    return FullMoonDay;
}

long RebirthDay(long YYYY)
{
    long i;
    long FullMoonDay = CalcFullMoonDay(YYYY);
    long FullMoonDayExcel = CDateToExcelDate(FullMoonDay);
    long TempExcelDate = FullMoonDayExcel;
    long MOD7;
    if (TempExcelDate % 7 == 0) return ExcelDateToCDate(FullMoonDayExcel + 8);
    else if (TempExcelDate % 7 == 1) return ExcelDateToCDate(FullMoonDayExcel + 7);
    for (i = 1; i < 8; i++)
    {
        TempExcelDate = FullMoonDayExcel + i;
        MOD7 = TempExcelDate % 7;
        if (MOD7 == 1)
        {
            break;
        }
    }
    return ExcelDateToCDate(TempExcelDate);
}

long RebirthDayMinus2(long YYYY)
{
    long i;
    long FullMoonDay = CalcFullMoonDay(YYYY);
    long FullMoonDayExcel = CDateToExcelDate(FullMoonDay);
    long TempExcelDate = FullMoonDayExcel;
    long MOD7;
    if (TempExcelDate % 7 == 0) return ExcelDateToCDate(FullMoonDayExcel + 8 - 2);
    else if (TempExcelDate % 7 == 1) return ExcelDateToCDate(FullMoonDayExcel + 7 - 2);
    for (i = 1; i < 8; i++)
    {
        TempExcelDate = FullMoonDayExcel + i;
        MOD7 = TempExcelDate % 7;
        if (MOD7 == 1)
        {
            break;
        }
    }
    return ExcelDateToCDate(TempExcelDate - 2);
}

long RebirthDayPlus1(long YYYY)
{
    long i;
    long FullMoonDay = CalcFullMoonDay(YYYY);
    if (FullMoonDay < 0) return -9999999;
    long FullMoonDayExcel = CDateToExcelDate(FullMoonDay);
    long TempExcelDate = FullMoonDayExcel;
    long MOD7;
    if (TempExcelDate % 7 == 0) return ExcelDateToCDate(FullMoonDayExcel + 8 + 1);
    else if (TempExcelDate % 7 == 1) return ExcelDateToCDate(FullMoonDayExcel + 7 + 1);
    for (i = 1; i < 8; i++)
    {
        TempExcelDate = FullMoonDayExcel + i;
        MOD7 = TempExcelDate % 7;
        if (MOD7 == 1)
        {
            break;
        }
    }
    return ExcelDateToCDate(TempExcelDate + 1);
}

// U.S Holiday Mapping
void Mapping_USHoliday(
    long YYYY,                  // 연도 
    long* HolidayArray         // 미리 할당된 Array 길이 11개
)
{
    long Jan01 = (YYYY * 10000 + 101);
    long Jan01Excel = CDateToExcelDate(Jan01);
    if (Jan01Excel % 7 == 1) Jan01 = DayPlus(Jan01, 1); // 새해 첫날이 일요일일경우만 대체해줌

    long President = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 120);  // 대통령 취임식 안쉼
    long Juneteenth = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 619);
    long Independence = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 704);
    long Veterans = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1111);
    long Christmas = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1225);

    long MartinLuther = Nth_Date(YYYY, 1, 3, 2);    // 1월 3번째 월요일
    long PresidentsDay = Nth_Date(YYYY, 2, 3, 2);   // 2월 3번째 월요일
    long MemorialDay = Nth_Date(YYYY, 5, 5, 2);     // 5월 마지막 월요일
    long LaborDay = Nth_Date(YYYY, 9, 1, 2);        // 9월 첫번째 월요일
    long ColumBus = Nth_Date(YYYY, 10, 2, 2);       // 10월 두번째 월요일
    long Thanks = Nth_Date(YYYY, 11, 4, 5);         // 11월 네번째 목요일

    HolidayArray[0] = Jan01;
    HolidayArray[1] = MartinLuther;
    HolidayArray[2] = PresidentsDay;
    HolidayArray[3] = MemorialDay;
    HolidayArray[4] = Juneteenth;
    HolidayArray[5] = Independence;
    HolidayArray[6] = LaborDay;
    HolidayArray[7] = ColumBus;
    HolidayArray[8] = Veterans;
    HolidayArray[9] = Thanks;
    HolidayArray[10] = Christmas;
}

// U.S Holiday Array를 Malloc하는 함수
long* Malloc_USHolidayArray(
    long Start_YYYY,                // 시작연도
    long End_YYYY,                  // 종료연도
    long& NHolidayArray             // Output : 할당된 공휴일 Array의 길이 리턴
)
{
    // U.S Holiday Array를 Malloc하는 함수
    long i, j, k;
    long** Holidays = (long**)malloc(sizeof(long*) * max(1, (End_YYYY - Start_YYYY + 1)));          // 메모리할당1
    long* nholidays = (long*)malloc(sizeof(long) * max(1, (End_YYYY - Start_YYYY + 1)));            // 메모리할당2
    long n = 0;
    long nh = 0;
    long ispresidflag = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        ispresidflag = IsPresidentYear(Start_YYYY + i);
        Holidays[i] = (long*)malloc(sizeof(long) * 15);
        Mapping_USHoliday(Start_YYYY + i, Holidays[i]);
        nholidays[i] = 11;
        bubble_sort_date(Holidays[i], nholidays[i], 1);
        n += nholidays[i];
    }

    NHolidayArray = n;
    long* ResultArray = (long*)malloc(sizeof(long) * max(1, n));                                    // 리턴용할당
    k = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        for (j = 0; j < nholidays[i]; j++)
        {
            ResultArray[k] = Holidays[i][j];
            k += 1;
        }
    }

    for (i = 0; i < max(1, (End_YYYY - Start_YYYY + 1)); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2
    return ResultArray;
}

// U.S NYMEX Holiday Mapping
void Mapping_US_NYMEXHoliday(
    long YYYY,                  // 연도 
    long* HolidayArray         // 미리 할당된 Array(11개
)
{
    long TempDate;
    // Nymex : 부활절 쉼, 준틴스 안쉼, 독립일 전날도 쉼, 콜럼버스 안쉼, 빼뺴로 안쉼, Thanksgiv 쉼
    long Jan01 = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 101);
    long RebirthMinus2;

    if (YYYY < LunarDateKoreanHardCodeYear) RebirthMinus2 = RebirthDayMinus2(YYYY);     // 부활절 쉼
    else RebirthMinus2 = Jan01;


    //long President = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 120);                    // 취임식 안쉼
    //long Juneteenth = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 619);                   // 준틴스 안쉼
    long Independence = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 704);                   // 독립일 쉼
    long IndependenceExcel = CDateToExcelDate(Independence);
    long IndependencePrev = Independence;                                               // 독립일 전날 쉼
    if (IndependenceExcel % 7 == 3)
    {
        // 독립일이 화요일이면 월요일, 독립일이 목요일이면 금요일
        IndependencePrev = ExcelDateToCDate(IndependenceExcel - 1);
    }
    else if (IndependenceExcel % 7 == 5)
    {
        IndependencePrev = ExcelDateToCDate(IndependenceExcel + 1);
        TempDate = IndependencePrev;
        IndependencePrev = Independence;
        Independence = TempDate;
    }

    //long Veterans = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1111);                    // 빼빼로 안쉼
    long Christmas = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1225);
    long ChristmasExcel = CDateToExcelDate(Christmas);
    long ChristmasPrev = Christmas;
    if (ChristmasExcel % 7 == 3)
    {
        ChristmasPrev = ExcelDateToCDate(ChristmasExcel - 1);
    } 
    else if (ChristmasExcel % 7 == 5)
    {
        ChristmasPrev = ExcelDateToCDate(ChristmasExcel + 1);
        TempDate = ChristmasPrev;
        ChristmasPrev = Christmas;
        Christmas = TempDate;
    }

    long MartinLuther = Nth_Date(YYYY, 1, 3, 2);    // 1월 3번째 월요일
    long PresidentsDay = Nth_Date(YYYY, 2, 3, 2);   // 2월 3번째 월요일
    long MemorialDay = Nth_Date(YYYY, 5, 5, 2);     // 5월 마지막 월요일
    long LaborDay = Nth_Date(YYYY, 9, 1, 2);        // 9월 첫번째 월요일
    //long ColumBus = Nth_Date(YYYY, 10, 2, 2);       // 10월 두번째 월요일             // 콜롬버스 안쉼
    long Thanks = Nth_Date(YYYY, 11, 4, 5);         // 11월 네번째 목요일

    HolidayArray[0] = Jan01;
    HolidayArray[1] = MartinLuther;
    HolidayArray[2] = PresidentsDay;
    HolidayArray[3] = RebirthMinus2;
    HolidayArray[4] = MemorialDay;
    HolidayArray[5] = IndependencePrev;
    HolidayArray[6] = Independence;
    HolidayArray[7] = LaborDay;
    HolidayArray[8] = Thanks;
    HolidayArray[9] = ChristmasPrev;
    HolidayArray[10] = Christmas;
}

// U.S NYMEX Holiday Array를 Malloc하는 함수
long* Malloc_US_NYMEX_HolidayArray(
    long Start_YYYY,                // 시작연도
    long End_YYYY,                  // 종료연도
    long& NHolidayArray             // Output : 할당된 공휴일 Array의 길이 리턴
)
{
    // U.S Holiday Array를 Malloc하는 함수
    long i, j, k;
    long** Holidays = (long**)malloc(sizeof(long*) * max(1, (End_YYYY - Start_YYYY + 1)));          // 메모리할당1
    long* nholidays = (long*)malloc(sizeof(long) * max(1, (End_YYYY - Start_YYYY + 1)));            // 메모리할당2
    long n = 0;
    long nh = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        Holidays[i] = (long*)malloc(sizeof(long) * 15);
        Mapping_US_NYMEXHoliday(Start_YYYY + i, Holidays[i]);
        nholidays[i] = 11;
        bubble_sort_date(Holidays[i], nholidays[i], 1);
        n += nholidays[i];
    }

    NHolidayArray = n;
    long* ResultArray = (long*)malloc(sizeof(long) * max(1, n));                                    // 리턴용할당
    k = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        for (j = 0; j < nholidays[i]; j++)
        {
            ResultArray[k] = Holidays[i][j];
            k += 1;
        }
    }

    for (i = 0; i < max(1, (End_YYYY - Start_YYYY + 1)); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2
    return ResultArray;
}

// U.S NYSE Holiday Mapping
void Mapping_US_NYSEHoliday(
    long YYYY,                  // 연도 
    long* HolidayArray         // 미리 할당된 Array(13개
)
{
    // NYSE : 부활절 쉼, 준틴스쉼, 독립일 전날도 쉼, 콜럼버스 안쉼, 빼뺴로 안쉼, Thanksgiv 다음도 당일도 쉼, 크리스마스 전날도 쉼
    long Jan01 = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 101);
    long RebirthMinus2;

    if (YYYY < LunarDateKoreanHardCodeYear) RebirthMinus2 = RebirthDayMinus2(YYYY);     // 부활절 쉼
    else RebirthMinus2 = Jan01;

    //long President = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 120);                    // 취임식 안쉼
    long Juneteenth = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 619);                     // 준틴스 쉼
    long Independence = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 704);                   // 독립일 쉼

    //long Veterans = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1111);                    // 빼빼로 안쉼
    long Christmas = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1225);

    long MartinLuther = Nth_Date(YYYY, 1, 3, 2);    // 1월 3번째 월요일
    long PresidentsDay = Nth_Date(YYYY, 2, 3, 2);   // 2월 3번째 월요일
    long MemorialDay = Nth_Date(YYYY, 5, 5, 2);     // 5월 마지막 월요일
    long LaborDay = Nth_Date(YYYY, 9, 1, 2);        // 9월 첫번째 월요일
    //long ColumBus = Nth_Date(YYYY, 10, 2, 2);       // 10월 두번째 월요일             // 콜롬버스 안쉼

    long Thanks = Nth_Date(YYYY, 11, 4, 5);         // 11월 네번째 목요일
    long ThanksNext = ExcelDateToCDate(CDateToExcelDate(Thanks) + 1);// 추수감사절 다음
    HolidayArray[0] = Jan01;
    HolidayArray[1] = MartinLuther;
    HolidayArray[2] = PresidentsDay;
    HolidayArray[3] = RebirthMinus2;
    HolidayArray[4] = MemorialDay;
    HolidayArray[5] = Juneteenth;
    HolidayArray[6] = Independence;
    HolidayArray[7] = LaborDay;
    HolidayArray[8] = Thanks;
    HolidayArray[9] = ThanksNext;
    HolidayArray[10] = Christmas;
}

// U.S NYSE Holiday Array를 Malloc하는 함수
long* Malloc_US_NYSE_HolidayArray(
    long Start_YYYY,                // 시작연도
    long End_YYYY,                  // 종료연도
    long& NHolidayArray             // Output : 할당된 공휴일 Array의 길이 리턴
)
{
    // U.S Holiday Array를 Malloc하는 함수
    long i, j, k;
    long** Holidays = (long**)malloc(sizeof(long*) * max(1, (End_YYYY - Start_YYYY + 1)));          // 메모리할당1
    long* nholidays = (long*)malloc(sizeof(long) * max(1, (End_YYYY - Start_YYYY + 1)));            // 메모리할당2
    long n = 0;
    long nh = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        Holidays[i] = (long*)malloc(sizeof(long) * 15);
        Mapping_US_NYSEHoliday(Start_YYYY + i, Holidays[i]);
        nholidays[i] = 11;
        bubble_sort_date(Holidays[i], nholidays[i], 1);
        n += nholidays[i];
    }

    NHolidayArray = n;
    long* ResultArray = (long*)malloc(sizeof(long) * max(1, n));                                    // 리턴용할당
    k = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        for (j = 0; j < nholidays[i]; j++)
        {
            ResultArray[k] = Holidays[i][j];
            k += 1;
        }
    }

    for (i = 0; i < max(1, (End_YYYY - Start_YYYY + 1)); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2
    return ResultArray;
}

//////////////////////////
// GBP 영국 공휴일 관련 함수
//////////////////////////

// 날짜가 고정된 공휴일 -> 대체공휴일 또는 당일 산출
long FixedHoliday_YYYYMMDD_GBP(long YYYYMMDD)
{
    long i;
    long ExcelDate = CDateToExcelDate(YYYYMMDD);
    long MOD7 = ExcelDate % 7;
    if (MOD7 == 0)
    {
        // 공휴일이 토요일이면 2일 후
        return DayPlus(YYYYMMDD, 2);
    }
    else if (MOD7 == 1)
    {
        // 공휴일이 일요일이면 1일 후
        return DayPlus(YYYYMMDD, 1);
    }
    else
    {
        return YYYYMMDD;
    }
}

// GBP Holiday를 mapping
void Mapping_GBPHoliday(
    long YYYY,                  // 연도
    long* HolidayArray,         // 미리 할당된 Array(부활절이 입력되면 7개 아니면 5개 길이)
    long EasterMondayDay        // 부활절 날짜 YYYYMMDD 입력
)
{
    long MOD07;
    long Jan01 = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 101);
    long Christmas = YYYY * 10000 + 1225;

    MOD07 = CDateToExcelDate(Christmas) % 7;
    if (MOD07 == 0 || MOD07 == 1) Christmas = YYYY * 10000 + 1227;      // 크리스마스 대체휴일

    long BoxingDay = YYYY * 10000 + 1226;
    MOD07 = CDateToExcelDate(BoxingDay) % 7;
    if (MOD07 == 0 || MOD07 == 1) BoxingDay = YYYY * 10000 + 1228;      // Boxing Day 대체휴일

    long MemorialDay = Nth_Date(YYYY, 5, 5, 2);     // 5월 마지막 월요일
    long LaborDay = Nth_Date(YYYY, 5, 1, 2);        // 5월 첫번째 월요일

    HolidayArray[0] = Jan01;
    HolidayArray[1] = Christmas;
    HolidayArray[2] = BoxingDay;
    if (HolidayArray[1] > HolidayArray[2])
    {
        HolidayArray[1] = BoxingDay;
        HolidayArray[2] = Christmas;
    }
    HolidayArray[3] = MemorialDay;
    HolidayArray[4] = LaborDay;
    HolidayArray[5] = Nth_Date(YYYY, 8, 5, 2);      // 8월 마지막 월요일
    
    if (EasterMondayDay > 0)
    {
        HolidayArray[6] = EasterMondayDay;
        long EasterMondayExcel = CDateToExcelDate(EasterMondayDay);
        long GoodFriday = -1;
        for (long i = 1; i < 10; i++)
        {
            MOD07 = (EasterMondayExcel - i) % 7;
            if (MOD07 == 6)
            {
                GoodFriday = ExcelDateToCDate(EasterMondayExcel - i);
                break;
            }
        }
        HolidayArray[7] = GoodFriday;
    }

}

// GBP Holiday Array를 Malloc하는 함수
long* Malloc_GBPHolidayArray(
    long Start_YYYY,                            // 시작 연도
    long End_YYYY,                              // 종료 연도
    long& NHolidayArray                        // 할당된 Array 길이
)
{
    long i, j, k;
    long** Holidays = (long**)malloc(sizeof(long*) * max(1, (End_YYYY - Start_YYYY + 1)));          // 메모리할당1
    long* nholidays = (long*)malloc(sizeof(long) * max(1, (End_YYYY - Start_YYYY + 1)));            // 메모리할당2
    long n = 0;
    long nh = 0;
    long EasterMonday;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        Holidays[i] = (long*)malloc(sizeof(long) * 15);
        if (Start_YYYY + i < LunarDateKoreanHardCodeYear)
        {
            EasterMonday = RebirthDayPlus1(Start_YYYY + i);
            Mapping_GBPHoliday(Start_YYYY + i, Holidays[i], EasterMonday);
            nholidays[i] = 8;
        }
        else
        {
            Mapping_GBPHoliday(Start_YYYY + i, Holidays[i], 0);
            nholidays[i] = 6;
        }
        bubble_sort_date(Holidays[i], nholidays[i], 1);
        n += nholidays[i];
    }

    NHolidayArray = n;
    long* ResultArray = (long*)malloc(sizeof(long) * max(1, n));                                    // 리턴용할당
    k = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        for (j = 0; j < nholidays[i]; j++)
        {
            ResultArray[k] = Holidays[i][j];
            k += 1;
        }
    }
    bubble_sort_date(ResultArray, NHolidayArray, 1);

    for (i = 0; i < max(1, (End_YYYY - Start_YYYY + 1)); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2

    return ResultArray;
}

// EUR Holiday Mapping
void Mapping_EUR_Holiday(
    long YYYY,                  // 연도 
    long* HolidayArray         // 미리 할당된 Array(7개
)
{
    long TempDate;
    long Jan01 = YYYY * 10000 + 101;
    long RebirthMinus2;
    long RebirthPlus1;

    if (YYYY < LunarDateKoreanHardCodeYear) RebirthMinus2 = RebirthDayMinus2(YYYY);     // 부활절 쉼
    else RebirthMinus2 = Jan01;

    if (YYYY < LunarDateKoreanHardCodeYear) RebirthPlus1= RebirthDayPlus1(YYYY);     // 부활절 쉼
    else RebirthPlus1 = Jan01;

    long May01 = YYYY * 10000 + 101;
    long Christmas = YYYY * 10000 + 1225;
    long ChristmasPlus1 = YYYY * 10000 + 1226;

    HolidayArray[0] = Jan01;
    HolidayArray[1] = RebirthMinus2;
    HolidayArray[2] = RebirthPlus1;
    HolidayArray[3] = RebirthMinus2;
    HolidayArray[4] = May01;
    HolidayArray[5] = Christmas;
    HolidayArray[6] = ChristmasPlus1;
}

// EUR Holiday Array를 Malloc하는 함수
long* Malloc_EURHolidayArray(
    long Start_YYYY,                            // 시작 연도
    long End_YYYY,                              // 종료 연도
    long& NHolidayArray                        // 할당된 Array 길이
)
{
    long i, j, k;
    long** Holidays = (long**)malloc(sizeof(long*) * max(1, (End_YYYY - Start_YYYY + 1)));          // 메모리할당1
    long* nholidays = (long*)malloc(sizeof(long) * max(1, (End_YYYY - Start_YYYY + 1)));            // 메모리할당2
    long n = 0;
    long nh = 0;

    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        Holidays[i] = (long*)malloc(sizeof(long) * 15);
        Mapping_EUR_Holiday(Start_YYYY + i, Holidays[i]);
        nholidays[i] = 7;
        bubble_sort_date(Holidays[i], nholidays[i], 1);
        n += nholidays[i];
    }

    NHolidayArray = n;
    long* ResultArray = (long*)malloc(sizeof(long) * max(1, n));                                    // 리턴용할당
    k = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        for (j = 0; j < nholidays[i]; j++)
        {
            ResultArray[k] = Holidays[i][j];
            k += 1;
        }
    }
    bubble_sort_date(ResultArray, NHolidayArray, 1);

    for (i = 0; i < max(1, (End_YYYY - Start_YYYY + 1)); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2

    return ResultArray;
}

// JPY Holiday Mapping
void Mapping_JPY_Holiday(
    long YYYY,                  // 연도 
    long* HolidayArray          // 미리 할당된 Array(14개
)
{
    long TempDate;
    long Jan01 = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 101);
    long SeiJinNoHee = Nth_Date(YYYY, 1, 2, 2);        // 1월 2번째 월요일
    long KenKoKuKynenHee = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 211);
    long TennoTanjobi = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 223);
    long Showhanohee = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 429);
    long KenpoKinenbee = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 503);
    long Midorinohee = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 504);
    long Kodomonohee = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 505);
    long Uminohee = Nth_Date(YYYY, 7, 3, 2);        // 7월 3번째 월요일
    long Yamanohee = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 811);
    long Keronohee = Nth_Date(YYYY, 9, 3, 2);        // 9월 3번째 월요일
    long Sportsnohee = Nth_Date(YYYY, 10, 2, 2);        // 9월 3번째 월요일
    if (YYYY == 2020) Sportsnohee = 20200724;
    long Bunkanohee = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 1103);
    long KinroKanshyanohee = FixedHoliday_YYYYMMDD_GBP(YYYY * 10000 + 1123);

    HolidayArray[0] = Jan01;
    HolidayArray[1] = SeiJinNoHee;
    HolidayArray[2] = KenKoKuKynenHee;
    HolidayArray[3] = TennoTanjobi;
    HolidayArray[4] = Showhanohee;
    HolidayArray[5] = KenpoKinenbee;
    HolidayArray[6] = Midorinohee;
    HolidayArray[7] = Kodomonohee;
    HolidayArray[8] = Uminohee;
    HolidayArray[9] = Yamanohee;
    HolidayArray[10] = Keronohee;
    HolidayArray[11] = Sportsnohee;
    HolidayArray[12] = Bunkanohee;
    HolidayArray[13] = KinroKanshyanohee;
}

// JPY Holiday Array를 Malloc하는 함수
long* Malloc_JPYHolidayArray(
    long Start_YYYY,                            // 시작 연도
    long End_YYYY,                              // 종료 연도
    long& NHolidayArray                        // 할당된 Array 길이
)
{
    long i, j, k;
    long** Holidays = (long**)malloc(sizeof(long*) * max(1, (End_YYYY - Start_YYYY + 1)));          // 메모리할당1
    long* nholidays = (long*)malloc(sizeof(long) * max(1, (End_YYYY - Start_YYYY + 1)));            // 메모리할당2
    long n = 0;
    long nh = 0;
    long EasterMonday;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        Holidays[i] = (long*)malloc(sizeof(long) * 15);
        Mapping_JPY_Holiday(Start_YYYY + i, Holidays[i]);
        nholidays[i] = 14;
        bubble_sort_date(Holidays[i], nholidays[i], 1);
        n += nholidays[i];
    }

    NHolidayArray = n;
    long* ResultArray = (long*)malloc(sizeof(long) * max(1, n));                                    // 리턴용할당
    k = 0;
    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++)
    {
        for (j = 0; j < nholidays[i]; j++)
        {
            ResultArray[k] = Holidays[i][j];
            k += 1;
        }
    }
    bubble_sort_date(ResultArray, NHolidayArray, 1);

    for (i = 0; i < max(1, (End_YYYY - Start_YYYY + 1)); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2

    return ResultArray;
}

// Counting HolidayNumber From Start YYYY to EndYYYY 
DLLEXPORT(long) Number_Holiday(
    long StartYYYY,         // 시작연도
    long EndYYYY,           // 종료연도
    long NationFlag         // 0: KRW한국, 1: USD미국, 2: GBP영국
)
{
    if (NationFlag < 10)
    {
        // 시작연도 ~ 종료연도까지 공휴일 개수 세기
        long i;
        long k;
        long NHoliday = 0;
        long* Holidays;

        if (NationFlag == 0) Holidays = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 1) Holidays = Malloc_USHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 3) Holidays = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 4) Holidays = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 5) Holidays = Malloc_EURHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 6) Holidays = Malloc_JPYHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else Holidays = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, NHoliday);

        long N = 0;
        long* UniqueArray = MallocUnique(Holidays, NHoliday, N);
        free(UniqueArray);
        free(Holidays);
        return N;
    }
    else if (NationFlag >= 10 && NationFlag < 100)
    {
        long Nation1 = (long)(NationFlag / 10);
        long Nation2 = NationFlag - Nation1 * 10;
        return Number_Holiday(StartYYYY, EndYYYY, Nation1) + Number_Holiday(StartYYYY, EndYYYY, Nation2);
    }
    else
    {
        return 0;
    }
}

// Put Holiday to ResultArray
DLLEXPORT(long) Mapping_Holiday_ExcelType(
    long StartYYYY,     // 시작연도
    long EndYYYY,       // 종료연도
    long NationFlag,    // 국가Flag 0한국 1미국 2영국 3NYSE 4NYMEX 5GBP 6JPY
    long NResultArray,  // 배열 개수 Number_Holiday에서 확인
    long* ResultArray   // Holiday 들어가는 배열
)
{
    // 시작연도 ~ 종료연도까지 공휴일을 ResultArray에 집어넣는다.
    long i;
    long k;
    long NHoliday = 0;
    long* Holidays;
    if (NationFlag < 10)
    {
        if (NationFlag == 0) Holidays = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 1) Holidays = Malloc_USHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 3) Holidays = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 4) Holidays = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 5) Holidays = Malloc_EURHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 6) Holidays = Malloc_JPYHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else Holidays = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, NHoliday);
    }
    else
    {
        long* Holidays1;
        long* Holidays2;
        long N1 = 0;
        long N2 = 0;
        long Nation1 = (long)(NationFlag / 10);
        long Nation2 = NationFlag - Nation1 * 10;
        if (Nation1 == 0) Holidays1 = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 1) Holidays1 = Malloc_USHolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 3) Holidays1 = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 4) Holidays1 = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 5) Holidays1 = Malloc_EURHolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 6) Holidays1 = Malloc_JPYHolidayArray(StartYYYY, EndYYYY, N1);
        else Holidays1 = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, N1);

        if (Nation2 == 0) Holidays2 = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 1) Holidays2 = Malloc_USHolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 3) Holidays2 = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 4) Holidays2 = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 5) Holidays2 = Malloc_EURHolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 6) Holidays2 = Malloc_JPYHolidayArray(StartYYYY, EndYYYY, N2);
        else Holidays2 = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, N2);

        NHoliday = N1 + N2;
        Holidays = (long*)malloc(sizeof(long) * (N1 + N2));
        for (i = 0; i < N1; i++)
        {
            Holidays[i] = Holidays1[i];
        }
        for (i = 0; i < N2; i++)
        {
            Holidays[i + N1] = Holidays2[i];
        }
        free(Holidays1);
        free(Holidays2);
    }

    long N = 0;
    long* UniqueArray = MallocUnique(Holidays, NHoliday, N);
    for (i = 0; i < N; i++)
    {
        ResultArray[i] = CDateToExcelDate(UniqueArray[i]);
    }
    free(UniqueArray);      // 할당제거 1
    free(Holidays);         // 할당제거 2
    return 1;
}

DLLEXPORT(long) Mapping_Holiday_CType(
    long StartYYYY,     // 시작연도
    long EndYYYY,       // 종료연도
    long NationFlag,    // 국가Flag 0한국 1미국 2영국 3NYSE 4NYMEX 5GBP 6JPY
    long NResultArray,  // 배열 개수 Number_Holiday에서 확인
    long* ResultArray   // Holiday 들어가는 배열
)
{
    // 시작연도 ~ 종료연도까지 공휴일을 ResultArray에 집어넣는다.
    long i;
    long k;
    long NHoliday = 0;
    long* Holidays;
    if (NationFlag < 10)
    {
        if (NationFlag == 0) Holidays = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 1) Holidays = Malloc_USHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 3) Holidays = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 4) Holidays = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 5) Holidays = Malloc_EURHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else if (NationFlag == 6) Holidays = Malloc_JPYHolidayArray(StartYYYY, EndYYYY, NHoliday);
        else Holidays = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, NHoliday);
    }
    else
    {
        long* Holidays1;
        long* Holidays2;
        long N1 = 0;
        long N2 = 0;
        long Nation1 = (long)(NationFlag / 10);
        long Nation2 = NationFlag - Nation1 * 10;
        if (Nation1 == 0) Holidays1 = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 1) Holidays1 = Malloc_USHolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 3) Holidays1 = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 4) Holidays1 = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 5) Holidays1 = Malloc_EURHolidayArray(StartYYYY, EndYYYY, N1);
        else if (Nation1 == 6) Holidays1 = Malloc_JPYHolidayArray(StartYYYY, EndYYYY, N1);
        else Holidays1 = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, N1);

        if (Nation2 == 0) Holidays2 = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 1) Holidays2 = Malloc_USHolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 3) Holidays2 = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 4) Holidays2 = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 5) Holidays2 = Malloc_EURHolidayArray(StartYYYY, EndYYYY, N2);
        else if (Nation2 == 6) Holidays2 = Malloc_JPYHolidayArray(StartYYYY, EndYYYY, N2);
        else Holidays2 = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, N2);

        NHoliday = N1 + N2;
        Holidays = (long*)malloc(sizeof(long) * (N1 + N2));
        for (i = 0; i < N1; i++)
        {
            Holidays[i] = Holidays1[i];
        }
        for (i = 0; i < N2; i++)
        {
            Holidays[i + N1] = Holidays2[i];
        }
        free(Holidays1);
        free(Holidays2);
        bubble_sort_date(Holidays, NHoliday, 1);
    }

    long N = 0;
    long* UniqueArray = MallocUnique(Holidays, NHoliday, N);
    for (i = 0; i < N; i++)
    {
        ResultArray[i] = UniqueArray[i];
    }
    free(UniqueArray);      // 할당제거 1
    free(Holidays);         // 할당제거 2
    return 1;
}

DLLEXPORT(long) ParseBusinessDateIfHoliday(long YYYYMMDD, long* Holidays, long NHolidays)
{
    if (YYYYMMDD < 19000101) YYYYMMDD = ExcelDateToCDate(YYYYMMDD);
    // 만약 Holiday라면 WorkingDate 날짜를 Return한다.
    long i;
    for (i = 0; i < NHolidays; i++)
    {
        if (Holidays[i] < 19000101)
        {
            Holidays[i] = ExcelDateToCDate(Holidays[i]);
        }
    }

    long ResultYYYYMMDD;

    long TempExcelDate;
    long TempYYYYMMDD;

    long ExcelDate = CDateToExcelDate(YYYYMMDD);
    long IsHolidayFlag = 0;
    long IsSaturSundayFlag = 0;
    long MOD7 = ExcelDate % 7;
    if (MOD7 == 0 || MOD7 == 1) IsSaturSundayFlag = 1;
    if (isin_Longtype(YYYYMMDD, Holidays, NHolidays)) IsHolidayFlag = 1;

    if (IsSaturSundayFlag == 0 && IsHolidayFlag == 0)
    {
        ResultYYYYMMDD = YYYYMMDD;
    }
    else
    {
        for (i = 0; i < 100; i++)
        {
            TempExcelDate = ExcelDate + 1 + i;
            TempYYYYMMDD = ExcelDateToCDate(TempExcelDate);
            MOD7 = TempExcelDate % 7;

            if (MOD7 == 0 || MOD7 == 1) IsSaturSundayFlag = 1;
            else IsSaturSundayFlag = 0;

            if (isin_Longtype(TempYYYYMMDD, Holidays, NHolidays)) IsHolidayFlag = 1;
            else IsHolidayFlag = 0;

            if (IsSaturSundayFlag == 0 && IsHolidayFlag == 0)
            {
                ResultYYYYMMDD = TempYYYYMMDD;
                break;
            }
        }
    }
    return ResultYYYYMMDD;
}

DLLEXPORT(long) NBusinessCountFromEndToPay(long EndYYYYMMDD, long PayYYYYMMDD, long* Holidays, long NHolidays, long ModifiedFollowing, long* ResultEndDate)
{
    ///////////////////////////////////////////////////
    // Business Date From ENDYYYYMMDD To PayYYYYMMDD //
    // or From NBD From StartYYYYMMDD to PayYYYYMMDD //
    ///////////////////////////////////////////////////

    if (EndYYYYMMDD < 19000101) EndYYYYMMDD = ExcelDateToCDate(EndYYYYMMDD);
    if (PayYYYYMMDD < 19000101) PayYYYYMMDD = ExcelDateToCDate(PayYYYYMMDD);

    if (EndYYYYMMDD > PayYYYYMMDD)
    {
        return -NBusinessCountFromEndToPay(PayYYYYMMDD, EndYYYYMMDD, Holidays, NHolidays, ModifiedFollowing, ResultEndDate);
    }
    else if (EndYYYYMMDD == PayYYYYMMDD)
    {
        *ResultEndDate = EndYYYYMMDD;
        return 0;
    }

    long i;
    for (i = 0; i < NHolidays; i++)
    {
        if (Holidays[i] < 19000101)
        {
            Holidays[i] = ExcelDateToCDate(Holidays[i]);
        }
    }
    long nbd;
    long TempExcelDate;
    long TempDate;
    long MOD7;
    long IsSaturSundayFlag;
    long IsHolidayFlag;

    long EndYYYY = EndYYYYMMDD / 10000;
    long EndMM = (EndYYYYMMDD - EndYYYY * 10000) / 100;
    long EndDD = (EndYYYYMMDD - EndYYYY * 10000 - EndMM * 100);
    long EndExcelDate = CDateToExcelDate(EndYYYYMMDD);

    long PayYYYY = PayYYYYMMDD / 10000;
    long PayMM = (PayYYYYMMDD - PayYYYY * 10000) / 100;
    long PayDD = (PayYYYYMMDD - PayYYYY * 10000 - PayMM * 100);
    long PayExcelDate = CDateToExcelDate(PayYYYYMMDD);

    long TempYYYY;
    long TempMM;
    long TempDD;
    long LastBD;

    long PrevTempMM, PrevTempDD;
    if (EndDD == PayDD)
    {
        *ResultEndDate = PayYYYYMMDD;
        nbd = 0;
    }
    else
    {
        nbd = 0;
        for (i = 0; i < 30; i++)
        {
            ///////////////////////////////////
            // PayDate로부터 앞으로 땡겨서   //
            // EndDate까지 BDate를 계산      //
            ///////////////////////////////////
            TempExcelDate = PayExcelDate - 1 - i;
            TempDate = ExcelDateToCDate(TempExcelDate);

            TempYYYY = TempDate / 10000;
            TempMM = (TempDate - TempYYYY * 10000) / 100;
            TempDD = (TempDate - TempYYYY * 10000 - TempMM * 100);

            MOD7 = TempExcelDate % 7;

            if (MOD7 == 0 || MOD7 == 1) IsSaturSundayFlag = 1;
            else IsSaturSundayFlag = 0;

            if (isin_Longtype(TempDate, Holidays, NHolidays)) IsHolidayFlag = 1;
            else IsHolidayFlag = 0;

            if (IsSaturSundayFlag == 0 && IsHolidayFlag == 0)
            {
                nbd += 1;
            }

            if (i > 0)
            {
                if (PrevTempMM > TempMM || (PrevTempMM == 1 && TempMM == 12))
                {
                    ///////////////////////////////
                    // 월이 전달로 넘어가는 경우 // 
                    // EndDate의 ModifiedFollow  //
                    ///////////////////////////////

                    if (ModifiedFollowing == 1)
                    {
                        LastBD = LastBusinessDate(TempYYYY * 100 + TempMM, NHolidays, Holidays);
                        if (EndDD > LastBD - (long)(LastBD / 100) * 100)
                        {
                            EndDD = LastBD - (long)(LastBD / 100) * 100;
                        }
                    }
                }
            }

            if (TempDD == EndDD)
            {
                // Day가 동일하면 종료
                break;
            }

            PrevTempMM = TempMM;
        }

        *ResultEndDate = ParseBusinessDateIfHoliday(TempYYYY * 10000 + TempMM * 100 + EndDD, Holidays, NHolidays);
    }
    return nbd;
}

long isweekendflag(long ExlDate)
{
    // 나머지 1이면 일요일, 2이면 월요일, 3이면 화요일, 4이면 수요일, 5이면 목요일, 6이면 금요일, 0이면 토요일
    long MOD7;
    if (ExlDate > 0)
    {
        MOD7 = ExlDate % 7;
        if (MOD7 == 1 || MOD7 == 0) return 1;
    }
    return 0;
}

long* Malloc_CpnDate_Holiday(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD, long ModifiedFollowing = 1)
{
    long i, j;
    long LastBusiDay;
    long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
    long PriceMM = (long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100;

    long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
    long SwapMatMM = (long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100;

    long n = ((SwapMat_YYYYMMDD / 10000 - PriceDateYYYYMMDD / 10000) + 2) * AnnCpnOneYear;
    long narray = 0;
    long CpnDate;
    long m;
    if (AnnCpnOneYear == 0)
    {
        narray = 1;
        n = 1;
    }
    else
    {
        m = max(1, 12 / AnnCpnOneYear);
        for (i = 0; i < n; i++)
        {
            if (i == 0) CpnDate = SwapMat_YYYYMMDD;
            else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i * m);
            if (DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7)
            {
                FirstCpnDate = CpnDate;
                break;
            }
            if (CpnDate <= PriceDateYYYYMMDD) break;
            narray++;
        }
    }

    long* ResultCpnDate = (long*)malloc(sizeof(long) * narray);
    long CpnDateExcel, CpnDateTemp;
    long MOD7;
    long SaturSundayFlag;
    long PrevDate;
    for (i = 0; i < n; i++)
    {
        if (i == 0) CpnDate = SwapMat_YYYYMMDD;
        else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i * m);

        if (CpnDate <= PriceDateYYYYMMDD || DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7) break;
        else
        {
            CpnDateExcel = CDateToExcelDate(CpnDate);
            MOD7 = CpnDateExcel % 7;
            if ((MOD7 == 1 || MOD7 == 0) || isin_Longtype(CpnDate, HolidayYYYYMMDD, NHoliday)) SaturSundayFlag = 1;
            else SaturSundayFlag = 0;

            if (SaturSundayFlag == 0)
            {
                ResultCpnDate[narray - 1 - i] = CpnDate;
            }
            else
            {
                if (ModifiedFollowing == 1)
                {
                    // Forward End 날짜가 토요일 또는 일요일의 경우 날짜 미룸
                    for (j = 1; j <= 7; j++)
                    {
                        CpnDateExcel += 1;
                        MOD7 = CpnDateExcel % 7;
                        CpnDateTemp = ExcelDateToCDate(CpnDateExcel);
                        if ((MOD7 != 1 && MOD7 != 0) && !isin_Longtype(CpnDateTemp, HolidayYYYYMMDD, NHoliday))
                        {
                            PrevDate = ExcelDateToCDate(CpnDateExcel);
                            break;
                        }
                    }
                    ResultCpnDate[narray - 1 - i] = min(LastBusinessDate((long)(CpnDate / 100), NHoliday, HolidayYYYYMMDD), PrevDate);
                }
                else
                {
                    // Forward End 날짜가 토요일 또는 일요일의 경우 날짜 미룸
                    for (j = 1; j <= 7; j++)
                    {
                        CpnDateExcel += 1;
                        MOD7 = CpnDateExcel % 7;
                        CpnDateTemp = ExcelDateToCDate(CpnDateExcel);
                        if ((MOD7 != 1 && MOD7 != 0) && !isin_Longtype(CpnDateTemp, HolidayYYYYMMDD, NHoliday))
                        {
                            CpnDate = ExcelDateToCDate(CpnDateExcel);
                            break;
                        }
                    }
                    ResultCpnDate[narray - 1 - i] = CpnDate;
                }
            }
        }
    }
    lenArray = narray;
    if (AnnCpnOneYear == 1 && PriceMM != SwapMatMM)
    {
        long TargetDateYYYYMMDD = ResultCpnDate[0];
        long TargetDateYYYY;
        long TargetDateMM;
        for (i = 1; i <= 12; i++)
        {
            TargetDateYYYYMMDD = EDate_Cpp(TargetDateYYYYMMDD, -1);
            TargetDateYYYY = (long)TargetDateYYYYMMDD / 10000;
            TargetDateMM = (long)(TargetDateYYYYMMDD - TargetDateYYYY * 10000) / 100;
            if (TargetDateYYYY == PriceYYYY && TargetDateMM == PriceMM)
            {
                FirstCpnDate = TargetDateYYYYMMDD;
                break;
            }
        }
    }
    return ResultCpnDate;
}

DLLEXPORT(long) Number_of_Coupons(
    long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
    long PriceDate,                 // 평가일
    long SwapMat,                   // 스왑 만기
    long AnnCpnOneYear,             // 연 스왑쿠폰지급수
    long HolidayUseFlag,            // 공휴일 입력 사용 Flag
    long NHoliday,                  // 공휴일 개수
    long* Holidays,                 // 공휴일
    long ModifiedFollowingFlag
)
{
    long i;
    long PriceDateYYYYMMDD;
    long SwapMat_YYYYMMDD;

    if (PriceDate < 19000000) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDate);          // 평가일
    else PriceDateYYYYMMDD = PriceDate;

    if (SwapMat < 19000000) SwapMat_YYYYMMDD = ExcelDateToCDate(SwapMat);             // 스왑 만기
    else SwapMat_YYYYMMDD = SwapMat;

    if (DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) > 366 * 2) ProductType = 1;
    if (ProductType == 0) return 1;

    // 에러처리
    if (PriceDateYYYYMMDD <= 19000101 || PriceDateYYYYMMDD >= 999990101)  return -1;
    if (SwapMat_YYYYMMDD <= 19000101 || SwapMat_YYYYMMDD >= 999990101) return -1;
    if (AnnCpnOneYear > 6) return -1;

    long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1, NHoliday));
    for (i = 0; i < NHoliday; i++)
    {
        if (Holidays[i] < 19000000 && Holidays[i] >= 0) HolidayYYYYMMDD[i] = ExcelDateToCDate(Holidays[i]);
        else HolidayYYYYMMDD[i] = Holidays[i];
    }

    long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
    long PriceMM = (long)((long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100);
    long PriceDD = (PriceDateYYYYMMDD - PriceYYYY * 10000 - PriceMM * 100);

    long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
    long SwapMatMM = (long)((long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100);
    long SwapMatDD = (SwapMat_YYYYMMDD - SwapMatYYYY * 10000 - SwapMatMM * 100);

    long n;
    long TempYYYYMMDD = PriceDateYYYYMMDD;
    long TempYYYYMMDD2 = SwapMat_YYYYMMDD;
    long TempYYYY = 0;
    long TempMM = 0;
    long ncpn = 0;
    long* CpnDate;

    if (DayCountAtoB(PriceDateYYYYMMDD, SwapMat_YYYYMMDD) <= 62)
    {
        // 2개월 미만의 경우 쿠폰 한번지급으로 고정
        free(HolidayYYYYMMDD);
        return 1;
    }
    else if (SwapMatYYYY - PriceYYYY <= 1)
    {
        // 1년 미만 만기의 경우 만기까지 몇개월 남았는지 카운트
        n = 0;
        for (i = 0; i < 24; i++)
        {
            TempYYYYMMDD = EDate_Cpp(PriceDateYYYYMMDD, i + 1);
            TempYYYY = (long)TempYYYYMMDD / 10000;
            TempMM = (long)(TempYYYYMMDD - TempYYYY * 10000) / 100;
            n = i + 1;
            if (TempYYYY == SwapMatYYYY && TempMM == SwapMatMM)
            {
                break;
            }
        }

        if (n < 6)
        {
            // 만기까지 6개월 미만으로 남았으면 쿠폰 1번 지급 끝
            // (1년에 4번을 초과하여 지급하는 경우는 없다고 가정)
            free(HolidayYYYYMMDD);
            return 1;
        }
        else
        {
            if (PriceDD >= 24 && SwapMatDD < 7)
            {
                NBusinessCountFromEndToPay(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, NHoliday, ModifiedFollowingFlag, &TempYYYYMMDD2);
                SwapMat_YYYYMMDD = TempYYYYMMDD2;
            }

            if (HolidayUseFlag == 1) CpnDate = Malloc_CpnDate_Holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD, ModifiedFollowingFlag);
            else CpnDate = Malloc_CpnDate_Holiday(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, 0, HolidayYYYYMMDD, ModifiedFollowingFlag);

            free(CpnDate);
            free(HolidayYYYYMMDD);
            return ncpn;
        }
    }
    else
    {
        long* CpnDate;
        long TempYYYYMMDD = PriceDateYYYYMMDD;
        long TempDateExcelType;
        long StartDateYYYYMMDD = PriceDateYYYYMMDD;
        long StartYYYYMM = (long)StartDateYYYYMMDD / 100;
        long StartDD = StartDateYYYYMMDD - StartYYYYMM * 100;
        long EndYYYYMM = (long)SwapMat_YYYYMMDD / 100;
        long EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD;
        if (PriceDD >= 24 && SwapMatDD < 7)
        {
            NBusinessCountFromEndToPay(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, NHoliday, ModifiedFollowingFlag, &TempYYYYMMDD2);
            EndDateYYYYMMDD = TempYYYYMMDD2;
        }

        if (HolidayUseFlag == 1) CpnDate = Malloc_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD, ModifiedFollowingFlag);
        else CpnDate = Malloc_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, 0, HolidayYYYYMMDD, ModifiedFollowingFlag);

        free(CpnDate);
        free(HolidayYYYYMMDD);
        return ncpn;
    }
}

DLLEXPORT(long) MappingCouponDates(
    long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
    long PriceDate,                 // 평가일
    long StartDate,                 // 시작일
    long SwapMat,                   // 스왑 만기
    long NBDayFromEndDate,          // N영업일 뒤 지급(만약 -1일 경우 EndDate To PayDate 자동 계산)
    long AnnCpnOneYear,             // 연 스왑쿠폰지급수
    long HolidayUseFlag,            // 공휴일 입력 사용 Flag
    long NHoliday,                  // 공휴일 개수
    long* Holidays,                 // 공휴일
    long ModifiedFollowingFlag,     
    long NumberCoupon,
    long* ResultForwardStart,
    long* ResultForwardEnd,
    long* ResultPayDate
)
{
    long i;
    long j;
    long n;
    long PriceDateYYYYMMDD;
    long StartDateYYYYMMDD;
    long SwapMat_YYYYMMDD;
    long ResultIsExcelType;

    if (PriceDate < 19000000) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDate);
    else PriceDateYYYYMMDD = PriceDate;

    if (StartDate < 19000000) StartDateYYYYMMDD = ExcelDateToCDate(StartDate);
    else StartDateYYYYMMDD = StartDate;

    if (SwapMat < 19000000) SwapMat_YYYYMMDD = ExcelDateToCDate(SwapMat);
    else SwapMat_YYYYMMDD = SwapMat;

    if (PriceDate < 19000000 && StartDate < 19000000 && SwapMat < 19000000) ResultIsExcelType = 1;
    else ResultIsExcelType = 0;

    long PayDateExcelType, PayDateYYYYMMDD, EndDateYYYYMMDD, EndDateExcel, MOD7;
    
    long StartYYYYMM = (long)StartDateYYYYMMDD / 100;
    long StartDD = StartDateYYYYMMDD - StartYYYYMM * 100;
    long SwapMat_DD = SwapMat_YYYYMMDD - ((long)(SwapMat_YYYYMMDD / 100)) * 100;

    long ncpn;
    long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1, NHoliday));
    for (i = 0; i < NHoliday; i++)
    {
        if (Holidays[i] < 19000000) HolidayYYYYMMDD[i] = ExcelDateToCDate(Holidays[i]);
        else HolidayYYYYMMDD[i] = Holidays[i];
    }

    if (NumberCoupon < 0) return -1;
    if (NumberCoupon <= 1)
    {
        if (NBDayFromEndDate == 0)
        {
            if (ResultIsExcelType == 1)
            {
                ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                ResultForwardEnd[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
                ResultPayDate[0] = ResultForwardEnd[0];
            }
            else
            {
                ResultForwardStart[0] = StartDateYYYYMMDD;
                ResultForwardEnd[0] = SwapMat_YYYYMMDD;
                ResultPayDate[0] = ResultForwardEnd[0];
            }
        }
        else if (NBDayFromEndDate < 0)
        {
            // NBD Auto계산
            NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, NHoliday, ModifiedFollowingFlag, &EndDateYYYYMMDD);
            if (ResultIsExcelType == 1)
            {
                ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                ResultForwardEnd[0] = CDateToExcelDate(EndDateYYYYMMDD);
                ResultPayDate[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
            }
            else
            {
                ResultForwardStart[0] = StartDateYYYYMMDD;
                ResultForwardEnd[0] = EndDateYYYYMMDD;
                ResultPayDate[0] = SwapMat_YYYYMMDD;
            }
        }
        else
        {
            if (SwapMat_DD < 7 && StartDD >= 24)
            {
                //////////////////////////////////////////
                // If PayDate is next month of EndDate  //
                //////////////////////////////////////////
                NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, NHoliday, ModifiedFollowingFlag, &EndDateYYYYMMDD);
                if (ResultIsExcelType == 1)
                {
                    ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                    ResultForwardEnd[0] = CDateToExcelDate(EndDateYYYYMMDD);
                    ResultPayDate[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
                }
                else
                {
                    ResultForwardStart[0] = StartDateYYYYMMDD;
                    ResultForwardEnd[0] = EndDateYYYYMMDD;
                    ResultPayDate[0] = SwapMat_YYYYMMDD;
                }
            }
            else
            {
                n = 0;
                if (ResultIsExcelType == 1) ResultForwardStart[0] = StartDate;
                else ResultForwardStart[0] = StartDateYYYYMMDD;

                // PayDate결정
                PayDateYYYYMMDD = SwapMat_YYYYMMDD;
                PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
                MOD7 = PayDateExcelType % 7;
                for (i = 1; i < 35; i++)
                {
                    if (isweekendflag(PayDateExcelType) || isin_Longtype(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                    {
                        // 휴일이면 n+=1
                        PayDateExcelType += 1;
                        PayDateYYYYMMDD = ExcelDateToCDate(PayDateExcelType);
                    }
                    else
                    {
                        break;
                    }
                }

                if (ResultIsExcelType == 1) ResultPayDate[0] = PayDateExcelType;
                else ResultPayDate[0] = PayDateYYYYMMDD;

                EndDateYYYYMMDD = PayDateYYYYMMDD;
                EndDateExcel = PayDateExcelType;
                for (i = 1; i < 35; i++)
                {
                    EndDateExcel = EndDateExcel - 1;
                    EndDateYYYYMMDD = ExcelDateToCDate(EndDateExcel);
                    MOD7 = EndDateExcel % 7;
                    if ((MOD7 != 1 && MOD7 != 0) && !isin_Longtype(EndDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                    {
                        // 영업일이면 n+=1
                        n += 1;
                    }

                    if (n == NBDayFromEndDate)
                    {
                        if (ResultIsExcelType == 1) ResultForwardEnd[0] = EndDateExcel;
                        else ResultForwardEnd[0] = EndDateYYYYMMDD;
                        break;
                    }
                }
            }
        }
    }
    else
    {
        long* CpnDate;
        long TempYYYYMMDD = PriceDateYYYYMMDD;
        long TempDateExcelType;
        long EndYYYYMM = (long)SwapMat_YYYYMMDD / 100;
        if (SwapMat_DD < 7 && StartDD >= 24 || NBDayFromEndDate == -1)
        {
            //////////////////////////////////////////
            // If PayDate is next month of EndDate  //
            //////////////////////////////////////////
            NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDD, NHoliday, ModifiedFollowingFlag, &EndDateYYYYMMDD);
        }
        else
        {
            EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD;
        }

        if (HolidayUseFlag == 1) CpnDate = Malloc_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD, ModifiedFollowingFlag);
        else CpnDate = Malloc_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, 0, HolidayYYYYMMDD, ModifiedFollowingFlag);

        for (i = 0; i < min(NumberCoupon, ncpn); i++)
        {
            if (i == 0)
            {
                if (ResultIsExcelType == 1)
                {
                    ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                    TempDateExcelType = CDateToExcelDate(CpnDate[0]);
                    ResultForwardEnd[0] = TempDateExcelType;
                }
                else
                {
                    ResultForwardStart[0] = StartDateYYYYMMDD;
                    ResultForwardEnd[0] = CpnDate[0];
                }
            }
            else
            {
                if (ResultIsExcelType == 1)
                {
                    ResultForwardStart[i] = CDateToExcelDate(CpnDate[i - 1]);
                    TempDateExcelType = CDateToExcelDate(CpnDate[i]);
                    ResultForwardEnd[i] = TempDateExcelType;
                }
                else
                {
                    ResultForwardStart[i] = CpnDate[i - 1];
                    ResultForwardEnd[i] = CpnDate[i];
                }
            }

            if (NBDayFromEndDate == 0)
            {
                ResultPayDate[i] = ResultForwardEnd[i];
            }
            else
            {
                n = 0;
                for (j = 1; j < 35; j++)
                {
                    PayDateYYYYMMDD = DayPlus(CpnDate[i], j);
                    PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
                    MOD7 = PayDateExcelType % 7;
                    if ((MOD7 != 1 && MOD7 != 0) && !isin_Longtype(PayDateYYYYMMDD, HolidayYYYYMMDD, NHoliday))
                    {
                        // 영업일이면 n+=1
                        n += 1;
                    }

                    if (n == NBDayFromEndDate)
                    {
                        if (ResultIsExcelType == 1) ResultPayDate[i] = PayDateExcelType;
                        else ResultPayDate[i] = PayDateYYYYMMDD;
                        break;
                    }
                }
            }
        }

        if (CpnDate) free(CpnDate);
    }
    if (HolidayYYYYMMDD) free(HolidayYYYYMMDD);
    return 1;
}

DLLEXPORT(long) MappingCouponDates2(
    long ProductType,               // 상품종류 0이면 Futures, 1이면 Swap
    long PriceDate,                 // 평가일
    long StartDate,                 // 시작일
    long SwapMat,                   // 스왑 만기
    long NBDayFromEndDate,          // N영업일 뒤 지급(만약 -1일 경우 EndDate To PayDate 자동 계산)
    long AnnCpnOneYear,             // 연 스왑쿠폰지급수
    long HolidayUseFlag,            // 공휴일 입력 사용 Flag
    long NHoliday,                  // Fixing 공휴일 개수
    long* Holidays,                 // Fixing 공휴일
    long NHolidayPayDate,           // Payment 공휴일 개수
    long* HolidaysPayDate,          // Payment 공휴일
    long ModifiedFollowingFlag,
    long NumberCoupon,
    long* ResultForwardStart,
    long* ResultForwardEnd,
    long* ResultPayDate
)
{
    long i;
    long j;
    long n;
    long PriceDateYYYYMMDD;
    long StartDateYYYYMMDD;
    long SwapMat_YYYYMMDD;
    long ResultIsExcelType;

    if (PriceDate < 19000000) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDate);
    else PriceDateYYYYMMDD = PriceDate;

    if (StartDate < 19000000) StartDateYYYYMMDD = ExcelDateToCDate(StartDate);
    else StartDateYYYYMMDD = StartDate;

    if (SwapMat < 19000000) SwapMat_YYYYMMDD = ExcelDateToCDate(SwapMat);
    else SwapMat_YYYYMMDD = SwapMat;

    if (PriceDate < 19000000 && StartDate < 19000000 && SwapMat < 19000000) ResultIsExcelType = 1;
    else ResultIsExcelType = 0;

    long PayDateExcelType, PayDateYYYYMMDD, EndDateYYYYMMDD, EndDateExcel, MOD7;

    long StartYYYYMM = (long)StartDateYYYYMMDD / 100;
    long StartDD = StartDateYYYYMMDD - StartYYYYMM * 100;
    long SwapMat_DD = SwapMat_YYYYMMDD - ((long)(SwapMat_YYYYMMDD / 100)) * 100;

    long ncpn;
    long* HolidayYYYYMMDD = (long*)malloc(sizeof(long) * max(1, NHoliday));
    for (i = 0; i < NHoliday; i++)
    {
        if (Holidays[i] < 19000000) HolidayYYYYMMDD[i] = ExcelDateToCDate(Holidays[i]);
        else HolidayYYYYMMDD[i] = Holidays[i];
    }

    long* HolidayYYYYMMDDPayDate = (long*)malloc(sizeof(long) * max(1, NHolidayPayDate));
    for (i = 0; i < NHolidayPayDate; i++)
    {
        if (Holidays[i] < 19000000) HolidayYYYYMMDDPayDate[i] = ExcelDateToCDate(HolidaysPayDate[i]);
        else HolidayYYYYMMDDPayDate[i] = HolidaysPayDate[i];
    }

    if (NumberCoupon < 0) return -1;
    if (NumberCoupon <= 1)
    {
        if (NBDayFromEndDate == 0)
        {
            if (ResultIsExcelType == 1)
            {
                ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                ResultForwardEnd[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
                ResultPayDate[0] = ResultForwardEnd[0];
            }
            else
            {
                ResultForwardStart[0] = StartDateYYYYMMDD;
                ResultForwardEnd[0] = SwapMat_YYYYMMDD;
                ResultPayDate[0] = ResultForwardEnd[0];
            }
        }
        else if (NBDayFromEndDate < 0)
        {
            // NBD Auto계산
            NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, NHolidayPayDate, ModifiedFollowingFlag, &EndDateYYYYMMDD);
            if (ResultIsExcelType == 1)
            {
                ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                ResultForwardEnd[0] = CDateToExcelDate(EndDateYYYYMMDD);
                ResultPayDate[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
            }
            else
            {
                ResultForwardStart[0] = StartDateYYYYMMDD;
                ResultForwardEnd[0] = EndDateYYYYMMDD;
                ResultPayDate[0] = SwapMat_YYYYMMDD;
            }
        }
        else
        {
            if (SwapMat_DD < 7 && StartDD >= 24)
            {
                //////////////////////////////////////////
                // If PayDate is next month of EndDate  //
                //////////////////////////////////////////
                NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, NHolidayPayDate, ModifiedFollowingFlag, &EndDateYYYYMMDD);
                if (ResultIsExcelType == 1)
                {
                    ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                    ResultForwardEnd[0] = CDateToExcelDate(EndDateYYYYMMDD);
                    ResultPayDate[0] = CDateToExcelDate(SwapMat_YYYYMMDD);
                }
                else
                {
                    ResultForwardStart[0] = StartDateYYYYMMDD;
                    ResultForwardEnd[0] = EndDateYYYYMMDD;
                    ResultPayDate[0] = SwapMat_YYYYMMDD;
                }
            }
            else
            {
                n = 0;
                if (ResultIsExcelType == 1) ResultForwardStart[0] = StartDate;
                else ResultForwardStart[0] = StartDateYYYYMMDD;

                // PayDate결정
                PayDateYYYYMMDD = SwapMat_YYYYMMDD;
                PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
                MOD7 = PayDateExcelType % 7;
                for (i = 1; i < 35; i++)
                {
                    if (isweekendflag(PayDateExcelType) || isin_Longtype(PayDateYYYYMMDD, HolidayYYYYMMDDPayDate, NHolidayPayDate))
                    {
                        // 휴일이면 n+=1
                        PayDateExcelType += 1;
                        PayDateYYYYMMDD = ExcelDateToCDate(PayDateExcelType);
                    }
                    else
                    {
                        break;
                    }
                }

                if (ResultIsExcelType == 1) ResultPayDate[0] = PayDateExcelType;
                else ResultPayDate[0] = PayDateYYYYMMDD;

                EndDateYYYYMMDD = PayDateYYYYMMDD;
                EndDateExcel = PayDateExcelType;
                for (i = 1; i < 35; i++)
                {
                    EndDateExcel = EndDateExcel - 1;
                    EndDateYYYYMMDD = ExcelDateToCDate(EndDateExcel);
                    MOD7 = EndDateExcel % 7;
                    if ((MOD7 != 1 && MOD7 != 0) && !isin_Longtype(EndDateYYYYMMDD, HolidayYYYYMMDDPayDate, NHolidayPayDate))
                    {
                        // 영업일이면 n+=1
                        n += 1;
                    }

                    if (n == NBDayFromEndDate)
                    {
                        if (ResultIsExcelType == 1) ResultForwardEnd[0] = EndDateExcel;
                        else ResultForwardEnd[0] = EndDateYYYYMMDD;
                        break;
                    }
                }
            }
        }
    }
    else
    {
        long* CpnDate;
        long TempYYYYMMDD = PriceDateYYYYMMDD;
        long TempDateExcelType;
        long EndYYYYMM = (long)SwapMat_YYYYMMDD / 100;
        if (SwapMat_DD < 7 && StartDD >= 24)
        {
            //////////////////////////////////////////
            // If PayDate is next month of EndDate  //
            //////////////////////////////////////////
            NBDayFromEndDate = NBusinessCountFromEndToPay(StartDateYYYYMMDD, SwapMat_YYYYMMDD, HolidayYYYYMMDDPayDate, NHolidayPayDate, ModifiedFollowingFlag, &EndDateYYYYMMDD);
        }
        else
        {
            EndDateYYYYMMDD = EndYYYYMM * 100 + StartDD;
        }

        if (HolidayUseFlag == 1) CpnDate = Malloc_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, NHoliday, HolidayYYYYMMDD, ModifiedFollowingFlag);
        else CpnDate = Malloc_CpnDate_Holiday(StartDateYYYYMMDD, EndDateYYYYMMDD, AnnCpnOneYear, ncpn, TempYYYYMMDD, 0, HolidayYYYYMMDD, ModifiedFollowingFlag);

        for (i = 0; i < min(NumberCoupon, ncpn); i++)
        {
            if (i == 0)
            {
                if (ResultIsExcelType == 1)
                {
                    ResultForwardStart[0] = CDateToExcelDate(StartDateYYYYMMDD);
                    TempDateExcelType = CDateToExcelDate(CpnDate[0]);
                    ResultForwardEnd[0] = TempDateExcelType;
                }
                else
                {
                    ResultForwardStart[0] = StartDateYYYYMMDD;
                    ResultForwardEnd[0] = CpnDate[0];
                }
            }
            else
            {
                if (ResultIsExcelType == 1)
                {
                    ResultForwardStart[i] = CDateToExcelDate(CpnDate[i - 1]);
                    TempDateExcelType = CDateToExcelDate(CpnDate[i]);
                    ResultForwardEnd[i] = TempDateExcelType;
                }
                else
                {
                    ResultForwardStart[i] = CpnDate[i - 1];
                    ResultForwardEnd[i] = CpnDate[i];
                }
            }

            if (NBDayFromEndDate == 0)
            {
                ResultPayDate[i] = ResultForwardEnd[i];
            }
            else
            {
                n = 0;
                for (j = 1; j < 35; j++)
                {
                    PayDateYYYYMMDD = DayPlus(CpnDate[i], j);
                    PayDateExcelType = CDateToExcelDate(PayDateYYYYMMDD);
                    MOD7 = PayDateExcelType % 7;
                    if ((MOD7 != 1 && MOD7 != 0) && !isin_Longtype(PayDateYYYYMMDD, HolidayYYYYMMDDPayDate, NHolidayPayDate))
                    {
                        // 영업일이면 n+=1
                        n += 1;
                    }

                    if (n == NBDayFromEndDate)
                    {
                        if (ResultIsExcelType == 1) ResultPayDate[i] = PayDateExcelType;
                        else ResultPayDate[i] = PayDateYYYYMMDD;
                        break;
                    }
                }
            }
        }

        if (CpnDate) free(CpnDate);
    }
    if (HolidayYYYYMMDD) free(HolidayYYYYMMDD);
    if (HolidayYYYYMMDDPayDate) free(HolidayYYYYMMDDPayDate);
    return 1;
}

DLLEXPORT(long) Preprocessing_TermAndRate(long PriceDate, long NZeroTerm, double* Term, double* Rate)
{
    long i;
    long PriceDateYYYYMMDD = PriceDate;
    if (PriceDate < 19000101) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDate);
    long PriceDateExcel = CDateToExcelDate(PriceDateYYYYMMDD);

    double m_rate = 0.;
    long TempExcelDate;
    long TempYYYYMMDD;
    for (i = 0; i < NZeroTerm; i++)
    {
        if (Term[i] > 19000101.0)
        {
            TempExcelDate = CDateToExcelDate(((long)(Term[i] + 0.00001)));
            Term[i] = ((double)(TempExcelDate - PriceDateExcel)) / 365.0;
        }
        else if (Term[i] > 300.0)
        {
            TempExcelDate = (long)(Term[i] + 0.00001);
            Term[i] = ((double)(TempExcelDate - PriceDateExcel)) / 365.0;
        }
        if (m_rate < fabs(Rate[i])) m_rate = fabs(Rate[i]);

    }

    if (m_rate > 1.2)
    {
        // Max Rate가 120%보다 크면 단위가 %단위로 들어온듯
        for (i = 0; i < NZeroTerm; i++)
        {
            Rate[i] = Rate[i] / 100.;
        }
    }
    return 1;
}

DLLEXPORT(long) Preprocessing_TermAndRate_MultiCurve(long nCurve, long PriceDate, long* NZeroTerm, double* Term, double* Rate)
{
    long i;
    long n;
    n = 0;
    for (i = 0; i < nCurve; i++)
    {
        Preprocessing_TermAndRate(PriceDate, NZeroTerm[i], Term + n, Rate + n);
        n += NZeroTerm[i];
    }
    return 1;
}

DLLEXPORT(long) Preprocessing_TermAndVol(long PriceDate, long NZeroTerm, double* Term, double* Vols, long IR_0_EQ_1)
{
    long i;
    long PriceDateYYYYMMDD = PriceDate;
    if (PriceDate < 19000101) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDate);
    long PriceDateExcel = CDateToExcelDate(PriceDateYYYYMMDD);

    double m_rate = 0.;
    long TempExcelDate;
    long TempYYYYMMDD;
    for (i = 0; i < NZeroTerm; i++)
    {
        if (Term[i] > 19000101.0)
        {
            TempExcelDate = CDateToExcelDate(((long)(Term[i] + 0.00001)));
            Term[i] = ((double)(TempExcelDate - PriceDateExcel)) / 365.0;
        }
        else if (Term[i] > 300.0)
        {
            TempExcelDate = (long)(Term[i] + 0.00001);
            Term[i] = ((double)(TempExcelDate - PriceDateExcel)) / 365.0;
        }
        if (m_rate < fabs(Vols[i])) m_rate = fabs(Vols[i]);

    }

    if (IR_0_EQ_1 == 0)
    {
        if (m_rate > 0.25)
        {
            // Max Vols가 25%보다 크면 단위가 bp단위로 들어온듯
            for (i = 0; i < NZeroTerm; i++)
            {
                Vols[i] = Vols[i] / 100.;
            }
        }
    }
    else
    {
        if (m_rate > 10.0)
        {
            // Max Vols가 1000%보다 크면 단위가 %단위로 들어온듯
            for (i = 0; i < NZeroTerm; i++)
            {
                Vols[i] = Vols[i] / 100.;
            }
        }
    }
    return 1;
}

DLLEXPORT(long) Preprocessing_TermAndEqVol(long PriceDate, long NZeroTerm, double* Term, long NParity, double* Parity, double* Vols)
{
    long i, j, n;
    long PriceDateYYYYMMDD = PriceDate;
    if (PriceDate < 19000101) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDate);
    long PriceDateExcel = CDateToExcelDate(PriceDateYYYYMMDD);

    double m_rate = 0.;
    long TempExcelDate;
    long TempYYYYMMDD;
    n = 0;
    for (i = 0; i < NZeroTerm; i++)
    {
        if (Term[i] > 19000101.0)
        {
            TempExcelDate = CDateToExcelDate(((long)(Term[i] + 0.00001)));
            Term[i] = ((double)(TempExcelDate - PriceDateExcel)) / 365.0;
        }
        else if (Term[i] > 300.0)
        {
            TempExcelDate = (long)(Term[i] + 0.00001);
            Term[i] = ((double)(TempExcelDate - PriceDateExcel)) / 365.0;
        }

        for (j = 0; j < NParity; j++)
        {
            if (m_rate < fabs(Vols[n])) m_rate = fabs(Vols[n]);
            n += 1;
        }
    }

    n = 0;
    if (m_rate > 10.0)
    {
        // Max Vols가 1000%보다 크면 단위가 %단위로 들어온듯
        for (i = 0; i < NZeroTerm; i++)
        {
            for (j = 0; j < NParity; j++)
            {
                Vols[n] = Vols[n] / 100.;
                n += 1;
            }
        }
    }
    return 1;
}

/////////////////////////////////////
// Calculate Next Nth BusinessDate //
/////////////////////////////////////
DLLEXPORT(long) NextNthBusinessDate(long YYYYMMDD, long NBDate, long* Holidays, long NHolidays)
{
    /////////////////////////////////////
    // Calculate Next Nth BusinessDate //
    /////////////////////////////////////

    if (YYYYMMDD < 19000101) YYYYMMDD = ExcelDateToCDate(YYYYMMDD);
    long StartDate = ParseBusinessDateIfHoliday(YYYYMMDD, Holidays, NHolidays);
    long StartDateExcel = CDateToExcelDate(StartDate);
    long i;
    for (i = 0; i < NHolidays; i++)
    {
        if (Holidays[i] < 19000101)
        {
            Holidays[i] = ExcelDateToCDate(Holidays[i]);
        }
    }
    long n;
    long TempExcelDate;
    long TempYYYYMMDD;
    long IsHolidayFlag = 0;
    long IsSaturSundayFlag = 0;
    long MOD7;
    long ResultYYYYMMDD = YYYYMMDD;
    if (NBDate > 0)
    {
        n = 0;
        for (i = 0; i < 100; i++)
        {
            TempExcelDate = StartDateExcel + 1 + i;
            TempYYYYMMDD = ExcelDateToCDate(TempExcelDate);
            MOD7 = TempExcelDate % 7;

            if (MOD7 == 0 || MOD7 == 1) IsSaturSundayFlag = 1;
            else IsSaturSundayFlag = 0;

            if (isin_Longtype(TempYYYYMMDD, Holidays, NHolidays)) IsHolidayFlag = 1;
            else IsHolidayFlag = 0;

            if (IsSaturSundayFlag == 0 && IsHolidayFlag == 0)
            {
                n += 1;
            }

            if (n >= NBDate)
            {
                ResultYYYYMMDD = TempYYYYMMDD;
                break;
            }
        }
    }
    return ResultYYYYMMDD;
}

// Linear Interpolation (X변수, Y변수, X길이, 타겟X)
double LinterpDate(long* DateArray, double* fx, long NDate, long TargetDate, long extrapolateflag)
{
    long i;
    double result = 0.0;
    for (i = 0; i < NDate; i++) if (DateArray[i] < 19000101) DateArray[i] = ExcelDateToCDate(DateArray[i]);

    if (NDate == 1 || TargetDate == DateArray[0]) return fx[0];
    else if (TargetDate == DateArray[NDate - 1]) return fx[NDate - 1];


    if (TargetDate < DateArray[0])
    {
        if (extrapolateflag == 0) return fx[0];
        else return (fx[1] - fx[0]) / ((double)DayCountAtoB(DateArray[0], DateArray[1])) * -((double)DayCountAtoB(TargetDate, DateArray[0])) + fx[0];
    }
    else if (TargetDate > DateArray[NDate - 1])
    {
        if (extrapolateflag == 0) return fx[NDate - 1];
        else return (fx[NDate - 1] - fx[NDate - 2]) / ((double)DayCountAtoB(DateArray[NDate - 2], DateArray[NDate - 1])) * ((double)DayCountAtoB(DateArray[NDate - 1], TargetDate)) + fx[NDate - 1];
    }
    else
    {
        for (i = 1; i < NDate; i++)
        {
            if (TargetDate < DateArray[i])
            {
                result = (fx[i] - fx[i - 1]) / ((double)DayCountAtoB(DateArray[i - 1], DateArray[i])) * ((double)DayCountAtoB(DateArray[i - 1], TargetDate)) + fx[i - 1];
                break;
            }
        }
        return result;
    }
}

// DayCountFraction(A, B, flag = 0:Act/365 1:Act/360 2: ActAct 3:30/360 4:BD/252, HolidaysArray, HolidayArrayLength)
double FractionAtoB(long Day1, long Day2, long Flag, long* Holidays, long NHolidays)
{
    long i;
    double tau;
    long imax;
    double Div;

    if (Day1 < 19000101) Day1 = ExcelDateToCDate(Day1);
    if (Day2 < 19000101) Day2 = ExcelDateToCDate(Day2);

    if (Flag == 0) return DayCountAtoB(Day1, Day2) / 365.0;
    else if (Flag == 1) return DayCountAtoB(Day1, Day2) / 360.;
    else if (Flag == 2)
    {
        // Act/Act
        long YearA, YearB;
        long MonthA, MonthB;
        long DayA, DayB;
        long CurrentY;
        long NextY;

        YearA = Day1 / 10000;
        MonthA = (Day1 - YearA * 10000) / 100;
        DayA = (Day1 - YearA * 10000 - MonthA * 100);

        YearB = Day2 / 10000;
        MonthB = (Day2 - YearB * 10000) / 100;
        DayB = (Day2 - YearB * 10000 - MonthB * 100);

        NextY = Day1 + 10000;
        if (Day2 > Day1 && Day2 < NextY)
        {
            Div = DayCountAtoB(Day1, NextY);
            return DayCountAtoB(Day1, Day2) / Div;
        }
        else
        {
            tau = 0.;
            for (i = 0; i <= YearB - YearA; i++)
            {
                CurrentY = Day1 + i * 10000;
                NextY = Day1 + (i + 1) * 10000;
                if (Day2 > CurrentY && Day2 <= NextY)
                {
                    Div = DayCountAtoB(CurrentY, NextY);
                    tau += DayCountAtoB(CurrentY, Day2) / Div;
                    break;
                }
                else
                {
                    tau += 1.0;
                }
            }
            return tau;
        }
    }
    else if (Flag == 3)
    {
        // 30/360
        long YearA, YearB;
        long MonthA, MonthB;
        long nMonth;
        YearA = Day1 / 10000;
        MonthA = (Day1 - YearA * 10000) / 100;

        YearB = Day2 / 10000;
        MonthB = (Day2 - YearB * 10000) / 100;

        nMonth = (YearB - YearA) * 12 + (MonthB - MonthA);
        return ((double)30. * (nMonth)) / 360.0;
    }
    else
    {
        long Day1Excel = CDateToExcelDate(Day1);
        long Day2Excel = CDateToExcelDate(Day2);
        for (i = 0; i < NHolidays; i++) if (Holidays[i] < 19000101) Holidays[i] = ExcelDateToCDate(Holidays[i]);
        long TempDateExcel;
        long TempCDate;
        long nbd = 0;
        long MOD7;
        for (TempDateExcel = Day1Excel; TempDateExcel < Day2Excel; TempDateExcel++)
        {
            TempCDate = ExcelDateToCDate(TempDateExcel);
            MOD7 = TempDateExcel % 7;
            if ((MOD7 != 0 && MOD7 != 1) && (isin_Longtype(TempCDate, Holidays, NHolidays) == 0))
            {
                nbd += 1;
            }
        }
        return ((double)nbd )/ 252.;
    }
}

double CalcDiscountFactor_FromDate(long PriceDate, long* DateArray, double* Rate, long NDate, long TargetDate, long extrapolateflag)
{
    if (PriceDate < 19000101) PriceDate = ExcelDateToCDate(PriceDate);
    if (PriceDate == TargetDate) return 1.0;
    long i;
    double maxrate = 0.;
    double* RateCopy = (double*)malloc(sizeof(double) * NDate);
    for (i = 0; i < NDate; i++) RateCopy[i] = Rate[i];

    long div100flag = 0;
    for (i = 0; i < NDate; i++) if (fabs(RateCopy[i]) >= maxrate) maxrate = fabs(RateCopy[i]);
    // 이자율이 0.5가 넘어가면 
    // 퍼센트 단위인걸로 간주
    if (maxrate >= 0.5) div100flag = 1;

    if (div100flag == 1)
    {
        for (i = 0; i < NDate; i++) RateCopy[i] /= 100.;
    }
    double r = LinterpDate(DateArray, RateCopy, NDate, TargetDate, extrapolateflag);
    double t = ((double)DayCountAtoB(PriceDate, TargetDate)) / 365.;
    free(RateCopy);
    return exp(-r * t);
}

long CalcZeroRateAnalytic(
    long PriceDateYYYYMMDD,
    long StartDateYYYYMMDD,
    long NCpnDate,
    long* CpnDateYYYYMMDD,
    long NZero,
    long* ZeroDate,
    double* ZeroRate,
    double SwapRate,
    long DayCountFracFlag,
    double& ResultZeroRate)
{
    // EndDate == PayDate일 경우 Analytic으로 계산
    long i;
    double t = 0.;
    double a = 0.;
    double b = 0.;
    double deltat = 0.;
    double DF = 0.;
    double zero = 0.;
    long MyNaN = 0;

    if (NZero == 0) return -1;

    double DF_Start = CalcDiscountFactor_FromDate(PriceDateYYYYMMDD, ZeroDate, ZeroRate, NZero, StartDateYYYYMMDD, 0);
    if (NCpnDate == 1)
    {
        // 일반 스왑이 한개라면 
        // 적어도 StartDate까지의 
        // ZeroRate는 있어야함
        if (ZeroDate[NZero - 1] < StartDateYYYYMMDD) return -1;
        else
        {
            DF = DF_Start / (1.0 + SwapRate * FractionAtoB(StartDateYYYYMMDD, CpnDateYYYYMMDD[NCpnDate - 1], DayCountFracFlag, &MyNaN, MyNaN));
            t = ((double)DayCountAtoB(PriceDateYYYYMMDD, CpnDateYYYYMMDD[NCpnDate - 1])) / 365.;
            ResultZeroRate = -1.0 / t * log(DF);
            return 1;
        }
    }
    else if (NCpnDate > 1)
    {
        // 적어도 CpnDate[NCpnDate-2]까지의 
        // ZeroRate는 있어야함
        if (ZeroDate[NZero - 1] < CpnDateYYYYMMDD[NCpnDate - 2]) return -1;

        a = DF_Start;
        for (i = 0; i < NCpnDate - 1; i++)
        {
            if (i == 0) deltat = FractionAtoB(StartDateYYYYMMDD, CpnDateYYYYMMDD[i], DayCountFracFlag, &MyNaN, MyNaN);
            else deltat = FractionAtoB(CpnDateYYYYMMDD[i - 1], CpnDateYYYYMMDD[i], DayCountFracFlag, &MyNaN, MyNaN);
            t = ((double)DayCountAtoB(PriceDateYYYYMMDD, CpnDateYYYYMMDD[i])) / 365.;
            a -= (SwapRate * deltat * CalcDiscountFactor_FromDate(PriceDateYYYYMMDD, ZeroDate, ZeroRate, NZero, CpnDateYYYYMMDD[i], 0));
        }
        b = 1.0 + SwapRate * FractionAtoB(CpnDateYYYYMMDD[NCpnDate - 2], CpnDateYYYYMMDD[NCpnDate - 1], DayCountFracFlag, &MyNaN, MyNaN);
        DF = a / b;
        t = ((double)DayCountAtoB(PriceDateYYYYMMDD, CpnDateYYYYMMDD[NCpnDate - 1])) / 365.;
        ResultZeroRate = -1.0 / t * log(DF);
        return 1;
    }
    else
    {
        return -1;
    }
}

// ZeroCurve Analytic으로 어림계산
DLLEXPORT(long) CalcZeroRateAnalyticFast(
    long PriceDateYYYYMMDD,     // PriceDate
    long NTerm,                 // Number of Par Rate Term(Maturity)
    double* Term,               // Par Rate Term(Maturity)
    double* MarketQuote,        // Par Rate or YTM
    long DayCountFracFlag,      // 0:ACT365, 1:ACT360 2: ACTACT  3:30/360
    long AnnCpnOneYear,         // Annual Payment Number of Swap
    long NationFlag,            // 0:KRW, 1:USD, 2:GBP, ...
    double* ResultRate          // Output : Result (ArrayLength = NTerm)
)
{
    // ZeroCurve Analytic으로 어림계산
    if (PriceDateYYYYMMDD < 19000101) PriceDateYYYYMMDD = ExcelDateToCDate(PriceDateYYYYMMDD);
    long PriceDateExcel = CDateToExcelDate(PriceDateYYYYMMDD);
    long NHolidays = Number_Holiday(PriceDateYYYYMMDD / 100, PriceDateYYYYMMDD / 100 + 50, NationFlag);
    long* Holidays = (long*)malloc(sizeof(long) * NHolidays);           // 할당1
    Mapping_Holiday_CType(PriceDateYYYYMMDD / 100, PriceDateYYYYMMDD / 100 + 50, NationFlag, NHolidays, Holidays);
    
    long i = 0;
    long n = 0;
    double maxrate = 0.;
    for (i = 0; i < NTerm; i++) if (fabs(MarketQuote[i]) >= maxrate) maxrate = fabs(MarketQuote[i]);
    // 이자율이 0.5가 넘어가면 
    // 퍼센트 단위인걸로 간주
    if (maxrate >= 0.5) 
    {
        for (i = 0; i < NTerm; i++) MarketQuote[i] /= 100.;
    }

    long Num_MMF = 0;

    long* Maturity = (long*)malloc(sizeof(long) * NTerm);
    long NCpnDate = 0;
    long FirstCpnDate = PriceDateYYYYMMDD;
    long MyNaN = 0;

    long StartDate = NextNthBusinessDate(PriceDateYYYYMMDD, 1, Holidays, NHolidays);
    long StartDateExcel = CDateToExcelDate(StartDate);
    for (i = 0; i < NTerm; i++)
    {
        if (Term[i] < 300.) Maturity[i] = ExcelDateToCDate(PriceDateExcel + (long)(Term[i] * 365. + 0.1e-5));
        else if (Term[i] < 19000101) Maturity[i] = ExcelDateToCDate(Term[i]);
        else Maturity[i] = ((long)Term[i] + 0.1e-9);
    }

    long EndDate = ((long)Maturity[NTerm - 1]/100) * 100 + (StartDate % 100);
    long* CpnDate = Malloc_CpnDate_Holiday(StartDate, EndDate, AnnCpnOneYear, NCpnDate, FirstCpnDate, MyNaN, &MyNaN, 1);
    double* SwapRate = (double*)malloc(sizeof(double) * NCpnDate);
    for (i = 0; i < NCpnDate; i++)
    {
        SwapRate[i] = LinterpDate(Maturity, MarketQuote, NTerm, CpnDate[i], 0);
    }

    for (i = 0; i < NTerm; i++)
    {
        if (Maturity[i] < CpnDate[0]) Num_MMF += 1;
    }

    double df0, df, t, r;
    double* ResultZeroRate;
    long* ResultZeroDate;
    long ResultCode;
    double OvNightRate;
    long NCurve = 0;
    if (Num_MMF == 0)
    {
        OvNightRate = LinterpDate(CpnDate, SwapRate, NCpnDate, StartDate, 1);
        ResultZeroRate = (double*)malloc(sizeof(double) * (1 + NCpnDate));
        ResultZeroDate = (long*)malloc(sizeof(long) * (1 + NCpnDate));
        ResultZeroDate[0] = StartDate;
        df = 1.0 / (1.0 + OvNightRate * FractionAtoB(PriceDateYYYYMMDD, StartDate, DayCountFracFlag, &MyNaN, MyNaN));
        t = ((double)DayCountAtoB(PriceDateYYYYMMDD, StartDate)) / 365.;
        r = -1. / t * log(df);
        ResultZeroRate[0] = r;
        NCurve = 1;
    }
    else
    {
        OvNightRate = LinterpDate(Maturity, MarketQuote, NTerm, StartDate, 1);
        df0 = 1.0 / (1.0 + OvNightRate * FractionAtoB(PriceDateYYYYMMDD, StartDate, DayCountFracFlag, &MyNaN, MyNaN));
        ResultZeroRate = (double*)malloc(sizeof(double) * (Num_MMF + NCpnDate));
        ResultZeroDate = (long*)malloc(sizeof(long) * (Num_MMF + NCpnDate));
        n = 0;
        for (i = 0; i < NTerm; i++)
        {
            if (Maturity[i] < CpnDate[0])
            {
                ResultZeroDate[n] = Maturity[i];
                if (Maturity[i] > StartDate) df = df0 / (1.0 + MarketQuote[i] * FractionAtoB(StartDate, Maturity[i], DayCountFracFlag, &MyNaN, MyNaN));
                else df = 1.0 / (1.0 + MarketQuote[i] * FractionAtoB(PriceDateYYYYMMDD, StartDate, DayCountFracFlag, &MyNaN, MyNaN));
                t = ((double)DayCountAtoB(PriceDateYYYYMMDD, Maturity[i])) / 365.;
                ResultZeroRate[n] = -1. / t * log(df);
                n += 1;
            }
        }
        NCurve = Num_MMF;
    }

    r = -99.9;
    for (i = 0; i < NCpnDate; i++)
    {
        ResultCode = CalcZeroRateAnalytic(PriceDateYYYYMMDD, StartDate, i+1, CpnDate, NCurve,
            ResultZeroDate,ResultZeroRate,SwapRate[i],DayCountFracFlag, r);
        if (ResultCode >= 0) ResultZeroRate[NCurve] = r;
        else ResultZeroRate[NCurve] = ResultZeroRate[NCurve - 1];
        ResultZeroDate[NCurve] = CpnDate[i];
        NCurve += 1;
    }

    for (i = 0; i < NTerm; i++)
    {
        ResultRate[i] = LinterpDate(ResultZeroDate, ResultZeroRate, NCurve, Maturity[i], 1);
    }
    free(Holidays);
    free(Maturity);
    free(CpnDate);
    free(SwapRate);
    free(ResultZeroRate);
    free(ResultZeroDate);
    return 1;
}

// Function : O/N, T/N, 1m, ... (Input String) -> to Maturity -> YYYYMMDD (Output)
// Tenor -> String - O/N, 1M, 2M, ...
// StartDate -> Swap StartDate
// NBDAfter -> NBD from FixEnd to Pay
// NationFlag -> HolidayFlag
// NAdditionalHoliday -> Number of Alternative Holidays
// AdditionalHolidays -> Alternative Holidays
DLLEXPORT(long) TenorStrToMaturity(char* Tenor, long StartDate, long NBDAfterFix, long NationFlag, long NAdditionalHoliday, long* AdditionalHolidays)
{
    long i;
    long n;
    long n1;
    long n2;
    if (StartDate < 19000101) StartDate = ExcelDateToCDate(StartDate);
    for (i = 0; i < NAdditionalHoliday; i++) if (AdditionalHolidays[i] < 19000100) AdditionalHolidays[i] = ExcelDateToCDate(AdditionalHolidays[i]);

    //////////////////////
    // Domestic Holiday //
    //////////////////////

    long NDomesticHolidays;
    long* DomesticHolidays;
    if (NationFlag >= 0 && NationFlag < 5)
    {
        // 0 KRW, 1:USD, 2:GBP, 3:NYSE, 4:NYMEX
        n1 = Number_Holiday(StartDate/10000, StartDate / 10000+60, NationFlag);
        NDomesticHolidays = NAdditionalHoliday + n1;
        DomesticHolidays = (long*)malloc(sizeof(long) * NDomesticHolidays);
        Mapping_Holiday_CType(StartDate / 10000, StartDate / 10000 + 60, NationFlag, n1, DomesticHolidays);
        for (i = n1; i < NDomesticHolidays; i++)
        {
            DomesticHolidays[i] = AdditionalHolidays[i - n1];
        }
    }
    else
    {
        NDomesticHolidays = NAdditionalHoliday;
        DomesticHolidays = (long*)malloc(sizeof(long) * NDomesticHolidays);
        for (i = 0; i < NAdditionalHoliday; i++) DomesticHolidays[i] = AdditionalHolidays[i];
    }

    long longpart[10] = { -1,-1,-1,-1,-1,-1,-1,-1,-1,-1 };
    char charpart[10] = "---------";

    n = 0;
    for (i = 0; i < 10; i++)
    {
        if ((Tenor[i] >= 65 && Tenor[i] <= 90) || (Tenor[i] >= 97 && Tenor[i] <= 122))
        {
            charpart[n] = Tenor[i];
            n++;
        }
    }

    n = 0;
    for (i = 0; i < 10; i++)
    {
        if (Tenor[i] >= 48 && Tenor[i] <= 57) 
        {
            longpart[n] = (long)(Tenor[i]) - 48;
            n++;
        }
    }

    long A = 0;
    for (i = 0; i < 10; i++)
    {
        if (longpart[i] >= 0)
        {
            A *= 10;
            A += longpart[i];
        }
    }

    long FixDate = -1;
    long PayDate = -1;
    if ((int(charpart[0]) == 68) || (int(charpart[0]) == 100))
    {
        // 1D, 1d, 2D, 2d, 3D, 3d, ...
        FixDate = NextNthBusinessDate(StartDate, A, DomesticHolidays, NDomesticHolidays);
        PayDate = NextNthBusinessDate(FixDate, NBDAfterFix, DomesticHolidays, NDomesticHolidays);
    }
    else if (((int(charpart[0]) == 79) || (int(charpart[0]) == 111)) && ((int(charpart[1]) == 78) || (int(charpart[1]) == 110)))
    {
        // O/N
        FixDate = NextNthBusinessDate(StartDate, 1, DomesticHolidays, NDomesticHolidays);
        PayDate = NextNthBusinessDate(FixDate, NBDAfterFix, DomesticHolidays, NDomesticHolidays);
    }
    else if (((int(charpart[0]) == 84) || (int(charpart[0]) == 116)) && ((int(charpart[1]) == 78) || (int(charpart[1]) == 110)))
    {
        // T/N
        FixDate = NextNthBusinessDate(StartDate, 2, DomesticHolidays, NDomesticHolidays);
        PayDate = NextNthBusinessDate(FixDate, NBDAfterFix, DomesticHolidays, NDomesticHolidays);
    }
    else if ((int(charpart[0]) == 87) || (int(charpart[0]) == 119))
    {
        // 1W, 2W, 3W, ....        
        FixDate = ParseBusinessDateIfHoliday(DayPlus(StartDate, A * 7),DomesticHolidays, NDomesticHolidays);
        PayDate = NextNthBusinessDate(FixDate, NBDAfterFix, DomesticHolidays, NDomesticHolidays);
    }
    else if ((int(charpart[0]) == 77) || (int(charpart[0]) == 109))
    {
        // 1m, 2m, 3m, ....
        FixDate = min(LastBusinessDate(EDate_Cpp(StartDate, A)/100, NDomesticHolidays, DomesticHolidays), EDate_Cpp(StartDate, A));
        PayDate = NextNthBusinessDate(FixDate, NBDAfterFix, DomesticHolidays, NDomesticHolidays);
    }
    else if ((int(charpart[0]) == 89) || (int(charpart[0]) == 121))
    {
        // 1y, 2y, 3y, ....
        FixDate = min(LastBusinessDate(EDate_Cpp(StartDate, A*12) / 100, NDomesticHolidays, DomesticHolidays), EDate_Cpp(StartDate, A*12));
        PayDate = NextNthBusinessDate(FixDate, NBDAfterFix, DomesticHolidays, NDomesticHolidays);
    }

    free(DomesticHolidays);
    return PayDate;
}