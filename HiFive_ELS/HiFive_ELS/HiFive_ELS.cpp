#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

#include "CalcDate.h"
#include "GetTextDump.h"

#ifndef NULL
#define NULL 0
#endif

#include "SABR.h"
#ifndef UTILITY
#define UTILITY 1
#endif

#ifndef STRUCTURE
#define STRUCTURE 1
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

long sumation(long NArray, long* Array)
{
	long i;
	long s = 0;
	for (i = 0; i < NArray; i++)
	{
		s += Array[i];
	}
	return s;
}

class simulinfo {
private:
public:
	long simulationflag;			// �ùķ��̼��� ����Ǵ��� ����
	long nsimul;					// �ùķ��̼� Ƚ��
	long nstock;					// �ùķ��̼� �����ڻ갳��
	long greekflag;					// �׸��� ����ϴ��� ����
	long pricingdate;				// ���ݰ���� CDate
	double* s0;						// S Start ��
	double** correlation;			// �� �ڻ꺰 ������ Matrix
	long dynamicflag;				// FixedRandn ��뿩��
	double resultprice;				// ���ݰ��
	long maxsimulnode;				// �ùķ��̼� ��¥����

	long randseed;					// �ùķ��̼� �����õ尪

	double* pathprice;				// ���� Path
	double*** FixedRandn;			// Random Number Array

	// �Լ��� �����ؾ��ϴ� Daily Data
	long daily_flag;				// Daily �����Ͱ� �����ϴ��� Flag
	double** daily_forward_rate;	// Daily Forward Rate
	double** daily_forward_div;		// Daily Forward Div
	long* divtype;					// Dividend Type 0: Flat, 1:Div Curve, 2: Discrete 
	double** daily_forward_fxvol;	// Daily Forward FX Vol
	long* quantoflag;				// Quanto ���뿩��
	double* quantocorr;				// FX, S Correlation

	// Forward Rate�� Daily�� ����Ѵ�.
	// ���� = (������ �Ⱓ���� ����, ������ �Ⱓ���� Term, ������ �Ⱓ���� ������, �� Array, �� Array����) 
	void ForwardRateDaily(long nterm, double* term, double* rate, double* forward_rate_daily, long lengthday)
	{
		long i;
		long TimePos = 0;
		double deltat = 1.0 / 365.0;
		double T;

		T = 0.0;
		for (i = 0; i < lengthday; i++)
		{
			forward_rate_daily[i] = Calc_Forward_Rate_Daily(term, rate, nterm, T, &TimePos);
			T += deltat;
		}

	}

	// Forward FX Vol�� Daily�� ����Ѵ�.
	// ���� = (FX Vol �Ⱓ���� ����, FX Vol �Ⱓ���� Term, FX Vol �Ⱓ���� Volatility, �� Array, �� Array����) 
	void ForwardFXVolDaily(long nterm, double* term, double* rate, double* forward_fxvol_daily, long lengthday)
	{
		long i;
		long TimePos = 0;
		double deltat = 1.0 / 365.0;
		double T;

		T = 0.0;
		for (i = 0; i < lengthday; i++)
		{
			forward_fxvol_daily[i] = Calc_Forward_FXVol_Daily(term, rate, nterm, T, &TimePos);
			T += deltat;
		}

	}

	// Forward Dividend�� Daily�� ����Ѵ�.
	// ���� = (Dividend �Ⱓ���� ����, Dividend �Ⱓ���� Term, Dividend �Ⱓ���� ���(�Ǵ¹����ͷ�), ���Ÿ��(0:Flat, 1:Forward���, 2: Discrete), �����ְ�, �� Array, �� Array����) 
	void ForwardDivDaily(long nterm, double* term, double* div, long divtype, double StockPrice, double* div_daily, long lengthday)
	{
		// div type = 0 -> Flat
		// div type = 1 -> curve
		// div type = 2 -> discrete

		long i;
		double T;
		double dt = 1.0 / 365.0;
		long TimePos = 0;
		double T_Plus;

		if (divtype == 0)
		{
			double flat_div = div[0];
			for (i = 0; i < lengthday; i++)
			{
				div_daily[i] = flat_div;
			}
		}
		else if (divtype == 1)
		{

			T = 0.0;
			for (i = 0; i < lengthday; i++)
			{
				div_daily[i] = Calc_Forward_Rate_Daily(term, div, nterm, T, &TimePos);
				T += dt;
			}
		}
		else
		{
			long term_idx = 0;

			double next_term;
			double div_rate;
			if (nterm > 0)
			{
				if (term[0] > 0.0)
				{
					// ���� ��� ��¥�� ����� Daily�� ����
					next_term = term[term_idx];
					div_rate = min(1.0, div[term_idx] / term[term_idx]) * dt;
					T = 0.;
					for (i = 0; i < lengthday; i++)
					{
						if (T >= next_term && T < term[max(term_idx + 1, nterm - 1)])
						{
							term_idx = term_idx + 1;
							next_term = term[term_idx];
							div_rate = div[term_idx] / term[term_idx] * dt;
						}
						div_daily[i] = div_rate;
						T = T + dt;
					}
				}
			}
		}
	}

	// Daily Forward Rate, Dividend, FX Vol Setting
	void set_daily_data(long* NTerm_Rf, double* Term_Rf, double* Rate_Rf,
		long* NTerm_Div, double* Term_Div, double* Div, long* DivType,
		long* NTerm_FXVol, double* Term_FXVol, double* Rate_FXVol, long* Quanto_Flag, double* Quanto_Corr,
		double** temp_daily_forward_rate, double** temp_daily_forward_div, double** temp_daily_forward_fxvol)
	{
		long i, j;

		long Sum_NTerm_Rf = 0;
		long Sum_NTerm_Div = 0;
		long Sum_NTerm_FXVol = 0;

		long nterm_riskfree = 0;
		long nterm_dividend = 0;
		long nterm_fx_volatility = 0;

		if (daily_flag == 0)
		{
			daily_flag = 1;

			daily_forward_rate = temp_daily_forward_rate;
			daily_forward_div = temp_daily_forward_div;
			daily_forward_fxvol = temp_daily_forward_fxvol;

			divtype = (long*)malloc(sizeof(long*) * nstock);
			quantoflag = (long*)malloc(sizeof(long*) * nstock);
			quantocorr = (double*)malloc(sizeof(double) * nstock);

			for (i = 0; i < nstock; i++)
			{
				nterm_riskfree = NTerm_Rf[i];
				nterm_dividend = NTerm_Div[i];
				nterm_fx_volatility = NTerm_FXVol[i];

				divtype[i] = DivType[i];
				quantoflag[i] = Quanto_Flag[i];
				quantocorr[i] = Quanto_Corr[i];

				ForwardRateDaily(nterm_riskfree, Term_Rf + Sum_NTerm_Rf, Rate_Rf + Sum_NTerm_Rf, daily_forward_rate[i], maxsimulnode);

				if (Quanto_Flag[i] > 0)
				{
					ForwardFXVolDaily(nterm_fx_volatility, Term_FXVol + Sum_NTerm_FXVol, Rate_FXVol + Sum_NTerm_FXVol, daily_forward_fxvol[i], maxsimulnode);
				}
				else
				{
					for (j = 0; j < maxsimulnode; j++) daily_forward_fxvol[i][j] = 0.0;
				}
				ForwardDivDaily(nterm_dividend, Term_Div + Sum_NTerm_Div, Div + Sum_NTerm_Div, DivType[i], s0[i], daily_forward_div[i], maxsimulnode);

				Sum_NTerm_Rf += nterm_riskfree;
				Sum_NTerm_FXVol += nterm_fx_volatility;
				Sum_NTerm_Div += nterm_dividend;
			}
		}
	}

	void delete_daily_data()
	{
		if (daily_flag == 1)
		{
			long i;
			daily_flag = 0;
			free(divtype);
			free(quantoflag);
			free(quantocorr);
		}
	}

	void reset_pathprice()
	{
		long i;
		for (i = 0; i < nsimul; i++)
		{
			pathprice[i] = 0.0;
		}
	}

	simulinfo() {
		dynamicflag = 0;
		daily_flag = 0;
	}

	simulinfo(long SimulateFlag, long Number_Simul, long Number_Stock, long CalcGreekFlag, long CalculationDate, double* S0_Value, double** CorrelationMat, long MaxSimulDays, double*** FixedRn, double* path_price_input)
	{
		long i, j, k;

		simulationflag = SimulateFlag;
		daily_flag = 0;
		nsimul = Number_Simul;
		nstock = Number_Stock;
		greekflag = CalcGreekFlag;
		pricingdate = CalculationDate;
		s0 = S0_Value;
		correlation = CorrelationMat;
		maxsimulnode = MaxSimulDays;

		if (SimulateFlag > 0)
		{
			dynamicflag = 1;
			pathprice = path_price_input;
			if (greekflag != 0) FixedRandn = FixedRn;
		}
		else
		{
			dynamicflag = 0;
		}

	}

	double Call_Randn(long idx_simul, long idx_node, long idx_nstock)
	{
		if (greekflag != 0)
		{
			return FixedRandn[idx_simul][idx_node][idx_nstock];
		}
		else
		{
			return randnorm();
		}
	}

	~simulinfo()
	{
		if (dynamicflag == 1)
		{
			long i, j;
		}

		if (daily_flag != 0)
		{
			long i;

			free(divtype);
			free(quantoflag);
			free(quantocorr);
		}
	}
};

// HiFive Information
class HiFiveInfo {
public:
	double FaceValue;			// Notional Amount
	long FaceValueFlag;			// Notional Amount ���޿���
	long NStock;				// Underlying Asset ����

	double MaxProfit;			// �ִ�����
	double MaxLoss;				// �ִ�ս�

	// KI ���� ����
	long KI_Method;				// Knock In Method 0: �����������, 1: Continuous Knock In, 2: ���⿡�� ���� üũ
	double KI_Barrier_Level;	// Kncok In Barrier 
	long Now_KI_State;			// ���� ���� ����

	// Autocall ���� ����
	long NEvaluation;			// �����ȯ ���� ����
	long* Days_Autocall_Eval;	// �����ȯ ���ϱ��� ��¥�� Array -> Shape = (NEvaluation, )
	long* Days_Autocall_Pay;	// �����ȯ �����ϱ��� ��¥�� Array -> Shape = (NEvaluation, )

	long nK;					// �� �����ȯ ���Ͽ� ��簡�� ����(�ɼǰ���)
	double** Strike;			// �� �����ȯ ���Ͽ� ��簡�� Array -> Shape = (3, NEvaluation )
	double** Slope;				// �� �����ȯ ���Ͽ� ������ Array -> Shape = (3, NEvaluation)
	double** FixedAmount;		// �� �����ȯ ���Ͽ� Coupon Rate Array -> Shape = (3, NEvaluation)

	// Lizard ���� ����
	long NLizard;					// ���ڵ� �� ����
	long* LizardFlag;				// �� �����ȯ ���Ͽ� ���ڵ� �� �Ǵ������� Array -> Shape = (NLizard, )
	long* Days_LizardStart;			// �� �����ȯ ���Ͽ� ���ڵ� �踮�� �� ������ Array -> Shape = (NLizard, )
	long* Days_LizardEnd;			// �� �����ȯ ���Ͽ� ���ڵ� �踮�� �� ������ Array -> Shape = (NLizard, )
	double* Lizard_Barrier_Level;	// ���ڵ�踮�� ���� Array -> Shape = (NLizard, )
	double* Lizard_Coupon;			// ���ڵ� ���� Array -> Shape = (NLizard, )
	long* Now_Lizard_KI_State;		// ���� ���ڵ� �踮�� ���λ�Ȳ Array -> Shape = (NLizard, )

	long NCPN;					// �Ϲ������򰡰���
	long* Days_CPN_Eval;		// �Ϲ��������ϱ��� ��¥�� Array -> Shape = (NCPN , )
	long* Days_CPN_Pay;			// �Ϲ����������ϱ��� ��¥�� Array -> Shape = (NCPN , )
	double* CPN_Lower_Barrier;	// �Ϲ����������� �Ϲ�踮�� Array -> Shape = (NCPN , )
	double* CPN_Upper_Barrier;	// �Ϲ����������� ���踮�� Array -> Shape = (NCPN , )
	double* CPN_Rate;			// �Ϲ�����Rate Array -> Shape = (NCPN , )


};

long SaveErrorName(char* Error, char ErrorName[100])
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

