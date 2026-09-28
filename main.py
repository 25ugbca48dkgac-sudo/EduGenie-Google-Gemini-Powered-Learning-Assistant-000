import os
import json
import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set in .env file!")

genai.configure(api_key=api_key)

app = FastAPI(title="EduGenie", description="AI-Powered Educational Assistant")

templates = Jinja2Templates(directory="templates")

# Cached working model helper with dynamic auto-fallback
_cached_model = None

def get_model():
    global _cached_model
    if _cached_model is not None:
        return _cached_model
    
    candidate_models = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-2.5-pro",
        "gemini-pro-latest"
    ]
    
    for candidate in candidate_models:
        try:
            _cached_model = genai.GenerativeModel(candidate)
            return _cached_model
        except Exception:
            continue
            
    # Fallback to listing models dynamically
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                model_name = m.name.replace("models/", "")
                _cached_model = genai.GenerativeModel(model_name)
                return _cached_model
    except Exception:
        pass
        
    _cached_model = genai.GenerativeModel("gemini-3.8-flash")
    return _cached_model


# Request Models
class QueryRequest(BaseModel):
    text: str
    level: Optional[str] = "High School"

class ExplainRequest(BaseModel):
    concept: str
    target_audience: Optional[str] = "Beginner (ELI5)"
    include_analogy: Optional[bool] = True

class QuizRequest(BaseModel):
    topic: str
    num_questions: Optional[int] = 4
    difficulty: Optional[str] = "Medium"

class LearningPathRequest(BaseModel):
    topic: str
    current_level: Optional[str] = "Beginner"
    target_goal: Optional[str] = "Industry Ready / Mastery"
    timeframe_weeks: Optional[int] = 6

class SummaryRequest(BaseModel):
    text: str
    format: Optional[str] = "bullet_points" # "bullet_points", "executive", "flashcards"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/ask")
async def ask_question(request: QueryRequest):
    """Scenario 1: Ask questions and receive smart, concise answers."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")
            
        model = get_model()
        prompt = f"""
You are EduGenie, an expert and supportive educational AI tutor.
Audience Level: {request.level}

Question:
{request.text}

Instructions:
- Provide a smart, clear, concise, and academically accurate response.
- Use clean formatting (bullet points, bold highlights, or short paragraphs).
- If relevant, provide 1 quick 'Did You Know?' or real-world example at the end.
"""
        response = model.generate_content(prompt)
        return {"success": True, "answer": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@app.post("/api/explain")
async def explain_concept(request: ExplainRequest):
    """Understand complex concepts through simplified explanations and analogies."""
    try:
        if not request.concept.strip():
            raise HTTPException(status_code=400, detail="Concept cannot be empty.")
            
        model = get_model()
        prompt = f"""
You are EduGenie's Concept Simplifier.
Explain the following topic for an audience of level: {request.target_audience}.

Topic / Concept:
{request.concept}

Format your response with:
1. 🎯 **Core Concept in Plain English** (1-2 sentences)
2. 💡 **Intuitive Real-World Analogy** (Relatable everyday comparison)
3. 🔍 **Step-by-Step Breakdown** (Simple key elements)
4. 🚀 **Why It Matters / Common Application**
5. ⚠️ **Common Misconception to Avoid**
"""
        response = model.generate_content(prompt)
        return {"success": True, "explanation": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining concept: {str(e)}")


@app.post("/api/quiz")
async def generate_quiz(request: QuizRequest):
    """Scenario 2: Generate quizzes from topics or text with interactive questions."""
    try:
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty.")
            
        model = get_model()
        num_q = max(1, min(request.num_questions or 4, 10))
        
        prompt = f"""
You are an expert educator creating an interactive multiple-choice quiz.
Topic/Passage: {request.topic}
Difficulty: {request.difficulty}
Number of Questions: {num_q}

