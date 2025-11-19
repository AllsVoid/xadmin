"""
TPGEN 模型测试用例
测试 SutDevice、OsConfig、TestType、TestCase 等模型
"""
import pytest
from django.db import IntegrityError
from django.utils import timezone
from tpgen.models import (
    SutDevice, OsConfig, OsSupportedKernel, 
    TestType, TestComponent, TestCase, 
    TestPlan, TestPlanCase
)


@pytest.mark.django_db
class TestSutDeviceModel:
    """测试 SutDevice 模型"""
    
    def test_create_sut_device(self):
        """测试创建测试设备"""
        device = SutDevice.objects.create(
            hostname='test-machine-01',
            asic_name='Navi10 GFX1010',
            product_name='navi10',
            ip_address='192.168.1.100',
            device_id='0x1234',
            rev_id='0x01',
            gpu_series='Radeon RX 5000',
            gpu_model='RX 5700 XT'
        )
        
        assert device.id is not None
        assert device.hostname == 'test-machine-01'
        assert device.product_name == 'navi10'
        assert device.created_at is not None
        assert device.updated_at is not None
        print(f"\n✅ 创建测试设备成功: {device}")
    
    def test_sut_device_unique_hostname(self):
        """测试主机名唯一性约束"""
        SutDevice.objects.create(
            hostname='unique-host-001',
            product_name='navi10'
        )
        
        # 尝试创建相同主机名的设备，应该抛出异常
        with pytest.raises(IntegrityError):
            SutDevice.objects.create(
                hostname='unique-host-001',
                product_name='navi21'
            )
        print("\n✅ 主机名唯一性约束测试通过")
    
    def test_sut_device_str_representation(self):
        """测试字符串表示"""
        device = SutDevice.objects.create(
            hostname='test-host-repr',
            product_name='navi10'
        )
        
        str_repr = str(device)
        assert 'test-host-repr' in str_repr
        print(f"\n✅ 设备字符串表示: {str_repr}")
    
    def test_query_by_product_name(self):
        """测试按产品名称查询"""
        # 确保从空数据库开始
        SutDevice.objects.all().delete()
        
        SutDevice.objects.create(hostname='query-host-1', product_name='navi10-query')
        SutDevice.objects.create(hostname='query-host-2', product_name='navi10-query')
        SutDevice.objects.create(hostname='query-host-3', product_name='navi21-query')
        
        navi10_devices = SutDevice.objects.filter(product_name='navi10-query')
        assert navi10_devices.count() == 2
        print(f"\n✅ 按产品名称查询成功: 找到 {navi10_devices.count()} 台设备")
    
    def test_query_by_asic_name(self):
        """测试按 ASIC 名称查询"""
        # 确保从空数据库开始
        SutDevice.objects.all().delete()
        
        SutDevice.objects.create(
            hostname='asic-query-host',
            asic_name='Navi10 GFX1010 Special',
            product_name='navi10'
        )
        
        devices = SutDevice.objects.filter(asic_name='Navi10 GFX1010 Special')
        assert devices.count() == 1
        print("\n✅ 按 ASIC 名称查询成功")


@pytest.mark.django_db
class TestOsConfigModel:
    """测试 OsConfig 模型"""
    
    def test_create_os_config(self):
        """测试创建操作系统配置"""
        os_config = OsConfig.objects.create(
            os_family='Ubuntu-Test',
            version='22.04.1',
            download_url='http://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso'
        )
        
        assert os_config.id is not None
        assert os_config.os_family == 'Ubuntu-Test'
        assert os_config.version == '22.04.1'
        print(f"\n✅ 创建OS配置成功: {os_config}")
    
    def test_os_config_unique_together(self):
        """测试 os_family 和 version 组合唯一性"""
        OsConfig.objects.create(
            os_family='Ubuntu-Unique',
            version='22.04.2'
        )
        
        # 尝试创建相同组合，应该抛出异常
        with pytest.raises(IntegrityError):
            OsConfig.objects.create(
                os_family='Ubuntu-Unique',
                version='22.04.2'
            )
        print("\n✅ OS配置唯一性约束测试通过")
    
    def test_os_config_str_representation(self):
        """测试字符串表示"""
        os_config = OsConfig.objects.create(
            os_family='RHEL-Test',
            version='9.0.1'
        )
        
        str_repr = str(os_config)
        assert 'RHEL-Test' in str_repr
        assert '9.0.1' in str_repr
        print(f"\n✅ OS配置字符串表示: {str_repr}")


