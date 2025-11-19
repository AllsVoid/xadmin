"""
TPGEN API 测试用例
测试 SUT Device、OS Config、Test Type、Test Case 等 API 端点
"""
import pytest
from django.test import Client
from tpgen.models import (
    SutDevice, OsConfig, OsSupportedKernel,
    TestType, TestComponent, TestCase
)
import time


@pytest.fixture
def api_client():
    """创建测试客户端（无需认证）"""
    return Client()


@pytest.fixture
def timestamp():
    """生成唯一时间戳标识符"""
    return str(int(time.time() * 1000000))[-8:]


@pytest.fixture
def sample_devices(db, timestamp):
    """创建示例设备数据"""
    devices = [
        SutDevice.objects.create(
            hostname=f'test-navi10-{timestamp}',
            asic_name='Navi10 GFX1010',
            product_name=f'navi10-{timestamp}',
            ip_address='10.67.65.101',
            gpu_model='RX 5700 XT'
        ),
        SutDevice.objects.create(
            hostname=f'test-navi21-{timestamp}',
            asic_name='Navi21 GFX1030',
            product_name=f'navi21-{timestamp}',
            ip_address='10.67.65.102',
            gpu_model='RX 6800 XT'
        ),
        SutDevice.objects.create(
            hostname=f'test-navi31-{timestamp}',
            asic_name='Navi31 GFX1100',
            product_name=f'navi31-{timestamp}',
            ip_address='10.67.65.103',
            gpu_model='RX 7900 XTX'
        ),
    ]
    yield devices
    # 清理数据
    SutDevice.objects.filter(hostname__startswith=f'test-navi').delete()


@pytest.fixture
def sample_os_configs(db, timestamp):
    """创建示例 OS 配置数据"""
    os_configs = []
    
    ubuntu = OsConfig.objects.create(
        os_family=f'TestUbuntu-{timestamp}',
        version='22.04.test'
    )
    OsSupportedKernel.objects.create(os_config=ubuntu, kernel_version=f'5.15.0-test-{timestamp[:4]}')
    OsSupportedKernel.objects.create(os_config=ubuntu, kernel_version=f'5.15.1-test-{timestamp[:4]}')
    os_configs.append(ubuntu)
    
    fedora = OsConfig.objects.create(
        os_family=f'TestFedora-{timestamp}',
        version='39.test'
    )
    OsSupportedKernel.objects.create(os_config=fedora, kernel_version=f'6.5.6-test-{timestamp[:4]}')
    os_configs.append(fedora)
    
    yield os_configs
    # 清理数据
    OsConfig.objects.filter(os_family__startswith='Test').delete()


@pytest.fixture
def sample_test_data(db, timestamp):
    """创建示例测试类型、组件和用例数据"""
    # 创建测试类型
    benchmark = TestType.objects.create(type_name=f'TestBenchmark-{timestamp}')
    functional = TestType.objects.create(type_name=f'TestFunctional-{timestamp}')
    
    # 创建测试组件
    clpeak = TestComponent.objects.create(
        test_type=benchmark,
        component_category='Compute',
        component_name=f'test-clpeak-{timestamp}'
    )
    ffmpeg = TestComponent.objects.create(
        test_type=benchmark,
        component_category='Media',
        component_name=f'test-ffmpeg-{timestamp}'
    )
    
    # 创建测试用例
    case1 = TestCase.objects.create(
        test_component=clpeak,
        case_name=f'Test OpenCL SP-{timestamp}',
        case_config={'precision': 'single'}
    )
    case2 = TestCase.objects.create(
        test_component=clpeak,
        case_name=f'Test OpenCL DP-{timestamp}',
        case_config={'precision': 'double'}
    )
    case3 = TestCase.objects.create(
        test_component=ffmpeg,
        case_name=f'Test H.264 Encoding-{timestamp}',
        case_config={'resolution': '3840x2160', 'codec': 'h264'}
    )
    
    data = {
        'test_types': [benchmark, functional],
        'components': [clpeak, ffmpeg],
        'cases': [case1, case2, case3]
    }
    
    yield data
    # 清理数据
    TestType.objects.filter(type_name__startswith='Test').delete()


