# 🏠 Real Estate Analysis Chatbot

A full-stack web application for analyzing real estate data through an interactive chatbot interface.

## 📋 Features

- ✅ Interactive chat interface for real estate queries
- ✅ Data visualization with Chart.js (price trends, demand analysis)
- ✅ Filtered data tables
- ✅ Excel file upload support
- ✅ Data export functionality
- ✅ Comparison between multiple areas
- ✅ Mock LLM-style summaries (no API key required)
- ✅ Responsive Bootstrap UI

## 🛠️ Tech Stack

### Backend
- Django 4.2.7
- Django REST Framework
- Pandas (data processing)
- OpenPyXL (Excel handling)

### Frontend
- React 18
- Bootstrap 5
- React-Bootstrap
- Chart.js
- Axios

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip
- npm

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start Django server
python manage.py runserver
```

Backend will run at: `http://127.0.0.1:8000`

### Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

Frontend will run at: `http://localhost:3000`

## 📊 Sample Dataset

Download the sample dataset from:
[Google Sheets Link](https://docs.google.com/spreadsheets/d/1BPFvRBLAFFLyQ1EDJ4ogXt8HYCUXhM80/edit?usp=sharing)

Save as `real_estate_data.xlsx` in `backend/data/` directory.

## 🎯 Sample Queries

Try these queries in the chatbot:

```
"Analyze Wakad"
"Compare Aundh and Baner"
"Show price trends for Akurdi"
"What is the demand in Kothrud?"
"Price growth for Ambegaon Budruk over 3 years"
```

## 📁 Project Structure

```
real-estate-chatbot/
├── backend/
│   ├── real_estate_project/      # Django project settings
│   ├── chatbot/                  # Django app
│   ├── utils/                    # Data processing utilities
│   ├── data/                     # Excel data files
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API services
│   │   ├── App.js
│   │   └── App.css
│   └── package.json
└── README.md
```

## 🔌 API Endpoints

- `POST /api/query/` - Process chat queries
- `GET /api/areas/` - Get list of available areas
- `POST /api/upload/` - Upload Excel file
- `POST /api/download/` - Download filtered data
- `GET /api/health/` - Health check

## 🚀 Deployment

### Backend (Render/Heroku)
1. Create `Procfile`:
```
web: gunicorn real_estate_project.wsgi
```

2. Install gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

3. Deploy to Render/Heroku

### Frontend (Vercel/Netlify)
1. Build the app:
```bash
npm run build
```

2. Deploy `build/` folder to Vercel or Netlify

## 📸 Screenshots

### Chat Interface
Interactive chat with real-time analysis

### Results Panel
Charts, statistics, and data tables

## 🎥 Demo Video

Record a 1-2 minute video showing:
1. Starting both servers
2. Asking sample queries
3. Viewing charts and tables
4. Downloading data
5. Uploading a new file

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

## 📝 License

MIT License

## 👨‍💻 Author

Shreyash Patil - Sigmavalue Full Stack Developer Assignment

## 🙏 Acknowledgments

- Django REST Framework
- React
- Chart.js
- Bootstrap
