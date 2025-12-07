#!/usr/bin/env python3
"""
AI Quiz Generator - Generate quiz questions using OpenAI API or fallback to simple generation
This version is more scalable and works with any book content
"""

import json
import random
import re
from typing import List, Dict
import requests
import os

class AIQuizGenerator:
    def __init__(self, use_openai=True, openai_api_key=None):
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Fallback question templates for different subjects
        self.question_templates = {
            'general': [
                "Што е {concept}?",
                "Кои се карактеристиките на {concept}?",
                "Како функционира {concept}?",
                "Зошто е важно {concept}?",
                "Кога се користи {concept}?",
                "Каков е ефектот на {concept}?",
                "Што предизвикува {concept}?",
                "Како се мери {concept}?"
            ],
            'physics': [
                "Што е {concept} во физиката?",
                "Како се пресметува {concept}?",
                "Кои се единиците за {concept}?",
                "Каков е принципот на {concept}?",
                "Што влијае на {concept}?",
                "Како се применува {concept}?"
            ],
            'biology': [
                "Што е {concept} во биологијата?",
                "Каде се наоѓа {concept}?",
                "Како функционира {concept}?",
                "Зошто е важен {concept}?",
                "Што се случува ако недостасува {concept}?"
            ],
            'chemistry': [
                "Што е {concept} во хемијата?",
                "Како се формира {concept}?",
                "Кои се својствата на {concept}?",
                "Што се случува кога {concept} реагира?",
                "Каде се користи {concept}?"
            ]
        }
    
    def detect_subject(self, text: str) -> str:
        """Detect the subject of the text based on keywords"""
        text_lower = text.lower()
        
        physics_keywords = ['физика', 'енергија', 'сила', 'брзина', 'забрзување', 'маса', 'волумен', 'притисок', 'температура', 'топлина', 'електрична', 'магнетна', 'осцилација', 'бранови']
        biology_keywords = ['биологија', 'ќелија', 'организам', 'орган', 'тканина', 'систем', 'метаболизам', 'ДНК', 'протеин', 'ензим']
        chemistry_keywords = ['хемија', 'атом', 'молекула', 'соединение', 'реакција', 'елемент', 'период', 'оксидација', 'редукција']
        
        physics_score = sum(1 for keyword in physics_keywords if keyword in text_lower)
        biology_score = sum(1 for keyword in biology_keywords if keyword in text_lower)
        chemistry_score = sum(1 for keyword in chemistry_keywords if keyword in text_lower)
        
        if physics_score >= biology_score and physics_score >= chemistry_score:
            return 'physics'
        elif biology_score >= chemistry_score:
            return 'biology'
        elif chemistry_score > 0:
            return 'chemistry'
        else:
            return 'general'
    
    def extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text using improved pattern matching"""
        concepts = []
        
        # Look for capitalized words (potential concepts)
        capitalized_words = re.findall(r'\b[А-Я][а-я]+\b', text)
        
        # Look for technical terms (more comprehensive)
        technical_terms = re.findall(r'\b(енергија|сила|брзина|забрзување|маса|волумен|притисок|температура|топлина|електрична|магнетна|осцилација|бранови|звук|светлина|атом|нуклеарна|физика|ќелија|организам|орган|тканина|систем|метаболизам|ДНК|протеин|ензим|хемија|молекула|соединение|реакција|елемент|период|оксидација|редукција|концепт|принцип|закон|теорија|модел|процес|механизам|функција|структура|својство|карактеристика|ефект|резултат|причина|последица)\b', text, re.IGNORECASE)
        
        # Look for definitions (words followed by "е" or "се")
        definitions = re.findall(r'\b([А-Я][а-я]+)\s+(?:е|се)\s+', text)
        
        # Look for important phrases in quotes or after colons
        quoted_concepts = re.findall(r'["""]([^"""]+)["""]', text)
        colon_concepts = re.findall(r':\s*([А-Я][а-я]+)', text)
        
        # Combine and deduplicate
        all_concepts = capitalized_words + technical_terms + definitions + quoted_concepts + colon_concepts
        concepts = list(set([c.strip() for c in all_concepts if len(c.strip()) > 3 and len(c.strip()) < 50]))
        
        return concepts[:15]  # Limit to 15 concepts
    
    def generate_with_openai(self, chapter_content: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions using OpenAI API"""
        if not self.openai_api_key:
            print("OpenAI API key not found, falling back to simple generation")
            return self.generate_simple(chapter_content, num_questions)
        
        content = chapter_content[:3000]  # Limit content length
        
        prompt = f"""
Генерирај {num_questions} прашања за квиз од следниот текст на македонски јазик.
За секое прашање дај 4 можни одговори (A, B, C, D) и означи го точниот одговор.

Текст: {content}

Формат:
Прашање 1: [прашање]
A) [одговор 1]
B) [одговор 2] 
C) [одговор 3]
D) [одговор 4]
Точен одговор: [A/B/C/D]

