#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <crtdbg.h>

#include "CalcDate.h"
#include "Util.h"
#include "GetTextDump.h"
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

#ifndef strcpy_s
#include <string.h>
#endif

double IRS(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long FirstCpnDate, long Number_Ann_CPN, long* CpnDate, long nCpnDate, long Convention1Y, long NRate, double* RateTerm, double* Rate, long InterpFlag);

double round_double(double x, long n_decimal)
{
	long i;

	double div = 1.0;
	for (i = 0; i < n_decimal; i++) div *= 10.0;
	return floor(x * div + 0.5) / div;
}

double Bootstrapping_Deposit(double mktrate, long YYYYMMDD1, long YYYYMMDD2, long convention1Y)
{
	double tau= (double)DayCountAtoB(YYYYMMDD1, YYYYMMDD2);

	double DF_st;
	if (convention1Y == 360) DF_st = 1.0 / (1.0 + mktrate * tau /360.0);
	else DF_st = 1.0 / (1.0 + mktrate * tau / 365.0);
	double z_st = 365.0 / tau * -log(DF_st);
	return z_st;
}

double Bootstrapping_Futures(long PriceDateYYYYMMDD, double mktrate, double DF_0_tstart, long YYYYMMDD1, long YYYYMMDD2, long convention1Y)
{
	double tau = ((double)DayCountAtoB(YYYYMMDD1, YYYYMMDD2));
	double DF2;
	if (convention1Y == 360) DF2 = 1.0 / (1.0 + mktrate * tau / 360.0);
	else DF2 = 1.0 / (1.0 + mktrate * tau / 365.0);

	double tau2 = ((double)DayCountAtoB(PriceDateYYYYMMDD, YYYYMMDD2));
	double DF_st = DF_0_tstart * DF2;
	double z_st = 365.0 / tau2 * -log(DF_st);
	return z_st;
}

double CalcForward(long PriceDateYYYYMMDD, long ForwardStartYYYYMMDD, long ForwardEndYYYYMMDD, long Conv1Y, long NZero, double* ZeroTerm, double* ZeroRate)
{
	double Time;
	if (Conv1Y == 360) Time = 360.0;
	else Time = 365.0;
	double T0, TN, deltaT;
	double r0, rN;
	double s;

	T0 = ((double)DayCountAtoB(PriceDateYYYYMMDD, ForwardStartYYYYMMDD)) / 365.0;
	TN = ((double)DayCountAtoB(PriceDateYYYYMMDD, ForwardEndYYYYMMDD)) / 365.0;
	deltaT = ((double)DayCountAtoB(ForwardStartYYYYMMDD, ForwardEndYYYYMMDD))/Time;
	r0 = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, T0);
	rN = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, TN);
	s = (exp(-r0 * T0) - exp(-rN * TN)) / (deltaT * exp(-rN * TN));
	return s;
}

long MonthDateisSame(long YYYYMMDD1, long YYYYMMDD2)
{
	long Year = (long)YYYYMMDD1 / 10000;
	long Month = (long)(YYYYMMDD1 - Year * 10000) / 100;
	long Day = (long)(YYYYMMDD1 - Year * 10000 - Month * 100);

	long Year2 = (long)YYYYMMDD2 / 10000;
	long Month2 = (long)(YYYYMMDD2 - Year2 * 10000) / 100;
	long Day2 = (long)(YYYYMMDD2 - Year2 * 10000 - Month2 * 100);
	if ((Month == Month2) && (Day == Day2)) return 1;
	else 0;
}


double DF_From_Swap(long PriceDate_C, long* CpnDate, long NCpnDate, double swaprate, long NZero, double* ZeroTerm, double* ZeroRate, long DayCount1Y_Fix, long FirstCpnDate, long InterpFlag)
{
	long i;
	long tau;
	double t = 0.;
	double Disc = 1.0;
	double s;
	double deltat = 0.25;
	double r = 0.0;
	double Time_Fix = 365.0;

	if (DayCount1Y_Fix == 360) Time_Fix = 360.0;
	else Time_Fix = 365.0;

	double DF0 = 1.0;
	double t0, r0;

	if (PriceDate_C != FirstCpnDate)
	{
		t0 = ((double)DayCountAtoB(PriceDate_C, FirstCpnDate) / 365.0);
		if (InterpFlag == 0 || InterpFlag == 1) r0 = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, t0);
		else r0 = CubicSpline(NZero, ZeroTerm, ZeroRate, t0);
		DF0 = exp(-r0 * t0);
	}

	s = DF0;
	for (i = 0; i < NCpnDate-1; i++)
	{
		tau = DayCountAtoB(PriceDate_C, CpnDate[i]);
		t = ((double)tau) / 365.0;

		if (i == 0) deltat = ((double)(DayCountAtoB(FirstCpnDate, CpnDate[i])) ) / Time_Fix;
		else deltat = ((double)(DayCountAtoB(CpnDate[i-1],CpnDate[i]) )) / Time_Fix;
		if (InterpFlag == 0) r = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, t);
		else if (InterpFlag == 1)
		{
			r = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, t, 1);
		}
		else r = CubicSpline(NZero, ZeroTerm, ZeroRate, t);

		Disc = exp(-r * t);
		s -= swaprate * deltat * Disc;
	}
	deltat = (double)(DayCountAtoB(CpnDate[NCpnDate - 2], CpnDate[NCpnDate - 1])) / Time_Fix;

	return s / (1.0 + swaprate * deltat);
}

