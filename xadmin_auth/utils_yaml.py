"""
YAML 测试计划解析和验证工具
"""
import yaml
import re
from typing import Dict, List, Any, Tuple


# 模拟的机器数据库
MOCK_MACHINES = [
    {"id": 1, "name": "AMD-TEST-001", "motherboard": "ASUS ROG", "cpu": "Ryzen Threadripper", "gpu": "Radeon RX 7900 Series", "status": "Available"},
    {"id": 2, "name": "AMD-TEST-002", "motherboard": "MSI MPG", "cpu": "Ryzen Threadripper", "gpu": "Radeon RX 7900 Series", "status": "Available"},
    {"id": 3, "name": "AMD-TEST-003", "motherboard": "Gigabyte Aorus", "cpu": "EPYC", "gpu": "Radeon Pro W7800", "status": "Available"},
    {"id": 4, "name": "AMD-TEST-004", "motherboard": "ASRock Phantom", "cpu": "Ryzen 9", "gpu": "Radeon RX 6800 Series", "status": "In Use"},
    {"id": 5, "name": "AMD-TEST-005", "motherboard": "ASUS TUF", "cpu": "Ryzen 7", "gpu": "Radeon RX 6800 Series", "status": "Available"},
]

# 标准 YAML 模板
SMOKE_TEMPLATE = """
test_plan:
  name: "Smoke Test"
  description: "Basic smoke test for GPU functionality"
  
hardware:
  cpu: "Ryzen Threadripper"
  gpu: "Radeon RX 7900 Series"
  gpu_version: "24.10.1621"  # GPU firmware version
  
environment:
  os: "Ubuntu 22.04"
  kernel: "6.2"
  driver: "amdgpu-install 24.10"
  
test_cases:
  - name: "GPU Detection"
    command: "lspci | grep VGA"
    expected: "Contains AMD/ATI"
  
  - name: "Driver Load"
    command: "lsmod | grep amdgpu"
    expected: "Module loaded"
  
  - name: "ROCm Info"
    command: "rocm-smi"
    expected: "GPU info displayed"
"""