@pytest.mark.django_db
class TestOsSupportedKernelModel:
    """测试 OsSupportedKernel 模型"""
    
    def test_create_supported_kernel(self):
        """测试创建支持的内核版本"""
        os_config = OsConfig.objects.create(
            os_family='Ubuntu-Kernel',
            version='22.04.3'
        )
        
        kernel = OsSupportedKernel.objects.create(
            os_config=os_config,
            kernel_version='5.15.0-56-generic'
        )
        
        assert kernel.id is not None
        assert kernel.os_config == os_config
        assert kernel.kernel_version == '5.15.0-56-generic'
        print(f"\n✅ 创建支持的内核版本成功: {kernel}")
    
    def test_kernel_cascade_delete(self):
        """测试级联删除"""
        os_config = OsConfig.objects.create(
            os_family='Ubuntu-Cascade',
            version='22.04.4'
        )
        
        OsSupportedKernel.objects.create(
            os_config=os_config,
            kernel_version='5.15.0-56'
        )
        OsSupportedKernel.objects.create(
            os_config=os_config,
            kernel_version='5.15.0-57'
        )
        
        kernel_count = OsSupportedKernel.objects.filter(os_config=os_config).count()
        assert kernel_count == 2
        
        # 删除 OS 配置，内核版本应该也被删除
        os_config_id = os_config.id
        os_config.delete()
        
        # 验证关联的内核已被删除
        kernel_count = OsSupportedKernel.objects.filter(os_config_id=os_config_id).count()
        assert kernel_count == 0
        print("\n✅ 级联删除测试通过")
    
    def test_os_config_related_kernels(self):
        """测试反向查询关联的内核版本"""
        os_config = OsConfig.objects.create(
            os_family='Fedora-Related',
            version='39.1'
        )
        
        OsSupportedKernel.objects.create(os_config=os_config, kernel_version='6.5.6')
        OsSupportedKernel.objects.create(os_config=os_config, kernel_version='6.5.7')
        OsSupportedKernel.objects.create(os_config=os_config, kernel_version='6.5.8')
        
        kernels = os_config.supported_kernels.all()
        assert kernels.count() == 3
        print(f"\n✅ 反向查询内核版本成功: {kernels.count()} 个版本")


@pytest.mark.django_db
class TestTestTypeModel:
    """测试 TestType 模型"""
    
    def test_create_test_type(self):
        """测试创建测试类型"""
        test_type = TestType.objects.create(type_name='Benchmark-Test-001')
        
        assert test_type.id is not None
        assert test_type.type_name == 'Benchmark-Test-001'
        print(f"\n✅ 创建测试类型成功: {test_type}")
    
    def test_test_type_unique_name(self):
        """测试类型名称唯一性"""
        TestType.objects.create(type_name='Functional-Unique-001')
        
        with pytest.raises(IntegrityError):
            TestType.objects.create(type_name='Functional-Unique-001')
        print("\n✅ 测试类型唯一性约束通过")


@pytest.mark.django_db
class TestTestComponentModel:
    """测试 TestComponent 模型"""
    
    def test_create_test_component(self):
        """测试创建测试组件"""
        test_type = TestType.objects.create(type_name='Benchmark-Comp-001')
        
        component = TestComponent.objects.create(
            test_type=test_type,
            component_category='Media',
            component_name='ffmpeg-001'
        )
        
        assert component.id is not None
        assert component.component_name == 'ffmpeg-001'
        assert component.test_type == test_type
        print(f"\n✅ 创建测试组件成功: {component}")
    
    def test_component_unique_together(self):
        """测试组件唯一性约束"""
        test_type = TestType.objects.create(type_name='Benchmark-Comp-002')
        
        TestComponent.objects.create(
            test_type=test_type,
            component_category='Media',
            component_name='ffmpeg-unique'
        )
        
        # 相同组合应该失败
        with pytest.raises(IntegrityError):
            TestComponent.objects.create(
                test_type=test_type,
                component_category='Media',
                component_name='ffmpeg-unique'
            )
        print("\n✅ 组件唯一性约束通过")


