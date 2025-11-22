"""
Sparkify ETL DAG
每小时执行一次数据ETL处理
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import sys

# 添加项目路径到 Python 路径
sys.path.insert(0, '/opt/airflow/dags')

# 导入ETL模块（使用别名避免与任务名冲突）
try:
    from create_tables import create_database, drop_tables, create_tables as create_tables_func
    from etl import process_data, process_song_file, process_log_file
    from sql_queries import create_table_queries, drop_table_queries
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    # 如果导入失败，定义占位函数
    def create_tables_func(cur, conn):
        pass
    def drop_tables(cur, conn):
        pass

# 默认参数
default_args = {
    'owner': 'sparkify',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 创建 DAG
dag = DAG(
    'sparkify_etl_pipeline',
    default_args=default_args,
    description='Sparkify 数据ETL处理管道',
    schedule_interval=timedelta(hours=1),  # 每小时执行一次
    catchup=False,
    tags=['sparkify', 'etl', 'postgresql'],
)

def create_tables_task():
    """创建数据库表结构（仅在数据库不存在时创建，表已存在则跳过）"""
    import psycopg2
    
    # 获取数据库连接参数
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('DB_USER', 'student')
    db_password = os.getenv('DB_PASSWORD', 'student')
    default_db = os.getenv('DEFAULT_DB', 'studentdb')
    target_db = os.getenv('DB_NAME', 'sparkifydb')
    
    # 连接到默认数据库检查sparkifydb是否存在
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=default_db,
        user=db_user,
        password=db_password
    )
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    # 检查数据库是否存在
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
    db_exists = cur.fetchone()
    
    if not db_exists:
        # 创建sparkify数据库
        cur.execute("CREATE DATABASE sparkifydb WITH ENCODING 'utf8' TEMPLATE template0")
        print(f"Database {target_db} created")
    else:
        print(f"Database {target_db} already exists")
    
    conn.close()
    
    # 连接到sparkify数据库
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=target_db,
        user=db_user,
        password=db_password
    )
    cur = conn.cursor()
    
    # 检查表是否存在，如果不存在则创建
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'songplays'
        )
    """)
    tables_exist = cur.fetchone()[0]
    
    if not tables_exist:
        # 创建表
        drop_tables(cur, conn)
        create_tables_func(cur, conn)
        print("Tables created successfully")
    else:
        print("Tables already exist, skipping creation")
    
    conn.close()

def etl_task():
    """执行ETL处理"""
    import psycopg2
    
    # 获取数据库连接参数
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'sparkifydb')
    db_user = os.getenv('DB_USER', 'student')
    db_password = os.getenv('DB_PASSWORD', 'student')
    
    # 获取数据文件路径（相对于 DAG 目录）
    dag_dir = os.path.dirname(os.path.abspath(__file__))
    song_data_path = os.path.join(dag_dir, 'data', 'song_data')
    log_data_path = os.path.join(dag_dir, 'data', 'log_data')
    
    print(f"DAG directory: {dag_dir}")
    print(f"Song data path: {song_data_path}")
    print(f"Log data path: {log_data_path}")
    print(f"Song data exists: {os.path.exists(song_data_path)}")
    print(f"Log data exists: {os.path.exists(log_data_path)}")
    
    # 连接数据库
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    cur = conn.cursor()
    
    # 执行ETL处理（使用绝对路径）
    process_data(cur, conn, filepath=song_data_path, func=process_song_file)
    process_data(cur, conn, filepath=log_data_path, func=process_log_file)
    
    conn.close()
    print("ETL process completed successfully")

# 定义任务
create_tables = PythonOperator(
    task_id='create_tables',
    python_callable=create_tables_task,
    dag=dag,
)

run_etl = PythonOperator(
    task_id='run_etl',
    python_callable=etl_task,
    dag=dag,
)

# 设置任务依赖：先创建表，再执行ETL
create_tables >> run_etl

