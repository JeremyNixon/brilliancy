from flask import render_template, request, redirect, url_for, flash
from passlib.hash import sha256_crypt
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

import openai
from openai import OpenAI
client = OpenAI(api_key =open('OPENAI_API_KEY.txt').read().strip())


def generate(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a quantitative judge that outputs a single number."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return completion.choices[0].message.content.strip('*').strip('#')

from flask import jsonify
import time
from datetime import datetime

@app.route("/judge", methods=['POST'])
def judge_idea():
    """
    Route to judge submitted ideas in the Brilliancy game.
    Expects JSON with: {
        "idea": "user's creative idea",
        "topic": "current game topic",
        "game_id": "unique identifier for game session"
    }
    Returns: {
        "score": float,
        "message": str,
        "timestamp": str,
        "status": str
    }
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["idea", "topic"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    idea = data["idea"]
    topic = data["topic"]
    
    # Construct prompt for the LLM judge
    prompt = f"""
    As a judge of creative ideas, evaluate the following idea on a scale of 1-100.
    
    Topic: {topic}
    Idea: {idea}
    
    Consider the following criteria:
    1. Originality (uniqueness and novelty)
    2. Relevance to the topic
    3. Potential impact or usefulness
    4. Cleverness of the solution
    5. Feasibility of implementation
    
    Output only a single number between 1 and 100, where:
    1-20: Poor - Obvious or commonplace ideas
    21-40: Below Average - Slightly original but lacking depth
    41-60: Average - Decent ideas with some creative elements
    61-80: Good - Original and well-thought-out ideas
    81-100: Excellent - Highly innovative and impactful ideas
    """
    
    try:
        # Get score from LLM
        raw_score = generate(prompt)
        
        # Convert score to float and validate
        try:
            score = float(raw_score)
            if not 1 <= score <= 100:
                score = max(1, min(100, score))  # Clamp between 1 and 100
        except ValueError:
            return jsonify({
                "error": "Invalid score generated",
                "status": "error"
            }), 500
        
        # Prepare response
        response = {
            "score": score,
            "message": get_score_message(score),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "error": "Error processing idea",
            "status": "error",
            "details": str(e)
        }), 500

def get_score_message(score):
    """Return encouraging message based on score range"""
    if score >= 81:
        return "Brilliant! This is an exceptional idea!"
    elif score >= 61:
        return "Great thinking! You're on the right track!"
    elif score >= 41:
        return "Good start! Keep pushing the boundaries!"
    elif score >= 21:
        return "You're making progress. Try thinking more outside the box!"
    else:
        return "Keep brainstorming! Every idea brings you closer to brilliance!"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("index.html")
