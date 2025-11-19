"""
YAML Test Plan Upload and Validation API
"""
from ninja import Router, File
from ninja.files import UploadedFile
from django.http import HttpRequest
from xutils.utils import RespSuccessTempl, RespFailedTempl
from loguru import logger
from yaml_test_plan.validator import validate_yaml_full

router = Router()


@router.post('/upload')
def upload_yaml_test_plan(request: HttpRequest, file: UploadedFile = File(...)):
    """
    Upload and validate YAML test plan file using comprehensive validation
    Returns file content with detailed error information including line numbers
    """
    try:
        # Read file content
        content = file.read().decode('utf-8')
        
        # Split content into lines for frontend display
        lines = content.split('\n')
        
        # Use comprehensive YAML validation from yaml_test_plan.validator
        is_valid, errors = validate_yaml_full(content)
        
        # If validation failed
        if not is_valid:
            resp = RespFailedTempl()
            resp.code = 400
            resp.message = "YAML validation failed"
            resp.data = {
                "file_name": file.name,
                "file_size": file.size,
                "file_content": content,
                "lines": lines,
                "errors": errors,
                "error_count": len(errors)
            }
            return resp.as_dict()
        
        # Success
        resp = RespSuccessTempl()
        resp.data = {
            "file_name": file.name,
            "file_size": file.size,
            "file_content": content,
            "lines": lines,
            "message": "File uploaded and validated successfully"
        }
        return resp.as_dict()
        
    except Exception as e:
        logger.error(f"Error uploading YAML file: {e}")
        resp = RespFailedTempl()
        resp.code = 500
        resp.message = f"Internal server error: {str(e)}"
        return resp.as_dict()

