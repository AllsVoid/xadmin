"""
YAML 验证辅助函数
对应 check_yaml.ts 第 54-87 行
"""

class YamlHelper:
    @staticmethod
    def is_empty(value):
        """检查值是否为空"""
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == '':
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False
    
    @staticmethod
    def get_nested_value(obj, path):
        """使用点号路径获取嵌套值"""
        keys = path.split('.')
        current = obj
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    @staticmethod
    def has_key(obj, key):
        """检查对象中是否存在某个键（任意深度）"""
        if not isinstance(obj, dict):
            return False
        if key in obj:
            return True
        for k, v in obj.items():
            if isinstance(v, dict) and YamlHelper.has_key(v, key):
                return True
        return False
    
    @staticmethod
    def get_value_type(value):
        """获取值的类型"""
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return 'boolean'
        if isinstance(value, int):
            return 'int'
        if isinstance(value, float):
            return 'number'
        if isinstance(value, str):
            return 'string'
        if isinstance(value, list):
            return 'array'
        if isinstance(value, dict):
            return 'object'
        return 'unknown'



"""
YAML 验证器主类
对应 check_yaml.ts 第 94-267 行
"""

from .config import (
    REQUIRED_ROOT_KEYS,
    MANDATORY_NON_EMPTY_KEYS,
    VALUE_TYPE_CONFIG,
    VALUE_RANGE_CONFIG
)

class YamlValidator:
    
    def __init__(self):
        self.helper = YamlHelper()
    
    def validate_required_root_keys(self, yaml_data):
        """E001: 验证必需的根键"""
        for key in REQUIRED_ROOT_KEYS:
            exists = False
            if '.' in key:
                value = self.helper.get_nested_value(yaml_data, key)
                exists = value is not None
            else:
                exists = self.helper.has_key(yaml_data, key)
            
            if not exists:
                return {
                    'valid': False,
                    'error_code': 'E001',
                    'error_message': f'E001 Unsupported: missing mandatory key [{key}]'
                }
        return {'valid': True, 'error_code': '0', 'error_message': 'OK'}
    
    def validate_mandatory_non_empty_keys(self, yaml_data):
        """E002: 验证不能为空的键"""
        for key in MANDATORY_NON_EMPTY_KEYS:
            if '.' in key:
                value = self.helper.get_nested_value(yaml_data, key)
            else:
                value = self.helper.get_nested_value(yaml_data, key)
                if value is None and 'hardware' in yaml_data:
                    value = yaml_data['hardware'].get(key)
                if value is None:
                    value = yaml_data.get(key)
            
            if value is None:
                return {
                    'valid': False,
                    'error_code': 'E002',
                    'error_message': f'E002 Unsupported: empty value for [{key}]'
                }
            
            if self.helper.is_empty(value):
                return {
                    'valid': False,
                    'error_code': 'E002',
                    'error_message': f'E002 Unsupported: empty value for [{key}]'
                }
        
        return {'valid': True, 'error_code': '0', 'error_message': 'OK'}
    
    def validate_value_types(self, yaml_data):
        """E101: 验证值类型"""
        for key, expected_type in VALUE_TYPE_CONFIG.items():
            if '.' in key:
                value = self.helper.get_nested_value(yaml_data, key)
            else:
                value = yaml_data.get(key)
            
            if value is None:
                continue
            
            actual_type = self.helper.get_value_type(value)
            
            # 类型映射
            type_map = {
                'string': ['string'],
                'int': ['int', 'number'],
                'number': ['int', 'number'],
                'boolean': ['boolean'],
                'array': ['array'],
                'object': ['object']
            }
            
            valid_types = type_map.get(expected_type, [expected_type])
            
            if actual_type not in valid_types:
                return {
                    'valid': False,
                    'error_code': 'E101',
                    'error_message': f'E101 Unsupported: value type error for [{key}]. Expected {expected_type}, got {actual_type}'
                }
        
        return {'valid': True, 'error_code': '0', 'error_message': 'OK'}
    
    def validate_value_ranges(self, yaml_data):
        """E102: 验证值范围（白名单）"""
        for key, allowed_values in VALUE_RANGE_CONFIG.items():
            if '.' in key:
                value = self.helper.get_nested_value(yaml_data, key)
            else:
                value = yaml_data.get(key)
            
            if value is None:
                continue
            
            if value not in allowed_values:
                return {
                    'valid': False,
                    'error_code': 'E102',
                    'error_message': f'E102 Unsupported: invalid value range for [{key}]. Value "{value}" is not in whitelist [{", ".join(allowed_values)}]'
                }
        
        return {'valid': True, 'error_code': '0', 'error_message': 'OK'}
    
    def validate(self, yaml_data):
        """
        主验证函数
        对应 check_yaml.ts 的 compatibility_analysis
        """
        try:
            # 输入验证
            if not yaml_data or not isinstance(yaml_data, dict):
                return {
                    'success': False,
                    'error': {
                        'code': 'E000',
                        'message': 'Invalid YAML data object'
                    }
                }
            
            # E001: 验证必需的根键
            result = self.validate_required_root_keys(yaml_data)
            if not result['valid']:
                return {
                    'success': False,
                    'error': {
                        'code': result['error_code'],
                        'message': result['error_message']
                    }
                }
            
            # E002: 验证不能为空的键
            result = self.validate_mandatory_non_empty_keys(yaml_data)
            if not result['valid']:
                return {
                    'success': False,
                    'error': {
                        'code': result['error_code'],
                        'message': result['error_message']
                    }
                }
            
            # E101: 验证值类型
            result = self.validate_value_types(yaml_data)
            if not result['valid']:
                return {
                    'success': False,
                    'error': {
                        'code': result['error_code'],
                        'message': result['error_message']
                    }
                }
            
            # E102: 验证值范围
            result = self.validate_value_ranges(yaml_data)
            if not result['valid']:
                return {
                    'success': False,
                    'error': {
                        'code': result['error_code'],
                        'message': result['error_message']
                    }
                }
            
            # 所有验证通过
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'code': 'E999',
                    'message': f'Validation exception: {str(e)}'
                }
            }