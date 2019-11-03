from drf_multiple_model.mixins import FlatMultipleModelMixin, ObjectMultipleModelMixin

from rest_framework.generics import GenericAPIView
from django.utils.decorators import classonlymethod
from functools import update_wrapper
from django.views.decorators.csrf import csrf_exempt


class BaseAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return None

    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        """
        Because of the way class based views create a closure around the
        instantiated view, we need to totally reimplement `.as_view`,
        and slightly modify the view function that is created and returned.
        """
        # The suffix initkwarg is reserved for displaying the viewset type.
        # eg. 'List' or 'Instance'.
        cls.suffix = None

        # Setting a basename allows a view to reverse its action urls. This
        # value is provided by the router through the initkwargs.
        cls.basename = None

        # actions must not be empty
        if not actions:
            raise TypeError("The `actions` argument must be provided when "
                            "calling `.as_view()` on a ViewSet. For example "
                            "`.as_view({'get': 'list'})`")

        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r" % (
                    cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            # We also store the mapping of request methods to actions,
            # so that we can later set the action attribute.
            # eg. `self.action = 'list'` on an incoming GET request.
            self.action_map = actions

            # Bind methods to actions
            # This is the bit that's different to a standard view
            for method, action in actions.items():
                handler = getattr(self, action)
                setattr(self, method, handler)

            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get

            self.request = request
            self.args = args
            self.kwargs = kwargs

            # And continue as usual
            return self.dispatch(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())

        # We need to set these on the view function, so that breadcrumb
        # generation can pick out these bits of information from a
        # resolved URL.
        view.cls = cls
        view.initkwargs = initkwargs
        view.suffix = initkwargs.get('suffix', None)
        view.actions = actions
        return csrf_exempt(view)


class FlatMultipleModelAPIView(FlatMultipleModelMixin, BaseAPIView):
    pass


class ObjectMultipleModelAPIView(ObjectMultipleModelMixin, BaseAPIView):
    pass
