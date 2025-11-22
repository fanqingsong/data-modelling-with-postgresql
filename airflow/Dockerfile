FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.9-slim

# Set Airflow home directory
ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONPATH=/opt/airflow

# Create airflow user
RUN useradd -m -d /opt/airflow -s /bin/bash airflow && \
    mkdir -p /opt/airflow/dags /opt/airflow/logs && \
    chown -R airflow:airflow /opt/airflow

# Configure apt to use Aliyun mirror for faster downloads in China
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's|https://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources; \
    elif [ -f /etc/apt/sources.list ]; then \
        sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list && \
        sed -i 's|https://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list; \
    fi

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Switch to airflow user
USER airflow
WORKDIR /opt/airflow

# Install Airflow and dependencies using Tsinghua mirror
# Skip optional dependencies that require compilation to speed up installation
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    "apache-airflow==2.7.3" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.9.txt" && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    "apache-airflow-providers-postgres==5.8.0" \
    psycopg2-binary \
    pandas \
    numpy

# Copy DAG files and scripts
COPY --chown=airflow:airflow dags/ /opt/airflow/dags/
COPY --chown=airflow:airflow create_tables.py /opt/airflow/dags/
COPY --chown=airflow:airflow etl.py /opt/airflow/dags/
COPY --chown=airflow:airflow sql_queries.py /opt/airflow/dags/

# Set PATH
ENV PATH="${PATH}:/opt/airflow/.local/bin"

