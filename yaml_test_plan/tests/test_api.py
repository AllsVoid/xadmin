"""
YAML Test Plan 模型和业务逻辑测试
测试 YAML 数据模型、验证逻辑的集成
不依赖用户认证
"""
import pytest
from yaml_test_plan.models import TestPlanYaml
from yaml_test_plan.validator import validate_yaml_full


@pytest.fixture
def valid_yaml_content():
    """返回有效的 YAML 内容"""
    return """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
  description: "Test Plan for Model Testing"

hardware:
  machines:
    - id: 1
      hostname: "test-machine-01"
      ipAddress: "192.168.1.100"
      asicName: "Navi10 GFX1010"
      gpuModel: "RX 5700 XT"
      productName: "navi10"

environment:
  machines:
    test-machine-01:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          kernel:
            kernel_version: "5.15.0-56"
          test_type: "Benchmark"
          deployment_method: "bare_metal"
          execution_case_list:
            - "OpenCL Compute SP"
            - "OpenCL Compute DP"
"""


@pytest.fixture
def invalid_yaml_content():
    """返回无效的 YAML 内容"""
    return """
metadata:
  version: "2.0"
  # 缺少必需的字段
"""


@pytest.mark.django_db
class TestYAMLModel:
    """测试 YAML 数据模型"""
    
    def test_create_yaml_record(self, valid_yaml_content):
        """测试创建 YAML 记录"""
        record = TestPlanYaml.objects.create(
            file_name='test_plan.yaml',
            file_content=valid_yaml_content,
            file_size=len(valid_yaml_content),
            validation_status='valid',
            create_user=1
        )
        
        assert record.id is not None
        assert record.file_name == 'test_plan.yaml'
        assert record.validation_status == 'valid'
        assert record.create_time is not None
        
        print(f"\n✅ 创建 YAML 记录成功: ID={record.id}")
    
    def test_query_yaml_records(self, valid_yaml_content):
        """测试查询 YAML 记录"""
        # 创建多条记录
        for i in range(3):
            TestPlanYaml.objects.create(
                file_name=f'plan_{i}.yaml',
                file_content=valid_yaml_content,
                file_size=len(valid_yaml_content),
                validation_status='valid',
                create_user=1
            )
        
        # 查询所有记录
        records = TestPlanYaml.objects.all()
        assert records.count() >= 3
        
        # 查询特定记录
        record = TestPlanYaml.objects.filter(file_name='plan_0.yaml').first()
        assert record is not None
        assert record.file_name == 'plan_0.yaml'
        
        print(f"\n✅ 查询 YAML 记录成功: 共 {records.count()} 条记录")
    
    def test_update_yaml_record(self, valid_yaml_content):
        """测试更新 YAML 记录"""
        record = TestPlanYaml.objects.create(
            file_name='update_test.yaml',
            file_content=valid_yaml_content,
            file_size=len(valid_yaml_content),
            validation_status='valid',
            create_user=1
        )
        
        # 更新记录
        record.validation_status = 'warning'
        record.plan_name = 'Updated Test Plan'
        record.save()
        
        # 重新查询验证
        updated_record = TestPlanYaml.objects.get(id=record.id)
        assert updated_record.validation_status == 'warning'
        assert updated_record.plan_name == 'Updated Test Plan'
        
        print(f"\n✅ 更新 YAML 记录成功: ID={record.id}")
    
    def test_delete_yaml_record(self, valid_yaml_content):
        """测试删除 YAML 记录"""
        record = TestPlanYaml.objects.create(
            file_name='delete_test.yaml',
            file_content=valid_yaml_content,
            file_size=len(valid_yaml_content),
            validation_status='valid',
            create_user=1
        )
        
        record_id = record.id
        record.delete()
        
        # 验证记录已删除
        assert not TestPlanYaml.objects.filter(id=record_id).exists()
        
        print(f"\n✅ 删除 YAML 记录成功: ID={record_id}")
    
    def test_yaml_record_ordering(self, valid_yaml_content):
        """测试 YAML 记录排序"""
        import time
        
        # 创建多条记录
        for i in range(3):
            TestPlanYaml.objects.create(
                file_name=f'order_test_{i}.yaml',
                file_content=valid_yaml_content,
                file_size=len(valid_yaml_content),
                validation_status='valid',
                create_user=1
            )
            time.sleep(0.01)  # 确保创建时间不同
        
        # 查询记录，应按创建时间倒序
        records = list(TestPlanYaml.objects.filter(file_name__startswith='order_test_'))
        
        # 验证排序（最新的在前面）
        for i in range(len(records) - 1):
            assert records[i].create_time >= records[i + 1].create_time
        
        print(f"\n✅ YAML 记录排序正确: 最新记录在前")


