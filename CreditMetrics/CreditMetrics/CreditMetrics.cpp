#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "Util.h"
#include "GetTextDump.h"

#ifndef DLLEXPORT(A)
#ifdef WIN32
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#elif _WIN64
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#elif __linux__
#define DLLEXPORT(A) extern "C" __declspec
#elif __hpux
#define DLLEXPORT(A) extern "C" __declspec
#elif __unix__
#define DLLEXPORT(A) extern "C" __declspec
#else 
#define DLLEXPORT(A) extern "C" __declspec(dllexport) A __stdcall 
#endif
#endif

double Calc_Geometric_Value(
	long CurrentIndex,
	long PrevIndex,
	double PrevValue,
	long NextIndex,
	double NextValue
)
{
	double N = (double)(NextIndex - PrevIndex);
	double N_A = (double)(CurrentIndex - PrevIndex);
	double N_B = (double)(NextIndex - CurrentIndex);
	return pow(pow(PrevValue, N - N_A) * pow(NextValue, N - N_B), 1.0 / N);
}

double Calc_Boundary_Value(
	double PrevValue,
	double PrevPrevValue
)
{
	return PrevValue * PrevValue / PrevPrevValue;
}

void Adjust_DiagonalMax(
	long SizeMatrix,
	double** MyMatrix
)
{
	long i, j;
	double diagvalue;
	for (i = 0 ; i < SizeMatrix; i++)
	{
		diagvalue = MyMatrix[i][i];

		// 정방향
		for (j = i + 1; j < SizeMatrix - 1; j++)
		{
			if (MyMatrix[i][j] > diagvalue)
			{
				if (MyMatrix[i][j + 1] > 0.0 && MyMatrix[i][j - 1] > 0.0) MyMatrix[i][j] = sqrt(MyMatrix[i][j - 1] * MyMatrix[i][j + 1]);
			}
		}

		// 역방향
		for (j = i - 1; j > 0; j--)
		{
			if (MyMatrix[i][j] > diagvalue)
			{
				if (MyMatrix[i][j + 1] > 0.0 && MyMatrix[i][j - 1] > 0.0) MyMatrix[i][j] = sqrt(MyMatrix[i][j - 1] * MyMatrix[i][j + 1]);
			}
		}
	}
}

void TransposeMatrix(
	long SizeMatrix,
	double** MyMatrix
)
{
	long i, j;
	double TempValue = 0.0;

	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			if (j > i)
			{
				TempValue = MyMatrix[i][j] + 0.0;
				MyMatrix[i][j] = MyMatrix[j][i] + 0.0;
				MyMatrix[i][j] = TempValue;
			}
		}
	}
}

double sum_array(long size, double* myarray)
{
	double s = 0.;
	for (long i = 0; i < size; i++) s += myarray[i];
	return s;
}

long sum_array(long size, long* myarray)
{
	long s = 0;
	for (long i = 0; i < size; i++) s += myarray[i];
	return s;
}

double prod_array(long size, double* myarray)
{
	double s = 1.;
	for (long i = 0; i < size; i++) s *= myarray[i];
	return s;
}

void CummulativeSum_TM(long Size, double** MyMatrix, double** ResultMatrix, long axis = 1)
{
	long i, j, k;
	long NRow = Size;
	long NCol = Size;
	double s = 0.0;
	if (axis == 1)
	{
		for (i = 0; i < NRow; i++)
		{
			for (j = 0; j < NCol; j++)
			{
				ResultMatrix[i][j] = MyMatrix[i][j];
			}
		}

		for (i = 0; i < NRow; i++)
		{
			for (j = 1; j < NCol; j++)
			{
				ResultMatrix[i][j] += ResultMatrix[i][j-1];
			}
		}
	}
	else
	{
		for (i = 0; i < NRow; i++)
		{
			for (j = 0; j < NCol; j++)
			{
				ResultMatrix[i][j] = MyMatrix[i][j];
			}
		}

		for (j = 0; j < NCol; j++)
		{
			for (i = 1; i < NRow; i++)
			{
				ResultMatrix[i][j] += ResultMatrix[i - 1][j];
			}
		}
	}
}

void Calc_StressedTM(
	long SizeMatrix,
	double** TM,
	double CCI,
	double Beta,
	double** ResultMatrix
)
{
	long i, j;
	long zeroflag = 0;
	double s = 0.0;
	double* TempMatrix = (double*)malloc(sizeof(double) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++)
	{
		zeroflag = 0;
		for (j = 0; j < SizeMatrix; j++)
		{
			if (TM[i][j] <= 0.0)
			{
				zeroflag = 1;
				break;
			}
		}

		if (zeroflag == 1)
		{
			for (j = 0; j < SizeMatrix; j++)
			{
				TempMatrix[j] = TM[i][j] + 1.0e-10;
			}
			s = 1.0 + 1.0e-10 * (double)SizeMatrix;
			for (j = 0; j < SizeMatrix; j++)
			{
				TM[i][j] = TempMatrix[j] / s;
			}
		}
	}
	
	double** CummTM = (double**)malloc(sizeof(double*) * SizeMatrix);
	double N_inv_P;
	double BX = CCI * Beta;
	double sqrt_term = sqrt(1.0 - Beta * Beta);
	double NPrev;
	double NCurr;
	double temptest = 0.0;
	for (i = 0; i < SizeMatrix; i++) CummTM[i] = (double*)malloc(sizeof(double) * SizeMatrix);
	CummulativeSum_TM(SizeMatrix, TM, CummTM, 1);

	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			if (j == 0)
			{
				N_inv_P = INV_CDF_N(min(CummTM[i][j], 0.99999999999));
				NCurr = CDF_N((N_inv_P + BX) / sqrt_term);
				ResultMatrix[i][j] = NCurr;
			}
			else
			{
				NPrev = NCurr;
				N_inv_P = INV_CDF_N(min(CummTM[i][j], 0.99999999999));
				NCurr = CDF_N((N_inv_P + BX) / sqrt_term);
				ResultMatrix[i][j] = NCurr - NPrev;
			}
		}
	}
	free(TempMatrix);
	for (i = 0; i < SizeMatrix; i++) free(CummTM[i]);
	free(CummTM);
}