long LastDayCountHaveLeapDate(long YYYYMMDD)
{
	long Year = (long)YYYYMMDD / 10000;
	long Month = (long)(YYYYMMDD - Year * 10000) / 100;
	long Day = (long)(YYYYMMDD - Year * 10000 - Month * 100);
	long PrevYear = Year - 1;
	long leap = LeapCheck(PrevYear);
	if (leap == 1)
	{
		// 작년이 윤년인경우이면서 쿠폰날짜가 2월 28일 이전
		if ((long)(YYYYMMDD - Year * 10000) <= 228) return 1;
		else return 0;
	}
	else return 0;
}

long* Generate_Date(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long AnnCpnOneYear, long &lenArray, long& FirstCpnDate)
{
	long i, j;

	long PriceYYYY = (long)PriceDateYYYYMMDD / 10000;
	long PriceMM = (long)(PriceDateYYYYMMDD - PriceYYYY * 10000) / 100;

	long SwapMatYYYY = (long)SwapMat_YYYYMMDD / 10000;
	long SwapMatMM = (long)(SwapMat_YYYYMMDD - SwapMatYYYY * 10000) / 100;

	long n = ((SwapMat_YYYYMMDD/ 10000 - PriceDateYYYYMMDD /10000) + 2) * AnnCpnOneYear;
	long narray = 0;
	long CpnDate;
	long m = max(1, 12 / AnnCpnOneYear);
	for (i = 0; i < n; i++)
	{
		if (i == 0) CpnDate = SwapMat_YYYYMMDD;
		else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i*m);
		if (DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7)
		{
			FirstCpnDate = CpnDate;
			break;
		}
		if (CpnDate <= PriceDateYYYYMMDD ) break;
		narray++;
	}

	long* ResultCpnDate = (long*)malloc(sizeof(long) * narray);
	long CpnDateExcel;
	long MOD7;
	long SaturSundayFlag;
	for (i = 0; i < n; i++)
	{
		if (i == 0) CpnDate = SwapMat_YYYYMMDD;
		else CpnDate = EDate_Cpp(SwapMat_YYYYMMDD, -i*m);

		if (CpnDate <= PriceDateYYYYMMDD|| DayCountAtoB(PriceDateYYYYMMDD, CpnDate) < 7) break;
		else
		{
			CpnDateExcel = CDateToExcelDate(CpnDate);
			MOD7 = CpnDateExcel % 7;
			if (MOD7 == 1 || MOD7 == 0) SaturSundayFlag = 1;
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
					if (MOD7 != 1 && MOD7 != 0)
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

long SaveErrorName2(char* Error, char ErrorName[100])
{
	long k;
	long i;
	long Ascii;
	k = 0;
	for (i = 0; i < 100; i++)
	{
		Ascii = (long)ErrorName[i];
		if ((Ascii >= 48 && Ascii <= 57) || (Ascii >= 65 && Ascii <= 90) || (Ascii >= 97 && Ascii <= 122) || (Ascii == 32))
		{
			Error[k] = ErrorName[i];
			k++;
		}
		else
		{
			break;
		}
	}
	return -1;
}

double CPN_Bond_Pricing(long PricingDate, long BondMaturityDate, long Number_Ann_CPN, double Yield_To_Maturity, double CouponRate, long Convention1Y)
{
	long i;
	long n;

	double NA = 100.0;

	long Maturity_Day = (PricingDate, BondMaturityDate);	
	
	long NDays;
	long FirstCpnDate = PricingDate;
	long* CpnDate = Generate_Date(PricingDate, BondMaturityDate, Number_Ann_CPN, NDays, FirstCpnDate);
	
	double Time = 365.0;
	if (Convention1Y == 360) Time = 360.0;
	else Time = 365.0;

	double T = 0.0;
	double DF = 1.0;
	double deltat;
	double PV = 0.0;
	for (i = 0; i < NDays; i++)
	{
		T = ((double)DayCountAtoB(PricingDate, CpnDate[i])) / 365.0;
		DF = 1.0 / pow((1.0 + Yield_To_Maturity / (double)Number_Ann_CPN), (double)(i + 1));

		if (i == 0) deltat = ((double)DayCountAtoB(FirstCpnDate, CpnDate[i]) / Time);
		else deltat = ((double)DayCountAtoB(CpnDate[i - 1], CpnDate[i]) / Time);
		PV += CouponRate * deltat * DF * NA;
	}
	PV += NA * DF;
	free(CpnDate);
	return PV;
}

double CalcDiscountFromCouponBond(long PricingDate, long BondMaturityDate, long Number_Ann_CPN, double CouponRate, long Convention1Y, double PV_Bond, long NZero, double* ZeroTerm, double* ZeroRate, long InterpFlag)
{
	long i;
	long n;

	double NA = 100.0;

	long Maturity_Day = (PricingDate, BondMaturityDate);

	long NDays;
	long FirstCpnDate = PricingDate;
	long* CpnDate = Generate_Date(PricingDate, BondMaturityDate, Number_Ann_CPN, NDays, FirstCpnDate);

	double Time = 365.0;
	if (Convention1Y == 360) Time = 360.0;
	else Time = 365.0;

	double T = 0.0;
	double DF = 1.0;
	double deltat = 0.0;
	double a, b, r;
	a = PV_Bond;
	for (i = 0; i < NDays - 1; i++)
	{
		T = ((double)DayCountAtoB(PricingDate, CpnDate[i])) / 365.0;
		if (InterpFlag == 0) r = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, T);
		else if (InterpFlag == 1)
		{
			r = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, T, 1);
		}
		else 
		{ 
			r = CubicSpline(NZero, ZeroTerm, ZeroRate, T); 
		}

		DF = exp(-r * T);
		if (i == 0) deltat = ((double)DayCountAtoB(FirstCpnDate, CpnDate[i]) / Time);
		else deltat = ((double)DayCountAtoB(CpnDate[i - 1], CpnDate[i]) / Time);
		a = a - CouponRate * deltat * DF * NA;
	}
	double CF_N = NA * (1.0 + CouponRate * deltat);
	free(CpnDate);
	return a / CF_N;
}


