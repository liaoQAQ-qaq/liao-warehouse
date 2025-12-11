# -*- coding: utf-8 -*-
import random
import uuid
from faker import Faker
import pyodbc

fake = Faker("zh_CN")

# 每个表目标行数
ROWS_PER_TABLE = 400

# FreeTDS 驱动真实路径
DRIVER_PATH = "/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so"

# 一些通用枚举值，尽量贴合你的字段含义
# 武汉市 13 区 + 156 个街道，保证“街道归属区”真实
DISTRICT_STREETS = {
    "江岸区": [
        "大智街道", "车站街道", "一元街道", "永清街道", "四唯街道", "球场街道",
        "西马街道", "花桥街道", "台北街道", "劳动街道", "二七街道", "新村街道",
        "丹水池街道", "谌家矶街道", "后湖街道", "塔子湖街道",
    ],
    "江汉区": [
        "民族街道", "满春街道", "前进街道", "民权街道", "民意街道", "万松街道",
        "新华街道", "北湖街道", "花楼街道", "水塔街道", "常青街道", "汉兴街道",
        "唐家墩街道",
    ],
    "硚口区": [
        "宗关街道", "宝丰街道", "荣华街道", "古田街道", "汉中街道", "汉正街道",
        "易家街道", "韩家墩街道", "汉水桥街道", "六角亭街道", "长丰街道",
    ],
    "汉阳区": [
        "晴川街道", "建桥街道", "鹦鹉街道", "洲头街道", "五里墩街道", "琴断口街道",
        "江汉二桥街道", "永丰街道", "江堤街道", "龙阳街道", "四新街道",
    ],
    "武昌区": [
        "杨园街道", "南湖街道", "粮道街道", "紫阳街道", "徐家棚街道", "石洞街道",
        "积玉桥街道", "中华路街道", "黄鹤楼街道", "白沙洲街道", "首义路街道",
        "中南路街道", "水果湖街道", "珞珈山街道",
    ],
    "青山区": [
        "冶金街道", "武东街道", "红卫路街道", "钢花村街道", "新沟桥街道",
        "红钢城街道", "工人村街道", "青山镇街道", "白玉山街道", "钢都花园街道",
    ],
    "洪山区": [
        "关山街道", "珞南街道", "狮子山街道", "卓刀泉街道", "梨园街道", "张家湾街道",
        "和平街道", "洪山街道", "花山街道", "八吉府街道", "青菱街道",
        "左岭街道", "九峰街道",
    ],
    "东西湖区": [
        "吴家山街道", "长青街道", "慈惠街道", "走马岭街道", "径河街道", "金银湖街道",
        "将军路街道", "新沟镇街道", "柏泉街道", "东山街道", "辛安渡街道",
    ],
    "汉南区": [
        "纱帽街道", "湘口街道", "东荆街道", "邓南街道",
    ],
    "蔡甸区": [
        "蔡甸街道", "张湾街道", "侏儒山街道", "永安街道", "奓山街道", "大集街道",
        "沌口街道", "沌阳街道", "军山街道", "索河街道", "玉贤街道",
    ],
    "江夏区": [
        "纸坊街道", "龙泉街道", "金口街道", "郑店街道", "乌龙泉街道", "五里界街道",
        "安山街道", "豹澥街道", "关东街道", "佛祖岭街道", "滨湖街道", "山坡街道",
        "法泗街道", "湖泗街道", "舒安街道",
    ],
    "黄陂区": [
        "前川街道", "横店街道", "滠口街道", "天河街道", "六指街道", "祁家湾街道",
        "罗汉寺街道", "武湖街道", "长轩岭街道", "王家河街道", "李家集街道",
        "姚家集街道", "蔡家榨街道", "三里桥街道", "蔡店街道",
    ],
    "新洲区": [
        "邾城街道", "阳逻街道", "仓埠街道", "李集街道", "三店街道", "汪集街道",
        "旧街街道", "双柳街道", "潘塘街道", "涨渡湖街道", "辛冲街道", "徐古街道",
    ],
}

