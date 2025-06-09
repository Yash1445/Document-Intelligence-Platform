from .processors import DocumentProcessor
from .models import Document, DocumentChunk

# Test the processor directly
processor = DocumentProcessor()
print("Testing processor directly...")

# Assuming document ID 1 exists
try:
    result = processor.ask_question(1, "What are the benefits mentioned?", 3)
    print(f"Direct test result: {result}")
except Exception as e:
    print(f"Direct test error: {e}")
