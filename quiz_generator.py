#!/usr/bin/env python3
"""
Quiz Generator - Generate quiz questions from chapter content
"""

import json
import random
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class QuizGenerator:
    def __init__(self, model_name="google/mt5-small"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        
    def generate_quiz_questions(self, chapter_content, num_questions=5):
        """Generate quiz questions from chapter content"""
        
        # Clean content for better generation
        content = chapter_content[:2000]  # Limit content length
        
        # Create prompt for quiz generation
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
        
        # Generate questions
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=2048, truncation=True).to(self.device)
        
        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=800,
                do_sample=True,
                temperature=0.7,
                num_beams=4
            )
        
        result = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        # Parse the generated questions
        questions = self.parse_questions(result)
        
        return questions
    
    def parse_questions(self, generated_text):
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
                    questions.append({
                        'question': question,
                        'options': options,
                        'correct_answer': correct_answer
                    })
                    
            except Exception as e:
                print(f"Error parsing question block: {e}")
                continue
        
        return questions

def main():
    """Test the quiz generator"""
    print("Loading quiz generator...")
    generator = QuizGenerator()
    
    # Load clean chapters
    with open("labeled_chunks/clean_chapters_no_noise.json", "r", encoding="utf-8") as f:
        chapters = json.load(f)
    
    print(f"Found {len(chapters)} chapters")
    
    # Generate quiz for first chapter
    if chapters:
        chapter = chapters[0]
        print(f"\nGenerating quiz for Chapter {chapter['chapter_number']}: {chapter['title']}")
        
        questions = generator.generate_quiz_questions(chapter['content'], num_questions=3)
        
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
        
        with open("sample_quiz2.json", "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Quiz saved to sample_quiz.json")

if __name__ == "__main__":
    main()

