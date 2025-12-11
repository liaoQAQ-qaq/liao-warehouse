import random
from faker import Faker
from datetime import datetime, timedelta
import pyodbc

# ===================== 基础配置 =====================
fake = Faker("zh_CN")
ROWS_PER_TABLE = 400  # 每个表生成的数据量

# 数据库连接配置 (端口 1436)
DB_CONFIG = {
    "server": "192.168.7.72",
    "port": 1436,
    "database": "sde",
    "user": "sa",
    "password": "zhuquezhihui1234!",
}
# FreeTDS 驱动路径
DRIVER_PATH = "/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so"

# ===================== 真实化数据字典 =====================

# 武汉行政区划
WUHAN_ADM = {
    "江岸区": ["大智街道", "一元街道", "车站街道", "四唯街道", "永清街道", "西马街道", "球场街道", "劳动街道", "二七街道", "新村街道", "丹水池街道", "台北街道", "花桥街道", "谌家矶街道", "后湖街道", "塔子湖街道"],
    "江汉区": ["民族街道", "花楼街道", "水塔街道", "民权街道", "满春街道", "民意街道", "新华街道", "万松街道", "唐家墩街道", "北湖街道", "前进街道", "常青街道", "汉兴街道"],
    "硚口区": ["易家街道", "韩家墩街道", "宗关街道", "汉水桥街道", "宝丰街道", "荣华街道", "古田街道", "汉中街道", "汉正街道", "六角亭街道", "长丰街道"],
    "汉阳区": ["建桥街道", "晴川街道", "鹦鹉街道", "洲头街道", "五里墩街道", "琴断口街道", "江汉二桥街道", "永丰街道", "江堤街道", "四新街道", "龙阳街道"],
    "武昌区": ["积玉桥街道", "杨园街道", "徐家棚街道", "粮道街道", "中华路街道", "黄鹤楼街道", "紫阳街道", "白沙洲街道", "首义路街道", "中南路街道", "水果湖街道", "珞珈山街道", "石洞街道", "南湖街道"],
    "青山区": ["红卫路街道", "冶金街道", "新沟桥街道", "红钢城街道", "工人村街道", "青山镇街道", "厂前街道", "武东街道", "白玉山街道", "钢花村街道", "钢都花园街道"],
    "洪山区": ["珞南街道", "关山街道", "狮子山街道", "张家湾街道", "梨园街道", "卓刀泉街道", "洪山街道", "和平街道", "青菱街道", "花山街道", "左岭街道", "九峰街道"],
    "东西湖区": ["吴家山街道", "柏泉街道", "将军路街道", "慈惠街道", "走马岭街道", "径河街道", "长青街道", "辛安渡街道", "东山街道", "新沟镇街道", "金银湖街道"],
    "汉南区": ["纱帽街道", "邓南街道", "东荆街道", "湘口街道"],
    "蔡甸区": ["蔡甸街道", "奓山街道", "永安街道", "侏儒山街道", "大集街道", "张湾街道", "索河街道", "玉贤街道", "沌口街道", "军山街道", "沌阳街道"],
    "江夏区": ["纸坊街道", "金口街道", "乌龙泉街道", "郑店街道", "五里界街道", "安山街道", "山坡街道", "法泗街道", "湖泗街道", "舒安街道", "佛祖岭街道", "豹澥街道", "龙泉街道", "滨湖街道"],
    "黄陂区": ["前川街道", "祁家湾街道", "横店街道", "罗汉寺街道", "滠口街道", "六指街道", "天河街道", "王家河街道", "长轩岭街道", "李家集街道", "姚家集街道", "蔡家榨街道", "三里桥街道", "蔡店街道", "木兰乡"],
    "新洲区": ["邾城街道", "阳逻街道", "仓埠街道", "汪集街道", "李集街道", "三店街道", "潘塘街道", "旧街街道", "双柳街道", "涨渡湖街道", "辛冲街道", "徐古街道", "凤凰镇"],
}

# 拼音映射 (替代 fake.pinyin)
DISTRICT_CODE_MAP = {
    "江岸区": "JA", "江汉区": "JH", "硚口区": "QK", "汉阳区": "HY",
    "武昌区": "WC", "青山区": "QS", "洪山区": "HS", "东西湖区": "DXH",
    "汉南区": "HN", "蔡甸区": "CD", "江夏区": "JX", "黄陂区": "HP",
    "新洲区": "XZ"
}