DLLEXPORT(long) Calc_StressedTransitionMatrix(
	double* CCI,						// CCI
	double Beta,						// Gamma(포트폴리오 Copula Correlation)
	long SizeMatrix,					// 정방 매트릭스 한쪽 길이
	double* TM_Reshaped,				// 전이행렬 Reshaped
	double* ResultSTM_Reshaped,			// STM 1
	double* ResultSTM_Reshaped2,		// STM 2
	double* ResultSTM_Reshaped3,		// STM 3
	double* TotalSTMResult,				// STM 1, STM12, STM123
	long TextDumpFlag
)
{
	long i, j, k;

	char CalcFunctionName[] = "Calc_StressedTransitionMatrix";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag == 1)
	{
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "CCI", 3, CCI);
		DumppingTextData(CalcFunctionName, SaveFileName, "Beta", Beta);
		DumppingTextData(CalcFunctionName, SaveFileName, "SizeMatrix", SizeMatrix);
		DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "TM_Reshaped", SizeMatrix, SizeMatrix, TM_Reshaped);
	}

	double** TM = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) TM[i] = (double*)malloc(sizeof(double) * SizeMatrix);
	double** STM = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) STM[i] = (double*)malloc(sizeof(double) * SizeMatrix);
	double** STM2 = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) STM2[i] = (double*)malloc(sizeof(double) * SizeMatrix);
	double** STM3 = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) STM3[i] = (double*)malloc(sizeof(double) * SizeMatrix);

	double** STM12 = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) STM12[i] = (double*)malloc(sizeof(double) * SizeMatrix);
	double** STM123 = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) STM123[i] = (double*)malloc(sizeof(double) * SizeMatrix);


	k = 0;
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			TM[i][j] = TM_Reshaped[k];
			k++;
		}
	}
	Calc_StressedTM(SizeMatrix, TM, CCI[0], Beta, STM);

	k = 0;
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			ResultSTM_Reshaped[k] = STM[i][j];
			k++;
		}
	}

	Calc_StressedTM(SizeMatrix, TM, CCI[1], Beta, STM2);
	k = 0;
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			ResultSTM_Reshaped2[k] = STM2[i][j];
			k++;
		}
	}

	Calc_StressedTM(SizeMatrix, TM, CCI[2], Beta, STM3);
	k = 0;
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			ResultSTM_Reshaped3[k] = STM3[i][j];
			k++;
		}
	}
	long shape[2] = { SizeMatrix, SizeMatrix };
	Dot2dArray(STM, shape, STM2, shape, STM12);
	Dot2dArray(STM12, shape, STM3, shape, STM123);
	k = 0;
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			TotalSTMResult[k] = STM[i][j];
			k++;
		}
	}
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			TotalSTMResult[k] = STM12[i][j];
			k++;
		}
	}
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			TotalSTMResult[k] = STM123[i][j];
			k++;
		}
	}

	for (i = 0; i < SizeMatrix; i++) free(TM[i]);
	free(TM);
	for (i = 0; i < SizeMatrix; i++) free(STM[i]);
	free(STM);
	for (i = 0; i < SizeMatrix; i++) free(STM2[i]);
	free(STM2);
	for (i = 0; i < SizeMatrix; i++) free(STM3[i]);
	free(STM3);
	for (i = 0; i < SizeMatrix; i++) free(STM12[i]);
	free(STM12);
	for (i = 0; i < SizeMatrix; i++) free(STM123[i]);
	free(STM123);
	return 1;
}

void Comprehensive_Adjust_Matrix(
	long SizeMatrix,
	double** MyMatrix,
	double* PD_by_Grade,
	double** ResultMatrix
)
{
	long i, j;
	double s, p;
	for (i = 0; i < SizeMatrix; i++)
	{
		s = sum_array(SizeMatrix, MyMatrix[i]);
		p = PD_by_Grade[i];
		for (j = 0; j < SizeMatrix; j++)
		{
			ResultMatrix[i][j] = MyMatrix[i][j] * (1.0 - p) / s;
		}
	}
}

long Parallel_Condition(
	long CurrentIndex,
	double CurrentValue,
	long PrevIndex,
	double PrevValue,
	long NextIndex,
	double NextValue,
	long NextNextIndex,
	double NextNextValue,
	long direction,
	long SameValueSmoothingFlag
)
{
	long Resultbool = 0;
	if (direction > 0)
	{
		if (PrevIndex < CurrentIndex && NextIndex > CurrentIndex)
		{
			if (SameValueSmoothingFlag == 0)
			{
				// Logic 1
				if (PrevValue > CurrentValue && NextValue > CurrentValue)
				{
					Resultbool = 1;
				}
			}
			else
			{
				// Logic 1
				if (PrevValue > CurrentValue && NextValue >= CurrentValue)
				{
					Resultbool = 1;
				}
			}
		}
	}
	else
	{
		if (PrevIndex > CurrentIndex && NextIndex < CurrentIndex)
		{
			if (SameValueSmoothingFlag == 0)
			{
				if (PrevValue > CurrentValue && NextValue > CurrentValue)
				{
					Resultbool = 1;
				}
			}
			else
			{
				if (PrevValue > CurrentValue && NextValue >= CurrentValue)
				{
					Resultbool = 1;
				}
			}
		}
	}
	return Resultbool;
}

