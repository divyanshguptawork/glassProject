"""
Glass AI - Advanced AI Assistant with Vision Capabilities
========================================================

A sophisticated Flask-based AI assistant that combines computer vision, speech recognition,
and Google's Gemini AI to create an intelligent, context-aware co-pilot experience.

Features:
- Real-time screenshot analysis using Gemini Vision
- Speech-to-text with Google Speech Recognition
- Text-to-speech feedback
- OCR capabilities with high accuracy
- Personal context awareness
- RESTful API architecture
- Glass-morphic UI design

Author: Divyansh Gupta
Version: 2.0.0
License: MIT
"""

from flask import Flask, render_template, request, jsonify
import base64
import io
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import json

# Third-party imports
from PIL import Image, ImageGrab
import speech_recognition as sr
import pyttsx3
import threading
import time
import google.generativeai as genai

# Configure logging for production readiness
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('glass_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask application with enhanced configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Environment variables and configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', "AIzaSyBU30IKlP3f5_NrOvLqtWMQSx3-UZTV8M4")
ENABLE_SPEECH = os.environ.get('ENABLE_SPEECH', 'True').lower() == 'true'
MAX_SCREENSHOT_SIZE = (1920, 1080)  # Optimize screenshot size for processing

# Configure Gemini AI with enhanced error handling
try:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini AI configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini AI: {e}")
    raise