ALL_DISTRICTS = list(DISTRICT_STREETS.keys())


def pick_district_and_street():
    """随机选一个【区 + 该区下的街道】"""
    district = random.choice(ALL_DISTRICTS)
    street = random.choice(DISTRICT_STREETS[district])
    return district, street

LAND_TYPES = [
    ("0101", "水田"),
    ("0201", "旱地"),
    ("0302", "园地"),
    ("0501", "城镇用地"),
    ("0601", "工业用地"),
    ("0701", "交通运输用地"),
]
QSXZ_CHOICES = ["国有", "集体", "个人", "其他"]
MAIN_CITY_FLAGS = ["中心城区", "近郊", "远郊"]
RING_LEVELS = ["二环内", "二环至三环", "三环至四环", "四环外"]
KEY_ZONE_FLAGS = ["重点发展区", "限制建设区", "生态保护区", "一般区域"]
INDUSTRIAL_PARK_FLAGS = ["一般工业园区", "高新产业园", "物流园区", "无"]

# ---------- 连接配置：这里只做“现状底图数据库（sde，1435 端口）” ----------
DB_CONFIGS = {
    "xzdt": {   # label；只是脚本内部使用的名字
        "server": "192.168.7.72",
        "port": 1435,
        "database": "sde",
        "user": "sa",
        "password": "zhuquezhihui1234!",
    }
}


def get_connection(label: str, conf: dict):
    """通过 FreeTDS 连接 SQL Server"""
    server = conf["server"]
    port = conf["port"]
    database = conf["database"]
    user = conf["user"]
    password = conf["password"]

    conn_str = (
        f"DRIVER={DRIVER_PATH};"
        f"SERVER={server};"
        f"PORT={port};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        "TDS_Version=7.4;"
    )

    print(f"  使用连接: {server},{port} / DB={database}")
    return pyodbc.connect(conn_str)


def pick_land_type():
    return random.choice(LAND_TYPES)


# --------------------- 六张表的造数函数（按字段含义造） ---------------------


def gen_zd_row(i: int):
    """sde.使用权宗地_问数测试"""
    year = random.choice([2020, 2021, 2022, 2023, 2024])
    district, street = pick_district_and_street()  # ✅ 真实区 + 街道
    qlr = fake.name()

    return (
        qlr,                                        # QLR 权利人
        f"ZDDM{year}{i:06d}",                       # ZDDM 宗地代码
        f"BD{year}{i:08d}",                         # BDCDYH 不动产单元号
        round(random.uniform(50, 5000), 2),         # ZDMJ 宗地面积
        f"CLGC-{year}-{i:04d}",                     # CLGCH 测量工程号
        fake.date_time_between("-3y", "now"),       # DRSJ 导入时间
        random.choice(["正常", "注销", "冻结"]),      # ZDZT 宗地状态
        fake.date_time_between("-3y", "now"),       # DJSJ 登记时间
        f"{district}{street}{fake.street_address()}",  # ZL 坐落
        f"YZD{year-1}{i:06d}",                      # YZDDM 原宗地代码
        f"{year}年第{(i % 5) + 1}批",               # QUSHU 取数批次
        fake.name(),                                # CZY 操作员
        fake.date_time_between("-3y", "now"),       # CZSJ 操作时间
        "测试数据",                                  # BZ 备注
        random.choice(["有效", "无效"]),             # STATUS 状态
        f"YSDM{random.randint(1, 999):03d}",        # YSDM 要素代码
        f"TZM{year}{i:06d}",                        # ZDTZM 宗地特征码
        "平方米",                                   # MJDW 面积单位
        random.choice(["住宅用地", "工业用地", "商业用地"]),  # YT 用途
        random.choice(["一级", "二级", "三级"]),     # DJ 等级
        round(random.uniform(1000, 30000), 2),      # JG 价格
        random.choice(["国有出让", "国有划拨", "集体建设用地"]),  # QLLX
        random.choice(["国有", "集体", "个人"]),     # QLXZ
        random.choice(["出让", "划拨", "作价出资"]), # QLSDFS
        round(random.uniform(0.5, 5.0), 2),         # RJL 容积率
        round(random.uniform(0.1, 0.8), 2),         # JZMD 建筑密度
        round(random.uniform(10, 100), 1),          # JZXG 建筑限高
        f"东至{fake.street_name()}",                # ZDSZD
        f"西至{fake.street_name()}",                # ZDSZX
        f"南至{fake.street_name()}",                # ZDSZN
        f"北至{fake.street_name()}",                # ZDSZB
        f"TFH{year}{i:04d}",                        # TFH 图幅号
        f"DJH{year}{i:04d}",                        # DJH 地籍号
        f"DA{year}{i:06d}",                         # DAH 档案号
        random.choice(["在用", "注销", "过渡"]),     # ZT 不动产单元状态
        random.choice(["基准宗地", "分割宗地", "合并宗地"]),  # ZDTYPE
        "入库通过",                                  # RFJGYSYJ
        f"YW{year}{i:06d}",                         # 业务码
        f"DK{year}{i:06d}",                         # 地块码
        str(uuid.uuid4()),                          # uuid
        district,                                   # 所属区 —— 必须是真实区
        f"DKZX-{year}-{i:06d}",                     # QM_DKZX
        district,                                   # GZQH_GLQMC 行政区/工作区划
        str(year),                                  # ssnf 所属年份
        random.choice([0, 1]),                      # 人工判断为重复地块
        qlr,                                        # QLR_原始
        random.choice([0, 1]),                      # 是否历史数据
    )