void Smooth_RightDirection(
	long SizeMatrix,
	double** MyMatrix,
	double** MyResultMatrix,
	long SameValueSmoothingFlag,
	long LargeDifferenceAdjustFlag,
	long** AdjustNeeded
)
{
	long i, j, idx, k, n;
	long SmoothFlag = 0;
	long SmoothNearSameValue = 0;
	long CurrentIndex, PrevIndex, NextIndex, NextNextIndex;
	double CurrentValue, PrevValue, NextValue, NextNextValue;
	double InterpValue = 0.;
	double MaxValue = 0.;
	double MinValue = 0.;
	long direction = 0;
	for (i = 0; i < SizeMatrix; i++)
	{
		if (SameValueSmoothingFlag == 0) SmoothNearSameValue = 0;
		else if (LargeDifferenceAdjustFlag == 1 && SameValueSmoothingFlag == 1)
		{
			// Parallel 지나치게 기존과 차이 많이나면 조정
			SmoothNearSameValue = SameValueSmoothingFlag;
			for (n = 0; n < SizeMatrix; n++)
			{
				if (AdjustNeeded[i][n] == 1)
				{
					SmoothNearSameValue = 0;
					break;
				}
			}
		}
		else SmoothNearSameValue = SameValueSmoothingFlag;

		for (j = 0; j < SizeMatrix; j++)
		{
			if (j > i)
			{
				CurrentIndex = j;
				PrevIndex = j;
				CurrentValue = MyMatrix[i][j];
				PrevValue = MyMatrix[i][j];
				direction = 1;
				SmoothFlag = 0;

				// 차기값결정
				NextIndex = CurrentIndex;
				NextValue = MyMatrix[i][j];
				MaxValue = CurrentValue;
				for (idx = CurrentIndex + 1; idx < SizeMatrix; idx++)
				{
					if (SmoothNearSameValue == 0)
					{
						if (MyMatrix[i][idx] > MaxValue)
						{
							NextIndex = idx;
							MaxValue = MyMatrix[i][idx];
						}
					}
					else
					{
						if (MyMatrix[i][idx] >= MaxValue)
						{
							NextIndex = idx;
							MaxValue = MyMatrix[i][idx];
						}
					}
				}
				NextNextIndex = -1;
				NextNextValue = -1.0;
				if (NextIndex != CurrentIndex && MaxValue > 0.)
				{
					NextValue = MaxValue;
					if ((NextIndex + 1) < SizeMatrix)
					{
						// 차차기값결정
						NextNextIndex = NextIndex + 1;
						NextNextValue = MyMatrix[i][NextNextIndex];
					}
				}

				// 직전값 결정
				PrevIndex = CurrentIndex;
				PrevValue = MyMatrix[i][j];

				for (idx = CurrentIndex - 1; idx >= 0; idx--)
				{
					if (SmoothNearSameValue == 0)
					{
						if (MyMatrix[i][idx] >= max(CurrentValue, NextValue) && MyMatrix[i][idx] > 0.)
						{
							PrevIndex = idx;
							PrevValue = MyMatrix[i][idx];
							break;
						}
					}
					else
					{
						if (MyMatrix[i][idx] > max(CurrentValue, NextValue) && MyMatrix[i][idx] > 0.)
						{
							PrevIndex = idx;
							PrevValue = MyMatrix[i][idx];
							break;
						}
					}
				}

				SmoothFlag = Parallel_Condition(CurrentIndex, CurrentValue, PrevIndex, PrevValue, NextIndex, NextValue, NextNextIndex, NextNextValue, direction, SmoothNearSameValue);
				if (SmoothFlag == 1)
				{
					InterpValue = Calc_Geometric_Value(CurrentIndex, PrevIndex, PrevValue, NextIndex, NextValue);
					MyResultMatrix[i][j] = InterpValue;
					if (j + 2 == SizeMatrix - 1)
					{
						if (j - 1 >= 0 && (MyMatrix[i][j] > 0. && MyMatrix[i][j - 1] > MyMatrix[i][j] && MyMatrix[i][j + 1] > MyMatrix[i][j] && MyMatrix[i][j + 2] == 0.))
						{
							MyResultMatrix[i][j] = MyMatrix[i][j];
							MyResultMatrix[i][j + 1] = Calc_Boundary_Value(MyMatrix[i][j], MyMatrix[i][j - 1]);
						}
					}
					else if (j + 3 <= SizeMatrix - 1)
					{
						MaxValue = 0.;
						for (k = j + 3; k < SizeMatrix; k++) MaxValue = max(MaxValue, MyMatrix[i][k]);
						if (j - 1 >= 0 && (MyMatrix[i][j] > 0. && MyMatrix[i][j - 1] > MyMatrix[i][j] && MyMatrix[i][j + 1] > MyMatrix[i][j] && MyMatrix[i][j + 2] == 0. && MaxValue == 0.))
						{
							MyResultMatrix[i][j] = MyMatrix[i][j];
							MyResultMatrix[i][j + 1] = Calc_Boundary_Value(MyMatrix[i][j], MyMatrix[i][j - 1]);
						}
					}
				}
			}
			else if (j < i)
			{
				CurrentIndex = j;
				PrevIndex = j;
				CurrentValue = MyMatrix[i][j];
				PrevValue = MyMatrix[i][j];
				direction = -1;
				SmoothFlag = 0;

				// 차기값결정
				NextIndex = CurrentIndex;
				NextValue = MyMatrix[i][j];
				MaxValue = CurrentValue;
				for (idx = CurrentIndex - 1; idx >= 0; idx--)
				{
					if (SmoothNearSameValue == 0)
					{
						if (MyMatrix[i][idx] > MaxValue)
						{
							NextIndex = idx;
							MaxValue = MyMatrix[i][idx];
						}
					}
					else
					{
						if (MyMatrix[i][idx] >= MaxValue)
						{
							NextIndex = idx;
							MaxValue = MyMatrix[i][idx];
						}
					}
				}

				NextNextIndex = -1;
				NextNextValue = -1.0;
				if (NextIndex != CurrentIndex && MaxValue > 0.)
				{
					NextValue = MaxValue;
					if ((NextIndex) > 0)
					{
						// 차차기값
						NextNextIndex = NextIndex - 1;
						NextNextValue = MyMatrix[i][NextNextIndex];
					}
				}

				// 직전값
				PrevIndex = CurrentIndex;
				PrevValue = MyMatrix[i][j];
				for (idx = CurrentIndex + 1; idx <= i; idx++)
				{
					if (SmoothNearSameValue == 0)
					{
						if (MyMatrix[i][idx] >= max(CurrentValue, NextValue) && MyMatrix[i][idx] > 0.)
						{
							PrevIndex = idx;
							PrevValue = MyMatrix[i][idx];
							break;
						}
					}
					else
					{
						if (MyMatrix[i][idx] >= max(CurrentValue, NextValue) && MyMatrix[i][idx] > 0.)
						{
							PrevIndex = idx;
							PrevValue = MyMatrix[i][idx];
							break;
						}
					}
				}

				SmoothFlag = Parallel_Condition(CurrentIndex, CurrentValue, PrevIndex, PrevValue, NextIndex, NextValue, NextNextIndex, NextNextValue, direction, SmoothNearSameValue);
				if (SmoothFlag == 1)
				{
					InterpValue = Calc_Geometric_Value(CurrentIndex, PrevIndex, PrevValue, NextIndex, NextValue);
					MyResultMatrix[i][j] = InterpValue;
					if (j - 2 == 0 && j + 1 < SizeMatrix)
					{
						if (MyMatrix[i][j] > 0. && MyMatrix[i][j - 1] > MyMatrix[i][j] && MyMatrix[i][j + 1] > MyMatrix[i][j] && MyMatrix[i][j - 2] == 0.)
						{
							MyResultMatrix[i][j] = MyMatrix[i][j];
							MyResultMatrix[i][j - 1] = Calc_Boundary_Value(MyMatrix[i][j], MyMatrix[i][j + 1]);
						}
					}
					else if (j - 3 >= 0 && j + 1 < SizeMatrix)
					{
						MaxValue = 0.;
						for (k = j - 3; k >= 0; k--) MaxValue = max(MaxValue, MyMatrix[i][k]);
						if (MyMatrix[i][j] > 0.0 && MyMatrix[i][j - 1] > MyMatrix[i][j] && MyMatrix[i][j + 1] > MyMatrix[i][j] && MyMatrix[i][j - 2] == 0.0 && MaxValue == 0.0)
						{
							MyResultMatrix[i][j] = MyMatrix[i][j];
							MyResultMatrix[i][j - 1] = Calc_Boundary_Value(MyMatrix[i][j], MyMatrix[i][j + 1]);
						}
					}
				}
			}
		}
	}
}

