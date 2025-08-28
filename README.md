# Glass AI - Advanced AI Assistant with Vision Capabilities

## Table of Contents
- [ Project Overview](#-project-overview)  
- [ Key Features](#-key-features)  
- [ Project Structure & File Details](#-project-structure--file-details)  
  - [Core Application Files](#core-application-files)  
  - [Frontend Files](#frontend-files)  
  - [Styling Files](#styling-files)  
  - [JavaScript Files](#javascript-files)  
- [ Installation & Setup](#-installation--setup)  
- [ Configuration Options](#-configuration-options)  
- [ Usage Guide](#-usage-guide)  
- [ Future Development Roadmap](#-future-development-roadmap)  
- [ Technical Architecture](#-technical-architecture)  
- [ API Documentation](#-api-documentation)  
- [ Troubleshooting](#-troubleshooting)  
- [ Contributing](#-contributing)  
- [ License & Credits](#-license--credits)  
- [ Support & Contact](#-support--contact)  
- [ Quick Start Commands](#-quick-start-commands)  

---

##  Project Overview
Glass AI is a sophisticated Flask-based AI assistant that combines computer vision, speech recognition, and Google's Gemini AI to create an intelligent, context-aware co-pilot experience. The application features a modern glass-morphic UI design with real-time screenshot analysis, speech-to-text capabilities, and OCR functionality.

---

##  Key Features
- Real-time Screenshot Analysis using Gemini Vision API  
- Speech-to-Text with Google Speech Recognition  
- Text-to-Speech feedback system  
- OCR Capabilities with high accuracy text extraction  
- Personal Context Awareness for tailored responses  
- RESTful API Architecture for extensibility  
- Glass-morphic UI Design with modern aesthetics  
- Detached Mode for floating assistant interface  
- Multi-modal Input supporting images, voice, and text  

---

##  Project Structure & File Details

### Core Application Files

#### `app.py` - Main Flask Application
The heart of the Glass AI system, handling all backend operations:

**Key Components:**
- `AIAssistantCore` class: encapsulates AI operations (screenshots, speech recognition, TTS, OCR, AI responses)  
- Flask routes: RESTful API endpoints for frontend communication  
- Error handling & performance monitoring  

**Main Features:**
- Screenshot capture with `ImageGrab.grab()`  
- Speech recognition (`speech_recognition`)  
- Text-to-speech with `pyttsx3`  
- Gemini AI integration  
- Personal context management  

**API Endpoints:**
- `GET /` → Main interface  
- `GET /detached` → Detached floating interface  
- `POST /api/screenshot` → Screenshot capture  
- `POST /api/listen` → Speech recognition  
- `POST /api/ask` → AI processing  
- `GET/POST /api/settings` → Settings management  
- `GET /api/stats` → System statistics  
- `GET /health` → Health check  

#### `ocr_module.py` - OCR Processing
- `extract_text(image_file)`: Processes images and extracts text using Gemini Flash model  
- Supports multiple formats, preserves formatting  
- Config: Gemini-1.5-Flash, low temperature (0.1), 2000 tokens  

#### `prompt_module.py` - AI Response Generation
- `create_and_send_prompt(extracted_text, user_query)`  
- `format_ai_response(raw_text, mode)`  
- Supports analyze, summarize, translate modes  
- Markdown formatting, context-aware prompts  

---

### Frontend Files

#### `templates/index.html` - Main Interface
Features glass-morphic design with:  
- Video background, blurred panels  
- Chat interface with typewriter AI responses  
- File upload (drag/drop)  
- Settings dropdown for personal context  

#### `templates/detached.html` - Floating Interface
- Floating control bar  
- Collapsible chat window  
- Status indicators  

---

### Styling Files
- `static/style.css`: Full glass UI, dark mode, animations, responsive grid  
- `static/detached.css`: Floating interface, compact styling  

### JavaScript Files
- `static/script.js`: Handles screenshots, voice, chat, detached mode  
- `static/detached.js`: Compact floating interface logic  

---

##  Installation & Setup

### Prerequisites
- Python 3.8+  
- Google Cloud account (Gemini API enabled)  
- Windows/macOS/Linux  
- Browser with WebRTC support  

### Steps
```bash
# Clone repo
git clone https://github.com/yourusername/glass-ai.git
cd glass-ai

# Create virtual environment
python -m venv glass_ai_env
source glass_ai_env/bin/activate   # Windows: glass_ai_env\Scripts\activate

# Install dependencies
pip install flask pillow speechrecognition pyttsx3 google-generativeai
````

### Configure Environment

Create `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
ENABLE_SPEECH=True
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
SECRET_KEY=your_secret_key_here
```

### System Dependencies

**Windows:**

```bash
pip install pyaudio
```

**macOS:**

```bash
brew install portaudio
pip install pyaudio
```

**Linux:**

```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

### Run

```bash
python app.py
```

Access → [http://localhost:5000](http://localhost:5000)

---

##  Configuration Options

* `GEMINI_API_KEY` → required
* `ENABLE_SPEECH` → enable/disable speech (default: True)
* `FLASK_DEBUG` → debug mode
* `FLASK_HOST` & `FLASK_PORT` → server config
* `SECRET_KEY` → Flask session key

---

##  Usage Guide

* **Screenshots**: Click *Ask* → analyze screen content
* **Voice**: Click *Listen* → speak your query
* **File Upload**: Drag/drop image → ask questions
* **Chat**: Type questions → AI responds with context

**Advanced Features:**

* Personal context in settings
* Detached floating mode

---

##  Future Development Roadmap

* **Phase 1**: Better OCR, multi-language speech, advanced screenshots
* **Phase 2**: Memory system, multimodal inputs (video, audio, docs)
* **Phase 3**: Enterprise (multi-user, security, analytics)
* **Phase 4**: Mobile apps, cloud infra, collaboration tools

---

##  Technical Architecture

**Backend (Flask)**

* AI Core → screenshots, voice, OCR, responses
* REST API → `/api/screenshot`, `/api/listen`, `/api/ask`, `/api/settings`

**Frontend**

* `index.html` → main UI
* `detached.html` → floating UI
* JS controllers for real-time updates

**Data Flow**
User → Input (text/voice/screenshot) → Flask API → Gemini AI → Response → UI

---

##  API Documentation

### Screenshot Capture

`POST /api/screenshot`

```json
{
  "success": true,
  "screenshot": "base64_encoded_image",
  "timestamp": "iso_string",
  "size": 1024
}
```

### AI Query

`POST /api/ask`

```json
{
  "query": "user_question",
  "screenshot_data": "base64_image",
  "personal_context": "user_context"
}
```

### Speech Recognition

`POST /api/listen`

```json
{
  "success": true,
  "text": "recognized speech",
  "timestamp": "iso_string"
}
```

---

##  Troubleshooting

* **Mic not working** → check permissions, devices
* **Screenshot fails** → grant permissions (macOS/Windows)
* **API rate limiting** → monitor Gemini quotas
* **Performance** → lower screenshot resolution

**Error Codes**

* `400` Invalid request
* `429` Rate limited
* `500` Internal error
* `503` AI service unavailable

---

##  Contributing

* Follow **PEP 8**
* Add docstrings & unit tests
* Use `pytest`, `black`, `flake8`, `mypy`

```bash
pytest tests/
black src/
flake8 src/
```

---

##  Credits

* **Author**: Divyansh Gupta, Abhi Arora, Vince Reynolds
* **Version**: 2.0.0
* **AI**: Google Gemini API
* **UI**: Custom Glass-morphic Design
* **Speech**: Google Speech Recognition, pyttsx3

**Libraries**: Flask, Pillow, SpeechRecognition, pyttsx3, google-generativeai

---

##  Support & Contact

* **Issues** → GitHub Issues
* **Discussions** → GitHub Discussions
* **Email** → [divyanshguptabooks@gmail.com](mailto:divyanshguptabooks@gmail.com)

---

##  Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/yourusername/glass-ai.git
cd glass-ai
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with API keys

# Run
python app.py

# Access
# Open http://localhost:5000
```

---

Glass AI represents a cutting-edge approach to AI-assisted computing, combining modern web technologies with powerful AI capabilities to create an intuitive and helpful digital assistant. Its modular architecture ensures easy maintenance, extensibility, and developer adoption.

