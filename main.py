import uvicorn
from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.dependencies import get_current_user_dependency
from database import Base, engine
from database.models import init_models
from routers.v1 import auth as v1_auth
from routers.v1 import link_url_domains as v1_link_url_domains
from routers.v1 import linkchecks as v1_linkchecks
from routers.v1 import links as v1_links
from routers.v1 import page_url_domains as v1_page_url_domains
from routers.v1 import postgres as v1_postgres
from routers.v1 import reports as v1_reports
from routers.v1 import tasks as v1_tasks
from routers.v1 import users as v1_users
from routers.v2 import link_url_domains as v2_link_url_domains
from routers.v2 import links as v2_links
from routers.v2 import reports as v2_reports

init_models()

#  |  |  |
# \/ \/ \/ the following line will create tables according to database.models inherited from Base
Base.metadata.create_all(bind=engine)

app = FastAPI(
    swagger_ui_init_oauth={
        # If you are using pkce (which you should)
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.KEYCLOAK_CLIENT_ID_APP,
    }
)
app.mount('/static', StaticFiles(directory='static'), name='static')

#  |  |  |
# \/ \/ \/ routes that require header 'Authentication': 'Bearer token'

# v1 router

v1_auth_router = APIRouter(dependencies=[Depends(get_current_user_dependency)])

v1_auth_router.include_router(v1_users.router, prefix='/users',
                              tags=['users'])
v1_auth_router.include_router(v1_links.router, prefix='/links',
                              tags=['links'])
v1_auth_router.include_router(v1_linkchecks.router, prefix='/linkchecks',
                              tags=['linkchecks'])
v1_auth_router.include_router(v1_reports.router, prefix='/reports',
                              tags=['reports'])
v1_auth_router.include_router(v1_link_url_domains.router, prefix='/link_url_domains',
                              tags=['link_url_domains'])
v1_auth_router.include_router(v1_page_url_domains.router, prefix='/page_url_domains',
                              tags=['page_url_domains'])
v1_auth_router.include_router(v1_tasks.router, prefix='/tasks',
                              tags=['tasks'])
v1_auth_router.include_router(v1_postgres.router, prefix='/postgres',
                              tags=['postgres'])

# v2 router

v2_auth_router = APIRouter(dependencies=[Depends(get_current_user_dependency)])

v2_auth_router.include_router(v2_links.router, prefix='/links',
                              tags=['links'])
v2_auth_router.include_router(v2_link_url_domains.router, prefix='/link_url_domains',
                              tags=['link_url_domains'])
v2_auth_router.include_router(v2_reports.router, prefix='/reports',
                              tags=['reports'])

#  |  |  |
# \/ \/ \/ public routes without authentication

v1_public_router = APIRouter()

v1_public_router.include_router(v1_auth.router, prefix='/auth',
                                tags=['auth'])

#  |  |  |
# \/ \/ \/ adding routers to app

v1_api_router = APIRouter(default_response_class=JSONResponse)
v1_api_router.include_router(v1_auth_router)
v1_api_router.include_router(v1_public_router)

v2_api_router = APIRouter()
v2_api_router.include_router(v2_auth_router)

app.include_router(v1_api_router, prefix="/api/v1")
app.include_router(v2_api_router, prefix="/api/v2")

if __name__ == "__main__":
    uvicorn.run('main:app', host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)
