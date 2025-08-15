import google.generativeai as genai
from PIL import Image


def extract_text(image_file):
    """Extract text from image using Google's Gemini Vision model"""
    try:
        genai.configure(api_key="AIzaSyBU30IKlP3f5_NrOvLqtWMQSx3-UZTV8M4")

        # Reset file pointer to beginning
        image_file.seek(0)

        # Open and process the image
        image = Image.open(image_file)

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Use Gemini Flash for faster OCR
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for more accurate OCR
                max_output_tokens=2000,
            )
        )

        prompt = """
        Please extract all text from this image accurately. 
        Return only the text content without any additional commentary, explanations, or formatting.
        If there's no readable text in the image, return "No text found in image".
        Preserve the original structure and formatting of the text as much as possible.
        """

        response = model.generate_content([prompt, image])
        extracted_text = response.text.strip() if response.text else "No text found in image"

        return extracted_text

    except Exception as e:
        return f"Error extracting text: {str(e)}"