# views.py
import qrcode
import os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from user_agents import parse

def generate_qr_code(url):
    """
    Generate a QR code for the given URL and save it in the media directory
    
    Args:
        url (str): URL to encode in the QR code
    
    Returns:
        str: Path to the generated QR code image
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Ensure media directory exists
    media_dir = os.path.join(settings.BASE_DIR, 'media', 'qr_codes')
    os.makedirs(media_dir, exist_ok=True)

    # Generate filename
    filename = 'download_qr.png'
    filepath = os.path.join(media_dir, filename)

    # Save the image
    img.save(filepath)

    # Return relative path for template
    return f'/media/qr_codes/{filename}'

def index(request):
    """
    Main view for detecting device type and preparing download options
    """
    # Application download information
    app_info = {
        'name': 'CaffeeManagement',
        'description': 'Aplicación de gestión para cafeterías',
        'github_repo': 'https://github.com/zkin1/app-cafemanagement',
        'git_apk_download': 'https://github.com/zkin1/app-cafemanagement/raw/main/android/app/release/app-release.apk'
    }

    # Detect mobile device
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)

    # Comprehensive mobile detection
    is_mobile = (
        user_agent.is_mobile or 
        user_agent.is_tablet or 
        'mobile' in user_agent_string.lower()
    )

    # Prepare context
    context = {
        'app_info': app_info,
        'is_mobile': is_mobile,
        'download_link': app_info['git_apk_download']
    }

    # Generate QR code for non-mobile devices
    if not is_mobile:
        try:
            context['qr_code'] = generate_qr_code(app_info['git_apk_download'])
        except Exception as e:
            context['qr_code_error'] = str(e)
            print(f"QR Code Generation Error: {e}")  # Log the error

    return render(request, 'index.html', context)