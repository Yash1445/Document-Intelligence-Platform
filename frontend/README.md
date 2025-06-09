# documents/urls.py
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document endpoints
    path('documents/', views.DocumentListView.as_view(), name='document-list'),
    path('documents/upload/', views.DocumentUploadView.as_view(), name='document-upload'),
    path('documents/<int:document_id>/', views.document_detail, name='document-detail'),
    path('documents/<int:document_id>/delete/', views.document_delete, name='document-delete'),
    
    # Q&A endpoint
    path('ask/', views.QuestionAnswerView.as_view(), name='ask-question'),
    
    # Health check
    path('health/', views.health_check, name='health-check'),
]