# 🎓 EduGenie: AI-Powered Educational Assistant

EduGenie is a lightweight AI-powered educational assistant that simplifies learning through generative AI powered by **Google Gemini** and **FastAPI**. Designed for learners of all academic levels, EduGenie offers interactive Q&A, intuitive concept simplifications, dynamic quizzes with real-time scoring, structured learning path roadmaps, and high-yield passage summarization.

---

## 🌟 Key Features & Supported Scenarios

| Feature | Description | Scenario Addressed |
| :--- | :--- | :--- |
| **💬 Smart Q&A** | Ask any educational question and receive clear, concise, curriculum-aligned answers. | **Scenario 1:** Ask *“Which is the largest ocean?”* and get instant smart answers. |
| **💡 Concept Explainer** | Break down complex concepts with intuitive real-world analogies (ELI5 to College). | Understand complex topics like Quantum Computing, Relativity, or Neural Networks. |
| **📝 Interactive Quiz Generator** | Generate custom multiple-choice quizzes with live scoring and explanations. | **Scenario 2:** Check mastery of *“The Pythagoras Theorem”* with interactive questions. |
| **🗺️ Learning Path Roadmaps** | Generate week-by-week structured curriculum plans with milestones and projects. | **Scenario 3:** Request a structured *“SQL Beginner to Advanced”* learning path. |
| **📄 Smart Summarizer** | Distill large educational texts into bulleted key takeaways, abstracts, or flashcards. | Summarize lengthy textbooks, scientific papers, and articles. |

---

## 🚀 Technology Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python asynchronous framework)
- **AI Engine:** [Google Gemini API](https://ai.google.dev/) (`gemini-1.5-flash`)
- **Frontend:** Responsive Glassmorphism UI (HTML5, Modern CSS tokens, Jinja2 Templates, FontAwesome, Marked.js)
- **Environment Management:** `python-dotenv`, `pydantic`

---

## 🛠️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Clone / Open Project
```bash
cd EduGen
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create or verify your `.env` file in the root directory:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 5. Run the Application
```bash
python main.py
```
or via Uvicorn directly:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Access EduGenie
Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 📌 API Endpoints

- `GET /` — Interactive web application interface.
- `POST /api/ask` — Educational Q&A endpoint (`{ "text": "...", "level": "High School" }`).
- `POST /api/explain` — Concept simplifier (`{ "concept": "...", "target_audience": "..." }`).
- `POST /api/quiz` — Interactive quiz generator (`{ "topic": "...", "difficulty": "Medium", "num_questions": 4 }`).
- `POST /api/learning-path` — Structured roadmap planner (`{ "topic": "...", "current_level": "Beginner", "timeframe_weeks": 6 }`).
- `POST /api/summarize` — Passage summarizer (`{ "text": "...", "format": "bullet_points" }`).

---

## 👨‍💻 Project Deliverables Checklist
- [x] Functional FastAPI backend with all 5 educational endpoints in [main.py](file:///d:/EduGen/main.py).
- [x] Responsive, modern frontend in [templates/index.html](file:///d:/EduGen/templates/index.html) with 1-click test buttons for all scenarios.
- [x] Interactive Quiz Engine with real-time feedback and scoring.
- [x] Visual roadmap timeline renderer for personalized learning paths.
