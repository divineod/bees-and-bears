from rest_framework import permissions


class IsInstaller(permissions.BasePermission):
    """
    Permission class that only allows access to users with INSTALLER role.
    """

    message = "Only installers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_installer
        )


class IsInstallerOrOwner(permissions.BasePermission):
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_installer:
            return True

        if request.user.is_customer:
            if (
                not hasattr(request.user, "customer_profile")
                or not request.user.customer_profile
            ):
                return False

            if obj.__class__.__name__ == "Customer":
                return obj.id == request.user.customer_profile.id

            if obj.__class__.__name__ == "LoanOffer":
                return obj.customer.id == request.user.customer_profile.id

        return False


class IsSuperuserOrInstaller(permissions.BasePermission):
    message = "Only superusers and installers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_installer)
        )
