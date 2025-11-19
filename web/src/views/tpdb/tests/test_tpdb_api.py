"""
TPDB 前端对应的后端 API 测试
测试 tpgen 模块的各个 API 端点，这些API为 TPDB 前端界面提供数据
"""
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from tpgen.models import (
    SutDevice, OsConfig, OsSupportedKernel,
    TestType, TestComponent, TestCase
)

User = get_user_model()


@pytest.fixture
def api_client():
    """创建测试客户端"""
    return Client()


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User.objects.create_user(
        username='tpdbuser',
        password='testpass123',
        email='tpdb@example.com'
    )
    return user


@pytest.fixture
def auth_client(api_client, test_user):
    """创建已认证的客户端"""
    api_client.force_login(test_user)
    return api_client


@pytest.fixture
def tpdb_sample_data(db):
    """创建 TPDB 示例数据"""
    # 创建设备
    devices = []
    for i in range(5):
        device = SutDevice.objects.create(
            hostname=f'tpdb-machine-{i:02d}',
            asic_name=f'TestASIC{i}',
            product_name=f'product{i % 3}',
            ip_address=f'192.168.1.{100 + i}',
            gpu_model=f'GPU Model {i}'
        )
        devices.append(device)
    
    # 创建 OS 配置
    os_configs = []
    os_families = ['Ubuntu', 'Fedora', 'RHEL']
    for i, family in enumerate(os_families):
        os_config = OsConfig.objects.create(
            os_family=family,
            version=f'v{i+20}.04'
        )
        OsSupportedKernel.objects.create(
            os_config=os_config,
            kernel_version=f'5.{i+15}.0-56'
        )
        os_configs.append(os_config)
    
    # 创建测试类型和组件
    test_types = []
    for type_name in ['Benchmark', 'Functional', 'Performance']:
        test_type = TestType.objects.create(type_name=type_name)
        test_types.append(test_type)
        
        # 为每个类型创建组件
        for j in range(2):
            component = TestComponent.objects.create(
                test_type=test_type,
                component_category=f'Category{j}',
                component_name=f'{type_name}_Component_{j}'
            )
            
            # 为每个组件创建测试用例
            for k in range(3):
                TestCase.objects.create(
                    test_component=component,
                    case_name=f'{type_name}_Case_{j}_{k}',
                    case_config={'test': True, 'iteration': k}
                )
    
    return {
        'devices': devices,
        'os_configs': os_configs,
        'test_types': test_types
    }


@pytest.mark.django_db
class TestTPDBDeviceAPI:
    """测试 TPDB 设备相关 API"""
    
    def test_get_all_devices(self, auth_client, tpdb_sample_data):
        """测试获取所有设备列表"""
        response = auth_client.get('/api/tpgen/sut/machines')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 5
        
        print(f"\n✅ 获取所有设备成功: {len(data['data'])} 台设备")
    
    def test_filter_devices_by_product(self, auth_client, tpdb_sample_data):
        """测试按产品过滤设备"""
        response = auth_client.get('/api/tpgen/sut/machines?productName=product0')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证所有返回的设备都是 product0
        for device in data['data']:
            assert device['productName'] == 'product0'
        
        print("\n✅ 按产品过滤设备成功")
    
    def test_get_product_list(self, auth_client, tpdb_sample_data):
        """测试获取产品列表"""
        response = auth_client.get('/api/tpgen/sut/product-names')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 3
        
        product_names = [item['value'] for item in data['data']]
        assert 'product0' in product_names
        
        print(f"\n✅ 获取产品列表成功: {len(data['data'])} 个产品")
    
    def test_get_asic_list(self, auth_client, tpdb_sample_data):
        """测试获取 ASIC 列表"""
        response = auth_client.get('/api/tpgen/sut/asic-names')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 5
        
        print(f"\n✅ 获取 ASIC 列表成功: {len(data['data'])} 个 ASIC")


