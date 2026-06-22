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
    if header_idx >= 0 : 
        df.columns = df.iloc[0]
        df = df.iloc[1:]
    return df

def DataFrameTotxt(df, header = False, seperateby = ',', saveflag = False) : 

    MyName = input("저장할 텍스트파일 이름은? -> ") if saveflag == True else ""
    if '.dat' in MyName : 
        seperateby = "|"
    if header == False :
        lines = []
        for i, row in enumerate(df.values):
            line = seperateby.join(map(str, row))
            if i % 200 == 0: 
                print(str(i) + 'Lines')
            lines.append(line)
        txt = "\n".join(lines)
        #txt = '\n'.join(seperateby.join(map(str, row)) for row in df.values)
    else : 
        lines = []

        header = seperateby.join(map(str, df.columns))
        print("Header :", header)
        lines.append(header)
        for row_idx, row in enumerate(df.values):
            line = seperateby.join(map(str, row))
            if row_idx % 200 == 0: 
                print(str(row_idx) + 'Lines')
            lines.append(line)
        txt = "\n".join(lines)
        #txt = (','.join(map(str, df.columns)) + '\n' + '\n'.join(seperateby.join(map(str, row)) for row in df.values))    

    if saveflag == True : 
        if '.txt' not in MyName and '.dat' not in MyName : 
            if '.txt' not in MyName : 
                MyName += '.txt'
            elif '.dat' not in MyName : 
                MyName += '.dat'
            with open(MyName, "w", encoding="utf-8") as f:
                f.write(txt)
            print("저장완료")
        else : 
            with open(MyName, "w", encoding="utf-8") as f:
                f.write(txt)
            print("저장완료")

    return txt

def AddNewColumnOnDF(df, col_idx = -1, insertflag = True, value = None, colname = "NEW_COL") : 
    if colname in df.columns : 
        colname += "_"

    if col_idx < 0 : 
        col_idx = len(df.columns) + col_idx + 1

    if 'th' in str(value).lower() and 'col' in str(value).lower() : 
        value = df[df.columns[int(value.lower().split('th')[0])]]
        if insertflag == True : 
            df.insert(loc = col_idx + 1, column = colname, value = value)
        else : 
            df[df.columns[col_idx]] = value
    else :        
        if insertflag == True : 
            df.insert(loc=col_idx + 1,column=colname,value=value)
        else : 
            df[df.columns[col_idx]] = value
    return df

def CopyTextFile(curdir = os.getcwd()) : 

    targetfilename = input("복호화할 텍스트파일명을 입력하시오(.txt 또는 .dat 포함)\n -> ")
    if '.txt' not in targetfilename and '.dat' not in targetfilename : 
        if (targetfilename + '.txt') in os.listdir(curdir) : 
            targetfilename += '.txt'
        elif (targetfilename + '.dat') in os.listdir(curdir) : 
            targetfilename += '.dat'

    seperatebystr = input("해당 파일은 쉼표(,)로 나뉜 파일입니까? (|)로 나뉜 파일입니까? \n  -> "  )
    seperateby = ',' if len(str(seperatebystr)) == 0 or str(seperatebystr) in [',','0'] else '|'
    columnaddflag = input("해당 파일에 컬럼을 더 추가하시겠습니까? (y/n) \n -> ") 
    df = ReadtxtByApplication(targetfilename, seperateby = seperateby, header_idx = -1, curdir = os.getcwd())

    if len(str(columnaddflag)) == 0 or columnaddflag.lower() == 'n' :
        DataFrameTotxt(df, header = False, seperateby = seperateby, saveflag=True)

    else : 
        col_idxstr = input("몇 번째 Column에 새 값을 추가합니까? \n -> ")    
        col_idx = -1 if len(str(col_idxstr)) == 0 else int(col_idxstr)
        insertflagstr = input("삽입하려면 0 수정하려면 1 ->")
        insertflag = True if len(str(insertflagstr)) == 0 or str(insertflagstr) == '0' else False
        value = input("어떤 글자를 추가하겠습니까? enter를 입력하면 공백을 입력 ->")
        df = AddNewColumnOnDF(df, col_idx = col_idx, insertflag = insertflag, value = value)        
        DataFrameTotxt(df, header = False, seperateby = seperateby, saveflag=True)

if __name__ == '__main__' : 
    CopyTextFile()

# %%
