import asyncio
from backend.app.workers.celery_app import celery_app
from backend.app.database.session import AsyncSessionLocal
from backend.app.services.test_executor import test_pipeline_executor
from backend.app.core.logging import logger


@celery_app.task(bind=True, name="run_website_test_task")
def run_website_test_task(self, test_id: str):
    """
    Celery task wrapper to execute asynchronous Playwright test pipeline.
    """
    logger.info(f"Celery worker picked up test task: {test_id}")
    
    async def _async_run():
        async with AsyncSessionLocal() as session:
            await test_pipeline_executor.execute_test(test_id=test_id, db=session)

    try:
        asyncio.run(_async_run())
    except Exception as e:
        logger.error(f"Celery task failed for test_id {test_id}: {e}")
        raise e
