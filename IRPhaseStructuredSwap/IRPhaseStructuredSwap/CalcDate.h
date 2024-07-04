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
            if (m < 12)
                Month = m + 1;
            else
                Month = 12;
            Day = ExcelDate - CummulativeDays_Leap[m];
        }
        else
        {
            for (m = 0; m < 12; m++)
            {
                if (CummulativeDays[m + 1] >= ExcelDate && CummulativeDays[m] < ExcelDate) break;
            }

            if (m < 12)
                Month = m + 1;
            else
                Month = 12;

            Day = ExcelDate - CummulativeDays[m];
        }
        return   Year * 10000 + Month * 100 + Day;
    }
}

DLLEXPORT(long) DayCountAtoB(long Day1, long Day2)
{
    return CDateToExcelDate(Day2) - CDateToExcelDate(Day1);
}

DLLEXPORT(long) DayPlus(long Cdate, long NDays)
{
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
    if (NDays < 0) 
        return ExcelDateToCDate(CDateToExcelDate(Cdate) + NDays);
    else if (NDays == 0)
        return Cdate;

    Leap = LeapCheck(Year);
    if (Year == 1900) Leap = 1;

    long LeftDaysofMonth;
    if (Leap == 1)
        LeftDaysofMonth = Days_Leap[Month - 1] - Day;
    else
        LeftDaysofMonth = Days[Month - 1] - Day;

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
            if (_info_array[i][j] == 1) mm = 29;
            else if (_info_array[i][j] == 2) mm = 30;
            else if (_info_array[i][j] == 3) mm = 58;
            else if (_info_array[i][j] == 4) mm = 59;
            else if (_info_array[i][j] == 5) mm = 59;
            else if (_info_array[i][j] == 6) mm = 60;
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
                m1 = 29;
                m2 = 29;
            }
            else if (_info_array[ly][lm] == 4) {
                m1 = 29;
                m2 = 30;
            }
            else if (_info_array[ly][lm] == 5) {
                m1 = 30;
                m2 = 29;
            }
            else if (_info_array[ly][lm] == 6) {
                m1 = 30;
                m2 = 30;
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

    long** _info_array = (long**)malloc(sizeof(long*) * N_Info_Array);
    for (i = 0; i < N_Info_Array; i++) _info_array[i] = _info_array_raw + i * 12;

    long _info_month[12] = { 31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    long Year = YYYYMMDD / 10000;
    long Month = (YYYYMMDD - Year * 10000) / 100;
    long Day = (YYYYMMDD - Year * 10000 - Month * 100);

    if (Year < 1841 || 2043 < Year) return -99999999;
    if (Month < 1 || 12 < Month) return -99999999;

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
    const long NTempHoliday = 8;
    long TempHolidayList[NTempHoliday] =
    {

        // 더 있으면 추가하고 NTempHoliday 바꾸기
        20020701, 20150814, 20171002, 20200817, 20220309, 
        20220601, 20231002, 20240410

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
    Calc3_newyear(YYYY, Seol, ResultCode);                      // 설연휴
    if (ResultCode < 0) for (i = 0; i < 3; i++) Seol[i] = -99999999;// 음력 코드 갱신안해서 매핑안되면 걍 1.1일로

    long Samil = Calc_31Day_Korea(YYYY);
    Array16[4] = Samil;
    
    long Labor = YYYY * 10000 + 501;
    Array16[5] = Labor;

    long Budda = Calc_Budda_Korea(YYYY);
    Array16[6] = Budda;
    long ChildrenDay = Calc_ChildrensDay_Korea(YYYY);
    Array16[7] = ChildrenDay;
    Array16[8] = YYYY * 10000 + 606;
    long Gwangbok = Calc_Gwangbok_Korea(YYYY);
    Array16[9] = Gwangbok;

    long* Chuseok = Array16 + 10;
    Calc3_chuseok(YYYY, Chuseok, ResultCode);
    if (ResultCode < 0) for (i = 0; i < 3; i++) Chuseok[i] = -99999999; // 음력코드 갱신 안한 경우 이전공휴일 매핑

    long GaeChun = Calc_GaechunJeol_Korea(YYYY);
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
    long NArray = 16 + NTempHoliday;

    // 원래는 16개 + 임시공휴일개수 이나 
    // 하드코드된 음력 연도보다 커지면 설, 추석, 석가탄신일 제외하자
    if (YYYY > LunarDateKoreanHardCodeYear) NArray = NArray_Org - 7 + NTempHoliday;

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

    long temp;
    long j;
    for (i = 0; i < NArray; i++)
    {
        for (j = 0; j < NArray - 1; j++)
        {
            if (ResultArray[j] > ResultArray[j + 1])
            {
                temp = ResultArray[j];
                ResultArray[j] = ResultArray[j + 1];
                ResultArray[j + 1] = temp;
            }
        }
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

    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2
    return ResultArray;
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
    else if (TempExcelDate % 7 == 1) return ExcelDateToCDate(FullMoonDayExcel + 7 -2);
    for (i = 1; i < 8; i++)
    {
        TempExcelDate = FullMoonDayExcel + i;
        MOD7 = TempExcelDate % 7;
        if (MOD7 == 1)
        {
            break;
        }
    }
    return ExcelDateToCDate(TempExcelDate-2);
}

long RebirthDayPlus1(long YYYY)
{
    long i;
    long FullMoonDay = CalcFullMoonDay(YYYY);
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
    long* HolidayArray,         // 미리 할당된 Array( 대통령 취임식 연도가 아니면 11개 그렇지 않으면 12개
    long IsPresidentYearFlag    // YYYY가 대통령 취임식 연도인지 Flag
)
{
    long Jan01 = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 101);
    long President = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 120);
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
    if (IsPresidentYearFlag == 1)
    {
        HolidayArray[1] = MartinLuther;
        HolidayArray[2] = President;
        HolidayArray[3] = PresidentsDay;
        HolidayArray[4] = MemorialDay;
        HolidayArray[5] = Juneteenth;
        HolidayArray[6] = Independence;
        HolidayArray[7] = LaborDay;
        HolidayArray[8] = ColumBus;
        HolidayArray[9] = Veterans;
        HolidayArray[10] = Thanks;
        HolidayArray[11] = Christmas;
    }
    else
    {
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
        Mapping_USHoliday(Start_YYYY + i, Holidays[i], ispresidflag);
        if (ispresidflag > 0) nholidays[i] = 12;
        else nholidays[i] = 11;
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

    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++) if (Holidays[i]) free(Holidays[i]);
    free(Holidays);                                                                                 // 메모리할당해제1
    free(nholidays);                                                                                // 메모리할당해제2
    return ResultArray;
}

// U.S NYMEX Holiday Mapping
void Mapping_US_NYMEXHoliday(
    long YYYY,                  // 연도 
    long* HolidayArray         // 미리 할당된 Array(10개
)
{
    // Nymex : 부활절 쉼, 준틴스 안쉼, 독립일 전날도 쉼, 콜럼버스 안쉼, 빼뺴로 안쉼, Thanksgiv 쉼
    long Jan01 = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 101);
    long RebirthMinus2;
    
    if (YYYY < LunarDateKoreanHardCodeYear) RebirthMinus2 = RebirthDayMinus2(YYYY);     // 부활절 쉼
    else RebirthMinus2 = Jan01;


    //long President = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 120);                    // 취임식 안쉼
    //long Juneteenth = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 619);                   // 준틴스 안쉼
    long Independence = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 704);                   // 독립일 쉼
    long IndependenceExcel = CDateToExcelDate(Independence);
    long IndependencePrev = ExcelDateToCDate(IndependenceExcel - 1);                    // 독립일 전날 쉼
    if (IndependenceExcel % 7 == 2)
    {
        // 독립일이 월요일이면 전날은 금요일
        IndependencePrev = ExcelDateToCDate(IndependenceExcel - 3);
    }

    //long Veterans = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1111);                    // 빼빼로 안쉼
    long Christmas = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1225);

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
    HolidayArray[9] = Christmas;
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
        nholidays[i] = 10;
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

    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++) if (Holidays[i]) free(Holidays[i]);
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
    long IndependenceExcel = CDateToExcelDate(Independence);
    long IndependencePrev = ExcelDateToCDate(IndependenceExcel - 1);                    // 독립일 전날 쉼
    if (IndependenceExcel % 7 == 2)
    {
        // 독립일이 월요일이면 전날은 금요일
        IndependencePrev = ExcelDateToCDate(IndependenceExcel - 3);
    }

    //long Veterans = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1111);                    // 빼빼로 안쉼
    long Christmas = FixedHoliday_YYYYMMDD_US(YYYY * 10000 + 1225);
    long ChristmasExcel = CDateToExcelDate(Christmas);
    long ChristmasPrev = ExcelDateToCDate(ChristmasExcel - 1);
    if (ChristmasExcel % 7 == 2)
    {
        // 크리스마스가 월요일이면 전날은 금요일
        ChristmasPrev = ExcelDateToCDate(ChristmasExcel - 3);
    }

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
    HolidayArray[6] = IndependencePrev;
    HolidayArray[7] = Independence;
    HolidayArray[8] = LaborDay;
    HolidayArray[9] = Thanks;
    HolidayArray[10] = ThanksNext;
    HolidayArray[11] = ChristmasPrev;
    HolidayArray[12] = Christmas;
}

