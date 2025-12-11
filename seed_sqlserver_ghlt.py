import random
from faker import Faker
from datetime import datetime, timedelta
import pyodbc

# ===================== 基本配置 =====================
fake = Faker("zh_CN")

# 每张表目标行数
ROWS_PER_TABLE = 400

# FreeTDS 驱动路径（你之前已经验证过）
DRIVER_PATH = "/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so"

# 规划蓝图数据库连接配置（端口 1434）
DB_CONFIG = {
    "server": "192.168.7.72",
    "port": 1434,
    "database": "sde",
    "user": "sa",
    "password": "zhuquezhihui1234!",
}

# ===================== 武汉市 区 / 街道全局规则 =====================
WUHAN_DISTRICT_STREETS = {
    "江岸区": ["大智街道","车站街道","一元街道","永清街道","四唯街道","球场街道","西马街道","花桥街道","台北街道","劳动街道","二七街道","新村街道","丹水池街道","谌家矶街道","后湖街道","塔子湖街道"],
    "江汉区": ["民族街道","满春街道","前进街道","民权街道","民意街道","万松街道","新华街道","北湖街道","花楼街道","水塔街道","常青街道","汉兴街道","唐家墩街道"],
    "硚口区": ["宗关街道","宝丰街道","荣华街道","古田街道","汉中街道","汉正街道","易家街道","韩家墩街道","汉水桥街道","六角亭街道","长丰街道"],
    "汉阳区": ["晴川街道","建桥街道","鹦鹉街道","洲头街道","五里墩街道","琴断口街道","江汉二桥街道","永丰街道","江堤街道","龙阳街道","四新街道"],
    "武昌区": ["杨园街道","南湖街道","粮道街道","紫阳街道","徐家棚街道","石洞街道","积玉桥街道","中华路街道","黄鹤楼街道","白沙洲街道","首义路街道","中南路街道","水果湖街道","珞珈山街道"],
    "青山区": ["冶金街道","武东街道","红卫路街道","钢花村街道","新沟桥街道","红钢城街道","工人村街道","青山镇街道","白玉山街道","钢都花园街道"],
    "洪山区": ["关山街道","珞南街道","狮子山街道","卓刀泉街道","梨园街道","张家湾街道","和平街道","洪山街道","花山街道","八吉府街道","青菱街道","左岭街道","九峰街道"],
    "东西湖区": ["吴家山街道","长青街道","慈惠街道","走马岭街道","径河街道","金银湖街道","将军路街道","新沟镇街道","柏泉街道","东山街道","辛安渡街道"],
    "汉南区": ["纱帽街道","湘口街道","东荆街道","邓南街道"],
    "蔡甸区": ["蔡甸街道","张湾街道","侏儒山街道","永安街道","奓山街道","大集街道","沌口街道","沌阳街道","军山街道","索河街道","玉贤街道"],
    "江夏区": ["纸坊街道","龙泉街道","金口街道","郑店街道","乌龙泉街道","五里界街道","安山街道","豹澥街道","关东街道","佛祖岭街道","滨湖街道","山坡街道","法泗街道","湖泗街道","舒安街道"],
    "黄陂区": ["前川街道","横店街道","滠口街道","天河街道","六指街道","祁家湾街道","罗汉寺街道","武湖街道","长轩岭街道","王家河街道","李家集街道","姚家集街道","蔡家榨街道","三里桥街道","蔡店街道"],
    "新洲区": ["邾城街道","阳逻街道","仓埠街道","李集街道","三店街道","汪集街道","旧街街道","双柳街道","潘塘街道","涨渡湖街道","辛冲街道","徐古街道"],
}

MAIN_URBAN_DISTRICTS = {"江岸区","江汉区","硚口区","汉阳区","武昌区","青山区","洪山区"}

RING_LEVELS = ["二环内","二环-三环","三环-四环","四环外"]
KEY_FUNC_ZONES = ["普通功能区","中心城区重点功能区","新城发展组团","生态功能区"]
NEW_TWO_PARKS_OPTIONS = ["", "新两园重点片区"]
INDUSTRIAL_PARK_OPTIONS = ["", "工业园区", "开发区园区"]


def random_admin_info():
    """
    统一生成：区 / 街道 / 主城区标识 / 环线 / 重点功能区 / 新两园 / 工业园区 / 社区 / 工作区划 / QM_DKZX
    所有“主城区 / 所属街道 / 环线 / 重点功能区 / 新两园 / 工业园区 / 所属社区 / GZQH_GLQMC / QM_DKZX”
    都从这里走，保证和上一个数据库脚本的规则统一。
    """
    qu = random.choice(list(WUHAN_DISTRICT_STREETS.keys()))
    street = random.choice(WUHAN_DISTRICT_STREETS[qu])
    main_city = "主城区" if qu in MAIN_URBAN_DISTRICTS else "新城区"
    ring = random.choice(RING_LEVELS)
    key_zone = random.choice(KEY_FUNC_ZONES)
    new_two_parks = random.choice(NEW_TWO_PARKS_OPTIONS)
    industrial_park = random.choice(INDUSTRIAL_PARK_OPTIONS)
    community = street.replace("街道", "社区")
    gzqh = qu
    qm_dkzx = f"{qu[:2]}-{random.randint(1, 999):03d}"

    return {
        "qu": qu,
        "street": street,
        "main_city": main_city,
        "ring": ring,
        "key_zone": key_zone,
        "new_two_parks": new_two_parks,
        "industrial_park": industrial_park,
        "community": community,
        "gzqh": gzqh,
        "qm_dkzx": qm_dkzx,
    }


