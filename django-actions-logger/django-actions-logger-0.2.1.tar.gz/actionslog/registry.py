from __future__ import unicode_literals

from django.db.models.signals import pre_save, post_save, post_delete
from django.db.models import Model


class ActionslogModelRegistry(object):
    """
    A registry that keeps track of the models that use actionslog to track changes.
    """
    def __init__(self, create=True, update=True, delete=True, custom=None):
        from actionslog.receivers import action_log_create, action_log_update, action_log_delete

        self._registry = {}
        self._signals = {}

        if create:
            self._signals[post_save] = action_log_create
        if update:
            self._signals[pre_save] = action_log_update
        if delete:
            self._signals[post_delete] = action_log_delete

        if custom is not None:
            self._signals.update(custom)

    def register(self, model, include_fields=[], exclude_fields=[]):
        """
        Register a model with actionslog. Actionslog will then track mutations on this model's instances.

        :param model: The model to register.
        :type model: Model
        :param include_fields: The fields to include. Implicitly excludes all other fields.
        :type include_fields: list
        :param exclude_fields: The fields to exclude. Overrides the fields to include.
        :type exclude_fields: list
        """
        if issubclass(model, Model):
            self._registry[model] = {
                'include_fields': include_fields,
                'exclude_fields': exclude_fields,
            }
            self._connect_signals(model)
        else:
            raise TypeError("Supplied model is not a valid model.")

    def contains(self, model):
        """
        Check if a model is registered with actionslog.

        :param model: The model to check.
        :type model: Model
        :return: Whether the model has been registered.
        :rtype: bool
        """
        return model in self._registry

    def unregister(self, model):
        """
        Unregister a model with actionslog. This will not affect the database.

        :param model: The model to unregister.
        :type model: Model
        """
        try:
            del self._registry[model]
        except KeyError:
            pass
        else:
            self._disconnect_signals(model)

    def _connect_signals(self, model):
        """
        Connect signals for the model.
        """
        for signal in self._signals:
            receiver = self._signals[signal]
            signal.connect(receiver, sender=model, dispatch_uid=self._dispatch_uid(signal, model))

    def _disconnect_signals(self, model):
        """
        Disconnect signals for the model.
        """
        for signal, receiver in self._signals.items():
            signal.disconnect(sender=model, dispatch_uid=self._dispatch_uid(signal, model))

    def _dispatch_uid(self, signal, model):
        """
        Generate a dispatch_uid.
        """
        return (self.__class__, model, signal)

    def get_model_fields(self, model):
        return {
            'include_fields': self._registry[model]['include_fields'],
            'exclude_fields': self._registry[model]['exclude_fields'],
        }


actionslog = ActionslogModelRegistry()
