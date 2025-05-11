from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from threading import Lock
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

DATABASE = os.path.abspath('seats.db')  # Absolute path
db_lock = Lock()  # Critical for SQLite thread safety

def init_db():  
    with db_lock:
        conn = sqlite3.connect(DATABASE)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS seats (
            id INTEGER PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'empty'
        )''')
        # Initialize seats
        for seat_id in [1, 2, 3]:
            conn.execute('INSERT OR IGNORE INTO seats (id, status) VALUES (?, ?)', 
                       (seat_id, 'empty'))
        conn.commit()
        conn.close()

@app.route('/update_status', methods=['GET'])
def update_status():
    seat = request.args.get('seat', type=int)
    status = request.args.get('status')
    
    print(f"\nReceived: Seat {seat} -> {status}")  # Debug

    
    if not all([seat in [1,2,3], status in ['empty','solo','group']]):
        return jsonify({'error': 'Invalid parameters'}), 400
    
    try:
        with db_lock:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Debug current state
            cursor.execute('SELECT status FROM seats WHERE id = ?', (seat,))
            old_status = cursor.fetchone()[0]
            print(f"Current status: {old_status}")
            
            # Perform update
            cursor.execute('UPDATE seats SET status = ? WHERE id = ?', 
                         (status, seat))
            conn.commit()
            
            # Verify update
            cursor.execute('SELECT status FROM seats WHERE id = ?', (seat,))
            new_status = cursor.fetchone()[0]
            print(f"Updated status: {new_status}")
            
            conn.close()
            return jsonify({'success': True, 'seat': seat, 'status': new_status})
            
    except Exception as e:
        print(f" Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_status')
def get_status():
    with db_lock:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        seats = conn.execute('SELECT * FROM seats ORDER BY id').fetchall()
        conn.close()
        return jsonify([dict(seat) for seat in seats])

@app.route('/')
def index():
    return render_template('dashboard2.html')

@app.route('/reset_status', methods=['POST'])
def reset_status():
    print("Received request to reset status")
    try:
        with db_lock:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('UPDATE seats SET status = "empty"')
            conn.commit()
            conn.close()
        print("Successfully reset status")
        return jsonify({'success': True})
    except Exception as e:
        print("Error during reset:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)