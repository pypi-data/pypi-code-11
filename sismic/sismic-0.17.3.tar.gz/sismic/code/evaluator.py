import abc
from sismic.model import Event, Transition, StateMixin, Statechart

__all__ = ['Evaluator']


class Evaluator(metaclass=abc.ABCMeta):
    """
    Abstract base class for any evaluator.

    An instance of this class defines what can be done with piece of codes
    contained in a statechart (condition, action, etc.).

    Notice that the execute_* methods are called at each step, even if there is no
    code to execute. This allows the evaluator to keep track of the states that are
    entered or exited, and of the transitions that are processed.

    :param interpreter: the interpreter that will use this evaluator,
        is expected to be an *Interpreter* instance
    :param initial_context: an optional dictionary to populate the context
    """
    def __init__(self, interpreter=None, initial_context: dict = None):
        self._context = initial_context if initial_context else {}
        self._interpreter = interpreter

    @property
    def context(self) -> dict:
        """
        The context of this evaluator. A context is a dict-like mapping between
        variables and values that is expected to be exposed when the code is evaluated.
        """
        return self._context

    @abc.abstractmethod
    def _evaluate_code(self, code: str, additional_context: dict = None) -> bool:
        """
        Generic method to evaluate a piece of code. This method is a fallback if one of
        the other evaluate_* methods is not overridden.

        :param code: code to evaluate
        :param additional_context: an optional additional context
        :return: truth value of *code*
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def _execute_code(self, code: str, additional_context: dict = None):
        """
        Generic method to execute a piece of code. This method is a fallback if one
        of the other execute_* methods is not overridden.

        :param code: code to execute
        :param additional_context: an optional additional context
        """
        raise NotImplementedError()

    def execute_statechart(self, statechart: Statechart):
        """
        Execute the initial code of a statechart.
        This method is called at the very beginning of the execution.

        :param statechart: statechart to consider
        """
        if statechart.preamble:
            return self._execute_code(statechart.preamble)

    def evaluate_guard(self, transition: Transition, event: Event) -> bool:
        """
        Evaluate the guard for given transition.

        :param transition: the considered transition
        :param event: instance of *Event* if any
        :return: truth value of *code*
        """
        if transition.guard:
            return self._evaluate_code(transition.guard, {'event': event})

    def execute_action(self, transition: Transition, event: Event) -> bool:
        """
        Execute the action for given transition.
        This method is called for every transition that is processed, even those with no *action*.

        :param transition: the considered transition
        :param event: instance of *Event* if any
        :return: truth value of *code*
        """
        if transition.action:
            return self._execute_code(transition.action, {'event': event})

    def execute_onentry(self, state: StateMixin):
        """
        Execute the on entry action for given state.
        This method is called for every state that is entered, even those with no *on_entry*.

        :param state: the considered state
        """
        if getattr(state, 'on_entry', None):
            return self._execute_code(state.on_entry)

    def execute_onexit(self, state: StateMixin):
        """
        Execute the on exit action for given state.
        This method is called for every state that is exited, even those with no *on_exit*.

        :param state: the considered state
        """
        if getattr(state, 'on_exit', None):
            return self._execute_code(state.on_exit)

    def evaluate_preconditions(self, obj, event: Event = None) -> list:
        """
        Evaluate the preconditions for given object (either a *StateMixin* or a
        *Transition*) and return a list of conditions that are not satisfied.

        :param obj: the considered state or transition
        :param event: an optional *Event* instance, in the case of a transition
        :return: list of unsatisfied conditions
        """
        event_d = {'event': event} if isinstance(obj, Transition) else None
        return filter(lambda c: not self._evaluate_code(c, event_d), getattr(obj, 'preconditions', []))

    def evaluate_invariants(self, obj, event: Event = None) -> list:
        """
        Evaluate the invariants for given object (either a *StateMixin* or a
        *Transition*) and return a list of conditions that are not satisfied.

        :param obj: the considered state or transition
        :param event: an optional *Event* instance, in the case of a transition
        :return: list of unsatisfied conditions
        """
        event_d = {'event': event} if isinstance(obj, Transition) else None
        return filter(lambda c: not self._evaluate_code(c, event_d), getattr(obj, 'invariants', []))

    def evaluate_postconditions(self, obj, event: Event = None) -> list:
        """
        Evaluate the postconditions for given object (either a *StateMixin* or a
        *Transition*) and return a list of conditions that are not satisfied.

        :param obj: the considered state or transition
        :param event: an optional *Event* instance, in the case of a transition
        :return: list of unsatisfied conditions
        """
        event_d = {'event': event} if isinstance(obj, Transition) else None
        return filter(lambda c: not self._evaluate_code(c, event_d), getattr(obj, 'postconditions', []))

