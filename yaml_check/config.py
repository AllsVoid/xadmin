"""
YAML 验证规则配置
对应前端 check_yaml.ts 中的配置常量
"""

# E001: 必需的根键
REQUIRED_ROOT_KEYS = [
    'hardware.cpu',
    'hardware.gpu',
]

# E002: 不能为空的键
MANDATORY_NON_EMPTY_KEYS = [
    'hardware.machines',
    'test_suites',
]

# E101: 值类型配置
VALUE_TYPE_CONFIG = {
    'hardware.cpu': 'string',
}

# E102: 值范围配置（白名单）
VALUE_RANGE_CONFIG = {
    'hardware.cpu': ['Ryzen Threadripper', 'Ryzen 7', 'Ryzen 9', 'EPYC'],
}