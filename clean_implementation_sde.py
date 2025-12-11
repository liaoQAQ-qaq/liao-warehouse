import pyodbc

# ===================== 数据库配置 =====================
# 保持与造数脚本一致
DB_CONFIG = {
    "server": "192.168.7.72",
    "port": 1436,
    "database": "sde",
    "user": "sa",
    "password": "zhuquezhihui1234!",
}
DRIVER_PATH = "/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so"

# ===================== 目标表列表 =====================
# 只针对那12张表进行清理
TARGET_TABLES = [
    "储备要点_问数测试",
    "国家级开发范围_问数测试",
    "土地供应_问数测试",
    "土地征收范围_问数测试",
    "建筑工程许可证_问数测试",
    "成片开发范围_问数测试",
    "新增建设用地报批_问数测试",
    "用地许可证_问数测试",
    "省级开发范围_问数测试",
    "规划条件_问数测试",
    "规划条件核实证明_问数测试",
    "选址意见书_问数测试"
]

def get_conn():
    conn_str = (
        f"DRIVER={DRIVER_PATH};"
        f"SERVER={DB_CONFIG['server']};"
        f"PORT={DB_CONFIG['port']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['user']};"
        f"PWD={DB_CONFIG['password']};"
        "TDS_Version=7.4;"
    )
    return pyodbc.connect(conn_str)

def clean_tables():
    print("⚠️  警告：该操作将【永久清空】以下表的所有数据，并将 ID 重置为 1：")
    for t in TARGET_TABLES:
        print(f"   - [sde].[{t}]")
    
    confirm = input("\n❓ 确认要执行吗？(输入 yes 确认): ")
    if confirm.lower() != "yes":
        print("已取消操作。")
        return

    conn = None
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        print("\n🚀 开始清理...")
        
        for table in TARGET_TABLES:
            full_name = f"[sde].[{table}]"
            try:
                # 使用 TRUNCATE 清空数据并重置自增 ID
                # 如果表有外键约束，需要改用 DELETE FROM
                sql = f"TRUNCATE TABLE {full_name}"
                cursor.execute(sql)
                print(f"✅ 已清空: {full_name}")
            except Exception as e:
                print(f"❌ 清理失败 {full_name}: {e}")
                # 如果 TRUNCATE 失败（例如权限问题），尝试 DELETE
                try:
                    print(f"   🔄 尝试使用 DELETE 清除 {full_name}...")
                    cursor.execute(f"DELETE FROM {full_name}")
                    print(f"   ✅ DELETE 成功: {full_name}")
                except Exception as e2:
                    print(f"   ❌ DELETE 也失败: {e2}")

        conn.commit()
        print("\n🏁 清理完成。现在您可以重新运行造数脚本了。")

    except Exception as e:
        print(f"❌ 数据库连接或执行错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clean_tables()