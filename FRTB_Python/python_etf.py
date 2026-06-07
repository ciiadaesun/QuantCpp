#%%
"""
v1.0.2
"""

# python -m pip install selenium 

import pandas as pd
import requests
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time


def get_stock_code(stock_name):

    url = (
        "https://finance.naver.com/api/search/searchList.naver"
        f"?query={stock_name}"
    )

    data = requests.get(
        url,
        headers={"User-Agent":"Mozilla/5.0"}
    ).json()

    for item in data["stocks"]:
        if item["itemName"] == stock_name:
            return item["itemCode"]

    return None

def _collect_all_frame_html(driver):
    html_list = []

    def collect():
        html_list.append(driver.page_source)

        frames = driver.find_elements(By.TAG_NAME, "iframe")
        for i in range(len(frames)):
            frames = driver.find_elements(By.TAG_NAME, "iframe")
            driver.switch_to.frame(frames[i])
            collect()
            driver.switch_to.parent_frame()

    driver.switch_to.default_content()
    collect()
    return html_list


def get_naver_etf_holdings(etf_code):
    etf_code = str(etf_code).zfill(6)

    url = f"https://finance.naver.com/item/coinfo.naver?code={etf_code}"

    opt = Options()
    opt.add_argument("--headless=new")
    opt.add_argument("--window-size=1400,1200")
    opt.add_argument("--disable-gpu")
    opt.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=opt)
    driver.get(url)
    time.sleep(2)

    html_list = _collect_all_frame_html(driver)
    title = driver.title
    titlename = title.split(":")[0]
    etf_name = titlename[:-1] if titlename[-1] == ' ' else titlename

    driver.quit()
    candidates = []

    for html in html_list:
        try:
            tables = pd.read_html(StringIO(html))
        except Exception:
            continue

        for df in tables:
            cols = [str(c).strip() for c in df.columns]

            if any("구성종목명" in c for c in cols) and any("구성비중" in c for c in cols):
                candidates.append(df)

    if not candidates:
        raise ValueError("네이버 ETF분석 iframe 안에서도 CU당 구성종목 테이블을 찾지 못했습니다.")

    df = candidates[0].copy()
    df.columns = [str(c).strip() for c in df.columns]

    rename = {}
    for c in df.columns:
        if "구성종목명" in c:
            rename[c] = "구성종목명"
        elif "주식수" in c:
            rename[c] = "주식수"
        elif "구성비중" in c:
            rename[c] = "구성비중"

    df = df.rename(columns=rename)

    df["주식수"] = pd.to_numeric(
        df["주식수"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

    df["구성비중"] = pd.to_numeric(
        df["구성비중"].astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False),
        errors="coerce"
    )

    df.insert(0, "ETF코드", etf_code)
    df.insert(0, "ETF명", etf_name)
    return df[["ETF명","ETF코드", "구성종목명", "주식수", "구성비중"]]

InputString = input("ETF 번호 입력(ex : 451060, 102110, 396500 ...) - \n").replace(" ","")
ETFCodeList = InputString.split(",")
df_list = []
for c in ETFCodeList : 
    df = get_naver_etf_holdings(c)
    #df["종목코드"] = df["구성종목명"].apply(get_stock_code)
    df_list.append(df)

with pd.ExcelWriter("ETF_네이버_구성종목.xlsx", engine="openpyxl") as writer:
    for n in range(len(df_list)) : 
        df_list[n].to_excel(writer, sheet_name=df_list[n]["ETF코드"].iloc[0], index=False)
# %%

# %%