PROJ_FEATURES = ["滨江", "国际", "新城", "智慧", "生态", "创新", "花园", "中心", "广场", "天地", "壹号", "公馆", "府", "悦府", "时代"]
PROJ_TYPES = ["综合体项目", "住宅小区项目", "商业中心项目", "还建房项目", "产业园基础设施项目", "道路拓宽工程", "景观提升工程", "学校改扩建项目", "医院新建项目", "研发中心项目"]
PHASES = ["一期", "二期", "三期", "A地块", "B地块", "启动区", "核心区"]

COMPANIES = [
    "武汉城市建设集团有限公司", "武汉地铁集团有限公司", "武汉地产开发投资集团有限公司", 
    "武汉市土地整理储备中心", "武汉高科国有控股集团有限公司", "武汉光谷建设投资有限公司",
    "保利(武汉)房地产开发有限公司", "万科企业股份有限公司武汉分公司", 
    "华润置地(武汉)有限公司", "龙湖地产武汉分公司", "中建三局集团有限公司",
    "武汉旅游体育集团有限公司", "武汉碧桂园置业发展有限公司"
]

DOC_PREFIXES = {
    "approval": ["鄂政土批", "武政土批"],
    "plan": ["武自然资规", "武规"],
    "license_yd": ["地字第", "武自资规地"],
    "license_gc": ["建字第", "武自资规建"],
    "reserve": ["武土储", "武土资"],
}

# 用地性质 (代码, 大类名称, 常见容积率范围)
LAND_USE_TYPES = [
    ("R2", "二类居住用地", (2.0, 4.5)), 
    ("R21", "住宅用地", (1.5, 3.5)), 
    ("B1", "商业用地", (3.0, 6.0)), 
    ("B2", "商务用地", (3.0, 5.5)),
    ("M1", "一类工业用地", (1.0, 2.5)), 
    ("A33", "中小学用地", (0.8, 1.5)), 
    ("G1", "公园绿地", (0.05, 0.2)), 
    ("S4", "交通场站用地", (0.5, 1.2))
]

# ===================== 辅助函数 =====================

def get_random_adm():
    """获取随机行政区划信息"""
    dist = random.choice(list(WUHAN_ADM.keys()))
    street = random.choice(WUHAN_ADM[dist])
    is_main = "主城区" if dist in ["江岸区", "江汉区", "硚口区", "汉阳区", "武昌区", "青山区", "洪山区"] else "新城区"
    ring = random.choice(["二环内", "二环至三环", "三环至四环", "四环外"])
    code_prefix = DISTRICT_CODE_MAP.get(dist, "WH")
    return {
        "dist": dist, "street": street, "is_main": is_main, "ring": ring,
        "code_pre": code_prefix, "gzqh": dist
    }

def gen_proj_name(adm):
    """生成写实的项目名称"""
    feat = random.choice(PROJ_FEATURES)
    ptype = random.choice(PROJ_TYPES)
    phase = random.choice(PHASES)
    road = random.choice(["解放大道", "建设大道", "中山大道", "和平大道", "友谊大道", "光谷大道", "金银湖路", "珞喻路"]) if random.random() < 0.3 else fake.street_name()
    return f"{adm['dist']}{road}{feat}{ptype}{phase}"

def gen_company():
    if random.random() < 0.4: return random.choice(COMPANIES)
    return fake.company()

def gen_doc_no(doc_type, year=None):
    if not year: year = random.randint(2019, 2024)
    pre = random.choice(DOC_PREFIXES.get(doc_type, ["武文"]))
    num = random.randint(1, 1500)
    if "字第" in pre: return f"{pre}4201{year}{num:05d}号"
    return f"{pre}[{year}]{num}号"

def gen_area_val(base, var=0.3):
    val = base * random.uniform(1-var, 1+var)
    return round(max(val, 10.0), 2)

def gen_date(year=None):
    """生成指定年份或近几年的过去日期"""
    if year is None: year = random.randint(2020, 2024)
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    # 限制不超过今天，避免逻辑错误
    now = datetime.now()
    if end > now: end = now
    if start > end: start = end - timedelta(days=1)
    
    days = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, days)))

def gen_future_date(base_date, days_offset=730):
    """生成基于某个日期的未来日期"""
    return base_date + timedelta(days=random.randint(30, days_offset))

def gen_guid():
    return fake.uuid4().upper()

# ===================== 填充逻辑 =====================

