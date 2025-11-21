"""
Highlight extraction module for Media Reels Generator
Uses LLM to analyze transcript and extract key points with timestamps
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
import time

logger = logging.getLogger("media_reels_generator")


class HighlightExtractor:
    """Extract highlights from transcript using LLM"""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4o-mini", api_key: Optional[str] = None, temperature: float = 0.3):
        """
        Initialize highlight extractor
        
        Args:
            provider: LLM provider ("openai", "anthropic", "local")
            model: Model name
            api_key: API key (or from environment)
            temperature: Sampling temperature
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        
        if provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
            except ImportError:
                raise ImportError("openai package not installed. Install with: pip install openai")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
        
        elif provider == "anthropic":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
            except ImportError:
                raise ImportError("anthropic package not installed. Install with: pip install anthropic")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Anthropic client: {e}")
        
        elif provider == "local":
            # For local LLM, you would use llama.cpp, ollama, etc.
            raise NotImplementedError("Local LLM provider not yet implemented")
    
    def extract_highlights(
        self,
        transcript: str,
        segments: List[Dict[str, Any]],
        num_highlights: int = 5,
        min_duration: float = 6.0,
        max_duration: float = 60.0,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Extract highlights from transcript
        
        Args:
            transcript: Full transcript text
            segments: List of transcript segments with timestamps
            num_highlights: Number of highlights to extract
            min_duration: Minimum clip duration in seconds
            max_duration: Maximum clip duration in seconds
            language: Language code
        
        Returns:
            List of highlight dictionaries
        """
        logger.info(f"Extracting {num_highlights} highlights using {self.provider} ({self.model})")
        
        # Build prompt
        prompt = self._build_prompt(transcript, segments, num_highlights, min_duration, max_duration, language)
        
        # Call LLM
        response = self._call_llm(prompt)
        
        # Parse response
        highlights = self._parse_response(response, segments)
        
        # Validate and adjust timestamps
        highlights = self._validate_highlights(highlights, segments, min_duration, max_duration)
        
        logger.info(f"Extracted {len(highlights)} highlights")
        return highlights
    
    def _build_prompt(
        self,
        transcript: str,
        segments: List[Dict[str, Any]],
        num_highlights: int,
        min_duration: float,
        max_duration: float,
        language: str
    ) -> str:
        """Build prompt for LLM"""
        
        # Create segment summary with timestamps
        segment_text = "\n".join([
            f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}"
            for seg in segments[:100]  # Limit to first 100 segments to avoid token limits
        ])
        
        # Limit transcript length to avoid token limits
        transcript_limited = transcript[:5000] if len(transcript) > 5000 else transcript
        
        prompt = f"""You are analyzing a transcript to extract the most important and engaging highlights for social media reels.

TRANSCRIPT:
{transcript_limited}

SEGMENTS WITH TIMESTAMPS:
{segment_text}

TASK:
Extract exactly {num_highlights} key highlights from this content. Each highlight should be:
1. Engaging and attention-grabbing
2. Self-contained and understandable out of context
3. Between {min_duration} and {max_duration} seconds long
4. Covering the most important or interesting points

For each highlight, provide:
- start_time: Start timestamp in seconds (must match a segment timestamp)
- end_time: End timestamp in seconds (must match a segment timestamp)
- hook: A one-sentence catchy caption/hook (in {language})
- summary: A 2-3 line summary explaining the key point (in {language})
- confidence: Your confidence score (0.0-1.0) that this is a good highlight

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "start_time": 12.5,
    "end_time": 28.3,
    "hook": "One sentence engaging hook here",
    "summary": "First line of summary.\\nSecond line of summary.\\nThird line if needed.",
    "confidence": 0.95
  }},
  ...
]

IMPORTANT:
- Use exact timestamps from the segments provided
- Ensure each highlight is between {min_duration}s and {max_duration}s
- Make hooks catchy and social-media friendly
- Return ONLY the JSON array, no other text
"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM API with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                if self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that extracts highlights from transcripts. Always return valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=self.temperature,
                        response_format={"type": "json_object"} if self.model.startswith("gpt-4") else None
                    )
                    return response.choices[0].message.content
                
                elif self.provider == "anthropic":
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=4096,
                        temperature=self.temperature,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.content[0].text
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"LLM call attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"LLM call failed after {max_retries} attempts: {e}")
                    raise
        
        raise RuntimeError("LLM call failed after all retries")
    
    def _parse_response(self, response: str, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse LLM response and extract highlights"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith("```"):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1]) if lines[-1].startswith('```') else '\n'.join(lines[1:])
            
            # Parse JSON
            if response.startswith('{'):
                # Single object, wrap in array
                data = json.loads(response)
                if 'highlights' in data:
                    highlights = data['highlights']
                else:
                    highlights = [data]
            else:
                highlights = json.loads(response)
            
            # Validate structure
            if not isinstance(highlights, list):
                highlights = [highlights]
            
            # Ensure all required fields
            for h in highlights:
                if 'start_time' not in h or 'end_time' not in h:
                    raise ValueError("Missing required fields in highlight")
                if 'hook' not in h:
                    h['hook'] = "Key highlight"
                if 'summary' not in h:
                    h['summary'] = "Important point from the content."
                if 'confidence' not in h:
                    h['confidence'] = 0.8
            
            return highlights
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response: {response[:500]}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
    
    def _validate_highlights(
        self,
        highlights: List[Dict[str, Any]],
        segments: List[Dict[str, Any]],
        min_duration: float,
        max_duration: float
    ) -> List[Dict[str, Any]]:
        """Validate and adjust highlight timestamps"""
        validated = []
        
        for h in highlights:
            start = float(h['start_time'])
            end = float(h['end_time'])
            duration = end - start
            
            # Adjust if duration is too short or too long
            if duration < min_duration:
                # Extend end time
                end = start + min_duration
                h['end_time'] = end
                logger.warning(f"Extended highlight duration to minimum: {min_duration}s")
            
            elif duration > max_duration:
                # Trim end time
                end = start + max_duration
                h['end_time'] = end
                logger.warning(f"Trimmed highlight duration to maximum: {max_duration}s")
            
            # Ensure timestamps align with segment boundaries
            # Find nearest segment boundaries
            best_start = start
            best_end = end
            
            for seg in segments:
                if abs(seg['start'] - start) < 1.0:
                    best_start = seg['start']
                if abs(seg['end'] - end) < 1.0:
                    best_end = seg['end']
            
            h['start_time'] = best_start
            h['end_time'] = best_end
            
            validated.append(h)
        
        # Sort by start time
        validated.sort(key=lambda x: x['start_time'])
        
        return validated

