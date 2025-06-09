import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Document
from .serializers import DocumentSerializer, QuestionSerializer

@method_decorator(csrf_exempt, name='dispatch')
class DocumentListView(View):
    """GET: Retrieve all documents"""
    
    def get(self, request):
        try:
            documents = Document.objects.all()
            serializer = DocumentSerializer(documents, many=True)
            
            return JsonResponse({
                'status': 'success',
                'documents': serializer.data,
                'total': documents.count()
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DocumentUploadView(View):
    """POST: Upload and process documents"""
    
    def post(self, request):
        try:
            print("UPLOAD: Starting document upload")
            
            # Check if file is present
            if 'file' not in request.FILES:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No file provided'
                }, status=400)
            
            uploaded_file = request.FILES['file']
            
            # Save file
            upload_dir = os.path.join(settings.BASE_DIR, 'media', 'documents')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, uploaded_file.name)
            
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Create document record
            document = Document.objects.create(
                title=os.path.splitext(uploaded_file.name)[0],
                file_path=file_path,
                document_type='txt',
                file_size=uploaded_file.size,
                processing_status='processing'
            )
            
            print("UPLOAD: Processing document")
            # Import processor
            from .processors import DocumentProcessor
            
            processor = DocumentProcessor()
            result = processor.process_document(document.pk, file_path)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Document uploaded successfully',
                'document_id': document.pk,
                'processing_result': result
            })
            
        except Exception as e:
            print("UPLOAD ERROR:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class QuestionAnswerView(View):
    """POST: Ask questions about documents"""
    
    def post(self, request):
        try:
            print("QA: Starting question processing")
            
            # Parse JSON data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON data'
                }, status=400)
            
            print("QA: Received data:", data)
            
            # Validate data using serializer
            serializer = QuestionSerializer(data=data)
            if not serializer.is_valid():
                print("QA: Validation errors:", serializer.errors)
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid data',
                    'errors': serializer.errors
                }, status=400)

            # Extract validated data safely
            validated_data = serializer.validated_data if hasattr(serializer, 'validated_data') else {}
            if not isinstance(validated_data, dict):
                validated_data = {}
                
            document_id = validated_data.get('document_id')
            question = validated_data.get('question')
            num_chunks = validated_data.get('num_chunks', 3)
            # Ensure question is a valid string
            if question is None:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Question cannot be empty'
                }, status=400)
            
            print("QA: Validated - Document ID:", document_id, "Question:", question)
            
            # Get document
            try:
                document = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Document not found'
                }, status=404)
            
            # Check if document is processed
            if document.processing_status != 'completed':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Document is not ready. Status: ' + document.processing_status
                }, status=400)
            
            print("QA: Processing question")
            # Import and use processor
            from .processors import DocumentProcessor
            
            processor = DocumentProcessor()
            result = processor.ask_question(document.pk, question, num_chunks)
            
            return JsonResponse({
                'status': 'success',
                'document_title': document.title,
                'document_id': document_id,
                'question': question,
                **result
            })
            
        except Exception as e:
            print("QA ERROR:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'success',
        'message': 'API is running'
    })

def document_detail(request, document_id):
    """GET: Get document details and statistics"""
    try:
        from .processors import DocumentProcessor
        processor = DocumentProcessor()
        stats = processor.get_document_stats(document_id)
        
        if 'error' in stats:
            return JsonResponse({
                'status': 'error',
                'message': stats['error']
            }, status=404)
        
        return JsonResponse({
            'status': 'success',
            'document': stats
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def document_delete(request, document_id):
    """DELETE: Delete a document and its chunks"""
    if request.method == 'DELETE':
        try:
            document = Document.objects.get(id=document_id)
            document.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Document deleted'
            })
        except Document.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Document not found'
            }, status=404)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)