@pytest.mark.django_db
class TestTestCaseModel:
    """测试 TestCase 模型"""
    
    def test_create_test_case(self):
        """测试创建测试用例"""
        test_type = TestType.objects.create(type_name='Benchmark-Case-001')
        component = TestComponent.objects.create(
            test_type=test_type,
            component_category='Compute',
            component_name='clpeak-001'
        )
        
        test_case = TestCase.objects.create(
            test_component=component,
            case_name='OpenCL Compute SP',
            case_config={'timeout': 300, 'iterations': 10}
        )
        
        assert test_case.id is not None
        assert test_case.case_name == 'OpenCL Compute SP'
        assert test_case.case_config['timeout'] == 300
        print(f"\n✅ 创建测试用例成功: {test_case}")
    
    def test_case_json_field(self):
        """测试 JSON 字段存储"""
        test_type = TestType.objects.create(type_name='Performance-JSON-001')
        component = TestComponent.objects.create(
            test_type=test_type,
            component_name='benchmark-json'
        )
        
        config_data = {
            'resolution': '1920x1080',
            'quality': 'ultra',
            'fps_target': 60,
            'options': ['vsync', 'aa']
        }
        
        test_case = TestCase.objects.create(
            test_component=component,
            case_name='Graphics Test',
            case_config=config_data
        )
        
        # 重新查询验证 JSON 存储
        saved_case = TestCase.objects.get(id=test_case.id)
        assert saved_case.case_config['resolution'] == '1920x1080'
        assert 'vsync' in saved_case.case_config['options']
        print("\n✅ JSON 字段存储测试通过")


@pytest.mark.django_db
class TestTestPlanModel:
    """测试 TestPlan 模型"""
    
    def test_create_test_plan(self):
        """测试创建测试计划"""
        device = SutDevice.objects.create(
            hostname='test-machine-plan-001',
            product_name='navi10'
        )
        os_config = OsConfig.objects.create(
            os_family='Ubuntu-Plan',
            version='22.04.5'
        )
        
        test_plan = TestPlan.objects.create(
            plan_name='Benchmark Plan 2025',
            plan_description='综合性能测试计划',
            sut_device=device,
            os_config=os_config,
            created_by='admin'
        )
        
        assert test_plan.id is not None
        assert test_plan.plan_name == 'Benchmark Plan 2025'
        assert test_plan.sut_device == device
        assert test_plan.os_config == os_config
        print(f"\n✅ 创建测试计划成功: {test_plan}")
    
    def test_test_plan_relationships(self):
        """测试测试计划关联关系"""
        device = SutDevice.objects.create(hostname='host-rel-001', product_name='navi10')
        os_config = OsConfig.objects.create(os_family='RHEL-Rel', version='9.0.2')
        
        plan = TestPlan.objects.create(
            plan_name='Test Plan Relationships',
            sut_device=device,
            os_config=os_config
        )
        
        # 通过设备反向查询计划
        plans_for_device = device.test_plans.all()
        assert plans_for_device.count() == 1
        assert plans_for_device.first() == plan
        
        # 通过 OS 配置反向查询计划
        plans_for_os = os_config.test_plans.all()
        assert plans_for_os.count() == 1
        print("\n✅ 测试计划关联关系测试通过")


