# skoloKvizAI 📚🤖

> ⚠️ **Work in Progress**: This project is currently under development and not yet complete. Some features may be incomplete or experimental.

AI-powered quiz generator for educational content in Macedonian. Automatically creates intelligent, multiple-choice quiz questions from textbook chapters using advanced text processing and optional OpenAI integration.

## Project Status

This is an active development project exploring AI-powered educational tools for Macedonian-language learning materials. The codebase includes multiple experimental approaches to quiz generation and text processing. Expect incomplete features, experimental code, and ongoing refactoring.

## Features

- 🧠 **AI-Powered Question Generation**: Creates meaningful quiz questions that test comprehension, not just memorization
- 📖 **PDF Processing**: Extracts and processes text from PDF textbooks using OCR
- 🌐 **Web Interface**: Flask-based web app for browsing chapters and taking quizzes
- 🔄 **Multiple Generation Methods**: Supports both OpenAI API and local rule-based generation
- 🇲🇰 **Macedonian Language Support**: Full support for Cyrillic script and Macedonian language
- ✨ **Smart Answer Generation**: Creates realistic distractors (wrong answers) that are plausible
- 🧹 **OCR Cleanup**: Advanced text cleaning to remove OCR artifacts and noise

## Components

### Quiz Generators

- **`enhanced_ai_quiz_generator.py`**: Advanced AI-powered question generation with OpenAI integration
- **`robust_quiz_generator.py`**: Fallback generator with local processing
- **`ai_quiz_generator.py`**: Hybrid approach combining AI and rule-based methods
- **`simple_quiz_generator.py`**: Basic rule-based question generation

### Text Processing

- **`textOCR.py`** / **`textEasyOCR.py`**: OCR implementations for PDF text extraction
- **`latinToCyrillic.py`**: Script conversion utilities
- **`tocContentExtract.py`**: Table of contents extraction
- **`chapters.py`** / **`chaptersAI.py`**: Chapter segmentation and processing

### Web Application

- **`app.py`**: Flask web server with quiz interface
- **`templates/`**: HTML templates for web interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/skoloKvizAI.git
cd skoloKvizAI
```

2. Install dependencies:
```bash
pip install flask easyocr pdf2image pytesseract openai
```

3. (Optional) Set up OpenAI API key for enhanced generation:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Web Interface

Start the Flask web server:
```bash
python app.py
```

Then open your browser to `http://localhost:5000` to browse chapters and take quizzes.

### Programmatic Usage

Generate quiz questions from text:

```python
from enhanced_ai_quiz_generator import EnhancedAIQuizGenerator

generator = EnhancedAIQuizGenerator(use_openai=True)
questions = generator.generate_questions(chapter_text, num_questions=5)
```

### Process PDF Textbook

Extract text and chapters from a PDF:

```python
from textOCR import extract_text_from_pdf
from chaptersAI import process_chapters

# Extract text
text = extract_text_from_pdf('textbook.pdf')

# Process into chapters
chapters = process_chapters(text)
```

## Project Structure

```
skoloKvizAI/
├── app.py                          # Flask web application
├── enhanced_ai_quiz_generator.py   # Main quiz generation engine
├── robust_quiz_generator.py        # Fallback generator
├── textOCR.py                      # OCR processing
├── chaptersAI.py                   # Chapter extraction
├── templates/                      # Web templates
├── labeled_chunks/                 # Processed chapter data
├── chunks/                         # Raw text chunks
└── txt/                           # Extracted text files
```

## Question Types

The generator creates various types of questions:

- **Definition questions**: "Што е [concept]?"
- **Characteristic questions**: "Кои се карактеристиките на [concept]?"
- **Function questions**: "Како функционира [concept]?"
- **Calculation questions**: "Како се пресметува [concept]?"
- **Relationship questions**: "Како е поврзано [concept1] со [concept2]?"

## API Endpoints

- `GET /` - Main page with chapter list
- `GET /chapter/<chapter_num>` - Chapter detail with quiz
- `GET /api/quiz/<chapter_num>` - Get quiz questions as JSON
- `POST /api/check_answer` - Check quiz answer

## Technologies Used

- **Flask**: Web framework
- **EasyOCR/Tesseract**: Optical character recognition
- **OpenAI API**: Advanced question generation
- **PDF2Image**: PDF processing
- **Python 3**: Core language

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Since this is a work-in-progress project, feedback and suggestions are especially appreciated.

## License

MIT License

## Author

Created for educational purposes to support Macedonian-language STEM education.
