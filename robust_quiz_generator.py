#!/usr/bin/env python3
"""
Robust Quiz Generator - Creates high-quality quiz questions even from poor OCR text
This version is specifically designed to handle fragmented, noisy text content
"""

import json
import random
import re
from typing import List, Dict, Tuple
import requests
import os

class RobustQuizGenerator:
    def __init__(self, use_openai=True, openai_api_key=None):
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Physics-specific question templates
        self.question_templates = [
            "Што е {concept}?",
            "Како се дефинира {concept}?",
            "Кои се карактеристиките на {concept}?",
            "Како функционира {concept}?",
            "Зошто е важен {concept}?",
            "Каде се користи {concept}?",
            "Каков е принципот на {concept}?",
            "Што предизвикува {concept}?",
            "Како се мери {concept}?",
            "Кои се единиците за {concept}?"
        ]
        
        # Physics concepts and their typical properties/definitions
        self.physics_knowledge = {
            'енергија': {
                'definition': 'Способност за вршење работа',
                'characteristics': ['Се зачувува', 'Се трансформира', 'Има различни видови'],
                'units': ['Јули (J)', 'Калории', 'Електронволти']
            },
            'сила': {
                'definition': 'Влијание што го менува движењето на телото',
                'characteristics': ['Има големина и насока', 'Се мери во Њутни', 'Може да забрзува'],
                'units': ['Њутн (N)', 'Килограм-сила']
            },
            'брзина': {
                'definition': 'Промена на положбата во време',
                'characteristics': ['Има големина и насока', 'Се мери во m/s', 'Може да се менува'],
                'units': ['m/s', 'km/h', 'km/s']
            },
            'забрзување': {
                'definition': 'Промена на брзината во време',
                'characteristics': ['Се мери во m/s²', 'Може да биде позитивно или негативно', 'Зависи од силата'],
                'units': ['m/s²', 'g (гравитациско забрзување)']
            },
            'маса': {
                'definition': 'Количество материја во тело',
                'characteristics': ['Се мери во килограми', 'Не се менува', 'Определува инерција'],
                'units': ['кг (kg)', 'грам (g)', 'тон']
            },
            'притисок': {
                'definition': 'Сила по единица површина',
                'characteristics': ['Се мери во Паскали', 'Се пренесува во течности', 'Зависи од длабочината'],
                'units': ['Па (Pa)', 'атмосфера', 'бар']
            },
            'температура': {
                'definition': 'Мера за топлинската енергија',
                'characteristics': ['Се мери во Целзиусови или Келвинови степени', 'Определува насока на топлинска размена'],
                'units': ['°C', '°F', 'K (Келвин)']
            },
            'топлина': {
                'definition': 'Енергија што се пренесува поради температурна разлика',
                'characteristics': ['Се пренесува од топло кон ладно', 'Се мери во Јули', 'Може да промени температура'],
                'units': ['Ј (J)', 'калории', 'kWh']
            },
            'електрична': {
                'definition': 'Сврпзана со електрични полнежи',
                'characteristics': ['Има позитивен и негативен полнеж', 'Се привлекуваат спротивните', 'Се одбиваат истите'],
                'units': ['Кулон (C)', 'Ампер (A)', 'Волт (V)']
            },
            'магнетна': {
                'definition': 'Сврпзана со магнетни полиња',
                'characteristics': ['Има северен и јужен пол', 'Се привлекуваат спротивните', 'Влијае на движечки полнежи'],
                'units': ['Тесла (T)', 'Гаус', 'Вебер (Wb)']
            },
            'осцилација': {
                'definition': 'Периодично движење околу рамнотежна положба',
                'characteristics': ['Има период и фреквенција', 'Се повторува', 'Може да биде задушена'],
                'units': ['Херц (Hz)', 'радијан/секунда']
            },
            'бранови': {
                'definition': 'Пренос на енергија без пренос на материја',
                'characteristics': ['Има бранова должина', 'Има фреквенција', 'Може да се рефлектира'],
                'units': ['метри (м)', 'Херц (Hz)', 'm/s']
            },
            'атом': {
                'definition': 'Најмала единица на елемент',
                'characteristics': ['Се состои од јадро и електрони', 'Има атомска маса', 'Може да се јонизира'],
                'units': ['атомска маса единица', 'метри']
            }
        }
    
    def clean_and_extract_concepts(self, text: str) -> List[str]:
        """Extract physics concepts from even very noisy text"""
        # Clean the text first
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[ннина]+', '', text)
        text = re.sub(r'\d+\.\d+\.\d+', '', text)  # Remove section numbers
        
        # Extract physics terms (case insensitive)
        concepts = []
        
        # Look for known physics terms
        for term in self.physics_knowledge.keys():
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                concepts.append(term.title())
        
        # Look for capitalized terms that might be physics concepts
        capitalized_terms = re.findall(r'\b[А-Я][а-я]{3,15}\b', text)
        for term in capitalized_terms:
            if term not in concepts and len(term) > 3:
                concepts.append(term)
        
        # Remove duplicates and common non-physics words
        concepts = list(set(concepts))
        exclude_words = {'ТЕКСТ', 'СТРАНИЦА', 'ПОГЛАВЈЕ', 'СЛИКА', 'ТАБЕЛА', 'ПРИМЕР', 'ЗАДАЧА'}
        concepts = [c for c in concepts if c not in exclude_words]
        
        return concepts[:8]  # Limit to 8 concepts
    
    def generate_realistic_options(self, concept: str, all_concepts: List[str]) -> Tuple[List[str], int]:
        """Generate realistic multiple choice options"""
        concept_lower = concept.lower()
        
        # Get knowledge about this concept if available
        if concept_lower in self.physics_knowledge:
            knowledge = self.physics_knowledge[concept_lower]
            correct_answer = knowledge['definition']
            
            # Create realistic wrong answers from other concepts
            wrong_options = []
            other_concepts = [c for c in all_concepts if c.lower() != concept_lower]
            
            for other_concept in other_concepts[:2]:
                if other_concept.lower() in self.physics_knowledge:
                    wrong_options.append(self.physics_knowledge[other_concept.lower()]['definition'])
            
            # Fill with generic physics wrong answers
            generic_wrong = [
                f"Ова не е точна дефиниција за {concept}",
                f"{concept} се дефинира поинаку",
                f"Ова не одговара на {concept}"
            ]
            wrong_options.extend(generic_wrong)
            
        else:
            # Fallback for unknown concepts
            correct_answer = f"{concept} е важен концепт во физиката"
            wrong_options = [
                f"{concept} не е физички концепт",
                f"{concept} се користи во други науки",
                f"{concept} нема физичко значење"
            ]
        
        # Ensure we have exactly 4 options
        options = [correct_answer] + wrong_options[:3]
        
        # Shuffle and find correct index
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        
        return options, correct_index
    
    def generate_with_openai(self, chapter_content: str, num_questions: int = 5) -> List[Dict]:
        """Generate quiz questions using OpenAI API"""
        if not self.openai_api_key:
            return self.generate_simple(chapter_content, num_questions)
        
        # Clean the content
        content = re.sub(r'\s+', ' ', chapter_content)
        content = re.sub(r'[ннина]+', '', content)
        content = content[:3000]  # Limit content length
        
        prompt = f"""
Од следниот текст (кој може да содржи OCR грешки) генерирај {num_questions} добри прашања за квиз по физика на македонски јазик.

ВАЖНО:
- Прашањата треба да бидат разбирливи и да тестираат знаење
- Секој одговор треба да биде реална опција
- Погрешните одговори треба да бидат веродостојни
- Секое прашање треба да има точно 4 одговори (A, B, C, D)

Текст: {content}

Формат:
Прашање 1: [прашање]
A) [одговор]
B) [одговор]
C) [одговор]
D) [одговор]
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
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1200,
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
        """Generate quiz questions using robust pattern matching"""
        concepts = self.clean_and_extract_concepts(chapter_content)
        
        if not concepts:
            # Fallback: create generic physics questions
            concepts = ['Енергија', 'Сила', 'Брзина', 'Притисок']
        
        questions = []
        
        for i in range(min(num_questions, len(concepts))):
            concept = concepts[i]
            template = random.choice(self.question_templates)
            question = template.format(concept=concept)
            
            # Generate realistic options
            options, correct_index = self.generate_realistic_options(concept, concepts)
            
            questions.append({
                'question': question,
                'options': options,
                'correct_answer': correct_index
            })
        
        return questions
    
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
    """Test the robust quiz generator"""
    print("Loading Robust Quiz Generator...")
    generator = RobustQuizGenerator(use_openai=False)
    
    # Load clean chapters
    with open("labeled_chunks/clean_chapters_no_noise.json", "r", encoding="utf-8") as f:
        chapters = json.load(f)
    
    print(f"Found {len(chapters)} chapters")
    
    # Generate quiz for first chapter
    if chapters:
        chapter = chapters[0]
        print(f"\nGenerating quiz for Chapter {chapter['chapter_number']}: {chapter['title']}")
        print(f"Original content length: {len(chapter['content'])}")
        
        # Extract concepts first
        concepts = generator.clean_and_extract_concepts(chapter['content'])
        print(f"Extracted concepts: {concepts}")
        
        questions = generator.generate_questions(chapter['content'], num_questions=5)
        
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
        
        with open("sample_robust_quiz.json", "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Robust Quiz saved to sample_robust_quiz.json")

if __name__ == "__main__":
    main()
