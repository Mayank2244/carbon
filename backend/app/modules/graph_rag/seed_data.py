"""
Neo4j Seed Data Script
Populates the knowledge graph with initial tech concepts.
"""

SEED_DATA_STATEMENTS = [
    # Clear existing data
    "MATCH (n) DETACH DELETE n",

    # Create Core Concepts
    "CREATE (ai:Concept {name: 'Artificial Intelligence', definition: 'The simulation of human intelligence by machines', domain: 'Computer Science'})",
    "CREATE (ml:Concept {name: 'Machine Learning', definition: 'A subset of AI that learns from data without explicit programming', domain: 'Computer Science'})",
    "CREATE (dl:Concept {name: 'Deep Learning', definition: 'ML using neural networks with multiple layers', domain: 'Computer Science'})",
    "CREATE (nlp:Concept {name: 'Natural Language Processing', definition: 'AI for understanding and generating human language', domain: 'Computer Science'})",
    "CREATE (cv:Concept {name: 'Computer Vision', definition: 'AI for interpreting visual information', domain: 'Computer Science'})",

    # Create Techniques
    "CREATE (nn:Technique {name: 'Neural Networks', description: 'Computing systems inspired by biological neural networks'})",
    "CREATE (cnn:Technique {name: 'Convolutional Neural Networks', description: 'Neural networks specialized for processing grid-like data'})",
    "CREATE (rnn:Technique {name: 'Recurrent Neural Networks', description: 'Neural networks for sequential data'})",
    "CREATE (transformer:Technique {name: 'Transformers', description: 'Attention-based neural network architecture'})",

    # Create Domains
    "CREATE (tech:Domain {name: 'Technology'})",
    "CREATE (science:Domain {name: 'Science'})",
    "CREATE (business:Domain {name: 'Business'})",

    # Create Resources
    "CREATE (data:Resource {name: 'Training Data', type: 'Dataset'})",
    "CREATE (gpu:Resource {name: 'GPU', type: 'Hardware'})",
    "CREATE (python:Resource {name: 'Python', type: 'Programming Language'})",

    # Create Relationships
    "MATCH (ml:Concept {name: 'Machine Learning'}), (ai:Concept {name: 'Artificial Intelligence'}) CREATE (ml)-[:IS_A]->(ai)",
    "MATCH (dl:Concept {name: 'Deep Learning'}), (ml:Concept {name: 'Machine Learning'}) CREATE (dl)-[:IS_A]->(ml)",
    "MATCH (nlp:Concept {name: 'Natural Language Processing'}), (ai:Concept {name: 'Artificial Intelligence'}) CREATE (nlp)-[:IS_A]->(ai)",
    "MATCH (cv:Concept {name: 'Computer Vision'}), (ai:Concept {name: 'Artificial Intelligence'}) CREATE (cv)-[:IS_A]->(ai)",

    "MATCH (dl:Concept {name: 'Deep Learning'}), (nn:Technique {name: 'Neural Networks'}) CREATE (dl)-[:USES]->(nn)",
    "MATCH (cv:Concept {name: 'Computer Vision'}), (cnn:Technique {name: 'Convolutional Neural Networks'}) CREATE (cv)-[:USES]->(cnn)",
    "MATCH (nlp:Concept {name: 'Natural Language Processing'}), (transformer:Technique {name: 'Transformers'}) CREATE (nlp)-[:USES]->(transformer)",

    "MATCH (ml:Concept {name: 'Machine Learning'}), (data:Resource {name: 'Training Data'}) CREATE (ml)-[:REQUIRES]->(data)",
    "MATCH (dl:Concept {name: 'Deep Learning'}), (gpu:Resource {name: 'GPU'}) CREATE (dl)-[:REQUIRES]->(gpu)",
    "MATCH (ml:Concept {name: 'Machine Learning'}), (python:Resource {name: 'Python'}) CREATE (ml)-[:USES]->(python)",

    "MATCH (ai:Concept {name: 'Artificial Intelligence'}), (tech:Domain {name: 'Technology'}) CREATE (ai)-[:APPLIED_IN]->(tech)",
    "MATCH (ml:Concept {name: 'Machine Learning'}), (business:Domain {name: 'Business'}) CREATE (ml)-[:APPLIED_IN]->(business)",
    "MATCH (dl:Concept {name: 'Deep Learning'}), (science:Domain {name: 'Science'}) CREATE (dl)-[:APPLIED_IN]->(science)",

    # Python Ecosystem
    "CREATE (django:Concept {name: 'Django', definition: 'High-level Python web framework', domain: 'Web Development'})",
    "CREATE (flask:Concept {name: 'Flask', definition: 'Lightweight Python web framework', domain: 'Web Development'})",
    "CREATE (fastapi:Concept {name: 'FastAPI', definition: 'Modern, fast Python web framework', domain: 'Web Development'})",
    "CREATE (pandas:Concept {name: 'Pandas', definition: 'Data manipulation library for Python', domain: 'Data Science'})",
    "CREATE (numpy:Concept {name: 'NumPy', definition: 'Numerical computing library for Python', domain: 'Data Science'})",

    "MATCH (django:Concept {name: 'Django'}), (python:Resource {name: 'Python'}) CREATE (django)-[:USES]->(python)",
    "MATCH (flask:Concept {name: 'Flask'}), (python:Resource {name: 'Python'}) CREATE (flask)-[:USES]->(python)",
    "MATCH (fastapi:Concept {name: 'FastAPI'}), (python:Resource {name: 'Python'}) CREATE (fastapi)-[:USES]->(python)",
    "MATCH (pandas:Concept {name: 'Pandas'}), (numpy:Concept {name: 'NumPy'}) CREATE (pandas)-[:USES]->(numpy)",
    "MATCH (ml:Concept {name: 'Machine Learning'}), (pandas:Concept {name: 'Pandas'}) CREATE (ml)-[:USES]->(pandas)",

    # APIs and Web
    "CREATE (rest:Concept {name: 'REST API', definition: 'Representational State Transfer API architecture', domain: 'Web Development'})",
    "CREATE (graphql:Concept {name: 'GraphQL', definition: 'Query language for APIs', domain: 'Web Development'})",
    "CREATE (http:Concept {name: 'HTTP', definition: 'Hypertext Transfer Protocol', domain: 'Networking'})",

    "MATCH (rest:Concept {name: 'REST API'}), (http:Concept {name: 'HTTP'}) CREATE (rest)-[:USES]->(http)",
    "MATCH (graphql:Concept {name: 'GraphQL'}), (http:Concept {name: 'HTTP'}) CREATE (graphql)-[:USES]->(http)",
    "MATCH (fastapi:Concept {name: 'FastAPI'}), (rest:Concept {name: 'REST API'}) CREATE (fastapi)-[:SUPPORTS]->(rest)",

    # Databases
    "CREATE (postgres:Concept {name: 'PostgreSQL', definition: 'Open-source relational database', domain: 'Databases'})",
    "CREATE (redis:Concept {name: 'Redis', definition: 'In-memory data structure store', domain: 'Databases'})",
    "CREATE (neo4j:Concept {name: 'Neo4j', definition: 'Graph database management system', domain: 'Databases'})",

    "MATCH (django:Concept {name: 'Django'}), (postgres:Concept {name: 'PostgreSQL'}) CREATE (django)-[:USES]->(postgres)",
    "MATCH (fastapi:Concept {name: 'FastAPI'}), (redis:Concept {name: 'Redis'}) CREATE (fastapi)-[:USES]->(redis)",

    # Cloud & DevOps
    "CREATE (docker:Concept {name: 'Docker', definition: 'Platform for containerizing applications', domain: 'DevOps'})",
    "CREATE (k8s:Concept {name: 'Kubernetes', definition: 'Container orchestration platform', domain: 'DevOps'})",
    "CREATE (aws:Concept {name: 'AWS', definition: 'Amazon Web Services cloud platform', domain: 'Cloud Computing'})",

    "MATCH (k8s:Concept {name: 'Kubernetes'}), (docker:Concept {name: 'Docker'}) CREATE (k8s)-[:USES]->(docker)",
    "MATCH (fastapi:Concept {name: 'FastAPI'}), (docker:Concept {name: 'Docker'}) CREATE (fastapi)-[:DEPLOYED_ON]->(docker)"
]