# 1. 储备要点
def row_cb_point(i):
    adm = get_random_adm()
    year = random.randint(2021, 2024)
    land = random.choice(LAND_USE_TYPES)
    area = gen_area_val(30000)
    fzsj = gen_date(year)
    
    return (
        i,  # OBJECTID_1
        f"CB{year}{random.randint(1000,9999)}", # PROJECTCOD
        gen_guid(), # INSTANCEID
        f"{adm['dist']}{adm['street']}储备地块", # XMMC
        f"武汉市{adm['dist']}土地储备中心", # DWMC
        f"{adm['dist']}{adm['street']}{fake.street_address()}", # YDWZ
        gen_doc_no("reserve", year), # XKZWH
        adm['dist'], # DQDW
        "武汉市自然资源和规划局", # SBDW
        land[1], # GHYDXZ_DL
        area, # JYDMJ
        str(area * random.uniform(1.5, 3.5)), # JZMJ
        str(round(random.uniform(*land[2]), 2)), # RJL
        f"{random.randint(20,40)}%", # JZMD
        f"{random.randint(50,100)}米", # JZGD
        f"{random.randint(25,35)}%", # LHL
        f"{adm['code_pre']}-{year}-GH-{i:03d}", # TH
        fzsj, # FZSJ
        f"DEPT_{random.randint(10,99)}", # DEPTID
        fzsj + timedelta(days=random.randint(1, 30)), # GXSJ
        "储备中心录入员", # LRDW
        "符合土地储备规划", # MEMO_
        "已入库", # SHZT
        str(year), # ssnf
        "新增储备", # ydlx
        adm['dist'], # xzqname
        "审批通过", # approvesta
        f"{adm['code_pre']}-{random.randint(1000,9999)}", # QM_DKZX
        adm['gzqh'] # GZQH_GLQMC
    )

# 2. 国家级开发范围
def row_gjkf(i):
    zones = [("武汉东湖新技术开发区", "GXQ", "创新"), ("武汉经济技术开发区", "JKQ", "制造"), ("武汉临空港经开区", "LKK", "临空")]
    z = random.choice(zones)
    return (
        z[1] + f"{random.randint(100,999)}", # KFQDM
        z[0], # KFQMC
        "国家级", # KFQJB
        f"{z[2]}主导型", # PJLX
        gen_area_val(500000, 0.05), # PFMJ
        "武汉市", # GZQH_GLQMC
        f"KF-{i:03d}" # QM_DKZX
    )

# 3. 土地供应
def row_tdgy(i):
    adm = get_random_adm()
    year = random.randint(2020, 2024)
    start_date = gen_date(year)
    area = gen_area_val(15000)
    land = random.choice(LAND_USE_TYPES)
    
    return (
        str(year), # 年份
        fake.name(), # 项目主管
        random.choice(["挂牌出让", "协议出让", "划拨"]), # 供地类型
        gen_company(), # 用地单位名称
        f"{adm['dist']}{adm['street']}P({year}){i}号地块", # 土地坐落
        f"DJ{year}-{random.randint(10000,99999)}", # 地籍测量号
        land[1], # 土地用途
        area, # 土地面积
        area, # 图形面积
        "净地供应", # 备注
        "预留1", # TEMP1 (补齐空列)
        start_date, # TEMP2
        "预留3", "预留4", "预留BH", "预留JG", "预留XY", "预留CY", "预留JY",
        f"JG-{year}-{i}", # JGH
        f"IC-{random.randint(1000,9999)}", # NBBM
        gen_guid(), # GDGUID
        area * random.uniform(1.5, 4.0), # 建筑面积
        adm['ring'], # 环线
        random.choice(["重点功能区", "一般区域"]), # 重点功能区
        f"合同WH-{year}-{i:04d}", # 出让合同号划拨决定书
        gen_future_date(start_date, 180), # 约定开工时间 (在供应后半年内)
        gen_future_date(start_date, 1000), # 约定竣工时间 (在供应后3年内)
        0, # 距离开工天数 (int)
        "否", # 是否已撤销
        "正常开工", # 巡查项目开工状态
        gen_guid(), # INSTANCEID
        f"P{year}{random.randint(100000,999999)}", # PROJECTCODE
        1, # SFQDZZHT (int)
        i, # 原始OID (int)
        "无调整", # 调整
        gen_guid(), # uniCode
        str(year), # ssnf
        f"{adm['code_pre']}-{random.randint(1000,9999)}", # QM_DKZX
        adm['street'], adm['dist'], adm['is_main'], 
        "工业园区" if land[0]=="M1" else "非园区", # 工业园区
        1, # 是否参与土地储备供应计算
        adm['gzqh'], # GZQH_GLQMC
        0, # 是否历史数据
        gen_guid(), # uuid
        None # Shape
    )

