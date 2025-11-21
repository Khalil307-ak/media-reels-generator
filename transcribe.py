"""
Transcription module for Media Reels Generator
Supports multiple ASR providers: OpenAI Whisper API, local Whisper, Hugging Face, WhisperX
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import time

logger = logging.getLogger("media_reels_generator")


class TranscriptionProvider:
    """Base class for transcription providers"""
    
    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'ar', 'en')
        
        Returns:
            Dictionary with 'text', 'segments', 'language'
        """
        raise NotImplementedError


class OpenAIWhisperProvider(TranscriptionProvider):
    """OpenAI Whisper API provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        """
        Initialize OpenAI Whisper provider
        
        Args:
            api_key: OpenAI API key (or from environment)
            model: Model name (default: "whisper-1")
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
            self.model = model
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
    
    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        logger.info(f"Transcribing with OpenAI Whisper API: {audio_path.name}")
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                with open(audio_path, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        language=language,
                        response_format="verbose_json"
                    )
                
                # Convert to our format
                segments = []
                if hasattr(transcript, 'segments'):
                    for seg in transcript.segments:
                        segments.append({
                            'start': seg.start,
                            'end': seg.end,
                            'text': seg.text
                        })
                else:
                    # Fallback: create single segment
                    segments.append({
                        'start': 0.0,
                        'end': 0.0,  # Will be updated if available
                        'text': transcript.text
                    })
                
                return {
                    'text': transcript.text,
                    'segments': segments,
                    'language': getattr(transcript, 'language', language or 'unknown')
                }
            
            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    logger.warning(f"Transcription attempt {attempt + 1} failed: {error_msg}. Retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"Transcription failed after {max_retries} attempts: {error_msg}")
                    # Provide helpful error message for connection issues
                    if "Connection" in error_msg or "getaddrinfo" in error_msg or "ConnectError" in error_msg:
                        logger.error("\n" + "="*60)
                        logger.error("CONNECTION ERROR DETECTED")
                        logger.error("="*60)
                        logger.error("Possible solutions:")
                        logger.error("1. Check your internet connection")
                        logger.error("2. Check if OpenAI API is accessible from your network")
                        logger.error("3. Try using local Whisper instead:")
                        logger.error("   - Change 'provider: local_whisper' in config.yaml")
                        logger.error("   - Or run: python run.py --input <file> --use-local-whisper")
                        logger.error("4. Check firewall/proxy settings")
                        logger.error("="*60 + "\n")
                    raise
        
        raise RuntimeError("Transcription failed after all retries")


class LocalWhisperProvider(TranscriptionProvider):
    """Local Whisper (openai-whisper) provider"""
    
    def __init__(self, model: str = "base", device: Optional[str] = None):
        """
        Initialize local Whisper provider
        
        Args:
            model: Model size ("tiny", "base", "small", "medium", "large")
            device: Device ("cpu", "cuda", "mps")
        """
        try:
            import whisper
            self.model_name = model
            logger.info(f"Loading local Whisper model: {model}")
            self.model = whisper.load_model(model, device=device)
            logger.info("Model loaded successfully")
        except ImportError:
            raise ImportError("whisper package not installed. Install with: pip install openai-whisper")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe using local Whisper"""
        logger.info(f"Transcribing with local Whisper: {audio_path.name}")
        
        try:
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                verbose=False
            )
            
            segments = []
            for seg in result.get('segments', []):
                segments.append({
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip()
                })
            
            return {
                'text': result['text'],
                'segments': segments,
                'language': result.get('language', language or 'unknown')
            }
        
        except Exception as e:
            logger.error(f"Local Whisper transcription failed: {e}")
            raise


class HuggingFaceWhisperProvider(TranscriptionProvider):
    """Hugging Face Whisper provider (example implementation)"""
    
    def __init__(self, model_id: str = "openai/whisper-base"):
        """
        Initialize Hugging Face Whisper provider
        
        Args:
            model_id: Hugging Face model ID
        """
        try:
            from transformers import WhisperProcessor, WhisperForConditionalGeneration
            import torch
            
            logger.info(f"Loading Hugging Face model: {model_id}")
            self.processor = WhisperProcessor.from_pretrained(model_id)
            self.model = WhisperForConditionalGeneration.from_pretrained(model_id)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            logger.info(f"Model loaded on {self.device}")
        except ImportError:
            raise ImportError("transformers package not installed. Install with: pip install transformers torch")
        except Exception as e:
            raise RuntimeError(f"Failed to load Hugging Face model: {e}")
    
    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe using Hugging Face Whisper"""
        logger.info(f"Transcribing with Hugging Face Whisper: {audio_path.name}")
        
        try:
            import librosa
            import torch
            
            # Load audio
            audio, sr = librosa.load(str(audio_path), sr=16000)
            
            # Process
            inputs = self.processor(audio, sampling_rate=sr, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                generated_ids = self.model.generate(**inputs)
            
            # Decode
            transcription = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Note: Hugging Face Whisper doesn't provide segments by default
            # You may need to use chunking for segment-level timestamps
            return {
                'text': transcription,
                'segments': [{'start': 0.0, 'end': 0.0, 'text': transcription}],
                'language': language or 'unknown'
            }
        
        except Exception as e:
            logger.error(f"Hugging Face transcription failed: {e}")
            raise


def create_transcription_provider(
    provider: str,
    config: Dict[str, Any]
) -> TranscriptionProvider:
    """
    Factory function to create transcription provider
    
    Args:
        provider: Provider name ("openai", "local_whisper", "huggingface", "whisperx")
        config: Configuration dictionary
    
    Returns:
        TranscriptionProvider instance
    """
    transcription_config = config.get('transcription', {})
    
    if provider == "openai":
        # Try to get API key from config first, then environment
        api_key = config.get('api', {}).get('openai_api_key', '').strip()
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY', '').strip()
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or in config.yaml")
        model = transcription_config.get('model', 'whisper-1')
        return OpenAIWhisperProvider(api_key=api_key, model=model)
    
    elif provider == "local_whisper":
        model = transcription_config.get('local_model', 'base')
        return LocalWhisperProvider(model=model)
    
    elif provider == "huggingface":
        model_id = transcription_config.get('model_id', 'openai/whisper-base')
        return HuggingFaceWhisperProvider(model_id=model_id)
    
    elif provider == "whisperx":
        # WhisperX implementation would go here
        raise NotImplementedError("WhisperX provider not yet implemented. Use 'local_whisper' or 'openai' instead.")
    
    else:
        raise ValueError(f"Unknown transcription provider: {provider}")


def detect_language(text: str) -> str:
    """
    Detect language from text using langdetect
    
    Args:
        text: Text to analyze
    
    Returns:
        Language code (e.g., 'ar', 'en')
    """
    try:
        from langdetect import detect, LangDetectException
        try:
            return detect(text)
        except LangDetectException:
            return 'unknown'
    except ImportError:
        logger.warning("langdetect not installed. Install with: pip install langdetect")
        return 'unknown'

