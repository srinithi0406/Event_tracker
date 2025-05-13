# EventWise - Event Management and Tracking System

## Problem Statement Overview
The goal was to design and build an Event Management Application that streamlines event flow using unique digital identifiers (QR codes) for attendees. The system needed to handle attendee onboarding via CSV, track registrations, manage kit/lunch distribution, and provide a central dashboard for event statistics.

## Solution Overview
EventWise is a Flask-based web application that:
- Generates unique QR codes for each attendee from CSV data
- Tracks event check-ins and kit distribution
- Prevents duplicate registrations and kit collections
- Provides a comprehensive dashboard with statistics
- Generates PDF reports for event analytics
- Supports multiple events with different dates

## Features

### Core Features
* **CSV-based Attendee Onboarding**
  - Upload CSV files with attendee details
  - Automatic QR code generation for each attendee
  - Prevents duplicate entries

* **Registration Tracking**
  - QR code scanning for check-ins
  - Prevents double registration
  - Provides immediate feedback

* **Kit Distribution Tracking**
  - Tracks kit/lunch collection
  - Ensures attendees check-in before collecting kits
  - Prevents multiple collections

* **Central Dashboard**
  - Real-time statistics (total, registered, kits distributed)
  - Filterable attendee lists
  - Event-specific tracking

### Bonus Features Implemented
* Multi-day event support
* Comprehensive PDF report generation
* Offline-capable (SQLite database)
* Responsive web interface

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip package manager

### Dependencies
Install the required packages using:
```bash
pip install flask qrcode[pil] reportlab
```

## Running the Application

1. Clone the repository:
```bash
git clone https://github.com/yourusername/event_tracker.git
cd event_tracker
```
2. Install dependencies:
```
pip install flask qrcode[pil] reportlab
```
3. Run the application:
```
python app.py
```

### CSV Format

The system expects CSV files with the following columns:

Name,Email,Phone,Role

## Folder Structure
```
event_tracker/
├── static/
│   ├── css/
│   │   └── style.css
│   └── qrcodes/          # Generated QR codes are stored here
├── templates/
│   ├── index.html        # Main interface
│   └── dashboard.html    # Dashboard interface
├── app.py                # Main application file
└── event_data.db         # SQLite database 
```