# ===================== 各表字段列表（用于生成 INSERT SQL） =====================
COLS_POI = ["id_old","name","type","typeCode","bizType","address","tel","pname","cityName","adName","date","一类","二类","三类","QM_DKZX","主城区","所属街道","环线","重点功能区","新两园","工业园区","设施大类","设施小类","等时圈ID","GZQH_GLQMC"]

COLS_CKBJ = ["BSM","YSDM","XZQDM","XZQMC","GHFQDM","GHFQMC","BZ","MJ_YS","MJ_YS_DOUBLE","MJ_TQ","MJ","GZQH_GLQMC"]

COLS_JBNT_CZ = [
 "BSM","YSDM","TBBH","DLBM","DLMC","QSXZ","QSDWDM","ZLDWDM","KCDLBM",
 "KCXS","KCMJ","GDLX","GDPDJB","TBXHDM","TBXHMC","ZZSXDM","ZZSXMC","GDDB",
 "FRDBS","SJNF","BZ","XZQDM","XZQMC","YJJBNTTBBH","GGBZL","GDDJ","ZLFLDM",
 "CFZR","ZMC","ZZRR","ZRRZJHM","ZRRMC","LXDH","BHKSSJ","BHJSSJ","SJBH",
 "SJMC","ZRSYX","WDGD","SFWYYJJBNT","JZDZ","YJJBNTTBMJ","YJJBNTMJ","QSDWMC",
 "ZLDWMC","CZKFBJBH","CN","CZLXDM","YJJBNTLX","GZQH_GLQMC","处置类型","永久基本农田类型"
]

COLS_STBH_HX = [
 "BSM","YSDM","XZQDM","XZQMC","SHENG","SHI","XIAN","HXBM","HXLX","LXBM",
 "MJ","ZRBHDJB","ZRBHDLX","ZRBHDFQ","SZXJXZQDM","SZXJXZQMC","BZ","HXMC",
 "ZRBHDMC","XTYZBLX","GKCS","GZQH_GLQMC"
]

COLS_GD_BHMB = [
 "OBJECTID_1","BSM","YSDM","TBYBH","TBBH","DLBM","DLMC","QSXZ","QSDWDM",
 "ZLDWDM","TBMJ","KCDLBM","KCXS","KCMJ","TBDLMJ","GDLX","GDPDJB","TBXHDM",
 "TBXHMC","ZZSXDM","ZZSXMC","GDDB","FRDBS","SJNF","SFWHTD","QSDWMC","ZLDWMC",
 "TBMJ_YS","TBDLMJ_YS","KCMJ_YS","Shape_Leng","Shape_Le_1","Shape_Le_2",
 "ORIG_FID","GZQH_GLQMC"
]

COLS_RK2022 = [
 "DYBH","COUNT_Y0_2","COUNT_Y3_5","COUNT_Y6_1","COUNT_Y12_","COUNT_Y15_",
 "COUNT_Y18_","COUNT_Y36_","COUNT_Y65_","COUNT_","RKMD","sde_SDE_人口2022_AREA",
 "QM_DKZX","主城区","所属街道","环线","重点功能区","新两园","工业园区",
 "所属社区","GZQH_GLQMC"
]

COLS_ZZ_2023 = [
 "区片编号","土地级别","基准容积率","国有级别价","国有区片价",
 "宅基地级别价","宅基地区片价","租赁住房级别价","租赁住房区片价",
 "图形面积","QM_DKZX","GZQH_GLQMC"
]

COLS_GF_2023 = [
 "区片编号","土地级别","基准容积率","国有级别价","国有区片价",
 "集体级别价","集体区片价","图形面积","QM_DKZX","GZQH_GLQMC"
]

COLS_SY_2023 = [
 "区片编号","土地级别","国有级别价","国有区片价","集体级别价",
 "集体区片价","基准容积率","图形面积","QM_DKZX","GZQH_GLQMC"
]

COLS_SWBG_2023 = [
 "区片编号","土地级别","基准容积率","国有级别价","国有区片价",
 "集体级别价","集体区片价","图形面积","QM_DKZX","GZQH_GLQMC"
]

COLS_GY_2023 = [
 "区片编号","土地级别","基准容积率","国有级别价","国有区片价",
 "集体级别价","集体区片价","图形面积","QM_DKZX","GZQH_GLQMC"
]

COLS_STX_HY = [
 "生态线要求","TL","所属项目","审批审查状态","图形面积"
]

COLS_TYGLT = [
 "管理单元","强度分区","控制类别","控制类型","容积率","建筑密度",
 "建筑高度","绿地率","所属项目","景观设计","兼容情况","审批审查状态",
 "TL","用地性质","编制单元","特色生态管控","备注","城市设计控制要求",
 "海绵城市控制要求","地下空间控制要求","建设要求","YDXZ1","YDXZ2","图形面积"
]

COLS_ZH_2023 = [
 "土地级别","图形面积","QM_DKZX","GZQH_GLQMC"
]


