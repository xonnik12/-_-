# Устанавливаем библиотеки (если не стоят):
# pip install pyodbc networkx matplotlib 
# pip install git+https://github.com/WestHealth/pyvis.git

import pyodbc
import pandas as pd

# 1. Подключение к БД
db_file = r"D:\oksana\db.accdb"
conn_str = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    fr"DBQ={db_file};"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Считываем таблицы
df_persona = pd.read_sql("SELECT * FROM ПЕРСОНА", conn)
df_uch = pd.read_sql("SELECT * FROM УЧЕБНИК", conn)
df_content = pd.read_sql("SELECT * FROM Содержание", conn)
df_record = pd.read_sql("SELECT * FROM ЗАПИСЬ_ПЕРСОНЫ", conn)

# Закрываем соединение
conn.close()

# Проверяем, что всё считалось
print("ПЕРСОНА:", df_persona.shape)
print("УЧЕБНИК:", df_uch.shape)
print("Содержание:", df_content.shape)
print("ЗАПИСЬ_ПЕРСОНЫ:", df_record.shape)



df_persona.to_csv("persons.csv")
df_uch.to_csv("uch.csv")
df_content.to_csv("content.csv")
df_record.to_csv("records.csv")