// U.S NYMEX Holiday Array를 Malloc하는 함수
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
        nholidays[i] = 13;
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

    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++) if (Holidays[i]) free(Holidays[i]);
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
    if (EasterMondayDay > 0)
    {
        HolidayArray[5] = EasterMondayDay;
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
        HolidayArray[6] = GoodFriday;
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
            nholidays[i] = 7;
        }
        else
        {
            Mapping_GBPHoliday(Start_YYYY + i, Holidays[i], 0);
            nholidays[i] = 5;
        }                
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

    for (i = 0; i < (End_YYYY - Start_YYYY + 1); i++) if (Holidays[i]) free(Holidays[i]);
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
    // 시작연도 ~ 종료연도까지 공휴일 개수 세기
    long i;
    long k;
    long NHoliday = 0;
    long* Holidays;

    if (NationFlag == 0) Holidays = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 1) Holidays = Malloc_USHolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 3) Holidays = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 4) Holidays = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, NHoliday);
    else Holidays = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, NHoliday);

    long N = 0;
    for (i = 0; i < NHoliday; i++) if (Holidays[i] > 0) N += 1;
    free(Holidays);
    return N;
}

// Put Holiday to ResultArray
DLLEXPORT(long) Mapping_Holiday_ExcelType(
    long StartYYYY,     // 시작연도
    long EndYYYY,       // 종료연도
    long NationFlag,    // 국가Flag 0한국 1미국 2영국
    long NResultArray,  // 배열 개수 Number_Holiday에서 확인
    long* ResultArray   // Holiday 들어가는 배열
)
{
    // 시작연도 ~ 종료연도까지 공휴일을 ResultArray에 집어넣는다.
    long i;
    long k;
    long NHoliday = 0;
    long* Holidays;

    if (NationFlag == 0) Holidays = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 1) Holidays = Malloc_USHolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 3) Holidays = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 4) Holidays = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, NHoliday);
    else Holidays = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, NHoliday);

    long n = min(NResultArray, NHoliday);
    k = 0;
    for (i = 0; i < n; i++)
    {
        if (Holidays[i] > 0)
        {
            ResultArray[k] = CDateToExcelDate(Holidays[i]);
            k += 1;
        }
    }

    free(Holidays);         // 할당제거 1
    return 1;
}

