# Django Rest Framework Dango

A set of viewset mixins for the [Django REST Framework](https://www.django-rest-framework.org/) that provides fully complete type hints to reduce the complexity of the mixin class.

## Installation

```bash
pip install djangorestframework_dango
```

## Usage

### ActionMixin

This mixin provides six action methods to help determine the current action:

- `is_create_action()` (POST)
- `is_retrieve_action()` (GET)
- `is_list_action()` (GET)
- `is_update_action()` (PUT)
- `is_partial_update_action()` (PATCH)
- `is_destroy_action()` (DELETE)

```python
from rest_framework import viewsets
from djangorestframework_dango.mixins import ActionMixin

class ViewSet(ActionMixin, viewsets.GenericViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.is_create_action():
            queryset = queryset.change_for_create()
        elif self.is_retrieve_action():
            queryset = queryset.change_for_retrieve()
        elif self.is_list_action():
            queryset = queryset.change_for_list()
        elif self.is_update_action():
            queryset = queryset.change_for_update()
        elif self.is_partial_update_action():
            queryset = queryset.change_for_partial_update()
        elif self.is_destroy_action():
            queryset = queryset.change_for_destroy()

        return queryset
```

### QuerysetMixin

This mixin automatically calls action-specific methods to modify the queryset. The issue was needing exact method names. Now, auto-completion works.

```python
from rest_framework import viewsets
from djangorestframework_dango.mixins import QuerysetMixin
from rest_framework.request import Request
from rest_framework.response import Response

class ViewSet(QuerysetMixin, viewsets.GenericViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

    # If you provide the model class to the queryset, auto-completion will work.
    def create_queryset(self, queryset: QuerySetType[Model]):
        queryset = queryset.change_for_create()
        return queryset

    def list_queryset(self, queryset: QuerySetType[Model]):
        queryset = queryset.change_for_list()
        return queryset

    def retrieve_queryset(self, queryset: QuerySetType[Model]):
        queryset = queryset.change_for_retrieve()
        return queryset

    def update_queryset(self, queryset: QuerySetType[Model]):
        queryset = queryset.change_for_update()
        return queryset

    def partial_update_queryset(self, queryset: QuerySetType[Model]):
        queryset = queryset.change_for_partial_update()
        return queryset

    def destroy_queryset(self, queryset: QuerySetType[Model]):
        queryset = queryset.change_for_delete()
        return queryset

    # Customize the queryset for the update_extra_profile action (Not auto completed)
    def update_extra_profile_queryset(self, queryset: QuerySetType[Model]):
        queryset = queryset.change_for_update_extra_profile()
        return queryset

    @action(methods=["POST"], detail=True)
    def update_extra_profile(self, request: Request, pk=None):
        queryset = self.get_queryset()
        return Response(serializer.data)
```

### SerializerMixin

This mixin allows defining multiple serializers for different actions. The default method key name of `serializer_class_by_actions` can support auto-completion.

```python
from rest_framework import viewsets
from djangorestframework_dango.mixins import SerializerMixin
from rest_framework.request import Request
from rest_framework.response import Response

class ViewSet(SerializerMixin, viewsets.GenericViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    serializer_class_by_actions = {
        "create": ModelCreateSerializer,
        "list": ModelListSerializer,
        "retrieve": ModelRetrieveSerializer,
        "update": ModelUpdateSerializer,
        "partial_update": ModelPartialUpdateSerializer,
        "destroy": ModelDestroySerializer,
        "update_extra_profile": ModelUpdateExtraProfileSerializer, # Not auto completed
    }

    @action(methods=["POST"], detail=True)
    def update_extra_profile(self, request: Request, pk=None):
        serializer = self.get_serializer()
        return Response(serializer.data)
```

### PermissionMixin

This mixin allows defining different permissions for each action. The default method key name of `permission_by_actions` can support auto-completion.

```python
from rest_framework import viewsets
from djangorestframework_dango.mixins import PermissionMixin
from rest_framework.permissions import AllowAny, IsAuthenticated

class ViewSet(PermissionMixin, viewsets.GenericViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    permission_by_actions = {
        "create": (IsAuthenticated),
        "list": (AllowAny),
        "retrieve": (AllowAny),
        "update": (IsAuthenticated),
        "partial_update": (IsAuthenticated),
        "destroy": (IsAuthenticated),
        "update_extra_profile": (IsAuthenticated), # Not auto completed
    }

    @action(methods=["POST"], detail=True)
    def update_extra_profile(self, request, pk=None):
        serializer = self.get_serializer()
        return Response(serializer.data)
```

### SessionMiddleware

Use session data within the request lifecycle by adding `SessionMiddleware`.

```python
from rest_framework import viewsets
from djangorestframework_dango.middleware import SessionMiddleware

class ViewSet(viewsets.GenericViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

    def list_queryset(self, queryset: QuerySetType[Model]):
        session = SessionMiddleware.get_session()
        session["current_user"] = self.request.user
        return queryset

class Model:
    @property
    def current_user(self):
        session = SessionMiddleware.get_session()
        return session["current_user"]
```
