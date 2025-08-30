# cache.py
from flask_caching import Cache

# Initialize a Cache object.
# It will be configured and linked to the app in app.py to avoid circular imports.
cache = Cache()