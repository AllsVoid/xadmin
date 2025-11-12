"""
YAML 测试计划 API
"""
import yaml
from ninja import Router, File
from ninja.files import UploadedFile
from typing import List
from django.db import transaction
from xadmin_db.models import TestPlanYaml
from xadmin_auth.utils_yaml import YamlAnalyzer
from xadmin_auth.yaml_validator import validate_yaml_full  # 新增：导入严格的验证器
from xadmin_auth.auth import TitwBaseAuth

router = Router(tags=["测试计划YAML"])


@router.post("/upload", auth=TitwBaseAuth(), summary="上传YAML测试计划")
def upload_yaml(request, file: UploadedFile = File(...)):
    """
    上传 YAML 测试计划文件
    """
    try:
        # 检查文件类型
        if not file.name.endswith(('.yaml', '.yml')):
            return {
                'code': 400,
                'message': 'Only YAML files (.yaml, .yml) are allowed',
                'data': None
            }
        
        # 检查文件大小 (最大 5MB)
        if file.size > 5 * 1024 * 1024:
            return {
                'code': 400,
                'message': 'File size exceeds 5MB limit',
                'data': None
            }
        
        # 读取文件内容
        content = file.read().decode('utf-8')
        
        # ✅ 步骤 1: 使用 TPGen 标准验证器进行严格验证
        validation_result = validate_yaml_full(content)
        
        if not validation_result['valid']:
            # 构建错误响应
            error_message = validation_result['error_message']
            line_number = validation_result.get('line_number')
            error_code = validation_result.get('error_code')
            
            # 格式化错误消息
            if line_number:
                display_message = f"Line {line_number} [ERROR]\n{error_message}"
            else:
                display_message = f"[ERROR]\n{error_message}"
            
            return {
                'code': 400,
                'message': 'YAML Syntax Errors Found',
                'data': {
                    'error_code': error_code,
                    'error_message': display_message,
                    'line_number': line_number,
                    'errors': [error_message]
                }
            }
        
        # ✅ 步骤 2: 语法验证通过后，进行兼容性分析
        analyzer = YamlAnalyzer()
        analysis_result = analyzer.analyze(content)
        
        if not analysis_result['success']:
            return {
                'code': 400,
                'message': 'YAML parsing failed',
                'data': {
                    'errors': analysis_result.get('parse_errors', [])
                }
            }
        
        # 提取基本信息
        basic_info = analysis_result.get('basic_info', {})
        
        # 保存到数据库
        with transaction.atomic():
            yaml_record = TestPlanYaml.objects.create(
                file_name=file.name,
                file_content=content,
                file_size=file.size,
                plan_name=basic_info.get('plan_name'),
                test_type=basic_info.get('test_type'),
                cpu=basic_info.get('cpu'),
                gpu=basic_info.get('gpu'),
                os_distribution=basic_info.get('os'),
                kernel_version=basic_info.get('kernel'),
                analysis_result=analysis_result,
                validation_status='valid' if analysis_result['is_valid'] else ('warning' if analysis_result['warnings'] else 'error'),
                compatible_machines=analysis_result.get('compatible_machines', []),
                incompatible_machines=analysis_result.get('incompatible_machines', []),
                compatible_count=analysis_result.get('compatible_count', 0),
                incompatible_count=analysis_result.get('incompatible_count', 0),
                warnings=analysis_result.get('warnings', []),
                errors=analysis_result.get('validation_errors', []),
                warning_count=len(analysis_result.get('warnings', [])),
                error_count=len(analysis_result.get('validation_errors', [])),
                missing_fields=analysis_result.get('comparison', {}).get('missing_fields', []),
                type_errors=analysis_result.get('comparison', {}).get('type_errors', []),
                template_name='Smoke Template',
                is_analyzed=True,
                is_validated=True,
                create_user=request.user.id
            )
        
        return {
            'code': 200,
            'message': 'File uploaded and analyzed successfully',
            'data': {
                'id': yaml_record.id,
                'file_name': yaml_record.file_name,
                'basic_info': basic_info,
                'is_valid': analysis_result['is_valid'],
                'compatible_count': analysis_result['compatible_count'],
                'incompatible_count': analysis_result['incompatible_count'],
                'warning_count': len(analysis_result.get('warnings', [])),
                'error_count': len(analysis_result.get('validation_errors', []))
            }
        }
    
    except Exception as e:
        return {
            'code': 500,
            'message': f'Server error: {str(e)}',
            'data': None
        }


