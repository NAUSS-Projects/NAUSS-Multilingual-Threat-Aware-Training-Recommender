from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging


class SimilarityEngine:
    """
    Multilingual similarity engine using sentence transformers.
    Supports cross-lingual semantic similarity between Arabic and English.
    """
    
    def __init__(self, model_name='sentence-transformers/LaBSE'):
        """
        Initialize the similarity engine.
        LaBSE (Language-agnostic BERT Sentence Embedding) is good for multilingual tasks.
        Alternative models: 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logging.info(f"Loading multilingual model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logging.info("Model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load model {self.model_name}: {e}")
            # Fallback to a smaller model
            try:
                fallback_model = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
                logging.info(f"Trying fallback model: {fallback_model}")
                self.model = SentenceTransformer(fallback_model)
                self.model_name = fallback_model
                logging.info("Fallback model loaded successfully")
            except Exception as e2:
                logging.error(f"Failed to load fallback model: {e2}")
                raise Exception(f"Could not load any multilingual model: {e2}")
    
    def encode_texts(self, texts):
        """
        Encode a list of texts into embeddings.
        
        Args:
            texts (list): List of strings to encode
            
        Returns:
            numpy.ndarray: Array of embeddings
        """
        if not texts:
            return np.array([])
        
        if not self.model:
            raise Exception("Model not loaded")
        
        # Clean and filter empty texts
        clean_texts = [str(text).strip() for text in texts if text and str(text).strip()]
        
        if not clean_texts:
            return np.array([])
        
        try:
            embeddings = self.model.encode(clean_texts)
            return embeddings
        except Exception as e:
            logging.error(f"Failed to encode texts: {e}")
            raise e
    
    def compute_similarity_matrix(self, embeddings1, embeddings2=None):
        """
        Compute cosine similarity matrix between two sets of embeddings.
        
        Args:
            embeddings1 (numpy.ndarray): First set of embeddings
            embeddings2 (numpy.ndarray, optional): Second set of embeddings. 
                                                   If None, compute self-similarity.
        
        Returns:
            numpy.ndarray: Similarity matrix
        """
        if embeddings2 is None:
            embeddings2 = embeddings1
        
        if len(embeddings1) == 0 or len(embeddings2) == 0:
            return np.array([])
        
        similarity_matrix = cosine_similarity(embeddings1, embeddings2)
        return similarity_matrix
    
    def find_similar_texts(self, query_texts, corpus_texts, threshold=0.3, top_k=5):
        """
        Find similar texts in corpus for given query texts.
        
        Args:
            query_texts (list): List of query strings
            corpus_texts (list): List of corpus strings to search in
            threshold (float): Minimum similarity threshold
            top_k (int): Maximum number of results per query
            
        Returns:
            list: List of similarity results for each query
        """
        if not query_texts or not corpus_texts:
            return []
        
        # Encode both sets
        query_embeddings = self.encode_texts(query_texts)
        corpus_embeddings = self.encode_texts(corpus_texts)
        
        if len(query_embeddings) == 0 or len(corpus_embeddings) == 0:
            return []
        
        # Compute similarity matrix
        similarity_matrix = self.compute_similarity_matrix(query_embeddings, corpus_embeddings)
        
        results = []
        for i, query in enumerate(query_texts):
            if i >= len(similarity_matrix):
                continue
                
            similarities = similarity_matrix[i]
            
            # Get indices of similarities above threshold
            valid_indices = np.where(similarities >= threshold)[0]
            
            if len(valid_indices) == 0:
                results.append({
                    'query': query,
                    'matches': []
                })
                continue
            
            # Sort by similarity score (descending)
            sorted_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]]
            
            # Take top_k results
            top_indices = sorted_indices[:top_k]
            
            matches = []
            for idx in top_indices:
                if idx < len(corpus_texts):
                    matches.append({
                        'text': corpus_texts[idx],
                        'similarity': float(similarities[idx]),
                        'index': int(idx)
                    })
            
            results.append({
                'query': query,
                'matches': matches
            })
        
        return results
    
    def find_cross_lingual_similarities(self, arabic_texts, english_texts, threshold=0.3):
        """
        Find cross-lingual similarities between Arabic and English texts.
        
        Args:
            arabic_texts (list): List of Arabic texts
            english_texts (list): List of English texts
            threshold (float): Minimum similarity threshold
            
        Returns:
            dict: Cross-lingual similarity results
        """
        results = {
            'ar_to_en': [],
            'en_to_ar': []
        }
        
        if arabic_texts and english_texts:
            # Arabic to English similarities
            ar_to_en = self.find_similar_texts(arabic_texts, english_texts, threshold)
            results['ar_to_en'] = ar_to_en
            
            # English to Arabic similarities
            en_to_ar = self.find_similar_texts(english_texts, arabic_texts, threshold)
            results['en_to_ar'] = en_to_ar
        
        return results
    
    def get_subject_news_similarities(self, subjects, news_documents, threshold=0.3):
        """
        Find similarities between training subjects and news content.
        
        Args:
            subjects (list): List of subject area names
            news_documents (list): List of news document dicts with 'title' and 'content'
            threshold (float): Minimum similarity threshold
            
        Returns:
            dict: Similarities for each subject
        """
        if not subjects or not news_documents:
            return {}
        
        # Prepare news texts (combine title and content)
        news_texts = []
        for doc in news_documents:
            title = doc.get('title', '')
            content = doc.get('content', '')
            combined = f"{title}. {content}".strip()
            if combined and combined != '.':
                news_texts.append(combined)
        
        if not news_texts:
            return {}
        
        # Find similarities
        similarities = self.find_similar_texts(subjects, news_texts, threshold)
        
        # Format results by subject
        results = {}
        for result in similarities:
            subject = result['query']
            matches = result['matches']
            
            if matches:
                results[subject] = {
                    'matches': matches,
                    'best_similarity': max(match['similarity'] for match in matches),
                    'total_matches': len(matches)
                }
        
        return results