def gen_td2020_row(i: int):
    """sde.土地利用现状2020_问数测试"""
    year = 2020
    district, street = pick_district_and_street()
    code, name = pick_land_type()

    base = f"{year}{i:06d}"
    tbmj = round(random.uniform(10, 1000), 2)
    tbdlmj = round(random.uniform(10, tbmj), 2)
    kcxs = round(random.uniform(0.1, 1.0), 2)
    kcmj = round(tbmj * kcxs * random.uniform(0.2, 0.8), 2)

    return (
        base,                                       # BSM
        f"YSDM{random.randint(1, 999):03d}",        # YSDM
        f"TBY{base}",                               # TBYBH
        f"TBB{base}",                               # TBBH
        code,                                       # DLBM
        name,                                       # DLMC
        random.choice(QSXZ_CHOICES),               # QSXZ
        f"QSDW{random.randint(100, 999)}",          # QSDWDM
        f"{district}自然资源局",                     # QSDWMC
        f"ZLDW{random.randint(100, 999)}",          # ZLDWDM
        f"{district}{street}",                      # ZLDWMC
        tbmj,                                       # TBMJ
        code,                                       # KCDLBM
        kcxs,                                       # KCXS
        kcmj,                                       # KCMJ
        tbdlmj,                                     # TBDLMJ
        random.choice(["水田", "水浇地", "旱地"]),   # GDLX
        random.choice(["一等", "二等", "三等"]),     # GDPDJB
        round(random.uniform(0.5, 10.0), 2),        # XZDWKD
        f"TBXH{random.randint(1, 999):03d}",        # TBXHDM
        random.choice(["基本农田", "一般农用地", "建设用地"]),  # TBXHMC
        f"ZZ{random.randint(1, 999):03d}",          # ZZSXDM
        random.choice(["粮食作物", "经济作物", "园林作物"]),   # ZZSXMC
        random.randint(1, 15),                      # GDDB
        random.choice(["是", "否"]),                # FRDBS
        random.choice(["城镇", "建制镇", "村庄"]),  # CZCSXM
        f"{year}年土地利用现状图斑{i}",             # MSSM
        "无",                                       # HDMC
        "测试数据",                                  # BZ
        random.choice(["调整前", "调整后", "未调整"]), # XZQTZLX
        random.choice(["农用地", "建设用地", "未利用地"]),   # 分类
        "DL01",                                     # DL
        "DL01中类",                                  # DL中
        round(tbmj * random.uniform(0.9, 1.1), 2),  # 图形面积
        str(uuid.uuid4()),                          # suuid
        district,                                   # 行政区
        district,                                   # GZQH_GLQMC
        f"DKZX-{year}-{i:06d}",                     # QM_DKZX
    )


