import requests
import urllib3
import os


def disable_ssl_verification():
    """Disable SSL verification and patch OpenAI/CrewAI for testing environment"""
    
    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Patch requests - check if already patched
    if not hasattr(requests.Session.request, '_ssl_disabled'):
        old_request = requests.Session.request
        
        def patched_request(self, method, url, **kwargs):
            kwargs['verify'] = False
            return old_request(self, method, url, **kwargs)
        
        patched_request._ssl_disabled = True
        patched_request._original = old_request
        requests.Session.request = patched_request
    
    # Patch httpx if available
    try:
        import httpx
        import warnings
        
        # Suppress httpx SSL warnings
        warnings.filterwarnings('ignore', message='.*SSL.*')
        
        # Patch httpx.Client - check if already patched
        if not hasattr(httpx.Client.__init__, '_ssl_disabled'):
            old_httpx_client_init = httpx.Client.__init__
            
            def patched_httpx_client_init(self, *args, **kwargs):
                kwargs['verify'] = False
                return old_httpx_client_init(self, *args, **kwargs)
            
            patched_httpx_client_init._ssl_disabled = True
            patched_httpx_client_init._original = old_httpx_client_init
            httpx.Client.__init__ = patched_httpx_client_init
        
        # Patch httpx.AsyncClient - check if already patched
        if not hasattr(httpx.AsyncClient.__init__, '_ssl_disabled'):
            old_httpx_async_client_init = httpx.AsyncClient.__init__
            
            def patched_httpx_async_client_init(self, *args, **kwargs):
                kwargs['verify'] = False
                return old_httpx_async_client_init(self, *args, **kwargs)
            
            patched_httpx_async_client_init._ssl_disabled = True
            patched_httpx_async_client_init._original = old_httpx_async_client_init
            httpx.AsyncClient.__init__ = patched_httpx_async_client_init
            
    except ImportError:
        # httpx not installed, skip patching
        pass
    
    # Patch OpenAI client initialization for testing
    try:
        import openai
        
        # Patch OpenAI client to use environment settings and disable SSL verification
        if not hasattr(openai.OpenAI.__init__, '_crewai_patched'):
            old_openai_init = openai.OpenAI.__init__
            
            def patched_openai_init(self, *args, **kwargs):
                # Use environment variables if available, otherwise keep original values
                if os.getenv("OPENAI_API_KEY"):
                    kwargs['api_key'] = kwargs.get('api_key', os.getenv("OPENAI_API_KEY"))
                if os.getenv("OPENAI_API_BASE"):
                    kwargs['base_url'] = kwargs.get('base_url', os.getenv("OPENAI_API_BASE"))
                
                # Always disable SSL verification for proxy environments
                if 'http_client' not in kwargs:
                    import httpx
                    kwargs['http_client'] = httpx.Client(verify=False)
                
                return old_openai_init(self, *args, **kwargs)
            
            patched_openai_init._crewai_patched = True
            patched_openai_init._original = old_openai_init
            openai.OpenAI.__init__ = patched_openai_init
        
    except ImportError:
        # OpenAI not installed, skip patching
        pass