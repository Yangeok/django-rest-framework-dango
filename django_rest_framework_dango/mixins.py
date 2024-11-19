from typing import (
    Dict,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    Type,
    TypedDict,
    TypeVar,
)

from django.db.models import Model, QuerySet
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from typing_extensions import TypedDict

_T = TypeVar("_T", bound=Model)

# Define actions as a Literal for strict type checking
ViewSetAction = Literal[
    "list", "retrieve", "create", "update", "partial_update", "destroy"
]


# TypedDict for serializer_class_by_actions to ensure auto-completion
class SerializerClassByAction(TypedDict, total=False):
    list: Type[Serializer]
    retrieve: Type[Serializer]
    create: Type[Serializer]
    update: Type[Serializer]
    partial_update: Type[Serializer]
    destroy: Type[Serializer]


class ActionMixin:
    """A mixin class that provides utility methods for actions.

    This mixin provides check methods for each REST API action.
    """

    action: ViewSetAction

    def is_create_action(self) -> bool:
        """Check if the current action is create."""
        return "create" == self.action

    def is_retrieve_action(self) -> bool:
        return "retrieve" == self.action

    def is_list_action(self) -> bool:
        return "list" == self.action

    def is_update_action(self) -> bool:
        return "update" == self.action

    def is_partial_update_action(self) -> bool:
        return "partial_update" == self.action

    def is_destroy_action(self) -> bool:
        return "destroy" == self.action


class QuerySetType(Generic[_T], QuerySet):
    def __iter__(self) -> Iterable[_T]:
        pass

    def first(self) -> Optional[_T]:
        pass


class QuerysetMixin(ActionMixin, Generic[_T]):
    """A mixin class for customizing querysets.

    Allows returning different querysets for each action.
    """

    # Properties for auto-completion
    def list_queryset(self, queryset: QuerySetType[_T]) -> QuerySetType[_T]:
        raise NotImplementedError

    def retrieve_queryset(self, queryset: QuerySetType[_T]) -> QuerySetType[_T]:
        raise NotImplementedError

    def create_queryset(self, queryset: QuerySetType[_T]) -> QuerySetType[_T]:
        raise NotImplementedError

    def update_queryset(self, queryset: QuerySetType[_T]) -> QuerySetType[_T]:
        raise NotImplementedError

    def partial_update_queryset(self, queryset: QuerySetType[_T]) -> QuerySetType[_T]:
        raise NotImplementedError

    def destroy_queryset(self, queryset: QuerySetType[_T]) -> QuerySetType[_T]:
        raise NotImplementedError

    def get_queryset(self) -> QuerySetType[_T]:
        """Returns a custom queryset based on the current action.

        Returns:
            QuerySetType[_T]: The filtered queryset.
        """
        queryset: QuerySetType[_T] = super().get_queryset()

        if self.is_create_action and hasattr(self, "create_queryset"):
            queryset = self.create_queryset(queryset)
        elif self.is_retrieve_action() and hasattr(self, "retrieve_queryset"):
            queryset = self.retrieve_queryset(queryset)
        elif self.is_list_action() and hasattr(self, "list_queryset"):
            queryset = self.list_queryset(queryset)
        elif self.is_update_action() and hasattr(self, "update_queryset"):
            queryset = self.update_queryset(queryset)
        elif self.is_partial_update_action() and hasattr(
            self, "partial_update_queryset"
        ):
            queryset = self.partial_update_queryset(queryset)
        elif self.is_destroy_action() and hasattr(self, "destroy_queryset"):
            queryset = self.destroy_queryset(queryset)
        elif hasattr(self, f"{self.action}_queryset"):
            queryset_method = getattr(self, f"{self.action}_queryset")
            queryset = queryset_method(queryset)

        return queryset


class SerializerMixin:
    """A mixin class for serializer selection.

    Allows using different serializers for each action.
    """

    serializer_class: Type[Serializer]
    serializer_class_by_actions: SerializerClassByAction
    action: ViewSetAction
    request: Request

    def get_serializer_class(self) -> Type[Serializer]:
        """Returns a serializer class based on the current action.

        Returns:
            Type[Serializer]: The serializer class to use.
        """
        if hasattr(self, "serializer_class_by_actions"):
            serializer_class = self.serializer_class_by_actions.get(
                self.action, self.serializer_class
            )
            if isinstance(serializer_class, dict):
                return serializer_class.get(self.request.version)
            return serializer_class
        return self.serializer_class


class PermissionByActions(TypedDict, total=False):
    list: tuple[Type[BasePermission]]
    retrieve: tuple[Type[BasePermission]]
    create: tuple[Type[BasePermission]]
    update: tuple[Type[BasePermission]]
    partial_update: tuple[Type[BasePermission]]
    destroy: tuple[Type[BasePermission]]


class PermissionMixin:
    """A mixin class for permission configuration.

    Allows applying different permissions for each action.
    """

    permission_classes: List[Type[BasePermission]]
    permission_by_actions: PermissionByActions
    action: ViewSetAction

    def get_permissions(self) -> List[BasePermission]:
        """Returns a list of permission instances based on the current action.

        Returns:
            List[BasePermission]: List of permission instances.
        """
        permission_classes = self.permission_classes

        if hasattr(self, "permission_by_actions"):
            permission_classes = self.permission_by_actions.get(
                self.action, self.permission_classes
            )

        return [permission() for permission in permission_classes]


class DangoMixin(QuerysetMixin, SerializerMixin, PermissionMixin):
    """A convenience mixin class that combines QuerysetMixin, SerializerMixin, and PermissionMixin."""

    pass
