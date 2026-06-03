#%%
"""
v1.0.2
"""
import pandas as pd
import win32com.client as win32
from packaging import version
import os
curdir = os.getcwd()

targetfilepath = input("복사하실 엑셀 파일 명을 입력하시오(TempExcel.xlsx)")

if '.xlsx' not in targetfilepath : 
    targetfilepath += '.xlsx'

if '\\' not in targetfilepath : 
    targetfilepath = curdir + '\\' + targetfilepath

resultfilename = input("저장할 파일 명을 입력하시오(ex File2.xlsx)")
if ".xlsx" not in resultfilename:
    resultfilename += ".xlsx"

if "\\" not in resultfilename:
    resultfilename = curdir + "\\" + resultfilename

valuestring = input("0: 각각 셀 포멧 그대로복사 or 1: 값만 복사")
valueread = False if len(valuestring) == 0 or valuestring == '0' else True

excel = win32.Dispatch("Excel.Application")
excel.Visible = True
excel.DisplayAlerts = False

src_wb = excel.Workbooks.Open(targetfilepath)

# 첫 번째 시트를 복사해서 새 Workbook 생성
src_wb.Worksheets(1).Copy()
new_wb = excel.ActiveWorkbook

# 나머지 시트 복사
for i in range(2, src_wb.Worksheets.Count + 1):
    src_wb.Worksheets(i).Copy(
        After=new_wb.Worksheets(new_wb.Worksheets.Count)
    )

# 값만 복사 옵션: 서식/병합/열너비는 유지하고 수식만 값으로 바꿈
if valueread:
    for ws in new_wb.Worksheets:
        used_range = ws.UsedRange
        used_range.Value = used_range.Value

new_wb.SaveAs(resultfilename)

src_wb.Close(SaveChanges=False)
new_wb.Close(SaveChanges=True)

excel.DisplayAlerts = True
excel.Quit()

print("복사 완료")

#wb = excel.Workbooks.Open(targetfilepath)
#sheet_name_list = []
#data_list = []
#for ws in wb.Worksheets:
#    sheet_name_list.append(ws.Name)
#
#for n in range(len(sheet_name_list)) : 
#    ws = wb.Worksheets(sheet_name_list[n])
#    used_range = ws.UsedRange
#    if valueread == True : 
#        data = used_range.Value
#        df = pd.DataFrame(data)
#    else : 
#        nrows = used_range.Rows.Count
#        ncols = used_range.Columns.Count
#        data = []
#        for r in range(1, nrows + 1):
#            row = []
#            for c in range(1, ncols + 1):
#                cell = ws.Cells(r, c)
#                if cell.HasFormula:
#                    value = cell.Formula
#                else:
#                    value = cell.Value                
#                row.append(value)
#            data.append(row)
#        df = pd.DataFrame(data)    
#    print(sheet_name_list[n] + "복사완료, 잠시만기다려주세요" if n < len(sheet_name_list) - 1 else "복사완료")
#    data_list.append(df)
#
#
#writer = pd.ExcelWriter(resultfilename) # pylint: disable=abstract-class-instantiated
#for n in range(len(sheet_name_list)) : 
#    data_list[n].to_excel(writer, sheet_name = sheet_name_list[n], index = False, header = False)
#
#if version.parse(pd.__version__) < version.parse("1.6.0"):
#    writer.save()   # 구버전 pandas
#else:
#    pass            # 신버전 pandas            
#writer.save()
#writer.close()


# %%
