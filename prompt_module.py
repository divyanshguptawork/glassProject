import google.generativeai as genai


def create_and_send_prompt(extracted_text, user_query):
    """Create a conversational prompt and send it to Gemini AI."""

    try:
        genai.configure(api_key="AIzaSyBU30IKlP3f5_NrOvLqtWMQSx3-UZTV8M4")

        prompt_parts = []

        # System role with formatting instructions
        prompt_parts.append(
            "You are Glass - a real-time, context-aware co-pilot. Your primary goal is to provide concise, helpful, and friendly responses to a user's questions about one or more images. Format your responses using markdown where appropriate (use **bold** for emphasis, *italic* for subtle emphasis, and line breaks for readability).")

        # Add extracted text from all images if available
        if extracted_text and extracted_text.strip() != "":
            prompt_parts.append(f"Here is the text extracted from the user's image(s):\n---\n{extracted_text}\n---")

        # Add the user's direct query
        if user_query and user_query.strip() != "":
            prompt_parts.append(f"User's request: {user_query}")
        else:
            # If there's no direct query, provide a default instruction
            prompt_parts.append(
                "The user has provided images but no specific query. Please analyze the text in the images and provide a helpful, brief summary or insight.")

        full_prompt = "\n\n".join(prompt_parts)

        model = genai.GenerativeModel(
            "gemini-1.5-flash",  # Using Flash model for faster responses
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,  # Limit response length for faster processing
            )
        )
        response = model.generate_content(full_prompt)

        return response.text if response.text else "No response generated."

    except Exception as e:
        return f"Error communicating with AI: {str(e)}"