# ===================== 行生成器（row_generator） =====================
def gen_poi_row(i: int):
    adm = random_admin_info()
    poi_types = [
        ("餐饮服务", "快餐厅", "中式快餐"),
        ("购物服务", "购物中心", "百货商店"),
        ("生活服务", "生活服务场所", "洗衣店"),
        ("公司企业", "公司企业", "科技公司"),
        ("科教文化服务", "科教文化", "培训机构"),
        ("交通设施服务", "公交车站", "公交站"),
        ("政府机构及社会团体", "政府机构", "街道办事处"),
    ]
    big, mid, small = random.choice(poi_types)

    id_old = f"POI{100000 + i}"
    name = fake.company()
    type_str = f"{big};{mid};{small}"
    type_code = random.randint(1000, 9999)
    biz_type = mid
    address = f"{adm['qu']}{adm['street']}{fake.street_address()}"
    tel = fake.phone_number()
    pname = "湖北省"
    city_name = "武汉市"
    ad_name = adm["qu"]
    date_int = int(fake.date_between("-3y", "today").strftime("%Y%m%d"))
    qm_dkzx = adm["qm_dkzx"]
    main_city = adm["main_city"]
    street = adm["street"]
    ring = adm["ring"]
    key_zone = adm["key_zone"]
    new_two_parks = adm["new_two_parks"]
    industrial_park = adm["industrial_park"]
    facility_big = big
    facility_small = small
    iso_id = f"ISO{random.randint(1,50):03d}"
    gzqh = adm["gzqh"]

    return (
        id_old,        # id_old
        name,          # name
        type_str,      # type
        type_code,     # typeCode
        biz_type,      # bizType
        address,       # address
        tel,           # tel
        pname,         # pname
        city_name,     # cityName
        ad_name,       # adName
        date_int,      # date
        big,           # 一类
        mid,           # 二类
        small,         # 三类
        qm_dkzx,       # QM_DKZX
        main_city,     # 主城区
        street,        # 所属街道
        ring,          # 环线
        key_zone,      # 重点功能区
        new_two_parks, # 新两园
        industrial_park, # 工业园区
        facility_big,  # 设施大类
        facility_small,# 设施小类
        iso_id,        # 等时圈ID
        gzqh           # GZQH_GLQMC
    )


def gen_ckbj_row(i: int):
    adm = random_admin_info()
    qu = adm["qu"]
    xzqdm = f"4201{random.randint(1, 13):02d}"
    ghfqdm = f"GHFQ{random.randint(1, 99):03d}"
    bsm = f"CKBJ{100000 + i}"
    ysdm = "2001010100"
    bz = f"自动生成的城镇开发边界测试数据{i}"
    mj_ys = round(random.uniform(10000, 500000), 2)
    mj_ys_double = float(mj_ys)
    mj_tq = round(mj_ys * random.uniform(0.8, 1.2), 2)
    mj = mj_tq

    return (
        bsm,          # BSM
        ysdm,         # YSDM
        xzqdm,        # XZQDM
        qu,           # XZQMC
        ghfqdm,       # GHFQDM
        f"{qu}规划分区{random.randint(1,5)}", # GHFQMC
        bz,           # BZ
        mj_ys,        # MJ_YS
        mj_ys_double, # MJ_YS_DOUBLE
        mj_tq,        # MJ_TQ
        mj,           # MJ
        adm["gzqh"],  # GZQH_GLQMC
    )


