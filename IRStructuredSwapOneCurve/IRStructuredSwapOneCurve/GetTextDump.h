#ifdef _WIN32
#include <direct.h>
#elif WIN32
#include <direct.h>
#elif WIN64
#include <direct.h>
#elif _WIN64
#include <direct.h>
#endif

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <string.h>

void get_filenameYYYYMMDD( char *target_filename, long filenamelength, char *modulename)
{
	time_t timer = time(NULL); 
	struct tm st_time;

	localtime_s(&st_time, &timer);
	long YYYY = st_time.tm_year + 1900;
	long MM = st_time.tm_mon + 1;
	long DD = st_time.tm_mday;
	long HH = st_time.tm_hour;
	long II = st_time.tm_min;
	long SS = st_time.tm_sec;
	long YYYYMMDD = YYYY * 10000 + MM * 100 + DD;
	long HHIISS = HH * 10000 + II * 100 + SS;
	
	char YYYYMMDD_STR[10];
	char HHIISS_STR[10];
	char txtt[10] = ".txt";
	_itoa_s(YYYYMMDD, YYYYMMDD_STR, 10);
	_itoa_s(HHIISS, HHIISS_STR, 10);


	strcpy_s(target_filename, sizeof(char) * filenamelength, modulename);

	strcat_s(target_filename, sizeof(char) * filenamelength, YYYYMMDD_STR);
	strcat_s(target_filename, sizeof(char) * filenamelength, HHIISS_STR);
	strcat_s(target_filename, sizeof(char) * filenamelength, txtt);

}

void DumppingTextData(char* CalcFunctionName, char* filename, char* buf1)
{
	char* CalcFunctionName_Path = (char*)malloc((strlen(CalcFunctionName) + 25) * sizeof(char));
	char* lpszPath = (char*)malloc((strlen(CalcFunctionName) + strlen(filename) + 25) * sizeof(char));

	sprintf_s(CalcFunctionName_Path, (strlen(CalcFunctionName) + 25) * sizeof(char), "%s\\%s", "..\\MyQuant_Log", CalcFunctionName);
	sprintf_s(lpszPath, (strlen(CalcFunctionName) + strlen(filename) + 25) * sizeof(char), "%s\\%s", CalcFunctionName_Path, filename);

#ifdef WIN32
	_mkdir("..\\MyQuant_Log");
	_mkdir(CalcFunctionName_Path);
#elif _WIN32
	_mkdir("..\\MyQuant_Log");
	_mkdir(CalcFunctionName_Path);
#elif _WIN64
	_mkdir("..\\MyQuant_Log");
	_mkdir(CalcFunctionName_Path);
#elif WIN64
	_mkdir("..\\MyQuant_Log");
	_mkdir(CalcFunctionName_Path);
#endif
	//	mkdir(lpsFolder,777);
	//	char	lpszBuffer[100000];

	char* lpszBuffer = (char*)malloc((strlen(buf1) + 10) * sizeof(char));
	strcpy_s(lpszBuffer, (strlen(buf1) + 10) * sizeof(char), buf1);
	strcat_s(lpszBuffer, (strlen(buf1) + 10) * sizeof(char), "\r\n");
	
	FILE* fp = NULL;
	if (0 == fopen_s(&fp, lpszPath, "a+"))
	{
		fputs(lpszBuffer, fp);
		fclose(fp);
	}

	if (CalcFunctionName_Path) free(CalcFunctionName_Path);
	if (lpszPath) free(lpszPath);
	if (lpszBuffer) free(lpszBuffer);
}

void DumppingTextData(char* CalcFunctionName, char* filename, const char* VariableNameStr, int nValue)
{
	const long N = 5000;
	char lpszBuffer[N];
	sprintf_s(lpszBuffer,"%s : ", VariableNameStr);

	char Temp[100];
	sprintf_s(Temp, "%d", nValue);

	strcat_s(lpszBuffer, sizeof(char) * N, Temp);

	DumppingTextData(CalcFunctionName, filename, lpszBuffer);
}

void DumppingTextData(char* CalcFunctionName, char* filename, const char* VariableNameStr, double dblValue)
{
	const long N = 5000;
	char lpszBuffer[N];
	sprintf_s(lpszBuffer, "%s : ", VariableNameStr);

	char Temp[100];
	sprintf_s(Temp, "%f", dblValue);

	strcat_s(lpszBuffer, sizeof(char) * N, Temp);

	DumppingTextData(CalcFunctionName, filename, lpszBuffer);
}

