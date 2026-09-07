from functools import wraps
from django.shortcuts import redirect


def cliente_requerido(vista):
    @wraps(vista)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('cliente_id'):
            return redirect('clientes:login')
        return vista(request, *args, **kwargs)
    return wrapper