FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.9-slim

WORKDIR /app

# Configure apt to use Aliyun mirror for faster downloads in China
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's|https://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources; \
    elif [ -f /etc/apt/sources.list ]; then \
        sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list && \
        sed -i 's|https://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list; \
    fi

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
# Use Tsinghua mirror for pip to speed up installation in China
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Copy application files
COPY . .

# Default command (can be overridden in docker-compose.yml)
CMD ["python", "--version"]

