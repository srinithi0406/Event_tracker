# EventWise - Event Management and Tracking System

## Problem Statement Overview
Managing large-scale events can often be overwhelming. From attendee registration and check-in to distributing lunch kits or swag bags, every process demands precision and speed. Relying on manual methods is time-consuming, error-prone, and inefficient, especially when managing multiple events or multi-day programs. There is a pressing need for a seamless, automated solution that simplifies event management, prevents duplication, and ensures an organized flow of operations.

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

### Unique Features Implemented
 - Multi-event and Multi-day Handling: Supports various events and sessions across different days.
 - Live Stats with Visualization: Pie charts and tables make the dashboard highly intuitive and easy to interpret data.
 - Downloadable Reports: Export check-ins and distribution stats as PDF.
 - Secure QR Code System: Each attendee gets a unique, tamper-proof QR code.
 - Global Search & Filters: Easily find any attendee and check their real-time status.

## Tech stack used:
- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask)
- Database: SQLite
- Libraries used: QRCode, ReportLab

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
git clone https://github.com/srinithi0406/Event_tracker.git
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

## Demo link
[Click here for the Demo link of the web application](https://drive.google.com/file/d/11W6Z19SkPeV7QYse6xqgtyy8VMZPnQtO/view?usp=drivesdk)