class YamlAnalyzer:
    """YAML 文件分析器"""
    
    def __init__(self):
        self.machines = MOCK_MACHINES
        self.template = yaml.safe_load(SMOKE_TEMPLATE)
    
    def parse_yaml(self, content: str) -> Tuple[Dict[str, Any], List[str]]:
        """
        解析 YAML 内容
        返回: (parsed_data, errors)
        """
        errors = []
        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                errors.append("YAML content must be a dictionary")
                return {}, errors
            return data, errors
        except yaml.YAMLError as e:
            errors.append(f"YAML parsing error: {str(e)}")
            return {}, errors
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            return {}, errors
    
    def validate_yaml(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        验证 YAML 数据结构
        返回: (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # 检查必需的顶级字段
        required_top_level = ['test_plan', 'hardware', 'environment', 'test_cases']
        for field in required_top_level:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # 验证 test_plan
        if 'test_plan' in data:
            test_plan = data['test_plan']
            if not isinstance(test_plan, dict):
                errors.append("test_plan must be a dictionary")
            else:
                for field in ['name', 'description']:
                    if field not in test_plan or not test_plan[field]:
                        warnings.append(f"test_plan.{field} is missing or empty")
        
        # 验证 hardware
        if 'hardware' in data:
            hardware = data['hardware']
            if not isinstance(hardware, dict):
                errors.append("hardware must be a dictionary")
            else:
                required_hardware = ['cpu', 'gpu']
                for field in required_hardware:
                    if field not in hardware or not hardware[field]:
                        errors.append(f"hardware.{field} is required and cannot be empty")
                
                # GPU 版本警告
                if 'gpu_version' not in hardware or not hardware.get('gpu_version'):
                    warnings.append("GPU firmware version (gpu_version) is not specified - this may affect compatibility checks")
        
        # 验证 environment
        if 'environment' in data:
            env = data['environment']
            if not isinstance(env, dict):
                errors.append("environment must be a dictionary")
            else:
                for field in ['os', 'kernel', 'driver']:
                    if field not in env or not env[field]:
                        warnings.append(f"environment.{field} is missing or empty")
        
        # 验证 test_cases
        if 'test_cases' in data:
            test_cases = data['test_cases']
            if not isinstance(test_cases, list):
                errors.append("test_cases must be a list")
            elif len(test_cases) == 0:
                warnings.append("test_cases list is empty")
            else:
                for i, tc in enumerate(test_cases):
                    if not isinstance(tc, dict):
                        errors.append(f"test_cases[{i}] must be a dictionary")
                    else:
                        for field in ['name', 'command', 'expected']:
                            if field not in tc or not tc[field]:
                                warnings.append(f"test_cases[{i}].{field} is missing or empty")
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    def find_compatible_machines(self, data: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """
        查找兼容和不兼容的机器
        返回: (compatible_machines, incompatible_machines)
        """
        hardware = data.get('hardware', {})
        target_cpu = hardware.get('cpu', '')
        target_gpu = hardware.get('gpu', '')
        
        compatible = []
        incompatible = []
        
        for machine in self.machines:
            reasons = []
            
            # 检查 CPU
            if target_cpu and machine['cpu'] != target_cpu:
                reasons.append(f"CPU mismatch: expected {target_cpu}, found {machine['cpu']}")
            
            # 检查 GPU
            if target_gpu and machine['gpu'] != target_gpu:
                reasons.append(f"GPU mismatch: expected {target_gpu}, found {machine['gpu']}")
            
            if reasons:
                incompatible.append({
                    **machine,
                    'incompatible_reasons': reasons
                })
            else:
                compatible.append(machine)
        
        return compatible, incompatible
    
    def compare_with_template(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        与标准模板对比，找出缺失和错误的字段
        返回: comparison_result
        """
        missing_fields = []
        type_errors = []
        
        def check_structure(template: Any, user: Any, path: str = ""):
            if isinstance(template, dict):
                if not isinstance(user, dict):
                    type_errors.append({
                        'path': path,
                        'expected': 'dictionary',
                        'actual': type(user).__name__
                    })
                    return
                
                for key, value in template.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if key not in user:
                        missing_fields.append(current_path)
                    elif user[key] is None or user[key] == '':
                        missing_fields.append(current_path)
                    else:
                        check_structure(value, user[key], current_path)
            
            elif isinstance(template, list):
                if not isinstance(user, list):
                    type_errors.append({
                        'path': path,
                        'expected': 'list',
                        'actual': type(user).__name__
                    })
                    return
                
                if len(template) > 0 and len(user) > 0:
                    # 检查列表第一个元素的结构
                    check_structure(template[0], user[0], f"{path}[0]")
        
        check_structure(self.template, user_data)
        
        return {
            'missing_fields': missing_fields,
            'type_errors': type_errors,
            'has_issues': len(missing_fields) > 0 or len(type_errors) > 0
        }
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        完整分析 YAML 文件
        返回: analysis_result
        """
        # 解析 YAML
        data, parse_errors = self.parse_yaml(content)
        
        if parse_errors:
            return {
                'success': False,
                'parse_errors': parse_errors,
                'data': None
            }
        
        # 验证结构
        is_valid, validation_errors, warnings = self.validate_yaml(data)
        
        # 查找兼容机器
        compatible, incompatible = self.find_compatible_machines(data)
        
        # 与模板对比
        comparison = self.compare_with_template(data)
        
        # 提取基本信息
        test_plan = data.get('test_plan', {})
        hardware = data.get('hardware', {})
        environment = data.get('environment', {})
        
        return {
            'success': True,
            'is_valid': is_valid,
            'data': data,
            'basic_info': {
                'plan_name': test_plan.get('name'),
                'description': test_plan.get('description'),
                'test_type': test_plan.get('type', 'Unknown'),
                'cpu': hardware.get('cpu'),
                'gpu': hardware.get('gpu'),
                'gpu_version': hardware.get('gpu_version'),
                'os': environment.get('os'),
                'kernel': environment.get('kernel'),
                'driver': environment.get('driver'),
            },
            'validation_errors': validation_errors,
            'warnings': warnings,
            'compatible_machines': compatible,
            'incompatible_machines': incompatible,
            'compatible_count': len(compatible),
            'incompatible_count': len(incompatible),
            'comparison': comparison,
            'template': self.template
        }

