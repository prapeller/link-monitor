import fastapi as fa
from celery.result import AsyncResult
from fastapi.responses import JSONResponse

router = fa.APIRouter()


@router.get("/{task_id}")
def tasks_celery_get_task_status(
        task_id: str,
):
    task_result = AsyncResult(task_id)

    return JSONResponse({
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    })
