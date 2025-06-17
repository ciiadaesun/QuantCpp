#include <math.h>
#include <stdio.h>
#include <string.h>
#include "GetTextDump.h"

#ifndef UTILITY
#include "Util.h"
#endif

#ifndef DateFunction
#include "CalcDate.h"
#endif 
#include <crtdbg.h>

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

double DayCountFrc(long Day1, long Day2, long Flag)
{
	long i;
	double tau;
	long imax;
	double Div;

	if (Day1 < 19000000 && Day2 < 19000000)
	{
		Day1 = ExcelDateToCDate(Day1);
		Day2 = ExcelDateToCDate(Day2);
	}

	if (Flag == 0) return DayCountAtoB(Day1, Day2) / 365.0;
	else if (Flag == 1) return DayCountAtoB(Day1, Day2) / 360.;
	else if (Flag == 2)
	{
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
	else
	{
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
		return ((double)((YearB - YearA) * 12 + (MonthB - MonthA))) * 30.0 / 360.0;
	}
}

double Interpolate_Linear_Pointer(double* x, double* fx, long nx, double targetx, long& PointStart)
{
	long i;
	double result = 0.0;

	if (nx == 1 || targetx == x[0]) return fx[0];
	else if (targetx == x[nx - 1]) return fx[nx - 1];

	if (targetx < x[0])
	{
		PointStart = 0;
		return fx[0];
	}
	else if (targetx > x[nx - 1])
	{
		PointStart = nx - 1;
		return fx[nx - 1];
	}
	else
	{
		for (i = max(PointStart, 1); i < nx; i++)
		{
			if (targetx < x[i])
			{
				result = (fx[i] - fx[i - 1]) / (x[i] - x[i - 1]) * (targetx - x[i - 1]) + fx[i - 1];
				PointStart = i-1;
				break;
			}
		}
		return result;
	}
}

double Calc_DiscountFactor_Pointer(double* x, double* fx, long nx, double targetx, long& PointStart)
{
	double r = Interpolate_Linear_Pointer(x, fx, nx, targetx, PointStart);
	return exp(-r * targetx);
}

long isin(long x, long* array, long narray)
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

long isin(long x, long* array, long narray, long& startidx)
{
	long i;
	long s = 0;
	for (i = startidx; i < narray; i++)
	{
		if (x == array[i])
		{
			s = 1;
			startidx = i;
			break;
		}
	}
	return s;
}

long* Generate_CpnDate_Holiday_IRSwaption(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long& lenArray, long& FirstCpnDate, long NHoliday, long* HolidayYYYYMMDD)
{
	long i, j;

	long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
	long PriceMM = (long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100;

	long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
	long SwapMatMM = (long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100;

	long n = ((SwapMat_YYYYMMDD / 10000 - PriceDateYYYYMMDD / 10000) + 2) * AnnCpnOneYear;
	long narray = 0;
	long CpnDate;
	long m = max(1, 12 / AnnCpnOneYear);
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

	long* ResultCpnDate = (long*)malloc(sizeof(long) * narray);
	long CpnDateExcel, CpnDateTemp;
	long MOD7;
	long SaturSundayFlag;
	for (i = 0; i < n; i++)
	{
		if (i == 0) CpnDate = SwapMat_YYYYMMDD;
		else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i * m);

		if (CpnDate <= PriceDateYYYYMMDD || DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7) break;
		else
		{
			CpnDateExcel = CDateToExcelDate(CpnDate);
			MOD7 = CpnDateExcel % 7;
			if ((MOD7 == 1 || MOD7 == 0) || isin(CpnDate, HolidayYYYYMMDD, NHoliday)) SaturSundayFlag = 1;
			else SaturSundayFlag = 0;

			if (SaturSundayFlag == 0)
			{
				ResultCpnDate[narray - 1 - i] = CpnDate;
			}
			else
			{
				// Forward End 날짜가 토요일 또는 일요일의 경우 날짜 미룸
				for (j = 1; j <= 7; j++)
				{
					CpnDateExcel += 1;
					MOD7 = CpnDateExcel % 7;
					CpnDateTemp = ExcelDateToCDate(CpnDateExcel);
					if ((MOD7 != 1 && MOD7 != 0) && !isin(CpnDateTemp, HolidayYYYYMMDD, NHoliday))
					{
						CpnDate = ExcelDateToCDate(CpnDateExcel);
						break;
					}
				}
				ResultCpnDate[narray - 1 - i] = CpnDate;
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

double ForwardSwapRate(
	long PriceDate,
	long StartDate,
	long NCpn,
	long* SwapDate,
	long Fix_NTerm,
	double* Fix_Term,
	double* Fix_Rate,
	long Est_NTerm,
	double* Est_Term,
	double* Est_Rate,
	long DayCountFracFlag
)
{
	long i;
	long idx1 = 0;
	long idx2 = 0;
	long idx3 = 0;
	double t0 ,dt, t_pay, t1, t2, DF_t1, DF_t2;
	double a, b, f, p;
	a = 0.0;

	for (i = 0; i < NCpn; i++)
	{
		if (i == 0)
		{
			t1 = ((double)DayCountAtoB(PriceDate, StartDate)) / 365.0;
			t2 = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;
		}
		else
		{
			t1 = ((double)DayCountAtoB(PriceDate, SwapDate[i-1])) / 365.0;
			t2 = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;
		}

		if (i == 0)
		{
			dt = DayCountFrc(StartDate, SwapDate[i], DayCountFracFlag);
		}
		else
		{
			dt = DayCountFrc(SwapDate[i - 1], SwapDate[i], DayCountFracFlag);
		}

		DF_t1 = Calc_DiscountFactor_Pointer(Est_Term, Est_Rate, Est_NTerm, t1, idx1);
		DF_t2 = Calc_DiscountFactor_Pointer(Est_Term, Est_Rate, Est_NTerm, t2, idx2);

		f = 1.0 / (t2 - t1) * (DF_t1 / DF_t2 - 1.0);
		t_pay = t2;
		p = Calc_DiscountFactor_Pointer(Fix_Term, Fix_Rate, Fix_NTerm, t_pay, idx3);
		a += f * dt * p;
	}

	b = 0.0;
	idx1 = 0;
	for (i = 0; i < NCpn; i++)
	{
		if (i == 0)
		{
			dt = DayCountFrc(StartDate, SwapDate[i], DayCountFracFlag);
		}
		else
		{
			dt = DayCountFrc(SwapDate[i - 1], SwapDate[i], DayCountFracFlag);
		}
		t_pay = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;
		p = Calc_DiscountFactor_Pointer(Fix_Term, Fix_Rate, Fix_NTerm, t_pay, idx1);
		b += dt * p;
	}
	return a / b;
}

double Rate_A_S_T(
	double xt,
	double kappa,
	double sigma,
	double s,
	double t,
	long NTerm,
	double* ZeroTerm,
	double* ZeroRate,
	double ForwardDiscFactor,
	double B_s_t,
	double QVTerm
)
{
	double term = (t - s);

	double A_S_T = ForwardDiscFactor * exp(-B_s_t * xt + QVTerm);
	return -1.0 / term * log(A_S_T);
}

double Calc_B_s_t(double kappa, double t, double s)
{
	return (1.0 - exp(-kappa * (t - s))) / kappa;
}

double V_t_T(
	double kappa,
	double kappa2,
	double t,
	double T,
	double vol,
	double vol2
)
{
	return vol * vol2 / (kappa * kappa2) * (T - t + (exp(-kappa * (T - t)) - 1.0) / kappa + (exp(-kappa2 * (T - t)) - 1.0) / kappa2 - (exp(-(kappa + kappa2) * (T - t)) - 1.0) / (kappa + kappa2));
}

double Calc_QVTerm(double kappa, double t, double s, double sigma)
{
	return 0.5 * (V_t_T(kappa, kappa, s, t, sigma, sigma));
}

double BS_Swaption(
	long FixedPayer,				// Fixed Payer여부
	long PriceDate,					// 평가일
	long StartDate,					// 스왑시작일
	long NCpn,						// 쿠폰개수
	long* SwapDate,					// SwapDate Array YYYYMMDD
	double NA,						// Notional Amount
	double Vol,						// Volatility
	double StrikePrice,				// 행사가격
	double* Term,					// Zero Term Structure의 Term
	double* Rate,					// Zero Term Structure의 Rate
	long NTerm,						// Zero Term Structure의 길이
	long DayCountFracFlag,			// DayCountFraction
	long VolFlag,					// 0 Black Vol 1 바실리에 Normal Vol
	long PricingOrValueFlag,		// Pricing할지 Valuation할지
	double &ResultForwardSwapRate,	// ResultForwardRate
	double &ExerciseValue			// 행사 Value
)
{
	long i;
	long idx = 0;
	double FSR;

	double T_Option = ((double)DayCountAtoB(PriceDate, StartDate))/365.0;
	if (T_Option < 0.0000285388)
	{
		// 옵션만기까지 최소 15분
		T_Option = 0.0000285388;
	}
	double dt, t_pay, value, d1, d2, value_atm , d1_atm, d2_atm;
	double annuity = 0.0;
	
	FSR = ForwardSwapRate(PriceDate, StartDate, NCpn, SwapDate, NTerm, Term, Rate, NTerm, Term, Rate, DayCountFracFlag);
	ResultForwardSwapRate = FSR;

	for (i = 0; i < NCpn; i++)
	{
		if (i == 0) dt = DayCountFrc(StartDate, SwapDate[i], DayCountFracFlag);
		else dt = DayCountFrc(SwapDate[i - 1], SwapDate[i], DayCountFracFlag);
		t_pay = ((double)DayCountAtoB(PriceDate, SwapDate[i])) / 365.0;
		annuity += dt * Calc_DiscountFactor_Pointer(Term, Rate, NTerm, t_pay, idx);
	}
	
	value = 0.0;
	value_atm = 0.0;
	if (VolFlag == 0)
	{
		d1 = (log(FSR / StrikePrice) + 0.5 * Vol * Vol * T_Option) / (Vol * sqrt(T_Option));
		d2 = d1 - Vol * sqrt(T_Option);

		d1_atm = 0.5 * Vol * sqrt(T_Option);
		d2_atm = -0.5 * Vol * sqrt(T_Option);

		if (PriceDate != StartDate)
		{
			if (FixedPayer == 0)
			{
				value = max(annuity * (FSR * CDF_N(d1) - StrikePrice * CDF_N(d2)), 0.0);
				value_atm = annuity * (FSR * CDF_N(d1_atm) - FSR * CDF_N(d2_atm));
			}
			else
			{
				value = max(annuity * (-FSR * CDF_N(-d1) + StrikePrice * CDF_N(-d2)), 0.0);
				value_atm = annuity * (-FSR * CDF_N(-d1_atm) + FSR * CDF_N(-d2_atm));
			}
		}
		else
		{
			if (FixedPayer == 0)
			{
				value = annuity * max(FSR - StrikePrice, 0.0);
				value_atm = 0.0;
			}
			else
			{
				value = annuity * max(-FSR + StrikePrice, 0.0);
				value_atm = 0.0;
			}
		}
	}
	else
	{
		d1 = (FSR - StrikePrice) / (Vol * sqrt(T_Option));
		d1_atm = 0.0;
		if (PriceDate != StartDate)
		{
			if (FixedPayer == 0)
			{
				value = max(annuity * ((FSR - StrikePrice) * CDF_N(d1) + Vol * sqrt(T_Option) * (exp(-d1 * d1 / 2.0) / 2.506628274631)), 0.0);
				value_atm = annuity * Vol * sqrt(T_Option) * (exp(-d1_atm * d1_atm / 2.0) / 2.506628274631);
			}
			else
			{
				value = max(annuity * ((FSR - StrikePrice) * CDF_N(d1) + Vol * sqrt(T_Option) * (exp(-d1 * d1 / 2.0) / 2.506628274631)), 0.0);
				value_atm = annuity * Vol * sqrt(T_Option) * (exp(-d1_atm * d1_atm / 2.0) / 2.506628274631);
				value = max(0.0 , annuity * (StrikePrice - FSR) + value);
			}
		}
		else
		{
			if (FixedPayer == 0)
			{
				value = annuity * max(FSR - StrikePrice, 0.0);
			}
			else
			{
				value = annuity * max(-FSR + StrikePrice, 0.0);
			}
			value_atm = 0.0;
		}
	}
	ExerciseValue = (FSR - StrikePrice) * annuity;
	if (PricingOrValueFlag == 0) return NA * value;
	else return NA * (value - value_atm);
}

double B(double s, double t, double kappa)
{
	return (1.0 - exp(-kappa * (t - s))) / kappa;
}

// 적분 계산 공통함수
// I(t) = Int_0^t sigma(s)^2 A exp(Bs) ds
double Integ(
	double t,
	double A,
	double kappa,
	double* tVol,
	double* Vol,
	long nVol
)
{
	long i;
	long NodeNum = 4;
	long Point = 0;
	double ds = t / (double)NodeNum;
	double s;
	double value = 0.0;
	double sigma;

	for (i = 0; i < NodeNum; i++)
	{
		s = ((double)(i) + 1.0) * ds;
		sigma = Interpolate_Linear(tVol, Vol, nVol, s);
		value += sigma * sigma * A * exp(kappa * s) * ds;
	}
	return value;
}

// 1-factor 모형의 Fixed Payer Swaption 가격 계산
double HW_Swaption(
	long PriceDateYYYYMMDD,	// 평가일 YYYYMMDD
	double NA,				// 액면금액
	double kappa,			// 회귀속도 
	double* tVol,			// 변동성 구간 종점
	double* Vol,            // 구간 변동성
	long nVol,				// 변동성 구간 개수
	double* t,				// 할인채 만기
	double* r,				// 할인채 가격
	long nr,                // 할인채 개수
	double StrikeRate,		// 고정금리(지급부분)
	long MaturityYYYYMMDD,	// 옵션 만기일까지 일수
	long* DatesYYYYMMDD,    // 지급일: 계산일로부터 각 중간지급일까지의 일수
	long nDates             // 지급 회수(계산일 이후 남은 회수)
)
{
	long i;
	double T0, PrevT, T, deltaT;
	double* PT = (double*)malloc(sizeof(double) * (nDates + 1));
	double* Time = (double*)malloc(sizeof(double) * (nDates + 1));
	double VT0, G, H;
	double d1, d2;
	double value;

	if (kappa < -0.002) kappa = -0.002;

	for (i = 0; i < nVol; i++) {
		if (Vol[i] < 0.0) Vol[i] = -Vol[i];
		if (Vol[i] < 1.0e-7) Vol[i] = 1.0e-7;
	}

	T0 = ((double)DayCountAtoB(PriceDateYYYYMMDD, MaturityYYYYMMDD))/ 365.0;
	Time[0] = T0;
	PT[0] = Calc_Discount_Factor(t, r, nr, T0);

	for (i = 0; i < nDates; i++) {
		T = ((double)DayCountAtoB(PriceDateYYYYMMDD, DatesYYYYMMDD[i])) / 365.0;
		Time[i + 1] = T;
		PT[i + 1] = Calc_Discount_Factor(t, r, nr, T);
	}

	VT0 = exp(-2.0 * kappa * T0) * Integ(T0, 1.0, 2.0 * kappa, tVol, Vol, nVol);

	G = PT[nDates];
	PrevT = T0;
	for (i = 0; i < nDates; i++) {
		T = Time[i + 1];
		deltaT = T - PrevT;
		G += StrikeRate * deltaT * PT[i + 1];
		PrevT = T;
	}
	G /= PT[0];

	H = PT[nDates] * B(T0, Time[nDates] , kappa);
	PrevT = T0;
	for (i = 0; i < nDates; i++) {
		T = Time[i + 1];
		deltaT = T - PrevT;
		H += StrikeRate * deltaT * PT[i + 1] * B(T0, T, kappa);
		PrevT = T;
	}
	H /= G * PT[0];

	d1 = -log(G) / (H * sqrt(VT0)) + 0.5 * H * sqrt(VT0);
	d2 = -log(G) / (H * sqrt(VT0)) - 0.5 * H * sqrt(VT0);

	value = PT[0] * (CDF_N(d1) - G * CDF_N(d2));

	if (PT) free(PT);
	if (Time) free(Time);
	return NA * value;
}

DLLEXPORT(long) Pricing_BS_Swaption(
	long FixedPayer0,			// Fixed Payer = 0 Fixed Receiver = 1
	long PriceDate,				// 평가일
	long StartDate,				// 옵션시작일
	long SwapMaturityDate,		// 스왑 만기 YYYYMMDD
	long AnnCpnOneYear,			// 연 이자지급수
	long PricingOrValueFlag,	// 0: Pricing , 1: Valuation
	double kappa,				// FDM HW Kappa
	long AmericanFlag,			// 0: European, 1: American
	long NAutocall,				// 조기상환개수
	long *AutocallDate,			// 조기상환종료일
	double NA,					// 명목원금
	long NVolTerm,
	double* VolTerm,			// 변동성Term
	double* VolArray,			// 변동성
	double StrikePrice,			// 행사금리
	long NTerm,					// 금리 Term 개수
	double* Term,				// 금리 Term Array
	double* Rate,				// 금리 Rate Array
	long DayCountFracFlag,		// 0: Act/365, 1: Act/360 2: Act/Act 3: 30/360
	long VolFlag,				// 0: Black Vol 1: Normal Vol
	long HolidayAutoFlag,		// Holiday 자동계산
	long HolidayNationFlag,		// Holiday 자동계산 1일 때, 0: KRW, 1:USD, 2:GBP
	long NHoliday,				// Holiday 수동계산일 때 Holiday개수
	long* HolidayYYYYMMDD,		// Holiday YYYYMMDD Array
	long TextFlag,				// LoggingFlag
	long GreekFlag,				// Greek 계산여부
	double *ResultValue			// Output : 길이 = 4 + NTerm
)
{	
	long i, j,n;
	double swv;
	long ResultCode = 0;

	long NHolidayInput = 0;
	long* HolidayInput;
	if (HolidayAutoFlag == 0)
	{
		NHolidayInput = NHoliday;
		HolidayInput = (long*)malloc(sizeof(long) * NHolidayInput);
		for (i = 0; i < NHoliday; i++) HolidayInput[i] = HolidayYYYYMMDD[i];
	}
	else
	{
		NHolidayInput = Number_Holiday(PriceDate / 10000,				// 시작연도
									SwapMaturityDate / 10000,           // 종료연도
									HolidayNationFlag					// 0: KRW한국, 1: USD미국, 2: GBP영국
		);
		HolidayInput = (long*)malloc(sizeof(long) * NHolidayInput);
		ResultCode = Mapping_Holiday_CType(
			PriceDate / 10000,				// 시작연도
			SwapMaturityDate / 10000,       // 종료연도
			HolidayNationFlag,				// 국가Flag 0한국 1미국 2영국
			NHolidayInput,					// 배열 개수 Number_Holiday에서 확인
			HolidayInput					// Holiday 들어가는 배열
		);
		for (i = 0; i < min(NHoliday, NHolidayInput); i++) HolidayYYYYMMDD[i] = HolidayInput[i];
	}

	char CalcFunctionName[] = "Pricing_BS_Swaption";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextFlag > 0)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "PriceDate", PriceDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "StartDate", StartDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "SwapMaturityDate", SwapMaturityDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "AnnCpnOneYear", AnnCpnOneYear);
		DumppingTextData(CalcFunctionName, SaveFileName, "PricingOrValueFlag", PricingOrValueFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NA", NA);

		DumppingTextData(CalcFunctionName, SaveFileName, "AmericanFlag", AmericanFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NAutocall", NAutocall);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "AutocallDate", NAutocall, AutocallDate);
		DumppingTextData(CalcFunctionName, SaveFileName, "kappa", kappa);

		DumppingTextData(CalcFunctionName, SaveFileName, "NVolTerm", NVolTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "VolTerm", NVolTerm, VolTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "VolArray", NVolTerm, VolArray);
		DumppingTextData(CalcFunctionName, SaveFileName, "StrikePrice", StrikePrice);
		DumppingTextData(CalcFunctionName, SaveFileName, "NTerm", NTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Term", NTerm, Term);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Term", NTerm, Rate);

		DumppingTextData(CalcFunctionName, SaveFileName, "DayCountFracFlag", DayCountFracFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "VolFlag", VolFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "HolidayAutoFlag", HolidayAutoFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "HolidayNationFlag", HolidayNationFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NHolidayInput", NHolidayInput);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "HolidayInput", NHolidayInput, HolidayInput);
	}

	long TempDate;
	long TempExcelDate;
	long MOD7;
	long SaturSundayFlag;
	long isholiflag;
	StartDate = ParseBusinessDateIfHoliday(StartDate, HolidayYYYYMMDD, NHoliday);

	// StartDate에 맞춰서 EndDate도 세팅
	long EndYYYYMM = SwapMaturityDate / 100;
	long EndDD = StartDate - ((long)(StartDate / 100)) * 100;
	SwapMaturityDate = EndYYYYMM * 100 + EndDD;

	long nCpnDates = 0;
	TempDate = StartDate;
	long TempStartDate = StartDate;
	if (AmericanFlag > 0 && NAutocall > 0) StartDate = max(StartDate, AutocallDate[NAutocall-1]);
	long* CpnDates = Generate_CpnDate_Holiday_IRSwaption(StartDate, SwapMaturityDate, AnnCpnOneYear, nCpnDates, TempDate, NHoliday, HolidayYYYYMMDD);

	double* ResultFSR = ResultValue + 2;
	double* ExerciseValue = ResultValue + 3;
	double* Value = ResultValue;
	double t, Vol;
	if (AmericanFlag == 0)
	{
		t = ((double)DayCountAtoB(PriceDate, StartDate)) / 365.0;
		Vol = Interpolate_Linear(VolTerm, VolArray, NVolTerm, t);
		swv = BS_Swaption(FixedPayer0, PriceDate, StartDate, nCpnDates, CpnDates, NA, Vol, StrikePrice, Term, Rate, NTerm, DayCountFracFlag, VolFlag, PricingOrValueFlag, *ResultFSR, *ExerciseValue);
	}
	else
	{
		long nCpnDates2 = 0;
		long* CpnDates2 = Generate_CpnDate_Holiday_IRSwaption(TempStartDate, SwapMaturityDate, AnnCpnOneYear, nCpnDates2, TempDate, NHoliday, HolidayYYYYMMDD);
		t = ((double)DayCountAtoB(PriceDate, TempStartDate)) / 365.0;
		Vol = Interpolate_Linear(VolTerm, VolArray, NVolTerm, t);

		swv = BS_Swaption(FixedPayer0, PriceDate, TempStartDate, nCpnDates2, CpnDates2, NA, Vol, StrikePrice, Term, Rate, NTerm, DayCountFracFlag, VolFlag, PricingOrValueFlag, *ResultFSR, *ExerciseValue);
		free(CpnDates2);
	}
	Value[0] = swv;

	if (AmericanFlag == 1)
	{
		long Autocall_StartDate;
		long Autocall_SwapMaturityDate;
		long Autocall_nCpnDates = 0;
		long* Autocall_CpnDates;
		
		double ResultPrice, ResultPriceATM, ExercisePrice;
		double temp1 =0.0;
		double VolMin, VolMax, TargetRate, err;
		double RealPrice;
		double tVol = 1.0;
		double nVol = 1;
		double dblErrorRange = 0.0000001;
		double sigma; kappa = max(0.0001, kappa);
		double* VolForFDM = (double*)malloc(sizeof(double) * NVolTerm);
		double ForwardVariance;
		if (VolFlag == 0)
		{
			for (n = 0; n < NVolTerm; n++)
			{
				RealPrice = BS_Swaption(0, PriceDate, StartDate, nCpnDates, CpnDates, NA, VolArray[n], StrikePrice, Term, Rate, NTerm, DayCountFracFlag, VolFlag, 0, temp1, temp1);
				VolMin = 0.0001;
				VolMax = 1.0;
				TargetRate = VolMax;
				VolForFDM[n] = TargetRate;
				for (j = 0; j < 1000; j++)
				{
					err = HW_Swaption(PriceDate, NA, kappa, VolTerm, VolForFDM, n+1, Term, Rate, NTerm, StrikePrice, StartDate, CpnDates, nCpnDates) - RealPrice;
					if (fabs(err) < dblErrorRange) break;
					if (err > 0)
					{
						VolMax = VolForFDM[n];
						VolForFDM[n] = (VolMax + VolMin) / 2.0;
					}
					else
					{
						VolMin = VolForFDM[n];
						VolForFDM[n] = (VolMin + VolMax) / 2.0;
					}
				}
				//VolForFDM[n] = TargetRate;
			}
		}
		else
		{
			for (n = 0; n < NVolTerm; n++)
			{
				RealPrice = BS_Swaption(0, PriceDate, StartDate, nCpnDates, CpnDates, NA, VolArray[n], StrikePrice, Term, Rate, NTerm, DayCountFracFlag, VolFlag, 0, temp1, temp1);
				VolMin = 0.0001;
				VolMax = 1.0;
				TargetRate = VolMax;
				VolForFDM[n] = TargetRate;
				for (j = 0; j < 1000; j++)
				{
					err = HW_Swaption(PriceDate, NA, kappa, VolTerm, VolForFDM, n + 1, Term, Rate, NTerm, StrikePrice, StartDate, CpnDates, nCpnDates) - RealPrice;
					if (fabs(err) < dblErrorRange) break;
					if (err > 0)
					{
						VolMax = VolForFDM[n];
						VolForFDM[n] = (VolMax + VolMin) / 2.0;
					}
					else
					{
						VolMin = VolForFDM[n];
						VolForFDM[n] = (VolMin + VolMax) / 2.0;
					}
				}
				//VolForFDM[n] = TargetRate;
			}
		}

		long NGreed_xt = 200;
		long NGreed_time = DayCountAtoB(PriceDate, StartDate);

		long FDMPricingDate = StartDate;
		long FDMStartTime = ((double)NGreed_time) / 365.0;
		long StartExlDate = CDateToExcelDate(PriceDate);
		
		double swvtemp = 0.0;
		double exercisevalue = 0.0;
		double p, q;
		double xt_min = -0.1;
		double xt_max = 0.3;
		double dxt = (xt_max - xt_min) / ((double)NGreed_xt);
		double dt = 1.0 / 365.0;
		double FDM_t;
		double* xt_array = (double*)malloc(sizeof(double) * NGreed_xt);
		for (i = 0; i < NGreed_xt; i++) xt_array[i] = xt_min + (double)i * dxt;

		double* alpha = (double*)malloc(sizeof(double) * NGreed_xt);
		double* beta = (double*)malloc(sizeof(double) * NGreed_xt);
		double* gamma = (double*)malloc(sizeof(double) * NGreed_xt);
		double* alphatemp = (double*)malloc(sizeof(double) * NGreed_xt);
		double* betatemp = (double*)malloc(sizeof(double) * NGreed_xt);
		double* gammatemp = (double*)malloc(sizeof(double) * NGreed_xt);

		// alpha, beta, gamma는 나중에 정하자
		double w1 = dt/dxt, w2=dt/(dxt*dxt);
		double* t_array = (double*)malloc(sizeof(double) * NGreed_time);
		for (i = 0; i < NGreed_time; i++) t_array[i] = (double)(i + 1) * dt;

		long* Day_array = (long*)malloc(sizeof(long) * NGreed_time);
		for (i = 0; i < NGreed_time; i++) Day_array[i] = ExcelDateToCDate(StartExlDate + i + 1);

		long NTermFDM = NTerm;
		double** ZeroTermFDM = (double**)malloc(sizeof(double*) * NGreed_xt);
		for (i = 0; i < NGreed_xt; i++) ZeroTermFDM[i] = (double*)malloc(sizeof(double) * NTermFDM);

		double** ZeroRateFDM = (double**)malloc(sizeof(double*) * NGreed_xt);
		for (i = 0; i < NGreed_xt; i++) ZeroRateFDM[i] = (double*)malloc(sizeof(double) * NTermFDM);

		double* FDMValue = (double*)malloc(sizeof(double) * NGreed_xt);
		double* FDMExerciseValue = (double*)malloc(sizeof(double) * NGreed_xt);
		double* FDMValue_ATM = (double*)malloc(sizeof(double) * NGreed_xt);

		double s_fdm, t_fdm, xt_fdm,  v, v2, v3, fdmfsr = 0.;

		double* ForwardDiscFactor = (double*)malloc(sizeof(double) * NTermFDM);
		double* HW_B_s_t = (double*)malloc(sizeof(double) * NTermFDM);
		double* HW_QVTerm = (double*)malloc(sizeof(double) * NTermFDM);

		long nzero;
		double A, B, C, R, P0t, P0t1, P0t2, InstantDF, InstantB_s_t, Instant_QVTerm;
		double vo1, vo2;
		for (i = 0; i < NGreed_time; i++)
		{
			FDMPricingDate = Day_array[NGreed_time - 1 - i];
			FDM_t = t_array[NGreed_time - 1 - i];
			s_fdm = FDM_t;
			
			//sigma = Interpolate_Linear(VolTerm, VolForFDM, NVolTerm, FDM_t);

			vo1 = Interpolate_Linear(VolTerm, VolForFDM , NVolTerm, FDM_t);
			vo2 = Interpolate_Linear(VolTerm, VolForFDM, NVolTerm, FDM_t + dt);
			ForwardVariance = (vo2 * vo2 * (FDM_t + dt) - vo1 * vo1 * FDM_t) / dt;
			if (ForwardVariance > 0.0) sigma = sqrt(ForwardVariance);
			else sigma = vo1;

			Vol = Interpolate_Linear(VolTerm, VolArray, NVolTerm, FDM_t);
			// HW Params (t , t + dt)
			InstantDF = Calc_Discount_Factor(Term, Rate, NTerm, s_fdm + dt) / Calc_Discount_Factor(Term, Rate, NTerm, s_fdm);
			InstantB_s_t = Calc_B_s_t(kappa, s_fdm + dt, s_fdm);
			Instant_QVTerm = Calc_QVTerm(kappa, s_fdm + dt, s_fdm, sigma);

			for (j = 0; j < NGreed_xt; j++)
			{
				xt_fdm = xt_array[j];
				R = Rate_A_S_T(xt_fdm, kappa, sigma, s_fdm, s_fdm + dt, NTerm, Term, Rate, InstantDF, InstantB_s_t, Instant_QVTerm);
				p = kappa * 0.5 * w1 * xt_fdm;
				q = 0.5 * sigma * sigma * w2;
				A = -p - q;
				B = 1.0 + 2.0 * q;
				C = p-q;
				if (j == 0)
				{
					alpha[0] = 0.0;
					beta[0] = B + 2.0 * A + (1.0 / InstantDF - 1.0);// +R * dt;
					gamma[0] = C-A;
				}
				else if (j == NGreed_xt - 1)
				{
					alpha[NGreed_xt - 1] = A-C;
					beta[NGreed_xt - 1] = B + 2.0 * C + (1.0 / InstantDF - 1.0);// R* dt;
					gamma[NGreed_xt - 1] = C;
				}
				else
				{
					alpha[j] = A;
					beta[j] = B +(1.0 / InstantDF - 1.0);// R* dt;
					gamma[j] = C;
				}
			}

			if (i == 0)
			{
				/////////////////////////
				// 마지막 날의 가치
				/////////////////////////
				P0t = Calc_Discount_Factor(Term, Rate, NTerm, s_fdm);

				for (n = 0; n < NTermFDM; n++)
				{
					t_fdm = s_fdm + Term[n];
					ForwardDiscFactor[n] = Calc_Discount_Factor(Term, Rate, NTerm, t_fdm) / Calc_Discount_Factor(Term, Rate, NTerm, s_fdm);
					HW_B_s_t[n] = Calc_B_s_t(kappa, t_fdm, s_fdm);
					HW_QVTerm[n] = Calc_QVTerm(kappa, t_fdm, s_fdm, sigma);
				}

				for (j = 0; j < NGreed_xt; j++)
				{
					xt_fdm = xt_array[j];
					for (n = 0; n < NTermFDM; n++)
					{
						t_fdm = s_fdm + Term[n];
						ZeroTermFDM[j][n] = Term[n];
						ZeroRateFDM[j][n] = Rate_A_S_T(xt_fdm, kappa, sigma, s_fdm, t_fdm, NTerm, Term, Rate, ForwardDiscFactor[n], HW_B_s_t[n], HW_QVTerm[n]);
					}

					FDMValue[j] = BS_Swaption(FixedPayer0,FDMPricingDate, StartDate, nCpnDates, CpnDates, NA, Vol, StrikePrice, ZeroTermFDM[j], ZeroRateFDM[j], NTermFDM, DayCountFracFlag, VolFlag, 0, fdmfsr, v);
					FDMExerciseValue[j] = v;
					FDMValue_ATM[j] = BS_Swaption(FixedPayer0,FDMPricingDate, StartDate, nCpnDates, CpnDates, NA, Vol, *ResultFSR, ZeroTermFDM[j], ZeroRateFDM[j], NTermFDM, DayCountFracFlag, VolFlag, 0, v2, v3);
				}
			}
			nzero = 0;
			for (j = 0; j < NGreed_xt; j++) if (v > 0. && v < 1.0e-7) nzero += 1;

			// BS Option Price를 기반으로 한 Pricing

			Tri_diagonal_Fast(
				alpha,    // Tridiagonal Matrix에서 왼쪽 대각선 행렬
				beta,     // Tridiagonal Matrix에서 중앙 대각선 행렬
				gamma,    // Tridiagonal Matrix에서 오른쪽 대각선 행렬
				FDMValue,     // V(T1)
				NGreed_xt,           // 대각선 행렬들의 길이
				alphatemp,// 임시 행렬1 
				betatemp, // 임시 행렬2
				gammatemp // 임시 행렬3
			);

			// ATM 가치를 기반으로한 Pricing

			Tri_diagonal_Fast(
				alpha,    // Tridiagonal Matrix에서 왼쪽 대각선 행렬
				beta,     // Tridiagonal Matrix에서 중앙 대각선 행렬
				gamma,    // Tridiagonal Matrix에서 오른쪽 대각선 행렬
				FDMValue_ATM,     // V(T1)
				NGreed_xt,           // 대각선 행렬들의 길이
				alphatemp,// 임시 행렬1 
				betatemp, // 임시 행렬2
				gammatemp // 임시 행렬3
			);

			
			if (i != 0 && isin(FDMPricingDate, AutocallDate, NAutocall))
			{
				/////////////////////////
				// Autocall Date Pricing
				/////////////////////////
				Autocall_StartDate = FDMPricingDate;
				Autocall_SwapMaturityDate = SwapMaturityDate;
				Autocall_CpnDates = Generate_CpnDate_Holiday_IRSwaption(Autocall_StartDate, Autocall_SwapMaturityDate, AnnCpnOneYear, Autocall_nCpnDates, TempDate, NHoliday, HolidayYYYYMMDD);

				for (n = 0; n < NTermFDM; n++)
				{
					t_fdm = s_fdm + Term[n];
					ForwardDiscFactor[n] = Calc_Discount_Factor(Term, Rate, NTerm, t_fdm) / Calc_Discount_Factor(Term, Rate, NTerm, s_fdm);
					HW_B_s_t[n] = Calc_B_s_t(kappa, t_fdm, s_fdm);
					HW_QVTerm[n] = Calc_QVTerm(kappa, t_fdm, s_fdm, sigma);
				}

				for (j = 0; j < NGreed_xt; j++)
				{
					xt_fdm = xt_array[j];
					for (n = 0; n < NTermFDM; n++)
					{
						t_fdm = s_fdm + Term[n];
						ZeroTermFDM[j][n] = Term[n];
						ZeroRateFDM[j][n] = Rate_A_S_T(xt_fdm, kappa, sigma, s_fdm, t_fdm, NTerm, Term, Rate, ForwardDiscFactor[n], HW_B_s_t[n], HW_QVTerm[n]);
					}

					FDMValue[j] = max(FDMValue[j], BS_Swaption(FixedPayer0,FDMPricingDate, Autocall_StartDate, Autocall_nCpnDates, Autocall_CpnDates, NA, Vol, StrikePrice, ZeroTermFDM[j], ZeroRateFDM[j], NTermFDM, DayCountFracFlag, VolFlag, 0, fdmfsr, v));
					FDMValue_ATM[j] = max(FDMValue_ATM[j], BS_Swaption(FixedPayer0,FDMPricingDate, Autocall_StartDate, Autocall_nCpnDates, Autocall_CpnDates, NA, Vol, *ResultFSR, ZeroTermFDM[j], ZeroRateFDM[j], NTermFDM, DayCountFracFlag, VolFlag, 0, v2, v3));
				}

				free(Autocall_CpnDates);
			}
		}

		ResultPrice = Interpolate_Linear(xt_array, FDMValue, NGreed_xt, 0.0);
		ResultPriceATM = Interpolate_Linear(xt_array, FDMValue_ATM, NGreed_xt, 0.0);
		*ExerciseValue = Interpolate_Linear(xt_array, FDMExerciseValue, NGreed_xt, 0.0) * P0t;
		if (PricingOrValueFlag == 0) Value[0] = ResultPrice;
		else Value[0] = ResultPrice - ResultPriceATM;

		free(xt_array);
		free(t_array);
		free(Day_array);
		for (i = 0; i < NGreed_xt; i++)
		{
			free(ZeroTermFDM[i]);
			free(ZeroRateFDM[i]);
		}
		free(ZeroTermFDM);
		free(ZeroRateFDM);
		free(ForwardDiscFactor);
		free(HW_B_s_t);
		free(HW_QVTerm);
		free(FDMValue);
		free(FDMExerciseValue);
		free(FDMValue_ATM);
		free(alpha);
		free(alphatemp);
		free(beta);
		free(betatemp);
		free(gamma);
		free(gammatemp);
		free(VolForFDM);
	}
	double* PV01_Curve = ResultValue + 1;
	double* KeyRatePV01_Curve = ResultValue + 4;

	if (GreekFlag > 0)
	{
		long nCpnDates3 = 0;
		long* CpnDates3 = Generate_CpnDate_Holiday_IRSwaption(TempStartDate, SwapMaturityDate, AnnCpnOneYear, nCpnDates3, TempDate, NHoliday, HolidayYYYYMMDD);
		double TempFSR = 0.0;
		double TempExercise = 0.0;
		double* RateForGreek = (double*)malloc(sizeof(double) * NTerm);
		for (i = 0; i < NTerm; i++) RateForGreek[i] = Rate[i] + 0.0001;
		t = ((double)DayCountAtoB(PriceDate, TempStartDate)) / 365.0;
		Vol = Interpolate_Linear(VolTerm, VolArray, NVolTerm, t);
		PV01_Curve[0] = BS_Swaption(FixedPayer0,PriceDate, TempStartDate, nCpnDates3, CpnDates3, NA, Vol, StrikePrice, Term, RateForGreek, NTerm, DayCountFracFlag, VolFlag, PricingOrValueFlag, TempFSR, TempExercise) - swv;

		for (i = 0; i < NTerm; i++)
		{
			for (j = 0; j < NTerm; j++)
			{
				if (i == j) RateForGreek[j] = Rate[j] + 0.0001;
				else RateForGreek[j] = Rate[j];
			}
			KeyRatePV01_Curve[i] = BS_Swaption(FixedPayer0,PriceDate, TempStartDate, nCpnDates3, CpnDates3, NA, Vol, StrikePrice, Term, RateForGreek, NTerm, DayCountFracFlag, VolFlag, PricingOrValueFlag, TempFSR, TempExercise) - swv;
		}

		free(RateForGreek);
		free(CpnDates3);
	}
	free(HolidayInput);
	free(CpnDates);
	return 1;
}

DLLEXPORT(long) Pricing_BS_SwaptionPrice_to_Volatiliy(
	long FixedPayer0,			// Fixed Payer = 0 Fixed Receiver = 1
	long PriceDate,				// 평가일
	long StartDate,				// 옵션시작일
	long SwapMaturityDate,		// 스왑 만기 YYYYMMDD
	long AnnCpnOneYear,			// 연 이자지급수
	double kappa,				// FDM HW Kappa
	long AmericanFlag,			// 0: European, 1: American
	long NAutocall,				// 조기상환개수
	long* AutocallDate,			// 조기상환종료일
	double NA,					// 명목원금
	long NTerm,					// 금리 Term 개수
	double* Term,				// 금리 Term Array
	double* Rate,				// 금리 Rate Array
	long DayCountFracFlag,		// 0: Act/365, 1: Act/360 2: Act/Act 3: 30/360
	long VolFlag,				// 0: Black Vol 1: Normal Vol
	long HolidayAutoFlag,		// Holiday 자동계산
	long HolidayNationFlag,		// Holiday 자동계산 1일 때, 0: KRW, 1:USD, 2:GBP
	long NHoliday,				// Holiday 수동계산일 때 Holiday개수
	long* HolidayYYYYMMDD,		// Holiday YYYYMMDD Array
	double MarketPrice,
	double* ResultValue			// Output : 길이 = 4 + NTerm
)
{
	long i, j;
	long PricingOrValueFlag = 0;
	long NVolTerm = 1;
	double VolTerm[1] = { 1.0 };
	double MaxRate = 2.0;
	double MinRate = 0.0001;
	double TargetRate = MaxRate;
	double* ResultArray = (double*)malloc(sizeof(double) * 100);

	long nCpnDates = 0;
	long TempDate = StartDate;
	long TempStartDate = StartDate;
	if (AmericanFlag > 0 && NAutocall > 0) StartDate = max(StartDate, AutocallDate[0]);
	long* CpnDates = Generate_CpnDate_Holiday_IRSwaption(StartDate, SwapMaturityDate, AnnCpnOneYear, nCpnDates, TempDate, NHoliday, HolidayYYYYMMDD);
	double FSR = ForwardSwapRate(PriceDate, StartDate, nCpnDates, CpnDates, NTerm, Term, Rate, NTerm, Term, Rate, DayCountFracFlag);
	double CalcRate = 0.;
	double dblErrorRange = 0.0000001;
	for (j = 0; j < 1000; j++)
	{
		Pricing_BS_Swaption(
			FixedPayer0, PriceDate, StartDate, SwapMaturityDate, AnnCpnOneYear,			// 연 이자지급수
			PricingOrValueFlag, kappa, AmericanFlag, NAutocall, AutocallDate,			// 조기상환종료일
			NA, NVolTerm, VolTerm, &TargetRate, FSR,			// 행사금리
			NTerm, Term, Rate, DayCountFracFlag, VolFlag,				// 0: Black Vol 1: Normal Vol
			HolidayAutoFlag, HolidayNationFlag, NHoliday, HolidayYYYYMMDD, 0,				// LoggingFlag
			0, ResultArray			// Output : 길이 = 4 + NTerm
		);
		CalcRate = ResultArray[0] - MarketPrice;
		if (fabs(CalcRate/NA) < dblErrorRange) break;
		if (CalcRate > 0.)
		{
			MaxRate = TargetRate;
			TargetRate = (MaxRate + MinRate) / 2.0;
		}
		else
		{
			MinRate = TargetRate;
			TargetRate = (MinRate + MaxRate) / 2.0;
		}

	}
	ResultValue[0] = TargetRate;
	free(ResultArray);
	free(CpnDates);
	return 1;
}