long ErrorCheck(
	long PricingDate_Excel,			// ���ݰ�곯¥ ExcelType Ex) 44201(2021��01��05��)
	long NSimul,					// �ùķ��̼ǰ���
	long GreekFlag,					// �׸������������
	double FaceValue,				// ���ݾ�
	long FaceValueFlag,				// ���ݼ�������

	double MaxProfit,				// �ִ�����
	double MaxLoss,					// �ִ�ս�
	long NEvaluate,					// �����ȯ ���ϰ���
	double KI_Barrier_Level,		// ���ι踮�����
	long Now_KI_State,				// ���� ���λ���

	long KI_Method,					// ����ó�����
	long* EvalDate_Excel,			// �����ȯ ExcelType���� Array [ Shape = (NEvaluate , ) ]
	long* PayDate_Excel,			// �����ȯ ExcelType������ Array [ Shape = (NEvaluate , ) ]
	long* NStrike,					// �����ȯ ȸ���� ��簡�ݰ��� Array [ Shape = (NEvaluate , ) ]
	double* StrikeLevel,			// �����ȯ ȸ���� ��簡�� Array [ Shape = reshape(3 * NEvaluate) ]

	double* Slope,					// �����ȯ ȸ���� ������ [ Shape = reshape(3 * NEvaluate)  ]
	double* FixedAmount,			// �����ȯ ȸ���� ���� [ Shape = reshape(3 * NEvaluate)  ]
	long NLizard,					// ���ڵ��ȯ ���� ����
	long* LizardFlag,				// �����ȯ ȸ���� ���ڵ��ȯ ������ ���� Array [ Shape = (NLizard , ) ]
	long* LizardStartDate_Excel,	// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]

	long* LizardEndDate_Excel,		// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]
	double* LizardBarrierLevel,		// �����ȯ ȸ���� ���ڵ�踮�� �踮��� Array
	long* Now_LizardHitting,		// �����ȯ ȸ���� ���ڵ�踮�� ���� Hitting���� Array
	double* LizardCoupon,			// �����ȯ ȸ���� ���ڵ�踮�� ���������� Array
	long NCPN,						// �Ϲ� ���� ���� ����

	long* CPN_EvaluateDate_Excel,	// �Ϲ� ���� ���� ExcelType Array [ Shape = (NCPN , ) ]
	long* CPN_PayDate_Excel,		// �Ϲ� ���� ������ ExcelType Array [ Shape = (NCPN , ) ]
	double* CPN_Lower_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Upper_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Rate,				// �Ϲ� ���� ���������� Array [ Shape = (NCPN , ) ]

	long NStock,					// �����ڻ갳��
	double* S0X0,					// [�����ڻ�Array + ���ذ���Array + Autocall���� �򰡰���Array + Coupon���� �򰡰���Array]
	double* CorrelationReshaped,	// Correlation Matrix.reshape(-1)
	long* NTerm,					// ������ �Ⱓ���� ���� (Discount, Rf1, Rf2, ....) [ Shape = (NStock +1 , )]
	double* TermRate,				// ������ �Ⱓ���� Term -> append(Discount Term Array + RfTermArray1 + RfTermArray2 + ...] , Shape = (sum(NTerm) , )

	double* Rate,					// ������ �Ⱓ���� Rate append(Discount Rate Array + RfRateArray1 + RfRateArray2 + ...], Shape = (sum(NTerm), )
	long* NDivTerm,					// ��� �Ⱓ���� ���� (Stock1, Stock2, ....)    [ Shape = (NStock , )]
	long* DivFlag,					// ��� �Ⱓ���� ���Ÿ�� (Stock1DivType, ) , Shape = (sum(NDivTerm) , )
	double* TermDiv,				// ��� �Ⱓ���� Term -> append(Stock1DivTermArray+ Stock2DivTermArray + ....) , Shape = (sum(NDivTerm) , )
	double* Div,					// ��� �Ⱓ���� Rate �Ǵ� �ݾ� -> append(Stock1DivArray + Stock2DivArray + ....), Shape = (sum(NDivTerm), )

	long* QuantoFlag,				// Quanto ��뿩�� Array [Shape = (NStock ,)]
	double* QuantoCorr,				// FX, �����ڻ� Correlation Array [Shape = (NStock , )]
	long* NTermQuanto,				// Quanto FX Vol Term ���� Array [ Shape = (NStock, )]
	double* TermQuanto,				// Quanto FX Vol Term Array -> append[ FX Vol Term1 Array + FX Vol Term2 Array + FX Vol Term3 Array + ...] [ Shape = (sum(NTermQuanto), )]
	double* VolQuanto,				// Quanto FX Vol Array -> append[FX Vol1 Array + FX Vol2 Array + FX Vol3 Array + ....] [ Shape = (sum(NTermQuanto), )]

	long* ImVolLocalVolFlag,		// Imvol�� �� �� Localvol�� �� �� Flag Array (0: Imvol, 1: LocalVol) [ Shape = (NStock, )]
	long* NParityVol,				// �����ڻ꺰 �з�Ƽ ���� Array [ Shape = (NStock, )]
	double* ParityVol,				// �����ڻ꺰 �з�Ƽ Array -> append[Parity1 Array, Parity2 Array, Parity3 Array...]
	long* NTermVol,					// �����ڻ꺰 Volatility Term ���� Array [ Shape = (NStock, )]
	double* TermVol,				// �����ڻ꺰 Volatility Term Array -> append[VolTerm1, VolTerm2, VolTerm3 ...]

	double* Vol,					// �����ڻ꺰 Volatility Array -> append[ReshapedVol1, ReshapedVol2, ReshapedVol3, ReshapedVol4 .....]
	double* ResultPrice,			// ������� �� ��Ÿ�������� Shape = (1 + NStock * 3 , )
	double* AutocallProb,			// �����ȯ Ȯ�� �� �����ȯ Payoff -> Shape = (NEvaluate * 2, )
	double* CPNProb,				// ���� Ȯ�� �� ���� -> Shape = (NCPN * 2, )
	double* ResultLocalVol,			// LocalVolatility �����

	char* Error
)
{
	long i;

	char ErrorName[100];


	if (PricingDate_Excel < 0)
	{
		strcpy_s(ErrorName, "PricingDate is too early");
		return SaveErrorName(Error, ErrorName);
	}

	if (PricingDate_Excel > max(PayDate_Excel[NEvaluate - 1], CPN_PayDate_Excel[NCPN - 1]))
	{
		strcpy_s(ErrorName, "PricingDate is too late");
		return SaveErrorName(Error, ErrorName);
	}

	if (NSimul <= 0)
	{
		strcpy_s(ErrorName, "NSimul must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	if (GreekFlag < 0)
	{
		strcpy_s(ErrorName, "GreekFlag must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	if (FaceValue < 0.0)
	{
		strcpy_s(ErrorName, "FaceValue must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	if (FaceValueFlag < 0)
	{
		strcpy_s(ErrorName, "FaceValueFlag must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	if (NEvaluate == 0)
	{
		strcpy_s(ErrorName, "Autocall Evaluation Number is 0");
		return SaveErrorName(Error, ErrorName);
	}

	for (i = 0; i < NEvaluate - 1; i++)
	{
		if (EvalDate_Excel[i + 1] < EvalDate_Excel[i])
		{
			strcpy_s(ErrorName, "Check Autocall Evaluation Date");
			return SaveErrorName(Error, ErrorName);
		}
	}

	for (i = 0; i < NEvaluate; i++)
	{
		if (EvalDate_Excel[i] > PayDate_Excel[i])
		{
			strcpy_s(ErrorName, "Autocall Evaluation Date is later than PayDate");
			return SaveErrorName(Error, ErrorName);
		}
	}

	for (i = 0; i < NLizard; i++)
	{
		if (min(LizardStartDate_Excel[i], LizardEndDate_Excel[i]) <= 0)
		{
			strcpy_s(ErrorName, "LizardDate must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
	}

	for (i = 0; i < NCPN; i++)
	{
		if (min(CPN_EvaluateDate_Excel[i], CPN_PayDate_Excel[i]) <= 0)
		{
			strcpy_s(ErrorName, "CPNDate must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
	}

	if (NStock < 1)
	{
		strcpy_s(ErrorName, "NStock must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	for (i = 0; i < NStock; i++)
	{
		if (S0X0[i] < 0.0 || S0X0[i + NStock] < 0.0)
		{
			strcpy_s(ErrorName, "Stock Price must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
	}

	for (i = 0; i < NStock + 1; i++)
	{
		if (NTerm[i] <= 0)
		{
			strcpy_s(ErrorName, "RF Number must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
	}

	for (i = 0; i < NStock; i++)
	{
		if (DivFlag[i] < 0)
		{
			strcpy_s(ErrorName, "DivFlag must be Positive");
			return SaveErrorName(Error, ErrorName);
		}

		if (NDivTerm[i] <= 0)
		{
			strcpy_s(ErrorName, "Div Number must be Positive");
			return SaveErrorName(Error, ErrorName);
		}

		if (QuantoFlag[i] < 0)
		{
			strcpy_s(ErrorName, "QuantoFlag must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
		else if (QuantoFlag[i] > 0)
		{
			if (NTermQuanto[i] <= 0)
			{
				strcpy_s(ErrorName, "QuantoVol Number must be Positive");
				return SaveErrorName(Error, ErrorName);
			}
		}
	}

	long sum_n_parity = 0;
	long sum_n_term = 0;
	long sum_vol = 0;
	for (i = 0; i < NStock; i++)
	{
		if (NParityVol[i] <= 0)
		{
			strcpy_s(ErrorName, "VolParity Number must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
		if (NTermVol[i] <= 0)
		{
			strcpy_s(ErrorName, "VolTerm Number must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
		sum_n_parity += NParityVol[i];
		sum_n_term += NTermVol[i];
		sum_vol += NParityVol[i] * NTermVol[i];
	}

	for (i = 0; i < sum_vol; i++)
	{
		if (Vol[i] < 0.0)
		{
			strcpy_s(ErrorName, "Vol must be Positive");
			return SaveErrorName(Error, ErrorName);

		}
	}

	return 0;
}

double Redemption_Payoff(
	double FaceValue,
	long FaceValueFlag,
	double MaxProfit,
	double MaxLoss,
	double minS,
	double RedempSlope,
	double RedempCPN
)
{
	double Price;
	Price = FaceValue * min((double)FaceValueFlag + MaxProfit, max((double)FaceValueFlag - MaxLoss, (double)FaceValueFlag + RedempSlope * (minS - 1.0) + RedempCPN));
	return Price;
}

double Pricing_HiFive_MC(
	simulinfo& info_simul,			// �ùķ��̼�����
	HiFiveInfo& info_hifive,		// HiFive����
	curveinfo& disc_curve,			// Discount Curve ����
	curveinfo* rf_curves,			// Risk Free Rate ����
	curveinfo* div_curves,			// ��� ����
	curveinfo* quanto_curves,		// Quanto ����
	volinfo* VolMatrixList,			// Vol Matrix List
	double* ResultPrice,
	long pricingonly,				// ���ݸ� ���ϰ� ������ ������ ������ϴ��� Flag
	double* AutocallProb,
	double* CF,
	double* CPNProb
)
{
	long i, j, k, n;

	////////////
	// �����ѹ�����
	////////////
	long iy_forsim = 0;
	long iv_forsim[32];
	long idum_forsim = -1;
	long iset_forsim = 0;
	double gset_forsim = 0.0;
	long seed = 0;

	double dt = 1.0 / 365.0;
	double sqrt_dt = sqrt(1.0 / 365.0);
	double MeanPrice;

	double** Cholesky_Matrix;

	double* DF_Array;
	double Disc;
	double TTM_CPN;
	double Disc_CPN;
	double Payoff;
	double Disc_Payoff;
	long Now_KI_State;
	long Now_Lizard_KI_State;
	long RedempFlag;


	//Simulation Variables
	long* TimeNode;
	long* ParityNode;
	double* StockPrice;
	double* Randn;
	double* SortedS;
	double* SortedS0;
	double PrevS;
	long* IdxS;

	double Epsilon;
	double T;
	double Vol;
	double Drift;
	double Diffusion;

	long NextAutocall = 0;
	long NextAutocallPay = 0;
	long NextAutocall_Idx = 0;

	long NextCouponDate = 0;
	long NextCouponPay = 0;
	double NextCoupon = 0.0;
	double NextCouponLowerBarrier = 0.0;
	double NextCouponUpperBarrier = 0.0;
	long NextCoupon_Idx = 0;

	long NextLizardDate = 0;
	long NextLizardStart = 0;
	long NextLizardEnd = 0;
	long NextLizardPayDate = 0;
	double NextLizardBarrier = 0.0;
	double NextLizardCoupon = 0.0;
	long NextLizard_Idx = 0;

	RedempFlag = 0;
	long LizardRedempFlag = 0;

	long nK = info_hifive.nK;
	double* SortedStrike = (double*)malloc(sizeof(double) * nK);							// �޸� 1 SortedStrike
	long* StrikeIdx = (long*)malloc(sizeof(long) * nK);										// �޸� 2 StrikeIdx
	double RedempStrike = 0.0;
	double RedempSlope = 0.0;
	double RedempCPN = 0.0;
	double RedempPayoff = 0.0;


	TimeNode = (long*)malloc(sizeof(long) * info_simul.nstock);								// �޸� 3 TimeNode
	ParityNode = (long*)malloc(sizeof(long) * info_simul.nstock);							// �޸� 4 ParityNode
	StockPrice = (double*)malloc(sizeof(double) * info_simul.nstock);						// �޸� 5 StockPrice
	Randn = (double*)malloc(sizeof(double) * info_simul.nstock);							// �޸� 6 Randn
	SortedS = (double*)malloc(sizeof(double) * info_simul.nstock);							// �޸� 7 SortedS
	SortedS0 = (double*)malloc(sizeof(double) * info_simul.nstock);							// �޸� 8 SortedS0
	IdxS = (long*)malloc(sizeof(long) * info_simul.nstock);									// �޸� 9 IdxS
	for (i = 0; i < info_simul.nstock; i++)
	{
		SortedS0[i] = info_simul.s0[i];
	}
	bubble_sort(SortedS0, IdxS, info_simul.nstock);
	DF_Array = (double*)malloc(sizeof(double) * info_hifive.NEvaluation);					// �޸� 10 DF_Array
	for (i = 0; i < info_hifive.NEvaluation; i++)
	{
		DF_Array[i] = Calc_Discount_Factor(disc_curve.Term, disc_curve.Rate, disc_curve.nterm(), ((double)info_hifive.Days_Autocall_Pay[i]) / 365.0);
	}

	Cholesky_Matrix = Cholesky_Decomposition(info_simul.correlation, info_simul.nstock);	// �޸� 11 Cholesky_Matrix

	double temp = 0.0;

	if (info_simul.greekflag == 0) randn(seed, idum_forsim, iset_forsim, gset_forsim, iy_forsim, iv_forsim);

	for (i = 0; i < info_simul.nsimul; i++)
	{
		Now_KI_State = info_hifive.Now_KI_State;
		if (info_hifive.NLizard > 0) Now_Lizard_KI_State = info_hifive.Now_Lizard_KI_State[0];

		T = 0.0;
		Payoff = 0.0;
		Disc_Payoff = 0.0;
		for (n = 0; n < info_simul.nstock; n++)
		{
			TimeNode[n] = 0;
			ParityNode[n] = 0;
			StockPrice[n] = info_simul.s0[n];
		}

		RedempFlag = 0;

		LizardRedempFlag = 0;
		NextAutocall_Idx = 0;
		NextAutocall = info_hifive.Days_Autocall_Eval[0];
		NextAutocallPay = info_hifive.Days_Autocall_Pay[0];


		// ���� ������¥ �ʱ�ȭ
		if (info_hifive.NCPN > 0)
		{
			NextCoupon_Idx = 0;
			NextCouponDate = info_hifive.Days_CPN_Eval[0];
			NextCouponPay = info_hifive.Days_CPN_Pay[0];
			NextCouponLowerBarrier = info_hifive.CPN_Lower_Barrier[0];
			NextCouponUpperBarrier = info_hifive.CPN_Upper_Barrier[0];
			NextCoupon = info_hifive.CPN_Rate[0];
		}

		// ���ڵ� ��¥ �� ���� �ʱ�ȭ
		if (info_hifive.NLizard > 0)
		{
			NextLizard_Idx = 0;
			if (info_hifive.LizardFlag[0] > 0)
			{
				NextLizardDate = info_hifive.Days_Autocall_Eval[0];
				NextLizardPayDate = info_hifive.Days_Autocall_Pay[0];
				NextLizardStart = info_hifive.Days_LizardStart[0];
				NextLizardEnd = info_hifive.Days_LizardEnd[0];
				NextLizardBarrier = info_hifive.Lizard_Barrier_Level[0];
				NextLizardCoupon = info_hifive.Lizard_Coupon[0];
			}
			//���� ���ڵ� ���� üũ
			if (NextLizardStart < 0 && NextLizardEnd > 0 && SortedS0[0] < NextLizardBarrier) Now_Lizard_KI_State = 1;

		}

		for (j = 1; j < info_hifive.Days_Autocall_Eval[info_hifive.NEvaluation - 1] + 1; j++)
		{
			for (n = 0; n < info_simul.nstock; n++)
			{
				if (info_simul.greekflag == 0) Randn[n] = randn(1, idum_forsim, iset_forsim, gset_forsim, iy_forsim, iv_forsim);
				else Randn[n] = info_simul.Call_Randn(i, j - 1, n);
			}

			for (n = 0; n < info_simul.nstock; n++)
			{
				PrevS = StockPrice[n];
				Epsilon = 0.0;
				for (k = 0; k <= n; k++)
				{
					Epsilon += Cholesky_Matrix[n][k] * Randn[k];
				}

				Vol = (VolMatrixList + n)->Calc_Volatility_for_Simulation(T, StockPrice[n], TimeNode + n, ParityNode + n);
				StockPrice[n] = PrevS * (1.0 + (info_simul.daily_forward_rate[n][j - 1] - info_simul.quantocorr[n] * Vol * info_simul.daily_forward_fxvol[n][j - 1] - info_simul.daily_forward_div[n][j - 1]) * dt + Vol * sqrt_dt * Epsilon);
				SortedS[n] = StockPrice[n];
				IdxS[n] = n;
			}

			bubble_sort(SortedS, IdxS, info_simul.nstock);
			// Continuous Barrier

			if (SortedS[0] < info_hifive.KI_Barrier_Level && info_hifive.KI_Method == 1) Now_KI_State = 1;

			// Lizard Barrier KI Check
			if (j >= NextLizardStart && j < NextLizardEnd)
			{
				if (SortedS[0] < NextLizardBarrier)
				{
					Now_Lizard_KI_State = 1;
				}
			}

			// Coupon Check
			if ((NextCouponDate == NextCouponPay && j == NextCouponDate) || (j >= NextCouponDate && j < NextCouponPay))
			{
				NextCoupon_Idx = min(info_hifive.NCPN - 1, NextCoupon_Idx + 1);

				if (SortedS[0] >= NextCouponLowerBarrier && SortedS[0] < NextCouponUpperBarrier)
				{
					TTM_CPN = ((double)NextCouponPay) / 365.0;
					Disc = Calc_Discount_Factor(disc_curve.Term, disc_curve.Rate, disc_curve.nterm(), TTM_CPN);
					Disc_CPN = info_hifive.FaceValue * Disc * NextCoupon;
					info_simul.pathprice[i] = info_simul.pathprice[i] + Disc_CPN;
				}

				NextCouponDate = info_hifive.Days_CPN_Eval[NextCoupon_Idx];
				NextCouponPay = info_hifive.Days_CPN_Pay[NextCoupon_Idx];
				NextCouponLowerBarrier = info_hifive.CPN_Lower_Barrier[NextCoupon_Idx];
				NextCouponUpperBarrier = info_hifive.CPN_Upper_Barrier[NextCoupon_Idx];
				NextCoupon = info_hifive.CPN_Rate[NextCoupon_Idx];

			}

			// Autocall Check

			if ((NextAutocall == NextAutocallPay && j == NextAutocall) || (j >= NextAutocall && j < NextAutocallPay))
			{
				for (k = 0; k < nK; k++)
				{
					SortedStrike[k] = info_hifive.Strike[k][NextAutocall_Idx];
					StrikeIdx[k] = k;
				}

				bubble_sort(SortedStrike, StrikeIdx, nK, 0);

				for (k = 0; k < nK; k++)
				{
					RedempStrike = info_hifive.Strike[StrikeIdx[k]][NextAutocall_Idx];
					if (SortedS[0] >= RedempStrike && RedempStrike > 0.0)
					{
						RedempSlope = info_hifive.Slope[StrikeIdx[k]][NextAutocall_Idx];
						RedempCPN = info_hifive.FixedAmount[StrikeIdx[k]][NextAutocall_Idx];
						RedempPayoff = Redemption_Payoff(info_hifive.FaceValue, info_hifive.FaceValueFlag, info_hifive.MaxProfit, info_hifive.MaxLoss, SortedS[0], RedempSlope, RedempCPN);
						Disc = DF_Array[NextAutocall_Idx];
						info_simul.pathprice[i] = info_simul.pathprice[i] + RedempPayoff * Disc;
						RedempFlag = 1;

						AutocallProb[NextAutocall_Idx] += RedempPayoff / (double)info_simul.nsimul;
						CF[NextAutocall_Idx] += 1.0 / (double)info_simul.nsimul;

						break;
					}
				}
				NextAutocall_Idx = min(info_hifive.NEvaluation - 1, NextAutocall_Idx + 1);
				NextAutocall = info_hifive.Days_Autocall_Eval[NextAutocall_Idx];
				NextAutocallPay = info_hifive.Days_Autocall_Pay[NextAutocall_Idx];

			}

			if (RedempFlag > 0)
			{
				break;
			}

			if (j >= NextLizardDate && j < NextLizardPayDate)
			{

				if (Now_Lizard_KI_State == 0 && SortedS[0] >= NextLizardBarrier)
				{

					RedempSlope = 0.0;
					RedempCPN = NextLizardCoupon;
					RedempPayoff = Redemption_Payoff(info_hifive.FaceValue, info_hifive.FaceValueFlag, info_hifive.MaxProfit, info_hifive.MaxLoss, SortedS[0], RedempSlope, RedempCPN);
					Disc = DF_Array[NextLizard_Idx];
					info_simul.pathprice[i] = info_simul.pathprice[i] + RedempPayoff * Disc;
					LizardRedempFlag = 1;

					AutocallProb[info_hifive.NEvaluation + 2 + NextLizard_Idx] += RedempPayoff / (double)info_simul.nsimul;
					CF[info_hifive.NEvaluation + 2 + NextLizard_Idx] += 1.0 / (double)info_simul.nsimul;

					break;;
				}
				if (j == NextLizardPayDate - 1)
				{
					NextLizard_Idx = min(info_hifive.NLizard - 1, NextLizard_Idx + 1);
					if (info_hifive.LizardFlag[NextLizard_Idx] > 0)
					{
						NextLizardDate = info_hifive.Days_Autocall_Eval[NextLizard_Idx];
						NextLizardPayDate = info_hifive.Days_Autocall_Pay[NextLizard_Idx];
						NextLizardStart = info_hifive.Days_LizardStart[NextLizard_Idx];
						NextLizardEnd = info_hifive.Days_LizardEnd[NextLizard_Idx];
						NextLizardBarrier = info_hifive.Lizard_Barrier_Level[NextLizard_Idx];
						NextLizardCoupon = info_hifive.Lizard_Coupon[NextLizard_Idx];
						Now_Lizard_KI_State = info_hifive.Now_Lizard_KI_State[NextLizard_Idx];
					}
				}
			}

			if (LizardRedempFlag > 0)
			{
				break;
			}

			T += dt;
		}

		// �������̿���
		if (RedempFlag == 0 && LizardRedempFlag == 0)
		{
			if (SortedS[0] < info_hifive.KI_Barrier_Level && info_hifive.KI_Method > 0)
				Now_KI_State = 1;

			if (Now_KI_State == 1)
			{
				for (k = 0; k < nK; k++)
				{
					SortedStrike[k] = info_hifive.Strike[k][info_hifive.NEvaluation - 1];
					StrikeIdx[k] = k;
				}

				bubble_sort(SortedStrike, StrikeIdx, nK, 0);

				RedempStrike = info_hifive.Strike[StrikeIdx[0]][info_hifive.NEvaluation - 1];
				RedempSlope = info_hifive.Slope[StrikeIdx[0]][info_hifive.NEvaluation + 1];
				RedempCPN = info_hifive.FixedAmount[StrikeIdx[0]][info_hifive.NEvaluation + 1];
				RedempPayoff = Redemption_Payoff(info_hifive.FaceValue, info_hifive.FaceValueFlag, info_hifive.MaxProfit, info_hifive.MaxLoss, SortedS[0], RedempSlope, RedempCPN);
				Disc = DF_Array[info_hifive.NEvaluation - 1];
				info_simul.pathprice[i] = info_simul.pathprice[i] + RedempPayoff * Disc;

				AutocallProb[info_hifive.NEvaluation + 1] += RedempPayoff / (double)info_simul.nsimul;
				CF[info_hifive.NEvaluation + 1] += 1.0 / (double)info_simul.nsimul;
			}
			else
			{
				for (k = 0; k < nK; k++)
				{
					SortedStrike[k] = info_hifive.Strike[k][info_hifive.NEvaluation - 1];
					StrikeIdx[k] = k;
				}

				bubble_sort(SortedStrike, StrikeIdx, nK, 0);

				RedempStrike = info_hifive.Strike[StrikeIdx[0]][info_hifive.NEvaluation - 1];
				RedempSlope = info_hifive.Slope[StrikeIdx[0]][info_hifive.NEvaluation];
				RedempCPN = info_hifive.FixedAmount[StrikeIdx[0]][info_hifive.NEvaluation];
				RedempPayoff = Redemption_Payoff(info_hifive.FaceValue, info_hifive.FaceValueFlag, info_hifive.MaxProfit, info_hifive.MaxLoss, SortedS[0], RedempSlope, RedempCPN);
				Disc = DF_Array[info_hifive.NEvaluation - 1];
				info_simul.pathprice[i] = info_simul.pathprice[i] + RedempPayoff * Disc;

				AutocallProb[info_hifive.NEvaluation] += RedempPayoff / (double)info_simul.nsimul;
				CF[info_hifive.NEvaluation] += 1.0 / (double)info_simul.nsimul;
			}
		}

	}

	MeanPrice = 0.0;
	for (i = 0; i < info_simul.nsimul; i++) MeanPrice += info_simul.pathprice[i] / (double)info_simul.nsimul;

	ResultPrice[0] = MeanPrice;

	for (i = 0; i < info_simul.nstock; i++) free(Cholesky_Matrix[i]);
	free(Cholesky_Matrix);					// �޸� 11 Cholesky_Matrix

	free(TimeNode);							// �޸� 3 TimeNode
	free(ParityNode);						// �޸� 4 ParityNode
	free(StockPrice);						// �޸� 5 StockPrice
	free(Randn);							// �޸� 6 Randn
	free(SortedS);							// �޸� 7 SortedS
	free(IdxS);								// �޸� 9 IdxS
	free(StrikeIdx);						// �޸� 2 StrikeIdx
	free(SortedStrike);						// �޸� 1 SortedStrike
	free(SortedS0);							// �޸� 8 SortedS0
	free(DF_Array);							// �޸� 10 DF_Array

	return MeanPrice;
}

long Preprocessing_HiFive_MC_Excel(
	long PricingDate_Ctype,			// 1: Pricing Date Ctpye ex) 20200115
	long NSimul,					// 2: Number of Simulation
	long GreekFlag,					// 3: Greek Flag
	double FaceValue,				// 4: Notional Amount
	long FaceValueFlag,				// 5: NA Using Flag

	double MaxProfit,				// 6: �ִ�����
	double MaxLoss,					// 7: �ִ�ս�
	long NEvaluate,					// 8: �����ȯ��ȸ��
	double KI_Barrier_Level,		// 9: Knock In Barrier %
	long Now_KI_State,				// 10: ���� Knock In State

	long KI_Method,					// 11: �������� 0: ���ι踮�����, 1: Continuous KI Barrier 2: ���� ����üũ
	long* EvalDate_Ctype,			// 12: �����ȯ �򰡳�¥ Ctype 
	long* PayDate_Ctype,			// 13: ���޳�¥ Ctype
	long* NStrike,					// 14: �����ȯ����
	double** Strike,				// 15: [0~NStrike+1] ��簡��1, [NStrike+2~2*NStrike+3] ��簡��2, [2*NStrike+3 ~ 3*NStrike+5] ��簡��3

	double** AutocallSlope,			// 16: [0~NStrike+1] ������1, [NStrike+2~2*NStrike+3] ������2, [2*NStrike+3 ~ 3*NStrike+5] ������3
	double** AutocallCPN,			// 17: [0~NStrike+1] �����ȯ����1, [NStrike+2~2*NStrike+3] �����ȯ����2, [2*NStrike+3 ~ 3*NStrike+5] �����ȯ����3
	long NLizard,					// 18: ���ڵ� �� ����
	long* LizardFlag,				// 19: Nȸ�� �����ȯ ���Ͽ� ���ڵ� ���µ� �� ���� ����
	long* LizardStartDate_Ctype,	// 20: ���ڵ� �踮�� üũ ������

	long* LizardEndDate_Ctype,		// 21: ���ڵ� �踮�� üũ ������
	double* LizardBarrierLevel,		// 22: ���ڵ� �踮�� ����
	long* Now_LizardHitting,		// 23: ���� ���ڵ� �踮�� ���û���
	double* LizardCoupon,			// 24: ���ڵ� ����
	long NCPN,						// 25: �Ϲ� ���� ����

	long* CPN_EvaluateDate_Ctype,	// 26: ���� �򰡳�¥ Ctype
	long* CPN_PayDate_Ctype,		// 27: ���� ���� ��¥ Ctype
	double* CPN_Lower_Barrier,		// 28: ���� �Ϲ�踮��
	double* CPN_Upper_Barrier,		// 29: ���� ���踮��
	double* CPN_Rate,				// 30: ���� ������

	long NStock,					// 31: �����ڻ갳��
	double* S,						// 32: �����ڻ����緹��
	double* X,						// 33: �����ڻ� ���ذ���
	double* Base_S,					// 34: �������� �����ȯ ���ϰ� ������ ���̿� �ִٸ� �����ȯ ������ ����
	double* Base_S_CPN,				// 35: �������� �������ϰ� ���������� ���̿� �ִٸ� ���������� ����

	double* CorrelationReshaped,	// 36: CorrelationMatrix.reshaped(-1)
	long N_TermDisc,				// 37: ���� Term ����
	double* TermDisc,				// 38: ���� Term
	double* RateDisc,				// 39: ���� Rate
	long* N_TermRf,					// 40: �����ڻ� �� Risk Free Rate ����

	double* TermRf,					// 41: �����ڻ� �� Risk Free Rate Term
	double* RateRf,					// 42: �����ڻ� �� Risk Free Rate
	long* NDivTerm,					// 43: �����ڻ� �� ��� Term ����
	long* DivFlag,					// 44: �����ڻ� �� ��� Flag
	double* TermDiv,				// 45: �����ڻ� �� ��� Term

	double* Div,					// 46: �����ڻ� �� ���� �Ǵ� �����
	long* QuantoFlag,				// 47: Quanto Flag
	double* QuantoCorr,				// 48: Quanto Corr.Reshaped(-1)
	long* NTermQuanto,				// 49: �����ڻ� �� FX Vol Term ����
	double* TermQuanto,				// 50: �����ڻ� �� FX Vol Term

	double* VolQuanto,				// 51: �����ڻ� �� FX Vol
	long* ImVolLocalVolFlag,		// 52: Implied Vol�� ����� �� Local Vol�� ����� �� Flag
	long* NParityVol,				// 53: �����ڻ� �� Vol Parity ����
	double* ParityVol_Adj,			// 54: �����ڻ� �� Parity ��밡�� ���� ��
	long* NTermVol,					// 55: �����ڻ� �� Vol Term ����

	double* TermVol,				// 56: �����ڻ� �� Vol Term
	double* Vol,					// 57: �����ڻ� �� Vol.reshape(-1)
	double* ResultPrice,			// 58: OutPut ����� ���� Array
	double* path_price,				// 59: Simul Price Path ���� Array
	double** daily_forward_rate,	// 60: Daily Forward Rate ���� Array

	double** daily_forward_div,		// 61: Daily Forward Div ���� Array
	double** daily_forward_fxvol,	// 62: Daily Forward FXVol ���� Array
	double* AutocallProb,			// 63: OutPut �����ȯ Ȯ�� ���� Array
	double* CPNProb,				// 64: OutPut ����Ȯ�� ���� Array (�̿ϼ�)
	double* ResultLocalVol,			// 65: OutPut Dupire Local Volatility

	double* ParityVol_Org,			// 66: �����ڻ� �� Parity ��������
	double*** FixedRandn			// 67: FixedRandomNumber (Greek����ǰ��)
)
{
	long i, j, k, n;
	long nterm_rf, nterm_div, nterm_quanto, nterm_vol;
	long nparity;
	long nvol;
	double price;
	long MaxSimulDays;

	for (i = 0; i < NSimul; i++) path_price[i] = 0.0;

	//////////////////////////////////////////////////////
	// ���ذ� ��� �����ְ� ���, Correlation Matrix ���·� Reshape
	/////////////////////////////////////////////////////

	double* S0_Value = (double*)malloc(sizeof(double) * NStock);						// 1
	double** CorrelationMatrix = (double**)malloc(sizeof(double*) * NStock);			// 2
	for (i = 0; i < NStock; i++)
	{
		S0_Value[i] = S[i] / X[i];
		CorrelationMatrix[i] = CorrelationReshaped + i * NStock;

		// Diagonal Check
		if (CorrelationMatrix[i][i] != 1.0) CorrelationMatrix[i][i] = 1.0;
	}

	// �ִ� �ùķ��̼�Ƚ��
	MaxSimulDays = DayCountAtoB(PricingDate_Ctype, PayDate_Ctype[NEvaluate - 1]) + 1;

	// Day Difference ���Ǹ� ���� �ùķ��̼��� �ʿ��� �� �ƴ��� �Ǵ�
	long* Days_Autocall_Eval = (long*)malloc(sizeof(long) * max(NEvaluate, 1));			// 3
	long* Days_Autocall_Pay = (long*)malloc(sizeof(long) * max(NEvaluate, 1));			// 4
	long* Days_LizardStart = (long*)malloc(sizeof(double) * max(NLizard, 1));			// 5
	long* Days_LizardEnd = (long*)malloc(sizeof(double) * max(NLizard, 1));				// 6
	long* Days_CPN_Eval = (long*)malloc(sizeof(double) * max(NCPN, 1));					// 7
	long* Days_CPN_Pay = (long*)malloc(sizeof(double) * max(NCPN, 1));					// 8

	for (i = 0; i < NEvaluate; i++)
	{
		Days_Autocall_Eval[i] = DayCountAtoB(PricingDate_Ctype, EvalDate_Ctype[i]);
		Days_Autocall_Pay[i] = DayCountAtoB(PricingDate_Ctype, PayDate_Ctype[i]);
	}

	for (i = 0; i < NLizard; i++)
	{
		Days_LizardStart[i] = DayCountAtoB(PricingDate_Ctype, LizardStartDate_Ctype[i]);
		Days_LizardEnd[i] = DayCountAtoB(PricingDate_Ctype, LizardEndDate_Ctype[i]);
	}

	for (i = 0; i < NCPN; i++)
	{
		Days_CPN_Eval[i] = DayCountAtoB(PricingDate_Ctype, CPN_EvaluateDate_Ctype[i]);
		Days_CPN_Pay[i] = DayCountAtoB(PricingDate_Ctype, CPN_PayDate_Ctype[i]);
	}

	long RedempFlag = 0;			// �����ȯ�Ǵ�������
	long RedempIdx = 0;				// �����ȯ �� ��° �Ǵ���
	long LizardRedempFlag = 0;		// ���ڵ��ȯ�Ǵ�������
	long LizardRedempIdx = 0;		// ���ڵ� �� ��° ��ȯ�Ǵ���
	long CPNRedempFlag = 0;			// �������޵Ǵ�������
	long CPNRedempIdx = 0;			// ���� �� ��° ���޵Ǵ���
	long CPNIdx = 0;				// ���޵��� ���� ���� Index
	long Evaluation_Idx = 0;		// �򰡽���
	long Maturity_Flag = 0;			// �����ȯ Flag

	long Simulation_Required = 1;	// �ϴ� �ùķ��̼��� �䱸�ȴٴ� �������� ����
	long nK = 3;					// ��簡�ݰ���

	double minS;
	double T_CPN;
	double DF_CPN;
	double* SortedStrike = (double*)malloc(sizeof(double) * nK);				// 9
	long* StrikeIdx = (long*)malloc(sizeof(long) * nK);							// 10
	double RedempSlope = 0.0;
	double RedempCPN = 0.0;
	// ���ݰ����� �����ȯ���� üũ
	for (i = 0; i < NEvaluate; i++)
	{
		if (Days_Autocall_Eval[i] == 0)
		{
			/////////////////////////////////
			// �������� ���� �����ǰ��
			/////////////////////////////////

			minS = S0_Value[0];
			for (j = 1; j < NStock; j++)
			{
				minS = min(minS, S0_Value[j]);
			}

			for (j = 0; j < nK; j++)
			{
				SortedStrike[j] = Strike[j][i];
				StrikeIdx[j] = j;
			}

			bubble_sort(SortedStrike, StrikeIdx, nK);

			/////////////////////////////////
			// �����ȯ �Ǿ����� üũ
			/////////////////////////////////

			for (j = 0; j < nK; j++)
			{
				if (minS >= SortedStrike[j] && SortedStrike[j] > 0.0)
				{
					RedempFlag = 1;
					RedempIdx = i;
					RedempSlope = AutocallSlope[StrikeIdx[j]][i];
					RedempCPN = AutocallCPN[StrikeIdx[j]][i];
					break;
				}
			}

			if (RedempFlag == 1)
			{
				break;
			}
			else
			{

				/////////////////////////////////
				// ���ڵ� �踮�� ���õ��� �ʾ����� ���ڵ��ȯ
				/////////////////////////////////

				if (i < NLizard)
				{
					if (LizardFlag[i] > 0 && Now_LizardHitting[i] == 0)
					{
						LizardRedempFlag = 1;
						LizardRedempIdx = 1;
						break;
					}
				}

			}
		}
		else if (Days_Autocall_Eval[i] < 0 && Days_Autocall_Pay[i] > 0)
		{

			/////////////////////////////////
			// ���ݰ������� ���ϰ� ������ ������ ���
			/////////////////////////////////

			// ���� ������ �ԷµǾ������� �װ��� ���� �ƴϸ� ���簡�� ����.
			if (Base_S[0] > 0.0) minS = Base_S[0] / X[0];
			else minS = S0_Value[0];

			for (j = 1; j < NStock; j++)
			{
				if (Base_S[i] > 0.0) minS = min(minS, Base_S[j] / X[j]);
				else minS = min(minS, S0_Value[i]);
			}

			for (j = 0; j < nK; j++)
			{
				SortedStrike[j] = Strike[j][i];
				StrikeIdx[j] = j;
			}

			bubble_sort(SortedStrike, StrikeIdx, nK);

			/////////////////////////////////
			// �����ȯ �Ǿ����� üũ
			/////////////////////////////////

			for (j = 0; j < nK; j++)
			{
				if (minS >= SortedStrike[j] && SortedStrike[j] > 0.0)
				{
					RedempFlag = 1;
					RedempIdx = i;
					RedempSlope = AutocallSlope[StrikeIdx[j]][i];
					RedempCPN = AutocallCPN[StrikeIdx[j]][i];
					break;
				}
			}

			if (RedempFlag == 1)
			{
				break;
			}
			else
			{

				/////////////////////////////////
				// ���ڵ� �踮�� ���õ��� �ʾ����� ���ڵ��ȯ
				/////////////////////////////////

				if (i < NLizard)
				{
					if (LizardFlag[i] > 0 && Now_LizardHitting[i] == 0)
					{
						LizardRedempFlag = 1;
						LizardRedempIdx = 1;
						break;
					}
				}

			}
		}

		if (Days_Autocall_Eval[max(0, NEvaluate - 1 - i)] > 0)
		{
			Evaluation_Idx = NEvaluate - 1 - i;
		}
	}

	/////////////////////////////////
	// ���� ������� �����踮�� üũ
	/////////////////////////////////

	for (i = 0; i < NCPN; i++)
	{
		if (Days_CPN_Eval[i] == 0)
		{
			minS = S0_Value[0];
			for (j = 1; j < NStock; j++)
			{
				minS = min(minS, S0_Value[j]);
			}

			if (minS >= CPN_Lower_Barrier[i] && minS < CPN_Upper_Barrier[i])
			{
				CPNRedempFlag = 1;
				CPNRedempIdx = i;
				T_CPN = ((double)Days_CPN_Pay[i]) / 365.0;
				DF_CPN = Calc_Discount_Factor(TermDisc, RateDisc, N_TermDisc, T_CPN) * CPN_Rate[i];
				break;
			}
		}
		else if (Days_CPN_Eval[i] < 0 && Days_CPN_Pay[i] > 0)
		{
			if (Base_S_CPN[0] > 0.0)
				minS = Base_S_CPN[0] / X[0];
			else
				minS = S0_Value[0];

			for (j = 1; j < NStock; j++)
			{
				if (Base_S_CPN[i] > 0.0)
					minS = min(minS, Base_S_CPN[j] / X[j]);
				else
					minS = min(minS, S0_Value[i]);
			}

			if (minS >= CPN_Lower_Barrier[i] && minS < CPN_Upper_Barrier[i])
			{
				CPNRedempFlag = 1;
				CPNRedempIdx = i;
				T_CPN = ((double)Days_CPN_Pay[i]) / 365.0;
				DF_CPN = Calc_Discount_Factor(TermDisc, RateDisc, N_TermDisc, T_CPN) * CPN_Rate[i];
				break;
			}
		}

		if (Days_CPN_Eval[max(0, NCPN - 1 - i)] > 0)
		{
			CPNIdx = NCPN - 1 - i;
		}
	}

	/////////////////////////////////
	// �ϴ� ���� �ְ� �������� ���λ��º��� �ٽ� üũ
	/////////////////////////////////

	if (KI_Method == 1)
	{
		for (i = 0; i < NStock; i++)
		{
			if (S0_Value[i] < KI_Barrier_Level)
			{
				Now_KI_State = 1;
				break;
			}
		}
	}

	/////////////////////////////////
	// �����ȯ üũ
	/////////////////////////////////

	if (Days_Autocall_Eval[NEvaluate - 1] <= 0)
	{
		RedempFlag = 1;

		minS = S0_Value[0];
		for (j = 1; j < NStock; j++)
		{
			minS = min(minS, S0_Value[j]);
		}

		if (KI_Method == 2 && minS < KI_Barrier_Level)
		{
			Now_KI_State = 1;
		}

		if (Now_KI_State > 0)
		{
			RedempIdx = NEvaluate + 1;
			RedempSlope = 1.0;
			for (j = 0; j < nK; j++)
			{
				if (AutocallSlope[j][NEvaluate + 1] != 0.0)
				{
					RedempSlope = AutocallSlope[j][NEvaluate + 1];
					break;
				}
			}
			for (j = 0; j < nK; j++)
			{
				if (AutocallCPN[j][NEvaluate + 1] != 0.0)
				{
					RedempCPN = AutocallCPN[j][NEvaluate + 1];
					break;
				}
			}
		}
		else
		{
			RedempIdx = NEvaluate;
			RedempSlope = 0.0;
			for (j = 0; j < nK; j++)
			{
				if (AutocallSlope[j][NEvaluate + 1] != 0.0)
				{
					RedempSlope = AutocallSlope[j][NEvaluate + 1];
					break;
				}
			}
			for (j = 0; j < nK; j++)
			{
				if (AutocallCPN[j][NEvaluate + 1] != 0.0)
				{
					RedempCPN = AutocallCPN[j][NEvaluate + 1];
					break;
				}
			}
		}
	}

	///////////////////////////////////////////////////////
	// �����ȯ �Ǵ� ���ڵ��ȯ �Ǿ��ٸ� �ùķ��̼��� �ʿ������ ����
	///////////////////////////////////////////////////////

	if (RedempFlag == 1) Simulation_Required = 0;
	if (LizardRedempFlag == 1) Simulation_Required = 0;

	double TTM;
	double DiscFactor;
	double Payoff;
	if (RedempFlag > 0)
	{
		TTM = (double)Days_Autocall_Pay[min(NEvaluate - 1, RedempIdx)] / 365.0;
		DiscFactor = Calc_Discount_Factor(TermDisc, RateDisc, N_TermDisc, TTM);
		Payoff = Redemption_Payoff(FaceValue, FaceValueFlag, MaxProfit, MaxLoss, minS, RedempSlope, RedempCPN);
		ResultPrice[0] = Payoff * DiscFactor;

	}
	else if (LizardRedempFlag > 0)
	{
		TTM = (double)Days_Autocall_Pay[LizardRedempIdx] / 365.0;
		DiscFactor = Calc_Discount_Factor(TermDisc, RateDisc, N_TermDisc, TTM);
		Payoff = Redemption_Payoff(FaceValue, FaceValueFlag, MaxProfit, MaxLoss, minS, RedempSlope, RedempCPN);
		ResultPrice[0] = Payoff * DiscFactor;
	}

	simulinfo Info_Simul(Simulation_Required, NSimul, NStock, GreekFlag, PricingDate_Ctype, S0_Value, CorrelationMatrix, MaxSimulDays, FixedRandn, path_price);

	//////////////////////////
	// �̹� ���޵� ������ �ִٸ� ������ �̸� �־��ְ� �ùķ��̼� ����
	//////////////////////////

	if (CPNRedempFlag == 1)
	{
		for (i = 0; i < NSimul; i++)
		{
			Info_Simul.pathprice[i] = DF_CPN;
		}
	}

	//////////////////////////
	// �ùķ��̼� Daily Forward Rate, Daily Div ����
	//////////////////////////

	Info_Simul.set_daily_data(N_TermRf, TermRf, RateRf,
		NDivTerm, TermDiv, Div, DivFlag,
		NTermQuanto, TermQuanto, VolQuanto, QuantoFlag, QuantoCorr,
		daily_forward_rate, daily_forward_div, daily_forward_fxvol);


	HiFiveInfo info_hifive;

	info_hifive.FaceValue = FaceValue;
	info_hifive.FaceValueFlag = FaceValueFlag;
	info_hifive.NStock = NStock;

	info_hifive.MaxProfit = MaxProfit;
	info_hifive.MaxLoss = MaxLoss;

	// KI ���� ����
	info_hifive.KI_Method = KI_Method;
	info_hifive.KI_Barrier_Level = KI_Barrier_Level;
	info_hifive.Now_KI_State = Now_KI_State;

	// Autocall ���� ����
	info_hifive.NEvaluation = NEvaluate - Evaluation_Idx;
	info_hifive.Days_Autocall_Eval = Days_Autocall_Eval + Evaluation_Idx;
	info_hifive.Days_Autocall_Pay = Days_Autocall_Pay + Evaluation_Idx;

	double** AdjStrike = (double**)malloc(sizeof(double*) * nK);				// 11
	double** AdjSlope = (double**)malloc(sizeof(double*) * nK);					// 12
	double** AdjFixedAmount = (double**)malloc(sizeof(double*) * nK);			// 13

	for (i = 0; i < nK; i++)
	{
		AdjStrike[i] = Strike[i] + Evaluation_Idx;
		AdjSlope[i] = AutocallSlope[i] + Evaluation_Idx;
		AdjFixedAmount[i] = AutocallCPN[i] + Evaluation_Idx;
	}

	info_hifive.Strike = AdjStrike;
	info_hifive.Slope = AdjSlope;
	info_hifive.FixedAmount = AdjFixedAmount;
	info_hifive.nK = nK;


	// Lizard ���� ����
	info_hifive.NLizard = max(0, NLizard - Evaluation_Idx);
	info_hifive.LizardFlag = LizardFlag + Evaluation_Idx;
	info_hifive.Days_LizardStart = Days_LizardStart + Evaluation_Idx;
	info_hifive.Days_LizardEnd = Days_LizardEnd + Evaluation_Idx;
	info_hifive.Lizard_Barrier_Level = LizardBarrierLevel + Evaluation_Idx;
	info_hifive.Lizard_Coupon = LizardCoupon + Evaluation_Idx;
	info_hifive.Now_Lizard_KI_State = Now_LizardHitting + Evaluation_Idx;


	info_hifive.NCPN = NCPN - CPNIdx;
	info_hifive.Days_CPN_Eval = Days_CPN_Eval + CPNIdx;
	info_hifive.Days_CPN_Pay = Days_CPN_Pay + CPNIdx;
	info_hifive.CPN_Lower_Barrier = CPN_Lower_Barrier + CPNIdx;
	info_hifive.CPN_Upper_Barrier = CPN_Upper_Barrier + CPNIdx;
	info_hifive.CPN_Rate = CPN_Rate + CPNIdx;

	curveinfo disc_curve(N_TermDisc, TermDisc, RateDisc);   // Discount Curve Setting

	curveinfo* rf_curves = (curveinfo*)malloc(sizeof(curveinfo) * NStock);//new curveinfo[NStock];           // RiskFree Curve Setting
	curveinfo* div_curves = (curveinfo*)malloc(sizeof(curveinfo) * NStock);// new curveinfo[NStock];          // Dividend Setting
	curveinfo* quanto_curves = (curveinfo*)malloc(sizeof(curveinfo) * NStock);// new curveinfo[NStock];       // Quanto Setting 

	nterm_rf = 0;
	nterm_div = 0;
	nterm_quanto = 0;
	for (i = 0; i < NStock; i++)
	{
		(rf_curves + i)->initialize(N_TermRf[i], TermRf + nterm_rf, RateRf + nterm_rf);
		nterm_rf += N_TermRf[i];

		(div_curves + i)->initialize(NDivTerm[i], TermDiv + nterm_div, Div + nterm_div);
		nterm_div += NDivTerm[i];

		(quanto_curves + i)->initialize(NTermQuanto[i], TermQuanto + nterm_quanto, VolQuanto + nterm_quanto);
		nterm_quanto += NTermQuanto[i];
	}

	//////////////////////////
	// Imvol, LocalVol Setting
	//////////////////////////

	volinfo* VolMatrixList = (volinfo*)malloc(sizeof(volinfo) * NStock); // new volinfo[NStock];
	double* Parity_AfterAdj;
	nterm_vol = 0;
	nparity = 0;
	nvol = 0;
	n = 0;
	for (i = 0; i < NStock; i++)
	{
		Parity_AfterAdj = ParityVol_Adj + nparity;
		(VolMatrixList + i)->hardcopy(NParityVol[i], ParityVol_Org + nparity, NTermVol[i], TermVol + nterm_vol, Vol + nvol);
		nparity += NParityVol[i];
		nterm_vol += NTermVol[i];
		nvol += NParityVol[i] * NTermVol[i];
		if (ImVolLocalVolFlag[i] == 0 && (NParityVol[i] > 3 && NTermVol[i] > 3))
		{
			(VolMatrixList + i)->set_localvol((rf_curves + i), (div_curves + i), 2.0, 0.001);
			for (j = 0; j < NParityVol[i]; j++)
			{
				(VolMatrixList + i)->Parity[j] = Parity_AfterAdj[j];
				(VolMatrixList + i)->Parity_Locvol[j] = Parity_AfterAdj[j];
			}
		}
		else
		{
			(VolMatrixList + i)->LocalVolMat = (VolMatrixList + i)->Vol_Matrix;
			(VolMatrixList + i)->Parity_Locvol = (VolMatrixList + i)->Parity;
			(VolMatrixList + i)->Term_Locvol = (VolMatrixList + i)->Term;
		}

		// LocalVol Result ����
		for (j = 0; j < NParityVol[i]; j++)
		{
			for (k = 0; k < NTermVol[i]; k++)
			{
				ResultLocalVol[n] = (VolMatrixList + i)->LocalVolMat[j][k];
				n++;
			}
		}
	}

	double* CF = (double*)calloc((NEvaluate + 2 + NLizard), sizeof(double));			// 14
	
	long pricingonly = 1;
	if (GreekFlag == 0) pricingonly = 1;
	else pricingonly = 0;

	// �ùķ��̼��� �ʿ� ���� ���
	if (RedempFlag > 0 || LizardRedempFlag > 0)
	{
		price = ResultPrice[0];
	}
	else
	{
		price = Pricing_HiFive_MC(Info_Simul, info_hifive, disc_curve, rf_curves, div_curves, quanto_curves, VolMatrixList, ResultPrice, pricingonly, AutocallProb + Evaluation_Idx, CF + Evaluation_Idx, CPNProb);

		for (i = 0; i < NEvaluate + 2 + NLizard; i++) AutocallProb[NEvaluate + 2 + NLizard + i] = CF[i];
	}

	free(S0_Value);
	free(CorrelationMatrix);

	free(SortedStrike);
	free(StrikeIdx);

	if (rf_curves) free(rf_curves);
	if (div_curves) free(div_curves);
	if (quanto_curves) free(quanto_curves);
	if (VolMatrixList) free(VolMatrixList);

	free(Days_Autocall_Eval);
	free(Days_Autocall_Pay);
	free(Days_LizardStart);
	free(Days_LizardEnd);
	free(Days_CPN_Eval);
	free(Days_CPN_Pay);
	free(AdjStrike);
	free(AdjSlope);
	free(AdjFixedAmount);
	free(CF);
	return 1;
}

void Logging_HiFive_ELS_MC(
	long PricingDate_Excel,			// ���ݰ�곯¥ ExcelType Ex) 44201(2021��01��05��)
	long NSimul,					// �ùķ��̼ǰ���
	long GreekFlag,					// �׸������������
	double FaceValue,				// ���ݾ�
	long FaceValueFlag,				// ���ݼ�������

	double MaxProfit,				// �ִ�����
	double MaxLoss,					// �ִ�ս�
	long NEvaluate,					// �����ȯ ���ϰ���
	double KI_Barrier_Level,		// ���ι踮�����
	long Now_KI_State,				// ���� ���λ���

	long KI_Method,					// ����ó�����
	long* EvalDate_Excel,			// �����ȯ ExcelType���� Array [ Shape = (NEvaluate , ) ]
	long* PayDate_Excel,			// �����ȯ ExcelType������ Array [ Shape = (NEvaluate , ) ]
	long* NStrike,					// �����ȯ ȸ���� ��簡�ݰ��� Array [ Shape = (NEvaluate , ) ]
	double* StrikeLevel,			// �����ȯ ȸ���� ��簡�� Array [ Shape = reshape(3 * NEvaluate) ]

	double* Slope,					// �����ȯ ȸ���� ������ [ Shape = reshape(3 * NEvaluate)  ]
	double* FixedAmount,			// �����ȯ ȸ���� ���� [ Shape = reshape(3 * NEvaluate)  ]
	long NLizard,					// ���ڵ��ȯ ���� ����
	long* LizardFlag,				// �����ȯ ȸ���� ���ڵ��ȯ ������ ���� Array [ Shape = (NLizard , ) ]
	long* LizardStartDate_Excel,	// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]

	long* LizardEndDate_Excel,		// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]
	double* LizardBarrierLevel,		// �����ȯ ȸ���� ���ڵ�踮�� �踮��� Array
	long* Now_LizardHitting,		// �����ȯ ȸ���� ���ڵ�踮�� ���� Hitting���� Array
	double* LizardCoupon,			// �����ȯ ȸ���� ���ڵ�踮�� ���������� Array
	long NCPN,						// �Ϲ� ���� ���� ����

	long* CPN_EvaluateDate_Excel,	// �Ϲ� ���� ���� ExcelType Array [ Shape = (NCPN , ) ]
	long* CPN_PayDate_Excel,		// �Ϲ� ���� ������ ExcelType Array [ Shape = (NCPN , ) ]
	double* CPN_Lower_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Upper_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Rate,				// �Ϲ� ���� ���������� Array [ Shape = (NCPN , ) ]

	long NStock,					// �����ڻ갳��
	double* S0X0,					// [�����ڻ�Array + ���ذ���Array + Autocall���� �򰡰���Array + Coupon���� �򰡰���Array]
	double* CorrelationReshaped,	// Correlation Matrix.reshape(-1)
	long* NTerm,					// ������ �Ⱓ���� ���� (Discount, Rf1, Rf2, ....) [ Shape = (NStock +1 , )]
	double* TermRate,				// ������ �Ⱓ���� Term -> append(Discount Term Array + RfTermArray1 + RfTermArray2 + ...] , Shape = (sum(NTerm) , )

	double* Rate,					// ������ �Ⱓ���� Rate append(Discount Rate Array + RfRateArray1 + RfRateArray2 + ...], Shape = (sum(NTerm), )
	long* NDivTerm,					// ��� �Ⱓ���� ���� (Stock1, Stock2, ....)    [ Shape = (NStock , )]
	long* DivFlag,					// ��� �Ⱓ���� ���Ÿ�� (Stock1DivType, ) , Shape = (sum(NDivTerm) , )
	double* TermDiv,				// ��� �Ⱓ���� Term -> append(Stock1DivTermArray+ Stock2DivTermArray + ....) , Shape = (sum(NDivTerm) , )
	double* Div,					// ��� �Ⱓ���� Rate �Ǵ� �ݾ� -> append(Stock1DivArray + Stock2DivArray + ....), Shape = (sum(NDivTerm), )

	long* QuantoFlag,				// Quanto ��뿩�� Array [Shape = (NStock ,)]
	double* QuantoCorr,				// FX, �����ڻ� Correlation Array [Shape = (NStock , )]
	long* NTermQuanto,				// Quanto FX Vol Term ���� Array [ Shape = (NStock, )]
	double* TermQuanto,				// Quanto FX Vol Term Array -> append[ FX Vol Term1 Array + FX Vol Term2 Array + FX Vol Term3 Array + ...] [ Shape = (sum(NTermQuanto), )]
	double* VolQuanto,				// Quanto FX Vol Array -> append[FX Vol1 Array + FX Vol2 Array + FX Vol3 Array + ....] [ Shape = (sum(NTermQuanto), )]

	long* ImVolLocalVolFlag,		// Imvol�� �� �� Localvol�� �� �� Flag Array (0: Imvol, 1: LocalVol) [ Shape = (NStock, )]
	long* NParityVol,				// �����ڻ꺰 �з�Ƽ ���� Array [ Shape = (NStock, )]
	double* ParityVol,				// �����ڻ꺰 �з�Ƽ Array -> append[Parity1 Array, Parity2 Array, Parity3 Array...]
	long* NTermVol,					// �����ڻ꺰 Volatility Term ���� Array [ Shape = (NStock, )]
	double* TermVol,				// �����ڻ꺰 Volatility Term Array -> append[VolTerm1, VolTerm2, VolTerm3 ...]

	double* Vol,					// �����ڻ꺰 Volatility Array -> append[ReshapedVol1, ReshapedVol2, ReshapedVol3, ReshapedVol4 .....]
	char* CalcFunctionName,
	char* SaveFileName
)
{
	long i, ntotalnterm, ntotaldiv, ntotalquanto;
	long nparitytotal, ntermvoltotal, nvoltotal;
	ntotalnterm = 0;
	ntotaldiv = 0;
	ntotalquanto = 0;
	nparitytotal = 0;
	ntermvoltotal = 0;
	nvoltotal = 0;
	for (i = 0; i < NStock + 1; i++) ntotalnterm += NTerm[i];
	for (i = 0; i < NStock; i++) ntotaldiv += NDivTerm[i];
	for (i = 0; i < NStock; i++) ntotalquanto += NTermQuanto[i];

	for (i = 0; i < NStock; i++) nparitytotal += NParityVol[i];
	for (i = 0; i < NStock; i++) ntermvoltotal += NTermVol[i];
	for (i = 0; i < NStock; i++) nvoltotal += NParityVol[i] * NTermVol[i];
	double* volpoint;
	DumppingTextData(CalcFunctionName, SaveFileName, "PricingDate_Excel", PricingDate_Excel);
	DumppingTextData(CalcFunctionName, SaveFileName, "NSimul", NSimul);
	DumppingTextData(CalcFunctionName, SaveFileName, "GreekFlag", GreekFlag);
	DumppingTextData(CalcFunctionName, SaveFileName, "FaceValue", FaceValue);
	DumppingTextData(CalcFunctionName, SaveFileName, "FaceValueFlag", FaceValueFlag);

	DumppingTextData(CalcFunctionName, SaveFileName, "MaxProfit", MaxProfit);
	DumppingTextData(CalcFunctionName, SaveFileName, "MaxLoss", MaxLoss);
	DumppingTextData(CalcFunctionName, SaveFileName, "NEvaluate", NEvaluate);
	DumppingTextData(CalcFunctionName, SaveFileName, "KI_Barrier_Level", KI_Barrier_Level);
	DumppingTextData(CalcFunctionName, SaveFileName, "Now_KI_State", Now_KI_State);

	DumppingTextData(CalcFunctionName, SaveFileName, "KI_Method", KI_Method);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "EvalDate_Excel", NEvaluate, EvalDate_Excel);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayDate_Excel", NEvaluate, PayDate_Excel);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "NStrike", NEvaluate, NStrike);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "StrikeLevel", 3, NEvaluate, StrikeLevel);

	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "Slope", 3, (NEvaluate + 2), Slope);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "FixedAmount", 3, (NEvaluate + 2), FixedAmount);
	DumppingTextData(CalcFunctionName, SaveFileName, "NLizard", NLizard);
	if (NLizard > 0)
	{
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardFlag", NLizard, LizardFlag);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardStartDate_Excel", NLizard, LizardStartDate_Excel);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardEndDate_Excel", NLizard, LizardEndDate_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardBarrierLevel", NLizard, LizardBarrierLevel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Now_LizardHitting", NLizard, Now_LizardHitting);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardCoupon", NLizard, LizardCoupon);
		DumppingTextData(CalcFunctionName, SaveFileName, "NCPN", NCPN);
	}
	if (NCPN > 0)
	{
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_EvaluateDate_Excel", NCPN, CPN_EvaluateDate_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_PayDate_Excel", NCPN, CPN_PayDate_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_Lower_Barrier", NCPN, CPN_Lower_Barrier);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_Upper_Barrier", NCPN, CPN_Upper_Barrier);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_Rate", NCPN, CPN_Rate);
	}

	DumppingTextData(CalcFunctionName, SaveFileName, "NStock", NStock);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "S0X0", NStock * 3, S0X0);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "Correlation", NStock, NStock, CorrelationReshaped);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "NTerm", NStock + 1, NTerm);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "TermRate", ntotalnterm, TermRate);

	DumppingTextDataArray(CalcFunctionName, SaveFileName, "Rate", ntotalnterm, Rate);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "NDivTerm", NStock, NDivTerm);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "DivFlag", NStock, DivFlag);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "TermDiv", ntotaldiv, TermDiv);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "Div", ntotaldiv, Div);

	DumppingTextDataArray(CalcFunctionName, SaveFileName, "QuantoFlag", NStock, QuantoFlag);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "QuantoCorr", NStock, QuantoCorr);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "NTermQuanto", NStock, NTermQuanto);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "TermQuanto", ntotalquanto, TermQuanto);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "VolQuanto", ntotalquanto, VolQuanto);

	DumppingTextDataArray(CalcFunctionName, SaveFileName, "ImVolLocalVolFlag", NStock, ImVolLocalVolFlag);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "NParityVol", NStock, NParityVol);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "ParityVol", nparitytotal, ParityVol);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "NTermVol", NStock, NTermVol);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "TermVol", ntermvoltotal, TermVol);

	nvoltotal = 0;
	for (i = 0; i < NStock; i++)
	{
		volpoint = Vol + nvoltotal;
		DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "VolMatrix", NParityVol[i], NTermVol[i], volpoint);
		nvoltotal += NParityVol[i] * NTermVol[i];
	}

}
DLLEXPORT(long) Excel_HiFive_ELS_MC(
	long PricingDate,				// ���ݰ�곯¥
	long NSimul,					// �ùķ��̼ǰ���
	long GreekFlag,					// �׸������������
	double FaceValue,				// ���ݾ�
	long FaceValueFlag,				// ���ݼ�������

	double MaxProfit,				// �ִ�����
	double MaxLoss,					// �ִ�ս�
	long NEvaluate,					// �����ȯ ���ϰ���
	double KI_Barrier_Level,		// ���ι踮�����
	long Now_KI_State,				// ���� ���λ���

	long KI_Method,					// ����ó�����
	long* EvalDate,					// �����ȯ ExcelType���� Array [ Shape = (NEvaluate , ) ]
	long* PayDate,					// �����ȯ ExcelType������ Array [ Shape = (NEvaluate , ) ]
	long* NStrike,					// �����ȯ ȸ���� ��簡�ݰ��� Array [ Shape = (NEvaluate , ) ]
	double* StrikeLevel,			// �����ȯ ȸ���� ��簡�� Array [ Shape = reshape(3 * NEvaluate) ]

	double* Slope,					// �����ȯ ȸ���� ������ [ Shape = reshape(3 * NEvaluate)  ]
	double* FixedAmount,			// �����ȯ ȸ���� ���� [ Shape = reshape(3 * NEvaluate)  ]
	long NLizard,					// ���ڵ��ȯ ���� ����
	long* LizardFlag,				// �����ȯ ȸ���� ���ڵ��ȯ ������ ���� Array [ Shape = (NLizard , ) ]
	long* LizardStartDate,			// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]

	long* LizardEndDate,			// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]
	double* LizardBarrierLevel,		// �����ȯ ȸ���� ���ڵ�踮�� �踮��� Array
	long* Now_LizardHitting,		// �����ȯ ȸ���� ���ڵ�踮�� ���� Hitting���� Array
	double* LizardCoupon,			// �����ȯ ȸ���� ���ڵ�踮�� ���������� Array
	long NCPN,						// �Ϲ� ���� ���� ����

	long* CPN_EvaluateDate,			// �Ϲ� ���� ���� ExcelType Array [ Shape = (NCPN , ) ]
	long* CPN_PayDate,				// �Ϲ� ���� ������ ExcelType Array [ Shape = (NCPN , ) ]
	double* CPN_Lower_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Upper_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Rate,				// �Ϲ� ���� ���������� Array [ Shape = (NCPN , ) ]

	long NStock,					// �����ڻ갳��
	double* S0X0,					// [�����ڻ�Array + ���ذ���Array + Autocall���� �򰡰���Array + Coupon���� �򰡰���Array]
	double* CorrelationReshaped,	// Correlation Matrix.reshape(-1)
	long* NTerm,					// ������ �Ⱓ���� ���� (Discount, Rf1, Rf2, ....) [ Shape = (NStock +1 , )]
	double* TermRate,				// ������ �Ⱓ���� Term -> append(Discount Term Array + RfTermArray1 + RfTermArray2 + ...] , Shape = (sum(NTerm) , )

	double* Rate,					// ������ �Ⱓ���� Rate append(Discount Rate Array + RfRateArray1 + RfRateArray2 + ...], Shape = (sum(NTerm), )
	long* NDivTerm,					// ��� �Ⱓ���� ���� (Stock1, Stock2, ....)    [ Shape = (NStock , )]
	long* DivFlag,					// ��� �Ⱓ���� ���Ÿ�� (Stock1DivType, ) , Shape = (sum(NDivTerm) , )
	double* TermDiv,				// ��� �Ⱓ���� Term -> append(Stock1DivTermArray+ Stock2DivTermArray + ....) , Shape = (sum(NDivTerm) , )
	double* Div,					// ��� �Ⱓ���� Rate �Ǵ� �ݾ� -> append(Stock1DivArray + Stock2DivArray + ....), Shape = (sum(NDivTerm), )

	long* QuantoFlag,				// Quanto ��뿩�� Array [Shape = (NStock ,)]
	double* QuantoCorr,				// FX, �����ڻ� Correlation Array [Shape = (NStock , )]
	long* NTermQuanto,				// Quanto FX Vol Term ���� Array [ Shape = (NStock, )]
	double* TermQuanto,				// Quanto FX Vol Term Array -> append[ FX Vol Term1 Array + FX Vol Term2 Array + FX Vol Term3 Array + ...] [ Shape = (sum(NTermQuanto), )]
	double* VolQuanto,				// Quanto FX Vol Array -> append[FX Vol1 Array + FX Vol2 Array + FX Vol3 Array + ....] [ Shape = (sum(NTermQuanto), )]

	long* ImVolLocalVolFlag,		// Imvol�� �� �� Localvol�� �� �� Flag Array (0: Imvol, 1: LocalVol) [ Shape = (NStock, )]
	long* NParityVol,				// �����ڻ꺰 �з�Ƽ ���� Array [ Shape = (NStock, )]
	double* ParityVol,				// �����ڻ꺰 �з�Ƽ Array -> append[Parity1 Array, Parity2 Array, Parity3 Array...]
	long* NTermVol,					// �����ڻ꺰 Volatility Term ���� Array [ Shape = (NStock, )]
	double* TermVol,				// �����ڻ꺰 Volatility Term Array -> append[VolTerm1, VolTerm2, VolTerm3 ...]

	double* Vol,					// �����ڻ꺰 Volatility Array -> append[ReshapedVol1, ReshapedVol2, ReshapedVol3, ReshapedVol4 .....]
	double* ResultPrice,			// ������� �� ��Ÿ��������, SABR Parameter Shape = (1 + NStock * 3 + sum(NTermVol)*3 )
	double* AutocallProb,			// �����ȯ Ȯ�� �� �����ȯ Payoff -> Shape = (NEvaluate * 2, )
	double* CPNProb,				// ���� Ȯ�� �� ���� -> Shape = (NCPN * 2, )
	double* ResultLocalVol,			// LocalVolatility �����

	char* Error,
	double* RMSPE,
	long TextDumpFlag
)
{
	//_crtBreakAlloc = 91;

	long i, j, k;

	long ResultCode;

	/////////////
	// ����üũ
	/////////////

	ResultCode = ErrorCheck(
		PricingDate, NSimul, GreekFlag, FaceValue, FaceValueFlag,
		MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
		KI_Method, EvalDate, PayDate, NStrike, StrikeLevel,
		Slope, FixedAmount, NLizard, LizardFlag, LizardStartDate,
		LizardEndDate, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
		CPN_EvaluateDate, CPN_PayDate, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
		NStock, S0X0, CorrelationReshaped, NTerm, TermRate,
		Rate, NDivTerm, DivFlag, TermDiv, Div,
		QuantoFlag, QuantoCorr, NTermQuanto, TermQuanto, VolQuanto,
		ImVolLocalVolFlag, NParityVol, ParityVol, NTermVol, TermVol,
		Vol, ResultPrice, AutocallProb, CPNProb, ResultLocalVol,
		Error);

	if (ResultCode < 0) return ResultCode;

	char CalcFunctionName[] = "Excel_HiFive_ELS_MC";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag > 0)
	{

		Logging_HiFive_ELS_MC(PricingDate, NSimul, GreekFlag, FaceValue, FaceValueFlag,
			MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
			KI_Method, EvalDate, PayDate, NStrike, StrikeLevel,
			Slope, FixedAmount, NLizard, LizardFlag, LizardStartDate,
			LizardEndDate, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
			CPN_EvaluateDate, CPN_PayDate, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
			NStock, S0X0, CorrelationReshaped, NTerm, TermRate,
			Rate, NDivTerm, DivFlag, TermDiv, Div,
			QuantoFlag, QuantoCorr, NTermQuanto, TermQuanto, VolQuanto,
			ImVolLocalVolFlag, NParityVol, ParityVol, NTermVol, TermVol,
			Vol, CalcFunctionName, SaveFileName);
	}
	/////////////
	// ���� �� Ǯ�� and Reshape�ϱ�
	/////////////

	long nK = 3;
	double** Strike = (double**)malloc(sizeof(double*) * nK);			// 1
	double** AutocallSlope = (double**)malloc(sizeof(double*) * nK);	// 2
	double** AutocallCPN = (double**)malloc(sizeof(double*) * nK);		// 3
	for (i = 0; i < nK; i++)
	{
		Strike[i] = StrikeLevel + NEvaluate * i;
		AutocallSlope[i] = Slope + (NEvaluate + 2) * i;
		AutocallCPN[i] = FixedAmount + (NEvaluate + 2) * i;
	}

	double* S = S0X0;
	double* X = S0X0 + NStock;
	double* Base_S = S0X0 + 2 * NStock;
	double* Base_S_CPN = S0X0 + 3 * NStock;

	long N_DF_Curve = NTerm[0];
	double* Term_DF_Curve = TermRate;
	double* Rate_DF_Curve = Rate;

	long* N_Rf_Curve = NTerm + 1;
	double* Term_Rf_Curve = TermRate + NTerm[0];
	double* Rate_Rf_Curve = Rate + NTerm[0];

	////////////////////////////
	// SABR Imvol Calibration //
	////////////////////////////

	long s_rf, s_div, s_parity, s_termvol, s_vol;
	long CalcLocalVolFlag = 0; // ���ú��� ���߿����
	long N_Rf;
	double* RfTerm;
	double* RfRate;
	long N_Div;
	double* DivTerm;
	double* DivRate;
	long NParityforSABR;
	double* ParityforSABR;
	long NTermforSABR;
	double* TermforSABR;
	double* VolforSABR;
	double SABRBeta;
	s_rf = 0;
	s_div = 0;
	s_parity = 0;
	s_termvol = 0;
	s_vol = 0;
	double* ResultSABRParams = ResultPrice + NStock * 3 + 1;
	for (i = 0; i < NStock; i++)
	{
		N_Rf = N_Rf_Curve[i];
		RfTerm = Term_Rf_Curve + s_rf;
		RfRate = Rate_Rf_Curve + s_rf;
		N_Div = 0;
		if (DivFlag[i] != 2)
		{
			N_Div = NDivTerm[i];
			DivTerm = TermDiv + s_div;
			DivRate = Div + s_div;
		}
		else
		{
			N_Div = 0;
			DivTerm = NULL;
			DivRate = NULL;
		}
		NTermforSABR = NTermVol[i];
		TermforSABR = TermVol + s_termvol;
		NParityforSABR = NParityVol[i];
		ParityforSABR = ParityVol + s_parity;
		VolforSABR = Vol + s_vol;

		if (ImVolLocalVolFlag[i] == 2) SABRBeta = 1.0;
		else SABRBeta = 0.5;

		if (ImVolLocalVolFlag[i] == 2 || ImVolLocalVolFlag[i] == 3)
		{
			double* ResultParams = (double*)calloc(NTermforSABR * 4, sizeof(double));
			double* Futures = (double*)malloc(sizeof(double) * NTermforSABR);
			double* TempVol = (double*)malloc(sizeof(double) * NTermforSABR * NParityforSABR);
			if (NParityVol[i] >= 4 && NTermVol[i] >= 4)
			{
				ImVolLocalVolFlag[i] = 0;
				//////////////////////
				// SABR Calibration //
				//////////////////////
				ResultCode = SABR_Vol(N_Rf, RfTerm, RfRate, N_Div, DivTerm,
					DivRate, NTermforSABR, TermforSABR, NParityforSABR, ParityforSABR,
					VolforSABR, CalcLocalVolFlag, SABRBeta, VolforSABR, TempVol,
					ResultParams, Futures, RMSPE + i);
				for (j = 0; j < NTermforSABR * 3; j++) ResultSABRParams[j] = ResultParams[j];
			}
			free(ResultParams);
			free(Futures);
			free(TempVol);
		}
		s_rf += N_Rf_Curve[i];
		s_div += NDivTerm[i];
		s_parity += NParityVol[i];
		s_termvol += NTermVol[i];
		s_vol += NParityVol[i] * NTermVol[i];
		ResultSABRParams += NTermforSABR * 3;
	}



	/////////////
	// ��¥ �� Ctype���� �ٲٱ�
	/////////////

	long PricingDate_Ctype;
	if (PricingDate < 19000101) PricingDate_Ctype = ExcelDateToCDate(PricingDate);
	else PricingDate_Ctype = PricingDate;

	long* EvalDate_Ctype = (long*)malloc(sizeof(long) * max(NEvaluate, 1));			// 4
	long* PayDate_Ctype = (long*)malloc(sizeof(long) * max(NEvaluate, 1));			// 5
	for (i = 0; i < NEvaluate; i++)
	{
		if (EvalDate[i] < 19000101) EvalDate_Ctype[i] = ExcelDateToCDate(EvalDate[i]);
		else EvalDate_Ctype[i] = EvalDate[i];

		if (PayDate[i] < 19000101) PayDate_Ctype[i] = ExcelDateToCDate(PayDate[i]);
		else PayDate_Ctype[i] = PayDate[i];
	}

	long* LizardStartDate_Ctype = (long*)malloc(sizeof(double) * max(NLizard, 1));	// 6
	long* LizardEndDate_Ctype = (long*)malloc(sizeof(double) * max(NLizard, 1));	// 7
	for (i = 0; i < NLizard; i++)
	{
		if (LizardStartDate[i] < 19000101) LizardStartDate_Ctype[i] = ExcelDateToCDate(LizardStartDate[i]);
		else LizardStartDate_Ctype[i] = LizardStartDate[i];

		if (LizardEndDate[i] < 19000101) LizardEndDate_Ctype[i] = ExcelDateToCDate(LizardEndDate[i]);
		else LizardEndDate_Ctype[i] = LizardEndDate[i];
	}

	long* CPN_EvaluateDate_Ctype = (long*)malloc(sizeof(double) * max(NCPN, 1));	// 8
	long* CPN_PayDate_Ctype = (long*)malloc(sizeof(double) * max(NCPN, 1));			// 9
	for (i = 0; i < NCPN; i++)
	{
		if (CPN_EvaluateDate[i] < 19000101) CPN_EvaluateDate_Ctype[i] = ExcelDateToCDate(CPN_EvaluateDate[i]);
		else CPN_EvaluateDate_Ctype[i] = CPN_EvaluateDate[i];

		if (CPN_PayDate[i] < 19000101) CPN_PayDate_Ctype[i] = ExcelDateToCDate(CPN_PayDate[i]);
		else CPN_PayDate_Ctype[i] = CPN_PayDate[i];
	}

	k = 0;
	for (i = 0; i < NStock; i++) k += NParityVol[i];
	double* ParityVol_Adj = (double*)malloc(sizeof(double) * k);					// 10

	k = 0;
	for (i = 0; i < NStock; i++)
	{
		for (j = 0; j < NParityVol[i]; j++)
		{
			ParityVol_Adj[k + j] = ParityVol[k + j] * S[i] / X[i];
		}
		k += NParityVol[i];
	}

	long MaxSimulDays = DayCountAtoB(PricingDate_Ctype, PayDate_Ctype[NEvaluate - 1]) + 1;
	double*** FixedRandn = (double***)malloc(sizeof(double**) * NSimul);			// 11
	randnorm(0);
	if (GreekFlag != 0)
	{
		for (i = 0; i < NSimul; i++)
		{
			FixedRandn[i] = (double**)malloc(sizeof(double*) * MaxSimulDays);
			for (j = 0; j < MaxSimulDays; j++)
			{
				FixedRandn[i][j] = (double*)malloc(sizeof(double) * NStock);
				for (k = 0; k < NStock; k++)
				{
					FixedRandn[i][j][k] = randnorm();
				}
			}
		}
	}

	/////////////////////////////////////////
	// ���� ����� ���� �̸� �Ҵ��� �迭�� //
	/////////////////////////////////////////
	double* path_price = (double*)calloc(NSimul, sizeof(double));
	double** daily_forward_rate = (double**)malloc(sizeof(double*) * NStock);
	double** daily_forward_div = (double**)malloc(sizeof(double*) * NStock);
	double** daily_forward_fxvol = (double**)malloc(sizeof(double*) * NStock);
	for (i = 0; i < NStock; i++)
	{
		daily_forward_rate[i] = (double*)malloc(sizeof(double) * MaxSimulDays);
		daily_forward_div[i] = (double*)malloc(sizeof(double) * MaxSimulDays);
		daily_forward_fxvol[i] = (double*)malloc(sizeof(double) * MaxSimulDays);
	}

	/////////////
	// ��ó�� �Լ��� �Ѿ��
	/////////////

	ResultCode = Preprocessing_HiFive_MC_Excel(PricingDate_Ctype, NSimul, 0, FaceValue, FaceValueFlag,
		MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
		KI_Method, EvalDate_Ctype, PayDate_Ctype, NStrike, Strike,
		AutocallSlope, AutocallCPN, NLizard, LizardFlag, LizardStartDate_Ctype,
		LizardEndDate_Ctype, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
		CPN_EvaluateDate_Ctype, CPN_PayDate_Ctype, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
		NStock, S, X, Base_S, Base_S_CPN,
		CorrelationReshaped, N_DF_Curve, Term_DF_Curve, Rate_DF_Curve, N_Rf_Curve,
		Term_Rf_Curve, Rate_Rf_Curve, NDivTerm, DivFlag, TermDiv,
		Div, QuantoFlag, QuantoCorr, NTermQuanto, TermQuanto,
		VolQuanto, ImVolLocalVolFlag, NParityVol, ParityVol_Adj, NTermVol,
		TermVol, Vol, ResultPrice, path_price, daily_forward_rate,
		daily_forward_div, daily_forward_fxvol, AutocallProb, CPNProb, ResultLocalVol,
		ParityVol, FixedRandn);

	long* nvolsum = (long*)malloc(sizeof(long) * (NStock + 1));										// 12
	nvolsum[0] = 0;
	for (i = 1; i < NStock + 1; i++) nvolsum[i] = nvolsum[i - 1] + NParityVol[i - 1] * NTermVol[i - 1];

	double* ResultPriceTemp = (double*)malloc(sizeof(double) * (1 + NStock * 3));					// 13
	double* AutocallProbTemp = (double*)malloc(sizeof(double) * 2 * (NEvaluate + 2 + NLizard));		// 14
	double* CPNProbTemp = (double*)malloc(sizeof(double) * max(1, NCPN * 2));						// 15
	double* ResultLocalVolTemp = (double*)malloc(sizeof(double) * nvolsum[NStock]);					// 16

	if (GreekFlag > 0)
	{
		double* Su = (double*)malloc(sizeof(double) * NStock);
		double* Sd = (double*)malloc(sizeof(double) * NStock);
		double Del, Gam, Pu, Pd, P;
		ResultCode = Preprocessing_HiFive_MC_Excel(PricingDate_Ctype, NSimul, GreekFlag, FaceValue, FaceValueFlag,
			MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
			KI_Method, EvalDate_Ctype, PayDate_Ctype, NStrike, Strike,
			AutocallSlope, AutocallCPN, NLizard, LizardFlag, LizardStartDate_Ctype,
			LizardEndDate_Ctype, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
			CPN_EvaluateDate_Ctype, CPN_PayDate_Ctype, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
			NStock, S, X, Base_S, Base_S_CPN,
			CorrelationReshaped, N_DF_Curve, Term_DF_Curve, Rate_DF_Curve, N_Rf_Curve,
			Term_Rf_Curve, Rate_Rf_Curve, NDivTerm, DivFlag, TermDiv,
			Div, QuantoFlag, QuantoCorr, NTermQuanto, TermQuanto,
			VolQuanto, ImVolLocalVolFlag, NParityVol, ParityVol_Adj, NTermVol,
			TermVol, Vol, ResultPriceTemp, path_price, daily_forward_rate,
			daily_forward_div, daily_forward_fxvol, AutocallProbTemp, CPNProbTemp, ResultLocalVolTemp,
			ParityVol, FixedRandn);
		P = ResultPriceTemp[0];

		for (i = 0; i < NStock; i++)
		{
			for (j = 0; j < NStock; j++)
			{
				if (j == i)
				{
					Su[j] = S[j] * 1.01;
					Sd[j] = S[j] * 0.99;
				}
				else
				{
					Su[j] = S[j];
					Sd[j] = S[j];
				}
			}
			ResultCode = Preprocessing_HiFive_MC_Excel(PricingDate_Ctype, NSimul, GreekFlag, FaceValue, FaceValueFlag,
				MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
				KI_Method, EvalDate_Ctype, PayDate_Ctype, NStrike, Strike,
				AutocallSlope, AutocallCPN, NLizard, LizardFlag, LizardStartDate_Ctype,
				LizardEndDate_Ctype, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
				CPN_EvaluateDate_Ctype, CPN_PayDate_Ctype, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
				NStock, Su, X, Base_S, Base_S_CPN,
				CorrelationReshaped, N_DF_Curve, Term_DF_Curve, Rate_DF_Curve, N_Rf_Curve,
				Term_Rf_Curve, Rate_Rf_Curve, NDivTerm, DivFlag, TermDiv,
				Div, QuantoFlag, QuantoCorr, NTermQuanto, TermQuanto,
				VolQuanto, ImVolLocalVolFlag, NParityVol, ParityVol_Adj, NTermVol,
				TermVol, Vol, ResultPriceTemp, path_price, daily_forward_rate,
				daily_forward_div, daily_forward_fxvol, AutocallProbTemp, CPNProbTemp, ResultLocalVolTemp,
				ParityVol, FixedRandn);
			Pu = ResultPriceTemp[0];

			ResultCode = Preprocessing_HiFive_MC_Excel(PricingDate_Ctype, NSimul, GreekFlag, FaceValue, FaceValueFlag,
				MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
				KI_Method, EvalDate_Ctype, PayDate_Ctype, NStrike, Strike,
				AutocallSlope, AutocallCPN, NLizard, LizardFlag, LizardStartDate_Ctype,
				LizardEndDate_Ctype, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
				CPN_EvaluateDate_Ctype, CPN_PayDate_Ctype, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
				NStock, Sd, X, Base_S, Base_S_CPN,
				CorrelationReshaped, N_DF_Curve, Term_DF_Curve, Rate_DF_Curve, N_Rf_Curve,
				Term_Rf_Curve, Rate_Rf_Curve, NDivTerm, DivFlag, TermDiv,
				Div, QuantoFlag, QuantoCorr, NTermQuanto, TermQuanto,
				VolQuanto, ImVolLocalVolFlag, NParityVol, ParityVol_Adj, NTermVol,
				TermVol, Vol, ResultPriceTemp, path_price, daily_forward_rate,
				daily_forward_div, daily_forward_fxvol, AutocallProbTemp, CPNProbTemp, ResultLocalVolTemp,
				ParityVol, FixedRandn);
			Pd = ResultPriceTemp[0];

			Del = (Pu - Pd) / (2.0 * 0.01 * S[i]);
			Gam = (Pu + Pd - 2.0 * P) / (S[i] * 0.01 * S[i] * 0.01);
			ResultPrice[i + 1] = Del;
			ResultPrice[NStock + i + 1] = Gam;

		}

		free(Su);
		free(Sd);

	}

	if (GreekFlag > 1)
	{
		double pu, pd;
		double Vega;

		double* voltempup = (double*)malloc(sizeof(double) * nvolsum[NStock]);
		double* voltempdn = (double*)malloc(sizeof(double) * nvolsum[NStock]);

		for (i = 0; i < NStock; i++)
		{
			for (k = 0; k < nvolsum[NStock]; k++)
			{
				voltempup[k] = Vol[k];
				voltempdn[k] = Vol[k];
			}

			for (j = 0; j < NStock; j++)
			{
				if (j == i)
				{
					for (k = nvolsum[i]; k < nvolsum[i + 1]; k++)
					{
						voltempup[k] = Vol[k] + 0.01;
						voltempdn[k] = Vol[k] - 0.01;
					}
				}
			}

			ResultCode = Preprocessing_HiFive_MC_Excel(PricingDate_Ctype, NSimul, GreekFlag, FaceValue, FaceValueFlag,
				MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
				KI_Method, EvalDate_Ctype, PayDate_Ctype, NStrike, Strike,
				AutocallSlope, AutocallCPN, NLizard, LizardFlag, LizardStartDate_Ctype,
				LizardEndDate_Ctype, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
				CPN_EvaluateDate_Ctype, CPN_PayDate_Ctype, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
				NStock, S, X, Base_S, Base_S_CPN,
				CorrelationReshaped, N_DF_Curve, Term_DF_Curve, Rate_DF_Curve, N_Rf_Curve,
				Term_Rf_Curve, Rate_Rf_Curve, NDivTerm, DivFlag, TermDiv,
				Div, QuantoFlag, QuantoCorr, NTermQuanto, TermQuanto,
				VolQuanto, ImVolLocalVolFlag, NParityVol, ParityVol_Adj, NTermVol,
				TermVol, voltempup, ResultPriceTemp, path_price, daily_forward_rate,
				daily_forward_div, daily_forward_fxvol, AutocallProbTemp, CPNProbTemp, ResultLocalVolTemp,
				ParityVol, FixedRandn);
			pu = ResultPriceTemp[0];

			ResultCode = Preprocessing_HiFive_MC_Excel(PricingDate_Ctype, NSimul, GreekFlag, FaceValue, FaceValueFlag,
				MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
				KI_Method, EvalDate_Ctype, PayDate_Ctype, NStrike, Strike,
				AutocallSlope, AutocallCPN, NLizard, LizardFlag, LizardStartDate_Ctype,
				LizardEndDate_Ctype, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
				CPN_EvaluateDate_Ctype, CPN_PayDate_Ctype, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
				NStock, S, X, Base_S, Base_S_CPN,
				CorrelationReshaped, N_DF_Curve, Term_DF_Curve, Rate_DF_Curve, N_Rf_Curve,
				Term_Rf_Curve, Rate_Rf_Curve, NDivTerm, DivFlag, TermDiv,
				Div, QuantoFlag, QuantoCorr, NTermQuanto, TermQuanto,
				VolQuanto, ImVolLocalVolFlag, NParityVol, ParityVol_Adj, NTermVol,
				TermVol, voltempdn, ResultPriceTemp, path_price, daily_forward_rate,
				daily_forward_div, daily_forward_fxvol, AutocallProbTemp, CPNProbTemp, ResultLocalVolTemp,
				ParityVol, FixedRandn);
			pd = ResultPriceTemp[0];
			Vega = (pu - pd) / 2.0 / 100.0;
			ResultPrice[2 * NStock + i + 1] = Vega;
		}

		free(voltempup);
		free(voltempdn);
	}

	free(Strike);
	free(AutocallSlope);
	free(AutocallCPN);
	free(EvalDate_Ctype);
	free(PayDate_Ctype);
	free(LizardStartDate_Ctype);
	free(LizardEndDate_Ctype);
	free(CPN_EvaluateDate_Ctype);
	free(CPN_PayDate_Ctype);
	free(ParityVol_Adj);

	free(nvolsum);
	free(ResultPriceTemp);
	free(AutocallProbTemp);
	free(CPNProbTemp);
	free(ResultLocalVolTemp);


	if (GreekFlag != 0)
	{
		for (i = 0; i < NSimul; i++)
		{
			for (j = 0; j < MaxSimulDays; j++)
			{
				free(FixedRandn[i][j]);
			}
			free(FixedRandn[i]);
		}
	}
	free(FixedRandn);
	free(path_price);
	for (i = 0; i < NStock; i++)
	{
		free(daily_forward_rate[i]);
		free(daily_forward_div[i]);
		free(daily_forward_fxvol[i]);
	}
	free(daily_forward_rate);
	free(daily_forward_div);
	free(daily_forward_fxvol);
#ifdef _DEBUG
	_CrtDumpMemoryLeaks();
#elif DEBUG
	_CrtDumpMemoryLeaks();
#endif

	return ResultCode;
}