# 4. 土地征收
def row_tdzs(i):
    adm = get_random_adm()
    year = random.randint(2021, 2024)
    batch = random.randint(1, 20)
    return (
        gen_date(year), # PFRQ
        f"鄂政土批[{year}]{random.randint(1,1000)}号", # PFWH
        f"FA{year}-{batch:03d}", # FABH
        f"{adm['dist']}{year}年度第{batch}批次建设用地", # FAMC
        gen_area_val(300), # CPKFMJ
        gen_area_val(200), # NZDMJ
        gen_guid(), # ID
        adm['dist'], # 所属区
        f"{adm['code_pre']}-{random.randint(1000,9999)}", # QM_DKZX
        adm['street'], adm['is_main'], adm['ring'], 
        "普通区域", "重点开发区", # 工业园区, 重点功能区
        adm['gzqh'], # GZQH_GLQMC
        None # Shape
    )

# 5. 建筑工程许可证
def row_jzgc(i):
    adm = get_random_adm()
    year = random.randint(2021, 2024)
    fzsj = gen_date(year)
    area = gen_area_val(50000)
    land = random.choice(LAND_USE_TYPES)
    
    return (
        f"GC{year}{random.randint(10000,99999)}", # PROJECTCODE
        gen_guid(), # INSTANCEID
        gen_proj_name(adm), # XMMC
        gen_company(), # DWMC
        f"{adm['dist']}{adm['street']}{random.randint(1,200)}号", # JSDZ
        gen_doc_no("license_gc", year), # XKZWH
        "2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", # FAJSSJ...SGTQPSJ (Fill strings)
        fake.name(), # JBR
        "30%", "100m", "2.5", "30%", "5栋", "25层", # JZMD...JZCS
        fake.name(), fake.phone_number(), # DWLXR, LXDH
        "DEPT_001", "窗口", "正常办理", "已发证", "备注信息", "有效", # DEPTID...STATUS
        adm['dist'], "严格按图施工", "HF-001", "无延期", "无说明", "1", "是", "大型", 
        "建设工程规划许可", "SX-001", gen_guid(), "无调整", 
        fzsj, fzsj, # FZSJ, GXSJ
        "新建建筑", str(year), land[1], area * 2.5, # ...容积率
        area * 2.5, # 总建筑面积
        area * 1.5 if land[0].startswith('R') else 0, # 住宅
        0, # 公共管理
        area * 0.8 if land[0].startswith('B') else 0, # 商业
        area * 2.0 if land[0].startswith('M') else 0, # 工业
        25, 80.0, "否", "无", 
        0, # 其它
        "武汉市自然资源和规划局", "无", area * 2.5, 
        adm['dist'], f"{adm['code_pre']}-{random.randint(1000,9999)}", adm['street'], adm['is_main'], adm['ring'], 
        "无", "重点功能区", adm['gzqh'], str(year), 0, area, area * 2.5, None
    )

# 6. 成片开发 (结构同土地征收)
def row_cpkf(i):
    row = list(row_tdzs(i))
    row[3] = row[3].replace("建设用地", "成片开发方案") # FAMC
    return tuple(row)

# 7. 新增建设用地报批
def row_xzjs(i):
    adm = get_random_adm()
    year = random.randint(2022, 2024)
    total = gen_area_val(500)
    return (
        f"K{year}-{i:04d}", # 勘界编号
        f"武汉市{year}年度第{random.randint(1,15)}批次用地", # 批次名称
        gen_guid(), gen_guid(), fake.name(), # PC_ID, INSTANCEID, 主管
        f"{adm['dist']}{adm['street']}", # 位置
        "城镇建设用地", # 用途
        total, total*0.7, total*0.5, total*0.3, 0, total, 
        "符合规划", "T1", gen_date(year), "T3", "T4", 
        "1", i, "无", gen_guid(), str(year), 
        f"{adm['code_pre']}-{random.randint(1000,9999)}", 
        adm['street'], adm['dist'], "重点", adm['is_main'], adm['ring'], 
        "园区A", "是", adm['gzqh'], 0, None
    )

