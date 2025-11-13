"""
Pytest 配置文件

提供测试夹具和配置：
- Django 配置
- 测试客户端
- 测试数据库
- 测试用户和认证
"""
import os
import sys
import pytest
import django
from pathlib import Path
from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model

# 设置 Django 环境
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadmin.settings')
django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """设置测试数据库"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': False,
        'AUTOCOMMIT': True,
        'CONN_MAX_AGE': 0,
        'OPTIONS': {},
        'TIME_ZONE': None,
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }


@pytest.fixture(scope='function')
def client():
    """提供 Django 测试客户端"""
    return Client()


@pytest.fixture(scope='function')
def api_client(client, test_user):
    """提供带认证的 API 客户端
    
    使用 Django Test Client 而不是 Ninja Test Client 以避免多实例问题
    """
    # 为客户端添加认证
    from ninja_jwt.tokens import AccessToken
    
    token = AccessToken.for_user(test_user)
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {str(token)}'
    client.defaults['CONTENT_TYPE'] = 'application/json'
    
    # 添加辅助方法以匹配 Ninja TestClient 的接口
    class APIClientWrapper:
        def __init__(self, django_client):
            self._client = django_client
            
        def get(self, path, params=None, **kwargs):
            if params:
                from urllib.parse import urlencode
                path = f"{path}?{urlencode(params)}"
            return self._client.get(f'/case{path}', **kwargs)
        
        def post(self, path, json=None, **kwargs):
            import json as json_lib
            return self._client.post(
                f'/case{path}',
                data=json_lib.dumps(json) if json else None,
                content_type='application/json',
                **kwargs
            )
        
        def put(self, path, json=None, **kwargs):
            import json as json_lib
            return self._client.put(
                f'/case{path}',
                data=json_lib.dumps(json) if json else None,
                content_type='application/json',
                **kwargs
            )
        
        def delete(self, path, params=None, **kwargs):
            if params:
                from urllib.parse import urlencode
                path = f"{path}?{urlencode(params)}"
            return self._client.delete(f'/case{path}', **kwargs)
    
    return APIClientWrapper(client)


@pytest.fixture(scope='function')
def test_user(db):
    """创建测试用户"""
    from django.db.models import signals
    from django.utils import timezone
    from xauth import models, signals as xauth_signals
    
    User = get_user_model()
    
    # 临时禁用信号
    signals.pre_save.disconnect(xauth_signals.update_cu_user, sender=models.SysUser)
    
    try:
        now = timezone.now()
        user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            gender=0,
            dept_id=1,
            status=1,
            is_system=0,
            create_user=1,
            update_user=1,
            create_time=now,
            update_time=now
        )
        user.set_password('testpass123')
        user.save()
        return user
    finally:
        # 重新连接信号
        signals.pre_save.connect(xauth_signals.update_cu_user, sender=models.SysUser)


@pytest.fixture(scope='function')
def auth_headers(test_user):
    """提供认证头部"""
    from ninja_jwt.tokens import AccessToken
    
    token = AccessToken.for_user(test_user)
    return {
        'Authorization': f'Bearer {str(token)}',
        'Content-Type': 'application/json'
    }


@pytest.fixture(scope='function')
def temp_casespace(db, tmp_path):
    """创建临时 casespace 用于测试"""
    from xcase.file_manager import file_manager
    
    # 临时设置 storage_root 为 tmp_path
    original_storage_root = file_manager.storage_root
    file_manager.storage_root = tmp_path / 'caseeditor'
    file_manager._ensure_storage_exists()
    
    # 创建测试 casespace
    casespace_path = file_manager.storage_root / 'test_casespace'
    casespace_path.mkdir(parents=True, exist_ok=True)
    
    # 创建测试 case
    case_path = casespace_path / 'test_case'
    case_path.mkdir(parents=True, exist_ok=True)
    
    # 创建测试文件
    test_file = case_path / 'test.py'
    test_file.write_text('print("Hello, World!")', encoding='utf-8')
    
    yield {
        'casespace': 'test_casespace',
        'case': 'test_case',
        'storage_root': file_manager.storage_root
    }
    
    # 恢复原始 storage_root
    file_manager.storage_root = original_storage_root


@pytest.fixture(scope='function')
def sample_case_metadata(db, temp_casespace):
    """创建示例 case 元数据"""
    from xcase.models import CaseMetadata
    
    metadata = CaseMetadata.objects.create(
        casespace=temp_casespace['casespace'],
        case_name=temp_casespace['case']
    )
    return metadata


@pytest.fixture(scope='function')
def sample_case_with_tags(sample_case_metadata):
    """创建带标签的 case"""
    from xcase.models import CaseTag
    
    tags = ['smoke', 'regression', 'api']
    for tag in tags:
        CaseTag.objects.create(
            metadata=sample_case_metadata,
            tag=tag
        )
    
    return {
        'metadata': sample_case_metadata,
        'tags': tags
    }


@pytest.fixture(scope='function')
def sample_case_with_options(sample_case_metadata):
    """创建带选项的 case"""
    from xcase.models import CaseOption
    
    options = {
        'priority': 'high',
        'author': 'test_user',
        'timeout': '300'
    }
    
    for key, value in options.items():
        CaseOption.objects.create(
            metadata=sample_case_metadata,
            key=key,
            value=value
        )
    
    return {
        'metadata': sample_case_metadata,
        'options': options
    }



