# coding=utf-8
from django.core.exceptions import ImproperlyConfigured
from rest_framework.routers import DefaultRouter, flatten, Route, replace_methodname


class Api20Router(DefaultRouter):
    # FIXME: Ability of creation nonstandard list actions already added in DRF 2.4

    def get_routes(self, viewset):
        """
        Augment `self.routes` with any dynamically generated routes.

        Returns a list of the Route namedtuple.
        """

        known_actions = flatten([route.mapping.values() for route in self.routes])

        # Determine any `@action` or `@link` decorated methods on the viewset
        dynamic_routes = []
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, 'bind_to_methods', None)
            if httpmethods:
                if methodname in known_actions:
                    raise ImproperlyConfigured('Cannot use @action or @link decorator on '
                                               'method "%s" as it is an existing route' % methodname)
                httpmethods = [method.lower() for method in httpmethods]
                dynamic_routes.append((httpmethods, methodname))

        ret = []
        for route in self.routes:
            if route.mapping == {'{httpmethod}': '{methodname}'}:
                # Dynamic routes (@link or @action decorator)
                for httpmethods, methodname in dynamic_routes:
                    method_kwargs = getattr(viewset, methodname).kwargs
                    url_path = method_kwargs.pop("url_path", None) or methodname
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(method_kwargs)
                    if getattr(getattr(viewset, methodname), 'for_list', False):
                        ret.insert(0, Route(
                            url=replace_methodname(route.url, url_path).replace('{lookup}/', ''),
                            mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                            name=replace_methodname(route.name, url_path),
                            initkwargs=initkwargs,
                        ))
                    else:
                        ret.append(Route(
                            url=replace_methodname(route.url, url_path),
                            mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                            name=replace_methodname(route.name, url_path),
                            initkwargs=initkwargs,
                        ))
            else:
                # Standard route
                ret.append(route)

        return ret