def gen_jbnt_cz_row(i: int):
    """
    三区三线_基本农田核实处置_问数测试
    字段顺序对齐：
    BSM, YSDM, TBBH, DLBM, DLMC, QSXZ, QSDWDM, ZLDWDM, KCDLBM,
    KCXS, KCMJ, GDLX, GDPDJB, TBXHDM, TBXHMC, ZZSXDM, ZZSXMC,
    GDDB, FRDBS, SJNF, BZ, XZQDM, XZQMC, YJJBNTTBBH, GGBZL, GDDJ,
    ZLFLDM, CFZR, ZMC, ZZRR, ZRRZJHM, ZRRMC, LXDH, BHKSSJ, BHJSSJ,
    SJBH, SJMC, ZRSYX, WDGD, SFWYYJJBNT, JZDZ, YJJBNTTBMJ, YJJBNTMJ,
    QSDWMC, ZLDWMC, CZKFBJBH, CN, CZLXDM, YJJBNTLX, GZQH_GLQMC, 处置类型, 永久基本农田类型
    """
    adm = random_admin_info()
    qu = adm["qu"]
    year = random.randint(2020, 2024)

    # 地类、性质、等别等基础字典
    dlbm_list = ["011", "012", "013", "021", "031"]
    dlmc_map = {
        "011": "水田",
        "012": "水浇地",
        "013": "旱地",
        "021": "园地",
        "031": "有林地",
    }
    qsxz_list = ["国有", "集体", "个人"]
    gdlx_list = ["水田", "旱地", "菜地"]
    gdpd_list = ["I", "II", "III", "IV"]
    zzsx_list = ["一年一熟", "一年两熟", "一年三熟"]

    dlbm = random.choice(dlbm_list)
    dlmc = dlmc_map[dlbm]
    qsxz = random.choice(qsxz_list)
    qsdwdm = f"{random.randint(420100, 420199)}"
    zldwdm = f"{random.randint(420100, 420199)}"
    kcdlbm = dlbm
    kcxs = round(random.uniform(0.1, 0.5), 2)
    kcmj = round(random.uniform(1, 100), 2)
    gdlx = random.choice(gdlx_list)
    gdpdjb = random.choice(gdpd_list)
    tbxhdm = random.choice(["A1", "A2", "B1", "B2"])
    tbxhmc = f"{dlmc}{tbxhdm}"
    zzsxdm = ""  # 这里没有具体编码，就留空字符串
    zzsxmc = random.choice(zzsx_list)
    gdjb = random.randint(1, 15)
    frdbs = random.choice(["", "飞入地"])

    sjnf = year
    bz = f"基本农田核实处置自动造数{i}"
    xzqdm = f"4201{random.randint(1, 13):02d}"
    xzqmc = qu
    yjjbnttbbh = f"JBNT{year}{i:05d}"
    ggbzl = random.choice(["一般耕地保有量", "永久基本农田"])
    gddj = random.randint(1, 15)
    zlfl = random.choice(["集中连片", "零星散布"])

    cfzr = fake.name()
    zmc = f"{qu}{fake.street_name()}地块"
    zzrr = fake.name()
    zrrzjhm = fake.ssn()
    zrrmc = zzrr
    lxdh = fake.phone_number()

    bhkssj = fake.date_time_between(start_date="-5y", end_date="-2y")
    bhjssj = bhkssj + timedelta(days=random.randint(30, 365))

    sjbh = f"SJ{year}{i:06d}"
    sjmc = f"{year}年{qu}基本农田核实处置"

    # ZRSYX 字段备注为自身，这里理解为“自然资源属性是否有效”
    zrs_yx = random.choice(["有效", "无效"])

    # WDGD 是 nvarchar，这里写成“x.xx m”的高度字符串
    wdgd = f"{round(random.uniform(0.5, 5.0), 2)}m"

    # SFWYYJJBNT：是否为原有永久基本农田
    sfwyyjjbnt = random.choice(["是", "否"])

    jzdz = f"{qu}{adm['street']}{fake.street_address()}"

    yjjbnttbmj = round(random.uniform(1, 100), 2)
    yjjbntmj = round(yjjbnttbmj * random.uniform(0.8, 1.2), 2)

    qsdwmc = f"{qu}自然资源和规划局"
    zldwmc = f"{adm['street']}办事处"

    # 按备注：CZKFBJBH = 是否为城镇开发边界内补划（是/否）
    czkfbjbh = random.choice(["是", "否"])

    # CN = 承诺地块标注：承诺地块 / 非承诺地块
    cn = random.choice(["承诺地块", "非承诺地块"])

    # CZLXDM + 处置类型：保持一致用中文描述（调整/补划/占补平衡）
    czlx_options = ["调整", "补划", "占补平衡"]
    czlxdm = random.choice(czlx_options)  # 编码就用中文枚举
    czlx = czlxdm                         # 处置类型 = 同一枚举

    # YJJBNTLX = 永久基本农田类型：原划定 / 补划
    yjjbntlx = random.choice(["原划定", "补划"])

    # 永久基本农田类型：再细分一层形态（集中连片/零星散布）
    yjjbnt_type = random.choice(["集中连片", "零星散布"])

    gzqh = adm["gzqh"]

    return (
        f"JBNTCZ{100000 + i}",  # BSM
        "2001020100",          # YSDM
        f"TBBH{year}{i:05d}",  # TBBH
        dlbm,                  # DLBM
        dlmc,                  # DLMC
        qsxz,                  # QSXZ
        qsdwdm,                # QSDWDM
        zldwdm,                # ZLDWDM
        kcdlbm,                # KCDLBM
        kcxs,                  # KCXS
        kcmj,                  # KCMJ
        gdlx,                  # GDLX
        gdpdjb,                # GDPDJB
        tbxhdm,                # TBXHDM
        tbxhmc,                # TBXHMC
        zzsxdm,                # ZZSXDM
        zzsxmc,                # ZZSXMC
        gdjb,                  # GDDB
        frdbs,                 # FRDBS
        sjnf,                  # SJNF
        bz,                    # BZ
        xzqdm,                 # XZQDM
        xzqmc,                 # XZQMC
        yjjbnttbbh,            # YJJBNTTBBH
        ggbzl,                 # GGBZL
        gddj,                  # GDDJ
        zlfl,                  # ZLFLDM
        cfzr,                  # CFZR
        zmc,                   # ZMC
        zzrr,                  # ZZRR
        zrrzjhm,               # ZRRZJHM
        zrrmc,                 # ZRRMC
        lxdh,                  # LXDH
        bhkssj,                # BHKSSJ
        bhjssj,                # BHJSSJ
        sjbh,                  # SJBH
        sjmc,                  # SJMC
        zrs_yx,                # ZRSYX
        wdgd,                  # WDGD
        sfwyyjjbnt,            # SFWYYJJBNT
        jzdz,                  # JZDZ
        yjjbnttbmj,            # YJJBNTTBMJ
        yjjbntmj,              # YJJBNTMJ
        qsdwmc,                # QSDWMC
        zldwmc,                # ZLDWMC
        czkfbjbh,              # CZKFBJBH（是否为城镇开发边界内补划）
        cn,                    # CN（承诺地块标注）
        czlxdm,                # CZLXDM
        yjjbntlx,              # YJJBNTLX
        gzqh,                  # GZQH_GLQMC（行政区）
        czlx,                  # 处置类型
        yjjbnt_type,           # 永久基本农田类型
    )


