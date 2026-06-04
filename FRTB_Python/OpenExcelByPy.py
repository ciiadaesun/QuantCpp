#%%
"""
v1.0.2
"""
import pandas as pd
import win32com.client as win32
from packaging import version
import os
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font
import datetime
curdir = os.getcwd()

def remove_timezone_from_df(df):
    for col in df.columns:
        df[col] = df[col].map(
            lambda x: x.replace(tzinfo=None)
            if hasattr(x, "tzinfo") and x.tzinfo is not None
            else x
        )
    return df
input("다른 엑셀시트를 모두 종료하시기 바랍니다. 종료하고 엔터를 누르세요 : ")
targetfilepath = input("복사하실 엑셀 파일 명을 입력하시오(TempExcel.xlsx) : ")

if '.xlsx' not in targetfilepath:
    targetfilepath += '.xlsx'

if '\\' not in targetfilepath:
    targetfilepath = curdir + '\\' + targetfilepath

resultfilename = input("저장할 파일 명을 입력하시오(ex File2.xlsx) : ")

if ".xlsx" not in resultfilename:
    resultfilename += ".xlsx"

if "\\" not in resultfilename:
    resultfilename = curdir + "\\" + resultfilename

valuestring = input("0: 각각 셀 포멧 그대로복사 or 1: 값만 복사")
valueread = False if len(valuestring) == 0 or valuestring == '0' else True

excel = win32.Dispatch("Excel.Application")
excel.Visible = True
excel.DisplayAlerts = False

wb = excel.Workbooks.Open(targetfilepath)

sheet_name_list = []
data_list = []
merge_info_list = []
col_width_list = []
row_height_list = []
font_info_list = []

for ws in wb.Worksheets:
    sheet_name_list.append(ws.Name)

for n in range(len(sheet_name_list)):
    ws = wb.Worksheets(sheet_name_list[n])
    used_range = ws.UsedRange

    start_row = used_range.Row
    start_col = used_range.Column
    nrows = used_range.Rows.Count
    ncols = used_range.Columns.Count

    data = []
    font_infos = []
    for r in range(start_row, start_row + nrows):
        row = []
        font_row = []

        for c in range(start_col, start_col + ncols):
            cell = ws.Cells(r, c)
            font = cell.Font

            font_row.append({
                "name": font.Name,
                "size": font.Size,
                "bold": bool(font.Bold),
                "italic": bool(font.Italic),
                "underline": "single" if font.Underline != -4142 else None,
                "strike": bool(font.Strikethrough),
                "color": font.Color
            })

            # 병합셀 내부 셀은 pandas 저장 시 값 중복 방지
            if cell.MergeCells:
                ma = cell.MergeArea
                if cell.Row != ma.Row or cell.Column != ma.Column:
                    value = None
                else:
                    if valueread:
                        value = cell.Value
                    else:
                        value = cell.Formula if cell.HasFormula else cell.Value
                        if isinstance(value, (datetime.datetime, pd.Timestamp)):
                            if value.hour == 0 and value.minute == 0 and value.second == 0:
                                value = value.date()

            else:
                if valueread:
                    value = cell.Value
                else:
                    value = cell.Formula if cell.HasFormula else cell.Value
                    if isinstance(value, (datetime.datetime, pd.Timestamp)):
                        if value.hour == 0 and value.minute == 0 and value.second == 0:
                            value = value.date()

            row.append(value)
        font_infos.append(font_row)
        
        data.append(row)
    font_info_list.append(font_infos)

    df = pd.DataFrame(data)
    df = remove_timezone_from_df(df)
    data_list.append(df)

    # 병합셀 정보 저장
    merge_ranges = []
    merge_address_set = set()

    for r in range(start_row, start_row + nrows):
        for c in range(start_col, start_col + ncols):
            cell = ws.Cells(r, c)

            if cell.MergeCells:
                ma = cell.MergeArea
                addr = ma.Address

                # 같은 병합영역 중복 방지
                if addr not in merge_address_set:
                    merge_address_set.add(addr)

                    r1 = ma.Row - start_row + 1
                    c1 = ma.Column - start_col + 1
                    r2 = r1 + ma.Rows.Count - 1
                    c2 = c1 + ma.Columns.Count - 1

                    merge_ranges.append((r1, c1, r2, c2))

    merge_info_list.append(merge_ranges)

    # 열 너비 저장
    col_widths = []
    for c in range(start_col, start_col + ncols):
        col_widths.append(ws.Columns(c).ColumnWidth)

    col_width_list.append(col_widths)

    # 행 높이 저장
    row_heights = []
    for r in range(start_row, start_row + nrows):
        row_heights.append(ws.Rows(r).RowHeight)

    row_height_list.append(row_heights)

    print(
        sheet_name_list[n] + " 복사완료, 잠시만기다려주세요"
        if n < len(sheet_name_list) - 1
        else "복사완료"
    )
print("50%완료")
# 1차 저장
writer = pd.ExcelWriter(resultfilename, engine="openpyxl")

for n in range(len(sheet_name_list)):
    data_list[n].to_excel(
        writer,
        sheet_name=sheet_name_list[n],
        index=False,
        header=False
    )

writer.close()

# 2차로 병합셀 / 열너비 / 행높이 적용
out_wb = load_workbook(resultfilename)

for n, sheet_name in enumerate(sheet_name_list):
    out_ws = out_wb[sheet_name]

    # 폰트 / 글자색 적용
    for r_idx, font_row in enumerate(font_info_list[n], start=1):
        for c_idx, font_info in enumerate(font_row, start=1):

            out_cell = out_ws.cell(row=r_idx, column=c_idx)

            # 병합셀 내부는 쓰기 불가인 경우가 있어서 skip
            if out_cell.__class__.__name__ == "MergedCell":
                continue

            color = None

            if font_info["color"] is not None:
                try:
                    # Excel COM 색상값은 BGR 정수라서 RGB로 변환
                    color_int = int(font_info["color"])
                    red = color_int % 256
                    green = (color_int // 256) % 256
                    blue = (color_int // 65536) % 256
                    color = f"{red:02X}{green:02X}{blue:02X}"
                except:
                    color = None

            out_cell.font = Font(
                name=font_info["name"],
                size=font_info["size"],
                bold=font_info["bold"],
                italic=font_info["italic"],
                underline=font_info["underline"],
                strike=font_info["strike"],
                color=color
            )    

    # 병합셀 적용
    for r1, c1, r2, c2 in merge_info_list[n]:
        out_ws.merge_cells(
            start_row=r1,
            start_column=c1,
            end_row=r2,
            end_column=c2
        )

    # 열 너비 적용
    for idx, width in enumerate(col_width_list[n], start=1):
        col_letter = get_column_letter(idx)
        out_ws.column_dimensions[col_letter].width = width

    # 행 높이 적용
    for idx, height in enumerate(row_height_list[n], start=1):
        out_ws.row_dimensions[idx].height = height

out_wb.save(resultfilename)

wb.Close(SaveChanges=False)
excel.DisplayAlerts = True
excel.Quit()

print("전체 복사 완료")


# %%
# %%