@pytest.mark.django_db
class TestTestPlanCaseModel:
    """测试 TestPlanCase 关联模型"""
    
    def test_create_plan_case_association(self):
        """测试创建测试计划和用例的关联"""
        # 创建必要的对象
        device = SutDevice.objects.create(hostname='host-pc-001', product_name='navi10')
        os_config = OsConfig.objects.create(os_family='Ubuntu-PC', version='22.04.6')
        test_plan = TestPlan.objects.create(
            plan_name='Plan-Assoc-001',
            sut_device=device,
            os_config=os_config
        )
        
        test_type = TestType.objects.create(type_name='Benchmark-PC-001')
        component = TestComponent.objects.create(test_type=test_type, component_name='test-pc-001')
        test_case = TestCase.objects.create(test_component=component, case_name='Case 1')
        
        # 创建关联
        plan_case = TestPlanCase.objects.create(
            test_plan=test_plan,
            test_case=test_case,
            timeout=600
        )
        
        assert plan_case.id is not None
        assert plan_case.timeout == 600
        print(f"\n✅ 创建计划-用例关联成功: {plan_case}")
    
    def test_plan_case_unique_together(self):
        """测试计划-用例组合唯一性"""
        device = SutDevice.objects.create(hostname='h-unique-pc', product_name='navi10')
        os_config = OsConfig.objects.create(os_family='U-PC', version='22.7')
        test_plan = TestPlan.objects.create(
            plan_name='P-Unique-PC',
            sut_device=device,
            os_config=os_config
        )
        
        test_type = TestType.objects.create(type_name='B-PC-Unique')
        component = TestComponent.objects.create(test_type=test_type, component_name='c-pc-unique')
        test_case = TestCase.objects.create(test_component=component, case_name='tc-unique')
        
        TestPlanCase.objects.create(test_plan=test_plan, test_case=test_case)
        
        # 重复关联应该失败
        with pytest.raises(IntegrityError):
            TestPlanCase.objects.create(test_plan=test_plan, test_case=test_case)
        print("\n✅ 计划-用例唯一性约束通过")


@pytest.mark.django_db
class TestModelIntegration:
    """测试模型集成场景"""
    
    def test_complete_workflow(self):
        """测试完整的工作流程"""
        # 1. 创建设备
        device = SutDevice.objects.create(
            hostname='benchmark-server-integration-01',
            asic_name='Navi21 GFX1030',
            product_name='navi21-integration',
            ip_address='10.0.0.100',
            gpu_model='RX 6800 XT'
        )
        
        # 2. 创建 OS 配置和内核
        os_config = OsConfig.objects.create(
            os_family='Ubuntu-Integration',
            version='22.04.8'
        )
        OsSupportedKernel.objects.create(os_config=os_config, kernel_version='5.15.0-56')
        
        # 3. 创建测试类型和组件
        test_type = TestType.objects.create(type_name='Benchmark-Integration-001')
        component = TestComponent.objects.create(
            test_type=test_type,
            component_category='Compute',
            component_name='clpeak-integration'
        )
        
        # 4. 创建测试用例
        test_case1 = TestCase.objects.create(
            test_component=component,
            case_name='OpenCL Compute SP',
            case_config={'precision': 'single'}
        )
        test_case2 = TestCase.objects.create(
            test_component=component,
            case_name='OpenCL Compute DP',
            case_config={'precision': 'double'}
        )
        
        # 5. 创建测试计划
        test_plan = TestPlan.objects.create(
            plan_name='RX 6800 XT Benchmark Integration',
            plan_description='RX 6800 XT 显卡性能测试',
            sut_device=device,
            os_config=os_config,
            created_by='test_user'
        )
        
        # 6. 关联测试用例到计划
        TestPlanCase.objects.create(test_plan=test_plan, test_case=test_case1, timeout=300)
        TestPlanCase.objects.create(test_plan=test_plan, test_case=test_case2, timeout=600)
        
        # 验证
        assert test_plan.plan_cases.count() == 2
        assert test_plan.sut_device.hostname == 'benchmark-server-integration-01'
        assert test_plan.os_config.os_family == 'Ubuntu-Integration'
        
        print("\n✅ 完整工作流程测试通过")
        print(f"   设备: {device.hostname}")
        print(f"   OS: {os_config.os_family} {os_config.version}")
        print(f"   计划: {test_plan.plan_name}")
        print(f"   用例数: {test_plan.plan_cases.count()}")