# 8. 用地许可证
def row_ydxk(i):
    adm = get_random_adm()
    year = random.randint(2021, 2024)
    land = random.choice(LAND_USE_TYPES)
    area = gen_area_val(20000)
    
    return (
        f"YD{year}{random.randint(10000,99999)}", # PROJECTCODE
        gen_proj_name(adm), 
        gen_company(), 
        f"选字第{random.randint(10000,99999)}号", 
        gen_doc_no("license_yd", year), 
        land[1], land[1], land[1], # GHYDXZ_DL/ZL/XL
        fake.name(), 
        "国有", f"{adm['dist']}{adm['street']}", "资源规划局", "DEPT_YD", 
        "建设用地", "空地", "H1", "G1", # YDXZ...YDFL
        area, area, 0, 0, 0, # YDMJ...
        str(area*2.0), "2.0", "30%", "60m", "18层", "30%", "中型", 
        "第12期", "3次", "无", gen_guid(), "无", "录入员", "1", "有效", 
        adm['dist'], "严格用地", "无", "", "", "无", str(area), str(area*2), 
        i, "无", gen_guid(), gen_date(year), gen_date(year), 
        str(year), f"{adm['code_pre']}-{random.randint(1000,9999)}", adm['street'], adm['dist'], "重点", adm['is_main'], adm['ring'], "无", 
        1, f"图号{i}", adm['gzqh'], 0, None
    )

# 9. 省级开发 (同国家级，改名)
def row_sjkf(i):
    adm = get_random_adm()
    return (
        f"湖北{adm['dist']}经济开发区", 
        f"HBKF{i:03d}", "省级", "综合产业", gen_area_val(200000), 
        "武汉市", f"KF-{i}", None
    )

# 10. 规划条件 (字段最多，全填充)
def row_ghtj(i):
    adm = get_random_adm()
    year = random.randint(2022, 2024)
    land = random.choice(LAND_USE_TYPES)
    area = gen_area_val(25000)
    fzsj = gen_date(year)
    
    return (
        f"TJ{year}{random.randint(10000,99999)}", gen_guid(), 
        f"{adm['dist']}{adm['street']}规划条件{i}", 
        gen_company(), f"{adm['dist']}{adm['street']}", 
        gen_doc_no("approval", year), adm['dist'], "市局", 
        area, str(area*2.5), "2.5", f"TH-{i}", fzsj, 
        "DEPT_TJ", fzsj, "录入员A", "无", "1", adm['dist'], 
        "2.0-3.0", 1, area*2.5, f"{adm['code_pre']}-{random.randint(1000,9999)}", "AuxCode", 
        "审批通过", "1", fake.name(), "1001", fzsj, 
        land[1], land[1], "30%", "80m", "30%", 
        adm['street'], adm['dist'], "重点功能区", adm['is_main'], adm['ring'], 
        f"FJ_{i}", str(year), f"DK-{i:04d}", 
        area*2.0 if land[0].startswith("R") else 0, # 居住
        area*0.5 if land[0].startswith("B") else 0, # 商服
        0, 0, 0, 
        area*1.0 if land[0].startswith("M") else 0, # 工业
        0, 0, 
        1 if land[0].startswith("R") else 0, # 幼儿园数量
        12 if land[0].startswith("R") else 0, 
        3000 if land[0].startswith("R") else 0, 
        2000 if land[0].startswith("R") else 0, 
        "无", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, # 中小学...
        1000 if land[0].startswith("R") else 0, "配建养老", 
        500, "5%", "有", "有", "有", 2000, 
        "无", "无", "自动录入", area, adm['gzqh'], 
        area, area*0.8, area*2.0, area*3.0, "详细用地性质", "H1", None
    )

# 11. 规划条件核实
def row_ghtjhs(i):
    adm = get_random_adm()
    year = random.randint(2023, 2024)
    area = gen_area_val(20000)
    
    return (
        f"YW{year}{i:05d}", f"XM{year}{i:05d}", gen_company(), gen_proj_name(adm), 
        adm['dist'], f"{adm['dist']}{adm['street']}", 
        f"武规核[{year}]{i:04d}号", f"NO.{random.randint(100000,999999)}", 
        gen_date(year), "竣工验收", 
        str(area), str(area), str(area*2.5), str(area*2.5), 
        "大型", "大型", "合格", "合格", 
        gen_date(year), gen_date(year), 
        f"YD-{i}", f"GC-{i}", f"TD-{i}", "分中心", gen_date(year), 
        "验收通过", "1", adm['dist'], "鄂规核字001", "DEPT_HS", 
        "无", "符合要求", "1", i, "无", gen_guid(), 
        f"{adm['code_pre']}-{random.randint(1000,9999)}", adm['street'], adm['is_main'], adm['ring'], 
        "无", "重点", str(year), area, adm['gzqh'], 0, None
    )

