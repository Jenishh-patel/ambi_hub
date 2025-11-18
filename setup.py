#!/usr/bin/env python
"""
Quick setup script for Ambitious Hub
Run: python setup.py
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed")
        print(e.stderr)
        return False

def main():
    print("=" * 50)
    print("Ambitious Hub - Setup Script")
    print("=" * 50)
    
    # Check if virtual environment is recommended
    if not os.environ.get('VIRTUAL_ENV'):
        print("\n⚠ Warning: Not in a virtual environment.")
        print("Consider creating one: python -m venv venv")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("\n✗ Setup failed at dependency installation.")
        return
    
    # Run migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        print("\n✗ Setup failed at migrations creation.")
        return
    
    if not run_command("python manage.py migrate", "Running migrations"):
        print("\n✗ Setup failed at migrations.")
        return
    
    # Initialize default data
    if not run_command("python manage.py init_default_categories", "Initializing default categories"):
        print("\n⚠ Warning: Could not initialize default categories (may already exist)")
    
    if not run_command("python manage.py init_default_badges", "Initializing default badges"):
        print("\n⚠ Warning: Could not initialize default badges (may already exist)")
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("\n⚠ Warning: Could not collect static files")
    
    print("\n" + "=" * 50)
    print("✓ Setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the server: python manage.py runserver")
    print("3. Visit: http://127.0.0.1:8000/")
    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()