@pytest.mark.django_db
class TestYAMLValidationIntegration:
    """测试 YAML 验证与模型的集成"""
    
    def test_validate_and_save_valid_yaml(self, valid_yaml_content):
        """测试验证有效 YAML 并保存"""
        # 验证 YAML
        validation_result = validate_yaml_full(valid_yaml_content)
        
        assert validation_result['valid'] is True
        
        # 保存到数据库
        record = TestPlanYaml.objects.create(
            file_name='validated_plan.yaml',
            file_content=valid_yaml_content,
            file_size=len(valid_yaml_content),
            validation_status='valid',
            create_user=1
        )
        
        assert record.validation_status == 'valid'
        
        print(f"\n✅ 验证并保存有效 YAML 成功: ID={record.id}")
    
    def test_validate_and_reject_invalid_yaml(self, invalid_yaml_content):
        """测试验证无效 YAML 并拒绝保存"""
        # 验证 YAML
        validation_result = validate_yaml_full(invalid_yaml_content)
        
        assert validation_result['valid'] is False
        assert len(validation_result['error_message']) > 0
        
        # 不应该保存无效的 YAML（模拟业务逻辑）
        print(f"\n✅ 无效 YAML 被正确拒绝: {validation_result['error_message'][:50]}...")
    
    def test_batch_validation_workflow(self, valid_yaml_content, invalid_yaml_content):
        """测试批量验证工作流"""
        test_cases = [
            ('valid_1.yaml', valid_yaml_content, True),
            ('invalid_1.yaml', invalid_yaml_content, False),
            ('valid_2.yaml', valid_yaml_content, True),
        ]
        
        results = []
        for file_name, content, expected_valid in test_cases:
            validation_result = validate_yaml_full(content)
            
            assert validation_result['valid'] == expected_valid
            
            # 只保存有效的 YAML
            if validation_result['valid']:
                record = TestPlanYaml.objects.create(
                    file_name=file_name,
                    file_content=content,
                    file_size=len(content),
                    validation_status='valid',
                    create_user=1
                )
                results.append(record.id)
        
        # 验证只保存了有效的 YAML
        assert len(results) == 2
        assert TestPlanYaml.objects.filter(id__in=results).count() == 2
        
        print(f"\n✅ 批量验证工作流成功: 保存了 {len(results)} 个有效文件")


