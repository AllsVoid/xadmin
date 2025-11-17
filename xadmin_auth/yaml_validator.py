"""
YAML 测试计划验证器

基于 TPGen.html 中的 JavaScript 验证逻辑移植
支持完整的语法和兼容性验证
"""

import yaml
from typing import Dict, List, Any, Optional, Tuple


# ============================================================================
# 验证规则配置
# ============================================================================

# E001: 必需的根键（必须存在的字段）
REQUIRED_ROOT_KEYS = [
    # Metadata Section (must)
    'metadata',
    'metadata.generated',
    'metadata.version',
    
    # Hardware Section (must)
    'hardware',
    'hardware.cpu',
    'hardware.gpu',
    'hardware.machines',
    
    # Environment Section (must)
    'environment',
    'environment.os',
    'environment.os.method',
    'environment.kernel',
    'environment.kernel.method',
    
    # Firmware Section (must)
    'firmware',
    'firmware.gpu_version',
    'firmware.comparison',
    
    # Test Suites (must)
    'test_suites'
]

# E002: 必须非空的键
MANDATORY_NON_EMPTY_KEYS = [
    'metadata.generated',
    'metadata.version',
    'hardware.cpu',
    'hardware.gpu',
    'hardware.machines',
    'environment.os.method',
    'environment.kernel.method',
    'firmware.gpu_version',
    'firmware.comparison',
    'test_suites'
]

# E101: 值类型配置
VALUE_TYPE_CONFIG = {
    'metadata.generated': 'string',
    'metadata.version': 'string',
    'hardware.cpu': 'string',
    'hardware.gpu': 'string',
    'hardware.machines': 'array',
    'environment.os.method': 'string',
    'environment.os.os': 'string',
    'environment.os.deployment': 'string',
    'environment.os.machines': 'object',
    'environment.kernel.method': 'string',
    'environment.kernel.type': 'string',
    'environment.kernel.version': 'string',
    'environment.kernel.machines': 'object',
    'firmware.gpu_version': 'string',
    'firmware.comparison': 'boolean',
    'test_suites': 'array'
}

# E102: 值范围配置（白名单）
VALUE_RANGE_CONFIG = {
    'hardware.cpu': [
        'Ryzen Threadripper',
        'Ryzen 9',
        'Ryzen 7',
        'EPYC'
    ],
    'hardware.gpu': [
        'Radeon RX 7900 Series',
        'Radeon RX 6800 Series',
        'Radeon Pro W7800',
        'Radeon Pro W6800'
    ],
    'environment.os.method': ['same', 'individual'],
    'environment.os.os': [
        'Ubuntu 22.04',
        'Ubuntu 20.04',
        'RHEL 8',
        'RHEL 7',
        'Debian 11',
        'CentOS 8',
        'CentOS 7'
    ],
    'environment.os.deployment': [
        'Bare Metal',
        'Container',
        'VM'
    ],
    'environment.kernel.method': ['same', 'individual'],
    'environment.kernel.type': [
        'DKMS',
        'Mainline',
        'Custom Build',
        'LTS'
    ],
    'environment.kernel.version': [
        '6.2',
        '6.1',
        '6.0',
        '5.15',
        '5.10'
    ],
    'firmware.gpu_version': [
        '2024.01',
        '2023.12',
        '2023.07',
        '2023.01',
        '2022.12'
    ]
}

# E300: 无效组合配置
INVALID_COMBO_CONFIG = [
    {
        'name': 'RHEL 7 with LTS Kernel 6.1',
        'when': {
            'environment.os.os': 'RHEL 7',
            'environment.kernel.type': 'LTS',
            'environment.kernel.version': '6.1'
        },
        'action': 'report_error'
    },
    {
        'name': 'RHEL 7 with Mainline Kernel 6.0+',
        'when': {
            'environment.os.os': 'RHEL 7',
            'environment.kernel.type': 'Mainline',
            'environment.kernel.version': ['6.0', '6.1', '6.2']
        },
        'action': 'report_error'
    }
]

