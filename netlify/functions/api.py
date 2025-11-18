import sys
import os
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Point to Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ambitioushub.settings')

# Setup Django
django.setup()

from ambitioushub.wsgi import application
import awsgi

def handler(event, context):
    """Netlify function handler that forwards the incoming event to Django WSGI app

    This uses awsgi to convert the Netlify (Lambda-like) event into a WSGI request
    and returns a Lambda-style response expected by Netlify functions.
    """
    try:
        return awsgi.response(application, event, context)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'{{"error": "Internal Server Error: {str(e)}"}}',
            'headers': {'Content-Type': 'application/json'}
        }
