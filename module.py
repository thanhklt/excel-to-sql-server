from sqlalchemy import create_engine, text
import const
import pandas as pd
import glob
import re

def get_excel_lst():
    xls_lst = glob.glob("data/*.xlsx") + glob.glob("data/*.xls")
    return xls_lst

def create_database():
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
    return engine


def create_schemas(engine, file_name):
    with engine.connect() as con:
            if engine.dialect.has_schema(con, file_name) == False:
                con.execute(text(f"CREATE SCHEMA {file_name};"))
def process_sheet(engine, current_excel, file_name):
    for sheet in current_excel.sheet_names:
            print(f"Đang xử lý sheet: {sheet}")
            df = current_excel.parse(
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
def process_excel_file(xls_lst, engine):
    for xls in xls_lst:
        file_name = re.split(r"[\\/]", xls)[-1].split(sep = ".")[0]
        print(f"Đang xử lý file: {file_name}")
        create_schemas(engine, file_name)
        current_xls = pd.ExcelFile(xls)
        process_sheet(engine, current_xls, file_name)
    print("Xu ly du lieu thanh cong!")

def main():
     xls_lst = get_excel_lst()
     engine = create_database()
     process_excel_file(xls_lst, engine)


if __name__ ==  "__main__":
     main()