void Smooth_UpDirection(
	long SizeMatrix,
	double** MyMatrix,
	double** MyResultMatrix,
	long SameValueSmoothingFlag,
	long LargeDifferenceAdjustFlag,
	long** AdjustNeeded
)
{
	long i, j, idx, k, n;
	long SmoothFlag = 0;
	long SmoothNearSameValue = 0;
	long CurrentIndex, PrevIndex, NextIndex, NextNextIndex;
	double CurrentValue, PrevValue, NextValue, NextNextValue;
	double InterpValue = 0.;
	double MaxValue = 0.;
	double MinValue = 0.;
	long direction = 0;
	for (i = SizeMatrix - 1; i >= 0; i--)
	{
		for (j = SizeMatrix - 1; j >= 0; j--)
		{
			if (SameValueSmoothingFlag == 0) SmoothNearSameValue = 0;
			else if (LargeDifferenceAdjustFlag == 1 && SameValueSmoothingFlag == 1)
			{
				// Parallel 지나치게 기존 값과 차이나면 보정
				SmoothNearSameValue = SameValueSmoothingFlag;
				for (n = 0; n < SizeMatrix; n++)
				{
					if (AdjustNeeded[n][j] == 1)
					{
						SmoothNearSameValue = 0;
						break;
					}
				}
			}
			else SmoothNearSameValue = SameValueSmoothingFlag;

			if (j > i)
			{
				CurrentIndex = i;
				PrevIndex = i;
				CurrentValue = MyMatrix[i][j];
				PrevValue = MyMatrix[i][j];
				direction = -1;
				SmoothFlag = 0;
				// 차기값 결정
				NextIndex = CurrentIndex;
				NextValue = MyMatrix[i][j];
				MaxValue = CurrentValue;
				for (idx = CurrentIndex - 1; idx >= 0; idx--)
				{
					if (SmoothNearSameValue == 0)
					{
						if (MyMatrix[idx][j] > MaxValue)
						{
							NextIndex = idx;
							MaxValue = MyMatrix[idx][j];
						}
					}
					else
					{
						if (MyMatrix[idx][j] >= MaxValue)
						{
							NextIndex = idx;
							MaxValue = MyMatrix[idx][j];
						}
					}
				}

				NextNextIndex = -1;
				NextNextValue = -1.0;
				if (NextIndex != CurrentIndex && MaxValue > 0.0)
				{
					NextValue = MaxValue;
					if ((NextIndex - 1) > 0)
					{
						// 차차기값결정
						NextNextIndex = NextIndex - 1;
						NextNextValue = MyMatrix[NextNextIndex][j];
					}
				}

				// 직전값 결정
				PrevIndex = CurrentIndex;
				PrevValue = MyMatrix[i][j];
				for (idx = CurrentIndex + 1; idx <= j; idx++)
				{
					if (SmoothNearSameValue == 0)
					{
						if (MyMatrix[idx][j] >= max(CurrentValue, NextValue) && MyMatrix[idx][j] > 0.)
						{
							PrevIndex = idx;
							PrevValue = MyMatrix[idx][j];
							break;
						}
					}
					else
					{
						if (MyMatrix[idx][j] >= max(CurrentValue, NextValue ) && MyMatrix[idx][j] > 0.)
						{
							PrevIndex = idx;
							PrevValue = MyMatrix[idx][j];
							break;
						}
					}
				}

				SmoothFlag = Parallel_Condition(CurrentIndex, CurrentValue, PrevIndex, PrevValue, NextIndex, NextValue, NextNextIndex, NextNextValue, direction, SmoothNearSameValue);
				if (SmoothFlag == 1)
				{
					InterpValue = Calc_Geometric_Value(CurrentIndex, PrevIndex, PrevValue, NextIndex, NextValue);
					MyResultMatrix[i][j] = InterpValue;
					if (i - 2 == 0 && i + 1 < SizeMatrix)
					{
						if (MyMatrix[i][j] > 0. && MyMatrix[i - 1][j] > MyMatrix[i][j] && MyMatrix[i + 1][j] > MyMatrix[i][j] && MyMatrix[i - 2][j] == 0.)
						{
							MyResultMatrix[i][j] = MyMatrix[i][j];
							MyResultMatrix[i - 1][j] = Calc_Boundary_Value(MyMatrix[i][j], MyMatrix[i + 1][j]);
						}
					}
					else if (i - 3 >= 0 && i + 1 < SizeMatrix)
					{
						MaxValue = 0.;
						for (k = j - 3; k >= 0; k--) MaxValue = max(MaxValue, MyMatrix[k][j]);
						if (MyMatrix[i][j] > 0. && MyMatrix[i - 1][j] > MyMatrix[i][j] && MyMatrix[i + 1][j] > MyMatrix[i][j] && MyMatrix[i - 2][j] == 0. && MaxValue == 0.)
						{
							MyResultMatrix[i][j] = MyMatrix[i][j];
							MyResultMatrix[i - 1][j] = Calc_Boundary_Value(MyMatrix[i][j], MyMatrix[i + 1][j]);
						}
					}
				}
			}
			else if (j < i)
			{
				CurrentIndex = i;
				PrevIndex = i;
				CurrentValue = MyMatrix[i][j];
				PrevValue = MyMatrix[i][j];
				direction = +1;
				SmoothFlag = 0;
				// 차기값 결정
				NextIndex = CurrentIndex;
				NextValue = MyMatrix[i][j];
				MaxValue = CurrentValue;

				for (idx = CurrentIndex + 1; idx < SizeMatrix; idx++)
				{
					if (SmoothNearSameValue == 0)
					{
						if (MyMatrix[idx][j] > MaxValue)
						{
							NextIndex = idx;
							MaxValue = MyMatrix[idx][j];
						}
					}
					else
					{
						if (MyMatrix[idx][j] > MaxValue)
						{
							NextIndex = idx;
							MaxValue = MyMatrix[idx][j];
						}
					}
				}

				NextNextIndex = -1;
				NextNextValue = -1.0;
				if (NextIndex != CurrentIndex && MaxValue > 0.)
				{
					NextValue = MaxValue;
					if ((NextIndex + 1) < SizeMatrix)
					{
						// 차차기값
						NextNextIndex = NextIndex + 1;
						NextNextValue = MyMatrix[NextNextIndex][j];
					}
				}

				// 직전값 결정
				PrevIndex = CurrentIndex;
				PrevValue = MyMatrix[i][j];

				for (idx = CurrentIndex - 1; idx >= j; idx--)
				{
					if (SmoothNearSameValue == 0)
					{
						if (MyMatrix[idx][j] >= max(CurrentValue, NextValue) && MyMatrix[idx][j] > 0.)
						{
							PrevIndex = idx;;
							PrevValue = MyMatrix[idx][j];
							break;
						}
					}
					else
					{
						if (MyMatrix[idx][j] >= max(CurrentValue, NextValue) && MyMatrix[idx][j] > 0.)
						{
							PrevIndex = idx;;
							PrevValue = MyMatrix[idx][j];
							break;
						}

					}
				}

				SmoothFlag = Parallel_Condition(CurrentIndex, CurrentValue, PrevIndex, PrevValue, NextIndex, NextValue, NextNextIndex, NextNextValue, direction, SmoothNearSameValue);
				if (SmoothFlag == 1)
				{
					InterpValue = Calc_Geometric_Value(CurrentIndex, PrevIndex, PrevValue, NextIndex, NextValue);
					MyResultMatrix[i][j] = InterpValue;
					if (i + 2 == SizeMatrix - 1 && i - 1 >= 0)
					{
						if (MyMatrix[i][j] > 0. && MyMatrix[i + 1][j] > MyMatrix[i][j] && MyMatrix[i - 1][j] > MyMatrix[i][j] && MyMatrix[i + 2][j] == 0.)
						{
							MyResultMatrix[i][j] = MyMatrix[i][j];
							MyResultMatrix[i + 1][j] = Calc_Boundary_Value(MyMatrix[i][j], MyMatrix[i - 1][j]);
						}
					}
					else if (i + 3 < SizeMatrix && i-1 >=0)
					{
						MaxValue = 0.;
						for (k = i + 3; k < SizeMatrix; k++) MaxValue = max(MaxValue, MyMatrix[k][j]);
						if (MyMatrix[i][j] > 0. && MyMatrix[i + 1][j] > MyMatrix[i][j] && MyMatrix[i - 1][j] > MyMatrix[i][j] && MyMatrix[i + 2][j] == 0. && MaxValue == 0.)
						{
							MyResultMatrix[i][j] = MyMatrix[i][j];
							MyResultMatrix[i + 1][j] = Calc_Boundary_Value(MyMatrix[i][j], MyMatrix[i - 1][j]);
						}

					}
				}
			}
		}
	}
}

