import logging
import traceback

import fastapi as fa
import requests

from core.config import settings
from database.models.user import UserModel
from database.schemas.user import UserCreateSerializer, UserUpdateSerializer

logger = logging.getLogger(name='keycloak')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")
file_handler = logging.FileHandler(f'services/keycloak/keycloak.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

role_linkbuilder = {
    "id": '4f599ca3-6760-42c4-b26e-afd5bb88c095',
    "name": "linkbuilder",
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM_APP,
}

role_head = {
    "id": 'c9354b71-e67b-415d-b80e-63bbdf169979',
    "name": "head",
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM_APP,
}

role_teamlead = {
    "id": '423e1644-d750-42a3-a8e4-4b131849e934',
    "name": "teamlead",
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM_APP,
}

role_seo = {
    "id": '30c590e8-0d86-4ac8-8bef-af1609b29266',
    "name": "seo",
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM_APP,
}

role_content_author = {
    "id": 'ff5777c4-553a-47dc-b422-aefe4b7455f1',
    "name": "content_author",
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM_APP,
}

role_content_teamlead = {
    "id": 'cfa36350-3779-4e5d-b5a0-8a78c1a7139e',
    "name": "content_teamlead",
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM_APP,
}

role_content_head = {
    "id": '0cae18ba-bccb-41a1-86ab-cd96e0be872e',
    "name": "content_head",
    "composite": False,
    "clientRole": False,
    "containerId": settings.KEYCLOAK_REALM_APP,
}


def get_admin_token():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        "client_secret": f"{settings.KEYCLOAK_CLIENT_SECRET_ADMIN}",
        "client_id": f"{settings.KEYCLOAK_CLIENT_ID_ADMIN}",
        "username": f"{settings.KEYCLOAK_USERNAME_ADMIN}",
        "password": f"{settings.KEYCLOAK_PASSWORD_ADMIN}",
        "grant_type": "password",
    }
    try:
        resp = requests.post(
            f'{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM_ADMIN}/protocol/openid-connect/token',
            headers=headers, data=payload)
        return resp.json()
    except Exception as e:
        logger.error(traceback.format_exc())
        raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                               detail=f"keycloak cant get admin token ,{str(e)}")