double Preprocessing_HiFiVe_VaR(
	long RedempFlag,
	long LizardRedempFlag,
	double FaceValue,
	long FaceValueFlag,
	double MaxProfit,
	double MaxLoss,
	long NStock,
	double* S,
	double* X,
	long KI_Method,
	double KI_Barrier_Level,
	long Now_KI_State,
	long NEvaluate,
	long Evaluation_Idx,
	long* Days_Autocall_Eval,
	long* Days_Autocall_Pay,
	long nK,
	double** Strike,
	double** AutocallSlope,
	double** AutocallCPN,
	long NLizard,
	long* LizardFlag,
	long* Days_LizardStart,
	long* Days_LizardEnd,
	double* LizardBarrierLevel,
	double* LizardCoupon,
	long* Now_LizardHitting,
	long NCPN,
	long CPNIdx,
	long* Days_CPN_Eval,
	long* Days_CPN_Pay,
	double* CPN_Lower_Barrier,
	double* CPN_Upper_Barrier,
	double* CPN_Rate,
	long N_TermDisc,
	double* TermDisc,
	double* RateDisc,
	long* N_TermRf,
	double* TermRf,
	double* RateRf,
	long* NDivTerm,
	double* TermDiv,
	double* Div,
	long* NTermQuanto,
	double* TermQuanto,
	double* VolQuanto,
	long ImVolLocalVolFlag,
	long* NParityVol,
	double* ParityVol,
	long* NTermVol,
	double* TermVol,
	double* Vol,

	simulinfo& Info_Simul,
	long Simulation_Required,
	long NSimul,
	double* ResultPrice
)
{
	long i, j;

	HiFiveInfo info_hifive;

	info_hifive.FaceValue = FaceValue;
	info_hifive.FaceValueFlag = FaceValueFlag;
	info_hifive.NStock = NStock;

	info_hifive.MaxProfit = MaxProfit;
	info_hifive.MaxLoss = MaxLoss;

	// KI ���� ����
	info_hifive.KI_Method = KI_Method;
	info_hifive.KI_Barrier_Level = KI_Barrier_Level;
	info_hifive.Now_KI_State = Now_KI_State;

	// Autocall ���� ����
	info_hifive.NEvaluation = NEvaluate - Evaluation_Idx;
	info_hifive.Days_Autocall_Eval = Days_Autocall_Eval + Evaluation_Idx;
	info_hifive.Days_Autocall_Pay = Days_Autocall_Pay + Evaluation_Idx;

	double** AdjStrike = (double**)malloc(sizeof(double*) * nK);			// �Ҵ�1
	double** AdjSlope = (double**)malloc(sizeof(double*) * nK);				// �Ҵ�2
	double** AdjFixedAmount = (double**)malloc(sizeof(double*) * nK);		// �Ҵ�3

	for (i = 0; i < nK; i++)
	{
		AdjStrike[i] = Strike[i] + Evaluation_Idx;
		AdjSlope[i] = AutocallSlope[i] + Evaluation_Idx;
		AdjFixedAmount[i] = AutocallCPN[i] + Evaluation_Idx;
	}

	info_hifive.Strike = AdjStrike;
	info_hifive.Slope = AdjSlope;
	info_hifive.FixedAmount = AdjFixedAmount;
	info_hifive.nK = nK;


	// Lizard ���� ����
	info_hifive.NLizard = max(0, NLizard - Evaluation_Idx);
	info_hifive.LizardFlag = LizardFlag + Evaluation_Idx;
	info_hifive.Days_LizardStart = Days_LizardStart + Evaluation_Idx;
	info_hifive.Days_LizardEnd = Days_LizardEnd + Evaluation_Idx;
	info_hifive.Lizard_Barrier_Level = LizardBarrierLevel + Evaluation_Idx;
	info_hifive.Lizard_Coupon = LizardCoupon + Evaluation_Idx;
	info_hifive.Now_Lizard_KI_State = Now_LizardHitting + Evaluation_Idx;


	info_hifive.NCPN = NCPN - CPNIdx;
	info_hifive.Days_CPN_Eval = Days_CPN_Eval + CPNIdx;
	info_hifive.Days_CPN_Pay = Days_CPN_Pay + CPNIdx;
	info_hifive.CPN_Lower_Barrier = CPN_Lower_Barrier + CPNIdx;
	info_hifive.CPN_Upper_Barrier = CPN_Upper_Barrier + CPNIdx;
	info_hifive.CPN_Rate = CPN_Rate + CPNIdx;

	curveinfo disc_curve(N_TermDisc, TermDisc, RateDisc);   // Discount Curve Setting		

	curveinfo* rf_curves = (curveinfo*)malloc(sizeof(curveinfo) * NStock);//new curveinfo[NStock];           // RiskFree Curve Setting
	curveinfo* div_curves = (curveinfo*)malloc(sizeof(curveinfo) * NStock);// new curveinfo[NStock];          // Dividend Setting
	curveinfo* quanto_curves = (curveinfo*)malloc(sizeof(curveinfo) * NStock);// new curveinfo[NStock];       // Quanto Setting 

	long nterm_rf = 0;
	long nterm_div = 0;
	long nterm_quanto = 0;
	for (i = 0; i < NStock; i++)
	{
		(rf_curves + i)->initialize(N_TermRf[i], TermRf + nterm_rf, RateRf + nterm_rf);
		nterm_rf += N_TermRf[i];

		(div_curves + i)->initialize(NDivTerm[i], TermDiv + nterm_div, Div + nterm_div);
		nterm_div += NDivTerm[i];

		(quanto_curves + i)->initialize(NTermQuanto[i], TermQuanto + nterm_quanto, VolQuanto + nterm_quanto);
		nterm_quanto += NTermQuanto[i];
	}

	//////////////////////////
	// Imvol, LocalVol Setting
	//////////////////////////

	volinfo* VolMatrixList = (volinfo*)malloc(sizeof(volinfo) * NStock); // new volinfo[NStock];

	long nterm_vol = 0;
	long nparity = 0;
	long nvol = 0;
	long n = 0;
	for (i = 0; i < NStock; i++)
	{
		(VolMatrixList + i)->hardcopy(NParityVol[i], ParityVol + nparity, NTermVol[i], TermVol + nterm_vol, Vol + nvol);
		nparity += NParityVol[i];
		nterm_vol += NTermVol[i];
		nvol += NParityVol[i] * NTermVol[i];
		if (ImVolLocalVolFlag == 0)
			(VolMatrixList + i)->set_localvol((rf_curves + i), (div_curves + i), 2.0, 0.001);
		else
		{
			(VolMatrixList + i)->LocalVolMat = (VolMatrixList + i)->Vol_Matrix;
			(VolMatrixList + i)->Parity_Locvol = (VolMatrixList + i)->Parity;
			(VolMatrixList + i)->Term_Locvol = (VolMatrixList + i)->Term;
		}

		// �з�Ƽ ���� St/S0 �� 1�� �ƴ� ���
		if (S[i] / X[i] != 1.0)
		{
			for (j = 0; j < NParityVol[i]; j++)
			{
				(VolMatrixList + i)->Parity_Locvol[j] = (VolMatrixList + i)->Parity_Locvol[j] * S[i] / X[i];
			}
		}
	}

	double* CF = (double*)calloc((NEvaluate + 2 + NLizard), sizeof(double));			// �Ҵ�4


	long pricingonly = 2;
	double price;
	double* AutocallProb = make_array(NEvaluate + 2);
	double* CPNProb = make_array(NEvaluate + 2);
	// �ùķ��̼��� �ʿ� ���� ���
	if (RedempFlag > 0 || LizardRedempFlag > 0)
	{
		price = ResultPrice[0];
	}
	else
	{
		price = Pricing_HiFive_MC(Info_Simul, info_hifive, disc_curve, rf_curves, div_curves,
			quanto_curves, VolMatrixList, ResultPrice, pricingonly, AutocallProb + Evaluation_Idx, CF + Evaluation_Idx, CPNProb);
	}

	if (rf_curves) free(rf_curves);
	if (div_curves) free(div_curves);
	if (quanto_curves) free(quanto_curves);
	if (VolMatrixList) free(VolMatrixList);

	free(AdjStrike);				// 1
	free(AdjSlope);					// 2
	free(AdjFixedAmount);			// 3
	free(CF);						// 4
	free(AutocallProb);				// 5
	free(CPNProb);					// 6
	return price;
}

