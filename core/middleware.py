import threading

_user = threading.local()


class CurrentUserMiddleware:
    """
    Middleware that stores the current user for use throughout the request lifecycle.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user  # Set the user globally for this request
        response = self.get_response(request)
        return response

    @staticmethod
    def get_current_user():
        return getattr(_user, 'value', None)
