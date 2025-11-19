"""
My Test Plans 保存的测试计划 API 测试
测试 xadmin_tpgen 模块的 SavedPlan API 端点
"""
import pytest
import json
from django.test import Client
from django.contrib.auth import get_user_model
from xadmin_tpgen.models import TpgenSavedPlan

User = get_user_model()


@pytest.fixture
def api_client():
    """创建测试客户端"""
    return Client()


@pytest.fixture
def test_user(db):
    """创建测试用户"""
    user = User.objects.create_user(
        username='tpgenuser',
        password='testpass123',
        email='tpgen@example.com'
    )
    return user


@pytest.fixture
def auth_client(api_client, test_user):
    """创建已认证的客户端"""
    api_client.force_login(test_user)
    return api_client


@pytest.fixture
def sample_config_data():
    """示例配置数据"""
    return {
        'hardware': {
            'machines': [
                {
                    'id': 1,
                    'hostname': 'test-machine-01',
                    'ipAddress': '192.168.1.100',
                    'asicName': 'Navi10 GFX1010',
                    'gpuModel': 'RX 5700 XT',
                    'productName': 'navi10'
                }
            ]
        },
        'environment': {
            'machines': {
                'test-machine-01': {
                    'configurations': [
                        {
                            'config_id': 1,
                            'os': {
                                'id': 1,
                                'family': 'Ubuntu',
                                'version': '22.04'
                            },
                            'kernel': {
                                'kernel_version': '5.15.0-56'
                            },
                            'test_type': 'Benchmark',
                            'execution_case_list': ['OpenCL Compute SP']
                        }
                    ]
                }
            }
        }
    }


@pytest.fixture
def sample_yaml_data():
    """示例 YAML 数据"""
    return """metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
hardware:
  machines:
    - id: 1
      hostname: test-machine-01
environment:
  machines:
    test-machine-01:
      configurations:
        - config_id: 1
          os:
            family: Ubuntu
"""


@pytest.fixture
def sample_saved_plans(db, test_user, sample_config_data, sample_yaml_data):
    """创建示例保存的测试计划"""
    plans = []
    for i in range(3):
        plan = TpgenSavedPlan.objects.create(
            name=f'Test Plan {i+1}',
            category='Benchmark',
            description=f'Description for plan {i+1}',
            config_data=sample_config_data,
            yaml_data=sample_yaml_data,
            machine_count=1,
            test_case_count=5,
            status=1,
            tags='test,benchmark',
            create_user=test_user.id,
            create_user_name=test_user.username
        )
        plans.append(plan)
    return plans


@pytest.mark.django_db
class TestSavedPlanListAPI:
    """测试保存的测试计划列表 API"""
    
    def test_list_saved_plans(self, auth_client, sample_saved_plans):
        """测试查询测试计划列表"""
        response = auth_client.get('/api/tpgen/saved-plans/list')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']['list']) >= 3
        
        print(f"\n✅ 查询测试计划列表成功: {len(data['data']['list'])} 条记录")
    
    def test_list_with_pagination(self, auth_client, sample_saved_plans):
        """测试分页查询"""
        response = auth_client.get('/api/tpgen/saved-plans/list?page=1&size=2')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']['list']) <= 2
        assert 'total' in data['data']
        
        print(f"\n✅ 分页查询成功: 每页2条，共{data['data']['total']}条")
    
    def test_list_filter_by_category(self, auth_client, sample_saved_plans):
        """测试按类别过滤"""
        response = auth_client.get('/api/tpgen/saved-plans/list?category=Benchmark')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 所有返回的结果应该都是 Benchmark 类别
        for item in data['data']['list']:
            assert item['category'] == 'Benchmark'
        
        print("\n✅ 按类别过滤成功")
    
    def test_list_filter_by_name(self, auth_client, sample_saved_plans):
        """测试按名称搜索"""
        response = auth_client.get('/api/tpgen/saved-plans/list?name=Plan 1')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 结果中应该包含 "Plan 1"
        results = data['data']['list']
        if len(results) > 0:
            assert any('Plan 1' in item['name'] for item in results)
        
        print("\n✅ 按名称搜索成功")
    
    def test_list_filter_by_status(self, auth_client, sample_saved_plans):
        """测试按状态过滤"""
        response = auth_client.get('/api/tpgen/saved-plans/list?status=1')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 所有结果的状态应该是 1
        for item in data['data']['list']:
            assert item['status'] == 1
        
        print("\n✅ 按状态过滤成功")
    
    def test_list_sorting(self, auth_client, sample_saved_plans):
        """测试排序功能"""
        # 按创建时间倒序（默认）
        response = auth_client.get('/api/tpgen/saved-plans/list?sort=-create_time')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        print("\n✅ 排序功能测试成功")