# 12. 选址意见书
def row_xzyj(i):
    adm = get_random_adm()
    year = random.randint(2021, 2024)
    area = gen_area_val(40000)
    land = random.choice(LAND_USE_TYPES)
    
    return (
        f"XZ{year}{random.randint(10000,99999)}", gen_proj_name(adm), gen_company(), 
        f"选字第{year}{i:04d}号", f"地字第{year}{i:04d}号", 
        land[1], land[1], land[1], fake.name(), "国有", 
        f"{adm['dist']}{adm['street']}", f"TH-{i}", "市局", "DEPT_XZ", 
        "建设用地", "空地", "H1", "G1", 
        area, area, 0, 0, 0, area*2.0, "2.0", "30%", "60m", "15层", "30%", "中型", 
        gen_date(year), "1期", "1次", "无", gen_guid(), gen_date(year), "无", "录入员", 
        "1", "1", adm['dist'], "严格控制", "无", "", "", "无", i, "1", i, "无", gen_guid(), 
        str(year), f"{adm['code_pre']}-{random.randint(1000,9999)}", adm['street'], adm['dist'], "重点", adm['is_main'], adm['ring'], 
        "无", adm['gzqh'], 0, None
    )


# ===================== 表配置映射 =====================
TABLE_MAP = {
    "储备要点_问数测试": {
        "cols": ["OBJECTID_1", "PROJECTCOD", "INSTANCEID", "XMMC", "DWMC", "YDWZ", "XKZWH", "DQDW", "SBDW", "GHYDXZ_DL", "JYDMJ", "JZMJ", "RJL", "JZMD", "JZGD", "LHL", "TH", "FZSJ", "DEPTID", "GXSJ", "LRDW", "MEMO_", "SHZT", "ssnf", "ydlx", "xzqname", "approvesta", "QM_DKZX", "GZQH_GLQMC"],
        "func": row_cb_point
    },
    "国家级开发范围_问数测试": {
        "cols": ["KFQDM", "KFQMC", "KFQJB", "PJLX", "PFMJ", "GZQH_GLQMC", "QM_DKZX"],
        "func": row_gjkf
    },
    "土地供应_问数测试": {
        "cols": ["年份", "项目主管", "供地类型", "用地单位名称", "土地坐落", "地籍测量号", "土地用途", "土地面积", "图形面积", "备注", "TEMP1", "TEMP2", "TEMP3", "TEMP4", "TEMPBH", "TEMPJG", "TEMPXY", "TEMPCY", "TEMPJY", "JGH", "NBBM", "GDGUID", "建筑面积", "环线", "重点功能区", "出让合同号划拨决定书", "约定开工时间", "约定竣工时间", "距离开工天数", "是否已撤销", "巡查项目开工状态", "INSTANCEID", "PROJECTCODE", "SFQDZZHT", "原始OID", "调整", "uniCode", "ssnf", "QM_DKZX", "所属街道", "所属区", "主城区", "工业园区", "是否参与土地储备供应计算", "GZQH_GLQMC", "是否历史数据", "uuid", "Shape"],
        "func": row_tdgy
    },
    "土地征收范围_问数测试": {
        "cols": ["PFRQ", "PFWH", "FABH", "FAMC", "CPKFMJ", "NZDMJ", "ID", "所属区", "QM_DKZX", "所属街道", "主城区", "环线", "工业园区", "重点功能区", "GZQH_GLQMC", "Shape"],
        "func": row_tdzs
    },
    "建筑工程许可证_问数测试": {
        "cols": ["PROJECTCODE", "INSTANCEID", "XMMC", "DWMC", "JSDZ", "XKZWH", "FAJSSJ", "FAQPSJ", "SGTJSSJ", "SGTQPSJ", "JBR", "JZMD", "JZGD", "RJL", "LHL", "JZDS", "JZCS", "DWLXR", "LXDH", "DEPTID", "LRDW", "MEMO", "SHZT", "BZ", "STATUS", "QM", "重要说明", "HFXH", "YQSJ", "SM", "ZT", "RGSH", "JSGM", "MATTERNAME", "MATTERNO", "uniCode", "调整", "FZSJ", "GXSJ", "项目类型", "规划许可核发时间", "规划用地性质", "容积率", "总建筑面积", "住宅建筑面积", "公共管理与公共服务建筑面积", "商业服务业建筑面积", "工业仓储建筑面积", "最高建筑层数", "最高建筑高度", "是否混合用地", "备注", "其它建筑面积", "发证单位", "公共服务设施类别", "计容建筑面积", "所属区", "QM_DKZX", "所属街道", "主城区", "环线", "工业园区", "重点功能区", "GZQH_GLQMC", "ssnf", "是否历史数据", "YDMJ", "JZMJ", "Shape"],
        "func": row_jzgc
    },
    "成片开发范围_问数测试": {
        "cols": ["PFRQ", "PFWH", "FABH", "FAMC", "CPKFMJ", "NZDMJ", "ID", "所属区", "QM_DKZX", "所属街道", "主城区", "环线", "工业园区", "重点功能区", "GZQH_GLQMC", "Shape"],
        "func": row_cpkf
    },
    "新增建设用地报批_问数测试": {
        "cols": ["勘界编号", "批次名称", "PC_ID", "INSTANCEID", "项目主管", "用地位置", "规划用途", "总用地", "农用地", "耕地", "建设用地", "未利用地", "图形面积", "备注", "TEMP1", "TEMP2", "TEMP3", "TEMP4", "ZTDM", "原始OID", "调整", "uniCode", "ssnf", "QM_DKZX", "所属街道", "所属区", "重点功能区", "主城区", "环线", "工业园区", "新两园", "GZQH_GLQMC", "是否历史数据", "Shape"],
        "func": row_xzjs
    },
    "用地许可证_问数测试": {
        "cols": ["PROJECTCODE", "XMMC", "DWMC", "XZYJSZH", "YDXKZZH", "GHYDXZ_DL", "GHYDXZ_ZL", "GHYDXZ_XL", "JBRMC", "YDQS", "YDWZ", "ZGBM", "DEPTID", "YDXZ", "XZFL", "TDFL", "YDFL", "YDMJ", "JYDMJ", "DZDLMJ", "CLDYD", "XZDYDMJ", "JZMJ", "RJL", "JZMD", "JZGD", "JZCS", "LHL", "JSGM", "LHQS", "LHCS", "BZ", "INSTANCEID", "MEMO", "LRDW", "SHZT", "STATUS", "QM", "重要说明", "HFXH", "YQSJ", "YQJBR", "SM", "YDMJZZ", "JZMJZZ", "原始OID", "调整", "uniCode", "FZSJ", "GXSJ", "ssnf", "QM_DKZX", "所属街道", "所属区", "重点功能区", "主城区", "环线", "工业园区", "是否参与储备供应计算", "TH", "GZQH_GLQMC", "是否历史数据", "Shape"],
        "func": row_ydxk
    },
    "省级开发范围_问数测试": {
        "cols": ["KFQMC", "KFQDM", "KFQJB", "PJLX", "PFMJ", "GZQH_GLQMC", "QM_DKZX", "Shape"],
        "func": row_sjkf
    },
    "规划条件_问数测试": {
        "cols": ["PROJECTCOD", "INSTANCEID", "XMMC", "DWMC", "YDWZ", "XKZWH", "DQDW", "SBDW", "JYDMJ", "JZMJ_文本", "RJL", "TH", "FZSJ", "DEPTID", "GXSJ", "LRDW", "MEMO_", "SHZT", "xzq", "rjl_gl", "hxwz", "JZMJ", "QM_DKZX", "QM_DKZX1", "approvestateRemark", "approvestate", "lrr", "lrrcode", "lrdate", "GHYDXZ", "GHYDXZ_DL", "JZMD", "JZGD", "LHL", "所属街道", "所属区", "重点功能区", "主城区", "环线", "Fj_id", "ssnf", "地块编号", "居住建筑面积", "商服设施建筑面积", "公共设施建筑面积", "交通设施建筑面积", "公用设施建筑面积", "工业建筑面积", "仓储建筑面积", "其它建筑面积", "幼儿园数量", "幼儿园班数", "幼儿园用地面积", "幼儿园建筑面积", "中小学类型", "中小学数量", "中小学班数", "中小学用地面积", "中小学建筑面积", "中学数量", "中学班数", "中学用地面积", "中学建筑面积", "小学数量", "小学班数", "小学用地面积", "小学建筑面积", "居住配套建筑面积", "居住配套_备注", "公共停车位个数", "公租房配建", "用地许可证", "工程许可证", "验收证号", "地下商业建筑面积", "工业园区", "配建学校", "录入备注", "ZYDMJ", "GZQH_GLQMC", "地下用地面积", "地下建筑面积", "建筑面积_下限", "建筑面积_上限", "GHYDXZ_XX", "TDFL", "Shape"],
        "func": row_ghtj
    },
    "规划条件核实证明_问数测试": {
        "cols": ["业务编号", "项目编号", "单位名称", "项目名称", "建设区属", "建设地址", "规划验收合格证文号", "证书钢印号", "发证时间", "验收类型", "审批用地面积", "竣工用地面积", "审批建筑面积", "竣工建筑面积", "审批规模", "竣工规模", "审批性质", "竣工性质", "放线时间", "验线时间", "用地证号", "工程证号", "土地证号", "录入单位", "更新时间", "备注", "STATUS", "所属区", "省核发登记号", "部门编号", "延期时间及日期", "说明", "ZT", "原始OID", "调整", "uniCode", "QM_DKZX", "所属街道", "主城区", "环线", "工业园区", "重点功能区", "ssnf", "图形面积", "GZQH_GLQMC", "是否历史数据", "Shape"],
        "func": row_ghtjhs
    },
    "选址意见书_问数测试": {
        "cols": ["PROJECTCODE", "XMMC", "DWMC", "XZYJSZH", "YDXKZZH", "GHYDXZ_DL", "GHYDXZ_ZL", "GHYDXZ_XL", "JBRMC", "YDQS", "YDWZ", "TH", "ZGBM", "DEPTID", "YDXZ", "XZFL", "TDFL", "YDFL", "YDMJ", "JYDMJ", "DZDLMJ", "CLDYD", "XZDYDMJ", "JZMJ", "RJL", "JZMD", "JZGD", "JZCS", "LHL", "JSGM", "FZSJ", "LHQS", "LHCS", "BZ", "INSTANCEID", "GXSJ", "MEMO", "LRDW", "SHZT", "STATUS", "QM", "重要说明", "HFXH", "YQSJ", "YQJBR", "SM", "MYID", "ZT", "原始OID", "调整", "uniCode", "ssnf", "QM_DKZX", "所属街道", "所属区", "重点功能区", "主城区", "环线", "工业园区", "GZQH_GLQMC", "是否历史数据", "Shape"],
        "func": row_xzyj
    }
}