DLLEXPORT(long) Mapping_Holiday_CType(
    long StartYYYY,     // 시작연도
    long EndYYYY,       // 종료연도
    long NationFlag,    // 국가Flag 0한국 1미국 2영국
    long NResultArray,  // 배열 개수 Number_Holiday에서 확인
    long* ResultArray   // Holiday 들어가는 배열
)
{
    // 시작연도 ~ 종료연도까지 공휴일을 ResultArray에 집어넣는다.
    long i;
    long k;
    long NHoliday = 0;
    long* Holidays;
    if (NationFlag == 0) Holidays = Malloc_KoreaHolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 1) Holidays = Malloc_USHolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 3) Holidays = Malloc_US_NYSE_HolidayArray(StartYYYY, EndYYYY, NHoliday);
    else if (NationFlag == 4) Holidays = Malloc_US_NYMEX_HolidayArray(StartYYYY, EndYYYY, NHoliday);
    else Holidays = Malloc_GBPHolidayArray(StartYYYY, EndYYYY, NHoliday);

    long n = min(NResultArray, NHoliday);
    k = 0;
    for (i = 0; i < n; i++)
    {
        if (Holidays[i] > 0)
        {
            ResultArray[k] = Holidays[i];
            k++;
        }
    }

    free(Holidays);             // 할당제거 1
    return 1;
}