double Accrued_Interest(double Notional, double CpnRate, double Accrued_dt)
{
	return Notional * CpnRate * Accrued_dt;
}

long ZeroCurveGenerate_Bond(
	long PriceDate_C,

	long NShortTerm,
	long* ShortTerm_Maturity_C,
	double* ShortTerm_Rate,
	long* ShortTerm_OneYConvention,

	long NSwap,
	long* SwapMaturity_C,
	long* SwapPayDate_C,
	long* NCPN_Ann,
	double* SwapRate,
	long* Swap_OneYConvention,

	long NResultCurve,
	double* ResultCurveTerm,
	double* ResultCurve,
	double* ResultDF,
	double* ResultMktRate,
	long InterpFlag
)
{
	long i;
	long k;
	long N;

	double r; 
	
	long NCPNBond =NSwap;
	long* BondMaturityDate = SwapMaturity_C;
	long* BondPayDate = SwapPayDate_C;
	double* YTM = SwapRate;
	long* Bond_OneYConvention = Swap_OneYConvention;

	long NZero = (NShortTerm + NSwap);
	double* ZeroTerm = (double*)malloc(sizeof(double) * NZero);
	double* ZeroRate = (double*)malloc(sizeof(double) * NZero);
	N = NShortTerm;
	for (i = 0; i < N; i++)
	{
		ZeroTerm[i] = ((double)DayCountAtoB(PriceDate_C,ShortTerm_Maturity_C[i]))/365.0;
		ZeroRate[i] = Bootstrapping_Deposit(ShortTerm_Rate[i], PriceDate_C, ShortTerm_Maturity_C[i], ShortTerm_OneYConvention[i]);
	}

	double PV_Bond, DF_T, t;

	for (i = 0; i < NCPNBond; i++)
	{
		PV_Bond = CPN_Bond_Pricing(PriceDate_C, BondMaturityDate[i], NCPN_Ann[i], YTM[i], YTM[i], Bond_OneYConvention[i]);
		DF_T = CalcDiscountFromCouponBond(PriceDate_C, BondMaturityDate[i], NCPN_Ann[i], YTM[i], Bond_OneYConvention[i], PV_Bond, N, ZeroTerm, ZeroRate, InterpFlag);
		t = ((double)DayCountAtoB(PriceDate_C, BondMaturityDate[i])) / 365.0;
		ZeroTerm[i + NShortTerm] = t;
		ZeroRate[i + NShortTerm] = -1.0 / t * log(DF_T);
		N += 1;
	}

	for (i = 0; i < NShortTerm; i++)
	{
		ResultCurveTerm[i] = ZeroTerm[i];
		ResultCurve[i] = ZeroRate[i];
		ResultDF[i] = exp(-ZeroTerm[i] * ZeroRate[i]);
		ResultMktRate[i] = ShortTerm_Rate[i];
	}
	for (i = 0; i < NCPNBond; i++)
	{
		if (BondMaturityDate[i] != BondPayDate[i])
		{
			t = ((double)DayCountAtoB(PriceDate_C, BondPayDate[i])) / 365.0;
			if (InterpFlag == 0 || InterpFlag == 1) r = Interpolate_Linear(ZeroTerm, ZeroRate, NZero, t, 1);
			else r = CubicSpline(NZero, ZeroTerm, ZeroRate, t);
			ResultCurveTerm[i + NShortTerm] = t;
			ResultCurve[i + NShortTerm] = r;
		}
		else
		{
			ResultCurveTerm[i + NShortTerm] = ZeroTerm[i + NShortTerm];
			ResultCurve[i + NShortTerm] = ZeroRate[i + NShortTerm];
		}
		ResultDF[i + NShortTerm] = exp(-ResultCurveTerm[i + NShortTerm] * ResultCurve[i + NShortTerm]);
		ResultMktRate[i + NShortTerm] = YTM[i];
	}
	


	free(ZeroTerm);
	free(ZeroRate);
	return 1;
}