# 字段友好名称映射
FIELD_NAMES = {
    # Metadata
    'metadata': 'Metadata',
    'metadata.generated': 'Generated Time',
    'metadata.version': 'Version',
    
    # Hardware
    'hardware': 'Hardware',
    'hardware.cpu': 'CPU',
    'hardware.gpu': 'GPU',
    'hardware.machines': 'Machines',
    
    # Environment - OS
    'environment': 'Environment',
    'environment.os': 'Operating System',
    'environment.os.method': 'OS Configuration Method',
    'environment.os.os': 'Operating System',
    'environment.os.deployment': 'Deployment Method',
    'environment.os.machines': 'OS Machines Configuration',
    
    # Environment - Kernel
    'environment.kernel': 'Kernel',
    'environment.kernel.method': 'Kernel Configuration Method',
    'environment.kernel.type': 'Kernel Type',
    'environment.kernel.version': 'Kernel Version',
    'environment.kernel.machines': 'Kernel Machines Configuration',
    
    # Firmware
    'firmware': 'Firmware',
    'firmware.gpu_version': 'GPU Firmware Version',
    'firmware.comparison': 'Version Comparison Testing',
    
    # Test Suites
    'test_suites': 'Test Suites'
}


# ============================================================================
# 辅助函数
# ============================================================================

def get_nested_value(obj: Dict, path: str) -> Any:
    """
    使用点号路径获取嵌套值
    例如: get_nested_value(data, 'hardware.cpu')
    """
    keys = path.split('.')
    current = obj
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def is_empty(value: Any) -> bool:
    """检查值是否为空"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == '':
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    return False


def get_value_type(value: Any) -> str:
    """获取值的类型字符串"""
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, int) or isinstance(value, float):
        return 'number'
    if isinstance(value, str):
        return 'string'
    if isinstance(value, list):
        return 'array'
    if isinstance(value, dict):
        return 'object'
    return 'unknown'


def get_friendly_field_name(field_path: str) -> str:
    """获取字段的友好名称"""
    return FIELD_NAMES.get(field_path, field_path)


def find_line_number_in_yaml(yaml_content: str, field_path: str) -> Optional[int]:
    """
    在 YAML 文本中查找字段所在的行号
    """
    if not yaml_content:
        return None
    
    # 提取最后一级的键名
    keys = field_path.split('.')
    last_key = keys[-1]
    
    lines = yaml_content.split('\n')
    for i, line in enumerate(lines):
        # 匹配 "key:" 或 "key: value" 模式
        if f'{last_key}:' in line:
            return i + 1  # 返回 1-based 行号
    
    return None


# ============================================================================
# 验证函数
# ============================================================================

def validate_yaml_syntax(yaml_content: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    验证 YAML 语法
    
    返回: (is_valid, error_message, line_number)
    """
    try:
        yaml.safe_load(yaml_content)
        return True, None, None
    except yaml.YAMLError as e:
        error_msg = str(e)
        line_number = None
        
        # 尝试提取行号
        if hasattr(e, 'problem_mark'):
            line_number = e.problem_mark.line + 1  # PyYAML 使用 0-based 行号
        
        return False, f"Invalid YAML syntax. Expected key-value pair (key: value) or list item (- item).", line_number
    except Exception as e:
        return False, f"YAML parsing error: {str(e)}", None


