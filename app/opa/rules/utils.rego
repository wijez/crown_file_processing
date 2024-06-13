package utils

# Scopes
CREATE := "create"
READ := "read"
LIST := "list"
UPDATE := "update"
DELETE := "delete"

is_resource_owner {
    input.auth.user.id == input.resource.owner.id
}