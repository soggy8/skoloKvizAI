#!/usr/bin/env python3
"""
Simple Quiz Generator - Generate basic quiz questions from chapter content
Uses pattern matching instead of AI models for reliability
"""

import json
import re
import random
from typing import List, Dict

class SimpleQuizGenerator:
    def __init__(self):
        self.question_templates = [
            "Што е {concept}?",
            "Кои се карактеристиките на {concept}?",
            "Како функционира {concept}?",
            "Зошто е важно {concept}?",
            "Кога се користи {concept}?"
        ]
        
    def extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text using pattern matching"""
        concepts = []
        
        # Look for capitalized words (potential concepts)
        capitalized_words = re.findall(r'\b[А-Я][а-я]+\b', text)
        
        # Look for technical terms
        technical_terms = re.findall(r'\b(енергија|сила|брзина|забрзување|маса|волумен|притисок|температура|топлина|електрична|магнетна|осцилација|бранови|звук|светлина|атом|нуклеарна|физика)\b', text, re.IGNORECASE)
        
        # Look for definitions (words followed by "е" or "се")
        definitions = re.findall(r'\b([А-Я][а-я]+)\s+(?:е|се)\s+', text)
        
        # Combine and deduplicate
        all_concepts = capitalized_words + technical_terms + definitions
        concepts = list(set([c for c in all_concepts if len(c) > 3]))
        
        return concepts[:10]  # Limit to 10 concepts
    
    def generate_questions(self, chapter_content: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions from chapter content"""
        concepts = self.extract_key_concepts(chapter_content)
        
        if not concepts:
            return []
        
        questions = []
        
        for i in range(min(num_questions, len(concepts))):
            concept = random.choice(concepts)
            template = random.choice(self.question_templates)
            
            question = template.format(concept=concept)
            
            # Generate simple multiple choice options
            options, correct_index = self.generate_options(concept, concepts)
            
            questions.append({
                'question': question,
                'options': options,
                'correct_answer': correct_index  # Index of correct answer
            })
        
        return questions
    
    def generate_options(self, correct_concept: str, all_concepts: List[str]) -> tuple:
        """Generate multiple choice options and return options with correct answer index"""
        options = [f"Правилен одговор за {correct_concept}"]
        
        # Add 3 wrong options from other concepts
        wrong_concepts = [c for c in all_concepts if c != correct_concept]
        wrong_options = random.sample(wrong_concepts, min(3, len(wrong_concepts)))
        
        for concept in wrong_options:
            options.append(f"Погрешен одговор за {concept}")
        
        # Find correct answer index before shuffling
        correct_index = 0
        
        # Shuffle options
        random.shuffle(options)
        
        # Find new position of correct answer
        for i, option in enumerate(options):
            if correct_concept in option and "Правилен" in option:
                correct_index = i
                break
        
        return options, correct_index

def main():
    """Test the simple quiz generator"""
    print("Loading simple quiz generator...")
    generator = SimpleQuizGenerator()
    
    # Load clean chapters
    with open("labeled_chunks/clean_chapters_no_noise.json", "r", encoding="utf-8") as f:
        chapters = json.load(f)
    
    print(f"Found {len(chapters)} chapters")
    
    # Generate quiz for first chapter
    if chapters:
        chapter = chapters[0]
        print(f"\nGenerating quiz for Chapter {chapter['chapter_number']}: {chapter['title']}")
        
        questions = generator.generate_questions(chapter['content'], num_questions=3)
        
        print(f"\nGenerated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"\n{i}. {q['question']}")
            for j, option in enumerate(q['options']):
                letter = chr(65 + j)  # A, B, C, D
                print(f"   {letter}) {option}")
            print(f"   Точен одговор: {q['correct_answer']}")
        
        # Save quiz
        quiz_data = {
            "chapter_number": chapter['chapter_number'],
            "chapter_title": chapter['title'],
            "questions": questions
        }
        
        with open("sample_quiz.json", "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Quiz saved to sample_quiz.json")

if __name__ == "__main__":
    main()
