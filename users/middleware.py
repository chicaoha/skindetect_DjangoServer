import uuid
from django.utils.deprecation import MiddlewareMixin

class VisitorMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get or create a unique identifier for the visitor
        visitor_id = request.session.get('visitor_id')
        if not visitor_id:
            visitor_id = str(uuid.uuid4())
            request.session['visitor_id'] = visitor_id

        # Store the visitor_id in the request for easy access in views
        request.visitor_id = visitor_id