# ===================== 执行逻辑 =====================
def get_conn():
    conn_str = f"DRIVER={DRIVER_PATH};SERVER={DB_CONFIG['server']};PORT={DB_CONFIG['port']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['user']};PWD={DB_CONFIG['password']};TDS_Version=7.4;"
    return pyodbc.connect(conn_str)

def fill_table(name, conf, conn):
    table_name = f"[sde].[{name}]"
    cols = conf["cols"]
    func = conf["func"]
    
    # 过滤掉 Shape，不参与 insert
    valid_cols = [c for c in cols if c.lower() != "shape"]
    placeholders = ", ".join(["?"] * len(valid_cols))
    col_str = ", ".join([f"[{c}]" for c in valid_cols])
    sql = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"
    
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        needed = ROWS_PER_TABLE - count
        
        if needed <= 0:
            print(f"⏩ {name} 已有 {count} 行，跳过。")
            return

        print(f"🔄 正在生成 {name}: 需要 {needed} 行...")
        rows = []
        for i in range(needed):
            raw_data = func(count + i + 1)
            # 过滤掉数据元组中对应 Shape 的项
            cleaned_data = []
            for idx, col in enumerate(cols):
                if col.lower() != "shape":
                    cleaned_data.append(raw_data[idx])
            rows.append(tuple(cleaned_data))
        
        cursor.fast_executemany = False
        cursor.executemany(sql, rows)
        conn.commit()
        print(f"✅ {name} 写入完成！")
        
    except Exception as e:
        print(f"❌ {name} 写入失败: {e}")
        conn.rollback()

def main():
    print("🚀 开始生成真实化数据 (全字段补全版)...")
    conn = None
    try:
        conn = get_conn()
        for t_name, t_conf in TABLE_MAP.items():
            fill_table(t_name, t_conf, conn)
    except Exception as e:
        print(f"❌ 数据库连接错误: {e}")
    finally:
        if conn: conn.close()
    print("🏁 所有任务结束。")

if __name__ == "__main__":
    main()