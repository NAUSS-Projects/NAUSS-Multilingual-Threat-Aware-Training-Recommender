import ollama
import json
import logging
import os
from typing import Dict, List, Optional


class OllamaClient:
    """
    Client for interacting with Ollama models for course recommendations.
    """
    
    def __init__(self, model: Optional[str] = None, host: Optional[str] = None):
        """
        Initialize Ollama client.
        
        Args:
            model (str): Model name to use. If None, reads OLLAMA_MODEL from env (default: 'phi4').
            host (str): Ollama server host. If None, reads OLLAMA_HOST from env (default: 'localhost:11434').
        """
        self.model = model or os.environ.get('OLLAMA_MODEL', 'phi4')
        self.host = host or os.environ.get('OLLAMA_HOST', 'localhost:11434')
        self.client = ollama.Client(host=self.host)
        print(f"[OllamaClient] Using Ollama model: {self.model}")
        print(f"[OllamaClient] Using Ollama host: {self.host}")
        self._verify_model()
    
    def _choose_fallback_model(self, available_models: List[str]) -> Optional[str]:
        """Choose a reasonable fallback chat model from the available list."""
        # Normalize available names to their base (strip tag suffix like :latest)
        base_to_full = {}
        for name in available_models:
            base = name.split(':')[0]
            # Prefer the exact entry with tag for the chosen base
            if base not in base_to_full:
                base_to_full[base] = name
        # Preference order of generally lighter chat-capable models
        preferences = [
            'mistral',
            'llama3.1',
            'llama3',
            'phi4',
        ]
        for pref in preferences:
            if pref in base_to_full:
                return base_to_full[pref]
        # As a last resort, return the first available
        return available_models[0] if available_models else None
    
    def _verify_model(self):
        """Verify that the model is available or pull/fallback if needed."""
        try:
            models_response = self.client.list()
            # Handle both old dict format and new Pydantic model format
            if hasattr(models_response, 'models'):
                models = models_response.models
            else:
                models = models_response.get('models', [])
            
            available_models: List[str] = []
            for m in models:
                if hasattr(m, 'model'):
                    available_models.append(m.model)  # Pydantic model
                else:
                    available_models.append(m.get('name', m.get('model', '')))  # Dict format
            
            # Treat base-name equivalence (e.g., 'phi4' matches 'phi4:latest')
            available_bases = {name.split(':')[0] for name in available_models}
            if self.model not in available_models and self.model.split(':')[0] not in available_bases:
                logging.warning(f"Model {self.model} not found. Available models: {available_models}")
                # Try to pull the requested model
                try:
                    logging.info(f"Attempting to pull model: {self.model}")
                    self.client.pull(self.model)
                    logging.info(f"Successfully pulled model: {self.model}")
                except Exception as e:
                    logging.error(f"Failed to pull model {self.model}: {e}")
                    # Fallback to a reasonable available model
                    fallback = self._choose_fallback_model(available_models)
                    if fallback:
                        self.model = fallback
                        logging.info(f"Using fallback model: {self.model}")
                    else:
                        raise Exception("No Ollama models available")
            else:
                # If only the base matches, prefer the fully-qualified available name
                if self.model not in available_models:
                    # Find the first matching full name with the same base
                    base = self.model.split(':')[0]
                    for name in available_models:
                        if name.split(':')[0] == base:
                            self.model = name
                            break
        except Exception as e:
            logging.error(f"Failed to connect to Ollama: {e}")
            raise Exception(f"Cannot connect to Ollama server at {self.host}")
    
    def _chat(self, prompt: str) -> Dict:
        """Wrapper to call Ollama chat with basic retry on memory errors by falling back."""
        try:
            return self.client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
        except Exception as e:
            msg = str(e)
            logging.error(f"Ollama chat failed for model {self.model}: {msg}")
            # If memory error or general failure, try a fallback once
            try:
                models_response = self.client.list()
                if hasattr(models_response, 'models'):
                    models = models_response.models
                else:
                    models = models_response.get('models', [])
                available_models: List[str] = []
                for m in models:
                    if hasattr(m, 'model'):
                        available_models.append(m.model)
                    else:
                        available_models.append(m.get('name', m.get('model', '')))
                fallback = self._choose_fallback_model(available_models)
                if fallback and fallback != self.model:
                    logging.info(f"Retrying with fallback model: {fallback}")
                    self.model = fallback
                    return self.client.chat(
                        model=self.model,
                        messages=[{'role': 'user', 'content': prompt}]
                    )
            except Exception as e2:
                logging.error(f"Failed to retry with fallback model: {e2}")
            # Re-raise original error after failing fallback
            raise
    
    def generate_course_recommendations(
        self,
        subject_area: str,
        existing_courses: List[str],
        similar_news: List[Dict],
        language: str = 'en',
        max_recommendations: int = 3
    ) -> List[Dict]:
        """
        Generate course recommendations for a subject area based on news similarities.
        
        Args:
            subject_area (str): The subject area name
            existing_courses (list): List of existing course names in this subject
            similar_news (list): List of similar news articles with content
            language (str): Language for recommendations ('en' or 'ar')
            max_recommendations (int): Maximum number of recommendations
            
        Returns:
            list: List of course recommendation dictionaries
        """
        
        # Prepare context
        existing_courses_str = "\n- ".join(existing_courses) if existing_courses else "None"
        
        news_summaries = []
        for news in similar_news[:3]:  # Limit to top 3 most similar
            title = news.get('title', '')
            content = news.get('content', '')[:500]  # Limit content length
            news_summaries.append(f"Title: {title}\nContent: {content}")
        
        news_context = "\n\n".join(news_summaries)
        
        # Create prompt based on language
        if language == 'ar':
            prompt = f"""أنت خبير في التدريب والتطوير المهني. بناءً على الأخبار الحديثة، اقترح دورات تدريبية جديدة أو محدثة.

المجال: {subject_area}

الدورات الموجودة:
- {existing_courses_str}

الأخبار ذات الصلة:
{news_context}

اقترح {max_recommendations} دورات تدريبية جديدة أو محدثة لهذا المجال. لكل اقتراح، قدم:
1. اسم الدورة
2. السبب (كيف يرتبط بالأخبار الحديثة)
3. الحالة (new_course أو outdated_course أو new_subject_area)

الرد يجب أن يكون بصيغة JSON صالحة:
{{
  "recommendations": [
    {{
      "course_name": "اسم الدورة",
      "reason": "السبب والربط بالأخبار",
      "status": "new_course"
    }}
  ]
}}"""
        else:
            prompt = f"""You are an expert in professional training and development. Based on recent news, suggest new or updated training courses.

Subject Area: {subject_area}

Existing Courses:
- {existing_courses_str}

Related Recent News:
{news_context}

Suggest {max_recommendations} new or updated training courses for this subject area. For each suggestion, provide:
1. Course name
2. Reason (how it relates to recent news)
3. Status (new_course, outdated_course, or new_subject_area)

Response must be valid JSON format:
{{
  "recommendations": [
    {{
      "course_name": "Course Name",
      "reason": "Reason and connection to news",
      "status": "new_course"
    }}
  ]
}}"""
        
        try:
            response = self._chat(prompt)
            content = response['message']['content']
            # Try to extract JSON from response
            recommendations = self._extract_json_recommendations(content)
            return recommendations
        except Exception as e:
            logging.error(f"Failed to generate recommendations: {e}")
            return []
    
    def generate_new_subject_recommendations(
        self,
        news_documents: List[Dict],
        existing_subjects: List[str],
        language: str = 'en',
        max_recommendations: int = 2
    ) -> List[Dict]:
        """
        Generate recommendations for entirely new subject areas based on news.
        
        Args:
            news_documents (list): List of news documents
            existing_subjects (list): List of existing subject areas
            language (str): Language for recommendations
            max_recommendations (int): Maximum number of recommendations
            
        Returns:
            list: List of new subject area recommendations
        """
        
        # Prepare news context
        news_summaries = []
        for doc in news_documents[:5]:  # Limit to top 5
            title = doc.get('title', '')
            content = doc.get('content', '')[:300]
            news_summaries.append(f"Title: {title}\nContent: {content}")
        
        news_context = "\n\n".join(news_summaries)
        existing_subjects_str = ", ".join(existing_subjects) if existing_subjects else "None"
        
        # Create prompt based on language
        if language == 'ar':
            prompt = f"""أنت خبير في التدريب والتطوير المهني. بناءً على الأخبار الحديثة، اقترح مجالات موضوع جديدة للتدريب.

المجالات الموجودة: {existing_subjects_str}

الأخبار الحديثة:
{news_context}

اقترح {max_recommendations} مجالات موضوع جديدة للتدريب مستوحاة من هذه الأخبار. لكل اقتراح، قدم:
1. اسم المجال الجديد
2. السبب (كيف يرتبط بالأخبار)
3. دورة تدريبية مقترحة لهذا المجال

الرد يجب أن يكون بصيغة JSON صالحة:
{{
  "new_subjects": [
    {{
      "subject_name": "اسم المجال الجديد",
      "reason": "السبب والربط بالأخبار",
      "suggested_course": "دورة تدريبية مقترحة"
    }}
  ]
}}"""
        else:
            prompt = f"""You are an expert in professional training and development. Based on recent news, suggest new subject areas for training.

Existing Subject Areas: {existing_subjects_str}

Recent News:
{news_context}

Suggest {max_recommendations} new training subject areas inspired by this news. For each suggestion, provide:
1. New subject area name
2. Reason (how it relates to the news)
3. A suggested course for this subject area

Response must be valid JSON format:
{{
  "new_subjects": [
    {{
      "subject_name": "New Subject Area Name",
      "reason": "Reason and connection to news",
      "suggested_course": "Suggested Course Name"
    }}
  ]
}}"""
        print(language)
        print(prompt)
        try:
            response = self._chat(prompt)
            content = response['message']['content']
            # Try to extract JSON from response
            new_subjects = self._extract_json_new_subjects(content)
            return new_subjects
        except Exception as e:
            logging.error(f"Failed to generate new subject recommendations: {e}")
            return []
    
    def _extract_json_recommendations(self, content: str) -> List[Dict]:
        """Extract recommendations from JSON response."""
        try:
            # Try to find JSON in the content
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                return data.get('recommendations', [])
            
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse manually
        return []
    
    def _extract_json_new_subjects(self, content: str) -> List[Dict]:
        """Extract new subjects from JSON response."""
        try:
            # Try to find JSON in the content
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                return data.get('new_subjects', [])
            
        except json.JSONDecodeError:
            pass
        
        # Fallback: parse manually
        return []
