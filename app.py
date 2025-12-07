#!/usr/bin/env python3
"""
Simple Quiz App - Web interface for chapter selection and quiz taking
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from robust_quiz_generator import RobustQuizGenerator

app = Flask(__name__)

# Load chapters
def load_chapters():
    with open("labeled_chunks/clean_chapters_no_noise.json", "r", encoding="utf-8") as f:
        return json.load(f)

chapters = load_chapters()
quiz_generator = RobustQuizGenerator(use_openai=False)  # Use robust generator without OpenAI for now

@app.route('/')
def index():
    """Main page - show chapter list"""
    return render_template('index.html', chapters=chapters)

@app.route('/chapter/<int:chapter_num>')
def chapter_detail(chapter_num):
    """Show chapter details and generate quiz"""
    chapter = next((c for c in chapters if int(c['chapter_number']) == chapter_num), None)
    if not chapter:
        return "Chapter not found", 404
    
    # Generate quiz for this chapter
    questions = quiz_generator.generate_questions(chapter['content'], num_questions=5)
    
    return render_template('chapter.html', chapter=chapter, questions=questions)

@app.route('/api/quiz/<int:chapter_num>')
def get_quiz(chapter_num):
    """API endpoint to get quiz questions"""
    chapter = next((c for c in chapters if int(c['chapter_number']) == chapter_num), None)
    if not chapter:
        return jsonify({"error": "Chapter not found"}), 404
    
    questions = quiz_generator.generate_questions(chapter['content'], num_questions=5)
    
    return jsonify({
        "chapter_number": chapter['chapter_number'],
        "chapter_title": chapter['title'],
        "questions": questions
    })

@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    """API endpoint to check quiz answers"""
    data = request.json
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer')
    correct_answer = data.get('correct_answer')
    
    is_correct = selected_answer == correct_answer
    
    return jsonify({
        "is_correct": is_correct,
        "correct_answer": correct_answer
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

