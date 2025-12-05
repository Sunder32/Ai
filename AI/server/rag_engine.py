"""
RAG Engine - Retrieval-Augmented Generation
Простая реализация без внешних зависимостей (без ChromaDB)
Использует TF-IDF для векторного поиска
"""

import os
import json
import re
import math
from typing import List, Optional, Dict
from collections import Counter

# Директория для хранения индекса
INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "rag_index")


class SimpleRAGEngine:
    """Простой RAG движок на основе TF-IDF"""
    
    def __init__(self):
        os.makedirs(INDEX_DIR, exist_ok=True)
        self.documents: List[Dict] = []
        self.idf: Dict[str, float] = {}
        self.index_file = os.path.join(INDEX_DIR, "index.json")
        self._load_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """Простая токенизация"""
        text = text.lower()
        # Убираем спецсимволы, оставляем буквы и цифры
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        # Убираем короткие слова
        return [t for t in tokens if len(t) > 2]
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Term Frequency"""
        counter = Counter(tokens)
        total = len(tokens)
        return {word: count / total for word, count in counter.items()}
    
    def _compute_idf(self):
        """Inverse Document Frequency"""
        doc_count = len(self.documents)
        if doc_count == 0:
            return
        
        word_doc_count: Dict[str, int] = {}
        for doc in self.documents:
            unique_words = set(doc.get('tokens', []))
            for word in unique_words:
                word_doc_count[word] = word_doc_count.get(word, 0) + 1
        
        self.idf = {
            word: math.log(doc_count / count) 
            for word, count in word_doc_count.items()
        }
    
    def _compute_tfidf(self, tokens: List[str]) -> Dict[str, float]:
        """TF-IDF вектор"""
        tf = self._compute_tf(tokens)
        return {
            word: tf_val * self.idf.get(word, 0)
            for word, tf_val in tf.items()
        }
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Косинусное сходство"""
        common_words = set(vec1.keys()) & set(vec2.keys())
        if not common_words:
            return 0.0
        
        dot_product = sum(vec1[w] * vec2[w] for w in common_words)
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None, chunk_size: int = 200):
        """Добавить документы"""
        for doc_idx, text in enumerate(texts):
            chunks = self._split_text(text, chunk_size)
            
            for chunk_idx, chunk in enumerate(chunks):
                tokens = self._tokenize(chunk)
                if not tokens:
                    continue
                
                doc = {
                    "id": f"doc_{doc_idx}_chunk_{chunk_idx}",
                    "text": chunk,
                    "tokens": tokens,
                    "metadata": metadatas[doc_idx] if metadatas and doc_idx < len(metadatas) else {}
                }
                self.documents.append(doc)
        
        # Пересчитываем IDF
        self._compute_idf()
        
        # Вычисляем TF-IDF для каждого документа
        for doc in self.documents:
            doc['tfidf'] = self._compute_tfidf(doc['tokens'])
        
        self._save_index()
        return len(self.documents)
    
    def search(self, query: str, n_results: int = 5) -> List[dict]:
        """Поиск по запросу"""
        if not self.documents:
            return []
        
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        query_tfidf = self._compute_tfidf(query_tokens)
        
        # Вычисляем сходство с каждым документом
        results = []
        for doc in self.documents:
            similarity = self._cosine_similarity(query_tfidf, doc.get('tfidf', {}))
            if similarity > 0:
                results.append({
                    "text": doc['text'],
                    "metadata": doc.get('metadata', {}),
                    "score": similarity
                })
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:n_results]
    
    def get_context_for_query(self, query: str, max_tokens: int = 2000) -> str:
        """Получить контекст для запроса"""
        results = self.search(query, n_results=10)
        
        context_parts = []
        total_len = 0
        
        for r in results:
            text = r['text']
            if total_len + len(text) > max_tokens * 4:
                break
            context_parts.append(text)
            total_len += len(text)
        
        return "\n\n".join(context_parts)
    
    def clear(self):
        """Очистить индекс"""
        self.documents = []
        self.idf = {}
        self._save_index()
    
    def _split_text(self, text: str, chunk_size: int = 200) -> List[str]:
        """Разбить текст на чанки"""
        words = text.split()
        chunks = []
        overlap = chunk_size // 4
        
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk = " ".join(chunk_words)
            if chunk.strip():
                chunks.append(chunk)
            i += chunk_size - overlap
        
        return chunks if chunks else [text]
    
    def _save_index(self):
        """Сохранить индекс"""
        # Сохраняем без tokens и tfidf для экономии места
        save_data = {
            "documents": [
                {"id": d["id"], "text": d["text"], "metadata": d.get("metadata", {})}
                for d in self.documents
            ],
            "idf": self.idf
        }
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False)
    
    def _load_index(self):
        """Загрузить индекс"""
        if not os.path.exists(self.index_file):
            return
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.idf = data.get('idf', {})
            
            # Восстанавливаем документы с токенами и TF-IDF
            for doc_data in data.get('documents', []):
                tokens = self._tokenize(doc_data['text'])
                doc = {
                    "id": doc_data['id'],
                    "text": doc_data['text'],
                    "tokens": tokens,
                    "metadata": doc_data.get('metadata', {}),
                    "tfidf": self._compute_tfidf(tokens)
                }
                self.documents.append(doc)
                
        except Exception as e:
            print(f"[RAG] Ошибка загрузки индекса: {e}")
            self.documents = []
            self.idf = {}
    
    def get_stats(self) -> dict:
        """Статистика"""
        return {
            "total_chunks": len(self.documents),
            "vocabulary_size": len(self.idf)
        }


# Singleton
_rag_engine = None

def get_rag_engine() -> SimpleRAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = SimpleRAGEngine()
    return _rag_engine