def gen_td2021_row(i: int):
    """sde.土地利用现状2021_问数测试"""
    year = 2021
    district, street = pick_district_and_street()
    code, name = pick_land_type()
    tbmj = round(random.uniform(10, 1000), 2)
    tbdlmj = round(random.uniform(10, tbmj), 2)

    return (
        f"{year}{i:06d}",                           # BSM
        code,                                       # DLBM
        name,                                       # DLMC
        random.choice(QSXZ_CHOICES),               # QSXZ
        f"{district}自然资源局",                     # QSDWMC
        f"{district}{street}",                      # ZLDWMC
        tbmj,                                       # TBMJ
        tbdlmj,                                     # TBDLMJ
        random.choice(["一等", "二等", "三等"]),     # GDPDJB
        random.choice(["基本农田", "一般农用地", "建设用地"]),  # TBXHMC
        random.choice(["粮食作物", "经济作物", "园林作物"]),   # ZZSXMC
        random.choice(["城镇", "建制镇", "村庄"]),  # CZCSXM
        f"DKZX-{year}-{i:06d}",                     # QM_DKZX
        random.choice(MAIN_CITY_FLAGS),             # 主城区
        street,                                     # 所属街道
        random.choice(RING_LEVELS),                 # 环线
        random.choice(KEY_ZONE_FLAGS),              # 重点功能区
        random.choice(["是", "否"]),                # 新两园
        random.choice(INDUSTRIAL_PARK_FLAGS),       # 工业园区
        district,                                   # 行政区
        district,                                   # GZQH_GLQMC
    )



def gen_td2022_row(i: int):
    """sde.土地利用现状2022_问数测试"""
    year = 2022
    district, street = pick_district_and_street()
    code, name = pick_land_type()
    tbmj = round(random.uniform(10, 1000), 2)
    kcxs = round(random.uniform(0.1, 1.0), 2)
    tbdlmj = round(random.uniform(10, tbmj), 2)

    return (
        f"{year}{i:06d}",                           # BSM
        code,                                       # DLBM
        name,                                       # DLMC
        random.choice(QSXZ_CHOICES),               # QSXZ
        f"QSDW{random.randint(100, 999)}",          # QSDWDM
        f"{district}自然资源局",                     # QSDWMC
        f"ZLDW{random.randint(100, 999)}",          # ZLDWDM
        f"{district}{street}",                      # ZLDWMC
        tbmj,                                       # TBMJ
        kcxs,                                       # KCXS
        tbdlmj,                                     # TBDLMJ
        random.choice(["水田", "水浇地", "旱地"]),   # GDLX
        random.choice(["一等", "二等", "三等"]),     # GDPDJB
        random.choice(["基本农田", "一般农用地", "建设用地"]),  # TBXHMC
        random.choice(["粮食作物", "经济作物", "园林作物"]),   # ZZSXMC
        str(uuid.uuid4()),                          # Suuid
        district,                                   # 所属区
        f"DKZX-{year}-{i:06d}",                     # QM_DKZX
        street,                                     # 所属街道
        random.choice(MAIN_CITY_FLAGS),             # 主城区
        random.choice(RING_LEVELS),                 # 环线
        random.choice(INDUSTRIAL_PARK_FLAGS),       # 工业园区
        random.choice(KEY_ZONE_FLAGS),              # 重点功能区
        district,                                   # GZQH_GLQMC
    )