// 가로 평활화
DLLEXPORT(long) Parallel_Smoothing_Matrix(
	long SizeMatrix,						// 전이행렬 한쪽 사이즈
	double* MatrixReshaped,					// 전이행렬 Reshaped
	double* ResultMatrixReshaped,			// Smoothing 후 전이행렬 Output
	double* ResultMatrixSumAdj,				// Smoothing and 합계보정 후 Output
	long SameValueSmoothingFlag,			// 양 옆 같은값도 보정
	long LargeDifferenceAdjustFlag,			// 기존 매트릭스보다 너무 차이가 크면 보정
	long AdjustIfLargeThenDiag,				// Diagonal 보다 큰 값이 있으면 보정
	double* PD,								// PD
	long TextDumpFlag
)
{
	char CalcFunctionName[] = "Parallel_Smoothing_Matrix";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag == 1)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "SizeMatrix", SizeMatrix);
		DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "MatrixReshaped", SizeMatrix, SizeMatrix, MatrixReshaped);
		DumppingTextData(CalcFunctionName, SaveFileName, "SameValueSmoothingFlag", SameValueSmoothingFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "LargeDifferenceAdjustFlag", LargeDifferenceAdjustFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "CAdjustIfLargeThenDiagCI", AdjustIfLargeThenDiag);
	}

	long i, j, k;
	long ResultCode = 0;
	double** MyMatrix = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) MyMatrix[i] = (double*)malloc(sizeof(double) * SizeMatrix);

	double** MyResultMatrix = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) MyResultMatrix[i] = (double*)malloc(sizeof(double) * SizeMatrix);

	double** ProbMatrix_Adj = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) ProbMatrix_Adj[i] = (double*)malloc(sizeof(double) * SizeMatrix);

	long** AdjustNeeded = (long**)malloc(sizeof(long*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) AdjustNeeded[i] = (long*)malloc(sizeof(long) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) for (j = 0; j < SizeMatrix; j++) AdjustNeeded[i][j] = 0;

	k = 0; 
	for (i = 0 ; i < SizeMatrix; i++)
		for (j = 0; j < SizeMatrix; j++)
		{
			MyMatrix[i][j] = MatrixReshaped[k];
			MyResultMatrix[i][j] = MatrixReshaped[k];
			k++;
		}

	if (AdjustIfLargeThenDiag == 1)
	{
		Adjust_DiagonalMax(SizeMatrix, MyMatrix);
		for (i = 0; i < SizeMatrix; i++) for (j = 0; j < SizeMatrix; j++) MyResultMatrix[i][j] = MyMatrix[i][j];
	}

	Smooth_RightDirection(SizeMatrix, MyMatrix, MyResultMatrix, SameValueSmoothingFlag, 0, AdjustNeeded);
	Comprehensive_Adjust_Matrix(SizeMatrix, MyResultMatrix, PD, ProbMatrix_Adj);

	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			if ((fabs(ProbMatrix_Adj[i][j] - MyMatrix[i][j]) > 0.1) && MyMatrix[i][j] > 0. && i != j)
			{
				AdjustNeeded[i][j] = 1;
			}
		}
	}

	if (LargeDifferenceAdjustFlag * SameValueSmoothingFlag == 1)
	{
		// 초기화
		for (i = 0; i < SizeMatrix; i++) for (j = 0; j < SizeMatrix; j++) MyResultMatrix[i][j] = MyMatrix[i][j];
		Smooth_RightDirection(SizeMatrix, MyMatrix, MyResultMatrix, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustNeeded);
		Comprehensive_Adjust_Matrix(SizeMatrix, MyResultMatrix, PD, ProbMatrix_Adj);
	}

	k = 0;
	for (i = 0; i < SizeMatrix; i++)
		for (j = 0; j < SizeMatrix; j++)
		{
			ResultMatrixReshaped[k] = MyResultMatrix[i][j];
			ResultMatrixSumAdj[k] = ProbMatrix_Adj[i][j];
			k++;
		}

	for (i = 0; i < SizeMatrix; i++) free(MyMatrix[i]);
	free(MyMatrix);

	for (i = 0; i < SizeMatrix; i++) free(MyResultMatrix[i]);
	free(MyResultMatrix);

	for (i = 0; i < SizeMatrix; i++) free(ProbMatrix_Adj[i]);
	free(ProbMatrix_Adj);

	for (i = 0; i < SizeMatrix; i++) free(AdjustNeeded[i]);
	free(AdjustNeeded);
	return ResultCode;
}

DLLEXPORT(long) Vertical_Smoothing_Matrix(
	long SizeMatrix,						// 전이행렬 한쪽 사이즈
	double* MatrixReshaped,					// 전이행렬 Reshaped
	double* ResultMatrixReshaped,			// Smoothing 후 전이행렬 Output
	double* ResultMatrixSumAdj,				// Smoothing and 합계보정 후 Output
	long SameValueSmoothingFlag,			// 양 옆 같은값도 보정
	long LargeDifferenceAdjustFlag,			// 기존 매트릭스보다 너무 차이가 크면 보정
	long AdjustIfLargeThenDiag,				// Diagonal 보다 큰 값이 있으면 보정
	double* PD,								// PD
	long TextDumpFlag
)
{
	long i, j, k;
	long ResultCode = 0;

	char CalcFunctionName[] = "Vertical_Smoothing_Matrix";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag == 1)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "SizeMatrix", SizeMatrix);
		DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "MatrixReshaped", SizeMatrix, SizeMatrix, MatrixReshaped);
		DumppingTextData(CalcFunctionName, SaveFileName, "SameValueSmoothingFlag", SameValueSmoothingFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "LargeDifferenceAdjustFlag", LargeDifferenceAdjustFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "CAdjustIfLargeThenDiagCI", AdjustIfLargeThenDiag);
	}

	double** MyMatrix = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) MyMatrix[i] = (double*)malloc(sizeof(double) * SizeMatrix);

	double** MyResultMatrix = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) MyResultMatrix[i] = (double*)malloc(sizeof(double) * SizeMatrix);

	double** ProbMatrix_Adj = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) ProbMatrix_Adj[i] = (double*)malloc(sizeof(double) * SizeMatrix);

	long** AdjustNeeded = (long**)malloc(sizeof(long*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) AdjustNeeded[i] = (long*)malloc(sizeof(long) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) for (j = 0; j < SizeMatrix; j++) AdjustNeeded[i][j] = 0;

	k = 0;
	for (i = 0; i < SizeMatrix; i++)
		for (j = 0; j < SizeMatrix; j++)
		{
			MyMatrix[i][j] = MatrixReshaped[k];
			MyResultMatrix[i][j] = MatrixReshaped[k];
			k++;
		}

	if (AdjustIfLargeThenDiag == 1)
	{
		Adjust_DiagonalMax(SizeMatrix, MyMatrix);
		for (i = 0; i < SizeMatrix; i++) for (j = 0; j < SizeMatrix; j++) MyResultMatrix[i][j] = MyMatrix[i][j];
	}

	Smooth_UpDirection(SizeMatrix, MyMatrix, MyResultMatrix, SameValueSmoothingFlag, 0, AdjustNeeded);
	Comprehensive_Adjust_Matrix(SizeMatrix, MyResultMatrix, PD, ProbMatrix_Adj);

	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			if ((fabs(ProbMatrix_Adj[i][j] - MyMatrix[i][j]) > 0.1) && MyMatrix[i][j] > 0. && i != j)
			{
				AdjustNeeded[i][j] = 1;
			}
		}
	}

	if (LargeDifferenceAdjustFlag * SameValueSmoothingFlag == 1)
	{
		// 초기화
		for (i = 0; i < SizeMatrix; i++) for (j = 0; j < SizeMatrix; j++) MyResultMatrix[i][j] = MyMatrix[i][j];
		Smooth_UpDirection(SizeMatrix, MyMatrix, MyResultMatrix, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustNeeded);
		Comprehensive_Adjust_Matrix(SizeMatrix, MyResultMatrix, PD, ProbMatrix_Adj);
	}

	k = 0;
	for (i = 0; i < SizeMatrix; i++)
		for (j = 0; j < SizeMatrix; j++)
		{
			ResultMatrixReshaped[k] = MyResultMatrix[i][j];
			ResultMatrixSumAdj[k] = ProbMatrix_Adj[i][j];
			k++;
		}

	for (i = 0; i < SizeMatrix; i++) free(MyMatrix[i]);
	free(MyMatrix);

	for (i = 0; i < SizeMatrix; i++) free(MyResultMatrix[i]);
	free(MyResultMatrix);

	for (i = 0; i < SizeMatrix; i++) free(ProbMatrix_Adj[i]);
	free(ProbMatrix_Adj);

	for (i = 0; i < SizeMatrix; i++) free(AdjustNeeded[i]);
	free(AdjustNeeded);
	return ResultCode;
}