def gen_stbh_hx_row(i: int):
    adm = random_admin_info()
    qu = adm["qu"]

    bsm = f"HBHX{100000 + i}"
    ysdm = "3001010100"
    xzqdm = f"4201{random.randint(1, 13):02d}"
    sheng = "湖北省"
    shi = "武汉市"
    xian = qu
    hxbm = f"HX{random.randint(1,9999):04d}"
    hxlx = random.choice(["一级生态红线", "二级生态红线"])
    lxbm = random.choice(["01", "02", "03"])
    mj = round(random.uniform(1000, 200000), 2)
    zrbhdjb = random.choice(["国家级", "省级", "市级"])
    zrbhdlx = random.choice(["自然保护区", "风景名胜区", "饮用水源保护区"])
    zrbhdfq = qu
    szxjdm = xzqdm
    szxjmc = qu
    bz = f"生态保护红线自动造数{i}"
    hxmc = f"{qu}生态红线{i}"
    zrbhdmc = f"{qu}重要生态功能区"
    xtyzblx = random.choice(["陆地生态系统", "湿地生态系统", "水域生态系统"])
    gkcs = random.choice(["严格管控", "适度管控"])

    return (
        bsm,          # BSM
        ysdm,         # YSDM
        xzqdm,        # XZQDM
        qu,           # XZQMC
        sheng,        # SHENG
        shi,          # SHI
        xian,         # XIAN
        hxbm,         # HXBM
        hxlx,         # HXLX
        lxbm,         # LXBM
        mj,           # MJ
        zrbhdjb,      # ZRBHDJB
        zrbhdlx,      # ZRBHDLX
        zrbhdfq,      # ZRBHDFQ
        szxjdm,       # SZXJXZQDM
        szxjmc,       # SZXJXZQMC
        bz,           # BZ
        hxmc,         # HXMC
        zrbhdmc,      # ZRBHDMC
        xtyzblx,      # XTYZBLX
        gkcs,         # GKCS
        adm["gzqh"],  # GZQH_GLQMC
    )


def gen_gd_bhmb_row(i: int):
    adm = random_admin_info()
    qu = adm["qu"]

    dlbm_list = ["011", "012", "013", "021", "031"]
    dlmc_map = {
        "011": "水田",
        "012": "水浇地",
        "013": "旱地",
        "021": "园地",
        "031": "有林地",
    }
    qsxz_list = ["国有", "集体", "个人"]
    gdlx_list = ["水田", "旱地", "菜地"]
    gdpd_list = ["I", "II", "III", "IV"]
    zzsx_list = ["一年一熟", "一年两熟", "一年三熟"]

    dlbm = random.choice(dlbm_list)
    dlmc = dlmc_map[dlbm]
    qsxz = random.choice(qsxz_list)
    qsdwdm = f"{random.randint(420100, 420199)}"
    zldwdm = f"{random.randint(420100, 420199)}"
    tbmj = round(random.uniform(1, 200), 2)
    kcdlbm = dlbm
    kcxs = round(random.uniform(0.1, 0.5), 2)
    kcmj = round(tbmj * kcxs, 2)
    tbdlmj = round(tbmj - kcmj, 2)
    gdlx = random.choice(gdlx_list)
    gdpdjb = random.choice(gdpd_list)
    tbxhdm = random.choice(["A1", "A2", "B1", "B2"])
    tbxhmc = f"{dlmc}{tbxhdm}"
    zzsx = random.choice(zzsx_list)
    gdjb = random.randint(1, 15)
    frdbs = random.choice(["", "飞入地"])
    year = random.randint(2020, 2024)
    sfwhtd = random.randint(0, 1)
    qsdwmc = f"{qu}自然资源和规划局"
    zldwmc = f"{adm['street']}办事处"
    tbmj_ys = tbmj
    tbdlmj_ys = tbdlmj
    kcmj_ys = kcmj
    shape_leng = round(random.uniform(100, 10000), 2)
    shape_le1 = shape_leng
    shape_le2 = round(shape_leng * random.uniform(0.9, 1.1), 2)
    orig_fid = i

    return (
        i,                     # OBJECTID_1
        f"GDBH{100000 + i}",   # BSM
        "2001030100",          # YSDM
        f"TBY{year}{i:05d}",   # TBYBH
        f"TBBH{year}{i:05d}",  # TBBH
        dlbm,                  # DLBM
        dlmc,                  # DLMC
        qsxz,                  # QSXZ
        qsdwdm,                # QSDWDM
        zldwdm,                # ZLDWDM
        tbmj,                  # TBMJ
        kcdlbm,                # KCDLBM
        kcxs,                  # KCXS
        kcmj,                  # KCMJ
        tbdlmj,                # TBDLMJ
        gdlx,                  # GDLX
        gdpdjb,                # GDPDJB
        tbxhdm,                # TBXHDM
        tbxhmc,                # TBXHMC
        "",                    # ZZSXDM
        zzsx,                  # ZZSXMC
        gdjb,                  # GDDB
        frdbs,                 # FRDBS
        year,                  # SJNF
        sfwhtd,                # SFWHTD
        qsdwmc,                # QSDWMC
        zldwmc,                # ZLDWMC
        tbmj_ys,               # TBMJ_YS
        tbdlmj_ys,             # TBDLMJ_YS
        kcmj_ys,               # KCMJ_YS
        shape_leng,            # Shape_Leng
        shape_le1,             # Shape_Le_1
        shape_le2,             # Shape_Le_2
        orig_fid,              # ORIG_FID
        adm["gzqh"],           # GZQH_GLQMC
    )


