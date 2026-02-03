from sqlalchemy import create_engine, text
import const
import pandas as pd
import glob
import os
import re

# Lay file excel tu data (dam bao ko co file khac)
xls_lst = glob.glob("data/*.xlsx")

# Ket noi voi SQL Server
engine = create_engine('mssql+pyodbc://' + const.SERVER_NAME + '/' + 'master' + '?Trusted_Connection=yes&driver=ODBC+Driver+17+for+SQL+Server&autocommit=True')
with engine.connect() as con:
    con.execute(text(f'''
    IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{const.DB_NAME}')
    BEGIN
	    CREATE DATABASE {const.DB_NAME};
    END
''')
)
engine = create_engine("mssql+pyodbc://" + const.SERVER_NAME + "/" + const.DB_NAME + '?Trusted_Connection=yes&driver=ODBC+Driver+17+for+SQL+Server&autocommit=True')

# Duyet qua file excel. Trich xuat ten file
for xls in xls_lst:
    file_name = re.split(r"[\\/]", xls)[-1].split(sep = ".")[0]
    print(f"Đang xử lý file: {file_name}")
    # Tao schemas neu ko co
    with engine.connect() as con:
        if engine.dialect.has_schema(con, file_name) == False:
            con.execute(text(f"CREATE SCHEMA {file_name};"))
    current_xls = pd.ExcelFile(xls)
    for sheet in current_xls.sheet_names:
        print(f"Đang xử lý sheet: {sheet}")
        df = current_xls.parse(
            sheet, 
            nrows = 100)
        if df.empty == False:
            with engine.connect() as con:
                df.to_sql(
                    sheet,
                    con,
                    schema = file_name,
                    if_exists = 'replace',
                    index = False,
                )
print("Xu ly du lieu thanh cong!")