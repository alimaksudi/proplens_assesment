import os
import django
from django.contrib.auth import get_user_model

def create_superuser():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not all([username, email, password]):
        print("Superuser environment variables not set. Skipping superuser creation.")
        return

    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully.")
    else:
        print(f"Superuser {username} already exists.")

if __name__ == "__main__":
    # Ensure this script is run within a Django context if executed directly (helper for Render start command)
    # However, for manage.py runscript or direct execution relying on env setup elsewhere this might differ.
    # Given the start command context: `cd src && python scripts/create_superuser.py` or similar
    # We need to setup django.
    
    # Add project root to path if needed (assuming run from src/)
    import sys
    sys.path.append(os.getcwd())
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    
    create_superuser()
