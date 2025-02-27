from rest_framework import permissions

class AccessByCreatingUserPermission(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        # if not request.user.is_staff:
        #     return False
        print(self)
        print(request)
        return super().has_permission(request, view)

    # def has_permission(self, request, view):
    #     user = request.user
    #     print(user.get_all_permissions())
    #     if user.is_staff:
    #         if user.has_perm("proposals.add_proposal"): #"app_name.verb_modelname"
    #             return True
    #         if user.has_perm("proposals.delete_proposal"):
    #             return True
    #         if user.has_perm("proposals.change_proposal"):
    #             return True
    #         if user.has_perm("proposals.view_proposal"):
    #             return True
    #         return False
    #     return False
