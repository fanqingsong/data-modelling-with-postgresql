#!/bin/bash

# 一键启动脚本
echo "=========================================="
echo "启动 Sparkify PostgreSQL 数据建模项目"
echo "=========================================="

# 检查 docker compose 是否可用
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 启动服务
echo "正在启动 PostgreSQL 数据库..."
docker compose up -d postgres

# 等待 PostgreSQL 就绪
echo "等待 PostgreSQL 数据库就绪..."
timeout=60
counter=0
while ! docker compose exec -T postgres pg_isready -U student &> /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "错误: PostgreSQL 启动超时"
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""
echo "PostgreSQL 数据库已就绪"

# 启动应用容器
echo "正在启动应用容器..."
docker compose up -d app

# 启动 Web 服务
echo "正在启动 Web 管理界面..."
docker compose up -d web

# 启动 Airflow PostgreSQL
echo "正在启动 Airflow 数据库..."
docker compose up -d postgres_airflow

# 等待 Airflow PostgreSQL 就绪
echo "等待 Airflow 数据库就绪..."
timeout=60
counter=0
while ! docker compose exec -T postgres_airflow pg_isready -U airflow &> /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "错误: Airflow PostgreSQL 启动超时"
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""
echo "Airflow 数据库已就绪"

# 初始化 Airflow 数据库
echo "正在初始化 Airflow 数据库..."
docker compose run --rm airflow-webserver airflow db init || true

# 创建 Airflow 用户（如果不存在）
echo "正在创建 Airflow 用户..."
docker compose run --rm airflow-webserver airflow users create \
    --username airflow \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email admin@example.com \
    --password airflow \
    2>/dev/null || echo "Airflow 用户已存在"

# 启动 Airflow 服务
echo "正在启动 Airflow 服务..."
docker compose up -d airflow-scheduler airflow-webserver

# 启动 Metabase BI 工具
echo "正在启动 Metabase BI 工具..."
docker compose up -d metabase

# 等待服务就绪
sleep 5

# 等待 Airflow 服务就绪
echo "等待 Airflow 服务就绪..."
sleep 5

echo ""
echo "=========================================="
echo "服务启动完成！"
echo "=========================================="
echo ""
echo "🌐 Web 管理界面:"
echo "   http://localhost:5000"
echo ""
echo "🌐 Airflow 管理界面:"
echo "   http://localhost:8080"
echo "   用户名: airflow"
echo "   密码: airflow"
echo ""
echo "📊 Metabase BI 分析工具:"
echo "   http://localhost:3000"
echo "   首次访问需要设置管理员账户"
echo "   数据库连接信息："
echo "   - 类型: PostgreSQL"
echo "   - 主机: postgres"
echo "   - 端口: 5432"
echo "   - 数据库: sparkifydb"
echo "   - 用户名: student"
echo "   - 密码: student"
echo ""
echo "可用操作："
echo "  1. 通过 Web 界面执行操作（推荐）"
echo "     访问 http://localhost:5000"
echo ""
echo "  2. 通过 Airflow 管理定时任务（推荐）"
echo "     访问 http://localhost:8080"
echo "     DAG名称: sparkify_etl_pipeline"
echo "     默认每小时自动执行一次"
echo ""
echo "  3. 命令行操作："
echo "     创建数据库表结构:"
echo "     docker compose exec app python create_tables.py"
echo ""
echo "     执行 ETL 处理:"
echo "     docker compose exec app python etl.py"
echo ""
echo "  4. 查看日志:"
echo "     docker compose logs -f"
echo ""
echo "  5. 停止服务:"
echo "     ./stop.sh"
echo ""
echo "  6. 连接数据库:"
echo "     docker compose exec postgres psql -U student -d sparkifydb"
echo ""