@router.get("/{id}/analysis", auth=TitwBaseAuth(), summary="获取YAML分析结果")
def get_analysis(request, id: int):
    """
    获取指定 YAML 文件的分析结果
    """
    try:
        yaml_record = TestPlanYaml.objects.get(id=id)
        
        return {
            'code': 200,
            'message': 'Success',
            'data': {
                'id': yaml_record.id,
                'file_name': yaml_record.file_name,
                'file_size': yaml_record.file_size,
                'basic_info': {
                    'plan_name': yaml_record.plan_name,
                    'test_type': yaml_record.test_type,
                    'cpu': yaml_record.cpu,
                    'gpu': yaml_record.gpu,
                    'os': yaml_record.os_distribution,
                    'kernel': yaml_record.kernel_version,
                },
                'validation_status': yaml_record.validation_status,
                'compatible_machines': yaml_record.compatible_machines or [],
                'incompatible_machines': yaml_record.incompatible_machines or [],
                'compatible_count': yaml_record.compatible_count,
                'incompatible_count': yaml_record.incompatible_count,
                'warnings': yaml_record.warnings or [],
                'errors': yaml_record.errors or [],
                'warning_count': yaml_record.warning_count,
                'error_count': yaml_record.error_count,
                'create_time': yaml_record.create_time.isoformat(),
            }
        }
    
    except TestPlanYaml.DoesNotExist:
        return {
            'code': 404,
            'message': 'YAML record not found',
            'data': None
        }
    except Exception as e:
        return {
            'code': 500,
            'message': f'Server error: {str(e)}',
            'data': None
        }


@router.get("/{id}/comparison", auth=TitwBaseAuth(), summary="获取YAML对比结果")
def get_comparison(request, id: int):
    """
    获取 YAML 文件与标准模板的对比结果
    """
    try:
        yaml_record = TestPlanYaml.objects.get(id=id)
        
        # 重新分析以获取详细对比
        analyzer = YamlAnalyzer()
        analysis_result = analyzer.analyze(yaml_record.file_content)
        
        return {
            'code': 200,
            'message': 'Success',
            'data': {
                'id': yaml_record.id,
                'file_name': yaml_record.file_name,
                'user_yaml': yaml_record.file_content,
                'template_yaml': yaml.dump(analysis_result.get('template', {}), default_flow_style=False),
                'comparison': analysis_result.get('comparison', {}),
                'missing_fields': yaml_record.missing_fields or [],
                'type_errors': yaml_record.type_errors or [],
            }
        }
    
    except TestPlanYaml.DoesNotExist:
        return {
            'code': 404,
            'message': 'YAML record not found',
            'data': None
        }
    except Exception as e:
        return {
            'code': 500,
            'message': f'Server error: {str(e)}',
            'data': None
        }


@router.get("/list", auth=TitwBaseAuth(), summary="获取YAML列表")
def list_yaml(request, page: int = 1, page_size: int = 10):
    """
    获取 YAML 测试计划列表
    """
    try:
        offset = (page - 1) * page_size
        
        queryset = TestPlanYaml.objects.all()
        total = queryset.count()
        
        records = queryset[offset:offset + page_size]
        
        data_list = []
        for record in records:
            data_list.append({
                'id': record.id,
                'file_name': record.file_name,
                'file_size': record.file_size,
                'plan_name': record.plan_name,
                'test_type': record.test_type,
                'cpu': record.cpu,
                'gpu': record.gpu,
                'validation_status': record.validation_status,
                'compatible_count': record.compatible_count,
                'incompatible_count': record.incompatible_count,
                'warning_count': record.warning_count,
                'error_count': record.error_count,
                'create_time': record.create_time.isoformat(),
            })
        
        return {
            'code': 200,
            'message': 'Success',
            'data': {
                'list': data_list,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        }
    
    except Exception as e:
        return {
            'code': 500,
            'message': f'Server error: {str(e)}',
            'data': None
        }


@router.delete("/{id}", auth=TitwBaseAuth(), summary="删除YAML记录")
def delete_yaml(request, id: int):
    """
    删除指定的 YAML 记录
    """
    try:
        yaml_record = TestPlanYaml.objects.get(id=id)
        yaml_record.delete()
        
        return {
            'code': 200,
            'message': 'YAML record deleted successfully',
            'data': None
        }
    
    except TestPlanYaml.DoesNotExist:
        return {
            'code': 404,
            'message': 'YAML record not found',
            'data': None
        }
    except Exception as e:
        return {
            'code': 500,
            'message': f'Server error: {str(e)}',
            'data': None
        }