//////////////////////////
// Root Finder ZeroCurve Calibration
//////////////////////////
long ZeroCurveGenerate_IRS2(
	long PriceDate_C,

	long NShortTerm,
	long* ShortTerm_Maturity_C,
	double* ShortTerm_Rate,
	long* ShortTerm_OneYConvention,

	long NForward,
	long* ForwardStart_C,
	long* ForwardEnd_C,
	long* ForwardPayDate_C,
	double* ForwardRate,
	long* Forward_OneYConvention,

	long NSwap,
	long* SwapMaturity_C,
	long* SwapPayDate_C,
	long* NCPN_Ann,
	double* SwapRate,
	long* Swap_OneYConvention_Fix,

	long NResultCurve,
	double* ResultCurveTerm,
	double* ResultCurve,
	double* ResultDF,
	double* ResultMktRate,
	long InterpFlag
)
{
	long i;
	long j;
	long ncurve = 0;

	long* CpnDate;
	long nCpnArray = 0;
	long leapflag = 0;
	long CpnDateisBeforeFeb;
	double disc = 1.0;
	double tau = 0.0;
	long PrevCpnDate;
	long FirstCpnDate = 0;

	double dblErrorRange = 0.0000001;
	double ObjValue = 0.0;
	double MaxRate;
	double MinRate;
	double TargetRate;
	double* Rate;
	double* Term;
	double PrevRate;
	double CalcRate;

	double* ZeroTerm = (double*)malloc(sizeof(double) * NResultCurve);
	double* ZeroRate = (double*)malloc(sizeof(double) * NResultCurve);
	double* DiscFactor = (double*)malloc(sizeof(double) * NResultCurve);
	double* Mkt= (double*)malloc(sizeof(double) * NResultCurve);
	double t;
	for (i = 0; i < NShortTerm; i++)
	{
		t = ((double)DayCountAtoB(PriceDate_C, ShortTerm_Maturity_C[i])) / 365.0;
		ZeroTerm[i] = t;
		ZeroRate[i] = Bootstrapping_Deposit(ShortTerm_Rate[i], PriceDate_C, ShortTerm_Maturity_C[i], ShortTerm_OneYConvention[i]);
		DiscFactor[i] = exp(-ZeroTerm[i] * ZeroRate[i]);
		Mkt[i] = ShortTerm_Rate[i];
		ncurve++;
	}

	long maxshortday = ShortTerm_Maturity_C[NShortTerm - 1];
	double tstart, tend, DF_0_to_tstart, r_to_tstart;
	double F;
	for (i = 0; i < NForward; i++)
	{
		if (ForwardEnd_C[i] > maxshortday)
		{
			tau = (double)(DayCountAtoB(PriceDate_C, ForwardPayDate_C[i]));
			t = tau / 365.0;

			MaxRate = ForwardRate[i] + 0.25;
			MinRate = ForwardRate[i] - 0.15;
			TargetRate = MaxRate;

			Rate = (double*)malloc(sizeof(double) * (ncurve + 1));
			Term = (double*)malloc(sizeof(double) * (ncurve + 1));
			PrevRate = MaxRate;
			for (j = 0; j < ncurve; j++)
			{
				Rate[j] = ZeroRate[j];
				Term[j] = ZeroTerm[j];
			}
			Term[ncurve] = t;

			for (j = 0; j < 1000; j++)
			{
				Rate[ncurve] = TargetRate;
				F = CalcForward(PriceDate_C, ForwardStart_C[i], ForwardEnd_C[i], Forward_OneYConvention[i], ncurve + 1, Term, Rate);
				CalcRate = F - ForwardRate[i];
				if (fabs(CalcRate) < dblErrorRange) break;
				if (CalcRate > 0)
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

			free(Rate);
			free(Term);

			ZeroTerm[ncurve] = tau / 365.0;
			ZeroRate[ncurve] = TargetRate;
			DiscFactor[ncurve] = exp(-ZeroTerm[ncurve] * ZeroRate[ncurve]);
			Mkt[ncurve] = ForwardRate[i];
			ncurve++;
		}
	}

	for (i = 0; i < NSwap; i++)
	{
		FirstCpnDate = PriceDate_C;
		if (SwapMaturity_C[i] > PriceDate_C)
		{

			CpnDate = Generate_Date(PriceDate_C, SwapMaturity_C[i], NCPN_Ann[i], nCpnArray, FirstCpnDate);
			tau = (double)(DayCountAtoB(PriceDate_C, SwapPayDate_C[i]));
			t = tau / 365.0;

			MaxRate = SwapRate[i] + 0.25;
			MinRate = SwapRate[i] - 0.15;
			TargetRate = MaxRate;

			Rate = (double*)malloc(sizeof(double) * (ncurve +1));
			Term = (double*)malloc(sizeof(double) * (ncurve +1));
			PrevRate = MaxRate;
			for (j = 0; j < ncurve; j++)
			{
				Rate[j] = ZeroRate[j];
				Term[j] = ZeroTerm[j];
			}
			Term[ncurve] = t;

			for (j = 0; j < 1000; j++)
			{
				Rate[ncurve] = TargetRate;

				CalcRate = IRS(PriceDate_C, SwapMaturity_C[i], FirstCpnDate, NCPN_Ann[i], CpnDate, nCpnArray, Swap_OneYConvention_Fix[i], ncurve + 1, Term, Rate, InterpFlag) - SwapRate[i];
				if (fabs(CalcRate) < dblErrorRange) break;
				if (CalcRate > 0)
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
			
			free(CpnDate);
			free(Rate);
			free(Term);

			ZeroTerm[ncurve] = tau / 365.0;
			ZeroRate[ncurve] = TargetRate;
			DiscFactor[ncurve] = exp(-ZeroTerm[ncurve] * ZeroRate[ncurve]);
			Mkt[ncurve] = SwapRate[i];
			ncurve++;
		}
	}

	for (i = 0; i < ncurve; i++)
	{
		ResultCurveTerm[i] = ZeroTerm[i];
		ResultCurve[i] = ZeroRate[i];
		ResultDF[i] = DiscFactor[i];
		ResultMktRate[i] = Mkt[i];
	}

	free(ZeroTerm);
	free(ZeroRate);
	free(DiscFactor);
	free(Mkt);
	return 1;
}


long ZeroCurveGenerate_IRS(
	long PriceDate_C,

	long NShortTerm,
	long* ShortTerm_Maturity_C,
	double* ShortTerm_Rate,
	long* ShortTerm_OneYConvention,

	long NForward,
	long* ForwardStart_C,
	long* ForwardEnd_C,
	double* ForwardRate,
	long* Forward_OneYConvention,

	long NSwap,
	long* SwapMaturity_C,
	long* NCPN_Ann,
	double* SwapRate,
	long* Swap_OneYConvention_Fix,

	long NResultCurve,
	double* ResultCurveTerm,
	double* ResultCurve,
	double* ResultDF,
	double* ResultMktRate,
	long InterpFlag
)
{
	long i;
	long j;
	long ncurve = 0;
	
	double* ZeroTerm = (double*)malloc(sizeof(double) * NResultCurve);
	double* ZeroRate = (double*)malloc(sizeof(double) * NResultCurve);
	double* DiscFactor = (double*)malloc(sizeof(double) * NResultCurve);
	double* Mkt = (double*)malloc(sizeof(double) * NResultCurve);
	double t;
	for (i = 0; i < NShortTerm; i++)
	{
		t = ((double)DayCountAtoB(PriceDate_C, ShortTerm_Maturity_C[i]))/365.0;
		ZeroTerm[i] = t;
		ZeroRate[i] = Bootstrapping_Deposit(ShortTerm_Rate[i], PriceDate_C, ShortTerm_Maturity_C[i], ShortTerm_OneYConvention[i]);
		DiscFactor[i] = exp(-ZeroTerm[i] * ZeroRate[i]);
		Mkt[i] = ShortTerm_Rate[i];
		ncurve++;
	}

	long maxshortday = ShortTerm_Maturity_C[NShortTerm - 1];
	double tstart, tend, DF_0_to_tstart, r_to_tstart;
	for (i = 0; i < NForward; i++)
	{
		if (ForwardEnd_C[i] > maxshortday)
		{
			tstart = ((double)DayCountAtoB(PriceDate_C, ForwardStart_C[i])) / 365.0;
			tend = ((double)DayCountAtoB(PriceDate_C, ForwardEnd_C[i])) / 365.0;
			if (InterpFlag == 0) r_to_tstart = Interpolate_Linear(ZeroTerm, ZeroRate, ncurve, tstart);
			else if (InterpFlag == 1) r_to_tstart = Interpolate_Linear(ZeroTerm, ZeroRate, ncurve, tstart, 1);
			else r_to_tstart = CubicSpline(ncurve, ZeroTerm, ZeroRate, tstart);

			DF_0_to_tstart = exp(-r_to_tstart * tstart);
			ZeroTerm[ncurve] = tend;
			ZeroRate[ncurve] = Bootstrapping_Futures(PriceDate_C, ForwardRate[i], DF_0_to_tstart, ForwardStart_C[i], ForwardEnd_C[i], Forward_OneYConvention[i]);
			DiscFactor[ncurve] = exp(-ZeroTerm[ncurve] * ZeroRate[ncurve]);
			Mkt[ncurve] = ForwardRate[i];
			ncurve++;
		}
	}

	long *CpnDate;
	long nCpnArray = 0;
	long SameMonthDay = 0;
	long leapflag = 0;
	long CpnDateisBeforeFeb;
	double disc = 1.0;
	double tau = 0.0;
	long PrevCpnDate;
	long FirstCpnDate = 0;
	for (i = 0; i < NSwap; i++)
	{
		FirstCpnDate = PriceDate_C;
		if (SwapMaturity_C[i] > PriceDate_C)
		{
			SameMonthDay = MonthDateisSame(PriceDate_C, SwapMaturity_C[i]);

			CpnDate = Generate_Date(PriceDate_C, SwapMaturity_C[i], NCPN_Ann[i], nCpnArray, FirstCpnDate);
			disc = DF_From_Swap(PriceDate_C, CpnDate, nCpnArray, SwapRate[i], ncurve, ZeroTerm, ZeroRate, Swap_OneYConvention_Fix[i], FirstCpnDate, InterpFlag);
			free(CpnDate);

			tau = (double)(DayCountAtoB(PriceDate_C, SwapMaturity_C[i]));
			ZeroTerm[ncurve] = tau/365.0;
			ZeroRate[ncurve] = 365.0 / tau * -log(disc);
			DiscFactor[ncurve] = exp(-ZeroTerm[ncurve] * ZeroRate[ncurve]);
			Mkt[ncurve] = SwapRate[i];
			ncurve++;
		}
	}

	for (i = 0; i < ncurve; i++)
	{
		ResultCurveTerm[i] = ZeroTerm[i];
		ResultCurve[i] = ZeroRate[i];
		ResultDF[i] = DiscFactor[i];
		ResultMktRate[i] = Mkt[i];
	}

	free(ZeroTerm);
	free(ZeroRate);
	free(DiscFactor);
	free(Mkt);
	return 1;
}

long ErrorCheckZeroMakerExcel(
	long PriceDate_Excel,
	long MarketDataFlag,

	long NShortTerm,
	long* ShortTerm_Maturity_Excel,
	double* ShortTerm_Rate,
	long* ShortTerm_OneYConvention,

	long NForward,
	long* ForwardStart_Excel,
	long* ForwardEnd_Excel,
	double* ForwardRate,
	long* Forward_OneYConvention,

	long NSwap,
	long* SwapMaturity_Excel,
	long* NCPN_Ann,
	double* SwapRate,
	long* Swap_OneYConvention_Fix,

	long InterpFlag,
	char* Error
)
{
	long i;
	long j;
	char ErrorName[100];
	if (NForward > 0)
	{
		if (PriceDate_Excel < 0 || PriceDate_Excel >= ShortTerm_Maturity_Excel[0] || PriceDate_Excel >= ForwardStart_Excel[0] || PriceDate_Excel >= SwapMaturity_Excel[0])
		{
			strcpy_s(ErrorName, "Check PriceDate");
			return SaveErrorName2(Error, ErrorName);
		}
	}
	else
	{
		if (PriceDate_Excel < 0 || PriceDate_Excel >= ShortTerm_Maturity_Excel[0] || PriceDate_Excel >= SwapMaturity_Excel[0])
		{
			strcpy_s(ErrorName, "Check PriceDate");
			return SaveErrorName2(Error, ErrorName);
		}
	}

	if (NShortTerm < 1)
	{
		strcpy_s(ErrorName, "Check Short Term Rate Number");
		return SaveErrorName2(Error, ErrorName);
	}

	for (i = 0; i < NShortTerm; i++)
	{
		if (i > 0)
		{
			if (ShortTerm_Maturity_Excel[i] < ShortTerm_Maturity_Excel[i - 1])
			{
				strcpy_s(ErrorName, "Sort Short Term Maturity");
				return SaveErrorName2(Error, ErrorName);
			}
		}

		if (ShortTerm_Maturity_Excel[i] - PriceDate_Excel >= 555)
		{
			strcpy_s(ErrorName, "Check Short Term Rate Maturity");
			return SaveErrorName2(Error, ErrorName);
		}

		if (ShortTerm_OneYConvention[i] != 360 && ShortTerm_OneYConvention[i] != 365)
		{
			strcpy_s(ErrorName, "Check Short Term Rate Y Convention");
			return SaveErrorName2(Error, ErrorName);
		}
	}

	for (i = 0; i < NForward; i++)
	{
		if (i > 0)
		{
			if (ForwardStart_Excel[i] < ForwardStart_Excel[i - 1])
			{
				strcpy_s(ErrorName, "Sort Forward Start Date");
				return SaveErrorName2(Error, ErrorName);
			}
		}
		if (ForwardStart_Excel[i] - PriceDate_Excel > 366 + 365 || ForwardEnd_Excel[i] - PriceDate_Excel > 366 + 365)
		{
			strcpy_s(ErrorName, "Check IR Forward Maturity");
			return SaveErrorName2(Error, ErrorName);
		}

		if (Forward_OneYConvention[i] != 360 && Forward_OneYConvention[i] != 365)
		{
			strcpy_s(ErrorName, "Check Forward Y Convention");
			return SaveErrorName2(Error, ErrorName);
		}
	}

	if (NSwap < 1)
	{
		strcpy_s(ErrorName, "Check Swap Number");
		return SaveErrorName2(Error, ErrorName);
	}

	for (i = 0; i < NSwap; i++)
	{
		if (i > 0)
		{
			if (SwapMaturity_Excel[i] < SwapMaturity_Excel[i - 1])
			{
				strcpy_s(ErrorName, "Sort Swap Maturity Date");
				return SaveErrorName2(Error, ErrorName);
			}
		}

		if (NCPN_Ann[i] != 1 && NCPN_Ann[i] != 2 && NCPN_Ann[i] != 3 && NCPN_Ann[i] != 4 && NCPN_Ann[i] != 6 && NCPN_Ann[i] != 12)
		{
			strcpy_s(ErrorName, "Check Swap NCPN Ann");
			return SaveErrorName2(Error, ErrorName);
		}

		if (Swap_OneYConvention_Fix[i] != 360 && Swap_OneYConvention_Fix[i] != 365)
		{
			strcpy_s(ErrorName, "Check Forward Y Convention");
			return SaveErrorName2(Error, ErrorName);
		}



	}

	if (InterpFlag < 0 || InterpFlag > 2)
	{
		strcpy_s(ErrorName, "InterpMethod");
		return SaveErrorName2(Error, ErrorName);
	}
	return 1;
}

DLLEXPORT(long) ZeroMakerExcel(
	long PriceDate_Excel,			// Pricing Date ExcelType
	long MarketDataFlag,			// 0: MMF, IRForward, Swap 사용 1: 단기채YTM, 쿠폰채YTM사용

	long NShortTerm,				// Short Term 이자율 개수
	long* ShortTerm_Maturity_Excel,	// Short Term 이자율 만기일 ExcelType Array
	double* ShortTerm_Rate,			// Short Term 이자율 Rate Array
	long* ShortTerm_OneYConvention,	// DayCount 1Y (360 or 365)

	long NForward,					// Forward 이자율 개수
	long* ForwardStart_Excel,		// Forward금리 추정시작일 ExcelType Array
	long* ForwardEnd_Excel,			// Forward금리 추정종료일 ExcelType Array
	long* ForwardPayDate_Excel,		// Forward PayDate
	double* ForwardRate,			// Forward Rate Array
	long* Forward_OneYConvention,	// Forward Rate DayCount 1Y (360 or 365) Array

	long NSwap,						// 입력된 Swap 개수
	long* SwapMaturity_Excel,		// Swap 만기 ExcelType Array
	long* SwapPayDate_Excel,		// SwapPayDate Array
	long* NCPN_Ann,					// Swap 연 이자지급 회수 Array
	double* SwapRate,				// Swap Rate Array
	long* Swap_OneYConvention_Fix,	// Swap DayCount 1Y (360 or 365)

	long NResultCurve,				// Out: 결과 커브 Term 개수
	double* ResultCurveTerm,		// Out: 결과 커브 Term Array
	double* ResultCurve,			// Out: 결과 커브 Rate Array
	double* ResultDF,				// Out: DF Array
	double* MktRate,				// Out: MktRate Array

	long InterpFlag,				// 0: Linterp 1: Linterp + Extrap 2: Cubic
	long CaliFlag,					// 0: Analytic, 1: Root Finder
	char* Error,					// Out: 에러메시지
	long TextDumpFlag

)
{
	long i;
	long ResultCode;

	ResultCode = ErrorCheckZeroMakerExcel(PriceDate_Excel, MarketDataFlag, NShortTerm, ShortTerm_Maturity_Excel,
		ShortTerm_Rate, ShortTerm_OneYConvention, NForward, ForwardStart_Excel, ForwardEnd_Excel, ForwardRate, Forward_OneYConvention,
		NSwap, SwapMaturity_Excel, NCPN_Ann, SwapRate, Swap_OneYConvention_Fix, InterpFlag, Error);

	char CalcFunctionName[] = "ZeroMakerExcel";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag == 1)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "PriceDate_Excel", PriceDate_Excel);
		DumppingTextData(CalcFunctionName, SaveFileName, "MarketDataFlag", MarketDataFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "NShortTerm", NShortTerm);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ShortTerm_Maturity_Excel", NShortTerm, ShortTerm_Maturity_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ShortTerm_Rate", NShortTerm, ShortTerm_Rate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ShortTerm_OneYConvention", NShortTerm, ShortTerm_OneYConvention);

		DumppingTextData(CalcFunctionName, SaveFileName, "NForward", NForward);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardStart_Excel", NForward, ForwardStart_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardEnd_Excel", NForward, ForwardEnd_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardPayDate_Excel", NForward, ForwardPayDate_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "ForwardRate", NForward, ForwardRate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Forward_OneYConvention", NForward, Forward_OneYConvention);

		DumppingTextData(CalcFunctionName, SaveFileName, "NSwap", NSwap);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "SwapMaturity_Excel", NSwap, SwapMaturity_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "SwapPayDate_Excel", NSwap, SwapPayDate_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "NCPN_Ann", NSwap, NCPN_Ann);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "SwapRate", NSwap, SwapRate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Swap_OneYConvention_Fix", NSwap, Swap_OneYConvention_Fix);

		DumppingTextData(CalcFunctionName, SaveFileName, "InterpFlag", InterpFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "CaliFlag", CaliFlag);

	}

	if (ResultCode < 0) return ResultCode;

	long PriceDate_C = ExcelDateToCDate(PriceDate_Excel);
	long* ShortTerm_Maturity_C = (long*)malloc(sizeof(long) * NShortTerm);
	long* ForwardStart_C = (long*)malloc(sizeof(long) * NForward);
	long* ForwardEnd_C = (long*)malloc(sizeof(long) * NForward);
	long* ForwardPayDate_C = (long*)malloc(sizeof(long) * NForward);
	long* SwapMaturity_C = (long*)malloc(sizeof(long) * NSwap);
	long* SwapPayDate_C = (long*)malloc(sizeof(long) * NSwap);
	for (i = 0; i < NShortTerm; i++)
	{
		ShortTerm_Maturity_C[i] = ExcelDateToCDate(ShortTerm_Maturity_Excel[i]);
	}

	for (i = 0; i < NForward; i++)
	{
		ForwardStart_C[i] = ExcelDateToCDate(ForwardStart_Excel[i]);
		ForwardEnd_C[i] = ExcelDateToCDate(ForwardEnd_Excel[i]);
		if (ForwardPayDate_Excel[i]) ForwardPayDate_C[i] = ExcelDateToCDate(ForwardPayDate_Excel[i]);
		else ForwardPayDate_C[i] = ForwardEnd_C[i];
	}

	for (i = 0; i < NSwap; i++)
	{
		SwapMaturity_C[i] = ExcelDateToCDate(SwapMaturity_Excel[i]);
		if (SwapPayDate_Excel[i]) SwapPayDate_C[i] = ExcelDateToCDate(SwapPayDate_Excel[i]);
		else SwapPayDate_C[i] = SwapMaturity_C[i];
	}

	for (i = 0; i < NForward; i++)
	{
		if (ForwardEnd_C[i] >= SwapMaturity_C[0]) NForward -= 1;
	}

	if (MarketDataFlag == 0)
	{
		for (i = 0; i < NForward; i++)
		{
			if (ForwardEnd_C[i] != ForwardPayDate_C[i])
			{
				CaliFlag = 1;
				break;
			}
		}
		for (i = 0; i < NSwap; i++)
		{
			if (SwapMaturity_C[i] != SwapPayDate_C[i])
			{
				CaliFlag = 1;
				break;
			}
		}

		if (CaliFlag == 0)
		{
			ResultCode = ZeroCurveGenerate_IRS(
				PriceDate_C, NShortTerm, ShortTerm_Maturity_C, ShortTerm_Rate, ShortTerm_OneYConvention,
				NForward, ForwardStart_C, ForwardEnd_C, ForwardRate, Forward_OneYConvention,
				NSwap, SwapMaturity_C, NCPN_Ann, SwapRate, Swap_OneYConvention_Fix,
				NResultCurve, ResultCurveTerm, ResultCurve, ResultDF, MktRate, InterpFlag);
		}
		else
		{
			ResultCode = ZeroCurveGenerate_IRS2(
				PriceDate_C, NShortTerm, ShortTerm_Maturity_C, ShortTerm_Rate, ShortTerm_OneYConvention,
				NForward, ForwardStart_C, ForwardEnd_C, ForwardPayDate_C, ForwardRate, 
				Forward_OneYConvention, NSwap, SwapMaturity_C, SwapPayDate_C, NCPN_Ann, 
				SwapRate, Swap_OneYConvention_Fix, NResultCurve, ResultCurveTerm, ResultCurve, 
				ResultDF, MktRate, InterpFlag);
		}
	}
	else
	{
		ResultCode = ZeroCurveGenerate_Bond(
			PriceDate_C, NShortTerm, ShortTerm_Maturity_C, ShortTerm_Rate, ShortTerm_OneYConvention,
			NSwap, SwapMaturity_C, SwapPayDate_C, NCPN_Ann, SwapRate, 
			Swap_OneYConvention_Fix, NResultCurve, ResultCurveTerm, ResultCurve, ResultDF, MktRate, InterpFlag);
	}

	free(ShortTerm_Maturity_C);
	free(ForwardStart_C);
	free(ForwardEnd_C);
	free(ForwardPayDate_C);
	free(SwapMaturity_C);
	free(SwapPayDate_C);
	_CrtDumpMemoryLeaks();
	return ResultCode;
}

