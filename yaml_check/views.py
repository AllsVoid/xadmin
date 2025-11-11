from django.http import JsonResponse, HttpRequest
from ninja_extra import Router, api_controller
from xadmin_utils import utils
from .validator import YamlValidator
from .line_finder import YamlLineFinder
import json

router = Router()


@router.post('/validate')
def validate_yaml(request: HttpRequest):
    """
    YAML 兼容性验证 API
    
    请求体：
    {
        "yamlData": {
            "metadata": {...},
            "hardware": {...},
            ...
        }
    }
    
    响应：
    {
        "code": 200,
        "msg": "success",
        "data": {
            "success": true/false,
            "error": {
                "code": "E001",
                "message": "...",
                "key": "hardware.cpu",
                "lineNumber": 5
            }
        }
    }
    """
    try:
        # 解析请求体
        body = json.loads(request.body)
        yaml_data = body.get('yamlData')
        
        if not yaml_data:
            resp = utils.RespFailedTempl()
            resp.data = 'Missing yamlData in request body'
            return resp.as_dict()
        
        # 创建验证器并验证
        validator = YamlValidator()
        result = validator.validate(yaml_data)
        
        # 如果验证失败，计算行号
        if not result['success'] and result.get('error'):
            error = result['error']
            error_code = error.get('code', '')
            error_message = error.get('message', '')
            
            # 只对 E002, E101, E102 计算行号
            if error_code in ['E002', 'E101', 'E102']:
                # 提取 key 路径
                key_path = YamlLineFinder.extract_key_from_error(error_message)
                
                if key_path:
                    # 将 YAML 数据转换为文本格式
                    yaml_text = YamlLineFinder.js_to_yaml(yaml_data).rstrip()
                    
                    # 查找行号
                    line_number = YamlLineFinder.find_key_line_number(yaml_text, key_path)
                    
                    if line_number != -1:
                        error['key'] = key_path
                        error['lineNumber'] = line_number
        
        # 返回结果
        resp = utils.RespSuccessTempl()
        resp.data = result
        return resp.as_dict()
        
    except json.JSONDecodeError:
        resp = utils.RespFailedTempl()
        resp.data = 'Invalid JSON in request body'
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'Validation error: {str(e)}'
        return resp.as_dict()