def gen_td2023_row(i: int):
    """sde.土地利用现状2023_问数测试"""
    year = 2023
    district, street = pick_district_and_street()
    code, name = pick_land_type()
    tbmj = round(random.uniform(10, 1000), 2)
    kcxs = round(random.uniform(0.1, 1.0), 2)
    kcmj = round(tbmj * kcxs * random.uniform(0.2, 0.8), 2)
    tbdlmj = round(random.uniform(10, tbmj), 2)

    return (
        code,                                       # DLBM
        name,                                       # DLMC
        f"{district}{street}",                      # ZLDWMC
        tbdlmj,                                     # TBDLMJ
        random.choice(["基本农田", "一般农用地", "建设用地"]),  # TBXHMC
        random.choice(["粮食作物", "经济作物", "园林作物"]),   # ZZSXMC
        random.choice(["城镇", "建制镇", "村庄"]),  # CZCSXM
        f"{year}{i:06d}",                           # BSM
        code,                                       # KCDLBM
        kcxs,                                       # KCXS
        kcmj,                                       # KCMJ
        random.choice(QSXZ_CHOICES),               # QSXZ
        f"{district}自然资源局",                     # QSDWMC
        tbmj,                                       # TBMJ
        random.choice(["一等", "二等", "三等"]),     # GDPDJB
        random.choice(["是", "否"]),                # FRDBS
        f"DKM{year}{i:06d}",                        # dkm
        str(uuid.uuid4()),                          # Suuid
        district,                                   # 所属区
        f"DKZX-{year}-{i:06d}",                     # QM_DKZX
        street,                                     # 所属街道
        random.choice(MAIN_CITY_FLAGS),             # 主城区
        random.choice(RING_LEVELS),                 # 环线
        random.choice(INDUSTRIAL_PARK_FLAGS),       # 工业园区
        random.choice(KEY_ZONE_FLAGS),              # 重点功能区
        district,                                   # GZQH_GLQMC
        random.choice(["农用地", "建设用地", "未利用地"]),  # 土地管理类别
    )

def gen_td2024_row(i: int):
    """sde.土地利用现状2024_问数测试"""
    year = 2024
    district, street = pick_district_and_street()
    code, name = pick_land_type()
    tbmj = round(random.uniform(10, 1000), 2)
    kcxs = round(random.uniform(0.1, 1.0), 2)
    kcmj = round(tbmj * kcxs * random.uniform(0.2, 0.8), 2)
    tbdlmj = round(random.uniform(10, tbmj), 2)

    return (
        f"{year}{i:06d}",                           # BSM
        f"YSDM{random.randint(1, 999):03d}",        # YSDM
        f"TBY{year}{i:06d}",                        # TBYBH
        f"TBB{year}{i:06d}",                        # TBBH
        code,                                       # DLBM
        name,                                       # DLMC
        random.choice(QSXZ_CHOICES),               # QSXZ
        f"QSDW{random.randint(100, 999)}",          # QSDWDM
        f"{district}自然资源局",                     # QSDWMC
        f"ZLDW{random.randint(100, 999)}",          # ZLDWDM
        f"{district}{street}",                      # ZLDWMC
        tbmj,                                       # TBMJ
        code,                                       # KCDLBM
        kcxs,                                       # KCXS
        kcmj,                                       # KCMJ
        tbdlmj,                                     # TBDLMJ
        random.choice(["水田", "水浇地", "旱地"]),   # GDLX
        random.choice(["一等", "二等", "三等"]),     # GDPDJB
        round(random.uniform(0.5, 10.0), 2),        # XZDWKD
        f"TBXH{random.randint(1, 999):03d}",        # TBXHDM
        random.choice(["基本农田", "一般农用地", "建设用地"]),  # TBXHMC
        f"ZZ{random.randint(1, 999):03d}",          # ZZSXDM
        random.choice(["粮食作物", "经济作物", "园林作物"]),   # ZZSXMC
        random.randint(1, 15),                      # GDDB
        random.choice(["是", "否"]),                # FRDBS
        random.choice(["城镇", "建制镇", "村庄"]),  # CZCSXM
        year,                                       # SJNF
        f"{year}年土地利用现状图斑{i}",             # MSSM
        "无",                                       # HDMC
        "测试数据",                                  # BZ
        str(uuid.uuid4()),                          # Suuid
        district,                                   # GZQH_GLQMC（工作区划/行政区）
        f"DKZX-{year}-{i:06d}",                     # QM_DKZX
        district,                                   # 所属区
        street,                                     # 所属街道
        random.choice(MAIN_CITY_FLAGS),             # 主城区
        random.choice(RING_LEVELS),                 # 环线
        random.choice(KEY_ZONE_FLAGS),              # 重点功能区
        random.choice(INDUSTRIAL_PARK_FLAGS),       # 工业园区
        random.choice(["农用地", "建设用地", "未利用地"]),  # 土地管理类别
        f"D{code}",                                 # 大类编码
        f"{name}大类",                              # 大类名称
    )


