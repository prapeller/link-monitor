import fastapi as fa

from services.keycloak.keycloak import get_admin_token

router = fa.APIRouter()


@router.get("/admin-token")
def admin_token():
    return get_admin_token()