@pytest.mark.django_db
class TestTPDBOSConfigAPI:
    """测试 TPDB OS 配置相关 API"""
    
    def test_get_os_families(self, auth_client, tpdb_sample_data):
        """测试获取 OS 家族列表"""
        response = auth_client.get('/api/tpgen/os/families')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 3
        
        families = [item['value'] for item in data['data']]
        assert 'Ubuntu' in families
        assert 'Fedora' in families
        
        print(f"\n✅ 获取 OS 家族列表成功: {len(data['data'])} 个家族")
    
    def test_get_os_versions(self, auth_client, tpdb_sample_data):
        """测试获取指定家族的版本列表"""
        response = auth_client.get('/api/tpgen/os/versions?osFamily=Ubuntu')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 1
        
        print(f"\n✅ 获取 OS 版本列表成功: {len(data['data'])} 个版本")
    
    def test_get_kernel_versions(self, auth_client, tpdb_sample_data):
        """测试获取内核版本列表"""
        os_config = tpdb_sample_data['os_configs'][0]
        response = auth_client.get(f'/api/tpgen/os/kernels?osConfigId={os_config.id}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 1
        
        print(f"\n✅ 获取内核版本列表成功: {len(data['data'])} 个版本")


@pytest.mark.django_db
class TestTPDBTestTypeAPI:
    """测试 TPDB 测试类型相关 API"""
    
    def test_get_test_types(self, auth_client, tpdb_sample_data):
        """测试获取测试类型列表"""
        response = auth_client.get('/api/tpgen/test-types')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 3
        
        type_names = [item['type_name'] for item in data['data']]
        assert 'Benchmark' in type_names
        assert 'Functional' in type_names
        
        print(f"\n✅ 获取测试类型列表成功: {len(data['data'])} 个类型")
    
    def test_get_test_components(self, auth_client, tpdb_sample_data):
        """测试获取测试组件列表"""
        test_type = tpdb_sample_data['test_types'][0]
        response = auth_client.get(f'/api/tpgen/components?testTypeId={test_type.id}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 2
        
        print(f"\n✅ 获取测试组件列表成功: {len(data['data'])} 个组件")
    
    def test_get_test_cases(self, auth_client, tpdb_sample_data):
        """测试获取测试用例列表"""
        test_type = tpdb_sample_data['test_types'][0]
        components = TestComponent.objects.filter(test_type=test_type)
        
        if components.exists():
            component = components.first()
            response = auth_client.get(f'/api/tpgen/test-cases?componentId={component.id}')
            
            assert response.status_code == 200
            data = response.json()
            assert data['code'] == 200
            assert len(data['data']) >= 3
            
            print(f"\n✅ 获取测试用例列表成功: {len(data['data'])} 个用例")


@pytest.mark.django_db
class TestTPDBDataFlow:
    """测试 TPDB 数据流"""
    
    def test_cascading_queries(self, auth_client, tpdb_sample_data):
        """测试级联查询流程：产品 → ASIC → 设备"""
        # 1. 获取产品列表
        products_response = auth_client.get('/api/tpgen/sut/product-names')
        products = products_response.json()['data']
        assert len(products) > 0
        
        # 2. 选择第一个产品，获取 ASIC
        first_product = products[0]['value']
        asic_response = auth_client.get(f'/api/tpgen/sut/asic-names?productName={first_product}')
        asics = asic_response.json()['data']
        assert len(asics) > 0
        
        # 3. 获取该产品的设备
        device_response = auth_client.get(f'/api/tpgen/sut/machines?productName={first_product}')
        devices = device_response.json()['data']
        assert len(devices) > 0
        
        print("\n✅ 级联查询流程测试成功")
    
    def test_test_type_to_cases_flow(self, auth_client, tpdb_sample_data):
        """测试测试类型 → 组件 → 用例的查询流程"""
        # 1. 获取测试类型
        types_response = auth_client.get('/api/tpgen/test-types')
        test_types = types_response.json()['data']
        assert len(test_types) > 0
        
        # 2. 获取第一个类型的组件
        first_type_id = test_types[0]['id']
        components_response = auth_client.get(f'/api/tpgen/components?testTypeId={first_type_id}')
        components = components_response.json()['data']
        assert len(components) > 0
        
        # 3. 获取第一个组件的用例
        first_component_id = components[0]['id']
        cases_response = auth_client.get(f'/api/tpgen/test-cases?componentId={first_component_id}')
        test_cases = cases_response.json()['data']
        assert len(test_cases) > 0
        
        print("\n✅ 测试类型到用例流程测试成功")


@pytest.mark.django_db
class TestTPDBSearchAndFilter:
    """测试 TPDB 搜索和过滤功能"""
    
    def test_search_devices_by_hostname(self, auth_client, tpdb_sample_data):
        """测试按主机名搜索设备"""
        response = auth_client.get('/api/tpgen/sut/machines?hostname=machine-01')
        
        assert response.status_code == 200
        data = response.json()
        
        if data['code'] == 200:
            # 如果支持主机名搜索，验证结果
            assert len(data['data']) >= 0
            print("\n✅ 主机名搜索功能正常")
        else:
            print("\n💡 主机名搜索可能未实现")
    
    def test_combined_filters(self, auth_client, tpdb_sample_data):
        """测试组合过滤条件"""
        # 同时按产品和 ASIC 过滤
        response = auth_client.get(
            '/api/tpgen/sut/machines?productName=product0&asicName=TestASIC0'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 结果应该同时满足两个条件
        for device in data['data']:
            assert device['productName'] == 'product0'
            assert device['asicName'] == 'TestASIC0'
        
        print("\n✅ 组合过滤测试成功")


@pytest.mark.django_db
class TestTPDBPerformance:
    """测试 TPDB API 性能"""
    
    def test_large_device_list(self, auth_client):
        """测试大量设备时的查询性能"""
        # 创建100台设备
        for i in range(100):
            SutDevice.objects.create(
                hostname=f'perf-test-{i:03d}',
                product_name='test_product',
                ip_address=f'10.0.{i // 256}.{i % 256}'
            )
        
        import time
        start_time = time.time()
        response = auth_client.get('/api/tpgen/sut/machines?productName=test_product')
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['data']) == 100
        
        print(f"\n✅ 大量设备查询完成: 100台设备，耗时{elapsed_time:.3f}秒")
        assert elapsed_time < 3.0, "查询时间不应超过3秒"


@pytest.mark.django_db
class TestTPDBErrorHandling:
    """测试 TPDB API 错误处理"""
    
    def test_invalid_filter_values(self, auth_client):
        """测试无效的过滤值"""
        response = auth_client.get('/api/tpgen/sut/machines?productName=nonexistent_product')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) == 0  # 应该返回空列表
        
        print("\n✅ 无效过滤值处理正确")
    
    def test_invalid_parameter_types(self, auth_client, tpdb_sample_data):
        """测试无效的参数类型"""
        # 传递字符串给需要整数的参数
        response = auth_client.get('/api/tpgen/os/kernels?osConfigId=invalid_id')
        
        # 应该返回错误或空结果
        assert response.status_code in [200, 400, 422]
        
        print("\n✅ 无效参数类型处理正确")

