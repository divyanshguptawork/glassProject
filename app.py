from flask import Flask, render_template, request, jsonify
import base64
import io
from PIL import Image, ImageGrab
import speech_recognition as sr
import pyttsx3
import threading
import time
import os
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key="AIzaSyBU30IKlP3f5_NrOvLqtWMQSx3-UZTV8M4")


class AIAssistant:
    def __init__(self):
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()

        # Initialize Gemini model
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2000,
            )
        )

        # Initialize microphone (with error handling)
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Microphone initialization error: {e}")
            self.microphone = None

    def take_screenshot(self):
        """Take a screenshot and return as base64"""
        try:
            screenshot = ImageGrab.grab()
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None

    def process_speech(self):
        """Process speech input and return text - ACTUAL IMPLEMENTATION"""
        if not self.microphone:
            return "Microphone not available"

        try:
            print("Listening for speech...")
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

            print("Processing speech...")
            # Use Google's speech recognition
            text = self.recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text

        except sr.WaitTimeoutError:
            return "Listening timeout - no speech detected"
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError as e:
            return f"Speech recognition error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def speak_text(self, text):
        """Convert text to speech"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")

    def extract_text_from_image(self, image):
        """Extract text from image using Gemini Vision"""
        try:
            # Use Gemini for OCR
            ocr_prompt = """
            Extract all visible text from this image accurately. 
            Return only the text content without additional commentary.
            If there's no readable text, return "No text found in image".
            Preserve formatting and structure where possible.
            """

            response = self.model.generate_content([ocr_prompt, image])
            return response.text.strip() if response.text else "No text found in image"

        except Exception as e:
            print(f"OCR error: {e}")
            return f"Error extracting text: {str(e)}"

    def generate_response(self, query, screenshot_data=None, personal_context=None):
        """Generate AI response using Gemini with proper context handling"""
        try:
            prompt_parts = []
            image = None
            extracted_text = ""

            # Add personal context if provided
            if personal_context and personal_context.strip():
                prompt_parts.append(f"Personal context about the user: {personal_context}")
                prompt_parts.append(
                    "Please respond naturally incorporating this context into your communication style.")

            # Handle screenshot data
            if screenshot_data:
                try:
                    # Decode base64 screenshot
                    image_data = base64.b64decode(screenshot_data)
                    image = Image.open(io.BytesIO(image_data))

                    # Convert to RGB if necessary
                    if image.mode != 'RGB':
                        image = image.convert('RGB')

                    # Extract text from the image first
                    extracted_text = self.extract_text_from_image(image)

                    if extracted_text and extracted_text != "No text found in image":
                        prompt_parts.append(f"Text extracted from the screenshot: {extracted_text}")

                except Exception as img_error:
                    print(f"Image processing error: {img_error}")
                    prompt_parts.append(
                        "There was an issue processing the screenshot, but I'll help with your question.")

            # Handle the user query
            if query and query.strip():
                if image:
                    prompt_parts.append(f"The user is asking about this screenshot: '{query}'")
                    prompt_parts.append("Please analyze the image and respond to their question comprehensively.")
                else:
                    prompt_parts.append(f"The user is asking: '{query}'")
                    prompt_parts.append("Please provide a helpful and informative response.")
            else:
                if image:
                    prompt_parts.append(
                        "Please describe what you see in this screenshot and provide any relevant insights or analysis.")
                else:
                    prompt_parts.append(
                        "The user has started a conversation. Please provide a friendly greeting and ask how you can help.")

            # Generate the full prompt
            full_prompt = "\n\n".join(prompt_parts)

            # Generate response with or without image
            if image:
                response = self.model.generate_content([full_prompt, image])
            else:
                response = self.model.generate_content(full_prompt)

            if response.text:
                return response.text
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."

        except Exception as e:
            print(f"AI generation error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"


assistant = AIAssistant()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/detached')
def detached():
    return render_template('detached.html')


@app.route('/api/screenshot', methods=['POST'])
def get_screenshot():
    """API endpoint to take screenshot"""
    screenshot = assistant.take_screenshot()
    if screenshot:
        return jsonify({'success': True, 'screenshot': screenshot})
    else:
        return jsonify({'success': False, 'error': 'Failed to take screenshot'})


@app.route('/api/listen', methods=['POST'])
def listen():
    """API endpoint to start listening"""
    try:
        text = assistant.process_speech()
        return jsonify({'success': True, 'text': text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/ask', methods=['POST'])
def ask():
    """API endpoint to process question with optional screenshot"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        screenshot_data = data.get('screenshot_data', None)
        personal_context = data.get('personal_context', None)

        print(f"Received request - Query: {query[:50]}...")
        print(f"Has screenshot: {screenshot_data is not None}")
        print(f"Has personal context: {personal_context is not None}")

        # Generate response using Gemini
        response = assistant.generate_response(query, screenshot_data, personal_context)

        return jsonify({
            'success': True,
            'response': response,
            'screenshot_processed': screenshot_data is not None
        })

    except Exception as e:
        print(f"Error in ask endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """API endpoint for settings management"""
    if request.method == 'GET':
        return jsonify({
            'personal_context': '',
            'voice_enabled': True,
            'auto_screenshot': True,
            'theme': 'glass'
        })
    else:
        data = request.get_json()
        # Here you would save settings to a file or database
        return jsonify({'success': True, 'message': 'Settings updated'})


if __name__ == '__main__':
    print("Starting Glass AI Flask Server...")
    app.run(debug=True, host='127.0.0.1', port=5000)
