"""
Speech Recognition Service using Google Cloud Speech-to-Text
Provides better accuracy for English, Hindi, and Telugu
"""

import requests
import base64
import os
from typing import Optional

# Google Cloud Speech-to-Text API
# Free tier: 60 minutes/month
GOOGLE_SPEECH_API_URL = "https://speech.googleapis.com/v1/speech:recognize"

# Alternative: Use AssemblyAI (free tier available)
ASSEMBLYAI_API_URL = "https://api.assemblyai.com/v2/transcript"


def transcribe_audio_google(audio_data: bytes, language_code: str = "en-US") -> Optional[str]:
    """
    Transcribe audio using Google Cloud Speech-to-Text
    Requires GOOGLE_API_KEY environment variable
    
    language_code options:
    - "en-US" (English)
    - "hi-IN" (Hindi)
    - "te-IN" (Telugu)
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("Google API key not found. Please set GOOGLE_API_KEY environment variable.")
        return None
    
    try:
        # Encode audio to base64
        audio_content = base64.b64encode(audio_data).decode('utf-8')
        
        # Map language codes
        lang_map = {
            'en-US': 'en-US',
            'hi-IN': 'hi-IN',
            'te-IN': 'te-IN'
        }
        
        google_lang = lang_map.get(language_code, 'en-US')
        
        payload = {
            "config": {
                "encoding": "WEBM_OPUS",
                "sampleRateHertz": 48000,
                "languageCode": google_lang,
                "alternativeLanguageCodes": ["en-US", "hi-IN", "te-IN"],
                "enableAutomaticPunctuation": True,
                "model": "latest_long"
            },
            "audio": {
                "content": audio_content
            }
        }
        
        url = f"{GOOGLE_SPEECH_API_URL}?key={api_key}"
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'results' in result and len(result['results']) > 0:
                transcript = result['results'][0]['alternatives'][0]['transcript']
                return transcript
        
        print(f"Google Speech API error: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        print(f"Speech transcription error: {e}")
        return None


def transcribe_audio_assemblyai(audio_data: bytes, language_code: str = "en") -> Optional[str]:
    """
    Transcribe audio using AssemblyAI (free tier: 3 hours/month)
    Supports: English, Hindi
    
    Get API key from: https://www.assemblyai.com/
    """
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    
    if not api_key:
        print("AssemblyAI API key not found. Please set ASSEMBLYAI_API_KEY environment variable.")
        return None
    
    try:
        headers = {
            "authorization": api_key,
            "content-type": "application/json"
        }
        
        # Upload audio
        upload_response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=audio_data
        )
        
        if upload_response.status_code != 200:
            print(f"Upload error: {upload_response.text}")
            return None
        
        upload_url = upload_response.json()["upload_url"]
        
        # Language mapping
        lang_map = {
            'en-US': 'en',
            'hi-IN': 'hi',
            'te-IN': 'en'  # Telugu not supported, fallback to English
        }
        
        # Request transcription
        transcript_request = {
            "audio_url": upload_url,
            "language_code": lang_map.get(language_code, 'en')
        }
        
        transcript_response = requests.post(
            ASSEMBLYAI_API_URL,
            headers=headers,
            json=transcript_request
        )
        
        transcript_id = transcript_response.json()["id"]
        
        # Poll for result
        polling_endpoint = f"{ASSEMBLYAI_API_URL}/{transcript_id}"
        
        while True:
            polling_response = requests.get(polling_endpoint, headers=headers)
            polling_result = polling_response.json()
            
            if polling_result["status"] == "completed":
                return polling_result["text"]
            elif polling_result["status"] == "error":
                print(f"Transcription error: {polling_result['error']}")
                return None
            
            import time
            time.sleep(1)
        
    except Exception as e:
        print(f"AssemblyAI error: {e}")
        return None


def transcribe_audio_huggingface(audio_data: bytes, language_code: str = "en") -> Optional[str]:
    """
    Transcribe audio using Hugging Face Whisper model
    FREE - No API key needed for basic usage!
    Supports: English, Hindi, Telugu, and 90+ languages
    """
    try:
        # Hugging Face Inference API for Whisper
        # Using the correct API endpoint format
        api_url = "https://api-inference.huggingface.co/models/openai/whisper-base"
        
        # The API accepts raw audio bytes directly
        headers = {
            "Authorization": "Bearer hf_dummy",  # Dummy token for free tier
            "Content-Type": "audio/webm"
        }
        
        # Send audio data
        response = requests.post(api_url, headers=headers, data=audio_data, timeout=30)
        
        print(f"Whisper API status: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Whisper result: {result}", flush=True)
            
            # Extract text from result
            if isinstance(result, dict):
                if 'text' in result:
                    return result['text']
                if 'transcription' in result:
                    return result['transcription']
            elif isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    return result[0].get('text', str(result[0]))
                return str(result[0])
        
        elif response.status_code == 503:
            print("Whisper model is loading, please try again in a moment", flush=True)
            return None
        
        elif response.status_code == 401:
            print("Authentication error - trying without token", flush=True)
            # Try without authorization header
            headers = {"Content-Type": "audio/webm"}
            response = requests.post(api_url, headers=headers, data=audio_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and 'text' in result:
                    return result['text']
        
        else:
            print(f"Whisper API error: {response.status_code} - {response.text[:200]}", flush=True)
            return None
        
    except requests.exceptions.Timeout:
        print("Whisper API timeout - the model might be loading", flush=True)
        return None
    except Exception as e:
        print(f"Whisper transcription error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None


def transcribe_audio(audio_data: bytes, language_code: str = "en-US", provider: str = "huggingface") -> Optional[str]:
    """
    Main transcription function - tries multiple providers
    
    Args:
        audio_data: Raw audio bytes
        language_code: Language code (en-US, hi-IN, te-IN)
        provider: 'huggingface' (free), 'google', or 'assemblyai'
    
    Returns:
        Transcribed text or None
    """
    if provider == "google":
        return transcribe_audio_google(audio_data, language_code)
    elif provider == "assemblyai":
        return transcribe_audio_assemblyai(audio_data, language_code)
    else:
        # Default: Hugging Face Whisper (FREE)
        return transcribe_audio_huggingface(audio_data, language_code)


# Simple test
if __name__ == '__main__':
    print("Speech Service ready!")
    print("Available providers:")
    print("1. Hugging Face Whisper (FREE - Recommended)")
    print("2. Google Cloud Speech (60 min/month free)")
    print("3. AssemblyAI (3 hours/month free)")