def validate_required_root_keys(yaml_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    E001: 验证必需的根键
    """
    for key in REQUIRED_ROOT_KEYS:
        value = get_nested_value(yaml_data, key)
        if value is None:
            friendly_name = get_friendly_field_name(key)
            return False, f"E001 Unsupported: missing mandatory field \"{friendly_name}\" [{key}]"
    
    # 条件必需字段
    os_method = get_nested_value(yaml_data, 'environment.os.method')
    if os_method == 'same':
        if get_nested_value(yaml_data, 'environment.os.os') is None:
            return False, "E001 Unsupported: missing mandatory field \"Operating System\" [environment.os.os] when method is 'same'"
        if get_nested_value(yaml_data, 'environment.os.deployment') is None:
            return False, "E001 Unsupported: missing mandatory field \"Deployment Method\" [environment.os.deployment] when method is 'same'"
    elif os_method == 'individual':
        if get_nested_value(yaml_data, 'environment.os.machines') is None:
            return False, "E001 Unsupported: missing mandatory field \"OS Machines Configuration\" [environment.os.machines] when method is 'individual'"
    
    kernel_method = get_nested_value(yaml_data, 'environment.kernel.method')
    if kernel_method == 'same':
        if get_nested_value(yaml_data, 'environment.kernel.type') is None:
            return False, "E001 Unsupported: missing mandatory field \"Kernel Type\" [environment.kernel.type] when method is 'same'"
        if get_nested_value(yaml_data, 'environment.kernel.version') is None:
            return False, "E001 Unsupported: missing mandatory field \"Kernel Version\" [environment.kernel.version] when method is 'same'"
    elif kernel_method == 'individual':
        if get_nested_value(yaml_data, 'environment.kernel.machines') is None:
            return False, "E001 Unsupported: missing mandatory field \"Kernel Machines Configuration\" [environment.kernel.machines] when method is 'individual'"
    
    return True, None


def validate_mandatory_non_empty_keys(yaml_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    E002: 验证必需非空的键
    """
    for key in MANDATORY_NON_EMPTY_KEYS:
        value = get_nested_value(yaml_data, key)
        friendly_name = get_friendly_field_name(key)
        
        if value is None:
            return False, f"E002 Unsupported: empty value for \"{friendly_name}\" [{key}]"
        
        if is_empty(value):
            return False, f"E002 Unsupported: empty value for \"{friendly_name}\" [{key}]"
    
    return True, None


def validate_value_types(yaml_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    E101: 验证值类型
    """
    for key, expected_type in VALUE_TYPE_CONFIG.items():
        value = get_nested_value(yaml_data, key)
        
        if value is None:
            continue
        
        actual_type = get_value_type(value)
        
        # 类型映射
        type_map = {
            'string': ['string'],
            'int': ['number'],
            'number': ['number'],
            'boolean': ['boolean'],
            'array': ['array'],
            'object': ['object']
        }
        
        valid_types = type_map.get(expected_type, [expected_type])
        
        if actual_type not in valid_types:
            friendly_name = get_friendly_field_name(key)
            return False, f"E101 Unsupported: value type error for \"{friendly_name}\" [{key}]. Expected {expected_type}, got {actual_type}"
    
    return True, None


def validate_value_ranges(yaml_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    E102: 验证值范围（白名单）
    """
    for key, allowed_values in VALUE_RANGE_CONFIG.items():
        value = get_nested_value(yaml_data, key)
        
        if value is None:
            continue
        
        if value not in allowed_values:
            friendly_name = get_friendly_field_name(key)
            return False, f"E102 Unsupported: invalid value \"{value}\" for \"{friendly_name}\" [{key}]. Must be one of: {', '.join(map(str, allowed_values))}"
    
    return True, None


def validate_invalid_combinations(yaml_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    E300: 验证无效组合
    """
    for combo in INVALID_COMBO_CONFIG:
        all_conditions_met = True
        matched_conditions = []
        
        for key_path, expected_value in combo['when'].items():
            actual_value = get_nested_value(yaml_data, key_path)
            
            # 如果期望值是列表，检查实际值是否在列表中
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    all_conditions_met = False
                    break
                matched_conditions.append(f"[{key_path}]=\"{actual_value}\"")
            else:
                # 使用字符串比较以处理类型不匹配
                if str(actual_value) != str(expected_value):
                    all_conditions_met = False
                    break
                matched_conditions.append(f"[{key_path}]=\"{actual_value}\"")
        
        if all_conditions_met and combo['action'] == 'report_error':
            return False, f"E300 Unsupported: invalid combination detected {' with '.join(matched_conditions)}"
    
    return True, None


# ============================================================================
# 主验证函数
# ============================================================================

def validate_yaml_full(yaml_content: str) -> Dict[str, Any]:
    """
    完整的 YAML 验证（包括语法和兼容性）
    
    返回格式:
    {
        'valid': bool,
        'error_code': str,  # '0' 表示成功, 'E001', 'E002', 'E101', 'E102', 'E300' 表示错误类型
        'error_message': str,
        'line_number': int  # 错误所在行号（如果可用）
    }
    """
    # 步骤 1: 语法验证
    syntax_valid, syntax_error, line_number = validate_yaml_syntax(yaml_content)
    if not syntax_valid:
        return {
            'valid': False,
            'error_code': 'SYNTAX_ERROR',
            'error_message': syntax_error,
            'line_number': line_number
        }
    
    # 解析 YAML
    try:
        yaml_data = yaml.safe_load(yaml_content)
    except Exception as e:
        return {
            'valid': False,
            'error_code': 'PARSE_ERROR',
            'error_message': f"Failed to parse YAML: {str(e)}",
            'line_number': None
        }
    
    # 步骤 2: 必需键验证 (E001)
    valid, error_msg = validate_required_root_keys(yaml_data)
    if not valid:
        # 提取错误代码
        error_code = error_msg.split()[0] if error_msg else 'E001'
        # 查找行号
        field_match = error_msg.split('[')[-1].split(']')[0] if '[' in error_msg else None
        line_num = find_line_number_in_yaml(yaml_content, field_match) if field_match else None
        
        return {
            'valid': False,
            'error_code': error_code,
            'error_message': error_msg,
            'line_number': line_num
        }
    
    # 步骤 3: 非空键验证 (E002)
    valid, error_msg = validate_mandatory_non_empty_keys(yaml_data)
    if not valid:
        error_code = error_msg.split()[0] if error_msg else 'E002'
        field_match = error_msg.split('[')[-1].split(']')[0] if '[' in error_msg else None
        line_num = find_line_number_in_yaml(yaml_content, field_match) if field_match else None
        
        return {
            'valid': False,
            'error_code': error_code,
            'error_message': error_msg,
            'line_number': line_num
        }
    
    # 步骤 4: 值类型验证 (E101)
    valid, error_msg = validate_value_types(yaml_data)
    if not valid:
        error_code = error_msg.split()[0] if error_msg else 'E101'
        field_match = error_msg.split('[')[-1].split(']')[0] if '[' in error_msg else None
        line_num = find_line_number_in_yaml(yaml_content, field_match) if field_match else None
        
        return {
            'valid': False,
            'error_code': error_code,
            'error_message': error_msg,
            'line_number': line_num
        }
    
    # 步骤 5: 值范围验证 (E102)
    valid, error_msg = validate_value_ranges(yaml_data)
    if not valid:
        error_code = error_msg.split()[0] if error_msg else 'E102'
        field_match = error_msg.split('[')[-1].split(']')[0] if '[' in error_msg else None
        line_num = find_line_number_in_yaml(yaml_content, field_match) if field_match else None
        
        return {
            'valid': False,
            'error_code': error_code,
            'error_message': error_msg,
            'line_number': line_num
        }
    
    # 步骤 6: 无效组合验证 (E300)
    valid, error_msg = validate_invalid_combinations(yaml_data)
    if not valid:
        error_code = error_msg.split()[0] if error_msg else 'E300'
        # 对于组合错误，可能没有明确的行号
        
        return {
            'valid': False,
            'error_code': error_code,
            'error_message': error_msg,
            'line_number': None
        }
    
    # 所有验证通过
    return {
        'valid': True,
        'error_code': '0',
        'error_message': 'OK',
        'line_number': None
    }