@pytest.mark.django_db
class TestSutDeviceAPI:
    """测试 SUT Device API"""
    
    def test_get_product_names(self, api_client, sample_devices):
        """测试获取产品名称列表"""
        response = api_client.get('/tp/api/sut-device/product-names')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 3  # 至少有我们创建的3个产品
        
        # 验证我们创建的产品在列表中
        product_names = [item['value'] for item in data['data']]
        for device in sample_devices:
            assert device.product_name in product_names
        
        print(f"\n✅ 获取产品名称列表成功: {len(data['data'])} 个产品")
    
    def test_get_asic_names(self, api_client, sample_devices):
        """测试获取 ASIC 名称列表"""
        response = api_client.get('/tp/api/sut-device/asic-names')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 3
        
        # 验证我们创建的 ASIC 在列表中
        asic_names = [item['value'] for item in data['data']]
        for device in sample_devices:
            assert device.asic_name in asic_names
        
        print(f"\n✅ 获取 ASIC 名称列表成功: {len(data['data'])} 个 ASIC")
    
    def test_get_asic_names_filtered_by_product(self, api_client, sample_devices):
        """测试按产品名称过滤 ASIC 列表"""
        product_name = sample_devices[1].product_name
        response = api_client.get(f'/tp/api/sut-device/asic-names?productName={product_name}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 1
        assert data['data'][0]['value'] == sample_devices[1].asic_name
        
        print("\n✅ 按产品名称过滤 ASIC 列表成功")
    
    def test_get_machines_no_filter(self, api_client, sample_devices):
        """测试获取所有机器列表（无过滤）"""
        response = api_client.get('/tp/api/sut-device/machines')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 3
        
        print(f"\n✅ 获取所有机器列表成功: {len(data['data'])} 台机器")
    
    def test_get_machines_filtered_by_product(self, api_client, sample_devices):
        """测试按产品名称过滤机器列表"""
        product_name = sample_devices[2].product_name
        expected_hostname = sample_devices[2].hostname
        response = api_client.get(f'/tp/api/sut-device/machines?productName={product_name}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 1
        
        hostnames = [m['hostname'] for m in data['data']]
        assert expected_hostname in hostnames
        
        print("\n✅ 按产品名称过滤机器列表成功")
    
    def test_get_machines_filtered_by_asic(self, api_client, sample_devices):
        """测试按 ASIC 名称过滤机器列表"""
        asic_name = sample_devices[0].asic_name
        response = api_client.get(f'/tp/api/sut-device/machines?asicName={asic_name}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 1
        assert data['data'][0]['asicName'] == asic_name
        
        print("\n✅ 按 ASIC 名称过滤机器列表成功")
    
    def test_get_machines_combined_filters(self, api_client, sample_devices):
        """测试组合过滤条件"""
        product_name = sample_devices[1].product_name
        asic_name = sample_devices[1].asic_name
        response = api_client.get(
            f'/tp/api/sut-device/machines?productName={product_name}&asicName={asic_name}'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 1
        assert data['data'][0]['productName'] == product_name
        assert data['data'][0]['asicName'] == asic_name
        
        print("\n✅ 组合过滤条件测试成功")


@pytest.mark.django_db
class TestOsConfigAPI:
    """测试 OS Config API"""
    
    def test_get_os_options(self, api_client, sample_os_configs):
        """测试获取 OS 选项列表"""
        response = api_client.get('/tp/api/os-config/options')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 2
        
        # 验证创建的 OS 在列表中
        os_families = [item['osFamily'] for item in data['data']]
        for os_config in sample_os_configs:
            assert os_config.os_family in os_families
        
        print(f"\n✅ 获取 OS 选项列表成功: {len(data['data'])} 个配置")
    
    def test_get_os_list(self, api_client, sample_os_configs):
        """测试获取 OS 配置列表"""
        response = api_client.get('/tp/api/os-config/list?page=1&size=20')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'total' in data['data']
        assert 'list' in data['data']
        assert data['data']['total'] >= 2
        
        print(f"\n✅ 获取 OS 配置列表成功: {data['data']['total']} 个配置")
    
    def test_get_kernel_versions(self, api_client, sample_os_configs):
        """测试获取指定 OS 的内核版本列表"""
        ubuntu = sample_os_configs[0]
        response = api_client.get(f'/tp/api/os-config/{ubuntu.id}/kernels')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 2  # Ubuntu 有两个内核版本
        
        # 验证内核版本
        kernel_versions = [item['value'] for item in data['data']]
        assert len(kernel_versions) >= 2
        
        print(f"\n✅ 获取内核版本列表成功: {len(data['data'])} 个版本")


@pytest.mark.django_db
class TestTestTypeAPI:
    """测试 Test Type API"""
    
    def test_get_test_type_list(self, api_client, sample_test_data):
        """测试获取测试类型列表"""
        response = api_client.get('/tp/api/test-type/list')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 2
        
        # 验证创建的测试类型在列表中
        type_names = [item['typeName'] for item in data['data']]
        for test_type in sample_test_data['test_types']:
            assert test_type.type_name in type_names
        
        print(f"\n✅ 获取测试类型列表成功: {len(data['data'])} 个类型")
    
    def test_get_test_type_options(self, api_client, sample_test_data):
        """测试获取测试类型选项（用于下拉框）"""
        response = api_client.get('/tp/api/test-type/options')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 2
        
        labels = [item['label'] for item in data['data']]
        for test_type in sample_test_data['test_types']:
            assert test_type.type_name in labels
        
        print(f"\n✅ 获取测试类型选项成功: {len(data['data'])} 个类型")
    
    def test_get_test_components(self, api_client, sample_test_data):
        """测试获取测试组件列表"""
        benchmark = sample_test_data['test_types'][0]
        response = api_client.get(f'/tp/api/test-component/list?test_type_id={benchmark.id}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 2  # clpeak 和 ffmpeg
        
        # 验证组件在列表中
        component_names = [item['componentName'] for item in data['data']]
        for component in sample_test_data['components']:
            assert component.component_name in component_names
        
        print(f"\n✅ 获取测试组件列表成功: {len(data['data'])} 个组件")
    
    def test_get_test_cases(self, api_client, sample_test_data):
        """测试获取测试用例列表"""
        clpeak = sample_test_data['components'][0]
        response = api_client.get(f'/tp/api/test-case/list?test_component_id={clpeak.id}&page=1&size=20')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'total' in data['data']
        assert 'list' in data['data']
        assert data['data']['total'] >= 2  # SP 和 DP 两个用例
        
        # 验证用例在列表中
        case_names = [item['caseName'] for item in data['data']['list']]
        assert len(case_names) >= 2
        
        print(f"\n✅ 获取测试用例列表成功: {data['data']['total']} 个用例")
    
    def test_search_test_cases(self, api_client, sample_test_data):
        """测试搜索测试用例"""
        # 搜索包含 "Test" 的用例
        response = api_client.get('/tp/api/test-case/search?keyword=Test')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) >= 3  # 至少有我们创建的3个用例
        
        print(f"\n✅ 搜索测试用例成功: {len(data['data'])} 个结果")


@pytest.mark.django_db
class TestAPIErrorHandling:
    """测试 API 错误处理"""
    
    def test_invalid_product_name(self, api_client):
        """测试无效的产品名称"""
        response = api_client.get('/tp/api/sut-device/machines?productName=NonExistProduct999999')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) == 0  # 应该返回空列表
        
        print("\n✅ 无效产品名称处理正确")
    
    def test_invalid_os_config_id(self, api_client):
        """测试无效的 OS 配置 ID"""
        response = api_client.get('/tp/api/os-config/999999/kernels')
        
        # 应该返回错误或空列表
        assert response.status_code in [200, 404]
        data = response.json()
        if response.status_code == 200:
            assert data['code'] in [200, 400, 404]
        
        print("\n✅ 无效 OS 配置 ID 处理正确")
    
    def test_invalid_test_type_id(self, api_client):
        """测试无效的测试类型 ID"""
        response = api_client.get('/tp/api/test-component/list?test_type_id=999999')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) == 0  # 应该返回空列表
        
        print("\n✅ 无效测试类型 ID 处理正确")


@pytest.mark.django_db
class TestAPIIntegration:
    """测试 API 集成场景"""
    
    def test_full_workflow(self, api_client, sample_devices, sample_os_configs, sample_test_data):
        """测试完整的 API 调用流程"""
        # 1. 获取产品名称列表
        response = api_client.get('/tp/api/sut-device/product-names')
        assert response.status_code == 200
        products = response.json()['data']
        assert len(products) >= 3
        print(f"\n✓ Step 1: 获取产品列表 - {len(products)} 个产品")
        
        # 2. 获取 ASIC 列表
        response = api_client.get('/tp/api/sut-device/asic-names')
        assert response.status_code == 200
        asics = response.json()['data']
        assert len(asics) >= 3
        print(f"✓ Step 2: 获取 ASIC 列表 - {len(asics)} 个 ASIC")
        
        # 3. 获取机器列表
        product_name = sample_devices[0].product_name
        response = api_client.get(f'/tp/api/sut-device/machines?productName={product_name}')
        assert response.status_code == 200
        machines = response.json()['data']
        assert len(machines) >= 1
        print(f"✓ Step 3: 获取机器列表 - {len(machines)} 台机器")
        
        # 4. 获取 OS 配置列表
        response = api_client.get('/tp/api/os-config/options')
        assert response.status_code == 200
        os_configs = response.json()['data']
        assert len(os_configs) >= 2
        print(f"✓ Step 4: 获取 OS 配置 - {len(os_configs)} 个配置")
        
        # 5. 获取测试类型列表
        response = api_client.get('/tp/api/test-type/list')
        assert response.status_code == 200
        test_types = response.json()['data']
        assert len(test_types) >= 2
        print(f"✓ Step 5: 获取测试类型 - {len(test_types)} 个类型")
        
        # 6. 获取测试组件
        first_type_id = sample_test_data['test_types'][0].id
        response = api_client.get(f'/tp/api/test-component/list?test_type_id={first_type_id}')
        assert response.status_code == 200
        components = response.json()['data']
        assert len(components) >= 2
        print(f"✓ Step 6: 获取测试组件 - {len(components)} 个组件")
        
        # 7. 搜索测试用例
        response = api_client.get('/tp/api/test-case/search?keyword=Test')
        assert response.status_code == 200
        cases = response.json()['data']
        assert len(cases) >= 3
        print(f"✓ Step 7: 搜索测试用例 - {len(cases)} 个用例")
        
        print("\n✅ 完整 API 工作流程测试成功")
    
    def test_filtered_workflow(self, api_client, sample_devices, sample_test_data):
        """测试带过滤条件的工作流程"""
        # 使用特定产品过滤
        product_name = sample_devices[1].product_name
        
        # 获取该产品的 ASIC
        response = api_client.get(f'/tp/api/sut-device/asic-names?productName={product_name}')
        assert response.status_code == 200
        asics = response.json()['data']
        assert len(asics) >= 1
        
        # 获取该产品的机器
        asic_name = sample_devices[1].asic_name
        response = api_client.get(
            f'/tp/api/sut-device/machines?productName={product_name}&asicName={asic_name}'
        )
        assert response.status_code == 200
        machines = response.json()['data']
        assert len(machines) >= 1
        assert machines[0]['productName'] == product_name
        
        print("\n✅ 带过滤条件的工作流程测试成功")
