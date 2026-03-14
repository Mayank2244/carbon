"""
Prompt Templates Library.
Optimized patterns for compressing user intents into minimal tokens.
"""

from typing import Dict

# Map of high-level intents to template strings
TEMPLATES: Dict[str, str] = {
    # Definitions & Explanations
    'definition': 'Briefly answer or define: {topic} ({level}).',
    'explanation': 'Explain: {topic} (max {words} words).',
    'simple_explanation': 'Explain like I\'m 5: {topic}.',
    'analogy': 'Analogy for {topic} using {concept}.',
    
    # Comparisons
    'comparison': 'Compare: {item1} vs {item2} (focus: {aspect}).',
    'pros_cons': 'Pros/Cons: {topic}.',
    'difference': 'Difference between: {item1} and {item2}.',
    
    # Coding
    'code_function': 'Write function: {name} (lang: {lang}) args: {args} -> {desc}.',
    'code_snippet': 'Code snippet: {task} (lang: {lang}).',
    'code_debug': 'Debug: {error} in {lang}.',
    'code_convert': 'Convert code: {source_lang} -> {target_lang}.',
    'regex': 'Regex pattern for: {pattern_desc}.',
    'sql_query': 'SQL: {goal} (tables: {tables}). Format: SQL Code Block.',
    
    # Writing & Editing
    'summarize': 'Summarize: {topic} (max {words} words)',
    'headline': 'Headline: {topic} (style: {style})',
    'parameters': 'Extract params: {text}',
    'grammar': 'Fix grammar: {text}',
    'rewrite': 'Rewrite: {text} (tone: {tone})',
    'email': 'Email to: {recipient} re: {topic} (tone: {tone})',
    
    # Data & Lists
    'list': 'List {count} {item_type} for {topic}',
    'json_format': 'Format as JSON: {keys}',
    'csv_format': 'Format as CSV: {columns}',
    'extract_data': 'Extract entity: {entity_type} from {text}',
    
    # Business & formatting
    'meeting_agenda': 'Agenda: {topic} (duration: {time})',
    'pros_cons_table': 'Table: Pros vs Cons of {topic}',
    'timeline': 'Timeline: {event}',
    
    # Creative
    'story': 'Story: {topic} (genre: {genre})',
    'poem': 'Poem: {topic} (style: {style})',
    'joke': 'Joke about: {topic}',
    
    # Learning
    'quiz': 'Quiz: {topic} ({num_questions} questions)',
    'study_plan': 'Study plan: {topic} ({duration})',
    'key_points': 'Key points: {topic}',
    
    # Technical
    'cli_command': 'CLI: {task} (os: {os})',
    'git_command': 'Git: {task}',
    'docker_file': 'Dockerfile: {stack}',
    'algo_complexity': 'Time/Space complexity: {algorithm}',
    
    # Generic Helpers
    'steps': 'Steps to: {goal}',
    'history': 'History: {event}',
    'translation': 'Translate: {text} -> {lang}',
    'synonyms': 'Synonyms for: {word}',
    'antonyms': 'Antonyms for: {word}',
    'example': 'Example of: {concept}',
    'critique': 'Critique: {text}',
    'brainstorm': 'Ideas for: {topic}',
    'analyze': 'Analyze: {topic}'
}

# Regex patterns to detect intent from raw text
PATTERN_MATCHERS = {
    r"(?i)^(what is|define|meaning of)\s+(.+)": "definition",
    r"(?i)^(explain|how does)\s+(.+)\s+(work|mean)": "explanation",
    r"(?i)^(write|create|generate)\s+(python|java|js|code)\s+(for|to)\s+(.+)": "code_snippet",
    r"(?i)^(compare|difference between)\s+(.+)\s+and\s+(.+)": "comparison",
    r"(?i)^(summarise|summarize)\s+(.+)": "summarize",
    r"(?i)^(translate)\s+(.+)\s+(to|into)\s+(.+)": "translation",
    r"(?i)^(fix|correct)\s+(grammar|spelling)\s+in\s+(.+)": "grammar",
    r"(?i)^(list|give me)\s+(\d+)\s+(.+)": "list"
}