Return ONLY a valid JSON array of objects. Do not include markdown formatting or backticks outside the JSON.
Each object must strictly follow this JSON schema:
[
  {{
    "id": 1,
    "question": "Clear and engaging question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "explanation": "Concise explanation of why this option is correct."
  }}
]
Ensure exactly 4 options per question and correct_index is an integer from 0 to 3.
"""
        response = model.generate_content(prompt)
        text_content = response.text.strip()
        
        # Strip potential markdown fences
        if text_content.startswith("```"):
            text_content = re.sub(r"^```(?:json)?", "", text_content)
            text_content = re.sub(r"```$", "", text_content).strip()
            
        quiz_data = json.loads(text_content)
        return {"success": True, "quiz": quiz_data, "topic": request.topic}
    except Exception as e:
        try:
            match = re.search(r"\[.*\]", response.text, re.DOTALL)
            if match:
                quiz_data = json.loads(match.group(0))
                return {"success": True, "quiz": quiz_data, "topic": request.topic}
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


@app.post("/api/learning-path")
async def generate_learning_path(request: LearningPathRequest):
    """Scenario 3: Structured learning plan with beginner to advanced topics, timelines, and suggestions."""
    try:
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty.")
            
        model = get_model()
        prompt = f"""
You are EduGenie's Curriculum Architect.
Generate a structured, personalized learning path for:
Topic: {request.topic}
Current Level: {request.current_level}
Target Goal: {request.target_goal}
Duration: {request.timeframe_weeks} Weeks

Return ONLY a valid JSON object. Do not include markdown codeblock tags around the output.
JSON Structure:
{{
  "title": "Mastery Plan for {request.topic}",
  "estimated_hours_per_week": 5,
  "difficulty": "{request.current_level} to Advanced",
  "overview": "Short motivational summary of what the learner will achieve.",
  "phases": [
    {{
      "phase_number": 1,
      "phase_name": "Foundations & Core Principles",
      "duration": "Week 1-2",
      "milestones": ["Milestone 1", "Milestone 2", "Milestone 3"],
      "recommended_resources": ["Free documentation/interactive site", "Project idea"],
      "practice_project": "Beginner hands-on mini project"
    }},
    {{
      "phase_number": 2,
      "phase_name": "Intermediate Application & Deep Dive",
      "duration": "Week 3-4",
      "milestones": ["Milestone 1", "Milestone 2"],
      "recommended_resources": ["Resource suggestion"],
      "practice_project": "Intermediate portfolio project"
    }},
    {{
      "phase_number": 3,
      "phase_name": "Advanced Mastery & Real-World Capstone",
      "duration": "Week 5-6",
      "milestones": ["Milestone 1", "Milestone 2"],
      "recommended_resources": ["Advanced guides / best practices"],
      "practice_project": "Comprehensive capstone project"
    }}
  ],
  "pro_tips": [
    "Tip 1 for accelerating learning",
    "Tip 2 for avoiding common pitfalls"
  ]
}}
"""
        response = model.generate_content(prompt)
        text_content = response.text.strip()
        
        if text_content.startswith("```"):
            text_content = re.sub(r"^```(?:json)?", "", text_content)
            text_content = re.sub(r"```$", "", text_content).strip()
            
        path_data = json.loads(text_content)
        return {"success": True, "learning_path": path_data}
    except Exception as e:
        try:
            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            if match:
                path_data = json.loads(match.group(0))
                return {"success": True, "learning_path": path_data}
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Error generating learning path: {str(e)}")


@app.post("/api/summarize")
async def summarize(request: SummaryRequest):
    """Summarize large educational passages."""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text to summarize cannot be empty.")
            
        model = get_model()
        
        format_instructions = {
            "bullet_points": "Provide a bulleted summary highlighting the core takeaways, followed by a 2-sentence TL;DR.",
            "executive": "Provide a clean, high-level educational abstract suitable for quick revision.",
            "flashcards": "Summarize key terms and definitions into high-yield Question & Answer revision cards."
        }.get(request.format, "Provide a clear, structured summary in simple language.")
        
        prompt = f"""
You are EduGenie's Study Notes Summarizer.
Instructions: {format_instructions}

Passage to Summarize:
{request.text}
"""
        response = model.generate_content(prompt)
        return {"success": True, "summary": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Summary: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)