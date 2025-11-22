# OTHER DATA ENGINEERING WORK FOR SPARKIFY
#### [Data Modelling for NoSQL database with Apache Cassandra](https://github.com/lilianatang/data-modelling-with-apache-cassandra)
#### [Building a Cloud Data Warehouse in AWS Redshift & S3](https://github.com/lilianatang/building-aws-cloud-data-warehouse)
#### [Building a Cloud Data Lake in AWS with Spark](https://github.com/lilianatang/building-aws-data-lake)
#### [Building an Automated Data Pipeline with Apache Airflow](https://github.com/lilianatang/automating-data-pipeline-with-airflow)
# INTRODUCTION
### Purpose of the project:
This project is to create a database schema in Postgres & ETL pipeline to optimize queries on song play analysis. 
### What is Sparkify?
Sparkify is a startup that just launched a music streaming application. The application has collected song and user activities in JSON format. The anylytics team wants to understand what songs users are listening to more easily than looping through all the JSON files. 
### How this project is going to help Sparkify
This project will help the analytics team at Sparkify to run queries to understand their end users more.
# DATABASE SCHEMA DESIGN & ETL PROCESS
### Database Schema Design

本项目采用**星型模型（Star Schema）**设计，包含一个事实表和四个维度表。

#### **事实表（Fact Table）**

**songplays** 表是事实表，用于记录每次歌曲播放事件：
- **作用**：存储业务事件（歌曲播放）的核心数据
- **特点**：
  - 数据量大：每次播放都会产生一条记录
  - 增长快速：随时间不断累积
  - 包含度量值：`session_id`、`location`、`user_agent`、`start_time`
  - 包含外键：`user_id`、`song_id`、`artist_id`（指向维度表）
- **字段**：songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
- **用途**：用于统计分析，如播放次数、用户行为分析等

#### **维度表（Dimension Tables）**

维度表提供描述性信息，为事实表提供分析的上下文和分类维度：

1. **users** (user_id, first_name, last_name, gender, level)
   - **作用**：存储用户信息
   - **用途**：分析不同用户群体（性别、会员等级）的播放行为
   - **特点**：数据量相对较小，更新频率低

2. **songs** (song_id, title, artist_id, year, duration)
   - **作用**：存储歌曲信息
   - **用途**：分析热门歌曲、年代分布、歌曲时长等
   - **特点**：提供歌曲的详细描述信息

3. **artists** (artist_id, name, location, latitude, longitude)
   - **作用**：存储艺术家信息
   - **用途**：分析艺术家受欢迎程度、地域分布等
   - **特点**：包含地理位置信息，支持地理分析

4. **time** (start_time, hour, day, week, month, year, weekday)
   - **作用**：存储时间维度信息
   - **用途**：分析播放时间模式、高峰时段、季节性趋势等
   - **特点**：将时间戳分解为多个时间维度，便于时间分析

#### **为什么使用星型模型？**

1. **性能优化**
   - 避免数据冗余，减少存储空间
   - 通过 JOIN 查询，提高查询效率
   - 维度表可以建立索引，加速查询

2. **查询示例**
   ```sql
   -- 找出2024年11月，女性用户播放最多的前10首歌曲
   SELECT 
       s.title AS song_title,
       a.name AS artist_name,
       COUNT(*) AS play_count
   FROM songplays sp
   JOIN users u ON sp.user_id = u.user_id
   JOIN songs s ON sp.song_id = s.song_id
   JOIN artists a ON sp.artist_id = a.artist_id
   JOIN time t ON sp.start_time = t.start_time
   WHERE u.gender = 'F'
     AND t.year = 2024
     AND t.month = 11
   GROUP BY s.title, a.name
   ORDER BY play_count DESC
   LIMIT 10;
   ```

3. **业务价值**
   - **用户分析**：不同性别、会员等级的播放偏好
   - **内容分析**：热门歌曲、艺术家排名
   - **时间分析**：播放高峰时段、季节性趋势
   - **地域分析**：不同地区的音乐偏好

#### **事实表 vs 维度表对比**

| 特性 | 事实表（songplays） | 维度表（users, songs, artists, time） |
|------|-------------------|-------------------------------------|
| **作用** | 记录事件 | 提供上下文 |
| **数据量** | 大（数千到数百万） | 小（几十到几千） |
| **更新频率** | 高频（每次播放） | 低频（用户信息变化、新歌曲） |
| **主要字段** | 度量值 + 外键 | 描述性属性 |
| **查询用途** | 统计、聚合 | 筛选、分组 |

