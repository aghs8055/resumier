import logging

from celery import shared_task

from profiles.models import ResumeUpload
from profiles.services import ResumeConversionService
from common.enums import ProcessStatus


logger = logging.getLogger(__name__)


@shared_task
def process_resume_upload_task(resume_upload_id: int) -> dict:
    """
    Celery task to process a single resume upload.
    
    Args:
        resume_upload_id: ID of the ResumeUpload instance to process
        
    Returns:
        Dictionary with processing result
    """
    try:
        resume_upload = ResumeUpload.objects.get(id=resume_upload_id)
    except ResumeUpload.DoesNotExist:
        logger.error(f"ResumeUpload with id {resume_upload_id} not found")
        return {"success": False, "error": f"ResumeUpload {resume_upload_id} not found"}
    
    if resume_upload.process_status not in [ProcessStatus.PENDING.value, ProcessStatus.FAILED.value]:
        logger.info(f"ResumeUpload {resume_upload_id} is not in pending or failed status, skipping")
        return {"success": False, "error": "Resume is not in pending or failed status"}
    
    conversion_service = ResumeConversionService()
    
    try:
        profile = conversion_service.process_resume_upload(resume_upload)
        logger.info(f"Successfully processed ResumeUpload {resume_upload_id}, created Profile {profile.id}")
        return {
            "success": True,
            "resume_upload_id": resume_upload_id,
            "profile_id": profile.id,
        }
    except Exception as e:
        logger.error(f"Failed to process ResumeUpload {resume_upload_id}: {e}")
        return {
            "success": False,
            "resume_upload_id": resume_upload_id,
            "error": str(e),
        }


@shared_task
def process_pending_resume_uploads() -> dict:
    """
    Celery task to process all pending resume uploads.
    This task can be scheduled to run periodically.
    
    Returns:
        Dictionary with processing results summary
    """
    pending_uploads = ResumeUpload.objects.filter(process_status=ProcessStatus.PENDING.value)
    
    results = {
        "total": pending_uploads.count(),
        "success": 0,
        "failed": 0,
        "errors": [],
    }
    
    conversion_service = ResumeConversionService()
    
    for resume_upload in pending_uploads:
        try:
            profile = conversion_service.process_resume_upload(resume_upload)
            results["success"] += 1
            logger.info(f"Successfully processed ResumeUpload {resume_upload.id}, created Profile {profile.id}")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "resume_upload_id": resume_upload.id,
                "error": str(e),
            })
            logger.error(f"Failed to process ResumeUpload {resume_upload.id}: {e}")
    
    logger.info(
        f"Processed {results['total']} pending resume uploads: "
        f"{results['success']} successful, {results['failed']} failed"
    )
    
    return results


@shared_task
def retry_failed_resume_uploads(max_retries: int = 3) -> dict:
    """
    Celery task to retry processing failed resume uploads.
    
    Args:
        max_retries: Maximum number of times a resume can be retried (not implemented yet, 
                     but could be tracked in the model)
    
    Returns:
        Dictionary with processing results summary
    """
    failed_uploads = ResumeUpload.objects.filter(process_status=ProcessStatus.FAILED.value)
    
    results = {
        "total": failed_uploads.count(),
        "success": 0,
        "failed": 0,
        "errors": [],
    }
    
    conversion_service = ResumeConversionService()
    
    for resume_upload in failed_uploads:
        try:
            # Reset status to pending before retrying
            resume_upload.process_status = ProcessStatus.PENDING.value
            resume_upload.error_message = None
            resume_upload.save()
            
            profile = conversion_service.process_resume_upload(resume_upload)
            results["success"] += 1
            logger.info(f"Successfully retried ResumeUpload {resume_upload.id}, created Profile {profile.id}")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "resume_upload_id": resume_upload.id,
                "error": str(e),
            })
            logger.error(f"Failed to retry ResumeUpload {resume_upload.id}: {e}")
    
    logger.info(
        f"Retried {results['total']} failed resume uploads: "
        f"{results['success']} successful, {results['failed']} still failed"
    )
    
    return results