Прашање 2: [прашање]
...
"""

        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                return self.parse_questions(result)
            else:
                print(f"OpenAI API error: {response.status_code}")
                return self.generate_simple(chapter_content, num_questions)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self.generate_simple(chapter_content, num_questions)
    
    def generate_simple(self, chapter_content: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions using improved pattern matching"""
        concepts = self.extract_key_concepts(chapter_content)
        subject = self.detect_subject(chapter_content)
        
        if not concepts:
            return []
        
        templates = self.question_templates.get(subject, self.question_templates['general'])
        questions = []
        
        for i in range(min(num_questions, len(concepts))):
            concept = random.choice(concepts)
            template = random.choice(templates)
            
            question = template.format(concept=concept)
            
            # Generate multiple choice options
            options, correct_index = self.generate_options(concept, concepts, subject)
            
            questions.append({
                'question': question,
                'options': options,
                'correct_answer': correct_index  # Index of correct answer
            })
        
        return questions
    
    def generate_options(self, correct_concept: str, all_concepts: List[str], subject: str) -> tuple:
        """Generate multiple choice options with better distractors"""
        # Create a more realistic correct answer
        correct_answer = f"Точно - {correct_concept} е важен концепт во {subject}"
        
        # Generate better wrong options
        wrong_concepts = [c for c in all_concepts if c != correct_concept]
        wrong_options = []
        
        # Add 3 wrong options with different types of errors
        if len(wrong_concepts) >= 3:
            wrong_options = [
                f"Погрешно - {wrong_concepts[0]} не е поврзан со ова прашање",
                f"Не точно - {wrong_concepts[1] if len(wrong_concepts) > 1 else 'овој концепт'} е различен",
                f"Неточно - {wrong_concepts[2] if len(wrong_concepts) > 2 else 'оваа опција'} не одговара"
            ]
        else:
            # Fallback generic wrong answers
            wrong_options = [
                "Ова не е точен одговор",
                "Оваа опција е погрешна", 
                "Неточно"
            ]
        
        options = [correct_answer] + wrong_options
        
        # Shuffle options
        random.shuffle(options)
        
        # Find correct answer index
        correct_index = options.index(correct_answer)
        
        return options, correct_index
    
    def parse_questions(self, generated_text: str) -> List[Dict]:
        """Parse generated text into structured questions"""
        questions = []
        
        # Split by question markers
        question_blocks = generated_text.split("Прашање")
        
        for block in question_blocks[1:]:  # Skip first empty block
            if not block.strip():
                continue
                
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            
            if len(lines) < 6:  # Need question + 4 options + answer
                continue
                
            try:
                # Extract question
                question = lines[0].replace(':', '').strip()
                
                # Extract options
                options = []
                correct_answer = None
                
                for line in lines[1:]:
                    if line.startswith('A)') or line.startswith('B)') or line.startswith('C)') or line.startswith('D)'):
                        options.append(line[2:].strip())
                    elif line.startswith('Точен одговор:'):
                        correct_answer = line.split(':')[1].strip()
                
                if len(options) == 4 and correct_answer:
                    # Convert letter to index
                    letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                    correct_index = letter_to_index.get(correct_answer, 0)
                    
                    questions.append({
                        'question': question,
                        'options': options,
                        'correct_answer': correct_index
                    })
                    
            except Exception as e:
                print(f"Error parsing question block: {e}")
                continue
        
        return questions
    
    def generate_questions(self, chapter_content: str, num_questions: int = 5) -> List[Dict]:
        """Main method to generate quiz questions"""
        if self.use_openai and self.openai_api_key:
            return self.generate_with_openai(chapter_content, num_questions)
        else:
            return self.generate_simple(chapter_content, num_questions)

def main():
    """Test the AI quiz generator"""
    print("Loading AI quiz generator...")
    generator = AIQuizGenerator(use_openai=False)  # Test with simple generation first
    
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
            print(f"   Точен одговор: {chr(65 + q['correct_answer'])} (index: {q['correct_answer']})")
        
        # Save quiz
        quiz_data = {
            "chapter_number": chapter['chapter_number'],
            "chapter_title": chapter['title'],
            "questions": questions
        }
        
        with open("sample_ai_quiz.json", "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ AI Quiz saved to sample_ai_quiz.json")

if __name__ == "__main__":
    main()
