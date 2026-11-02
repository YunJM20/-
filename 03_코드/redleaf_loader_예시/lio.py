# -*- coding: utf-8 -*-
"""9월 잎상추 폴더 입출력 유틸 (openpyxl이 못 읽는 xlsx도 bookViews를 제거해 읽는다)"""
import io, re, zipfile, os
import pandas as pd

ROOT = r"C:\Users\yunjm\OneDrive - jbnu.ac.kr\바탕 화면\연구실\학회\2026 학회\추계 원예학회\9월 잎상추"


def rd(f, **kw):
    try:
        return pd.read_excel(f, **kw)
    except Exception:
        z = zipfile.ZipFile(f)
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as zo:
            for it in z.infolist():
                data = z.read(it.filename)
                if it.filename == "xl/workbook.xml":
                    data = re.sub(rb"<bookViews>.*?</bookViews>", b"", data, flags=re.S)
                zo.writestr(it, data)
        out.seek(0)
        return pd.read_excel(out, **kw)


def sheets(f):
    try:
        return pd.ExcelFile(f).sheet_names
    except Exception:
        z = zipfile.ZipFile(f)
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as zo:
            for it in z.infolist():
                data = z.read(it.filename)
                if it.filename == "xl/workbook.xml":
                    data = re.sub(rb"<bookViews>.*?</bookViews>", b"", data, flags=re.S)
                zo.writestr(it, data)
        out.seek(0)
        return pd.ExcelFile(out).sheet_names


def base(f):
    return os.path.basename(f)
