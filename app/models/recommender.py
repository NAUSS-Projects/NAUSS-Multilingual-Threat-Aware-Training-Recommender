import logging
from .ollama_client import OllamaClient
from .excel import get_unique_subjects_and_courses
from datetime import datetime, timedelta


class Recommender:
    """
    Main recommendation engine that orchestrates the process.
    """
    
    def __init__(self, similarity_threshold=0.3):
        """
        Initialize the recommender.
        
        Args:
            similarity_threshold (float): Minimum similarity threshold for matches
        """
        self.similarity_threshold = similarity_threshold
        self.ollama_client = None
        self._init_ollama_client()
    
    def _init_ollama_client(self):
        """Initialize Ollama client with error handling."""
        try:
            self.ollama_client = OllamaClient()
        except Exception as e:
            logging.error(f"Failed to initialize Ollama client: {e}")
            self.ollama_client = None
    
    def generate_recommendations(self, user_data, news_documents, similarity_engine):
        """
        Generate comprehensive recommendations based on user data and news.
        
        Args:
            user_data (dict): Parsed Excel data with subjects and courses
            news_documents (list): List of processed news documents
            similarity_engine: Initialized SimilarityEngine instance
            
        Returns:
            list: List of recommendation dictionaries in the required format
        """
        if not news_documents:
            return []
        
        recommendations = []
        
        # Get user language and subjects
        primary_language = user_data.get('primary_language', 'en')
        print("test",primary_language)
        subjects, all_courses = get_unique_subjects_and_courses(user_data)
        
        # Find similarities between subjects and news
        subject_news_similarities = similarity_engine.get_subject_news_similarities(
            subjects, news_documents, self.similarity_threshold
        )
        
        # Process subjects with similarities (existing subjects with related news)
        for subject, similarity_info in subject_news_similarities.items():
            subject_courses = [course['name'] for course in all_courses if course['subject'] == subject]
            
            # Get matching news documents
            similar_news = []
            for match in similarity_info['matches']:
                news_index = match['index']
                if news_index < len(news_documents):
                    similar_news.append(news_documents[news_index])
            
            # Generate course recommendations using Ollama
            if self.ollama_client and similar_news:
                try:
                    course_recs = self.ollama_client.generate_course_recommendations(
                        subject_area=subject,
                        existing_courses=subject_courses,
                        similar_news=similar_news,
                        language=primary_language,
                        max_recommendations=3
                    )
                    
                    if course_recs:
                        # Format recommendations
                        suggested_courses = []
                        for rec in course_recs:
                            suggested_courses.append({
                                "course_name": rec.get('course_name', ''),
                                "reason": rec.get('reason', ''),
                                "status": rec.get('status', 'new_course')
                            })
                        
                        if suggested_courses:
                            recommendations.append({
                                "subject_area": subject,
                                "suggested_courses": suggested_courses
                            })
                
                except Exception as e:
                    logging.error(f"Failed to generate recommendations for {subject}: {e}")
        
        # Generate new subject areas for news without matches
        unmatched_news = self._find_unmatched_news(news_documents, subject_news_similarities)
        
        if unmatched_news and self.ollama_client:
            try:
                new_subject_recs = self.ollama_client.generate_new_subject_recommendations(
                    news_documents=unmatched_news,
                    existing_subjects=subjects,
                    language=primary_language,
                    max_recommendations=4
                )
                
                for new_subject in new_subject_recs:
                    subject_name = new_subject.get('subject_name', '')
                    reason = new_subject.get('reason', '')
                    suggested_course = new_subject.get('suggested_course', '')
                    
                    if subject_name and suggested_course:
                        recommendations.append({
                            "subject_area": subject_name,
                            "suggested_courses": [{
                                "course_name": suggested_course,
                                "reason": reason,
                                "status": "new_subject_area"
                            }]
                        })
            
            except Exception as e:
                logging.error(f"Failed to generate new subject recommendations: {e}")
        
        return recommendations
    
    def _find_unmatched_news(self, news_documents, subject_similarities):
        """
        Find news documents that didn't match any existing subjects.
        
        Args:
            news_documents (list): All news documents
            subject_similarities (dict): Subject similarity results
            
        Returns:
            list: News documents without matches
        """
        matched_indices = set()
        
        # Collect all matched news indices
        for subject, similarity_info in subject_similarities.items():
            for match in similarity_info['matches']:
                matched_indices.add(match['index'])
        
        # Return unmatched news
        unmatched_news = []
        for i, doc in enumerate(news_documents):
            if i not in matched_indices:
                unmatched_news.append(doc)
        
        return unmatched_news
    
    def _is_course_outdated(self, course_info, months_threshold=12):
        """
        Check if a course is outdated based on its end date.
        
        Args:
            course_info (dict): Course information with dates
            months_threshold (int): Number of months to consider as outdated
            
        Returns:
            bool: True if course is outdated
        """
        if not course_info.get('end_date'):
            return False
        
        try:
            end_date = course_info['end_date']
            if isinstance(end_date, str):
                # Try to parse date string (basic parsing)
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            threshold_date = datetime.now() - timedelta(days=months_threshold * 30)
            return end_date < threshold_date
            
        except (ValueError, TypeError):
            return False
    
    def get_recommendation_summary(self, recommendations):
        """
        Generate a summary of recommendations.
        
        Args:
            recommendations (list): List of recommendations
            
        Returns:
            dict: Summary statistics
        """
        if not recommendations:
            return {
                "total_recommendations": 0,
                "subjects_with_recommendations": 0,
                "new_courses": 0,
                "outdated_courses": 0,
                "new_subject_areas": 0
            }
        
        total_courses = 0
        new_courses = 0
        outdated_courses = 0
        new_subject_areas = 0
        
        for rec in recommendations:
            courses = rec.get('suggested_courses', [])
            total_courses += len(courses)
            
            for course in courses:
                status = course.get('status', '')
                if status == 'new_course':
                    new_courses += 1
                elif status == 'outdated_course':
                    outdated_courses += 1
                elif status == 'new_subject_area':
                    new_subject_areas += 1
        
        return {
            "total_recommendations": total_courses,
            "subjects_with_recommendations": len(recommendations),
            "new_courses": new_courses,
            "outdated_courses": outdated_courses,
            "new_subject_areas": new_subject_areas
        }