long ErrorCheck_Excel_HiFive_VaR(
	long PricingDate_Excel,			// ���ݰ�곯¥ ExcelType Ex) 44201(2021��01��05��)
	long NSimul,					// �ùķ��̼ǰ���
	long NHistory,					// ������ History ����
	double FaceValue,				// ���ݾ�
	long FaceValueFlag,				// ���ݼ�������

	double MaxProfit,				// �ִ�����
	double MaxLoss,					// �ִ�ս�
	long NEvaluate,					// �����ȯ ���ϰ���
	double KI_Barrier_Level,		// ���ι踮�����
	long Now_KI_State,				// ���� ���λ���

	long KI_Method,					// ����ó�����
	long* EvalDate_Excel,			// �����ȯ ExcelType���� Array [ Shape = (NEvaluate , ) ]
	long* PayDate_Excel,			// �����ȯ ExcelType������ Array [ Shape = (NEvaluate , ) ]
	long* NStrike,					// �����ȯ ȸ���� ��簡�ݰ��� Array [ Shape = (NEvaluate , ) ]
	double* StrikeLevel,			// �����ȯ ȸ���� ��簡�� Array [ Shape = reshape(3 * NEvaluate) ]

	double* Slope,					// �����ȯ ȸ���� ������ [ Shape = reshape(3 * NEvaluate)  ]
	double* FixedAmount,			// �����ȯ ȸ���� ���� [ Shape = reshape(3 * NEvaluate)  ]
	long NLizard,					// ���ڵ��ȯ ���� ����
	long* LizardFlag,				// �����ȯ ȸ���� ���ڵ��ȯ ������ ���� Array [ Shape = (NLizard , ) ]
	long* LizardStartDate_Excel,	// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]

	long* LizardEndDate_Excel,		// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]
	double* LizardBarrierLevel,		// �����ȯ ȸ���� ���ڵ�踮�� �踮��� Array
	long* Now_LizardHitting,		// �����ȯ ȸ���� ���ڵ�踮�� ���� Hitting���� Array
	double* LizardCoupon,			// �����ȯ ȸ���� ���ڵ�踮�� ���������� Array
	long NCPN,						// �Ϲ� ���� ���� ����

	long* CPN_EvaluateDate_Excel,	// �Ϲ� ���� ���� ExcelType Array [ Shape = (NCPN , ) ]
	long* CPN_PayDate_Excel,		// �Ϲ� ���� ������ ExcelType Array [ Shape = (NCPN , ) ]
	double* CPN_Lower_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Upper_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Rate,				// �Ϲ� ���� ���������� Array [ Shape = (NCPN , ) ]

	long NStock,					// �����ڻ갳��
	double* S0,						// �����ڻ� Shape = NHistory * NStock
	double* X,						// ���ذ���,�ֱ����ϰ���, �ֱ��������ϰ���
	double* CorrelReshaped,
	long* NRf,
	double* TermRf,
	double* RateRf,

	long VolFlag,
	long* NParity,
	long* NTermVol,
	long* NVol,
	double* Parity,
	double* TermVol,
	double* Vol,

	long* DivFlag,
	long* NDiv,
	double* DivTerm,
	double* DivRate,

	long* QuantoFlag,
	double* QuantoCorr,

	long* NFXVol,
	double* FXVolTerm,
	double* FXVolRate,

	long VaRMethod,

	double* PriceHistory,
	double* VaRInfo,
	char* Error
)
{
	long i, j, k, n, l;

	char ErrorName[100];


	if (PricingDate_Excel < 0)
	{
		strcpy_s(ErrorName, "PricingDate is too early");
		return SaveErrorName(Error, ErrorName);
	}


	if (PricingDate_Excel > max(PayDate_Excel[NEvaluate - 1], CPN_PayDate_Excel[NCPN - 1]))
	{
		strcpy_s(ErrorName, "PricingDate is too late");
		return SaveErrorName(Error, ErrorName);
	}

	if (NSimul <= 0)
	{
		strcpy_s(ErrorName, "NSimul must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	if (NHistory < 0)
	{
		strcpy_s(ErrorName, "NHistory must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	if (FaceValue < 0.0)
	{
		strcpy_s(ErrorName, "FaceValue must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	if (FaceValueFlag < 0)
	{
		strcpy_s(ErrorName, "FaceValueFlag must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	if (NEvaluate == 0)
	{
		strcpy_s(ErrorName, "Autocall Evaluation Number is 0");
		return SaveErrorName(Error, ErrorName);
	}

	for (i = 0; i < NEvaluate - 1; i++)
	{
		if (EvalDate_Excel[i + 1] < EvalDate_Excel[i])
		{
			strcpy_s(ErrorName, "Check Autocall Evaluation Date");
			return SaveErrorName(Error, ErrorName);
		}
	}

	for (i = 0; i < NEvaluate; i++)
	{
		if (EvalDate_Excel[i] > PayDate_Excel[i])
		{
			strcpy_s(ErrorName, "Autocall Evaluation Date is later than PayDate");
			return SaveErrorName(Error, ErrorName);
		}
	}

	for (i = 0; i < NLizard; i++)
	{
		if (min(LizardStartDate_Excel[i], LizardEndDate_Excel[i]) <= 0)
		{
			strcpy_s(ErrorName, "LizardDate must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
	}

	for (i = 0; i < NCPN; i++)
	{
		if (min(CPN_EvaluateDate_Excel[i], CPN_PayDate_Excel[i]) <= 0)
		{
			strcpy_s(ErrorName, "CPNDate must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
	}

	if (NStock < 1)
	{
		strcpy_s(ErrorName, "NStock must be Positive");
		return SaveErrorName(Error, ErrorName);
	}

	k = 0;
	for (i = 0; i < NHistory; i++)
	{
		for (j = 0; j < NStock; j++)
		{
			if (S0[k] <= 0.0)
			{
				strcpy_s(ErrorName, "Stock Price must be Positive");
				return SaveErrorName(Error, ErrorName);
			}
			k += 1;
		}
	}

	for (i = 0; i < NStock * 3; i++)
	{
		if (X[i] <= 0.0)
		{
			strcpy_s(ErrorName, "Stock Price must be Positive");
			return SaveErrorName(Error, ErrorName);
		}
	}

	k = 0;
	for (n = 0; n < NHistory; n++)
	{
		for (i = 0; i < NStock; i++)
		{
			for (j = 0; j < NStock; j++)
			{
				if (i == j)
				{
					if (CorrelReshaped[k] > 1.001 || CorrelReshaped[k] < 0.999)
					{
						strcpy_s(ErrorName, "Diagonal must be One");
						return SaveErrorName(Error, ErrorName);
					}
				}
				k += 1;
			}
		}
	}

	k = 0;
	l = 0;
	for (n = 0; n < NHistory; n++)
	{
		for (j = 0; j < NStock + 1; j++)
		{
			if (NRf[k] <= 0)
			{
				strcpy_s(ErrorName, "NRf must be Positive");
				return SaveErrorName(Error, ErrorName);
			}
			for (i = 0; i < NRf[k]; i++)
			{
				if (i > 0)
				{
					if (TermRf[l] < TermRf[l - 1])
					{
						strcpy_s(ErrorName, "Sort Risk Free Term");
						return SaveErrorName(Error, ErrorName);
					}
				}
				l += 1;
			}
			k += 1;
		}
	}

	k = 0;
	l = 0;
	long idx_vol = 0;
	long idx_parity = 0;
	long idx_term = 0;
	double* parityary;
	double* termary;
	double* volary;
	for (n = 0; n < NHistory; n++)
	{
		for (j = 0; j < NStock; j++)
		{
			parityary = Parity + idx_parity;
			termary = TermVol + idx_term;
			if (NParity[k] <= 0)
			{
				strcpy_s(ErrorName, "NParity must be Positive");
				return SaveErrorName(Error, ErrorName);
			}
			for (i = 0; i < NParity[k]; i++)
			{
				if (i > 0)
				{
					if (parityary[i] < parityary[i - 1])
					{
						strcpy_s(ErrorName, "Sort Parity");
						return SaveErrorName(Error, ErrorName);
					}
				}
			}
			if (NTermVol[k] <= 0)
			{
				strcpy_s(ErrorName, "NTerm must be Positive");
				return SaveErrorName(Error, ErrorName);
			}
			for (i = 0; i < NTermVol[k]; i++)
			{
				if (i > 0)
				{
					if (termary[i] < termary[i - 1])
					{
						strcpy_s(ErrorName, "Sort TermVol");
						return SaveErrorName(Error, ErrorName);
					}
				}
			}

			volary = Vol + idx_vol;
			for (i = 0; i < NVol[k]; i++)
			{
				if (volary[i] <= 0.0)
				{
					strcpy_s(ErrorName, "Vol must be Positive");
					return SaveErrorName(Error, ErrorName);
				}
			}
			idx_term += NTermVol[k];
			idx_parity += NParity[k];
			idx_vol += NVol[k];
			k += 1;
		}
	}

	k = 0;
	l = 0;
	for (n = 0; n < NHistory; n++)
	{
		for (j = 0; j < NStock; j++)
		{
			if (NDiv[k] <= 0)
			{
				strcpy_s(ErrorName, "NDiv must be Positive");
				return SaveErrorName(Error, ErrorName);
			}
			for (i = 0; i < NDiv[k]; i++)
			{
				if (i > 0)
				{
					if (DivTerm[l] < DivTerm[l - 1])
					{
						strcpy_s(ErrorName, "Sort Div Term");
						return SaveErrorName(Error, ErrorName);
					}
				}
				l += 1;
			}
			k += 1;
		}
	}

	k = 0;
	l = 0;
	for (n = 0; n < NHistory; n++)
	{
		for (j = 0; j < NStock; j++)
		{
			if (NFXVol[k] <= 0)
			{
				strcpy_s(ErrorName, "NFXVol must be Positive");
				return SaveErrorName(Error, ErrorName);
			}
			for (i = 0; i < NFXVol[k]; i++)
			{
				if (i > 0)
				{
					if (FXVolTerm[l] < FXVolTerm[l - 1])
					{
						strcpy_s(ErrorName, "Sort FXVol Term");
						return SaveErrorName(Error, ErrorName);
					}
				}
				l += 1;
			}
			k += 1;
		}
	}


	return 1;
}

long HiFive_VaR_Excel(
	long PricingDate_Excel,			// ���ݰ�곯¥ ExcelType Ex) 44201(2021��01��05��)
	long NSimul,					// �ùķ��̼ǰ���
	long NHistory,					// ������ History ����
	double FaceValue,				// ���ݾ�
	long FaceValueFlag,				// ���ݼ�������

	double MaxProfit,				// �ִ�����
	double MaxLoss,					// �ִ�ս�
	long NEvaluate,					// �����ȯ ���ϰ���
	double KI_Barrier_Level,		// ���ι踮�����
	long Now_KI_State,				// ���� ���λ���

	long KI_Method,					// ����ó�����
	long* EvalDate_Excel,			// �����ȯ ExcelType���� Array [ Shape = (NEvaluate , ) ]
	long* PayDate_Excel,			// �����ȯ ExcelType������ Array [ Shape = (NEvaluate , ) ]
	long* NStrike,					// �����ȯ ȸ���� ��簡�ݰ��� Array [ Shape = (NEvaluate , ) ]
	double* StrikeLevel,			// �����ȯ ȸ���� ��簡�� Array [ Shape = reshape(3 * NEvaluate) ]

	double* Slope,					// �����ȯ ȸ���� ������ [ Shape = reshape(3 * NEvaluate)  ]
	double* FixedAmount,			// �����ȯ ȸ���� ���� [ Shape = reshape(3 * NEvaluate)  ]
	long NLizard,					// ���ڵ��ȯ ���� ����
	long* LizardFlag,				// �����ȯ ȸ���� ���ڵ��ȯ ������ ���� Array [ Shape = (NLizard , ) ]
	long* LizardStartDate_Excel,	// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]

	long* LizardEndDate_Excel,		// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]
	double* LizardBarrierLevel,		// �����ȯ ȸ���� ���ڵ�踮�� �踮��� Array
	long* Now_LizardHitting,		// �����ȯ ȸ���� ���ڵ�踮�� ���� Hitting���� Array
	double* LizardCoupon,			// �����ȯ ȸ���� ���ڵ�踮�� ���������� Array
	long NCPN,						// �Ϲ� ���� ���� ����

	long* CPN_EvaluateDate_Excel,	// �Ϲ� ���� ���� ExcelType Array [ Shape = (NCPN , ) ]
	long* CPN_PayDate_Excel,		// �Ϲ� ���� ������ ExcelType Array [ Shape = (NCPN , ) ]
	double* CPN_Lower_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Upper_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Rate,				// �Ϲ� ���� ���������� Array [ Shape = (NCPN , ) ]

	long NStock,					// �����ڻ갳��
	double* S0,						// �����ڻ� Shape = NHistory * NStock
	double* X,						// ���ذ���,�ֱ����ϰ���, �ֱ��������ϰ���
	double* CorrelReshaped,			// �̰���� History .Reshaped(-1) Shape = NHistory * (NStock * NStock)
	long* NRf,						// ���αݸ�, �� �����ڻ� ������ݸ� ���� Shape = NHistory * (NStock + 1)
	double* TermRf,					// ���αݸ�, �� �����ڻ� ������ݸ� Term Shape = sumation(NRf)
	double* RateRf,					// ���αݸ�, �� �����ڻ� ������ݸ� Rate Shape = sumation(NRf)

	long VolFlag,					// VolFlag 0: Imvol->Dupire LocalVol ������ 1: ���� ���ú� ���
	long* NParity,					// ������ �з�Ƽ ���� Shape = NHistory * NStock
	long* NTermVol,					// ������ Term ���� Shape = Nhistory * NStock
	long* NVol,						// ������ ���� Shape = NHistory * NStock
	double* Parity,					// �� �����ڻ꺰 Parity Array Shape = sumation(NParity)
	double* TermVol,				// �� �����ڻ꺰 Vol Term Array Shape = sumation(NTermVol)
	double* Vol,					// �� �����ڻ꺰 Vol History Array Shape = sumation(NVol)

	long* DivFlag,					// ��� ���� Flag 0:Flag, 1: Curve, 2:�̻���
	long* NDiv,						// ��簳�� Shape = NHistory * NStock
	double* DivTerm,				// ��� Term Shape = sumation(NDiv)
	double* DivRate,				// ��� Rate Shape = sumation(NDiv)

	long* QuantoFlag,				// Quanto ��뿩�� Shape = NSTock
	double* QuantoCorr,				// Quanto Corr History Array Shape = NHistory * NStock

	long* NFXVol,					// FXVol ���� History Shape = NHistory * NStock
	double* FXVolTerm,				// FXVolTerm �����丮 Shape = sumation(NFXVol)
	double* FXVolRate,				// FXVol �����丮 Shape = sumation(NFXVol)

	long VaRMethod,					// 0: Historical VaR, 1: MonteCarlo VaR

	double* PriceHistory,			// Output ���ݰ���� : Shape = NHistory
	double* VaRInfo,				// OutPut : 0~2 1d VaR 3~5 10d VaR 6~8 250d VaR
	char* Error						// OutPut �����޽���
)
{
	long i, j, k, l;

	if (VaRMethod == 1)
	{
		long np, nt;
		double*** VolMatrix_MC = (double***)malloc(sizeof(double**) * NStock);
		double** Parity_MC = (double**)malloc(sizeof(double*) * NStock);
		double** TermVol_MC = (double**)malloc(sizeof(double*) * NStock);
		double t = 0.0, sigma;
		l = 0;
		np = 0;
		nt = 0;
		for (i = 0; i < NStock; i++)
		{
			Parity_MC[i] = Parity + np;
			TermVol_MC[i] = TermVol + nt;
			VolMatrix_MC[i] = make_array(NParity[i], NTermVol[i]);
			for (j = 0; j < NParity[i]; j++)
			{
				for (k = 0; k < NTermVol[i]; k++)
				{
					VolMatrix_MC[i][j][k] = Vol[l];
					l += 1;
				}
			}
			np += NParity[i];
			nt += NTermVol[i];
		}

		k = 0;
		randnorm(0);
		for (i = 0; i < NHistory; i++)
		{
			t = (double)i * 1.0 / 365.0;
			for (j = 0; j < NStock; j++)
			{
				if (i > 0)
				{
					sigma = Calc_Volatility(NTermVol[j], NParity[j], TermVol_MC[j], Parity_MC[j], VolMatrix_MC[j], t, 1.0);
					S0[k] = S0[k - NStock] * (1.0 + sigma * sqrt(1.0 / 365.0) * randnorm());
				}
				k += 1;
			}
		}

		free(Parity_MC);
		free(TermVol_MC);
		for (i = 0; i < NStock; i++)
		{
			for (j = 0; j < NParity[i]; j++)
			{
				free(VolMatrix_MC[i][j]);
			}
			free(VolMatrix_MC[i]);
		}
		free(VolMatrix_MC);
	}

	long nK = 3;
	double** Strike = (double**)malloc(sizeof(double*) * nK);						// 1
	double** AutocallSlope = (double**)malloc(sizeof(double*) * nK);				// 2
	double** AutocallCPN = (double**)malloc(sizeof(double*) * nK);					// 3
	for (i = 0; i < nK; i++)
	{
		Strike[i] = StrikeLevel + NEvaluate * i;
		AutocallSlope[i] = Slope + (NEvaluate + 2) * i;
		AutocallCPN[i] = FixedAmount + (NEvaluate + 2) * i;
	}

	double** S0_ForSimul = (double**)malloc(sizeof(double*) * NHistory);				// 4
	for (i = 0; i < NHistory; i++)
	{
		S0_ForSimul[i] = S0 + i * NStock;
	}
	double* X_ForSimul = X;
	double* Base_S_ForSimul = X + 1 * NStock;
	double* Base_S_CPN_ForSimul = X + 2 * NStock;
	double** CorrelReshaped_Simul = (double**)malloc(sizeof(double*) * NHistory);	// 5 
	for (i = 0; i < NHistory; i++)
	{
		CorrelReshaped_Simul[i] = CorrelReshaped + NStock * NStock * i;
	}
	long* N_DF_Curve = (long*)malloc(sizeof(long) * NHistory);						// 6
	long** N_Rf_Curve = (long**)malloc(sizeof(long*) * NHistory);					// 7
	double** Term_DF_Curve = (double**)malloc(sizeof(double*) * NHistory);			// 8
	double** Term_Rf_Curve = (double**)malloc(sizeof(double*) * NHistory);			// 9
	double** Rate_DF_Curve = (double**)malloc(sizeof(double*) * NHistory);			// 10
	double** Rate_Rf_Curve = (double**)malloc(sizeof(double*) * NHistory);			// 11
	long total_ncurve = 0;
	for (i = 0; i < NHistory; i++)
	{
		N_DF_Curve[i] = NRf[i * (NStock + 1)];
		N_Rf_Curve[i] = NRf + i * (NStock + 1) + 1;
		Term_DF_Curve[i] = TermRf + total_ncurve;
		Term_Rf_Curve[i] = TermRf + total_ncurve + N_DF_Curve[i];
		Rate_DF_Curve[i] = RateRf + total_ncurve;
		Rate_Rf_Curve[i] = RateRf + total_ncurve + N_DF_Curve[i];
		total_ncurve = total_ncurve + N_DF_Curve[i] + sumation(NStock, N_Rf_Curve[i]);
	}

	long** NParity_Simul = (long**)malloc(sizeof(long*) * NHistory);				// 12
	long** NTermVol_Simul = (long**)malloc(sizeof(long*) * NHistory);				// 13
	double** Parity_Simul = (double**)malloc(sizeof(double*) * NHistory);			// 14
	double** TermVol_Simul = (double**)malloc(sizeof(double*) * NHistory);			// 15
	double** Vol_Simul = (double**)malloc(sizeof(double*) * NHistory);				// 16
	long total_nparity = 0;
	long total_ntermvol = 0;
	long total_nvol = 0;
	k = 0;
	for (i = 0; i < NHistory; i++)
	{
		NParity_Simul[i] = NParity + i * NStock;
		NTermVol_Simul[i] = NTermVol + i * NStock;
		Parity_Simul[i] = Parity + total_nparity;
		TermVol_Simul[i] = TermVol + total_ntermvol;
		Vol_Simul[i] = Vol + total_nvol;
		for (j = 0; j < NStock; j++)
		{
			total_nparity += NParity[k];
			total_ntermvol += NTermVol[k];
			total_nvol += NVol[k];
			k += 1;
		}
	}

	long** NDiv_Simul = (long**)malloc(sizeof(long*) * NHistory);					// 17
	double** DivTerm_Simul = (double**)malloc(sizeof(double*) * NHistory);			// 18
	double** DivRate_Simul = (double**)malloc(sizeof(double*) * NHistory);			// 19
	long total_ndiv = 0;
	k = 0;
	for (i = 0; i < NHistory; i++)
	{
		NDiv_Simul[i] = NDiv + i * NStock;
		DivTerm_Simul[i] = DivTerm + total_ndiv;
		DivRate_Simul[i] = DivRate + total_ndiv;
		for (j = 0; j < NStock; j++)
		{
			total_ndiv += NDiv[k];
			k += 1;
		}
	}

	double** QuantoCorr_Simul = (double**)malloc(sizeof(double*) * NHistory);		// 20

	k = 0;
	for (i = 0; i < NHistory; i++)
	{
		QuantoCorr_Simul[i] = QuantoCorr + i * NStock;
	}

	long** NFXVol_Simul = (long**)malloc(sizeof(long*) * NHistory);					// 21
	double** FXVolTerm_Simul = (double**)malloc(sizeof(double*) * NHistory);		// 22
	double** FXVolRate_Simul = (double**)malloc(sizeof(double*) * NHistory);		// 23
	long total_nFXVol = 0;
	k = 0;
	for (i = 0; i < NHistory; i++)
	{
		NFXVol_Simul[i] = NFXVol + i * NStock;
		FXVolTerm_Simul[i] = FXVolTerm + total_nFXVol;
		FXVolRate_Simul[i] = FXVolRate + total_nFXVol;
		for (j = 0; j < NStock; j++)
		{
			total_nFXVol += NFXVol[k];
			k += 1;
		}
	}

	/////////////
	// ��¥ �� Ctype���� �ٲٱ�
	/////////////

	long PricingDate_Ctype = ExcelDateToCDate(PricingDate_Excel);

	long* EvalDate_Ctype = (long*)malloc(sizeof(long) * max(NEvaluate, 1));			// 24
	long* PayDate_Ctype = (long*)malloc(sizeof(long) * max(NEvaluate, 1));			// 25
	for (i = 0; i < NEvaluate; i++)
	{
		EvalDate_Ctype[i] = ExcelDateToCDate(EvalDate_Excel[i]);
		PayDate_Ctype[i] = ExcelDateToCDate(PayDate_Excel[i]);
	}

	long* LizardStartDate_Ctype = (long*)malloc(sizeof(double) * max(NLizard, 1));	// 26
	long* LizardEndDate_Ctype = (long*)malloc(sizeof(double) * max(NLizard, 1));	// 27
	for (i = 0; i < NLizard; i++)
	{
		LizardStartDate_Ctype[i] = ExcelDateToCDate(LizardStartDate_Excel[i]);
		LizardEndDate_Ctype[i] = ExcelDateToCDate(LizardEndDate_Excel[i]);
	}

	long* CPN_EvaluateDate_Ctype = (long*)malloc(sizeof(double) * max(NCPN, 1));	// 28
	long* CPN_PayDate_Ctype = (long*)malloc(sizeof(double) * max(NCPN, 1));			// 29
	for (i = 0; i < NCPN; i++)
	{
		CPN_EvaluateDate_Ctype[i] = ExcelDateToCDate(CPN_EvaluateDate_Excel[i]);
		CPN_PayDate_Ctype[i] = ExcelDateToCDate(CPN_PayDate_Excel[i]);
	}

	/////////////
	// ��ó�� �Լ��� �Ѿ��
	/////////////

	// �ִ� �ùķ��̼�Ƚ��
	long MaxSimulDays;
	MaxSimulDays = DayCountAtoB(PricingDate_Ctype, PayDate_Ctype[NEvaluate - 1]) + 1;

	// Day Difference ���Ǹ� ���� �ùķ��̼��� �ʿ��� �� �ƴ��� �Ǵ�
	long* Days_Autocall_Eval = (long*)malloc(sizeof(long) * max(NEvaluate, 1));		// 30
	long* Days_Autocall_Pay = (long*)malloc(sizeof(long) * max(NEvaluate, 1));		// 31
	long* Days_LizardStart = (long*)malloc(sizeof(double) * max(NLizard, 1));		// 32
	long* Days_LizardEnd = (long*)malloc(sizeof(double) * max(NLizard, 1));			// 33
	long* Days_CPN_Eval = (long*)malloc(sizeof(double) * max(NCPN, 1));				// 34
	long* Days_CPN_Pay = (long*)malloc(sizeof(double) * max(NCPN, 1));				// 35

	for (i = 0; i < NEvaluate; i++)
	{
		Days_Autocall_Eval[i] = DayCountAtoB(PricingDate_Ctype, EvalDate_Ctype[i]);
		Days_Autocall_Pay[i] = DayCountAtoB(PricingDate_Ctype, PayDate_Ctype[i]);
	}

	for (i = 0; i < NLizard; i++)
	{
		Days_LizardStart[i] = DayCountAtoB(PricingDate_Ctype, LizardStartDate_Ctype[i]);
		Days_LizardEnd[i] = DayCountAtoB(PricingDate_Ctype, LizardEndDate_Ctype[i]);
	}

	for (i = 0; i < NCPN; i++)
	{
		Days_CPN_Eval[i] = DayCountAtoB(PricingDate_Ctype, CPN_EvaluateDate_Ctype[i]);
		Days_CPN_Pay[i] = DayCountAtoB(PricingDate_Ctype, CPN_PayDate_Ctype[i]);
	}

	long idx_hist;

	//////////////////////////////////////////////////////
	// ���ذ� ��� �����ְ� ���, Correlation Matrix ���·� Reshape
	/////////////////////////////////////////////////////

	double* S0_Value = (double*)malloc(sizeof(double) * NStock);					// 36
	double** CorrelationMatrix = (double**)malloc(sizeof(double*) * NStock);		// 37
	long RedempFlag;
	long RedempIdx;
	long LizardRedempFlag;
	long LizardRedempIdx;
	long CPNRedempFlag;
	long CPNRedempIdx;
	long CPNIdx;
	long Evaluation_Idx;
	long Maturity_Flag;
	long Simulation_Required;
	double minS;
	double T_CPN;
	double DF_CPN;
	nK = 3;					// ��簡�ݰ���

	double* SortedStrike = (double*)malloc(sizeof(double) * nK);					// 38
	long* StrikeIdx = (long*)malloc(sizeof(long) * nK);								// 39
	double RedempSlope;
	double RedempCPN;
	long N_TermDisc;				// ���� Term ����
	double* TermDisc;				// ���� Term
	double* RateDisc;				// ���� Rate
	long* N_TermRf;					// �����ڻ� �� Risk Free Rate ����

	double* TermRf_Simul;					// �����ڻ� �� Risk Free Rate Term
	double* RateRf_Simul;					// �����ڻ� �� Risk Free Rate
	double ResultPrice[10] = { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 };
	double TTM = 0.0;
	double DiscFactor = 1.0;
	double Payoff = 0.0;


	double*** FixedRandn = (double***)malloc(sizeof(double**) * NSimul);

	randnorm(0);
	for (i = 0; i < NSimul; i++)
	{
		FixedRandn[i] = (double**)malloc(sizeof(double*) * MaxSimulDays);
		for (j = 0; j < MaxSimulDays; j++)
		{
			FixedRandn[i][j] = (double*)malloc(sizeof(double) * NStock);
			for (k = 0; k < NStock; k++)
			{
				FixedRandn[i][j][k] = randnorm();
			}
		}
	}

	/////////////////////////////////////////
	// ���� ����� ���� �̸� �Ҵ��� �迭�� //
	/////////////////////////////////////////
	double* path_price = (double*)calloc(NSimul, sizeof(double));
	double** daily_forward_rate = (double**)malloc(sizeof(double*) * NStock);
	double** daily_forward_div = (double**)malloc(sizeof(double*) * NStock);
	double** daily_forward_fxvol = (double**)malloc(sizeof(double*) * NStock);
	for (i = 0; i < NStock; i++)
	{
		daily_forward_rate[i] = (double*)malloc(sizeof(double) * MaxSimulDays);
		daily_forward_div[i] = (double*)malloc(sizeof(double) * MaxSimulDays);
		daily_forward_fxvol[i] = (double*)malloc(sizeof(double) * MaxSimulDays);
	}

	simulinfo Info_Simul(1, NSimul, NStock, 1, PricingDate_Ctype, S0_ForSimul[0], CorrelationMatrix, MaxSimulDays, FixedRandn, path_price);

	for (idx_hist = 0; idx_hist < NHistory; idx_hist++)
	{
		ResultPrice[0] = 0.0;
		N_TermDisc = N_DF_Curve[idx_hist];
		TermDisc = Term_DF_Curve[idx_hist];
		RateDisc = Rate_DF_Curve[idx_hist];
		N_TermRf = N_Rf_Curve[idx_hist];
		TermRf_Simul = Term_Rf_Curve[idx_hist];
		RateRf_Simul = Rate_Rf_Curve[idx_hist];

		for (i = 0; i < NStock; i++)
		{
			S0_Value[i] = S0_ForSimul[idx_hist][i] / X[i];
			CorrelationMatrix[i] = CorrelReshaped_Simul[idx_hist] + i * NStock;
			// Diagonal Check
			if (CorrelationMatrix[i][i] != 1.0)
			{
				CorrelationMatrix[i][i] = 1.0;
			}
		}
		Info_Simul.s0 = S0_Value;
		Info_Simul.correlation = CorrelationMatrix;
		for (i = 0; i < NSimul; i++)
		{
			Info_Simul.pathprice[i] = 0.0;
		}

		RedempFlag = 0;			// �����ȯ�Ǵ�������
		RedempIdx = 0;				// �����ȯ �� ��° �Ǵ���
		LizardRedempFlag = 0;		// ���ڵ��ȯ�Ǵ�������
		LizardRedempIdx = 0;		// ���ڵ� �� ��° ��ȯ�Ǵ���
		CPNRedempFlag = 0;			// �������޵Ǵ�������
		CPNRedempIdx = 0;			// ���� �� ��° ���޵Ǵ���
		CPNIdx = 0;				// ���޵��� ���� ���� Index
		Evaluation_Idx = 0;		// �򰡽���
		Maturity_Flag = 0;			// �����ȯ Flag

		Simulation_Required = 1;	// �ϴ� �ùķ��̼��� �䱸�ȴٴ� �������� ����

		RedempSlope = 0.0;
		RedempCPN = 0.0;
		// ���ݰ����� �����ȯ���� üũ
		for (i = 0; i < NEvaluate; i++)
		{
			if (Days_Autocall_Eval[i] == 0)
			{
				/////////////////////////////////
				// �������� ���� �����ǰ��
				/////////////////////////////////

				minS = S0_Value[0];
				for (j = 1; j < NStock; j++)
				{
					minS = min(minS, S0_Value[j]);
				}

				for (j = 0; j < nK; j++)
				{
					SortedStrike[j] = Strike[j][i];
					StrikeIdx[j] = j;
				}

				bubble_sort(SortedStrike, StrikeIdx, nK);

				/////////////////////////////////
				// �����ȯ �Ǿ����� üũ
				/////////////////////////////////

				for (j = 0; j < nK; j++)
				{
					if (minS >= SortedStrike[j] && SortedStrike[j] > 0.0)
					{
						RedempFlag = 1;
						RedempIdx = i;
						RedempSlope = AutocallSlope[StrikeIdx[j]][i];
						RedempCPN = AutocallCPN[StrikeIdx[j]][i];
						break;
					}
				}

				if (RedempFlag == 1)
				{
					break;
				}
				else
				{

					/////////////////////////////////
					// ���ڵ� �踮�� ���õ��� �ʾ����� ���ڵ��ȯ
					/////////////////////////////////

					if (i < NLizard)
					{
						if (LizardFlag[i] > 0 && Now_LizardHitting[i] == 0)
						{
							LizardRedempFlag = 1;
							LizardRedempIdx = 1;
							break;
						}
					}

				}
			}
			else if (Days_Autocall_Eval[i] < 0 && Days_Autocall_Pay[i] > 0)
			{

				/////////////////////////////////
				// ���ݰ������� ���ϰ� ������ ������ ���
				/////////////////////////////////

				// ���� ������ �ԷµǾ������� �װ��� ���� �ƴϸ� ���簡�� ����.
				if (Base_S_ForSimul[0] > 0.0) minS = Base_S_ForSimul[0] / X[0];
				else minS = S0_Value[0];

				for (j = 1; j < NStock; j++)
				{
					if (Base_S_ForSimul[i] > 0.0) minS = min(minS, Base_S_ForSimul[j] / X[j]);
					else minS = min(minS, S0_Value[i]);
				}

				for (j = 0; j < nK; j++)
				{
					SortedStrike[j] = Strike[j][i];
					StrikeIdx[j] = j;
				}

				bubble_sort(SortedStrike, StrikeIdx, nK);

				/////////////////////////////////
				// �����ȯ �Ǿ����� üũ
				/////////////////////////////////

				for (j = 0; j < nK; j++)
				{
					if (minS >= SortedStrike[j] && SortedStrike[j] > 0.0)
					{
						RedempFlag = 1;
						RedempIdx = i;
						RedempSlope = AutocallSlope[StrikeIdx[j]][i];
						RedempCPN = AutocallCPN[StrikeIdx[j]][i];
						break;
					}
				}

				if (RedempFlag == 1)
				{
					break;
				}
				else
				{

					/////////////////////////////////
					// ���ڵ� �踮�� ���õ��� �ʾ����� ���ڵ��ȯ
					/////////////////////////////////

					if (i < NLizard)
					{
						if (LizardFlag[i] > 0 && Now_LizardHitting[i] == 0)
						{
							LizardRedempFlag = 1;
							LizardRedempIdx = 1;
							break;
						}
					}

				}
			}

			if (Days_Autocall_Eval[max(0, NEvaluate - 1 - i)] > 0)
			{
				Evaluation_Idx = NEvaluate - 1 - i;
			}
		}

		/////////////////////////////////
		// ���� ������� �����踮�� üũ
		/////////////////////////////////

		for (i = 0; i < NCPN; i++)
		{
			if (Days_CPN_Eval[i] == 0)
			{
				minS = S0_Value[0];
				for (j = 1; j < NStock; j++)
				{
					minS = min(minS, S0_Value[j]);
				}

				if (minS >= CPN_Lower_Barrier[i] && minS < CPN_Upper_Barrier[i])
				{
					CPNRedempFlag = 1;
					CPNRedempIdx = i;
					T_CPN = ((double)Days_CPN_Pay[i]) / 365.0;
					DF_CPN = Calc_Discount_Factor(TermDisc, RateDisc, N_TermDisc, T_CPN) * CPN_Rate[i];
					break;
				}
			}
			else if (Days_CPN_Eval[i] < 0 && Days_CPN_Pay[i] > 0)
			{
				if (Base_S_CPN_ForSimul[0] > 0.0)
					minS = Base_S_CPN_ForSimul[0] / X[0];
				else
					minS = S0_Value[0];

				for (j = 1; j < NStock; j++)
				{
					if (Base_S_CPN_ForSimul[i] > 0.0)
						minS = min(minS, Base_S_CPN_ForSimul[j] / X[j]);
					else
						minS = min(minS, S0_Value[i]);
				}

				if (minS >= CPN_Lower_Barrier[i] && minS < CPN_Upper_Barrier[i])
				{
					CPNRedempFlag = 1;
					CPNRedempIdx = i;
					T_CPN = ((double)Days_CPN_Pay[i]) / 365.0;
					DF_CPN = Calc_Discount_Factor(TermDisc, RateDisc, N_TermDisc, T_CPN) * CPN_Rate[i];
					break;
				}
			}

			if (Days_CPN_Eval[max(0, NCPN - 1 - i)] > 0)
			{
				CPNIdx = NCPN - 1 - i;
			}
		}

		/////////////////////////////////
		// �ϴ� ���� �ְ� �������� ���λ��º��� �ٽ� üũ
		/////////////////////////////////

		if (KI_Method == 1)
		{
			for (i = 0; i < NStock; i++)
			{
				if (S0_Value[i] < KI_Barrier_Level)
				{
					Now_KI_State = 1;
					break;
				}
			}
		}

		/////////////////////////////////
		// �����ȯ üũ
		/////////////////////////////////

		if (Days_Autocall_Eval[NEvaluate - 1] <= 0)
		{
			RedempFlag = 1;

			minS = S0_Value[0];
			for (j = 1; j < NStock; j++)
			{
				minS = min(minS, S0_Value[j]);
			}

			if (KI_Method == 2 && minS < KI_Barrier_Level)
			{
				Now_KI_State = 1;
			}

			if (Now_KI_State > 0)
			{
				RedempIdx = NEvaluate + 1;
				RedempSlope = 1.0;
				for (j = 0; j < nK; j++)
				{
					if (AutocallSlope[j][NEvaluate + 1] != 0.0)
					{
						RedempSlope = AutocallSlope[j][NEvaluate + 1];
						break;
					}
				}
				for (j = 0; j < nK; j++)
				{
					if (AutocallCPN[j][NEvaluate + 1] != 0.0)
					{
						RedempCPN = AutocallCPN[j][NEvaluate + 1];
						break;
					}
				}
			}
			else
			{
				RedempIdx = NEvaluate;
				RedempSlope = 0.0;
				for (j = 0; j < nK; j++)
				{
					if (AutocallSlope[j][NEvaluate + 1] != 0.0)
					{
						RedempSlope = AutocallSlope[j][NEvaluate + 1];
						break;
					}
				}
				for (j = 0; j < nK; j++)
				{
					if (AutocallCPN[j][NEvaluate + 1] != 0.0)
					{
						RedempCPN = AutocallCPN[j][NEvaluate + 1];
						break;
					}
				}
			}
		}

		///////////////////////////////////////////////////////
		// �����ȯ �Ǵ� ���ڵ��ȯ �Ǿ��ٸ� �ùķ��̼��� �ʿ������ ����
		///////////////////////////////////////////////////////

		if (RedempFlag == 1) Simulation_Required = 0;
		if (LizardRedempFlag == 1) Simulation_Required = 0;

		TTM = 0.0;
		DiscFactor = 1.0;
		Payoff = 0.0;
		if (RedempFlag > 0)
		{
			TTM = (double)Days_Autocall_Pay[min(NEvaluate - 1, RedempIdx)] / 365.0;
			DiscFactor = Calc_Discount_Factor(TermDisc, RateDisc, N_TermDisc, TTM);
			Payoff = Redemption_Payoff(FaceValue, FaceValueFlag, MaxProfit, MaxLoss, minS, RedempSlope, RedempCPN);
			ResultPrice[0] = Payoff * DiscFactor;

		}
		else if (LizardRedempFlag > 0)
		{
			TTM = (double)Days_Autocall_Pay[LizardRedempIdx] / 365.0;
			DiscFactor = Calc_Discount_Factor(TermDisc, RateDisc, N_TermDisc, TTM);
			Payoff = Redemption_Payoff(FaceValue, FaceValueFlag, MaxProfit, MaxLoss, minS, RedempSlope, RedempCPN);
			ResultPrice[0] = Payoff * DiscFactor;
		}

		//////////////////////////
		// �̹� ���޵� ������ �ִٸ� ������ �̸� �־��ְ� �ùķ��̼� ����
		//////////////////////////

		if (CPNRedempFlag == 1)
		{
			for (i = 0; i < NSimul; i++)
			{
				Info_Simul.pathprice[i] = DF_CPN;
			}
		}

		//////////////////////////
		// �ùķ��̼� Daily Forward Rate, Daily Div ����
		//////////////////////////

		Info_Simul.set_daily_data(N_TermRf, TermRf_Simul, RateRf_Simul,
			NDiv_Simul[idx_hist], DivTerm_Simul[idx_hist], DivRate_Simul[idx_hist], DivFlag,
			NFXVol_Simul[idx_hist], FXVolTerm_Simul[idx_hist], FXVolRate_Simul[idx_hist], QuantoFlag, QuantoCorr_Simul[idx_hist],
			daily_forward_rate, daily_forward_div, daily_forward_fxvol);

		PriceHistory[idx_hist] = Preprocessing_HiFiVe_VaR(RedempFlag, LizardRedempFlag, FaceValue, FaceValueFlag, MaxProfit,
			MaxLoss, NStock, S0_ForSimul[idx_hist], X, KI_Method,
			KI_Barrier_Level, Now_KI_State, NEvaluate, Evaluation_Idx, Days_Autocall_Eval,
			Days_Autocall_Pay, nK, Strike, AutocallSlope, AutocallCPN,
			NLizard, LizardFlag, Days_LizardStart, Days_LizardEnd, LizardBarrierLevel,
			LizardCoupon, Now_LizardHitting, NCPN, CPNIdx, Days_CPN_Eval,
			Days_CPN_Pay, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate, N_TermDisc,
			TermDisc, RateDisc, N_TermRf, TermRf_Simul, RateRf_Simul,
			NDiv_Simul[idx_hist], DivTerm_Simul[idx_hist], DivRate_Simul[idx_hist], NFXVol_Simul[idx_hist], FXVolTerm_Simul[idx_hist],
			FXVolRate_Simul[idx_hist], VolFlag, NParity_Simul[idx_hist], Parity_Simul[idx_hist], NTermVol_Simul[idx_hist],
			TermVol_Simul[idx_hist], Vol_Simul[idx_hist], Info_Simul, Simulation_Required, NSimul, ResultPrice);



		Info_Simul.delete_daily_data();
	}

	double* ReturnData = (double*)malloc(sizeof(double) * NHistory);			// 40
	double* Quantile = (double*)malloc(sizeof(double) * NHistory);				// 41
	for (i = 0; i < NHistory; i++)
	{
		if (i == 0) ReturnData[i] = 0.0;
		else ReturnData[i] = PriceHistory[i - 1] / PriceHistory[i] - 1.0;
		Quantile[i] = 1.0 / (double)NHistory * (double)(i + 1);
	}
	bubble_sort(ReturnData, NHistory);
	double a1, a2, a3;
	a1 = 0.05;
	a2 = 0.01;
	a3 = 0.001;

	VaRInfo[0] = PriceHistory[0] * Interpolate_Linear(Quantile, ReturnData, NHistory, a1, 1);
	VaRInfo[1] = PriceHistory[0] * Interpolate_Linear(Quantile, ReturnData, NHistory, a2, 1);
	VaRInfo[2] = PriceHistory[0] * Interpolate_Linear(Quantile, ReturnData, NHistory, a3, 1);
	VaRInfo[3] = VaRInfo[0] * sqrt(10.0);
	VaRInfo[4] = VaRInfo[1] * sqrt(10.0);
	VaRInfo[5] = VaRInfo[2] * sqrt(10.0);
	VaRInfo[6] = VaRInfo[0] * sqrt(250.0);
	VaRInfo[7] = VaRInfo[1] * sqrt(250.0);
	VaRInfo[8] = VaRInfo[2] * sqrt(250.0);

	free(Strike);
	free(AutocallSlope);
	free(AutocallCPN);
	free(S0_ForSimul);
	free(CorrelReshaped_Simul);
	free(N_DF_Curve);
	free(N_Rf_Curve);
	free(Term_DF_Curve);
	free(Term_Rf_Curve);
	free(Rate_DF_Curve);
	free(Rate_Rf_Curve);
	free(NParity_Simul);
	free(NTermVol_Simul);
	free(Parity_Simul);
	free(TermVol_Simul);
	free(Vol_Simul);
	free(NDiv_Simul);
	free(DivTerm_Simul);
	free(DivRate_Simul);
	free(QuantoCorr_Simul);
	free(NFXVol_Simul);
	free(FXVolTerm_Simul);
	free(FXVolRate_Simul);
	free(EvalDate_Ctype);
	free(PayDate_Ctype);
	free(LizardStartDate_Ctype);
	free(LizardEndDate_Ctype);
	free(CPN_EvaluateDate_Ctype);
	free(CPN_PayDate_Ctype);
	free(Days_Autocall_Eval);
	free(Days_Autocall_Pay);
	free(Days_LizardStart);
	free(Days_LizardEnd);
	free(Days_CPN_Eval);
	free(Days_CPN_Pay);
	free(S0_Value);
	free(CorrelationMatrix);
	free(SortedStrike);
	free(StrikeIdx);
	free(ReturnData);
	free(Quantile);

	for (i = 0; i < NSimul; i++)
	{
		for (j = 0; j < MaxSimulDays; j++)
		{
			free(FixedRandn[i][j]);
		}
		free(FixedRandn[i]);
	}
	free(FixedRandn);
	free(path_price);
	for (i = 0; i < NStock; i++)
	{
		free(daily_forward_rate[i]);
		free(daily_forward_div[i]);
		free(daily_forward_fxvol[i]);
	}
	free(daily_forward_rate);
	free(daily_forward_div);
	free(daily_forward_fxvol);
	return 1;
}

void Logging_Excel_HiFive_VaR(
	long PricingDate_Excel,			// ���ݰ�곯¥ ExcelType Ex) 44201(2021��01��05��)
	long NSimul,					// �ùķ��̼ǰ���
	long NHistory,					// ������ History ����
	double FaceValue,				// ���ݾ�
	long FaceValueFlag,				// ���ݼ�������

	double MaxProfit,				// �ִ�����
	double MaxLoss,					// �ִ�ս�
	long NEvaluate,					// �����ȯ ���ϰ���
	double KI_Barrier_Level,		// ���ι踮�����
	long Now_KI_State,				// ���� ���λ���

	long KI_Method,					// ����ó�����
	long* EvalDate_Excel,			// �����ȯ ExcelType���� Array [ Shape = (NEvaluate , ) ]
	long* PayDate_Excel,			// �����ȯ ExcelType������ Array [ Shape = (NEvaluate , ) ]
	long* NStrike,					// �����ȯ ȸ���� ��簡�ݰ��� Array [ Shape = (NEvaluate , ) ]
	double* StrikeLevel,			// �����ȯ ȸ���� ��簡�� Array [ Shape = reshape(3 * NEvaluate) ]

	double* Slope,					// �����ȯ ȸ���� ������ [ Shape = reshape(3 * NEvaluate)  ]
	double* FixedAmount,			// �����ȯ ȸ���� ���� [ Shape = reshape(3 * NEvaluate)  ]
	long NLizard,					// ���ڵ��ȯ ���� ����
	long* LizardFlag,				// �����ȯ ȸ���� ���ڵ��ȯ ������ ���� Array [ Shape = (NLizard , ) ]
	long* LizardStartDate_Excel,	// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]

	long* LizardEndDate_Excel,		// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]
	double* LizardBarrierLevel,		// �����ȯ ȸ���� ���ڵ�踮�� �踮��� Array
	long* Now_LizardHitting,		// �����ȯ ȸ���� ���ڵ�踮�� ���� Hitting���� Array
	double* LizardCoupon,			// �����ȯ ȸ���� ���ڵ�踮�� ���������� Array
	long NCPN,						// �Ϲ� ���� ���� ����

	long* CPN_EvaluateDate_Excel,	// �Ϲ� ���� ���� ExcelType Array [ Shape = (NCPN , ) ]
	long* CPN_PayDate_Excel,		// �Ϲ� ���� ������ ExcelType Array [ Shape = (NCPN , ) ]
	double* CPN_Lower_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Upper_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Rate,				// �Ϲ� ���� ���������� Array [ Shape = (NCPN , ) ]

	long NStock,					// �����ڻ갳��
	double* S0,						// �����ڻ� Shape = NHistory * NStock
	double* X,						// ���ذ���,�ֱ����ϰ���, �ֱ��������ϰ���
	double* CorrelReshaped,
	long* NRf,

	double* TermRf,
	double* RateRf,
	long VolFlag,
	long* NParity,
	long* NTermVol,

	long* NVol,
	double* Parity,
	double* TermVol,
	double* Vol,
	long* DivFlag,

	long* NDiv,
	double* DivTerm,
	double* DivRate,
	long* QuantoFlag,
	double* QuantoCorr,

	long* NFXVol,
	double* FXVolTerm,
	double* FXVolRate,
	long VaRMethod,
	char* CalcFunctionName,
	char* SaveFileName
)
{
	long i, j, n, nn, nnn;
	double* n2;
	double* n3;
	double* n4;
	DumppingTextData(CalcFunctionName, SaveFileName, "PricingDate_Excel", PricingDate_Excel);
	DumppingTextData(CalcFunctionName, SaveFileName, "NSimul", NSimul);
	DumppingTextData(CalcFunctionName, SaveFileName, "NHistory", NHistory);
	DumppingTextData(CalcFunctionName, SaveFileName, "FaceValue", FaceValue);
	DumppingTextData(CalcFunctionName, SaveFileName, "FaceValueFlag", FaceValueFlag);

	DumppingTextData(CalcFunctionName, SaveFileName, "MaxProfit", MaxProfit);
	DumppingTextData(CalcFunctionName, SaveFileName, "MaxLoss", MaxLoss);
	DumppingTextData(CalcFunctionName, SaveFileName, "NEvaluate", NEvaluate);
	DumppingTextData(CalcFunctionName, SaveFileName, "KI_Barrier_Level", KI_Barrier_Level);
	DumppingTextData(CalcFunctionName, SaveFileName, "Now_KI_State", Now_KI_State);

	DumppingTextData(CalcFunctionName, SaveFileName, "KI_Method", KI_Method);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "EvalDate_Excel", NEvaluate, EvalDate_Excel);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "PayDate_Excel", NEvaluate, PayDate_Excel);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "NStrike", NEvaluate, NStrike);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "StrikeLevel", 3, NEvaluate, StrikeLevel);

	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "Slope", 3, (NEvaluate + 2), Slope);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "FixedAmount", 3, (NEvaluate + 2), FixedAmount);
	DumppingTextData(CalcFunctionName, SaveFileName, "NLizard", NLizard);
	if (NLizard > 0)
	{
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardFlag", NLizard, LizardFlag);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardStartDate_Excel", NLizard, LizardStartDate_Excel);

		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardEndDate_Excel", NLizard, LizardEndDate_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardBarrierLevel", NLizard, LizardBarrierLevel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Now_LizardHitting", NLizard, Now_LizardHitting);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "LizardCoupon", NLizard, LizardCoupon);
		DumppingTextData(CalcFunctionName, SaveFileName, "NCPN", NCPN);
	}
	if (NCPN > 0)
	{
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_EvaluateDate_Excel", NCPN, CPN_EvaluateDate_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_PayDate_Excel", NCPN, CPN_PayDate_Excel);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_Lower_Barrier", NCPN, CPN_Lower_Barrier);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_Upper_Barrier", NCPN, CPN_Upper_Barrier);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CPN_Rate", NCPN, CPN_Rate);
	}

	DumppingTextData(CalcFunctionName, SaveFileName, "NStock", NStock);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "S0", NHistory * NStock, S0);
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "X", 3 * NStock, X);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "Correlation", NStock * NStock, NHistory, CorrelReshaped);

	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "NRf", NHistory, NStock + 1, NRf);
	nn = 0;
	for (i = 0; i < NHistory; i++)
	{
		n2 = TermRf + nn;
		n3 = RateRf + nn;
		n = 0;
		for (j = 0; j < NStock + 1; j++)
		{
			n += (NRf + (NStock + 1) * i)[j];
		}
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "TermRf", n, n2);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "RateRf", n, n3);
		nn += n;
	}

	DumppingTextData(CalcFunctionName, SaveFileName, "VolFlag", VolFlag);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "NParity", NHistory, NStock, NParity);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "NTermVol", NHistory, NStock, NTermVol);
	nn = 0;
	for (i = 0; i < NHistory; i++)
	{
		n2 = Parity + nn;
		n = 0;
		for (j = 0; j < NStock; j++)
		{
			n += (NParity + (NStock)*i)[j];
		}
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Parity", n, n2);
		nn += n;
	}

	nn = 0;
	for (i = 0; i < NHistory; i++)
	{
		n2 = TermVol + nn;
		n = 0;
		for (j = 0; j < NStock; j++)
		{
			n += (NTermVol + (NStock)*i)[j];
		}
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "TermVol", n, n2);
		nn += n;
	}

	nn = 0;
	for (i = 0; i < NHistory; i++)
	{
		n2 = Vol + nn;
		n = 0;
		for (j = 0; j < NStock; j++)
		{
			n += (NTermVol + (NStock)*i)[j] * (NParity + (NStock)*i)[j];
		}
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "Vol", n, n2);
		nn += n;
	}

	DumppingTextDataArray(CalcFunctionName, SaveFileName, "DivFlag", NStock, DivFlag);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "NDiv", NHistory, NStock, NDiv);

	nn = 0;
	for (i = 0; i < NHistory; i++)
	{
		n2 = DivTerm + nn;
		n3 = DivRate + nn;
		n = 0;
		for (j = 0; j < NStock; j++)
		{
			n += (NDiv + (NStock)*i)[j];
		}
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "DivTerm", n, n2);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "DivRate", n, n3);
		nn += n;
	}
	DumppingTextDataArray(CalcFunctionName, SaveFileName, "QuantoFlag", NStock, QuantoFlag);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "QuantoCorr", NHistory, NStock, QuantoCorr);
	DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "NFXVol", NHistory, NStock, NFXVol);
	nn = 0;
	for (i = 0; i < NHistory; i++)
	{
		n2 = FXVolTerm + nn;
		n3 = FXVolRate + nn;
		n = 0;
		for (j = 0; j < NStock; j++)
		{
			n += (NFXVol + (NStock)*i)[j];
		}
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "FXVolTerm", n, n2);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "FXVolRate", n, n3);
		nn += n;
	}
	DumppingTextData(CalcFunctionName, SaveFileName, "VaRMethod", VaRMethod);
}

