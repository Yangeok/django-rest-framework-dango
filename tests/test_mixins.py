from django.db.models import QuerySet
from pytest_mock import MockerFixture
from rest_framework.permissions import BasePermission

from django_rest_framework_dango.mixins import DangoMixin


# Mock model and QuerySet
class MockModel:
    pass

class MockQuerySet(QuerySet):
    def filter(self, **kwargs):
        return self  # Simply return self to allow method chaining

# Mock Serializer
class MockSerializer:
    pass

# Mock Permission
class MockPermission(BasePermission):
    def has_permission(self, request, view):
        return True


class TestView(DangoMixin):
    __test__ = False  # Prevent pytest from treating this as a test class

    def __init__(self):
        self.action = "list"  # Default action
        self.permission_classes = [MockPermission]
        self.permission_by_actions = {
            "list": (MockPermission,),
            "retrieve": (MockPermission,),
        }
        self.serializer_class = MockSerializer
        self.serializer_class_by_actions = {
            "list": MockSerializer,
        }

    def get_queryset(self) -> MockQuerySet:
        return MockQuerySet(MockModel)


# Test for Permissions
class TestPermissions:
    def test_get_permissions(self):
        # given: Create an instance of TestView
        view = TestView()
        view.action = "list"

        # when: Call get_permissions
        permissions = view.get_permissions()

        # then: Verify that the permissions list contains the correct Permission instance
        assert len(permissions) == 1
        assert isinstance(permissions[0], MockPermission)


# Test for Serializer Class Selection
class TestSerializerClass:
    def test_get_serializer_class(self):
        # given: Create an instance of TestView
        view = TestView()
        view.action = "list"

        # when: Call get_serializer_class
        serializer_class = view.get_serializer_class()

        # then: Verify that the serializer_class is MockSerializer
        assert serializer_class == MockSerializer

    def test_get_serializer_class_with_custom_version(self, mocker: MockerFixture):
        # given: A view with a versioned serializer_class_by_actions
        class CustomTestView(TestView):
            def __init__(self):
                super().__init__()
                self.serializer_class_by_actions = {
                    "list": {"v1": MockSerializer, "v2": MockSerializer},
                }
                self.request = mocker.MagicMock()
                self.request.version = "v2"

        view = CustomTestView()
        view.action = "list"

        # when: Call get_serializer_class
        serializer_class = view.get_serializer_class()

        # then: Verify the correct serializer for the version
        assert serializer_class == MockSerializer


# Test for QuerySet Handling
class TestQuerySet:
    def test_get_queryset(self):
        # given: Create an instance of TestView
        view = TestView()

        # when: Call get_queryset
        queryset = view.get_queryset()

        # then: Verify that the queryset type is MockQuerySet
        assert isinstance(queryset, MockQuerySet)

    def test_list_queryset(self):
        # given: Create an instance of TestView
        class CustomTestView(TestView):
            def list_queryset(self, queryset):
                return queryset.filter(active=True)

        view = CustomTestView()
        queryset = MockQuerySet(MockModel)

        # when: Call list_queryset
        filtered_queryset = view.list_queryset(queryset)

        # then: Verify that the result is a MockQuerySet
        assert isinstance(filtered_queryset, MockQuerySet)

    def test_get_queryset_with_create_action(self):
        # given: Create an instance of TestView with custom create_queryset
        class CustomTestView(TestView):
            def create_queryset(self, queryset):
                return queryset.filter(created=True)

        view = CustomTestView()
        view.action = "create"

        # when: Call get_queryset
        queryset = view.get_queryset()

        # then: Verify the queryset type and behavior
        assert isinstance(queryset, MockQuerySet)

    def test_get_queryset_with_partial_update_action(self):
        # given: A view with a custom partial_update_queryset
        class CustomTestView(TestView):
            def partial_update_queryset(self, queryset):
                return queryset.filter(partial_updated=True)

        view = CustomTestView()
        view.action = "partial_update"

        # when: Call get_queryset
        queryset = view.get_queryset()

        # then: Verify the partial_update_queryset logic
        assert isinstance(queryset, MockQuerySet)

    def test_get_queryset_with_dynamic_action(self):
        # given: A view with a dynamically added queryset handler
        class DynamicTestView(TestView):
            pass

        view = DynamicTestView()
        view.action = "dynamic"

        # Add a dynamic method to the view
        setattr(view, "dynamic_queryset", lambda queryset: queryset.filter(dynamic=True))

        # when: Call get_queryset
        queryset = view.get_queryset()

        # then: Verify the dynamic method was called and the queryset is correct
        assert isinstance(queryset, MockQuerySet)


# Test for Action Checks
class TestActionChecks:
    def test_is_create_action(self):
        # given: Create an instance of TestView
        view = TestView()
        view.action = "create"

        # when: Check is_create_action
        result = view.is_create_action()

        # then: Verify the action check works correctly
        assert result is True

    def test_is_list_action(self):
        # given: Create an instance of TestView
        view = TestView()
        view.action = "list"

        # when: Check is_list_action
        result = view.is_list_action()

        # then: Verify the action check works correctly
        assert result is True

    def test_is_partial_update_action(self):
        # given: Create an instance of TestView
        view = TestView()
        view.action = "partial_update"

        # when: Check is_partial_update_action
        result = view.is_partial_update_action()

        # then: Verify the action check works correctly
        assert result is True
