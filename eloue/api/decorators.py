# coding=utf-8


def list_link(**kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for GET requests.
    """
    def decorator(func):
        func.bind_to_methods = ['get']
        func.for_list = True
        func.kwargs = kwargs
        return func
    return decorator


def list_action(methods=['post'], **kwargs):
    """
    Used to mark a method on a ViewSet that should be routed for POST requests.
    """
    def decorator(func):
        func.bind_to_methods = methods
        func.for_list = True
        func.kwargs = kwargs
        return func
    return decorator
