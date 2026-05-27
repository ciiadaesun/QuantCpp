#%%
"""
Created By Daesun Lim (CIIA(R), FRM(R))
v1.2.2
"""
import pandas as pd
import win32com.client as win32
from packaging import version
import os
curdir = os.getcwd()
filelistincurdir = os.listdir(curdir)
targetfilepath = input("복사하실 엑셀 파일 명을 입력하시오(TempExcel.xlsx)")
if '.xlsx' not in targetfilepath : 
    targetfilepath += '.xlsx'

if '\\' not in targetfilepath : 
    targetfilepath = curdir + '\\' + targetfilepath

excel = win32.Dispatch("Excel.Application")
excel.Visible = True
valuestring = input("0: 각각 셀 포멧 그대로복사 or 1: 값만 복사")
valueread = False if len(valuestring) == 0 or valuestring == '0' else True
wb = excel.Workbooks.Open(targetfilepath)
sheet_name_list = []
data_list = []
for ws in wb.Worksheets:
    sheet_name_list.append(ws.Name)

for n in range(len(sheet_name_list)) : 
    ws = wb.Worksheets(sheet_name_list[n])
    used_range = ws.UsedRange
    if valueread == True : 
        data = used_range.Value
        df = pd.DataFrame(data)
    else : 
        nrows = used_range.Rows.Count
        ncols = used_range.Columns.Count
        data = []
        for r in range(1, nrows + 1):
            row = []
            for c in range(1, ncols + 1):
                cell = ws.Cells(r, c)
                if cell.HasFormula:
                    value = cell.Formula
                else:
                    value = cell.Value                
                row.append(value)
            data.append(row)
        df = pd.DataFrame(data)    
    print(sheet_name_list[n] + "복사완료, 잠시만기다려주세요" if n < len(sheet_name_list) - 1 else "복사완료")
    data_list.append(df)

resultfilename = input("저장할 파일 명을 입력하시오(ex File2.xlsx)")

writer = pd.ExcelWriter(resultfilename + '.xlsx' if '.xlsx' not in resultfilename else resultfilename) # pylint: disable=abstract-class-instantiated
for n in range(len(sheet_name_list)) : 
    data_list[n].to_excel(writer, sheet_name = sheet_name_list[n], index = False, header = False)

if version.parse(pd.__version__) < version.parse("1.6.0"):
    writer.save()   # 구버전 pandas
else:
    pass            # 신버전 pandas            
#writer.save()
writer.close()


# %%