def gen_rk2022_row(i: int):
    adm = random_admin_info()
    base = random.randint(100, 2000)
    c0_2 = random.randint(0, base // 10)
    c3_5 = random.randint(0, base // 10)
    c6_11 = random.randint(base // 20, base // 5)
    c12_14 = random.randint(base // 20, base // 5)
    c15_17 = random.randint(base // 20, base // 5)
    c18_35 = random.randint(base // 5, base // 2)
    c36_64 = random.randint(base // 5, base)
    c65 = random.randint(0, base // 3)
    total = c0_2 + c3_5 + c6_11 + c12_14 + c15_17 + c18_35 + c36_64 + c65
    rcmd = random.randint(1, 5)
    area = round(random.uniform(0.1, 10.0), 4)
    dybh = f"DY{2022}{i:05d}"

    return (
        dybh,                # DYBH
        c0_2,                # COUNT_Y0_2
        c3_5,                # COUNT_Y3_5
        c6_11,               # COUNT_Y6_1
        c12_14,              # COUNT_Y12_
        c15_17,              # COUNT_Y15_
        c18_35,              # COUNT_Y18_
        c36_64,              # COUNT_Y36_
        c65,                 # COUNT_Y65_
        total,               # COUNT_
        rcmd,                # RKMD
        area,                # sde_SDE_人口2022_AREA
        adm["qm_dkzx"],      # QM_DKZX
        adm["main_city"],    # 主城区
        adm["street"],       # 所属街道
        adm["ring"],         # 环线
        adm["key_zone"],     # 重点功能区
        adm["new_two_parks"],# 新两园
        adm["industrial_park"], # 工业园区
        adm["community"],    # 所属社区
        adm["gzqh"],         # GZQH_GLQMC
    )


def gen_zz2023_row(i: int):
    adm = random_admin_info()
    qpbh = f"ZQ{2023}{i:04d}"
    tdjb = random.randint(1, 10)
    jz_rjl = round(random.uniform(0.5, 5.0), 2)
    gyjbj = random.randint(1000, 5000)
    gyqpj = gyjbj + random.randint(0, 1000)
    zjdjbj = random.randint(800, 4000)
    zjdqpj = zjdjbj + random.randint(0, 800)
    zlzfjbj = random.randint(800, 4000)
    zlzfqpj = zlzfjbj + random.randint(0, 800)
    t_x_mj = round(random.uniform(1000, 50000), 2)

    return (
        qpbh,           # 区片编号
        tdjb,           # 土地级别
        jz_rjl,         # 基准容积率
        gyjbj,          # 国有级别价
        gyqpj,          # 国有区片价
        zjdjbj,         # 宅基地级别价
        zjdqpj,         # 宅基地区片价
        zlzfjbj,        # 租赁住房级别价
        zlzfqpj,        # 租赁住房区片价
        t_x_mj,         # 图形面积
        adm["qm_dkzx"], # QM_DKZX
        adm["gzqh"],    # GZQH_GLQMC
    )


def gen_gf2023_row(i: int):
    adm = random_admin_info()
    qpbh = f"GF{2023}{i:04d}"
    tdjb = random.randint(1, 10)
    jz_rjl = round(random.uniform(0.5, 5.0), 2)
    gyjbj = random.randint(800, 4000)
    gyqpj = gyjbj + random.randint(0, 800)
    jtjbj = random.randint(600, 3000)
    jtqpj = jtjbj + random.randint(0, 600)
    t_x_mj = round(random.uniform(500, 30000), 2)

    return (
        qpbh,           # 区片编号
        tdjb,           # 土地级别
        jz_rjl,         # 基准容积率
        gyjbj,          # 国有级别价
        gyqpj,          # 国有区片价
        jtjbj,          # 集体级别价
        jtqpj,          # 集体区片价
        t_x_mj,         # 图形面积
        adm["qm_dkzx"], # QM_DKZX
        adm["gzqh"],    # GZQH_GLQMC
    )


def gen_sy2023_row(i: int):
    adm = random_admin_info()
    qpbh = f"SY{2023}{i:04d}"
    tdjb = random.randint(1, 10)
    gyjbj = random.randint(1500, 8000)
    gyqpj = gyjbj + random.randint(0, 1500)
    jtjbj = random.randint(1000, 5000)
    jtqpj = jtjbj + random.randint(0, 1000)
    jz_rjl = round(random.uniform(0.5, 8.0), 2)
    t_x_mj = round(random.uniform(500, 30000), 2)

    return (
        qpbh,           # 区片编号
        tdjb,           # 土地级别
        gyjbj,          # 国有级别价
        gyqpj,          # 国有区片价
        jtjbj,          # 集体级别价
        jtqpj,          # 集体区片价
        jz_rjl,         # 基准容积率
        t_x_mj,         # 图形面积
        adm["qm_dkzx"], # QM_DKZX
        adm["gzqh"],    # GZQH_GLQMC
    )


def gen_swbg2023_row(i: int):
    adm = random_admin_info()
    qpbh = f"BG{2023}{i:04d}"
    tdjb = random.randint(1, 10)
    jz_rjl = round(random.uniform(1.0, 6.0), 2)
    gyjbj = random.randint(2000, 9000)
    gyqpj = gyjbj + random.randint(0, 2000)
    jtjbj = random.randint(1500, 6000)
    jtqpj = jtjbj + random.randint(0, 1500)
    t_x_mj = round(random.uniform(500, 30000), 2)

    return (
        qpbh,           # 区片编号
        tdjb,           # 土地级别
        jz_rjl,         # 基准容积率
        gyjbj,          # 国有级别价
        gyqpj,          # 国有区片价
        jtjbj,          # 集体级别价
        jtqpj,          # 集体区片价
        t_x_mj,         # 图形面积
        adm["qm_dkzx"], # QM_DKZX
        adm["gzqh"],    # GZQH_GLQMC
    )


def gen_gy2023_row(i: int):
    adm = random_admin_info()
    qpbh = f"GY{2023}{i:04d}"
    tdjb = random.randint(1, 10)
    jz_rjl = round(random.uniform(0.5, 3.0), 2)
    gyjbj = random.randint(800, 4000)
    gyqpj = gyjbj + random.randint(0, 800)
    jtjbj = random.randint(600, 3000)
    jtqpj = jtjbj + random.randint(0, 600)
    t_x_mj = round(random.uniform(1000, 100000), 2)

    return (
        qpbh,           # 区片编号
        tdjb,           # 土地级别
        jz_rjl,         # 基准容积率
        gyjbj,          # 国有级别价
        gyqpj,          # 国有区片价
        jtjbj,          # 集体级别价
        jtqpj,          # 集体区片价
        t_x_mj,         # 图形面积
        adm["qm_dkzx"], # QM_DKZX
        adm["gzqh"],    # GZQH_GLQMC
    )


def gen_stxhy_row(i: int):
    stx_yq = random.choice(["严格保护", "限制建设", "适度开发"])
    tl = random.choice(["一级控制线", "二级控制线"])
    ssxm = f"项目{random.randint(1,20)}"
    spzt = random.choice(["已批复", "审查中", "预审通过"])
    t_x_mj = round(random.uniform(1000, 50000), 2)

    return (
        stx_yq, # 生态线要求
        tl,     # TL
        ssxm,   # 所属项目
        spzt,   # 审批审查状态
        t_x_mj, # 图形面积
    )


def gen_tygltr_row(i: int):
    adm = random_admin_info()
    gldy = f"{adm['qu']}单元{random.randint(1,50)}"
    qdfq = random.choice(["低强度", "中等强度", "高强度"])
    kzl_b = random.choice(["刚性控制", "弹性控制"])
    kzl_t = random.choice(["用地控制", "空间形态控制"])
    rjl = round(random.uniform(0.5, 6.0), 2)
    jzmd = round(random.uniform(10, 40), 1)
    jzgd = round(random.uniform(12, 150), 1)
    ldl = round(random.uniform(20, 45), 1)
    ssxm = f"项目{random.randint(1,30)}"
    jgsj = random.choice(["需要城市设计", "一般设计要求"])
    jrqqk = random.choice(["允许兼容", "严格单一功能"])
    spzt = random.choice(["已批复", "审查中", "预审通过"])
    tl = random.choice(["一般控制性详细规划", "重点地区城市设计"])
    ydxz = random.choice(["居住用地", "商业用地", "工业用地", "综合用地"])
    bzdy = f"{adm['qu']}编制单元{random.randint(1,20)}"
    tsstgk = random.choice(["重要生态廊道", "一般管控区", "严格保护区"])
    bz = f"统一规划管理用图自动造数{i}"
    cs_sj = random.choice(["需控制天际线", "需控制天际线及天际线背后建筑高度"])
    spc_sx = random.choice(["要求设置雨水花园", "适用绿色屋顶"])
    dxkj_kz = random.choice(["控制地下空间深度", "控制地下空间开发范围"])
    js_yq = random.choice(["分期实施", "尽快实施"])
    ydxz1 = ""
    ydxz2 = ""
    t_x_mj = round(random.uniform(1000, 50000), 2)

    return (
        gldy,   # 管理单元
        qdfq,   # 强度分区
        kzl_b,  # 控制类别
        kzl_t,  # 控制类型
        rjl,    # 容积率
        jzmd,   # 建筑密度
        jzgd,   # 建筑高度
        ldl,    # 绿地率
        ssxm,   # 所属项目
        jgsj,   # 景观设计
        jrqqk,  # 兼容情况
        spzt,   # 审批审查状态
        tl,     # TL
        ydxz,   # 用地性质
        bzdy,   # 编制单元
        tsstgk, # 特色生态管控
        bz,     # 备注
        cs_sj,  # 城市设计控制要求
        spc_sx, # 海绵城市控制要求
        dxkj_kz,# 地下空间控制要求
        js_yq,  # 建设要求
        ydxz1,  # YDXZ1
        ydxz2,  # YDXZ2
        t_x_mj, # 图形面积
    )


def gen_zh2023_row(i: int):
    adm = random_admin_info()
    tdjb = random.randint(1, 10)
    t_x_mj = round(random.uniform(1000, 50000), 2)

    return (
        tdjb,           # 土地级别
        t_x_mj,         # 图形面积
        adm["qm_dkzx"], # QM_DKZX
        adm["gzqh"],    # GZQH_GLQMC
    )


# ===================== 表配置：构建 INSERT 语句 + 指定 row_generator =====================
TABLE_CONFIGS = {
    "POI_问数测试": {
        "schema": "sde",
        "cols": COLS_POI,
        "insert_sql": "INSERT INTO [sde].[POI_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_POI),
            placeholders=", ".join(["?"] * len(COLS_POI)),
        ),
        "row_generator": gen_poi_row,
    },
    "三区三线_城镇开发边界_问数测试": {
        "schema": "sde",
        "cols": COLS_CKBJ,
        "insert_sql": "INSERT INTO [sde].[三区三线_城镇开发边界_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_CKBJ),
            placeholders=", ".join(["?"] * len(COLS_CKBJ)),
        ),
        "row_generator": gen_ckbj_row,
    },
    "三区三线_基本农田核实处置_问数测试": {
        "schema": "sde",
        "cols": COLS_JBNT_CZ,
        "insert_sql": "INSERT INTO [sde].[三区三线_基本农田核实处置_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_JBNT_CZ),
            placeholders=", ".join(["?"] * len(COLS_JBNT_CZ)),
        ),
        "row_generator": gen_jbnt_cz_row,
    },
    "三区三线_生态保护红线_问数测试": {
        "schema": "sde",
        "cols": COLS_STBH_HX,
        "insert_sql": "INSERT INTO [sde].[三区三线_生态保护红线_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_STBH_HX),
            placeholders=", ".join(["?"] * len(COLS_STBH_HX)),
        ),
        "row_generator": gen_stbh_hx_row,
    },
    "三区三线_耕地保护目标_问数测试": {
        "schema": "sde",
        "cols": COLS_GD_BHMB,
        "insert_sql": "INSERT INTO [sde].[三区三线_耕地保护目标_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_GD_BHMB),
            placeholders=", ".join(["?"] * len(COLS_GD_BHMB)),
        ),
        "row_generator": gen_gd_bhmb_row,
    },
    "人口2022_问数测试": {
        "schema": "sde",
        "cols": COLS_RK2022,
        "insert_sql": "INSERT INTO [sde].[人口2022_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_RK2022),
            placeholders=", ".join(["?"] * len(COLS_RK2022)),
        ),
        "row_generator": gen_rk2022_row,
    },
    "住宅用地2023_问数测试": {
        "schema": "sde",
        "cols": COLS_ZZ_2023,
        "insert_sql": "INSERT INTO [sde].[住宅用地2023_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_ZZ_2023),
            placeholders=", ".join(["?"] * len(COLS_ZZ_2023)),
        ),
        "row_generator": gen_zz2023_row,
    },
    "公服用地2023_问数测试": {
        "schema": "sde",
        "cols": COLS_GF_2023,
        "insert_sql": "INSERT INTO [sde].[公服用地2023_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_GF_2023),
            placeholders=", ".join(["?"] * len(COLS_GF_2023)),
        ),
        "row_generator": gen_gf2023_row,
    },
    "商业用地2023_问数测试": {
        "schema": "sde",
        "cols": COLS_SY_2023,
        "insert_sql": "INSERT INTO [sde].[商业用地2023_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_SY_2023),
            placeholders=", ".join(["?"] * len(COLS_SY_2023)),
        ),
        "row_generator": gen_sy2023_row,
    },
    "商务办公用地2023_问数测试": {
        "schema": "sde",
        "cols": COLS_SWBG_2023,
        "insert_sql": "INSERT INTO [sde].[商务办公用地2023_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_SWBG_2023),
            placeholders=", ".join(["?"] * len(COLS_SWBG_2023)),
        ),
        "row_generator": gen_swbg2023_row,
    },
    "工业用地2023_问数测试": {
        "schema": "sde",
        "cols": COLS_GY_2023,
        "insert_sql": "INSERT INTO [sde].[工业用地2023_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_GY_2023),
            placeholders=", ".join(["?"] * len(COLS_GY_2023)),
        ),
        "row_generator": gen_gy2023_row,
    },
    "武汉市基本生态控制线优化_问数测试": {
        "schema": "sde",
        "cols": COLS_STX_HY,
        "insert_sql": "INSERT INTO [sde].[武汉市基本生态控制线优化_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_STX_HY),
            placeholders=", ".join(["?"] * len(COLS_STX_HY)),
        ),
        "row_generator": gen_stxhy_row,
    },
    "统一规划管理用图R_问数测试": {
        "schema": "sde",
        "cols": COLS_TYGLT,
        "insert_sql": "INSERT INTO [sde].[统一规划管理用图R_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_TYGLT),
            placeholders=", ".join(["?"] * len(COLS_TYGLT)),
        ),
        "row_generator": gen_tygltr_row,
    },
    "综合用地2023_问数测试": {
        "schema": "sde",
        "cols": COLS_ZH_2023,
        "insert_sql": "INSERT INTO [sde].[综合用地2023_问数测试] ({cols}) VALUES ({placeholders})".format(
            cols=", ".join(f"[{c}]" for c in COLS_ZH_2023),
            placeholders=", ".join(["?"] * len(COLS_ZH_2023)),
        ),
        "row_generator": gen_zh2023_row,
    },
}