DLLEXPORT(long) Smoothing_Matrix(
	long SizeMatrix,						// 전이행렬 한쪽 사이즈
	double* MatrixReshaped,					// 전이행렬 Reshaped
	double* ResultMatrixReshaped,			// Smoothing 후 전이행렬 Output
	double* ResultMatrixSumAdj,				// Smoothing and 합계보정 후 Output
	long SameValueSmoothingFlag,			// 양 옆 같은값도 보정
	long LargeDifferenceAdjustFlag,			// 기존 매트릭스보다 너무 차이가 크면 보정
	long AdjustIfLargeThenDiag,				// Diagonal 보다 큰 값이 있으면 보정
	double* PD,								// PD
	long TextDumpFlag
)
{
	long ResultCode = 1;

	char CalcFunctionName[] = "Smoothing_Matrix";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag == 1)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "SizeMatrix", SizeMatrix);
		DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "MatrixReshaped", SizeMatrix, SizeMatrix, MatrixReshaped);
		DumppingTextData(CalcFunctionName, SaveFileName, "SameValueSmoothingFlag", SameValueSmoothingFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "LargeDifferenceAdjustFlag", LargeDifferenceAdjustFlag);
		DumppingTextData(CalcFunctionName, SaveFileName, "CAdjustIfLargeThenDiagCI", AdjustIfLargeThenDiag);
	}

	double* Result1 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);
	double* Result2 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);
	double* Result3 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);
	double* Result4 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);
	double* Result5 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);

	ResultCode *= Parallel_Smoothing_Matrix(SizeMatrix, MatrixReshaped, Result1, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD,0);
	ResultCode *= Vertical_Smoothing_Matrix(SizeMatrix, Result1, Result2, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD,0);
	ResultCode *= Parallel_Smoothing_Matrix(SizeMatrix, Result2, Result3, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD,0);
	ResultCode *= Vertical_Smoothing_Matrix(SizeMatrix, Result3, Result4, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD,0);
	ResultCode *= Parallel_Smoothing_Matrix(SizeMatrix, Result4, Result5, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD,0);
	ResultCode *= Vertical_Smoothing_Matrix(SizeMatrix, Result5, ResultMatrixReshaped, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD,0);

	free(Result1);
	free(Result2);
	free(Result3);
	free(Result4);
	free(Result5);
	return ResultCode;
}

DLLEXPORT(long) Get_MasterPD(
	long NRate,
	double* InputPD,
	double* MinPD,
	double* ResultPD
)
{
	long i, j;
	long Calculation_Unit_Flag = 0;
	for (i = 0; i < NRate; i++)
	{
		if (InputPD[i] > 1.0)
		{
			Calculation_Unit_Flag = 1;
			break;
		}
	}
	double shiftamt = 0.;
	double PD = 0.;

	double MaxBound = 1.0;
	if (Calculation_Unit_Flag == 1) MaxBound = 100.0;

	bubble_sort(InputPD, NRate);

	for (i = 0; i < NRate; i++)
	{
		PD = min(MaxBound, max(InputPD[i] + shiftamt, MinPD[i]));
		if (InputPD[i] + shiftamt <= MinPD[i]) shiftamt += MinPD[i] - (InputPD[i] + shiftamt);
		ResultPD[i] = PD;
	}

	return min(NRate, 1);
}

DLLEXPORT(long) TransitionNum_To_TransitionProb(
	long NRate,
	double* TransitionNumberReshaped,
	double* TransitionProbReshaped,
	double* MasterPD
)
{
	long i, j, k;
	long ResultCode = 0;
	long Calculation_Unit_Flag = 0;
	for (i = 0; i < NRate; i++)
	{
		if (MasterPD[i] > 1.0)
		{
			Calculation_Unit_Flag = 1;
			break;
		}
	}

	double** MyMatrix = (double**)malloc(sizeof(double*) * NRate);
	for (i = 0; i < NRate; i++) MyMatrix[i] = (double*)malloc(sizeof(double) * NRate);

	double* TotalNum = (double*)malloc(sizeof(double) * NRate);

	k = 0;
	for (i = 0 ; i < NRate; i++)
		for (j = 0; j < NRate; j++)
		{
			MyMatrix[i][j] = TransitionNumberReshaped[k];
			k++;
		}

	for (i = 0; i < NRate; i++) TotalNum[i] = sum_array(NRate, MyMatrix[i]);

	k = 0;
	k = 0;
	for (i = 0; i < NRate; i++)
		for (j = 0; j < NRate; j++)
		{
			if (Calculation_Unit_Flag == 1) TransitionProbReshaped[k] = (100.0 - MasterPD[i]) / 100.0 * ((double)MyMatrix[i][j]) / ((double)TotalNum[i]);
			else TransitionProbReshaped[k] = (1.0 - MasterPD[i]) * ((double)MyMatrix[i][j]) / ((double)TotalNum[i]);
			k++;
		}

	for (i = 0; i < NRate; i++) free(MyMatrix[i]);
	free(MyMatrix);
	free(TotalNum);
	return ResultCode;
}

