import logging
import uuid
import json
from enum import Enum
from typing import Union, List, Optional

from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import User
from app.opa.permissions.base_permissions import OpenPolicyAgentPermission
from app.services import UserService

logger = logging.getLogger(__name__)


class UserPermission(OpenPolicyAgentPermission):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opa_url = self.opa_url + '/user/result'

    class UserScopes(Enum):
        CREATE = 'create'
        LIST = 'list'
        READ = 'read'
        UPDATE = 'update'
        DELETE = 'delete'

    @staticmethod
    def get_scopes(request: Request) -> List[UserScopes]:
        user_id = request.path_params.get('user_id', None)

        path = request.url.path
        method = request.method

        scopes_map = {
            (f'/api/users', 'POST'): UserPermission.UserScopes.CREATE,
            (f'/api/users/{user_id}', 'PUT'): UserPermission.UserScopes.UPDATE,
            (f'/api/users', 'GET'): UserPermission.UserScopes.LIST,
            (f'/api/users/{user_id}', 'DELETE'): UserPermission.UserScopes.DELETE,
        }

        return [scopes_map.get((path, method))]

    @classmethod
    async def create(cls, request: Request, session: AsyncSession, user: Union[User, None]) \
            -> List[OpenPolicyAgentPermission]:
        permissions = []
        body_json = await request.json()
        user_id = request.path_params.get('user_id', None)
        scopes_map = {
            'POST': cls.UserScopes.CREATE,
            'PUT': cls.UserScopes.UPDATE,
            'GET': cls.UserScopes.LIST,
            'DELETE': cls.UserScopes.DELETE,
        }

        method = request.method
        path = request.url.path

        if path.startswith(f'/api/users') and method == "POST":
            scope = scopes_map[method]
            perm = cls.create_base_perm(scope=scope.value, user_id=user.id, role=user.role.value)
            await perm.get_resource(session=session, request=request, user=user)
            permissions.append(perm)

        elif path.startswith(f'/api/users/{user_id}') and method == "PUT":
            scope = scopes_map[method]
            perm = cls.create_base_perm(scope=scope.value, user_id=user.id, role=user.role.value)
            await perm.get_resource(session=session, user_id=user_id)
            permissions.append(perm)

        elif path.startswith(f'/api/users/{user_id}') and method == "DELETE":
            scope = scopes_map[method]
            perm = cls.create_base_perm(scope=scope.value, user_id=user.id, role=user.role.value)
            await perm.get_resource(session=session, user_id=user_id)
            permissions.append(perm)

        elif path.startswith(f'/api/users') and method == "GET":
            scope = scopes_map[method]
            perm = cls.create_base_perm(scope=scope.value, user_id=user.id, role=user.role.value)
            await perm.get_resource(session=session)
            permissions.append(perm)

        return permissions

    async def get_resource(self, session: AsyncSession, **kwargs):
        switch_scope = {
            self.UserScopes.CREATE.value: self.handle_create_scope,
            self.UserScopes.LIST.value: self.handle_list_scope,
            self.UserScopes.READ.value: self.handle_read_scope,
            self.UserScopes.UPDATE.value: self.handle_update_scope,
            self.UserScopes.DELETE.value: self.handle_delete_scope,
        }

        handler = switch_scope.get(self.scope)
        if handler:
            await handler(session=session, **kwargs)

    async def handle_create_scope(self, session: AsyncSession, **kwargs):
        request: Optional[Request] = kwargs.get("request", None)
        request_body = await request.body()
        body_json = json.loads(request_body.decode("utf-8"))
        self.payload['input']['resource'] = {
            "role": body_json.get("role", 'MEMBER'),
        }

    async def handle_list_scope(self, session: AsyncSession):
        pass

    async def handle_read_scope(self, session: AsyncSession):
        pass

    async def handle_update_scope(self, session: AsyncSession, **kwargs):
        user_id = kwargs.get("user_id", uuid.uuid4())
        user_service = UserService(session=session)
        user_updated = await user_service.get_one_by_id(user_id=user_id)
        self.payload['input']['resource'] = {
            "role": user_updated.role.value
        }

    async def handle_delete_scope(self, session: AsyncSession, **kwargs):
        user_id = kwargs.get("user_id", uuid.uuid4())
        user_service = UserService(session=session)
        user_deleted = await user_service.get_one_by_id(user_id=user_id)
        print("user_delete", user_deleted.role.value)
        self.payload['input']['resource'] = {
            "role": user_deleted.role.value
        }
