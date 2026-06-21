#%%
"""
v1.0.2
"""
import pandas as pd
import win32com.client as win32
#from packaging import version
import os
#from openpyxl import load_workbook
#from openpyxl.utils import get_column_letter
#from openpyxl.styles import Font
#from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
#import datetime
curdir = os.getcwd()

#input("다른 엑셀시트를 모두 종료하시기 바랍니다. 종료하고 엔터를 누르세요 : ")
#targetfilepath = r'C:\Users\임대선\Desktop\새 폴더\ExcelUse\FRTB_RAW.csv'
def ReadExcelApplication(targetfilepath, sheet_idx = 0) : 

    excel = win32.Dispatch("Excel.Application")
    excel.Visible = True
    excel.DisplayAlerts = False
    print(targetfilepath)
    wb = excel.Workbooks.Open(targetfilepath)

    sheet_name_list = []

    for ws in wb.Worksheets:
        sheet_name_list.append(ws.Name)
    ws = wb.Worksheets(sheet_name_list[min(len(sheet_name_list)-1, sheet_idx)])

    ws = wb.Worksheets(sheet_name_list[min(len(sheet_name_list)-1, sheet_idx)])
    used_range = ws.UsedRange
    data = used_range.Value
    if data is None:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(data)
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    # 저장 안 하고 종료
    wb.Close(SaveChanges=False)

    excel.Quit()
    return df 

def ReadxlsxByApplication(targetfilepath, sheet_idx = 0, curdir = os.getcwd()) : 
    if '.xlsx' not in targetfilepath:
        targetfilepath += '.xlsx'

    if '\\' not in targetfilepath:
        targetfilepath = curdir + '\\' + targetfilepath
    return ReadExcelApplication(targetfilepath, sheet_idx = sheet_idx)

def ReadcsvByApplication(targetfilepath, sheet_idx = 0, curdir = os.getcwd()) : 
    if '.csv' not in targetfilepath:
        targetfilepath += '.csv'

    if '\\' not in targetfilepath:
        targetfilepath = curdir + '\\' + targetfilepath
    return ReadExcelApplication(targetfilepath, sheet_idx = sheet_idx)

def ReadtxtByApplication(filepath, seperateby = ',', header_idx = -1, curdir = os.getcwd()) : 
    if '\\' not in filepath:
        filepath = curdir + '\\' + filepath
    with open(filepath, "r", encoding="utf-8") as f:
        txt = f.read()

    rows = [row.split(seperateby) for row in txt.splitlines()]
    df = pd.DataFrame(rows)
    if header_idx > 0 : 
        df.columns = df.iloc[0]
        df = df.iloc[1:]
    return df

#df_xlsx = ReadxlsxByApplication(targetfilepath, sheet_idx = 0, curdir = os.getcwd())
#df_csv = ReadcsvByApplication('FRTB_RAW', sheet_idx = 0, curdir = os.getcwd())

def DataFrameTotxt(df, header = False, seperateby = ',') : 
    if header == False : 
        txt = '\n'.join(
            seperateby.join(map(str, row))
            for row in df.values
        )
    else : 
        txt = (
            ','.join(map(str, df.columns))
            + '\n'
            + '\n'.join(
                seperateby.join(map(str, row))
                for row in df.values
            )
        )    
    MyName = input("저장할 텍스트파일 이름은? -> ")
    if '.txt' not in MyName and '.dat' not in MyName : 
        if '.txt' not in MyName : 
            MyName += '.txt'
        elif '.dat' not in MyName : 
            MyName += '.dat'

    with open(MyName, "w", encoding="utf-8") as f:
        f.write(txt)
    print("저장완료")
# %%
