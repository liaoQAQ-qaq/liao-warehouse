import pyodbc

# 把下面这个路径换成你 dpkg -L 查到的 libtdsodbc.so 路径
DRIVER_PATH = "/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so"

conn_str = (
    f"DRIVER={DRIVER_PATH};"
    "SERVER=192.168.7.72;"      # 例如 192.168.1.10 或 主机名
    "PORT=1435;"
    "DATABASE=sde;"        # 例如 DB1
    "UID=sa;"
    "PWD=zhuquezhihui1234!;"
    "TDS_Version=7.4;"
)

print("使用连接字符串：", conn_str)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT @@VERSION")
row = cursor.fetchone()
print("SQL Server 版本：")
print(row[0])

cursor.close()
conn.close()
