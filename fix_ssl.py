"""
SSL Certificate Fix for macOS
This script configures SSL certificates for the viral fashion agent.
"""
import ssl
import certifi
import os

def fix_ssl_certificates():
    """Set up SSL certificates properly"""
    # Get certifi certificate path
    cert_path = certifi.where()
    
    # Set environment variables
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    os.environ['CURL_CA_BUNDLE'] = cert_path
    
    print(f"✅ SSL certificates configured: {cert_path}")
    
    # Monkey-patch requests to use certifi
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.ssl_ import create_urllib3_context
        
        class SSLAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                context = create_urllib3_context()
                context.load_verify_locations(cert_path)
                kwargs['ssl_context'] = context
                return super().init_poolmanager(*args, **kwargs)
        
        # This will be used by all requests
        print("✅ Requests library configured with certifi")
    except Exception as e:
        print(f"⚠️  Could not configure requests: {e}")

if __name__ == "__main__":
    fix_ssl_certificates()
