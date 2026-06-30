"""
llm.py - LLM integration module for Gemini 2.5 Flash.

Handles all communication with the Google Gemini API including
error handling, retries, and response formatting.
"""

import os
import time
from typing import Optional, Generator

import google.generativeai as genai
from dotenv import load_dotenv

from utils.constants import GEMINI_MODEL, LLM_TEMPERATURE, LLM_MAX_OUTPUT_TOKENS
from core.prompts import SYSTEM_PROMPT

load_dotenv()


def configure_gemini(api_key: Optional[str] = None) -> None:
    """Configure the Gemini API with the provided or environment API key."""
    key = api_key or os.getenv("GOOGLE_API_KEY", "")
    if not key:
        raise ValueError("GOOGLE_API_KEY not found. Set it in .env or pass it directly.")
    genai.configure(api_key=key)


def get_gemini_model(
    model_name: str = GEMINI_MODEL,
    temperature: float = LLM_TEMPERATURE,
    max_tokens: int = LLM_MAX_OUTPUT_TOKENS,
):
    """Create and return a configured Gemini generative model."""
    configure_gemini()
    
    generation_config = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT,
    )
    return model


def generate_response(
    prompt: str,
    model=None,
    max_retries: int = 3,
    retry_delay: float = 2.0,
) -> str:
    """
    Generate a response from Gemini with retry logic.
    
    Args:
        prompt: The formatted prompt to send.
        model: Pre-configured model (optional).
        max_retries: Number of retry attempts on failure.
        retry_delay: Seconds to wait between retries.
    
    Returns:
        Generated text response.
    """
    if model is None:
        model = get_gemini_model()
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            
            # Handle blocked responses
            if response.prompt_feedback:
                return "I cannot provide a response for this query due to content safety filters."
            
            return "No response generated. Please try rephrasing your question."
            
        except Exception as e:
            error_str = str(e).lower()
            
            if "quota" in error_str or "rate" in error_str or "429" in error_str:
                wait_time = retry_delay * (2 ** attempt)
                time.sleep(wait_time)
                continue
            
            if "internal" in error_str or "500" in error_str:
                time.sleep(retry_delay)
                continue
            
            if attempt == max_retries - 1:
                return f"Error generating response: {str(e)}"
            
            time.sleep(retry_delay)
    
    return "Failed to generate response after multiple attempts. Please try again."


def generate_streaming_response(
    prompt: str,
    model=None,
) -> Generator[str, None, None]:
    """
    Generate a streaming response from Gemini.
    
    Yields text chunks as they arrive for real-time display.
    """
    if model is None:
        model = get_gemini_model()
    
    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"\n\nError during streaming: {str(e)}"
