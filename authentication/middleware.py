"""
Authentication Middleware
Enforces login requirement for all pages except whitelisted public URLs
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class LoginRequiredMiddleware:
    """
    Middleware to enforce authentication on all pages.
    
    Redirects unauthenticated users to login page, except for:
    - Login page itself
    - Logout page
    - Password reset pages
    - Admin login
    - Static/media files
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # List of URL patterns that don't require authentication
        self.public_urls = [
            '/login/',
            '/logout/',
            '/password-reset/',
            '/admin/login/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Skip authentication check for public URLs
        if self.is_public_url(request.path):
            return self.get_response(request)
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Store the requested URL to redirect after login
            login_url = settings.LOGIN_URL or '/login/'
            
            # Redirect to login with 'next' parameter
            return redirect(f'{login_url}?next={request.path}')
        
        # User is authenticated, proceed with request
        response = self.get_response(request)
        return response
    
    def is_public_url(self, path):
        """
        Check if the requested path is in the public URLs list.
        
        Args:
            path (str): The request path
            
        Returns:
            bool: True if URL is public, False otherwise
        """
        # Check if path starts with any public URL pattern
        for public_url in self.public_urls:
            if path.startswith(public_url):
                return True
        
        return False
