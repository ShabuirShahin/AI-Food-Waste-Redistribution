# AI-Driven Real-Time Food Waste Redistribution System

## Overview
This project is a real-time system designed to reduce food waste by efficiently connecting food donors with nearby NGOs using intelligent prioritization.

----

## Problem Statement
- Significant food wastage in urban areas
- Lack of coordination between donors and NGOs
- Time-sensitive nature of food redistribution

----

## Solution
- AI-based NGO selection using priority scoring
- Real-time notifications via WebSockets
- Feedback-driven learning for improved decision making
- Location-based matching using distance calculation

---

## Key Features
- NGO Registration & Verification
- Food Posting System
- Intelligent Priority Calculation
- Real-Time Notification System
- Feedback Learning Mechanism

---

## Tech Stack
- Backend: FastAPI (Python)
- Database: SQLite with SQLAlchemy
- Real-Time: WebSockets
- Frontend: HTML, CSS, JavaScript
- Server: Uvicorn

---

## System Workflow
1. Donor posts food details
2. System calculates priority based on:
   - Distance
   - Expiry time
   - NGO reliability
3. Best NGO is selected
4. Notification sent in real time
5. NGO feedback improves future predictions

---

## Future Scope
- Integration with map services
- Authentication system (JWT)
- Cloud deployment
- Mobile application

---

## Author
- **Shabuir Shahin.A**
- **Aysha Kethar Fathima.A.S**