void DumppingTextData(char* CalcFunctionName, char* filename, const char* VariableNameStr, long nValue)
{
	DumppingTextData(CalcFunctionName, filename, VariableNameStr, (int)nValue);
}

void DumppingTextDataArray(char* CalcFunctionName, char* filename, const char* VariableNameStr, long nSize, double* dblValue)
{
	const long N = 100;
	char* lpszBuffer = (char*)malloc((N * nSize + 50) * sizeof(char));
	sprintf_s(lpszBuffer, (N * nSize + 50) , "%s : ", VariableNameStr);

	for (int i = 0; i < nSize; i++)
	{
		char Temp[N];
		sprintf_s(Temp, sizeof(char) * N, "%f", dblValue[i]);

		strcat_s(lpszBuffer, (N * nSize + 50) * sizeof(char), Temp);

		if (i < nSize - 1) strcat_s(lpszBuffer, (N * nSize + 50) * sizeof(char), ", ");
	}

	DumppingTextData(CalcFunctionName, filename, lpszBuffer);
	if (lpszBuffer) free(lpszBuffer);
}

void DumppingTextDataArray(char* CalcFunctionName, char* filename, const char* VariableNameStr, long nSize, long* nValue)
{
	const long N = 100;
	char* lpszBuffer = (char*)malloc((N* nSize + 50) * sizeof(char));
	sprintf_s(lpszBuffer, (N * nSize + 50), "%s : ", VariableNameStr);

	for (int i = 0; i < nSize; i++)
	{
		char Temp[N];
		sprintf_s(Temp, sizeof(char) * N, "%d", nValue[i]);

		strcat_s(lpszBuffer, (N * nSize + 50) * sizeof(char), Temp);

		if (i < nSize - 1) strcat_s(lpszBuffer, (N * nSize + 50) * sizeof(char), ", ");
	}

	DumppingTextData(CalcFunctionName, filename, lpszBuffer);

	if (lpszBuffer) free(lpszBuffer);
}

void DumppingTextDataArray(char* CalcFunctionName, char* filename, const char* VariableNameStr, int nSize, int* nValue)
{
	const long N = 100;
	char* lpszBuffer = (char*)malloc((N * nSize + 50) * sizeof(char));
	sprintf_s(lpszBuffer, (N * nSize + 50), "%s : ", VariableNameStr);

	for (int i = 0; i < nSize; i++)
	{
		char Temp[N];
		sprintf_s(Temp, sizeof(char) * N, "%d", nValue[i]);

		strcat_s(lpszBuffer, (N * nSize + 50) * sizeof(char), Temp);

		if (i < nSize - 1) strcat_s(lpszBuffer, (N * nSize + 50) * sizeof(char), ", ");
	}

	DumppingTextData(CalcFunctionName, filename, lpszBuffer);
	if (lpszBuffer) (lpszBuffer);
}

void DumppingTextDataMatrix(char* CalcFunctionName, char* filename, const char* VariableNameStr, long nRow, long nCol, double* dblValueReshaped)
{
	long i;
	double* line;
	for (i = 0; i < nRow; i++)
	{
		line = dblValueReshaped + i * nCol;
		DumppingTextDataArray(CalcFunctionName, filename, VariableNameStr, nCol, line);
	}
}

void DumppingTextDataMatrix(char* CalcFunctionName, char* filename, const char* VariableNameStr, long nRow, long nCol, long* dblValueReshaped)
{
	long i;
	long* line;
	for (i = 0; i < nRow; i++)
	{
		line = dblValueReshaped + i * nCol;
		DumppingTextDataArray(CalcFunctionName, filename, VariableNameStr, nCol, line);
	}
}

void DumppingTextDataMatrix(char* CalcFunctionName, char* filename, const char* VariableNameStr, long nRow, long nCol, int* dblValueReshaped)
{
	long i;
	int* line;
	for (i = 0; i < nRow; i++)
	{
		line = dblValueReshaped + i * nCol;
		DumppingTextDataArray(CalcFunctionName, filename, VariableNameStr, nCol, line);
	}
}

