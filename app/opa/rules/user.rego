package user

import future.keywords.if
import future.keywords.contains
import data.utils

default allow = false

is_admin {
    input.resource["role"] == "ADMIN"
}

is_super_admin {
    input.auth.user.role == "SUPER_ADMIN"
}

is_resource_super_admin {
    input.resource["role"] == "SUPER_ADMIN"
}

# Super admin permissions, ensuring they cannot create, delete, or update other super admins
allow {
    is_super_admin
    input.scope == utils.CREATE
    not is_resource_super_admin
}

allow {
    is_super_admin
    input.scope == utils.DELETE
    not is_resource_super_admin
}

allow {
    is_super_admin
    input.scope == utils.UPDATE
    not is_resource_super_admin
}


allow {
    is_super_admin
    input.scope == utils.LIST
}

# Admin permissions, ensuring they cannot create, delete, or update other admins or super admins
allow {
    input.auth.user.role == "ADMIN"
    input.scope == utils.CREATE
    not is_admin
    not is_resource_super_admin
}

allow {
    input.auth.user.role == "ADMIN"
    input.scope == utils.DELETE
    not is_admin
    not is_resource_super_admin
}

allow {
    input.auth.user.role == "ADMIN"
    input.scope == utils.UPDATE
    not is_admin
    not is_resource_super_admin
}

allow {
    input.auth.user.role == "ADMIN"
    input.scope == utils.LIST
}

# Reasons for denying access
reasons contains "The requested resource is restricted to admins or super admins." if {
    {utils.CREATE, utils.LIST, utils.UPDATE, utils.DELETE}[input.scope]
    not input.auth.user.role == "ADMIN"
    not is_super_admin
}

reasons contains "Admins cannot create, delete, or update other admins." if {
    {utils.CREATE, utils.DELETE, utils.UPDATE}[input.scope]
    input.auth.user.role == "ADMIN"
    is_admin
}

reasons contains "Admins cannot create, delete, or update super admins." if {
    {utils.CREATE, utils.DELETE, utils.UPDATE}[input.scope]
    input.auth.user.role == "ADMIN"
    is_resource_super_admin
}

reasons contains "Super admins cannot create, delete, update other super admins. Super admins are unique." if {
    {utils.CREATE, utils.DELETE, utils.UPDATE }[input.scope]
    is_super_admin
    is_resource_super_admin
}

result := {
    "allow": allow,
    "reasons": reasons
}