DLLEXPORT(double) Calc_IRS(long PricingDate_Excel, long SwapMaturityDate_Excel, long Number_Ann_CPN, long Convention1Y, long NRate, double* RateTerm, double* Rate)
{
	long i;
	long nCpnDate = 0;
	long PriceDateYYYYMMDD = ExcelDateToCDate(PricingDate_Excel);
	long SwapMat_YYYYMMDD = ExcelDateToCDate(SwapMaturityDate_Excel);
	long FirstCpnDate = PriceDateYYYYMMDD;
	long* CpnDate = Generate_Date(PriceDateYYYYMMDD, SwapMat_YYYYMMDD, Number_Ann_CPN, nCpnDate, FirstCpnDate);
	double DF0 = 1.0, t0, r0;
	double T_N = ((double)DayCountAtoB(PriceDateYYYYMMDD, CpnDate[nCpnDate - 1])/365.0);
	double r = Interpolate_Linear(RateTerm, Rate, NRate, T_N);
	double b = 0.0;
	double deltat;
	double TimeT;

	if (PriceDateYYYYMMDD != FirstCpnDate)
	{
		t0 = ((double)DayCountAtoB(PriceDateYYYYMMDD, FirstCpnDate) / 365.0);
		r0 = Interpolate_Linear(RateTerm, Rate, NRate, t0);
		DF0 = exp(-r0 * t0);
	}

	double a = DF0 - exp(-r * T_N);
	if (Convention1Y == 360) TimeT = 360.0;
	else TimeT = 365.0;

	for (i = 0; i < nCpnDate; i++)
	{
		T_N = ((double)DayCountAtoB(PriceDateYYYYMMDD, CpnDate[i]) / 365.0);

		if (i == 0) deltat = ((double)DayCountAtoB(FirstCpnDate, CpnDate[i]) / TimeT);
		else deltat = ((double)DayCountAtoB(CpnDate[i-1], CpnDate[i]) / TimeT);
		r = Interpolate_Linear(RateTerm, Rate, NRate, T_N);
		b += deltat * exp(-r * T_N);
	}
	free(CpnDate);
	return a / b;
}