DLLEXPORT(long) Get_LifeTimePD(
	long NRate,								// 신용등급개수
	double* InputPD,						// 인풋PD
	double* MinPD,							// 최소PD
	double* ResultPD,						// Output1 : 결과PD
	double* TransitionNumberReshaped,		// 전이개수 또는 전이행렬
	double* TransitionProbReshaped,			// Output2 : 조정전이행렬
	long NTermPD,							// 결과로 산출할 PD Term 개수
	double* CummulativePD,					// Output3 : 연간 누적PD
	double* ForwardPD,						// Output4 : 연간 Forward 기간PD
	double* MarginalPD,						// Output5 : 한계PD
	double* QuarterlyMarginalPD,			// Output6 : 분기 한계PD
	double* QuarterlyCummPD,				// Output7 : 분기 누적PD
	long TextDumpFlag						// 텍스트덤프 출력여부
)
{
	long i, j, k, n, ResultCode = 0;

	char CalcFunctionName[] = "Get_LifeTimePD";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag == 1)
	{
		DumppingTextData(CalcFunctionName, SaveFileName, "NRate", NRate);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "InputPD", NRate, InputPD);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "MinPD", NRate, MinPD);
		DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "MatrixReshaped", NRate, NRate, TransitionNumberReshaped);
	}

	double s = 0.;
	ResultCode = Get_MasterPD(NRate, InputPD, MinPD, ResultPD);

	double* MasterPD = ResultPD;
	ResultCode = TransitionNum_To_TransitionProb(NRate, TransitionNumberReshaped, TransitionProbReshaped, MasterPD);
	long Calculation_Unit_Flag = 0;
	for (i = 0; i < NRate; i++)
	{
		if (MasterPD[i] > 1.0)
		{
			Calculation_Unit_Flag = 1;
			break;
		}
	}

	double** TransitionProb = (double**)malloc(sizeof(double*) * (NRate + 1));
	for (i = 0; i < NRate + 1; i++) TransitionProb[i] = (double*)malloc(sizeof(double) * (NRate + 1));

	k = 0;
	for (i = 0; i < NRate; i++)
		for (j = 0; j < NRate; j++)
		{
			TransitionProb[i][j] = TransitionProbReshaped[k];
			k++;
		}

	for (i = 0; i < NRate; i++) TransitionProb[NRate][i] = 0.0;
	for (i = 0; i < NRate; i++) TransitionProb[i][NRate] = MasterPD[i];
	TransitionProb[NRate][NRate] = 1.0;

	double** AA = (double**)malloc(sizeof(double*) * (NRate + 1));
	for (i = 0; i < NRate + 1; i++) AA[i] = (double*)malloc(sizeof(double) * (NRate + 1));
	for (i = 0; i < NRate + 1; i++) for (j = 0; j < NRate + 1; j++) AA[i][j] = TransitionProb[i][j];

	long MyShape[2] = { NRate + 1, NRate + 1 };
	double* ResultTM;
	double** CummulativePDMat = (double**)malloc(sizeof(double*) * NRate);
	double** ForwardPDMat = (double**)malloc(sizeof(double*) * NRate);
	double** MarginalPDMat = (double**)malloc(sizeof(double*) * NRate);

	for (i = 0; i < NRate; i++)
	{
		CummulativePDMat[i] = CummulativePD + i * NTermPD;
		ForwardPDMat[i] = ForwardPD + i * NTermPD;
		MarginalPDMat[i] = MarginalPD + i * NTermPD;
	}

	for (i = 0; i < NRate; i++)
	{
		CummulativePDMat[i][0] = MasterPD[i];
		ForwardPDMat[i][0] = MasterPD[i];
		MarginalPDMat[i][0] = MasterPD[i];
	}

	double Q_Prev, Q_Curr;
	for (n = 1; n < 10; n++ )
	{
		ResultTM = TransitionProbReshaped + n * NRate * NRate;
		double** MyMatrix = Dot2dArray(AA, MyShape, TransitionProb, MyShape);
		for (i = 0; i < NRate + 1; i++) for (j = 0; j < NRate + 1; j++) TransitionProb[i][j] = MyMatrix[i][j];

		k = 0;
		for (i = 0; i < NRate; i++)
		{
			CummulativePDMat[i][n] = MyMatrix[i][NRate];
			if (Calculation_Unit_Flag == 1)
			{
				Q_Prev = 1.0 - CummulativePDMat[i][n-1] / 100.0;
				Q_Curr = 1.0 - CummulativePDMat[i][n] / 100.0;
				if (CummulativePDMat[i][n - 1] == 100.0) ForwardPDMat[i][n] = 0.0;
				else ForwardPDMat[i][n] = 100.0 * (1.0 - Q_Curr / Q_Prev);
				MarginalPDMat[i][n] = 100.0 * (1.0 - CummulativePDMat[i][n - 1] / 100.0) * ForwardPDMat[i][n] / 100.0;
			}
			else
			{
				Q_Prev = 1.0 - CummulativePDMat[i][n - 1];
				Q_Curr = 1.0 - CummulativePDMat[i][n];
				if (CummulativePDMat[i][n - 1] == 1.0) ForwardPDMat[i][n] = 0.0;
				else ForwardPDMat[i][n] = (1.0 - Q_Curr / Q_Prev);
				MarginalPDMat[i][n] = (1.0 - CummulativePDMat[i][n - 1]) * ForwardPDMat[i][n];
			}

			for (j = 0; j < NRate; j++)
			{
				ResultTM[k] = TransitionProb[i][j];
				k++;
			}
		}

		for (i = 0; i < NRate + 1; i++) free(MyMatrix[i]);
		free(MyMatrix);
	}

	for (n = 10; n < NTermPD; n++)
	{
		for (i = 0; i < NRate; i++)
		{
			ForwardPDMat[i][n] = ForwardPDMat[i][n - 1];
			if (Calculation_Unit_Flag == 1) MarginalPDMat[i][n] = 100.0 * ((1.0 - CummulativePDMat[i][n - 1] / 100.0) * ForwardPDMat[i][n] / 100.0);
			else MarginalPDMat[i][n] = (1.0 - CummulativePDMat[i][n - 1]) * ForwardPDMat[i][n];
			CummulativePDMat[i][n] = sum_array(n + 1, MarginalPDMat[i]);
		}
	}


	double* MarginalSurv = (double*)malloc(sizeof(double) * NTermPD * 4);
	double Q_Q = 1.0, forward_pd_Q, marginal_pd_Q, cumprodvalue;

	k = 0;
	for (i = 0; i < NRate; i++)
	{
		for (j = 0; j < NTermPD; j++)
		{
			for (n = 0; n < 4; n++)
			{
				if (Calculation_Unit_Flag == 1)
				{
					forward_pd_Q = 100.0 * (1.0 - pow(1.0 - ForwardPDMat[i][j] / 100.0, 0.25));
					MarginalSurv[4 * j + n] = 1.0 - forward_pd_Q / 100.0;
					QuarterlyMarginalPD[k] = prod_array(4 * j + n, MarginalSurv) * forward_pd_Q;
					QuarterlyCummPD[k] = min(100.0, sum_array(4 * j + n + 1, QuarterlyMarginalPD + i * NTermPD * 4));
				}
				else
				{
					forward_pd_Q = (1.0 - pow(1.0 - ForwardPDMat[i][j] , 0.25));
					MarginalSurv[4 * j + n] = 1.0 - forward_pd_Q ;
					QuarterlyMarginalPD[k] = prod_array(4 * j + n, MarginalSurv) * forward_pd_Q;
					QuarterlyCummPD[k] = min(1.0, sum_array(4 * j + n + 1, QuarterlyMarginalPD + i * NTermPD * 4));
				}
				k += 1;
			}
		}
	}

	for (i = 0; i < NRate + 1; i++) free(TransitionProb[i]);
	free(TransitionProb);
	for (i = 0; i < NRate + 1; i++) free(AA[i]);
	free(AA);
	free(CummulativePDMat);
	free(ForwardPDMat);
	free(MarginalPDMat);
	free(MarginalSurv);
	return ResultCode;
}

