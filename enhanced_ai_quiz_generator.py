#!/usr/bin/env python3
"""
Enhanced AI Quiz Generator - Creates high-quality quiz questions from any text content
This version focuses on generating meaningful, educational questions with realistic answer options
"""

import json
import random
import re
from typing import List, Dict, Tuple
import requests
import os

class EnhancedAIQuizGenerator:
    def __init__(self, use_openai=True, openai_api_key=None):
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Advanced question templates that create meaningful questions
        self.question_templates = {
            'definition': [
                "Што е {concept}?",
                "Како се дефинира {concept}?",
                "Што се подразбира под {concept}?",
                "Која е дефиницијата за {concept}?"
            ],
            'characteristics': [
                "Кои се карактеристиките на {concept}?",
                "Што се својствата на {concept}?",
                "Какви се особините на {concept}?",
                "Кои се главните карактеристики на {concept}?"
            ],
            'function': [
                "Како функционира {concept}?",
                "Како работи {concept}?",
                "Што е функцијата на {concept}?",
                "Како се користи {concept}?"
            ],
            'calculation': [
                "Како се пресметува {concept}?",
                "Која е формулата за {concept}?",
                "Како се изразува {concept} математички?",
                "Што е равенката за {concept}?"
            ],
            'importance': [
                "Зошто е важно {concept}?",
                "Што е значењето на {concept}?",
                "Зошто се изучува {concept}?",
                "Какво е практичното значење на {concept}?"
            ],
            'relationship': [
                "Како е поврзано {concept1} со {concept2}?",
                "Што е односот помеѓу {concept1} и {concept2}?",
                "Како влијае {concept1} на {concept2}?",
                "Што е врската меѓу {concept1} и {concept2}?"
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text to remove OCR artifacts and noise"""
        # Remove excessive whitespace and line breaks
        text = re.sub(r'\s+', ' ', text)
        
        # Remove OCR artifacts (repeated characters, numbers that don't make sense)
        text = re.sub(r'([а-я])\1{3,}', r'\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d{1,2}\.\d{1,2}\.\d{1,2}\b', '', text)  # Remove page numbers
        
        # Remove standalone numbers that are likely OCR errors
        text = re.sub(r'\b\d+\b(?=\s*[а-я])', '', text, flags=re.IGNORECASE)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '.', text)
        text = re.sub(r'[,]{2,}', ',', text)
        
        # Clean up common OCR errors
        ocr_replacements = {
            'ннинанинанана': '',
            'нининининини': '',
            'ннина': '',
            'нина': '',
            'ни': '',
            'а!': '',
            'чн': '',
            'нининеинининниннининнанини': '',
            'нинииниининининниненнанаи': '',
            'нинаа кана': '',
            'нини': '',
            'ниа': '',
            'нина нана': '',
            'нина нана': '',
            'нина': '',
            'ни': ''
        }
        
        for error, replacement in ocr_replacements.items():
            text = text.replace(error, replacement)
        
        return text.strip()
    
    def extract_meaningful_concepts(self, text: str) -> List[Dict]:
        """Extract meaningful concepts with context from cleaned text"""
        concepts = []
        
        # Look for definitions (X е/се Y pattern)
        definitions = re.findall(r'\b([А-Я][а-я]{2,20})\s+(?:е|се)\s+([^.!?]{10,100})', text)
        for concept, definition in definitions:
            if len(concept) > 3 and len(definition.strip()) > 10:
                concepts.append({
                    'term': concept,
                    'type': 'definition',
                    'context': definition.strip(),
                    'confidence': 0.9
                })
        
        # Look for important concepts mentioned multiple times
        important_terms = re.findall(r'\b([А-Я][а-я]{3,15})\b', text)
        term_counts = {}
        for term in important_terms:
            if len(term) > 3 and term not in ['ТЕКСТ', 'СТРАНИЦА', 'ПОГЛАВЈЕ']:
                term_counts[term] = term_counts.get(term, 0) + 1
        
        # Add frequently mentioned terms
        for term, count in term_counts.items():
            if count >= 2:  # Mentioned at least twice
                concepts.append({
                    'term': term,
                    'type': 'frequent',
                    'context': f'Се споменува {count} пати во текстот',
                    'confidence': 0.7
                })
        
        # Look for technical terms with explanations
        technical_patterns = [
            r'([А-Я][а-я]+)\s+се\s+(?:дефинира|означува|нарекува|вика)\s+како\s+([^.!?]{10,80})',
            r'([А-Я][а-я]+)\s+е\s+([^.!?]{10,80})',
            r'([А-Я][а-я]+)\s+представува\s+([^.!?]{10,80})'
        ]
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            for concept, explanation in matches:
                if len(concept) > 3 and len(explanation.strip()) > 10:
                    concepts.append({
                        'term': concept,
                        'type': 'technical',
                        'context': explanation.strip(),
                        'confidence': 0.8
                    })
        
        # Remove duplicates and sort by confidence
        unique_concepts = {}
        for concept in concepts:
            term = concept['term']
            if term not in unique_concepts or concept['confidence'] > unique_concepts[term]['confidence']:
                unique_concepts[term] = concept
        
        return sorted(unique_concepts.values(), key=lambda x: x['confidence'], reverse=True)[:10]
    
    def generate_with_openai(self, chapter_content: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions using OpenAI API with better prompting"""
        if not self.openai_api_key:
            print("OpenAI API key not found, falling back to enhanced simple generation")
            return self.generate_enhanced_simple(chapter_content, num_questions)
        
        content = self.clean_text(chapter_content)[:4000]  # Clean and limit content
        
        prompt = f"""
Ти си професор по физика кој создава квиз прашања за студенти. Од следниот текст генерирај {num_questions} висококвалитетни прашања за квиз на македонски јазик.

ВАЖНО:
- Прашањата треба да тестираат разбирање, не само меморија
- Одговорите треба да бидат реални и логични
- Погрешните одговори треба да бидат веродостојни (не очевидно погрешни)
- Секое прашање треба да има точно 4 одговори (A, B, C, D)
- Точниот одговор треба да биде јасно означен

Текст: {content}

Формат за секое прашање:
Прашање X: [смислено прашање кое тестира разбирање]
A) [реален одговор]
B) [реален одговор]
C) [реален одговор]
D) [реален одговор]
Точен одговор: [A/B/C/D]
"""

        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'Ти си професор по физика кој создава квиз прашања. Секој одговор треба да биде реална опција, не очевидно погрешна.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1500,
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
                return self.generate_enhanced_simple(chapter_content, num_questions)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self.generate_enhanced_simple(chapter_content, num_questions)
    
    def generate_enhanced_simple(self, chapter_content: str, num_questions: int = 5) -> List[Dict]:
        """Generate high-quality questions using enhanced pattern matching"""
        cleaned_text = self.clean_text(chapter_content)
        concepts = self.extract_meaningful_concepts(cleaned_text)
        
        if not concepts:
            return []
        
        questions = []
        used_concepts = set()
        
        for i in range(min(num_questions, len(concepts))):
            # Select a concept that hasn't been used
            available_concepts = [c for c in concepts if c['term'] not in used_concepts]
            if not available_concepts:
                break
                
            concept = random.choice(available_concepts)
            used_concepts.add(concept['term'])
            
            # Choose question type based on concept type
            if concept['type'] == 'definition':
                template = random.choice(self.question_templates['definition'])
                question = template.format(concept=concept['term'])
                options, correct_index = self.generate_definition_options(concept, concepts)
            elif concept['type'] == 'technical':
                template = random.choice(self.question_templates['function'])
                question = template.format(concept=concept['term'])
                options, correct_index = self.generate_function_options(concept, concepts)
            else:
                template = random.choice(self.question_templates['characteristics'])
                question = template.format(concept=concept['term'])
                options, correct_index = self.generate_characteristic_options(concept, concepts)
            
            questions.append({
                'question': question,
                'options': options,
                'correct_answer': correct_index
            })
        
        return questions
    
    def generate_definition_options(self, concept: Dict, all_concepts: List[Dict]) -> Tuple[List[str], int]:
        """Generate realistic options for definition questions"""
        correct_answer = concept['context'][:100] + "..." if len(concept['context']) > 100 else concept['context']
        
        # Generate plausible wrong answers
        wrong_options = []
        other_concepts = [c for c in all_concepts if c['term'] != concept['term']]
        
        if len(other_concepts) >= 3:
            for other_concept in other_concepts[:3]:
                if other_concept.get('context'):
                    wrong_answer = other_concept['context'][:100] + "..." if len(other_concept['context']) > 100 else other_concept['context']
                    wrong_options.append(wrong_answer)
        
        # Fill with generic wrong answers if needed
        while len(wrong_options) < 3:
            generic_wrong = [
                "Тоа е погрешен одговор за овој концепт",
                "Ова не одговара на дефиницијата",
                "Ова не е точна карактеристика"
            ][len(wrong_options)]
            wrong_options.append(generic_wrong)
        
        options = [correct_answer] + wrong_options
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return options, correct_index
    
    def generate_function_options(self, concept: Dict, all_concepts: List[Dict]) -> Tuple[List[str], int]:
        """Generate realistic options for function/mechanism questions"""
        # Create a more specific correct answer based on context
        context = concept.get('context', '')
        if 'функционира' in context.lower() or 'работи' in context.lower():
            correct_answer = context[:120] + "..." if len(context) > 120 else context
        else:
            correct_answer = f"{concept['term']} функционира според принципите опишани во текстот"
        
        # Generate realistic wrong answers
        wrong_options = [
            f"{concept['term']} функционира на спротивен начин од опишаниот",
            f"{concept['term']} не функционира како што е опишано",
            f"{concept['term']} функционира независно од основните принципи"
        ]
        
        options = [correct_answer] + wrong_options
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return options, correct_index
    
    def generate_characteristic_options(self, concept: Dict, all_concepts: List[Dict]) -> Tuple[List[str], int]:
        """Generate realistic options for characteristic questions"""
        context = concept.get('context', '')
        correct_answer = f"Главните карактеристики на {concept['term']} се опишани во текстот"
        
        # Generate realistic wrong answers
        wrong_options = [
            f"{concept['term']} нема специфични карактеристики",
            f"Карактеристиките на {concept['term']} се непознати",
            f"{concept['term']} има карактеристики различни од опишаните"
        ]
        
        options = [correct_answer] + wrong_options
        random.shuffle(options)
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
            return self.generate_enhanced_simple(chapter_content, num_questions)

def main():
    """Test the enhanced AI quiz generator"""
    print("Loading Enhanced AI quiz generator...")
    generator = EnhancedAIQuizGenerator(use_openai=False)  # Test with enhanced simple generation first
    
    # Load clean chapters
    with open("labeled_chunks/clean_chapters_no_noise.json", "r", encoding="utf-8") as f:
        chapters = json.load(f)
    
    print(f"Found {len(chapters)} chapters")
    
    # Generate quiz for first chapter
    if chapters:
        chapter = chapters[0]
        print(f"\nGenerating quiz for Chapter {chapter['chapter_number']}: {chapter['title']}")
        print(f"Original content length: {len(chapter['content'])}")
        
        questions = generator.generate_questions(chapter['content'], num_questions=3)
        
        print(f"\nGenerated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"\n{i}. {q['question']}")
            for j, option in enumerate(q['options']):
                letter = chr(65 + j)  # A, B, C, D
                marker = "✓" if j == q['correct_answer'] else " "
                print(f"   {letter}) [{marker}] {option}")
        
        # Save quiz
        quiz_data = {
            "chapter_number": chapter['chapter_number'],
            "chapter_title": chapter['title'],
            "questions": questions
        }
        
        with open("sample_enhanced_quiz.json", "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Enhanced Quiz saved to sample_enhanced_quiz.json")

if __name__ == "__main__":
    main()
