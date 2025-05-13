from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
import qrcode
import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO


app = Flask(__name__)

# Ensure the QR code folder exists
QR_FOLDER = 'static/qrcodes'
os.makedirs(QR_FOLDER, exist_ok=True)

# Initialize DB
def init_db():
    conn = sqlite3.connect('event_data.db')
    cursor = conn.cursor()

    # Create events table
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        day TEXT
                    )''')

    # Create attendees table with a foreign key reference to events
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        phone TEXT,
                        role TEXT,
                        qr_code TEXT,
                        is_registered INTEGER DEFAULT 0,
                        got_kit INTEGER DEFAULT 0,
                        event_id INTEGER,
                        FOREIGN KEY (event_id) REFERENCES events(id)
                    )''')
    
    conn.commit()
    conn.close()


# Home route
@app.route('/')
def index():
    return render_template('index.html', active_page='home')

# Upload CSV page
@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files['file']
        event_name = request.form.get('event_name')
        event_day = request.form.get('event_day')
        
        conn = sqlite3.connect('event_data.db')
        cursor = conn.cursor()
        
        # Check if the event exists
        cursor.execute("SELECT id FROM events WHERE name=? AND day=?", (event_name, event_day))
        event = cursor.fetchone()

        if not event:
            # Create a new event
            cursor.execute("INSERT INTO events (name, day) VALUES (?, ?)", (event_name, event_day))
            conn.commit()
            event_id = cursor.lastrowid
        else:
            event_id = event[0]

        # Save and process the CSV
        filepath = 'attendees.csv'
        file.save(filepath)

        with open(filepath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                name = row['Name']
                email = row['Email']
                phone = row['Phone']
                role = row['Role']
                unique_id = f"{name}_{email}".replace(" ", "_")
                qr_path = os.path.join(QR_FOLDER, f"{unique_id}.png")

                # Check for duplicates
                cursor.execute("SELECT COUNT(*) FROM attendees WHERE name=? AND email=? AND event_id=?", 
                               (name, email, event_id))
                exists = cursor.fetchone()[0]

                if exists:
                    continue  # Skip duplicates

                # Generate QR code
                qr = qrcode.make(unique_id)
                qr.save(qr_path)

                # Insert attendee
                cursor.execute('''INSERT INTO attendees (name, email, phone, role, qr_code, event_id)
                                VALUES (?, ?, ?, ?, ?, ?)''',
                               (name, email, phone, role, qr_path, event_id))

        conn.commit()
        conn.close()

        # Redirect to dashboard with event_id
        return redirect(url_for('dashboard', event_id=event_id))
    
    return render_template('index.html', active_page='upload_csv')


# Check-in page
@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        qr_data = request.json['qr_data']
        event_id = request.json['event_id']
        conn = sqlite3.connect('event_data.db')
        cursor = conn.cursor()

        # Check if the attendee exists by QR code and event_id
        cursor.execute("SELECT id, name, is_registered FROM attendees WHERE qr_code LIKE ? AND event_id = ?", 
                       (f"%{qr_data}.png", event_id))
        row = cursor.fetchone()

        if row:
            attendee_id, name, is_registered = row
            if is_registered == 1:
                msg = f"{name}, you have already registered!"
            else:
                # Mark the attendee as registered for this event
                cursor.execute("UPDATE attendees SET is_registered = 1 WHERE id = ?", (attendee_id,))
                conn.commit()
                msg = f"{name}, you have been successfully registered for this event!"
        else:
            msg = "Attendee not found for this event!"

        conn.close()
        return jsonify({'message': msg})
    
    # Fetch events for dropdown
    conn = sqlite3.connect('event_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, day FROM events")
    events = cursor.fetchall()
    conn.close()

    # Pass events to template
    return render_template('index.html', active_page='checkin', events=events)


# Kit collection page
@app.route('/kitbag', methods=['GET', 'POST'])
def kitbag():
    if request.method == 'POST':
        qr_data = request.json['qr_data']
        event_id = request.json['event_id']
        conn = sqlite3.connect('event_data.db')
        cursor = conn.cursor()

        # Find attendee by QR code and event_id
        cursor.execute("SELECT id, name, got_kit, is_registered FROM attendees WHERE qr_code LIKE ? AND event_id = ?", 
                       (f"%{qr_data}.png", event_id))
        row = cursor.fetchone()

        if row:
            attendee_id, name, got_kit, is_registered = row

            if got_kit == 1:
                msg = f"{name}, your kit has already been collected!"
            elif is_registered != 1:
                msg = f"{name}, please check-in first before collecting your kit!"
            else:
                # Only update if checked in and not already collected
                cursor.execute("UPDATE attendees SET got_kit = 1 WHERE id = ?", (attendee_id,))
                conn.commit()
                msg = f"Success: {name}, your kit collection is confirmed for this event!"
        else:
            msg = "Attendee not found for this event!"

        conn.close()
        return jsonify({'message': msg})

    # Fetch events for dropdown
    conn = sqlite3.connect('event_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, day FROM events")
    events = cursor.fetchall()
    conn.close()

    # Pass events to template
    return render_template('index.html', active_page='kitbag', events=events)


# Dashboard
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('event_data.db')
    cursor = conn.cursor()
    event_id = request.args.get('event_id')

    # Always get events list for the dropdown
    cursor.execute("SELECT id, name, day FROM events")
    events = cursor.fetchall()

    if not event_id:
        conn.close()
        return render_template(
            'dashboard.html',
            events=events,
            stats={'total': 0, 'registered': 0, 'kits': 0},
            attendees=[],
            registered_attendees=[],
            kit_attendees=[],
            event_name=None,
            event_day=None,
            event_id=None
        )


    # Fetch event details
    cursor.execute("SELECT * FROM events WHERE id=?", (event_id,))
    event = cursor.fetchone()

    if not event:
        conn.close()
        return render_template('dashboard.html', events=events)

    # Fetch attendees for the selected event
    cursor.execute("SELECT * FROM attendees WHERE event_id=?", (event_id,))
    data = cursor.fetchall()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM attendees WHERE event_id=?", (event_id,))
    total = cursor.fetchone()[0]

    # Checked-in count and list
    cursor.execute("SELECT * FROM attendees WHERE event_id=? AND is_registered = 1", (event_id,))
    registered_data = cursor.fetchall()
    registered = len(registered_data)

    # Kits collected count and list
    cursor.execute("SELECT * FROM attendees WHERE event_id=? AND got_kit = 1", (event_id,))
    kits_data = cursor.fetchall()
    kits = len(kits_data)

    stats = {
        'total': total,
        'registered': registered,
        'kits': kits
    }

    conn.close()

    return render_template(
        'dashboard.html',
        events=events,  
        attendees=data,
        stats=stats,
        registered_attendees=registered_data,
        kit_attendees=kits_data,
        event_name=event[1],
        event_day=event[2],
        event_id=event_id
    )

@app.route('/get_events')
def get_events():
    conn = sqlite3.connect('event_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, day FROM events")
    events = [{'id': row[0], 'name': row[1], 'day': row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(events)

# Generate event report
@app.route('/download_report/<int:event_id>')
def download_report(event_id):
    conn = sqlite3.connect('event_data.db')
    cursor = conn.cursor()
    
    # Get event details
    cursor.execute("SELECT name, day FROM events WHERE id=?", (event_id,))
    event = cursor.fetchone()
    if not event:
        return "Event not found", 404
    
    event_name, event_day = event
    
    # Get all attendees data
    cursor.execute("SELECT name, email, phone, is_registered, got_kit FROM attendees WHERE event_id=?", (event_id,))
    attendees = cursor.fetchall()
    conn.close()
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Content elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph(f"EventWise Report: {event_name}", styles['Title']))
    elements.append(Paragraph(f"Event Date: {event_day}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Summary statistics
    total = len(attendees)
    registered = sum(1 for a in attendees if a[3] == 1)
    kits = sum(1 for a in attendees if a[4] == 1)
    
    summary_data = [
        ["Total Attendees", str(total)],
        ["Checked In", f"{registered} ({registered/total*100:.1f}%)"],
        ["Kits Collected", f"{kits} ({kits/total*100:.1f}%)"],
        ["Not Checked In", f"{total - registered} ({(total-registered)/total*100:.1f}%)"]
    ]
    
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 24))
    
    # Detailed attendee data
    elements.append(Paragraph("Attendee Details", styles['Heading2']))
    
    # Prepare data for table
    attendee_data = [["Name", "Email", "Phone", "Status", "Kit"]]
    
    for attendee in attendees:
        name, email, phone, is_registered, got_kit = attendee
        status = "Checked In" if is_registered == 1 else "Not Checked In"
        kit_status = "Collected" if got_kit == 1 else "Not Collected"
        attendee_data.append([name, email, phone, status, kit_status])
    
    attendee_table = Table(attendee_data, colWidths=[120, 150, 100, 80, 80])
    attendee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(attendee_table)
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=EventWise_Report_{event_name.replace(" ", "_")}.pdf'
    }

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