# --------------------- TABLE_CONFIGS：六张表全部字段 ---------------------

TABLE_CONFIGS = {
    "xzdt": {
        "使用权宗地_问数测试": {
            "schema": "sde",
            "insert_sql": """
                INSERT INTO [sde].[使用权宗地_问数测试] (
                    [QLR],[ZDDM],[BDCDYH],[ZDMJ],[CLGCH],[DRSJ],[ZDZT],[DJSJ],[ZL],[YZDDM],
                    [QUSHU],[CZY],[CZSJ],[BZ],[STATUS],[YSDM],[ZDTZM],[MJDW],[YT],[DJ],
                    [JG],[QLLX],[QLXZ],[QLSDFS],[RJL],[JZMD],[JZXG],[ZDSZD],[ZDSZX],[ZDSZN],
                    [ZDSZB],[TFH],[DJH],[DAH],[ZT],[ZDTYPE],[RFJGYSYJ],[业务码],[地块码],[uuid],
                    [所属区],[QM_DKZX],[GZQH_GLQMC],[ssnf],[人工判断为重复地块],[QLR_原始],[是否历史数据]
                )
                        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?
        )

            """,
            "row_generator": gen_zd_row,
        },

        "土地利用现状2020_问数测试": {
            "schema": "sde",
            "insert_sql": """
                INSERT INTO [sde].[土地利用现状2020_问数测试] (
                    [BSM],[YSDM],[TBYBH],[TBBH],[DLBM],[DLMC],[QSXZ],[QSDWDM],[QSDWMC],[ZLDWDM],
                    [ZLDWMC],[TBMJ],[KCDLBM],[KCXS],[KCMJ],[TBDLMJ],[GDLX],[GDPDJB],[XZDWKD],[TBXHDM],
                    [TBXHMC],[ZZSXDM],[ZZSXMC],[GDDB],[FRDBS],[CZCSXM],[MSSM],[HDMC],[BZ],[XZQTZLX],
                    [分类],[DL],[DL中],[图形面积],[suuid],[行政区],[GZQH_GLQMC],[QM_DKZX]
                )
                VALUES (
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?
                )
            """,
            "row_generator": gen_td2020_row,
        },

        "土地利用现状2021_问数测试": {
            "schema": "sde",
            "insert_sql": """
                INSERT INTO [sde].[土地利用现状2021_问数测试] (
                    [BSM],[DLBM],[DLMC],[QSXZ],[QSDWMC],[ZLDWMC],[TBMJ],[TBDLMJ],[GDPDJB],[TBXHMC],
                    [ZZSXMC],[CZCSXM],[QM_DKZX],[主城区],[所属街道],[环线],[重点功能区],[新两园],[工业园区],
                    [行政区],[GZQH_GLQMC]
                )
                VALUES (
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?
                )
            """,
            "row_generator": gen_td2021_row,
        },

        "土地利用现状2022_问数测试": {
            "schema": "sde",
            "insert_sql": """
                INSERT INTO [sde].[土地利用现状2022_问数测试] (
                    [BSM],[DLBM],[DLMC],[QSXZ],[QSDWDM],[QSDWMC],[ZLDWDM],[ZLDWMC],[TBMJ],[KCXS],
                    [TBDLMJ],[GDLX],[GDPDJB],[TBXHMC],[ZZSXMC],[Suuid],[所属区],[QM_DKZX],[所属街道],
                    [主城区],[环线],[工业园区],[重点功能区],[GZQH_GLQMC]
                )
                VALUES (
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?
                )
            """,
            "row_generator": gen_td2022_row,
        },

        "土地利用现状2023_问数测试": {
            "schema": "sde",
            "insert_sql": """
                INSERT INTO [sde].[土地利用现状2023_问数测试] (
                    [DLBM],[DLMC],[ZLDWMC],[TBDLMJ],[TBXHMC],[ZZSXMC],[CZCSXM],[BSM],[KCDLBM],[KCXS],
                    [KCMJ],[QSXZ],[QSDWMC],[TBMJ],[GDPDJB],[FRDBS],[dkm],[Suuid],[所属区],[QM_DKZX],
                    [所属街道],[主城区],[环线],[工业园区],[重点功能区],[GZQH_GLQMC],[土地管理类别]
                )
                VALUES (
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?
                )
            """,
            "row_generator": gen_td2023_row,
        },

        "土地利用现状2024_问数测试": {
            "schema": "sde",
            "insert_sql": """
                INSERT INTO [sde].[土地利用现状2024_问数测试] (
                    [BSM],[YSDM],[TBYBH],[TBBH],[DLBM],[DLMC],[QSXZ],[QSDWDM],[QSDWMC],[ZLDWDM],
                    [ZLDWMC],[TBMJ],[KCDLBM],[KCXS],[KCMJ],[TBDLMJ],[GDLX],[GDPDJB],[XZDWKD],[TBXHDM],
                    [TBXHMC],[ZZSXDM],[ZZSXMC],[GDDB],[FRDBS],[CZCSXM],[SJNF],[MSSM],[HDMC],[BZ],
                    [Suuid],[GZQH_GLQMC],[QM_DKZX],[所属区],[所属街道],[主城区],[环线],[重点功能区],[工业园区],
                    [土地管理类别],[大类编码],[大类名称]
                )
                VALUES (
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,
                    ?,?,?
                )
            """,
            "row_generator": gen_td2024_row,
        },
    }
}
def fill_one_table(conn_label: str, table_name: str, conn, table_conf: dict):
    """给某个连接下的一张表补齐到 ROWS_PER_TABLE 行"""
    schema = table_conf.get("schema", "dbo")
    full_table = f"[{schema}].[{table_name}]"

    print(f"▶ 正在处理连接的表 {full_table} ...")
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {full_table}")
    current_rows = cursor.fetchone()[0]
    print(f"   当前行数: {current_rows}")

    need = ROWS_PER_TABLE - current_rows
    if need <= 0:
        print(f"   已经 >= {ROWS_PER_TABLE} 行，跳过。")
        return

    print(f"   需要新增: {need} 行")

    rows = [table_conf["row_generator"](i) for i in range(need)]

    
    cursor.executemany(table_conf["insert_sql"], rows)
    conn.commit()
    print(f"   已插入 {need} 行 ✅")


def main():
    for label, conf in DB_CONFIGS.items():
        if label not in TABLE_CONFIGS:
            continue

        print("\n==============================")
        print(f"连接到: {label}")
        print("==============================")

        conn = get_connection(label, conf)

        try:
            for table_name, table_conf in TABLE_CONFIGS[label].items():
                fill_one_table(label, table_name, conn, table_conf)
        finally:
            conn.close()
            print(f"关闭连接: {label}\n")


def debug_check():
    conn = get_connection("xzdt", DB_CONFIGS["xzdt"])
    cur = conn.cursor()
    for tbl in [
        "使用权宗地_问数测试",
        "土地利用现状2020_问数测试",
        "土地利用现状2021_问数测试",
        "土地利用现状2022_问数测试",
        "土地利用现状2023_问数测试",
        "土地利用现状2024_问数测试",
    ]:
        cur.execute(f"SELECT COUNT(*) FROM [sde].[{tbl}]")
        print(tbl, "=>", cur.fetchone()[0])
    conn.close()
    
if __name__ == "__main__":
    main()
