# =============================================================================
#  Filename: validation_keywords.py
#
#  Short Description: Central configuration for validation keywords
#
#  Creation date: 2025-10-10
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Validation Keywords Configuration

Central location for all keywords used across agents for:
- Reflection detection
- Follow-up question detection
- User satisfaction assessment
- Supervisor escalation triggers
"""

from typing import List


class ValidationKeywords:
    """Central repository for all validation keywords used in the system."""
    
    # =========================================================================
    # Reflection Trigger Keywords
    # =========================================================================
    
    REFLECTION_KEYWORDS: List[str] = [
        # Verification requests
        "is this right",
        "are you sure",
        "is this correct",
        "is that right",
        "can you verify",
        "verify this",
        
        # Double-checking
        "double check",
        "check this",
        "confirm this",
        "confirm that",
        
        # Uncertainty
        "certain",
        "positive",
        "sure about",
    ]
    
    # =========================================================================
    # Follow-Up Question Keywords
    # =========================================================================
    
    FOLLOW_UP_KEYWORDS: List[str] = [
        # Verification questions (overlap with reflection)
        "is this right",
        "are you sure",
        "is this correct",
        "is that right",
        "can you verify",
        "verify this",
        "double check",
        "confirm this",
        "check this",
        
        # Uncertainty expressions
        "i'm not sure",
        "not sure about",
        "unsure",
        
        # Dissatisfaction
        "not satisfied",
        "doesn't seem right",
        "seems wrong",
        "that's not",
        "this isn't",
        
        # Reconsideration
        "but",
        "however",
        "actually",
        "wait",
        "hold on",
        "reconsider",
        "think again",
        
        # Direct contradiction
        "wrong",
        "incorrect",
        "mistake",
    ]
    
    # Referential words indicating follow-up
    REFERENTIAL_WORDS: List[str] = [
        "this",
        "that",
        "it",
        "these",
        "those"
    ]
    
    # =========================================================================
    # User Satisfaction Keywords
    # =========================================================================
    
    # Dissatisfied user keywords
    DISSATISFIED_KEYWORDS: List[str] = [
        "not satisfied",
        "not happy",
        "unhappy",
        "wrong",
        "incorrect",
        "doesn't seem right",
        "that's not",
        "this isn't",
        "seems wrong",
        "not what i",
        "disappointed",
        "unacceptable",
        "no way",
        "can't be",
        "impossible",
        "not right",
        "this can't be",
        "too expensive",
        "too high",
        "too much",
    ]
    
    # Unsure/verification keywords
    UNSURE_KEYWORDS: List[str] = [
        "are you sure",
        "is this right",
        "is this correct",
        "can you verify",
        "double check",
        "confirm",
        "certain",
        "positive",
        "sure about",
        "really",
        "truly",
        "actually correct",
    ]
    
    # Satisfied keywords (for future use)
    SATISFIED_KEYWORDS: List[str] = [
        "perfect",
        "great",
        "excellent",
        "thank you",
        "thanks",
        "that's good",
        "sounds good",
        "looks good",
        "okay",
        "ok",
        "fine",
        "good",
    ]
    
    # =========================================================================
    # Supervisor Trigger Keywords
    # =========================================================================
    
    SUPERVISOR_KEYWORDS: List[str] = [
        "supervisor",
        "manager",
        "escalate",
        "speak to supervisor",
        "talk to manager",
        "need help",
        "human",
        "person",
        "representative",
    ]
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    @classmethod
    def is_reflection_request(cls, text: str) -> bool:
        """
        Check if text contains reflection keywords.
        
        Args:
            text: User input text
            
        Returns:
            True if reflection keywords detected
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in cls.REFLECTION_KEYWORDS)
    
    @classmethod
    def is_follow_up(cls, text: str, has_previous_context: bool = False) -> bool:
        """
        Check if text is a follow-up question.
        
        Args:
            text: User input text
            has_previous_context: Whether there's a previous recommendation
            
        Returns:
            True if this appears to be a follow-up
        """
        if not has_previous_context:
            return False
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Check for follow-up keywords
        has_follow_up_keyword = any(
            keyword in text_lower for keyword in cls.FOLLOW_UP_KEYWORDS
        )
        
        # Check for referential words
        has_referential = any(
            word in words for word in cls.REFERENTIAL_WORDS
        )
        
        # Short questions with pronouns are likely follow-ups
        is_short = len(words) < 10
        
        return has_follow_up_keyword or (has_referential and is_short)
    
    @classmethod
    def assess_satisfaction(cls, text: str) -> str:
        """
        Assess user satisfaction from text.
        
        Args:
            text: User input text
            
        Returns:
            "satisfied", "unsure", "dissatisfied", or "unknown"
        """
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in cls.DISSATISFIED_KEYWORDS):
            return "dissatisfied"
        elif any(keyword in text_lower for keyword in cls.UNSURE_KEYWORDS):
            return "unsure"
        elif any(keyword in text_lower for keyword in cls.SATISFIED_KEYWORDS):
            return "satisfied"
        else:
            return "unknown"
    
    @classmethod
    def needs_supervisor(cls, text: str) -> bool:
        """
        Check if text explicitly requests supervisor.
        
        Args:
            text: User input text
            
        Returns:
            True if supervisor keywords detected
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in cls.SUPERVISOR_KEYWORDS)


# Convenience functions for backward compatibility
def is_reflection_request(text: str) -> bool:
    """Check if text requests reflection."""
    return ValidationKeywords.is_reflection_request(text)


def is_follow_up_question(text: str, has_context: bool = False) -> bool:
    """Check if text is a follow-up question."""
    return ValidationKeywords.is_follow_up(text, has_context)


def assess_user_satisfaction(text: str) -> str:
    """Assess user satisfaction level."""
    return ValidationKeywords.assess_satisfaction(text)


def needs_supervisor_escalation(text: str) -> bool:
    """Check if supervisor is explicitly requested."""
    return ValidationKeywords.needs_supervisor(text)