DLLEXPORT(long) Excel_HiFive_VaR(
	long PricingDate_Excel,			// ���ݰ�곯¥ ExcelType Ex) 44201(2021��01��05��)
	long NSimul,					// �ùķ��̼ǰ���
	long NHistory,					// ������ History ����
	double FaceValue,				// ���ݾ�
	long FaceValueFlag,				// ���ݼ�������

	double MaxProfit,				// �ִ�����
	double MaxLoss,					// �ִ�ս�
	long NEvaluate,					// �����ȯ ���ϰ���
	double KI_Barrier_Level,		// ���ι踮�����
	long Now_KI_State,				// ���� ���λ���

	long KI_Method,					// ����ó�����
	long* EvalDate_Excel,			// �����ȯ ExcelType���� Array [ Shape = (NEvaluate , ) ]
	long* PayDate_Excel,			// �����ȯ ExcelType������ Array [ Shape = (NEvaluate , ) ]
	long* NStrike,					// �����ȯ ȸ���� ��簡�ݰ��� Array [ Shape = (NEvaluate , ) ]
	double* StrikeLevel,			// �����ȯ ȸ���� ��簡�� Array [ Shape = reshape(3 * NEvaluate) ]

	double* Slope,					// �����ȯ ȸ���� ������ [ Shape = reshape(3 * NEvaluate)  ]
	double* FixedAmount,			// �����ȯ ȸ���� ���� [ Shape = reshape(3 * NEvaluate)  ]
	long NLizard,					// ���ڵ��ȯ ���� ����
	long* LizardFlag,				// �����ȯ ȸ���� ���ڵ��ȯ ������ ���� Array [ Shape = (NLizard , ) ]
	long* LizardStartDate_Excel,	// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]

	long* LizardEndDate_Excel,		// �����ȯ ȸ���� ���ڵ�踮�� üũ ������ ExcelType Array [ Shape = (NLizard , ) ]
	double* LizardBarrierLevel,		// �����ȯ ȸ���� ���ڵ�踮�� �踮��� Array
	long* Now_LizardHitting,		// �����ȯ ȸ���� ���ڵ�踮�� ���� Hitting���� Array
	double* LizardCoupon,			// �����ȯ ȸ���� ���ڵ�踮�� ���������� Array
	long NCPN,						// �Ϲ� ���� ���� ����

	long* CPN_EvaluateDate_Excel,	// �Ϲ� ���� ���� ExcelType Array [ Shape = (NCPN , ) ]
	long* CPN_PayDate_Excel,		// �Ϲ� ���� ������ ExcelType Array [ Shape = (NCPN , ) ]
	double* CPN_Lower_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Upper_Barrier,		// �Ϲ� ���� �Ϲ�踮�� Array [ Shape = (NCPN , ) ]
	double* CPN_Rate,				// �Ϲ� ���� ���������� Array [ Shape = (NCPN , ) ]

	long NStock,					// �����ڻ갳��
	double* S0,						// �����ڻ� Shape = NHistory * NStock
	double* X,						// ���ذ���,�ֱ����ϰ���, �ֱ��������ϰ���
	double* CorrelReshaped,
	long* NRf,

	double* TermRf,
	double* RateRf,
	long VolFlag,
	long* NParity,
	long* NTermVol,

	long* NVol,
	double* Parity,
	double* TermVol,
	double* Vol,
	long* DivFlag,

	long* NDiv,
	double* DivTerm,
	double* DivRate,
	long* QuantoFlag,
	double* QuantoCorr,

	long* NFXVol,
	double* FXVolTerm,
	double* FXVolRate,
	long VaRMethod,
	double* PriceHistory,

	double* VaRInfo,
	char* Error,
	long TextDumpFlag
)
{
	long i, j;
	long ErrorCode = 0;

	ErrorCode = ErrorCheck_Excel_HiFive_VaR(
		PricingDate_Excel, NSimul, NHistory, FaceValue, FaceValueFlag,
		MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
		KI_Method, EvalDate_Excel, PayDate_Excel, NStrike, StrikeLevel,
		Slope, FixedAmount, NLizard, LizardFlag, LizardStartDate_Excel,
		LizardEndDate_Excel, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
		CPN_EvaluateDate_Excel, CPN_PayDate_Excel, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
		NStock, S0, X, CorrelReshaped, NRf,
		TermRf, RateRf, VolFlag, NParity, NTermVol,
		NVol, Parity, TermVol, Vol, DivFlag,
		NDiv, DivTerm, DivRate, QuantoFlag, QuantoCorr,
		NFXVol, FXVolTerm, FXVolRate, VaRMethod, PriceHistory,
		VaRInfo, Error);

	if (ErrorCode < 0)
	{
		return ErrorCode;
	}

	char CalcFunctionName[] = "Excel_HiFive_VaR";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag > 0)
	{
		Logging_Excel_HiFive_VaR(
			PricingDate_Excel, NSimul, NHistory, FaceValue, FaceValueFlag,
			MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
			KI_Method, EvalDate_Excel, PayDate_Excel, NStrike, StrikeLevel,
			Slope, FixedAmount, NLizard, LizardFlag, LizardStartDate_Excel,
			LizardEndDate_Excel, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
			CPN_EvaluateDate_Excel, CPN_PayDate_Excel, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
			NStock, S0, X, CorrelReshaped, NRf,
			TermRf, RateRf, VolFlag, NParity, NTermVol,
			NVol, Parity, TermVol, Vol, DivFlag,
			NDiv, DivTerm, DivRate, QuantoFlag, QuantoCorr,
			NFXVol, FXVolTerm, FXVolRate, VaRMethod, CalcFunctionName, SaveFileName);

	}

	ErrorCode = HiFive_VaR_Excel(
		PricingDate_Excel, NSimul, NHistory, FaceValue, FaceValueFlag,
		MaxProfit, MaxLoss, NEvaluate, KI_Barrier_Level, Now_KI_State,
		KI_Method, EvalDate_Excel, PayDate_Excel, NStrike, StrikeLevel,
		Slope, FixedAmount, NLizard, LizardFlag, LizardStartDate_Excel,
		LizardEndDate_Excel, LizardBarrierLevel, Now_LizardHitting, LizardCoupon, NCPN,
		CPN_EvaluateDate_Excel, CPN_PayDate_Excel, CPN_Lower_Barrier, CPN_Upper_Barrier, CPN_Rate,
		NStock, S0, X, CorrelReshaped, NRf,
		TermRf, RateRf, VolFlag, NParity, NTermVol,
		NVol, Parity, TermVol, Vol, DivFlag,
		NDiv, DivTerm, DivRate, QuantoFlag, QuantoCorr,
		NFXVol, FXVolTerm, FXVolRate, VaRMethod, PriceHistory,
		VaRInfo, Error);

	//_CrtDumpMemoryLeaks();
	return ErrorCode;
}