class KCAdmin():
    def __init__(self):
        self.admin_access_token = get_admin_token()['access_token']
        self.kc_base_url = settings.KEYCLOAK_BASE_URL
        self.kc_realm_app = settings.KEYCLOAK_REALM_APP
        self.kc_client_id_app = settings.KEYCLOAK_CLIENT_ID_APP

    def create_user(self, user_ser: UserCreateSerializer) -> requests.Response | None:
        try:
            resp = requests.post(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/users",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
                json={
                    'email': user_ser.email,
                    'firstName': user_ser.first_name,
                    'lastName': user_ser.last_name,
                    'enabled': True,
                }
            )
            return resp
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f"keycloak cant create user, {str(e)}")

    def update_user_credentials(self, user: UserModel, user_ser: UserUpdateSerializer) -> requests.Response | None:
        try:
            user_ser_credentials = {}
            email = user_ser.email
            if email is not None:
                user_ser_credentials['email'] = email
            first_name = user_ser.first_name
            if first_name is not None:
                user_ser_credentials['firstName'] = first_name
            last_name = user_ser.last_name
            if last_name is not None:
                user_ser_credentials['lastName'] = last_name

            if user_ser_credentials:
                resp = requests.put(
                    url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/users/{user.uuid}",
                    headers={"Authorization": f"Bearer {self.admin_access_token}"},
                    json=user_ser_credentials
                )
                return resp
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f'keycloak cant update user {user}, {str(e)}')

    def send_request_verify_email_and_reset_password(self, user: UserModel) -> requests.Response | None:
        try:
            resp = requests.put(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/users/{user.uuid}/execute-actions-email"
                    f"?client_id={self.kc_client_id_app}"
                    f"&redirect_uri={settings.BASE_URL}",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
                json=['VERIFY_EMAIL', 'UPDATE_PASSWORD']
            )
            return resp
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f"keycloak cant send verify email to user, {str(e)}")

    def deactivate_user(self, user: UserModel) -> requests.Response | None:
        try:
            resp = requests.put(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/users/{user.uuid}",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
                json={'enabled': False}
            )
            return resp
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f"keycloak cant deactivate user {user}, {str(e)}")

    def activate_user(self, user: UserModel) -> requests.Response | None:
        try:
            resp = requests.put(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/users/{user.uuid}",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
                json={'enabled': True}
            )
            return resp
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f"keycloak cant activate user {user}, {str(e)}")

    def remove_user(self, user: UserModel) -> requests.Response | None:
        try:
            resp = requests.delete(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/users/{user.uuid}",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
            )
            return resp
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f"keycloak cant remove user {user}, {str(e)}")

    def get_user_uuid_by_email(self, email: str) -> str:
        try:
            resp = requests.get(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/"
                    f"users?email={email}",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
            )
            user_id = resp.json()[0]['id']
            return user_id
        except IndexError:
            return ''

    def get_user_roles(self, user: UserModel) -> dict | None:
        try:
            resp = requests.get(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/"
                    f"users/{user.uuid}/role-mappings/realm",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
            )
            roles_dict = resp.json()
            return roles_dict
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f"keycloak cant get roles for {user}, {str(e)}")

    def set_user_role(self, user: UserModel, role: dict) -> requests.Response | None:
        try:
            resp = requests.post(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/"
                    f"users/{user.uuid}/role-mappings/realm",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
                json=[role]
            )
            return resp
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f"keycloak cant set role '{role.get('name')}' for {user}, {str(e)}")

    def delete_user_role(self, user: UserModel, role: dict) -> requests.Response | None:
        try:
            resp = requests.delete(
                url=f"{self.kc_base_url}/admin/realms/{self.kc_realm_app}/"
                    f"users/{user.uuid}/role-mappings/realm",
                headers={"Authorization": f"Bearer {self.admin_access_token}"},
                json=[role_head]
            )
            return resp
        except Exception as e:
            logger.error(traceback.format_exc())
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=f"keycloak cant delete role '{role.get('name')}' for {user}, {str(e)}")

    def set_role_head(self, user: UserModel) -> requests.Response | None:
        return self.set_user_role(user, role_head)

    def delete_role_head(self, user: UserModel) -> requests.Response | None:
        return self.delete_user_role(user, role_head)

    def set_role_teamlead(self, user: UserModel) -> requests.Response | None:
        return self.set_user_role(user, role_teamlead)

    def delete_role_teamlead(self, user: UserModel) -> requests.Response | None:
        return self.delete_user_role(user, role_teamlead)

    def set_role_seo(self, user: UserModel) -> requests.Response | None:
        return self.set_user_role(user, role_seo)

    def delete_role_seo(self, user: UserModel) -> requests.Response | None:
        return self.delete_user_role(user, role_seo)

    def set_role_content_teamlead(self, user: UserModel) -> requests.Response | None:
        return self.set_user_role(user, role_content_teamlead)

    def delete_role_content_teamlead(self, user: UserModel) -> requests.Response | None:
        return self.delete_user_role(user, role_content_teamlead)

    def set_role_content_head(self, user: UserModel) -> requests.Response | None:
        return self.set_user_role(user, role_content_head)

    def delete_role_content_head(self, user: UserModel) -> requests.Response | None:
        return self.delete_user_role(user, role_content_head)

    def set_role_content_author(self, user: UserModel) -> requests.Response | None:
        return self.set_user_role(user, role_content_author)

    def delete_role_content_author(self, user: UserModel) -> requests.Response | None:
        return self.delete_user_role(user, role_content_author)

    def set_role_linkbuilder(self, user: UserModel) -> requests.Response | None:
        return self.set_user_role(user, role_linkbuilder)

    def set_user_roles(self, user):
        if user.is_head:
            self.set_role_head(user)
        if user.is_content_head:
            self.set_role_content_head(user)
        if user.is_teamlead:
            self.set_role_teamlead(user)
        if user.is_seo:
            self.set_role_seo(user)
        if user.is_content_teamlead:
            self.set_role_content_teamlead(user)
        if user.is_content_author:
            self.set_role_content_author(user)
        if not user.is_head \
                and not user.is_content_head \
                and not user.is_teamlead \
                and not user.is_seo \
                and not user.is_content_teamlead \
                and not user.is_content_author:
            self.set_role_linkbuilder(user)

    def update_user_roles(self, user: UserModel,
                          user_ser: UserUpdateSerializer | UserCreateSerializer) -> None:
        if user_ser.is_head is True and user.is_head is False:
            self.set_role_head(user)

        if user_ser.is_head is False and user.is_head is True:
            self.delete_role_head(user)

        if user_ser.is_content_head is True and user.is_content_head is False:
            self.set_role_content_head(user)

        if user_ser.is_content_head is False and user.is_content_head is True:
            self.delete_role_content_head(user)

        if user_ser.is_teamlead is True and user.is_teamlead is False:
            self.set_role_teamlead(user)

        if user_ser.is_teamlead is False and user.is_teamlead is True:
            self.delete_role_teamlead(user)

        if user_ser.is_seo is True and user.is_seo is False:
            self.set_role_seo(user)

        if user_ser.is_seo is False and user.is_seo is True:
            self.delete_role_seo(user)

        if user_ser.is_content_teamlead is True and user.is_content_teamlead is False:
            self.set_role_content_teamlead(user)

        if user_ser.is_content_teamlead is False and user.is_content_teamlead is True:
            self.delete_role_content_teamlead(user)

        if user_ser.is_content_author is True and user.is_content_author is False:
            self.set_role_content_author(user)

        if user_ser.is_content_author is False and user.is_content_author is True:
            self.delete_role_content_author(user)