double probtologit(double p)
{
	return log(p / (1 - p));
}

double logittoprob(double logit)
{
	return 1.0 / (1.0 + exp(-logit));
}

void TempFuncOLS_ForPD(double** x, double* y, long num_data, long nvariables, long NeweyWestLag, double* ResultArray)
{
	long i;
	long nbeta = nvariables + 1;
	long n = nbeta;
	OLS OLSClass(x, y, num_data, nvariables, NeweyWestLag);
	for (i = 0; i < nbeta; i++) ResultArray[i] = OLSClass.beta[i];
	for (i = 0; i < nbeta; i++) ResultArray[i + nbeta] = OLSClass.std_B[i];
	for (i = 0; i < nbeta; i++) ResultArray[i + 2 * nbeta] = OLSClass.t_value[i];
	ResultArray[3 * nbeta] = OLSClass.rsquared;
	ResultArray[3 * nbeta + 1] = OLSClass.rsquared_adj;
	ResultArray[3 * n + 2] = OLSClass.resid_std;
	ResultArray[n * 3 + 3] = OLSClass.loglikelihood;
	ResultArray[n * 3 + 4] = OLSClass.Df_model;
	ResultArray[n * 3 + 5] = OLSClass.Df_res;
	ResultArray[n * 3 + 6] = OLSClass.Fstatistic;
	ResultArray[n * 3 + 7] = OLSClass.AIC;
	ResultArray[n * 3 + 8] = OLSClass.BIC;
	ResultArray[n * 3 + 9] = OLSClass.durbin_watson;
	ResultArray[n * 3 + 10] = OLSClass.sig;
	for (i = 0; i < num_data; i++) ResultArray[n * 3 + 11 + i] = OLSClass.estimated[i];
	for (i = 0; i < num_data; i++) ResultArray[n * 3 + 11 + num_data + i] = OLSClass.resid[i];
	ResultArray[n * 3 + 11 + 2 * num_data] = OLSClass.Skew;
	ResultArray[n * 3 + 11 + 2 * num_data + 1] = OLSClass.Kurt;
	ResultArray[n * 3 + 11 + 2 * num_data + 2] = OLSClass.JB;
	ResultArray[n * 3 + 11 + 2 * num_data + 3] = OLSClass.centered_tss;
	for (i = 0; i < nbeta; i++) ResultArray[n * 3 + 11 + 2 * num_data + 3 + i] = OLSClass.p[i];
	for (i = 0; i < nbeta; i++) ResultArray[n * 3 + 11 + 2 * num_data + 3 + nbeta + i] = OLSClass.std_B_NeweyWest[i];
	for (i = 0; i < nbeta; i++) ResultArray[n * 3 + 11 + 2 * num_data + 3 + 2 * nbeta + i] = OLSClass.p_neweywest[i];
}

DLLEXPORT(long) ProbitMeanStd(long NData, double* Data, double* Result)
{
	long i, j;
	long n = 0;
	long probflag = 0;
	for (i = 0; i < NData; i++)
	{
		if (Data[i] < 0.0)
		{
			n = 0;
			break;
		}
		if (Data[i] > 0.0 && Data[i] < 1.0) n += 1;
	}

	if (n == NData)
	{
		probflag = 1;
	}
	else
	{
		for (i = 0 ; i < NData; i++) Data[i] = logittoprob(Data[i]);
	}

	double mu = 0.0;
	double std = 0.0;
	double var = 0.0;
	for (i = 0; i < NData; i++) Data[i] = INV_CDF_N(Data[i]);
	for (i = 0; i < NData; i++) mu += Data[i]/(double)NData;
	for (i = 0; i < NData; i++) var += (Data[i] - mu) * (Data[i] - mu) / (double)NData;
	std = sqrt(var);
	Result[0] = mu;
	Result[1] = std;
	Result[2] = sqrt(var / (1 + var));
	return 1;
}

DLLEXPORT(long) OLS_Estimate_ForPD(
	double* x_reshape,				// X변수 Reshaped
	double* y,						// 종속변수
	long ndata,						// 데이터개수
	long nvariables,				// 변수개수
	long NeweyWestLag,				// HAC Lag
	double* ResultArray,			// [0~(nvar+1)-1] beta, [(nvar+1)~2(nvar+1)-1]std, [2(nvar+1)~3(nvar+1)-1]
	long TextDumpFlag
	)
{
	long i, j;

	char CalcFunctionName[] = "OLS_Estimate_ForPD";
	char SaveFileName[100];

	get_filenameYYYYMMDD(SaveFileName, 100, CalcFunctionName);
	if (TextDumpFlag == 1)
	{
		DumppingTextDataMatrix(CalcFunctionName, SaveFileName, "x_reshape", ndata, nvariables, x_reshape);
		DumppingTextDataArray(CalcFunctionName, SaveFileName, "y", ndata, y);
		DumppingTextData(CalcFunctionName, SaveFileName, "ndata", ndata);
		DumppingTextData(CalcFunctionName, SaveFileName, "nvariables", nvariables);
		DumppingTextData(CalcFunctionName, SaveFileName, "NeweyWestLag", NeweyWestLag);
	}

	long n = 0;
	for (i = 0; i < ndata; i++)
	{
		if (y[i] < 0.0)
		{
			n = 0;
			break;
		}
		if (y[i] > 0.0 && y[i] < 1.0) n += 1;
	}
	
	if (n == ndata)
	{
		for (i = 0; i < ndata; i++)
		{
			y[i] = probtologit(y[i]);
		}
	}

	long shape[2] = { ndata, nvariables };
	double** x_before_const = DataReshape(x_reshape, shape);
	TempFuncOLS_ForPD(x_before_const, y, ndata, nvariables, NeweyWestLag, ResultArray);

	for (i = 0; i < ndata; i++) free(x_before_const[i]);
	free(x_before_const);

	//_CrtDumpMemoryLeaks();
	return 1;
}

DLLEXPORT(long) CalcEstimatedScenarioPD(long NVariables, long NData, double* XDataReshaped, double* Betas, double probitmean, double probitstd, double* Result)
{
	long i, j, k;
	double s, p, cci, probit;
	double** Data = (double**)malloc(sizeof(double*) * NData);
	for (i = 0; i < NData; i++) Data[i] = (double*)malloc(sizeof(double) * NVariables);
	k = 0;
	for (i = 0; i < NData; i++)
	{
		for (j = 0; j < NVariables; j++)
		{
			Data[i][j] = XDataReshaped[k];
			k += 1;
		}
	}

	for (i = 0; i < NData; i++)
	{
		s = Betas[0];
		for (j = 0; j < NVariables; j++)
		{
			s += Betas[j + 1] * Data[i][j];
		}
		p = logittoprob(s);
		probit = INV_CDF_N(p);
		cci = -(probit - probitmean) / probitstd;
		Result[i] = s;
		Result[i + NData] = p;
		Result[i + NData * 2] = cci;
	}

	for (i = 0; i < NData; i++) free(Data[i]);
	free(Data);
	return 1;
}