double IRS(long PriceDateYYYYMMDD, long SwapMat_YYYYMMDD, long FirstCpnDate, long Number_Ann_CPN, long* CpnDate, long nCpnDate, long Convention1Y, long NRate, double* RateTerm, double* Rate, long InterpFlag)
{
	// CpnDate == PayDate
	long i;
	double T_N = ((double)DayCountAtoB(PriceDateYYYYMMDD, CpnDate[nCpnDate - 1]) / 365.0);
	double r;
	if (InterpFlag == 0 || InterpFlag == 1) r = Interpolate_Linear(RateTerm, Rate, NRate, T_N);
	else r = CubicSpline(NRate, RateTerm, Rate, T_N);

	double a;
	double b;
	double deltat;
	double TimeT;
	double DF0 = 1.0;
	double t0, r0;
	if (PriceDateYYYYMMDD != FirstCpnDate)
	{
		t0 = ((double)DayCountAtoB(PriceDateYYYYMMDD, FirstCpnDate) / 365.0);
		if (InterpFlag == 0 || InterpFlag == 1) r0 = Interpolate_Linear(RateTerm, Rate, NRate, t0);
		else r0 = CubicSpline(NRate, RateTerm, Rate, t0);
		DF0 = exp(-r0 * t0);
	}
	a = DF0 - exp(-r * T_N);
	b = 0.0;
	if (Convention1Y == 360) TimeT = 360.0;
	else TimeT = 365.0;

	for (i = 0; i < nCpnDate; i++)
	{
		T_N = ((double)DayCountAtoB(PriceDateYYYYMMDD, CpnDate[i]) / 365.0);

		if (i == 0) deltat = ((double)DayCountAtoB(FirstCpnDate, CpnDate[i]) / TimeT);
		else deltat = ((double)DayCountAtoB(CpnDate[i - 1], CpnDate[i]) / TimeT);

		if (InterpFlag == 0 || InterpFlag == 1) r = Interpolate_Linear(RateTerm, Rate, NRate, T_N);
		else r = CubicSpline(NRate, RateTerm, Rate, T_N);

		b += deltat * exp(-r * T_N);
	}


	return a / b;

}