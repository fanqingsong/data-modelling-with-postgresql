import os
import subprocess
import psycopg2
import json
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Store for background task status
task_status = {
    'create_tables': {'running': False, 'output': '', 'error': ''},
    'etl': {'running': False, 'output': '', 'error': ''}
}

# Get database connection parameters from environment variables
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'sparkifydb')
DB_USER = os.getenv('DB_USER', 'student')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'student')
DEFAULT_DB = os.getenv('DEFAULT_DB', 'studentdb')

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

def run_command_background(command):
    """Run command in background thread"""
    script = 'create_tables.py' if command == 'create_tables' else 'etl.py'
    task_status[command]['running'] = True
    task_status[command]['output'] = ''
    task_status[command]['error'] = ''
    
    try:
        process = subprocess.Popen(
            ['python', script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd='/app',
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output in real-time
        output_lines = []
        error_lines = []
        
        # Read stdout
        for line in process.stdout:
            output_lines.append(line)
            task_status[command]['output'] = ''.join(output_lines)
        
        # Read stderr
        for line in process.stderr:
            error_lines.append(line)
            task_status[command]['error'] = ''.join(error_lines)
        
        process.wait()
        
        task_status[command]['output'] = ''.join(output_lines)
        task_status[command]['error'] = ''.join(error_lines)
        task_status[command]['success'] = process.returncode == 0
        
    except Exception as e:
        task_status[command]['error'] = str(e)
        task_status[command]['success'] = False
    finally:
        task_status[command]['running'] = False

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute create_tables.py or etl.py in background"""
    data = request.json
    command = data.get('command')
    
    if command not in ['create_tables', 'etl']:
        return jsonify({'error': 'Invalid command'}), 400
    
    # Check if task is already running
    if task_status[command]['running']:
        return jsonify({
            'success': False,
            'error': 'Task is already running',
            'running': True
        }), 400
    
    # Start task in background thread
    thread = threading.Thread(target=run_command_background, args=(command,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Task started in background',
        'running': True
    })

@app.route('/api/execute/status/<command>')
def get_execute_status(command):
    """Get execution status"""
    if command not in ['create_tables', 'etl']:
        return jsonify({'error': 'Invalid command'}), 400
    
    status = task_status[command].copy()
    return jsonify(status)

@app.route('/api/tables')
def list_tables():
    """List all tables"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'tables': tables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/table/<table_name>')
def get_table_data(table_name):
    """Get table data"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        # Get column names
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (table_name,))
        columns = [{'name': row[0], 'type': row[1]} for row in cur.fetchall()]
        
        # Get row count
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cur.fetchone()[0]
        
        # Get data with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        offset = (page - 1) * per_page
        
        cur.execute(f"SELECT * FROM {table_name} LIMIT %s OFFSET %s", (per_page, offset))
        rows = cur.fetchall()
        
        # Convert rows to list of dicts
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Convert datetime and other types to string
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif value is None:
                    value = None
                else:
                    value = str(value)
                row_dict[col['name']] = value
            data.append(row_dict)
        
        cur.close()
        conn.close()
        
        return jsonify({
            'columns': columns,
            'data': data,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'pages': (total_count + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        stats = {}
        
        tables = ['songplays', 'users', 'songs', 'artists', 'time']
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cur.fetchone()[0]
            except:
                stats[table] = 0
        
        cur.close()
        conn.close()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

