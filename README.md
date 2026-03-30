# 🚀 Finance Tracker API & Dashboard

A high-performance personal finance management system built with **FastAPI** (Backend), **SQLite** (Database), and **Streamlit** (Analytics Frontend). This project demonstrates a clean separation of concerns between an asynchronous API and a reactive data visualization layer.

---

## 🏗️ System Architecture

The application follows a decoupled, modular architecture to ensure scalability and ease of maintenance:

1. **Backend:** FastAPI handles high-speed data validation, SQL transactions, and RESTful routing.
2. **Database:** SQLite/PostgreSQL manages persistent storage of financial records with strict data integrity.
3. **Frontend:** Streamlit provides a real-time, interactive dashboard for comprehensive financial data analysis.

---

## ⚡ Tech Stack

This project leverages modern engineering tools for optimal performance:

* **Frameworks:** FastAPI (Asynchronous Python Framework)
* **Database:** SQLite / PostgreSQL (SQLAlchemy ORM)
* **Frontend:** Streamlit (Reactive Data Dashboards)
* **Validation:** Pydantic Models for strict type checking
* **Server:** Uvicorn (ASGI Server)

---

## 📡 API Endpoints (RESTful Design)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/transactions/` | Create a new income or expense record. |
| `GET` | `/transactions/` | Retrieve all transactions with advanced filtering. |
| `GET` | `/summary/` | Fetch total income, balance, and expense metrics. |
| `DELETE` | `/transactions/{id}` | Remove a specific financial record by ID. |

---

🛠️ Features & Impact
This platform offers professional-grade financial tracking capabilities:

Real-time Analytics: Automated category-wise breakdown and dynamic monthly spending trends.

Data Integrity: Implementation of strict Pydantic models for robust request validation and error handling.

Scalable Design: Decoupled architecture allowing for seamless migration from SQLite to PostgreSQL.

Top Transactions: Intelligent logic to identify and highlight high-value financial events automatically.

🚀 Installation & Setup
Follow these simple steps to set up the project locally:

1️⃣ Clone the Repository
Bash
git clone [https://github.com/Savaliya03/finance-tracker-fastapi.git](https://github.com/Savaliya03/finance-tracker-fastapi.git)
cd finance-tracker-fastapi
2️⃣ Environment Setup
Create and activate a virtual environment to manage dependencies:

Bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
3️⃣ Install Dependencies
Bash
pip install -r requirements.txt
4️⃣ Launch Services
Start the Backend API:

Bash
uvicorn main:app --reload
Launch the Frontend Dashboard:

Bash
streamlit run index.py
📜 License
This project is licensed under the MIT License — allowing for modification, distribution, and private use.

🙌 Acknowledgements
Special thanks to the open-source communities behind FastAPI and Streamlit for providing the tools to build scalable and interactive web applications.


---

## Final Verdict

**UNIFORMITY 100% ACHIEVED.** હવે આ ફોર્મેટમાં તારો કોલેજ પ્રોજેક્ટ અને પેલો મોડલ ટ્રેનિંગ પ્રોજેક્ટ બંને એકસરખા પ્રોફેશનલ દેખાશે. આમાં ઇન્સ્ટોલેશનના સ્ટેપ્સ અને કોડ બ્લોક્સ હવે એકદમ ક્લીન છે.

શું તારે હવે આ પ્રોજેક્ટ માટે કોઈ **Demo Screenshots** માટેની જગ્યા (Placeholders) ઉમેરવી છે?
