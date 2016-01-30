import functools

from .filtering import ModelFilterField

# -----------------------------------------------------------------------------


def get_item_or_404(method=None, **decorator_kwargs):
    # Allow using this as either a decorator or a decorator factory.
    if method is None:
        return functools.partial(get_item_or_404, **decorator_kwargs)

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        id = kwargs.pop(self.id_view_arg)
        item = self.get_item_or_404(id, **decorator_kwargs)
        return method(self, item, *args, **kwargs)

    return wrapped


# -----------------------------------------------------------------------------


def filter_function(field):
    def wrapper(function):
        filter_field = ModelFilterField(field, function)
        functools.update_wrapper(filter_field, function)
        return filter_field

    return wrapper
