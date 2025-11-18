import sys
import os
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ambitioushub.settings')

# Setup Django
django.setup()

from django.test.client import Client

def handler(event, context):
    """
    Netlify Function handler for Django API requests
    Routes all /api/* requests through Django's URL routing
    """
    
    client = Client()
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET').upper()
    body = event.get('body', '')
    headers = event.get('headers', {})
    
    try:
        # Route the request through Django
        if method == 'GET':
            response = client.get(path, HTTP_AUTHORIZATION=headers.get('authorization', ''))
        elif method == 'POST':
            response = client.post(path, data=body, HTTP_AUTHORIZATION=headers.get('authorization', ''))
        elif method == 'PUT':
            response = client.put(path, data=body, HTTP_AUTHORIZATION=headers.get('authorization', ''))
        elif method == 'DELETE':
            response = client.delete(path, HTTP_AUTHORIZATION=headers.get('authorization', ''))
        else:
            response = client.get(path)
        
        return {
            'statusCode': response.status_code,
            'body': response.content.decode('utf-8'),
            'headers': dict(response.items())
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'{{"error": "Internal Server Error: {str(e)}"}}',
            'headers': {'Content-Type': 'application/json'}
        }