### ETL Process
1. Perform ETL on song_data files to create the songs and artists dimensional tables
2. Perform ETL on log_data files to create the time and user dimensional tables as well as the songplays fact table
# FILES IN REPOSITORY
* etl.py reads and process files from song_data and log_data and loads them into tables.
* create_tables.py drops and creates tables/ 
* sql_queries.py contains all the necessary SQL queries, and is imported into etl.py and create_tables.py
* README.md provides discussion on the project
# HOW TO RUN THE PYTHON SCRIPTS
* Run python create_tables.py to create the database, fact and dimension tables along with insert statements to populate data through etl.py file later
* Run python etl.py to process data from JSON files and populate corresponding data to tables in the database

# DOCKER COMPOSE 部署

## 快速启动

使用一键启动脚本：
```bash
./start.sh
```

使用一键停止脚本：
```bash
./stop.sh
```

## 服务访问

启动成功后，可以访问以下服务：

1. **Web 管理界面** (http://localhost:5000)
   - 查看数据库统计信息
   - 浏览数据表内容
   - 刷新统计数据

2. **Airflow 管理界面** (http://localhost:8080)
   - 用户名: `airflow`
   - 密码: `airflow`
   - 查看 ETL 任务执行状态
   - 手动触发任务执行
   - 查看任务执行历史和日志
   - DAG 名称: `sparkify_etl_pipeline`（每小时自动执行一次）

3. **Metabase BI 分析工具** (http://localhost:3000)
   - 首次访问需要设置管理员账户
   - 连接数据库信息：
     - 类型: PostgreSQL
     - 主机: `postgres`
     - 端口: `5432`
     - 数据库: `sparkifydb`
     - 用户名: `student`
     - 密码: `student`
   - 功能：
     - 可视化查询构建器（无需写 SQL）
     - 自动识别事实表和维度表关系
     - 丰富的图表类型
     - 创建仪表板和报表
     - 支持钻取、切片等 OLAP 操作

## Metabase 使用指南

### 首次设置

1. 访问 http://localhost:3000
2. 设置管理员账户（邮箱、姓名、密码）
3. 选择数据源：PostgreSQL
4. 填写连接信息：
   - 名称：Sparkify Database
   - 主机：`postgres`
   - 端口：`5432`
   - 数据库名：`sparkifydb`
   - 用户名：`student`
   - 密码：`student`
5. 点击"连接"完成设置

### 数据分析示例

#### 示例 1：按性别统计播放次数
1. 点击"新建" → "问题"
2. 选择 `songplays` 表（事实表）
3. 拖拽 `users.gender` 到分组
4. 拖拽 `songplays` 计数到值
5. 选择图表类型（如柱状图）
6. 保存问题

#### 示例 2：热门歌曲 Top 10
1. 新建问题
2. 选择 `songplays` 表
3. 关联 `songs` 表（自动识别关系）
4. 按 `songs.title` 分组
5. 计数 `songplays`
6. 排序：降序
7. 限制：10 条
8. 可视化

#### 示例 3：时间趋势分析
1. 新建问题
2. 选择 `songplays` 表
3. 关联 `time` 表
4. 按 `time.month` 分组
5. 计数 `songplays`
6. 选择折线图查看趋势

### 创建仪表板

1. 点击"新建" → "仪表板"
2. 添加已保存的问题
3. 调整布局和大小
4. 设置筛选器（如时间范围、用户类型等）
5. 保存并分享仪表板

## 服务架构

```
┌─────────────────┐
│   PostgreSQL    │ ← 主数据库（sparkifydb）
│   Port: 5432    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────────┐
    │         │          │             │
    ▼         ▼          ▼             ▼
┌──────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│  Web │ │Airflow │ │ Metabase │ │  App     │
│ :5000│ │ :8080  │ │  :3000   │ │ Container│
└──────┘ └────────┘ └──────────┘ └──────────┘
```

## 数据流程

1. **ETL 流程**（Airflow 自动执行，每小时一次）：
   - `create_tables` 任务：创建/更新数据库表结构
   - `run_etl` 任务：处理 JSON 文件并加载到数据库

2. **数据分析**（Metabase）：
   - 连接 PostgreSQL 数据库
   - 自动识别星型模型（事实表 + 维度表）
   - 通过可视化界面进行数据分析

3. **数据查看**（Web 界面）：
   - 实时查看数据库统计
   - 浏览数据表内容
   - 分页查看数据
