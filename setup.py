#!/usr/bin/env python3
"""
Setup script for Document Intelligence Platform
This script helps set up the project environment and dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False

def setup_backend():
    """Set up Django backend"""
    print("\n🔧 Setting up Django Backend...")
    
    # Create virtual environment
    if not os.path.exists('venv'):
        if not run_command('python -m venv venv'):
            return False
    
    # Activate virtual environment and install requirements
    if os.name == 'nt':  # Windows
        pip_cmd = 'venv\\Scripts\\pip install -r requirements.txt'
        python_cmd = 'venv\\Scripts\\python'
    else:  # Unix/Linux/macOS
        pip_cmd = 'source venv/bin/activate && pip install -r requirements.txt'
        python_cmd = 'venv/bin/python'
    
    if not run_command(pip_cmd):
        return False
    
    # Create necessary directories
    os.makedirs('media/documents', exist_ok=True)
    os.makedirs('chroma_db', exist_ok=True)
    
    # Run Django migrations
    if not run_command(f'{python_cmd} manage.py makemigrations'):
        return False
    
    if not run_command(f'{python_cmd} manage.py migrate'):
        return False
    
    print("✅ Backend setup complete!")
    return True

def setup_frontend():
    """Set up React frontend"""
    print("\n🔧 Setting up React Frontend...")
    
    frontend_dir = 'frontend'
    if not os.path.exists(frontend_dir):
        print(f"❌ Frontend directory '{frontend_dir}' not found")
        return False
    
    os.chdir(frontend_dir)
    
    # Install npm dependencies
    if not run_command('npm install'):
        os.chdir('..')
        return False
    
    os.chdir('..')
    print("✅ Frontend setup complete!")
    return True

def create_test_document():
    """Create a sample test document"""
    test_content = """
Document Intelligence Platform

Welcome to the Document Intelligence Platform! This is a powerful AI-driven system designed to help you interact with your documents in revolutionary ways.

Key Features:
- Advanced document processing and analysis
- Intelligent text chunking for optimal retrieval
- Semantic search capabilities using state-of-the-art embeddings
- Natural language question answering
- Real-time document chat interface
- Support for multiple document formats (TXT, PDF, DOCX, MD)

Benefits:
- Save time by quickly finding information in large documents
- Get instant answers to questions about your content
- Understand document relationships and themes
- Improve productivity with AI-powered insights
- Streamline document workflow and management

How It Works:
The platform uses advanced Natural Language Processing (NLP) techniques to understand and analyze your documents. When you upload a document, it's automatically processed and broken down into intelligent chunks. These chunks are then converted into high-dimensional vector embeddings that capture the semantic meaning of the text.

When you ask a question, the system uses both semantic similarity and keyword matching to find the most relevant information.
"""