@pytest.mark.django_db
class TestYAMLDataExtraction:
    """测试从 YAML 中提取数据"""
    
    def test_extract_basic_info(self, valid_yaml_content):
        """测试提取基本信息"""
        import yaml
        
        # 解析 YAML
        data = yaml.safe_load(valid_yaml_content)
        
        # 提取信息
        version = data['metadata']['version']
        description = data['metadata'].get('description', '')
        machine_count = len(data['hardware']['machines'])
        
        # 保存到数据库
        record = TestPlanYaml.objects.create(
            file_name='extract_test.yaml',
            file_content=valid_yaml_content,
            file_size=len(valid_yaml_content),
            plan_name=description,
            validation_status='valid',
            create_user=1,
            analysis_result={
                'version': version,
                'machine_count': machine_count
            }
        )
        
        assert record.analysis_result['version'] == '2.0'
        assert record.analysis_result['machine_count'] == 1
        
        print(f"\n✅ 提取基本信息成功: version={version}, machines={machine_count}")
    
    def test_extract_hardware_info(self):
        """测试提取硬件信息"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"

hardware:
  machines:
    - id: 1
      hostname: "gpu-test-01"
      ipAddress: "192.168.1.100"
      asicName: "Navi10 GFX1010"
      gpuModel: "RX 5700 XT"
      productName: "navi10"

environment:
  machines:
    gpu-test-01:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          test_type: "Benchmark"
          execution_case_list: ["test"]
"""
        
        import yaml
        data = yaml.safe_load(yaml_content)
        
        # 提取硬件信息
        machine = data['hardware']['machines'][0]
        gpu_model = machine.get('gpuModel', '')
        product_name = machine.get('productName', '')
        
        # 保存到数据库
        record = TestPlanYaml.objects.create(
            file_name='hardware_test.yaml',
            file_content=yaml_content,
            file_size=len(yaml_content),
            gpu=gpu_model,
            validation_status='valid',
            create_user=1,
            analysis_result={
                'product_name': product_name,
                'gpu_model': gpu_model
            }
        )
        
        assert record.gpu == 'RX 5700 XT'
        assert record.analysis_result['product_name'] == 'navi10'
        
        print(f"\n✅ 提取硬件信息成功: GPU={gpu_model}")


@pytest.mark.django_db
class TestYAMLQueryOperations:
    """测试 YAML 查询操作"""
    
    def test_filter_by_validation_status(self, valid_yaml_content):
        """测试按验证状态过滤"""
        # 创建不同状态的记录
        TestPlanYaml.objects.create(
            file_name='valid_1.yaml',
            file_content=valid_yaml_content,
            file_size=len(valid_yaml_content),
            validation_status='valid',
            create_user=1
        )
        
        TestPlanYaml.objects.create(
            file_name='warning_1.yaml',
            file_content=valid_yaml_content,
            file_size=len(valid_yaml_content),
            validation_status='warning',
            create_user=1
        )
        
        # 查询有效的记录
        valid_records = TestPlanYaml.objects.filter(validation_status='valid')
        warning_records = TestPlanYaml.objects.filter(validation_status='warning')
        
        assert valid_records.count() >= 1
        assert warning_records.count() >= 1
        
        print(f"\n✅ 按状态过滤成功: valid={valid_records.count()}, warning={warning_records.count()}")
    
    def test_search_by_filename(self, valid_yaml_content):
        """测试按文件名搜索"""
        # 创建多个记录
        for i in range(3):
            TestPlanYaml.objects.create(
                file_name=f'benchmark_plan_{i}.yaml',
                file_content=valid_yaml_content,
                file_size=len(valid_yaml_content),
                validation_status='valid',
                create_user=1
            )
        
        # 搜索包含 "benchmark" 的文件
        records = TestPlanYaml.objects.filter(file_name__icontains='benchmark')
        
        assert records.count() >= 3
        
        print(f"\n✅ 文件名搜索成功: 找到 {records.count()} 个文件")
    
    def test_pagination(self, valid_yaml_content):
        """测试分页查询"""
        # 创建10条记录
        for i in range(10):
            TestPlanYaml.objects.create(
                file_name=f'page_test_{i:02d}.yaml',
                file_content=valid_yaml_content,
                file_size=len(valid_yaml_content),
                validation_status='valid',
                create_user=1
            )
        
        # 分页查询
        page_size = 5
        page_1 = list(TestPlanYaml.objects.all()[:page_size])
        page_2 = list(TestPlanYaml.objects.all()[page_size:page_size*2])
        
        assert len(page_1) == page_size
        assert len(page_2) == page_size
        
        # 验证没有重复
        ids_1 = [r.id for r in page_1]
        ids_2 = [r.id for r in page_2]
        assert len(set(ids_1) & set(ids_2)) == 0
        
        print(f"\n✅ 分页查询成功: 第1页 {len(page_1)} 条，第2页 {len(page_2)} 条")

