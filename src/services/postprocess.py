"""
Post-processing service using LLM.

Cleans raw ASR transcript:
- Fix punctuation and capitalization
- Remove filler words (um, uh, etc)
- Correct obvious ASR errors
- Mark [INAUDIBLE] segments
"""
import logging
from typing import Dict, Any
from src.services.llm_provider import get_llm_provider, load_prompt
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def post_process_transcript(
    raw_transcript: str,
    language: str = "id",
    remove_fillers: bool = True,
    verbatim: bool = False
) -> str:
    """
    Post-process raw transcript using LLM.
    
    Args:
        raw_transcript: Raw text from Whisper
        language: ISO language code
        remove_fillers: Remove filler words (um, uh, etc)
        verbatim: Keep everything as-is (no cleanup)
        
    Returns:
        Cleaned transcript
    """
    # Load system prompt
    system_prompt = load_prompt("system_transcription")
    
    # Build user prompt
    user_prompt = f"""<task>post_process_transcript</task>

<raw_transcript>
{raw_transcript}
</raw_transcript>

<settings>
- language: {language}
- remove_fillers: {str(remove_fillers).lower()}
- verbatim: {str(verbatim).lower()}
</settings>

Clean and format this transcript. Fix punctuation, capitalization, and obvious ASR errors. Output only the cleaned transcript — no commentary."""
    
    # Get LLM provider
    provider = get_llm_provider(
        provider_name=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url
    )
    
    # Generate cleaned transcript
    logger.info(f"Post-processing transcript with {settings.llm_provider}")
    clean_transcript = provider.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=4096
    )
    
    return clean_transcript.strip()


def generate_meeting_notes(transcript: str, metadata: Dict[str, Any] = None) -> str:
    """
    Generate meeting notes from transcript.
    
    Args:
        transcript: Clean transcript
        metadata: Optional metadata (date, participants, etc)
        
    Returns:
        Structured meeting notes
    """
    system_prompt = load_prompt("system_meeting_notes")
    
    metadata = metadata or {}
    user_prompt = f"""<task>generate_meeting_notes</task>

<transcript>
{transcript}
</transcript>

<metadata>
- meeting_date: {metadata.get('date', 'unknown')}
- participants: {metadata.get('participants', 'unknown')}
- meeting_type: {metadata.get('type', 'general')}
</metadata>

Extract meeting intelligence from this transcript. Follow the output structure defined in your system prompt exactly. Output only the report — no preamble."""
    
    provider = get_llm_provider(
        provider_name=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url
    )
    
    logger.info(f"Generating meeting notes with {settings.llm_provider}")
    notes = provider.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=8192
    )
    
    return notes.strip()


def extract_quotes(transcript: str, count: int = 5) -> str:
    """
    Extract key quotes from transcript.
    
    Args:
        transcript: Clean transcript
        count: Number of quotes to extract (5-10)
        
    Returns:
        Formatted quotes with attribution
    """
    system_prompt = load_prompt("system_interview")
    
    user_prompt = f"""<task>extract_quotes</task>

<transcript>
{transcript}
</transcript>

<requirements>
- Count: {count} quotes
- Minimum quote length: 15 words
- Maximum quote length: 60 words
- Must be self-contained (understandable without full context)
- Speaker attribution required
</requirements>

Output format:
> "{{quote}}"
— {{Speaker Name or SPEAKER_1}}

Output only the quotes. No intro, no commentary."""
    
    provider = get_llm_provider(
        provider_name=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url
    )
    
    logger.info(f"Extracting quotes with {settings.llm_provider}")
    quotes = provider.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=4096
    )
    
    return quotes.strip()


def translate_transcript(
    transcript: str,
    source_language: str,
    target_language: str
) -> str:
    """
    Translate transcript to another language.
    
    Args:
        transcript: Source transcript
        source_language: Source language code
        target_language: Target language code
        
    Returns:
        Translated transcript
    """
    system_prompt = load_prompt("system_transcription")
    
    user_prompt = f"""<task>translate_transcript</task>

<source_language>{source_language}</source_language>
<target_language>{target_language}</target_language>

<transcript>
{transcript}
</transcript>

Translate this transcript accurately. Preserve:
- Speaker labels and formatting
- Technical terms (translate meaning, keep original in parentheses if ambiguous)
- Timestamps if present

Do not summarize. Translate the full content. Output only the translated transcript."""
    
    provider = get_llm_provider(
        provider_name=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url
    )
    
    logger.info(f"Translating transcript with {settings.llm_provider}")
    translated = provider.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=8192
    )
    
    return translated.strip()
