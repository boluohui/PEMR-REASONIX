# 📋 个人电子病历档案系统 (PEMR)

> **P**ersonal **E**lectronic **M**edical **R**ecord — 基于 Flask 的个人健康档案管理工具

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-000?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite)
![Material Design 3](https://img.shields.io/badge/Material%20Design-3-006B5E?logo=materialdesign)

---

## 📖 简介

个人电子病历档案系统是一款面向个人/家庭使用的医疗健康数据管理工具。它可以帮你集中管理所有就医记录、检验检查结果和处方信息，比纸质病历更方便查找、携带和保存。

### 核心功能

| 模块 | 功能描述 |
|------|---------|
| 🏥 **就医记录** | 记录每次就诊的医院、科室、医生、主诉、现病史、诊断等信息 |
| 🔬 **检验检查** | 管理化验单（血常规、生化等）和影像检查（CT、X光、B超等）结果 |
| 💊 **处方** | 记录处方信息及药品明细（名称、剂量、频次、途径、疗程、数量） |
| 🔗 **关联管理** | 检验检查和处方可以关联到对应的就医记录，形成完整的就诊档案 |
| 🔍 **搜索筛选** | 按关键词搜索、按分类筛选，快速定位历史记录 |
| 📄 **导出** | 将单次就医记录（含关联的检验检查和处方）导出为完整的 HTML 文件 |
| 🎨 **主题切换** | 内置 6 套 Material You 色彩主题 + 暗色模式 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip / venv

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/boluohui/PEMR-REASONIX.git
cd PEMR-REASONIX

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python app.py
```

浏览器打开 **http://localhost:5300** 即可使用。

> 如需从其他设备访问，将 `app.py` 中的 `host="0.0.0.0"` 保持默认，通过服务器 IP 访问（如 `http://192.168.1.100:5300`）。

### 生成测试数据

首次体验可以运行测试数据脚本：

```bash
python seed_data.py
```

将自动创建 5 条就医记录、7 条检验检查结果和 3 张处方（含 9 种药品）。

---

## 🏗 项目结构

```
med-records/
├── app.py                  # 应用入口 (Flask 启动)
├── config.py               # 配置文件 (数据库路径、端口等)
├── models.py               # 数据模型 (ORM)
├── seed_data.py            # 测试数据生成脚本
├── requirements.txt        # Python 依赖
├── routes/
│   ├── __init__.py         # 蓝图注册
│   ├── records.py          # 就医记录 CRUD + 导出
│   ├── exams.py            # 检验检查 CRUD
│   └── prescriptions.py    # 处方 CRUD (含药品明细)
├── templates/
│   ├── base.html           # 基础模板 (M3 Top App Bar + 主题切换)
│   ├── index.html          # 首页 (快捷入口 + 数据概览)
│   ├── records/            # 就医记录页面
│   ├── exams/              # 检验检查页面
│   └── prescriptions/      # 处方页面
└── static/
    └── style.css           # Material Design 3 样式系统
```

---

## 🗄 数据库设计

使用 SQLite 作为本地数据库，无需额外配置数据库服务。文件自动创建在项目根目录 `medical_records.db`。

### 实体关系图

```
┌──────────────────┐       ┌──────────────────┐
│  MedicalRecord   │       │   ExamResult     │
│  (就医记录)       │──1:N──│  (检验检查结果)    │
└──────────────────┘       └──────────────────┘
        │
        │1:N
        ▼
┌──────────────────┐       ┌──────────────────┐
│   Prescription   │──1:N──│ PrescriptionItem │
│   (处方)          │       │  (处方药品明细)    │
└──────────────────┘       └──────────────────┘
```

### 数据表

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `medical_records` | 就医记录 | visit_date, hospital, department, doctor, diagnosis |
| `exam_results` | 检验检查结果 | exam_date, category, exam_name, result, reference_range |
| `prescriptions` | 处方 | prescription_date, doctor, diagnosis |
| `prescription_items` | 处方药品明细 | drug_name, dosage, frequency, route, duration |

---

## 📡 API 路由

### 就医记录 `/records`

| 方法 | 路由 | 功能 |
|------|------|------|
| GET | `/records/` | 就医记录列表（支持 `?search=` 搜索和 `?page=` 分页） |
| GET | `/records/create` | 新建就医记录表单 |
| POST | `/records/create` | 提交新建 |
| GET | `/records/<id>` | 查看详情 |
| GET | `/records/<id>/edit` | 编辑表单 |
| POST | `/records/<id>/edit` | 提交编辑 |
| POST | `/records/<id>/delete` | 删除记录（级联删除关联数据） |
| GET | `/records/<id>/export` | **导出** 完整就医记录为 HTML |

### 检验检查 `/exams`

| 方法 | 路由 | 功能 |
|------|------|------|
| GET | `/exams/` | 列表（支持搜索 + 分类筛选） |
| GET | `/exams/create` | 新建表单 |
| POST | `/exams/create` | 提交新建 |
| GET | `/exams/<id>` | 查看详情 |
| GET | `/exams/<id>/edit` | 编辑 |
| POST | `/exams/<id>/edit` | 提交编辑 |
| POST | `/exams/<id>/delete` | 删除 |

### 处方 `/prescriptions`

| 方法 | 路由 | 功能 |
|------|------|------|
| GET | `/prescriptions/` | 列表 |
| GET | `/prescriptions/create` | 新建处方（含动态增删药品明细行） |
| POST | `/prescriptions/create` | 提交新建 |
| GET | `/prescriptions/<id>` | 查看详情（含药品明细表格） |
| GET | `/prescriptions/<id>/edit` | 编辑 |
| POST | `/prescriptions/<id>/edit` | 提交编辑 |
| POST | `/prescriptions/<id>/delete` | 删除 |

### 首页

| 方法 | 路由 | 功能 |
|------|------|------|
| GET | `/` | 首页（数据概览统计 + 快捷操作入口） |

---

## 🎨 主题系统

基于 **Material Design 3** (Material You) 设计规范，内置 6 套色彩主题：

| 主题 | 特色 | 适用场景 |
|------|------|---------|
| 🟢 **默认** (深青) | 医疗健康色系 | 通用 |
| 🔵 **蓝色** | 专业沉稳 | 办公/医疗 |
| 🟣 **紫色** | 典雅柔和 | 个人喜好 |
| 🌹 **玫红** | 温暖活力 | 女性用户 |
| 🌿 **绿色** | 清新自然 | 护眼 |
| 🌙 **暗色** | 完整暗色模式 | 夜间使用 |

选择后自动保存到浏览器 `localStorage`，下次访问自动恢复。

---

## 🖥 技术栈

| 层次 | 技术 |
|------|------|
| **后端框架** | Flask 3.0 |
| **ORM** | Flask-SQLAlchemy 3.1 (SQLAlchemy 2.0) |
| **数据库** | SQLite |
| **前端** | Bootstrap 5.3 (仅用布局网格) |
| **UI 设计** | Material Design 3 自定义 CSS |
| **图标** | Bootstrap Icons |
| **主题切换** | CSS 变量 + JavaScript |

---

## 📄 导出功能

在就医记录详情页点击 **导出** 按钮，会下载一个自包含的 HTML 文件，包含：

- 就医基本信息（日期、医院、科室、医生）
- 主诉、现病史、诊断、备注
- 所有关联的检验检查结果（表格）
- 所有关联的处方及药品明细（表格）

该 HTML 文件内嵌所有样式，离线打开排版正常。如需 PDF，用浏览器打开后按 **Ctrl+P → 另存为 PDF** 即可。

---

## 📌 注意事项

- ⚠️ 本项目使用 SQLite 数据库，数据文件 `medical_records.db` 默认在项目根目录，请定期备份
- ⚠️ 当前为个人单机使用设计，未实现多用户认证和权限管理
- ⚠️ 生产部署建议使用 Gunicorn / uWSGI 等 WSGI 服务器，配合 Nginx 反代

---

## 📝 License

MIT
