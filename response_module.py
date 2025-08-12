def format_ai_response(raw_text, mode):
    """
    Post-process AI raw output to add mode-specific headers and clean up.
    """
    if not raw_text or not raw_text.strip():
        return "No response received from AI."

    def format_ai_response(raw_text, mode):
        """
        Post-process AI raw output to add mode-specific headers and clean up.
        """
        if not raw_text or not raw_text.strip():
            return "No response received from AI."

        # The inner function definition was a copy-paste error. It is now removed.

        cleaned_text = raw_text.strip()

        headers = {
            "analyze": "Analysis Report:\n",
            "summarize": "Summary:\n",
            "translate": "Translation:\n"
        }
        header = headers.get(mode, "Response:\n")

        return f"{header}{cleaned_text}"
