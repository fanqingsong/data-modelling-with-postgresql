#!/bin/bash

# 一键停止脚本
echo "=========================================="
echo "停止 Sparkify PostgreSQL 数据建模项目"
echo "=========================================="

# 检查 docker compose 是否可用
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi

# 停止并删除容器
echo "正在停止服务..."
docker compose down

echo ""
echo "=========================================="
echo "服务已停止"
echo "=========================================="
echo ""
echo "注意: 数据库数据已保存在 Docker volume 中"
echo "如需完全清理（包括数据），请运行:"
echo "  docker compose down -v"
echo ""

