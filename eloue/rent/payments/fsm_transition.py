# -*- coding: utf-8 -*-
from functools import wraps
from fsm.exceptions import TransitionNotAllowed
from fsm.models import FSMMeta


def smart_transition(source='*', target=None, save=False, conditions=[]):
    
    """Method decorator for mark allowed transition"""
    def inner_transition(func):
        if not hasattr(func, '_django_fsm'):
            setattr(func, '_django_fsm', FSMMeta())
        if isinstance(source, (list, tuple)):
            for state in source:
                func._django_fsm.transitions[state] = target
        else:
            func._django_fsm.transitions[source] = target
        func._django_fsm.conditions[target] = conditions

        @wraps(func)
        def _change_state(instance, *args, **kwargs):
            meta = func._django_fsm
            if not meta.has_transition(instance):
                raise TransitionNotAllowed("Can't switch from state '%s' using method '%s'" % (FSMMeta.current_state(instance), func.func_name))
            result = func(instance, *args, **kwargs) # sth make the function smarter.
            for condition in conditions:
                if not condition(instance):
                    return False
            meta.to_next_state(instance)
            if save:
                instance.save()
            return result
        return _change_state

    if not target:
        raise ValueError("Result state not specified")
    return inner_transition