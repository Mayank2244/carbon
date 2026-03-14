"""
Prompt Optimizer Core Logic.
Implements Semantic Compression, Template Matching, Context Pruning, and Dynamic Verbosity.
"""

import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from app.modules.prompt_optimizer.templates import TEMPLATES, PATTERN_MATCHERS
from app.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class OptimizedPrompt:
    """Result of optimization process."""
    text: str
    tokens: int
    original_tokens: int
    compression_ratio: float
    technique_used: str

class PromptOptimizer:
    """
    Intelligent engine for reducing token usage and optimizing AI prompts.

    Implements several techniques to compress prompts without losing semantic
    meaning, including filler word removal, template matching, and context
    pruning.

    Attributes:
        templates (dict): Structured response templates for specific query types.
        matchers (dict): Regex patterns for detecting query templates.
        total_tokens_saved (int): Cumulative counter for token savings.
    """
    
    UNNECESSARY_PHRASES = [
        "You are a helpful assistant", "You are an AI", "Please provide", 
        "I would like you to", "Can you please", "Could you", "Thank you for", 
        "I need help with", "I want to know", "Make sure to", "Please"
    ]
    
    def __init__(self):
        self.templates = TEMPLATES
        self.matchers = PATTERN_MATCHERS
        self.total_tokens_saved = 0
        
    def optimize(self, prompt: str, context: List[Dict[str, Any]], query_metadata: Dict[str, Any]) -> OptimizedPrompt:
        """
        Executes the full prompt optimization pipeline.

        Args:
            prompt (str): The original user prompt.
            context (List[Dict[str, Any]]): Conversation history/context.
            query_metadata (Dict[str, Any]): Metadata including complexity and carbon budget.

        Returns:
            OptimizedPrompt: A structured object containing the rewritten prompt and
                efficiency metrics.
        """
        original_tokens = self._estimate_tokens(prompt + str(context))
        
        # Step 1: Semantic Compression
        compressed_text = self.compress_semantic(prompt)
        technique = "semantic"
        
        # Step 2: Template Matching
        technique = "semantic"
        if original_tokens > 15:
            template_text = self.try_template_compression(compressed_text)
            if template_text:
                compressed_text = template_text
                technique = "template"
            
        # Step 3: Context Pruning
        pruned_context = self.prune_context(context, max_tokens=200) if context else ""
        
        # Step 4: Dynamic Verbosity
        verbosity_instruction = ""
        if original_tokens > 25:
            verbosity_instruction = self.set_verbosity_level(
                query_metadata.get('complexity', 'MEDIUM'),
                query_metadata.get('carbon_budget', 100.0)
            )
        
        # Combine
        final_prompt = f"{compressed_text}\n{verbosity_instruction}" if verbosity_instruction else compressed_text
        if pruned_context:
            final_prompt = f"Context:\n{pruned_context}\n\nTask:\n{final_prompt}"
            
        final_tokens = self._estimate_tokens(final_prompt)
        ratio = 1.0 - (final_tokens / original_tokens) if original_tokens > 0 else 0.0
        
        saved = max(0, original_tokens - final_tokens)
        self.total_tokens_saved += saved
        
        logger.info(f"Prompt optimized: {ratio:.1%} reduction ({technique}). Saved {saved} tokens.")
        
        return OptimizedPrompt(
            text=final_prompt,
            tokens=final_tokens,
            original_tokens=original_tokens,
            compression_ratio=ratio,
            technique_used=technique
        )
    
    def compress_semantic(self, prompt: str) -> str:
        """
        Removes unnecessary politeness, filler words, and redundant whitespace.

        Args:
            prompt (str): The raw text to compress.

        Returns:
            str: The semantically compressed text.
        """
        compressed = prompt
        for phrase in self.UNNECESSARY_PHRASES:
            # Case insensitive replacement
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            compressed = pattern.sub("", compressed)
        
        # Remove redundant spaces
        compressed = " ".join(compressed.split())
        return compressed

    def try_template_compression(self, prompt: str) -> Optional[str]:
        """
        Attempts to map natural language queries to predefined structured templates.

        Args:
            prompt (str): The query text.

        Returns:
            Optional[str]: The formatted template string if a match is found, else None.
        """
        for pattern, template_key in self.matchers.items():
            match = re.search(pattern, prompt)
            if match:
                groups = match.groups()
                template = self.templates[template_key]
                
                # Naive slot filling based on captured groups
                # Only works if template slots match group order/count
                # This is a simplification; robust slot filling requires NER
                
                # Check known mappings
                if template_key == 'definition':
                    return template.format(topic=groups[1].strip(), level="simple")
                elif template_key == 'explanation':
                    return template.format(topic=groups[1].strip(), words=100)
                elif template_key == 'comparison':
                    return template.format(item1=groups[1].strip(), item2=groups[2].strip(), aspect="general")
                elif template_key == 'translation':
                    return template.format(text=groups[1].strip(), lang=groups[3].strip())
                elif template_key == 'code_snippet':
                    return template.format(task=groups[3].strip(), lang=groups[1].strip())
        return None

    def prune_context(self, conversation_history: List[Dict[str, Any]], max_tokens: int = 500) -> str:
        """
        Filters conversation history to fit within a specific token budget.

        Prioritizes most recent messages.

        Args:
            conversation_history (List[Dict[str, Any]]): Full history list.
            max_tokens (int): Maximum tokens allowed for context.

        Returns:
            str: A formatted string of the most relevant context.
        """
        pruned = []
        current_tokens = 0
        
        # Reverse to prioritize recent
        for msg in reversed(conversation_history):
            content = msg.get('content', '') or msg.get('text', '')
            role = msg.get('role', 'user')
            
            tokens = self._estimate_tokens(content)
            if current_tokens + tokens <= max_tokens:
                pruned.insert(0, f"{role}: {content}")
                current_tokens += tokens
            else:
                break
                
        return "\n".join(pruned)

    def set_verbosity_level(self, query_complexity: str, carbon_budget: float) -> str:
        """
        Inserts instructions to adjust the AI's response length based on metrics.

        Args:
            query_complexity (str): Complexity level (SIMPLE, MEDIUM, COMPLEX).
            carbon_budget (float): Remaining carbon budget for the query.

        Returns:
            str: A natural language instruction for the LLM.
        """
        if carbon_budget < 10:  # Critical budget
            return "Please provide a very concise answer (1-2 sentences)."
        elif str(query_complexity).upper() == 'SIMPLE':
            return "Please provide a brief, direct answer."
        elif str(query_complexity).upper() == 'MEDIUM':
            return "Please provide a clear and conversational explanation."
        else:
            return "Please provide a detailed and comprehensive answer."

    def _estimate_tokens(self, text: str) -> int:
        """Simple heuristic estimation (avg 4 chars/token)."""
        return len(text) // 4