# ===================== 通用连接 + 填充逻辑 =====================
def get_connection():
    conf = DB_CONFIG
    conn_str = (
        f"DRIVER={DRIVER_PATH};"
        f"SERVER={conf['server']};"
        f"PORT={conf['port']};"
        f"DATABASE={conf['database']};"
        f"UID={conf['user']};"
        f"PWD={conf['password']};"
        "TDS_Version=7.4;"
    )
    print(f"  使用连接: {conf['server']},{conf['port']} / DB={conf['database']}")
    return pyodbc.connect(conn_str)


def fill_one_table(table_name: str, conn, table_conf: dict):
    schema = table_conf.get("schema", "dbo")
    full_table = f"[{schema}].[{table_name}]"
    cursor = conn.cursor()

    print(f"▶ 正在处理连接的表 {full_table} ...")
    cursor.execute(f"SELECT COUNT(*) FROM {full_table}")
    current_rows = cursor.fetchone()[0]
    print(f"   当前行数: {current_rows}")

    need = ROWS_PER_TABLE - current_rows
    if need <= 0:
        print(f"   已经 >= {ROWS_PER_TABLE} 行，跳过。")
        return

    print(f"   需要新增: {need} 行")
    rows = [table_conf["row_generator"](current_rows + idx + 1) for idx in range(need)]

    cursor.fast_executemany = False
    cursor.executemany(table_conf["insert_sql"], rows)
    conn.commit()
    print(f"   已插入 {need} 行 ✅")


def main():
    print("\n==============================")
    print("连接到: 规划蓝图数据库 (ghlt)")
    print("==============================")

    conn = get_connection()
    try:
        for table_name, table_conf in TABLE_CONFIGS.items():
            fill_one_table(table_name, conn, table_conf)
    finally:
        conn.close()
        print("关闭连接: 规划蓝图数据库\n")


if __name__ == "__main__":
    main()
