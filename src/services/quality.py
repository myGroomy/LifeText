"""
Quality checking service for transcripts.

Evaluates transcript quality and flags issues.
"""
import logging
import re
from typing import Dict, Any
from src.services.llm_provider import get_llm_provider, load_prompt
from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def check_quality(transcript: str) -> Dict[str, Any]:
    """
    Check transcript quality using LLM.
    
    Args:
        transcript: Cleaned transcript to evaluate
        
    Returns:
        Dict with:
        - quality_score: int (1-10)
        - flag_review: bool
        - issues: list of critical issues
        - checks: dict of individual check results
    """
    # Build quality check prompt
    system_prompt = """You are a transcript quality checker. Evaluate transcripts for accuracy and completeness."""
    
    user_prompt = f"""<task>quality_check</task>

<transcript>
{transcript}
</transcript>

<checklist>
Evaluate this transcript on these criteria. For each, output: PASS / FAIL / WARN

1. Punctuation completeness (sentences end with . ? !)
2. Capitalization correctness (sentence start, proper nouns)
3. No obvious ASR errors (words that don't fit context)
4. [INAUDIBLE] used instead of guessed words
5. Speaker labels consistent (if multi-speaker)
6. No hallucinated content (additions not present in audio)
7. Filler word removal (if verbatim=false)
</checklist>

Output format:
| Check | Result | Note |
|-------|--------|------|
| Punctuation | PASS/FAIL/WARN | brief note |
...

Overall Quality Score: [1-10]
Critical Issues: [list or "None"]"""
    
    provider = get_llm_provider(
        provider_name=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url
    )
    
    logger.info(f"Checking quality with {settings.llm_provider}")
    response = provider.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        max_tokens=2048
    )
    
    # Parse response
    quality_score = extract_quality_score(response)
    critical_issues = extract_critical_issues(response)
    
    # Flag for review if score < 7 or has critical issues
    flag_review = quality_score < 7 or len(critical_issues) > 0
    
    return {
        "quality_score": quality_score,
        "flag_review": flag_review,
        "issues": critical_issues,
        "raw_report": response
    }


def extract_quality_score(response: str) -> int:
    """
    Extract quality score from LLM response.
    
    Args:
        response: LLM response text
        
    Returns:
        Quality score (1-10), defaults to 5 if not found
    """
    # Look for "Overall Quality Score: X"
    match = re.search(r"Overall Quality Score:\s*(\d+)", response, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        return max(1, min(10, score))  # Clamp to 1-10
    
    # Fallback: count PASS/FAIL/WARN
    passes = len(re.findall(r"\bPASS\b", response, re.IGNORECASE))
    fails = len(re.findall(r"\bFAIL\b", response, re.IGNORECASE))
    warns = len(re.findall(r"\bWARN\b", response, re.IGNORECASE))
    
    total = passes + fails + warns
    if total > 0:
        # Score based on pass rate
        pass_rate = passes / total
        return int(pass_rate * 10)
    
    # Default
    return 5


def extract_critical_issues(response: str) -> list:
    """
    Extract critical issues from LLM response.
    
    Args:
        response: LLM response text
        
    Returns:
        List of critical issue strings
    """
    issues = []
    
    # Look for "Critical Issues:" section
    match = re.search(
        r"Critical Issues:\s*(.+?)(?:\n\n|\Z)",
        response,
        re.IGNORECASE | re.DOTALL
    )
    
    if match:
        issues_text = match.group(1).strip()
        if issues_text.lower() not in ["none", "none identified", "n/a"]:
            # Split by newlines or bullets
            for line in issues_text.split("\n"):
                line = line.strip().lstrip("-•*").strip()
                if line:
                    issues.append(line)
    
    return issues


def quick_quality_check(transcript: str) -> Dict[str, Any]:
    """
    Quick heuristic-based quality check (no LLM).
    
    Useful for fast checks without API calls.
    
    Args:
        transcript: Transcript to check
        
    Returns:
        Dict with quality_score and flag_review
    """
    score = 10
    issues = []
    
    # Check 1: Length
    if len(transcript) < 50:
        score -= 3
        issues.append("Transcript too short")
    
    # Check 2: Punctuation
    sentences = re.split(r'[.!?]', transcript)
    if len(sentences) < 2:
        score -= 2
        issues.append("Missing punctuation")
    
    # Check 3: [INAUDIBLE] markers
    inaudible_count = transcript.count("[INAUDIBLE]")
    if inaudible_count > len(transcript) / 200:  # More than 1 per 200 chars
        score -= 2
        issues.append(f"Too many inaudible segments ({inaudible_count})")
    
    # Check 4: Capitalization
    if transcript[0].islower():
        score -= 1
        issues.append("Missing initial capitalization")
    
    # Check 5: Repeated words (ASR error indicator)
    words = transcript.split()
    repeated = sum(1 for i in range(len(words)-1) if words[i] == words[i+1])
    if repeated > len(words) / 50:
        score -= 2
        issues.append("Repeated words detected")
    
    score = max(1, score)
    flag_review = score < 7
    
    return {
        "quality_score": score,
        "flag_review": flag_review,
        "issues": issues,
        "method": "heuristic"
    }
