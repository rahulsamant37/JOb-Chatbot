from typing import List, Optional, TypedDict, Literal, Tuple, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.models import RefinedQuery
import spacy
import re

class QueryProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.job_related_terms = {
            'job', 'career', 'position', 'opportunity', 'vacancy', 'opening',
            'work', 'employment', 'role', 'developer', 'engineer', 'manager',
            'analyst', 'designer', 'consultant', 'specialist', 'coordinator',
            'associate', 'lead', 'senior', 'junior', 'mid', 'principal'
        }
        
        self.conversational_prefixes = [
            "i'm", "i am", "looking for", "show me", "find me", "searching for",
            "need", "want", "some", "please", "help me find", "can you find",
            "interested in", "seeking", "hunting for"
        ]
        
        self.experience_levels = {
            'entry level': 'entry',
            'junior': 'junior',
            'mid': 'mid-level',
            'senior': 'senior',
            'lead': 'senior',
            'principal': 'senior',
            'staff': 'senior'
        }
        
        self.job_title_patterns = [
            r'(?i)((?:senior|junior|lead|principal|staff)?\s*(?:software|python|java|frontend|backend|fullstack|full stack|web)?\s*(?:developer|engineer|architect|programmer))',
            r'(?i)((?:data|machine learning|ml|ai|devops|cloud|security)\s*(?:engineer|scientist|analyst|architect))',
            r'(?i)((?:product|project|program)\s*(?:manager|lead|owner))',
            r'(?i)((?:ux|ui|user experience|user interface)\s*(?:designer|researcher))',
            r'(?i)((?:business|systems|data)\s*(?:analyst|consultant))',
            r'(?i)((?:marketing|sales|account)\s*(?:manager|executive|representative))'
        ]
        
        self.tech_skills = {
            'python', 'java', 'javascript', 'react', 'node', 'aws', 'sql',
            'typescript', 'golang', 'ruby', 'c++', 'rust', 'scala', 'docker',
            'kubernetes', 'angular', 'vue', 'django', 'flask', 'spring',
            'devops', 'ci/cd', 'azure', 'gcp'
        }

    def is_job_related_query(self, text: str) -> bool:
        """Determine if the query is job-related"""
        text_lower = text.lower()
        # Process the text with spaCy to use lemmatization (catches plural and variant forms)
        doc = self.nlp(text_lower)
        words = {token.lemma_ for token in doc}
        if any(term in words for term in self.job_related_terms):
            return True

        if any(re.search(pattern, text_lower) for pattern in self.job_title_patterns):
            return True
        if any(prefix in text_lower for prefix in self.conversational_prefixes):
            return True
            
        return False

    def extract_location(self, doc) -> Optional[str]:
        """Extract location from spaCy doc using named entity recognition"""
        locations = []
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:
                locations.append(ent.text)
        
        return ' '.join(locations) if locations else None

    def clean_conversational_query(self, query: str) -> str:
        """Remove conversational elements from the query"""
        cleaned = query.lower()
        for prefix in self.conversational_prefixes:
            cleaned = cleaned.replace(prefix, "")
        filler_words = ['a', 'an', 'the', 'for', 'about', 'related', 'to']
        cleaned = ' '.join(word for word in cleaned.split() if word not in filler_words)
        
        return cleaned.strip()

    def process_query(self, query: str) -> RefinedQuery:
        """Process and validate the query"""
        is_job_related = self.is_job_related_query(query)
        
        if not is_job_related:
            return RefinedQuery(
                original_query=query,
                refined_query="",
                is_job_related=False
            )
        cleaned_query = self.clean_conversational_query(query)
        doc = self.nlp(cleaned_query)
        job_title = None
        location = None
        experience_level = None
        
        for pattern in self.job_title_patterns:
            match = re.search(pattern, cleaned_query)
            if match:
                job_title = match.group(1).strip()
                break
        
        location = self.extract_location(doc)
        
        for level, normalized in self.experience_levels.items():
            if level in cleaned_query:
                experience_level = normalized
                break
        query_parts = []
        if experience_level:
            query_parts.append(experience_level)
        if job_title:
            query_parts.append(job_title)
        if location:
            query_parts.extend(['in', location])
        
        refined_query = ' '.join(query_parts).strip()
        
        return RefinedQuery(
            original_query=query,
            refined_query=refined_query or cleaned_query,
            is_job_related=True,
            job_title=job_title,
            location=location,
            experience_level=experience_level
        )

def create_query_processor():
    return QueryProcessor()
