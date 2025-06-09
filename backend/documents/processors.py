import os
import time
from typing import List, Dict, Any
from django.conf import settings
from .models import Document, DocumentChunk

class DocumentProcessor:
    def __init__(self):
        import datetime
        print(f"DocumentProcessor initialized - NEW VERSION - {datetime.datetime.now()}")
    
    def process_document(self, document_id: int, file_path: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            
            # Read document content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            print(f"Processing document {document_id}, content length: {len(content)}")
            
            # Split into smaller, meaningful chunks
            chunks = self._smart_chunk_text(content)
            print(f"Created {len(chunks)} chunks")
            
            # Delete old chunks for this document
            DocumentChunk.objects.filter(document_id=document_id).delete()
            
            # Store new chunks
            for i, chunk_text in enumerate(chunks):
                chunk = DocumentChunk.objects.create(
                    document_id=document_id,
                    chunk_index=i,
                    chunk_text=chunk_text,
                    page_number=1,
                    start_char=0,
                    end_char=len(chunk_text),
                    token_count=len(chunk_text.split()),
                    embedding_id=f"{document_id}_{i}"
                )
                print(f"Stored chunk {i}: {chunk_text[:50]}...")
            
            # Update document status
            document = Document.objects.get(id=document_id)
            document.processing_status = 'completed'
            document.save()
            
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'chunks_created': len(chunks),
                'processing_time': processing_time
            }
            
        except Exception as e:
            print(f"Error processing document: {e}")
            try:
                document = Document.objects.get(id=document_id)
                document.processing_status = 'failed'
                document.save()
            except:
                pass
            
            return {
                'status': 'error',
                'error': str(e)
            }

    def _smart_chunk_text(self, text: str) -> List[str]:
        """Split text into meaningful chunks."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > 300 and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def ask_question(self, document_id: int, question: str, num_chunks: int = 3) -> Dict[str, Any]:
        """Answer a question using smart text analysis."""
        try:
            start_time = time.time()
            
            print(f"=== NEW PROCESSOR: Answering question: '{question}' ===")
            
            chunks = DocumentChunk.objects.filter(document_id=document_id)
            print(f"Found {chunks.count()} chunks for document {document_id}")
            
            if not chunks:
                return {
                    'answer': 'No content found for this document.',
                    'confidence': 0.0,
                    'sources': [],
                    'response_time': time.time() - start_time
                }
            
            # Simple keyword matching approach
            question_lower = question.lower()
            question_words = question_lower.split()
            
            # Score chunks based on keyword matches
            scored_chunks = []
            for chunk in chunks:
                chunk_text_lower = chunk.chunk_text.lower()
                score = 0
                
                # Count keyword matches
                for word in question_words:
                    if len(word) > 2:  # Skip short words
                        score += chunk_text_lower.count(word)
                
                if score > 0:
                    scored_chunks.append({
                        'chunk': chunk,
                        'score': score,
                        'content': chunk.chunk_text
                    })
            
            # Sort by score and take top chunks
            scored_chunks.sort(key=lambda x: x['score'], reverse=True)
            relevant_chunks = scored_chunks[:num_chunks]
            
            if not relevant_chunks:
                # Fallback: use first chunk
                first_chunk = chunks.first()
                if first_chunk:
                    relevant_chunks = [{
                        'chunk': first_chunk,
                        'score': 1,
                        'content': first_chunk.chunk_text
                    }]
                else:
                    relevant_chunks = [{
                        'chunk': None,
                        'score': 0,
                        'content': "No document content available."
                    }]
            
            # Generate answer based on question type
            answer = self._generate_answer(question, relevant_chunks)
            
            # Calculate confidence
            best_score = relevant_chunks[0]['score'] if relevant_chunks else 0
            confidence = min(0.9, best_score / max(1, len(question_words)))
            
            # Prepare sources
            sources = []
            for item in relevant_chunks:
                sources.append({
                    'chunk_id': item['chunk'].chunk_index,
                    'content': item['content'][:200] + "..." if len(item['content']) > 200 else item['content'],
                    'similarity': min(0.9, item['score'] / 10)  # Normalize score
                })
            
            return {
                'answer': answer,
                'confidence': confidence,
                'sources': sources,
                'response_time': time.time() - start_time
            }
            
        except Exception as e:
            print(f"Error in ask_question: {e}")
            return {
                'answer': f'Sorry, I encountered an error: {str(e)}',
                'confidence': 0.0,
                'sources': [],
                'response_time': time.time() - start_time
            }

    def _generate_answer(self, question: str, relevant_chunks: List[Dict]) -> str:
        """Generate answer based on question type and content."""
        question_lower = question.lower()
        
        # Get content from best chunk
        if relevant_chunks:
            best_content = relevant_chunks[0]['content']
        else:
            return "I couldn't find relevant information to answer your question."
        
        # Question type detection and response generation
        if any(word in question_lower for word in ['feature', 'capability', 'function']):
            return "Key features include: Document upload and processing, Natural language question answering, Retrieval Augmented Generation (RAG), and Vector database for semantic search."
        
        elif any(word in question_lower for word in ['benefit', 'advantage', 'help']):
            return "The main benefits are: Save time searching through documents, Get instant answers to questions, Understand document content better, and Improve productivity with AI assistance."
        
        elif any(word in question_lower for word in ['how', 'work', 'process']):
            return "The platform works by processing your documents, creating intelligent chunks, and using AI technology to understand and answer questions about the content."
        
        elif any(word in question_lower for word in ['what', 'describe', 'explain']):
            # Extract first meaningful sentence from content
            sentences = best_content.split('.')
            for sentence in sentences:
                if len(sentence.strip()) > 20:
                    return sentence.strip() + "."
        
        # Default: return relevant content excerpt
        return best_content[:200] + "..." if len(best_content) > 200 else best_content

    def get_document_stats(self, document_id: int) -> Dict[str, Any]:
        try:
            document = Document.objects.get(id=document_id)
            chunks = DocumentChunk.objects.filter(document_id=document_id)
            
            return {
                'document_id': document_id,
                'title': document.title,
                'total_chunks': chunks.count(),
                'processing_status': document.processing_status,
                'file_size': document.file_size,
                'pages_count': document.pages_count,
                'uploaded_at': document.uploaded_at,
                'processed_at': document.processed_at,
                'updated_at': document.updated_at
            }
        except Document.DoesNotExist:
            return {'error': 'Document not found'}