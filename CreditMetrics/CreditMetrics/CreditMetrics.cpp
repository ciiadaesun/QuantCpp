#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "Util.h"

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
	double CCI,
	double Beta,
	long SizeMatrix,
	double* TM_Reshaped,
	double* ResultSTM_Reshaped
)
{
	long i, j, k;
	double** TM = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) TM[i] = (double*)malloc(sizeof(double) * SizeMatrix);
	double** STM = (double**)malloc(sizeof(double*) * SizeMatrix);
	for (i = 0; i < SizeMatrix; i++) STM[i] = (double*)malloc(sizeof(double) * SizeMatrix);

	k = 0;
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			TM[i][j] = TM_Reshaped[k];
			k++;
		}
	}
	Calc_StressedTM(SizeMatrix, TM, CCI, Beta, STM);

	k = 0;
	for (i = 0; i < SizeMatrix; i++)
	{
		for (j = 0; j < SizeMatrix; j++)
		{
			ResultSTM_Reshaped[k] = STM[i][j];
			k++;
		}
	}

	for (i = 0; i < SizeMatrix; i++) free(TM[i]);
	free(TM);
	for (i = 0; i < SizeMatrix; i++) free(STM[i]);
	free(STM);
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

DLLEXPORT(long) Parallel_Smoothing_Matrix(
	long SizeMatrix,
	double* MatrixReshaped,
	double* ResultMatrixReshaped,
	double* ResultMatrixSumAdj,
	long SameValueSmoothingFlag,
	long LargeDifferenceAdjustFlag,
	long AdjustIfLargeThenDiag,
	double* PD
)
{
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
	long SizeMatrix,
	double* MatrixReshaped,
	double* ResultMatrixReshaped,
	double* ResultMatrixSumAdj,
	long SameValueSmoothingFlag,
	long LargeDifferenceAdjustFlag,
	long AdjustIfLargeThenDiag,
	double* PD
)
{
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
	long SizeMatrix,
	double* MatrixReshaped,
	double* ResultMatrixReshaped,
	double* ResultMatrixSumAdj,
	long SameValueSmoothingFlag,
	long LargeDifferenceAdjustFlag,
	long AdjustIfLargeThenDiag,
	double* PD
)
{
	long ResultCode = 1;
	double* Result1 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);
	double* Result2 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);
	double* Result3 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);
	double* Result4 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);
	double* Result5 = (double*)malloc(sizeof(double) * SizeMatrix * SizeMatrix);

	ResultCode *= Parallel_Smoothing_Matrix(SizeMatrix, MatrixReshaped, Result1, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD);
	ResultCode *= Vertical_Smoothing_Matrix(SizeMatrix, Result1, Result2, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD);
	ResultCode *= Parallel_Smoothing_Matrix(SizeMatrix, Result2, Result3, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD);
	ResultCode *= Vertical_Smoothing_Matrix(SizeMatrix, Result3, Result4, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD);
	ResultCode *= Parallel_Smoothing_Matrix(SizeMatrix, Result4, Result5, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD);
	ResultCode *= Vertical_Smoothing_Matrix(SizeMatrix, Result5, ResultMatrixReshaped, ResultMatrixSumAdj, SameValueSmoothingFlag, LargeDifferenceAdjustFlag, AdjustIfLargeThenDiag, PD);

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

	long** MyMatrix = (long**)malloc(sizeof(long*) * NRate);
	for (i = 0; i < NRate; i++) MyMatrix[i] = (long*)malloc(sizeof(long) * NRate);

	long* TotalNum = (long*)malloc(sizeof(long) * NRate);

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
	long NRate,
	double* InputPD,
	double* MinPD,
	double* ResultPD,
	double* TransitionNumberReshaped,
	double* TransitionProbReshaped,
	long NTermPD,
	double* CummulativePD,
	double* ForwardPD,
	double* MarginalPD,
	double* QuarterlyMarginalPD,
	double* QuarterlyCummPD
)
{
	long i, j, k, n, ResultCode = 0;
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