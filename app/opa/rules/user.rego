package user

import future.keywords.if
import future.keywords.contains
import data.utils

default allow = false

allow {
    input.auth.user.role == "ADMIN"
    input.scope == utils.CREATE
}

allow {
    input.auth.user.role == "ADMIN"
    input.scope == utils.LIST
}

allow {
    input.auth.user.role == "ADMIN"
    input.scope == utils.UPDATE
}

allow {
    input.auth.user.role == "ADMIN"
    input.scope == utils.DELETE
}

# Reasons for denying access if the user is not an admin
reasons contains "The requested resource is restricted to admin." if {
    {utils.CREATE, utils.LIST, utils.UPDATE, utils.DELETE}[input.scope]
    not input.auth.user.role == "ADMIN"
}

result := {
    "allow": true,
} if {
    input.auth.user.role == "ADMIN"
} else := {
    "allow": allow,
    "reasons": reasons
}