class AIAssistantCore:
    """
    Core AI Assistant class that handles all AI-related operations.

    This class encapsulates the main functionality of the Glass AI assistant,
    including screenshot processing, speech recognition, text-to-speech,
    OCR capabilities, and AI response generation using Google's Gemini model.
    """

    def __init__(self):
        """Initialize the AI Assistant with all required components."""
        self.is_listening = False
        self.recognizer = sr.Recognizer()

        # Initialize text-to-speech engine with error handling
        try:
            self.tts_engine = pyttsx3.init() if ENABLE_SPEECH else None
            self._configure_tts()
            logger.info("Text-to-speech engine initialized")
        except Exception as e:
            logger.warning(f"TTS initialization failed: {e}")
            self.tts_engine = None

        # Initialize Gemini model with optimized configuration
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2000,
                candidate_count=1,
                top_p=0.8,
                top_k=40
            )
        )

        # Initialize microphone with comprehensive error handling
        self._initialize_microphone()

        # Performance metrics
        self.request_count = 0
        self.start_time = datetime.now()

        logger.info("AI Assistant Core initialized successfully")

    def _configure_tts(self) -> None:
        """Configure text-to-speech engine with optimal settings."""
        if self.tts_engine:
            try:
                # Set speech rate and voice properties
                self.tts_engine.setProperty('rate', 180)  # Speed of speech
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Prefer female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                    else:
                        self.tts_engine.setProperty('voice', voices[0].id)
            except Exception as e:
                logger.warning(f"TTS configuration error: {e}")

    def _initialize_microphone(self) -> None:
        """Initialize and calibrate microphone for optimal speech recognition."""
        try:
            self.microphone = sr.Microphone()
            # Calibrate microphone for ambient noise
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            # Configure recognition settings for better accuracy
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3

            logger.info("Microphone initialized and calibrated")
        except Exception as e:
            logger.error(f"Microphone initialization error: {e}")
            self.microphone = None

    def capture_screenshot(self) -> Optional[str]:
        """
        Capture a screenshot and return it as a base64-encoded string.

        Returns:
            Optional[str]: Base64-encoded screenshot image, or None if capture fails
        """
        try:
            logger.info("Capturing screenshot...")
            screenshot = ImageGrab.grab()

            # Optimize screenshot size for faster processing
            if screenshot.size[0] > MAX_SCREENSHOT_SIZE[0] or screenshot.size[1] > MAX_SCREENSHOT_SIZE[1]:
                screenshot.thumbnail(MAX_SCREENSHOT_SIZE, Image.LANCZOS)

            # Convert to RGB if necessary and encode
            if screenshot.mode != 'RGB':
                screenshot = screenshot.convert('RGB')

            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG', optimize=True)
            img_str = base64.b64encode(buffer.getvalue()).decode()

            logger.info(f"Screenshot captured successfully ({len(img_str)} bytes)")
            return img_str

        except Exception as e:
            logger.error(f"Screenshot capture error: {e}")
            return None

    def process_speech_input(self) -> str:
        """
        Process speech input from microphone and convert to text.

        Returns:
            str: Recognized speech text or error message
        """
        if not self.microphone:
            return "Microphone not available"

        try:
            logger.info("Starting speech recognition...")
            with self.microphone as source:
                # Listen with timeout and phrase limits
                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

            logger.info("Processing audio data...")
            # Use Google's speech recognition service
            text = self.recognizer.recognize_google(
                audio,
                language='en-US',
                show_all=False
            )

            logger.info(f"Speech recognized: {text}")
            return text

        except sr.WaitTimeoutError:
            logger.warning("Speech recognition timeout")
            return "Listening timeout - no speech detected"
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return "Could not understand the audio"
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return f"Speech recognition error: {e}"
        except Exception as e:
            logger.error(f"Unexpected speech processing error: {e}")
            return f"Unexpected error: {e}"

    def synthesize_speech(self, text: str) -> bool:
        """
        Convert text to speech output.

        Args:
            text (str): Text to be spoken

        Returns:
            bool: True if speech synthesis was successful, False otherwise
        """
        if not self.tts_engine:
            logger.warning("TTS engine not available")
            return False

        try:
            # Clean text for better speech synthesis
            clean_text = text.replace('*', '').replace('#', '').strip()
            if len(clean_text) > 500:
                clean_text = clean_text[:500] + "..."

            self.tts_engine.say(clean_text)
            self.tts_engine.runAndWait()
            logger.info("Speech synthesis completed")
            return True

        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False

    def extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extract text from image using Gemini Vision OCR capabilities.

        Args:
            image (Image.Image): PIL Image object to extract text from

        Returns:
            str: Extracted text content or error message
        """
        try:
            logger.info("Starting OCR text extraction...")

            # Optimized OCR prompt for better accuracy
            ocr_prompt = """
            You are an advanced OCR system. Extract ALL visible text from this image with high accuracy.

            Instructions:
            1. Return ONLY the text content, no commentary
            2. Preserve original formatting and structure
            3. Include punctuation and special characters
            4. If no text is found, return "No text found in image"
            5. Maintain line breaks and spacing where meaningful

            Focus on accuracy and completeness.
            """

            response = self.model.generate_content([ocr_prompt, image])
            extracted_text = response.text.strip() if response.text else "No text found in image"

            logger.info(f"OCR extraction completed: {len(extracted_text)} characters extracted")
            return extracted_text

        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return f"Error extracting text: {str(e)}"

    def generate_ai_response(
            self,
            query: str,
            screenshot_data: Optional[str] = None,
            personal_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI response using Gemini with context awareness.

        Args:
            query (str): User's question or request
            screenshot_data (Optional[str]): Base64-encoded screenshot
            personal_context (Optional[str]): User's personal context/preferences

        Returns:
            Dict[str, Any]: Response data including text, metadata, and processing info
        """
        start_time = time.time()
        self.request_count += 1

        try:
            logger.info(f"Processing AI request #{self.request_count}")

            prompt_parts = []
            image = None
            extracted_text = ""
            processing_metadata = {}

            # Add personal context for tailored responses
            if personal_context and personal_context.strip():
                prompt_parts.append(
                    f"Personal Context: {personal_context}\n"
                    "Use this context to personalize your communication style and responses."
                )

            # Process screenshot if provided
            if screenshot_data:
                try:
                    # Decode and process image
                    image_data = base64.b64decode(screenshot_data)
                    image = Image.open(io.BytesIO(image_data))

                    # Ensure RGB format for Gemini
                    if image.mode != 'RGB':
                        image = image.convert('RGB')

                    # Extract text from image
                    extracted_text = self.extract_text_from_image(image)
                    processing_metadata['ocr_text_length'] = len(extracted_text)

                    if extracted_text and extracted_text != "No text found in image":
                        prompt_parts.append(
                            f"Screen Content Analysis:\n"
                            f"The following text was extracted from the user's screen:\n"
                            f"---\n{extracted_text}\n---"
                        )

                except Exception as img_error:
                    logger.error(f"Image processing error: {img_error}")
                    prompt_parts.append(
                        "Note: There was an issue processing the screenshot, "
                        "but I'll help with your question based on the text query."
                    )

            # Construct main prompt based on input
            if query and query.strip():
                if image:
                    prompt_parts.append(
                        f"User Query about Screen Content: '{query}'\n"
                        "Please analyze the screenshot and provide a comprehensive response "
                        "that addresses their specific question."
                    )
                else:
                    prompt_parts.append(
                        f"User Query: '{query}'\n"
                        "Please provide a helpful, informative, and engaging response."
                    )
            else:
                if image:
                    prompt_parts.append(
                        "Please analyze this screenshot and provide insights, explanations, "
                        "or relevant information about what you observe. Be specific and helpful."
                    )
                else:
                    prompt_parts.append(
                        "Hello! I'm Glass, your AI assistant. How can I help you today?"
                    )

            # Add response guidelines
            prompt_parts.append(
                "\nResponse Guidelines:\n"
                "- Be concise but comprehensive\n"
                "- Use markdown formatting for better readability\n"
                "- Provide actionable insights when possible\n"
                "- Be friendly and professional\n"
                "- If analyzing code or technical content, explain clearly"
            )

            # Generate response
            full_prompt = "\n\n".join(prompt_parts)

            if image:
                response = self.model.generate_content([full_prompt, image])
            else:
                response = self.model.generate_content(full_prompt)

            processing_time = time.time() - start_time

            if response.text:
                logger.info(f"AI response generated successfully in {processing_time:.2f}s")
                return {
                    'success': True,
                    'response': response.text,
                    'metadata': {
                        'processing_time': processing_time,
                        'request_id': self.request_count,
                        'has_screenshot': screenshot_data is not None,
                        'has_context': personal_context is not None,
                        'extracted_text_length': len(extracted_text),
                        **processing_metadata
                    }
                }
            else:
                return {
                    'success': False,
                    'error': "No response generated from AI model",
                    'metadata': {'processing_time': processing_time}
                }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"AI generation error: {e}")
            return {
                'success': False,
                'error': f"AI processing failed: {str(e)}",
                'metadata': {'processing_time': processing_time}
            }

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system performance and usage statistics.

        Returns:
            Dict[str, Any]: System statistics and performance metrics
        """
        uptime = datetime.now() - self.start_time
        return {
            'uptime_seconds': uptime.total_seconds(),
            'total_requests': self.request_count,
            'avg_requests_per_hour': self.request_count / max(uptime.total_seconds() / 3600, 1),
            'microphone_available': self.microphone is not None,
            'tts_available': self.tts_engine is not None,
            'gemini_configured': True
        }


# Initialize the AI Assistant
try:
    assistant = AIAssistantCore()
    logger.info("Glass AI Assistant initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize AI Assistant: {e}")
    raise


# Flask Route Handlers
# ===================

@app.route('/')
def index():
    """Serve the main Glass AI interface."""
    return render_template('index.html')


@app.route('/detached')
def detached():
    """Serve the detached/floating interface."""
    return render_template('detached.html')


@app.route('/api/screenshot', methods=['POST'])
def api_screenshot():
    """
    API endpoint to capture a screenshot.

    Returns:
        JSON response with screenshot data or error message
    """
    try:
        logger.info("Screenshot API endpoint called")
        screenshot = assistant.capture_screenshot()

        if screenshot:
            return jsonify({
                'success': True,
                'screenshot': screenshot,
                'timestamp': datetime.now().isoformat(),
                'size': len(screenshot)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to capture screenshot'
            }), 500

    except Exception as e:
        logger.error(f"Screenshot API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/listen', methods=['POST'])
def api_listen():
    """
    API endpoint to process speech input.

    Returns:
        JSON response with recognized text or error message
    """
    try:
        logger.info("Speech recognition API endpoint called")
        text = assistant.process_speech_input()

        return jsonify({
            'success': True,
            'text': text,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Speech recognition API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ask', methods=['POST'])
def api_ask():
    """
    Main AI processing endpoint - handles queries with optional screenshots.

    Expected JSON payload:
        - query (str): User's question or request
        - screenshot_data (str, optional): Base64-encoded screenshot
        - personal_context (str, optional): User's personal context

    Returns:
        JSON response with AI-generated answer and metadata
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400

        query = data.get('query', '').strip()
        screenshot_data = data.get('screenshot_data')
        personal_context = data.get('personal_context', '').strip()

        logger.info(
            f"AI query API called - Query: {len(query)} chars, "
            f"Has screenshot: {screenshot_data is not None}, "
            f"Has context: {len(personal_context) > 0}"
        )

        # Generate AI response
        result = assistant.generate_ai_response(query, screenshot_data, personal_context)

        # Add API-specific metadata
        result['api_version'] = '2.0'
        result['timestamp'] = datetime.now().isoformat()

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"AI query API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """
    Settings management endpoint.

    GET: Returns current settings
    POST: Updates settings with provided data
    """
    if request.method == 'GET':
        # Return default settings (in production, load from database)
        return jsonify({
            'personal_context': '',
            'voice_enabled': ENABLE_SPEECH,
            'auto_screenshot': True,
            'theme': 'glass',
            'max_response_length': 2000,
            'speech_rate': 180
        })
    else:
        try:
            data = request.get_json()
            logger.info("Settings updated via API")

            # In production, save to database
            # For now, just return success
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Settings API error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """
    System statistics and health check endpoint.

    Returns:
        JSON response with system performance metrics
    """
    try:
        stats = assistant.get_system_stats()
        stats['api_version'] = '2.0'
        stats['timestamp'] = datetime.now().isoformat()

        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Error Handlers
# ==============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with JSON response for API endpoints."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'API endpoint not found',
            'path': request.path
        }), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with proper logging."""
    logger.error(f"Internal server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    return render_template('500.html'), 500


# Health Check
# ============

@app.route('/health')
def health_check():
    """Basic health check endpoint for monitoring systems."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })


# Main Application Entry Point
# =============================

if __name__ == '__main__':
    logger.info("Starting Glass AI Flask Server v2.0...")
    logger.info(f"Speech recognition enabled: {ENABLE_SPEECH}")
    logger.info(f"Max content length: {app.config['MAX_CONTENT_LENGTH']} bytes")

    # Development server configuration
    app.run(
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        host=os.environ.get('FLASK_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        threaded=True
    )