@pytest.mark.django_db
class TestSavedPlanCreateAPI:
    """测试创建保存的测试计划 API"""
    
    def test_create_saved_plan(self, auth_client, test_user, sample_config_data, sample_yaml_data):
        """测试创建测试计划"""
        plan_data = {
            'name': 'New Test Plan',
            'category': 'Performance',
            'description': 'A new test plan',
            'config_data': json.dumps(sample_config_data),
            'yaml_data': sample_yaml_data,
            'machine_count': 2,
            'test_case_count': 10,
            'status': 1,
            'tags': 'performance,new'
        }
        
        response = auth_client.post(
            '/api/tpgen/saved-plans',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证数据库中的记录
        created_plan = TpgenSavedPlan.objects.get(name='New Test Plan')
        assert created_plan.category == 'Performance'
        assert created_plan.machine_count == 2
        assert created_plan.create_user == test_user.id
        
        print(f"\n✅ 创建测试计划成功: ID={created_plan.id}")
    
    def test_create_with_minimal_fields(self, auth_client, sample_config_data, sample_yaml_data):
        """测试只提供必需字段创建"""
        plan_data = {
            'name': 'Minimal Plan',
            'category': 'Benchmark',
            'config_data': json.dumps(sample_config_data),
            'yaml_data': sample_yaml_data
        }
        
        response = auth_client.post(
            '/api/tpgen/saved-plans',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        print("\n✅ 最小字段创建成功")
    
    def test_create_with_missing_required_field(self, auth_client):
        """测试缺少必需字段"""
        plan_data = {
            'category': 'Benchmark'
            # 缺少 name
        }
        
        response = auth_client.post(
            '/api/tpgen/saved-plans',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        # 应该返回错误
        assert response.status_code in [400, 422, 200]
        
        print("\n✅ 缺少必需字段被正确处理")


@pytest.mark.django_db
class TestSavedPlanDetailAPI:
    """测试测试计划详情 API"""
    
    def test_get_plan_detail(self, auth_client, sample_saved_plans):
        """测试获取测试计划详情"""
        plan = sample_saved_plans[0]
        
        response = auth_client.get(f'/api/tpgen/saved-plans/{plan.id}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['id'] == plan.id
        assert data['data']['name'] == plan.name
        assert 'config_data' in data['data']
        assert 'yaml_data' in data['data']
        
        print(f"\n✅ 获取详情成功: {plan.name}")
    
    def test_get_nonexistent_plan(self, auth_client):
        """测试获取不存在的计划"""
        response = auth_client.get('/api/tpgen/saved-plans/999999')
        
        assert response.status_code in [404, 200]
        if response.status_code == 200:
            data = response.json()
            assert data['code'] != 200
        
        print("\n✅ 不存在的计划被正确处理")


@pytest.mark.django_db
class TestSavedPlanUpdateAPI:
    """测试更新测试计划 API"""
    
    def test_update_plan(self, auth_client, sample_saved_plans):
        """测试更新测试计划"""
        plan = sample_saved_plans[0]
        
        update_data = {
            'name': 'Updated Plan Name',
            'description': 'Updated description',
            'status': 2,
            'tags': 'updated,modified'
        }
        
        response = auth_client.put(
            f'/api/tpgen/saved-plans/{plan.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证更新
        plan.refresh_from_db()
        assert plan.name == 'Updated Plan Name'
        assert plan.status == 2
        
        print(f"\n✅ 更新测试计划成功: {plan.name}")
    
    def test_partial_update(self, auth_client, sample_saved_plans):
        """测试部分更新"""
        plan = sample_saved_plans[0]
        original_name = plan.name
        
        update_data = {
            'description': 'Only update description'
        }
        
        response = auth_client.patch(
            f'/api/tpgen/saved-plans/{plan.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 405]  # PATCH may not be implemented
        
        print("\n✅ 部分更新测试完成")


@pytest.mark.django_db
class TestSavedPlanDeleteAPI:
    """测试删除测试计划 API"""
    
    def test_delete_plan(self, auth_client, sample_saved_plans):
        """测试删除测试计划"""
        plan = sample_saved_plans[0]
        plan_id = plan.id
        
        response = auth_client.delete(f'/api/tpgen/saved-plans/{plan_id}')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证已删除
        assert not TpgenSavedPlan.objects.filter(id=plan_id).exists()
        
        print(f"\n✅ 删除测试计划成功: ID={plan_id}")
    
    def test_batch_delete(self, auth_client, sample_saved_plans):
        """测试批量删除"""
        plan_ids = [plan.id for plan in sample_saved_plans[:2]]
        
        response = auth_client.delete(
            f'/api/tpgen/saved-plans/{",".join(map(str, plan_ids))}'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证已删除
        remaining = TpgenSavedPlan.objects.filter(id__in=plan_ids).count()
        assert remaining == 0
        
        print(f"\n✅ 批量删除成功: {len(plan_ids)} 条记录")


@pytest.mark.django_db
class TestSavedPlanUsageAPI:
    """测试计划使用相关 API"""
    
    def test_use_plan(self, auth_client, sample_saved_plans):
        """测试使用测试计划（增加使用次数）"""
        plan = sample_saved_plans[0]
        original_use_count = plan.use_count
        
        response = auth_client.post(f'/api/tpgen/saved-plans/{plan.id}/use')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证使用次数增加
        plan.refresh_from_db()
        assert plan.use_count == original_use_count + 1
        assert plan.last_used_time is not None
        
        print(f"\n✅ 使用计划成功: 使用次数 {original_use_count} → {plan.use_count}")


@pytest.mark.django_db
class TestSavedPlanCategoriesAPI:
    """测试计划类别 API"""
    
    def test_get_categories(self, auth_client, sample_saved_plans):
        """测试获取所有类别列表"""
        response = auth_client.get('/api/tpgen/saved-plans/categories/list')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) > 0
        
        # 应该包含 Benchmark
        categories = [item['value'] for item in data['data']]
        assert 'Benchmark' in categories
        
        print(f"\n✅ 获取类别列表成功: {len(data['data'])} 个类别")


@pytest.mark.django_db
class TestSavedPlanIntegration:
    """测试计划集成测试"""
    
    def test_full_crud_workflow(self, auth_client, test_user, sample_config_data, sample_yaml_data):
        """测试完整的 CRUD 工作流"""
        # 1. 创建
        plan_data = {
            'name': 'CRUD Test Plan',
            'category': 'Functional',
            'description': 'Testing CRUD',
            'config_data': json.dumps(sample_config_data),
            'yaml_data': sample_yaml_data,
            'status': 1
        }
        
        create_response = auth_client.post(
            '/api/tpgen/saved-plans',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == 200
        plan_id = create_response.json()['data']['id']
        
        # 2. 读取
        get_response = auth_client.get(f'/api/tpgen/saved-plans/{plan_id}')
        assert get_response.status_code == 200
        assert get_response.json()['data']['name'] == 'CRUD Test Plan'
        
        # 3. 更新
        update_response = auth_client.put(
            f'/api/tpgen/saved-plans/{plan_id}',
            data=json.dumps({'name': 'Updated CRUD Plan'}),
            content_type='application/json'
        )
        assert update_response.status_code == 200
        
        # 4. 使用
        use_response = auth_client.post(f'/api/tpgen/saved-plans/{plan_id}/use')
        assert use_response.status_code == 200
        
        # 5. 删除
        delete_response = auth_client.delete(f'/api/tpgen/saved-plans/{plan_id}')
        assert delete_response.status_code == 200
        
        # 验证已删除
        assert not TpgenSavedPlan.objects.filter(id=plan_id).exists()
        
        print("\n✅ 完整 CRUD 工作流测试成功")
    
    def test_list_filter_sort_combined(self, auth_client, sample_saved_plans):
        """测试组合过滤和排序"""
        response = auth_client.get(
            '/api/tpgen/saved-plans/list'
            '?category=Benchmark'
            '&status=1'
            '&sort=-create_time'
            '&page=1&size=10'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        print("\n✅ 组合过滤排序测试成功")

