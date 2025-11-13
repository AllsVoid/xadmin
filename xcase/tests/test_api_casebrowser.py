"""
Case Browser API 测试集

测试用例浏览器的所有 API 端点：
- 获取 case 元数据列表
- 获取 case 详情
- 标签管理（增删）
- 选项管理（增删改）
"""
import pytest
from django.test import Client
from xcase.models import CaseMetadata, CaseTag, CaseOption


@pytest.mark.casebrowser
class TestGetCasesMetadata:
    """测试获取 cases 元数据列表"""
    
    def test_get_cases_metadata_success(self, api_client, temp_casespace, sample_case_with_tags):
        """测试成功获取 cases 元数据"""
        casespace = temp_casespace['casespace']
        
        response = api_client.get(
            f'/casebrowser/casespaces/{casespace}/cases'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
        assert len(data['data']) > 0
        
        # 验证返回的数据结构
        case_data = data['data'][0]
        assert 'casespace' in case_data
        assert 'caseName' in case_data
        assert 'tags' in case_data
        assert isinstance(case_data['tags'], list)
    
    def test_get_cases_metadata_with_tags(self, api_client, temp_casespace, sample_case_with_tags):
        """测试返回的元数据包含标签"""
        casespace = temp_casespace['casespace']
        
        response = api_client.get(
            f'/casebrowser/casespaces/{casespace}/cases'
        )
        
        assert response.status_code == 200
        data = response.json()
        case_data = data['data'][0]
        
        # 验证标签
        expected_tags = sample_case_with_tags['tags']
        assert set(case_data['tags']) == set(expected_tags)
    
    def test_get_cases_metadata_empty_casespace(self, api_client, temp_casespace):
        """测试空 casespace"""
        # 创建空的 casespace
        from xcase.file_manager import file_manager
        empty_casespace = file_manager.storage_root / 'empty_casespace'
        empty_casespace.mkdir(parents=True, exist_ok=True)
        
        response = api_client.get(
            f'/casebrowser/casespaces/empty_casespace/cases'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] == []


@pytest.mark.casebrowser
class TestGetCaseDetail:
    """测试获取单个 case 详情"""
    
    def test_get_case_detail_success(self, api_client, sample_case_with_tags):
        """测试成功获取 case 详情"""
        metadata = sample_case_with_tags['metadata']
        
        response = api_client.get(
            f'/casebrowser/casespaces/{metadata.casespace}/cases/{metadata.case_name}'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证数据结构
        case_detail = data['data']
        assert case_detail['casespace'] == metadata.casespace
        assert case_detail['caseName'] == metadata.case_name
        assert 'tags' in case_detail
        assert 'options' in case_detail
        assert isinstance(case_detail['tags'], list)
        assert isinstance(case_detail['options'], list)
    
    def test_get_case_detail_with_options(self, api_client, sample_case_with_options):
        """测试获取包含选项的 case 详情"""
        metadata = sample_case_with_options['metadata']
        
        response = api_client.get(
            f'/casebrowser/casespaces/{metadata.casespace}/cases/{metadata.case_name}'
        )
        
        assert response.status_code == 200
        data = response.json()
        case_detail = data['data']
        
        # 验证选项
        expected_options = sample_case_with_options['options']
        returned_options = {opt['key']: opt['value'] for opt in case_detail['options']}
        assert returned_options == expected_options
    
    def test_get_case_detail_new_case(self, api_client, temp_casespace):
        """测试获取新 case（自动创建元数据）"""
        casespace = temp_casespace['casespace']
        new_case_name = 'new_test_case'
        
        # 创建新 case 目录
        from xcase.file_manager import file_manager
        new_case_path = file_manager.storage_root / casespace / new_case_name
        new_case_path.mkdir(parents=True, exist_ok=True)
        
        response = api_client.get(
            f'/casebrowser/casespaces/{casespace}/cases/{new_case_name}'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证自动创建了元数据
        assert CaseMetadata.objects.filter(
            casespace=casespace,
            case_name=new_case_name
        ).exists()


@pytest.mark.casebrowser
class TestTagManagement:
    """测试标签管理功能"""
    
    def test_add_tag_success(self, api_client, sample_case_metadata):
        """测试成功添加标签"""
        metadata = sample_case_metadata
        new_tag = 'performance'
        
        response = api_client.post(
            '/casebrowser/cases/tags',
            json={
                'casespace': metadata.casespace,
                'caseName': metadata.case_name,
                'tag': new_tag
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        assert '成功添加标签' in data['data']['message']
        
        # 验证数据库中存在该标签
        assert CaseTag.objects.filter(
            metadata=metadata,
            tag=new_tag
        ).exists()
    
    def test_add_duplicate_tag(self, api_client, sample_case_with_tags):
        """测试添加重复标签"""
        metadata = sample_case_with_tags['metadata']
        existing_tag = sample_case_with_tags['tags'][0]
        
        response = api_client.post(
            '/casebrowser/cases/tags',
            json={
                'casespace': metadata.casespace,
                'caseName': metadata.case_name,
                'tag': existing_tag
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert '标签已存在' in data['data']['message']
    
    def test_add_tag_to_new_case(self, api_client, temp_casespace):
        """测试为新 case 添加标签（自动创建元数据）"""
        casespace = temp_casespace['casespace']
        new_case_name = 'new_case_with_tag'
        
        response = api_client.post(
            '/casebrowser/cases/tags',
            json={
                'casespace': casespace,
                'caseName': new_case_name,
                'tag': 'new_tag'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证自动创建了元数据和标签
        metadata = CaseMetadata.objects.get(
            casespace=casespace,
            case_name=new_case_name
        )
        assert CaseTag.objects.filter(
            metadata=metadata,
            tag='new_tag'
        ).exists()
    
    def test_delete_tag_success(self, api_client, sample_case_with_tags):
        """测试成功删除标签"""
        metadata = sample_case_with_tags['metadata']
        tag_to_delete = sample_case_with_tags['tags'][0]
        
        response = api_client.delete(
            f'/casebrowser/cases/tags',
            params={
                'casespace': metadata.casespace,
                'case_name': metadata.case_name,
                'tag': tag_to_delete
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        assert '成功删除标签' in data['data']['message']
        
        # 验证标签已从数据库中删除
        assert not CaseTag.objects.filter(
            metadata=metadata,
            tag=tag_to_delete
        ).exists()
    
    def test_delete_nonexistent_tag(self, api_client, sample_case_metadata):
        """测试删除不存在的标签"""
        metadata = sample_case_metadata
        
        response = api_client.delete(
            f'/casebrowser/cases/tags',
            params={
                'casespace': metadata.casespace,
                'case_name': metadata.case_name,
                'tag': 'nonexistent_tag'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert '标签不存在' in data['data']['message']
    
    def test_delete_tag_case_not_found(self, api_client):
        """测试删除标签时 case 不存在"""
        response = api_client.delete(
            f'/casebrowser/cases/tags',
            params={
                'casespace': 'nonexistent_casespace',
                'case_name': 'nonexistent_case',
                'tag': 'some_tag'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 404
        assert 'Case 不存在' in data['data']


@pytest.mark.casebrowser
class TestOptionManagement:
    """测试选项管理功能"""
    
    def test_add_option_success(self, api_client, sample_case_metadata):
        """测试成功添加选项"""
        metadata = sample_case_metadata
        
        response = api_client.post(
            '/casebrowser/cases/options',
            json={
                'casespace': metadata.casespace,
                'caseName': metadata.case_name,
                'key': 'environment',
                'value': 'production'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        assert '成功添加选项' in data['data']['message']
        
        # 验证数据库中存在该选项
        option = CaseOption.objects.get(
            metadata=metadata,
            key='environment'
        )
        assert option.value == 'production'
    
    def test_add_option_to_new_case(self, api_client, temp_casespace):
        """测试为新 case 添加选项（自动创建元数据）"""
        casespace = temp_casespace['casespace']
        new_case_name = 'new_case_with_option'
        
        response = api_client.post(
            '/casebrowser/cases/options',
            json={
                'casespace': casespace,
                'caseName': new_case_name,
                'key': 'version',
                'value': '1.0.0'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证自动创建了元数据和选项
        metadata = CaseMetadata.objects.get(
            casespace=casespace,
            case_name=new_case_name
        )
        option = CaseOption.objects.get(
            metadata=metadata,
            key='version'
        )
        assert option.value == '1.0.0'
    
    def test_add_option_update_existing(self, api_client, sample_case_with_options):
        """测试添加已存在的选项（应该更新）"""
        metadata = sample_case_with_options['metadata']
        existing_key = list(sample_case_with_options['options'].keys())[0]
        new_value = 'updated_value'
        
        response = api_client.post(
            '/casebrowser/cases/options',
            json={
                'casespace': metadata.casespace,
                'caseName': metadata.case_name,
                'key': existing_key,
                'value': new_value
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert '成功更新选项' in data['data']['message']
        
        # 验证值已更新
        option = CaseOption.objects.get(
            metadata=metadata,
            key=existing_key
        )
        assert option.value == new_value
    
    def test_update_option_success(self, api_client, sample_case_with_options):
        """测试成功更新选项"""
        metadata = sample_case_with_options['metadata']
        option_key = list(sample_case_with_options['options'].keys())[0]
        new_value = 'updated_by_put'
        
        response = api_client.put(
            '/casebrowser/cases/options',
            json={
                'casespace': metadata.casespace,
                'caseName': metadata.case_name,
                'key': option_key,
                'value': new_value
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        assert '成功更新选项' in data['data']['message']
        
        # 验证值已更新
        option = CaseOption.objects.get(
            metadata=metadata,
            key=option_key
        )
        assert option.value == new_value
    
    def test_update_option_not_found(self, api_client, sample_case_metadata):
        """测试更新不存在的选项"""
        metadata = sample_case_metadata
        
        response = api_client.put(
            '/casebrowser/cases/options',
            json={
                'casespace': metadata.casespace,
                'caseName': metadata.case_name,
                'key': 'nonexistent_key',
                'value': 'some_value'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 404
        assert '选项不存在' in data['data']
    
    def test_update_option_case_not_found(self, api_client):
        """测试更新选项时 case 不存在"""
        response = api_client.put(
            '/casebrowser/cases/options',
            json={
                'casespace': 'nonexistent_casespace',
                'caseName': 'nonexistent_case',
                'key': 'some_key',
                'value': 'some_value'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 404
        assert 'Case 不存在' in data['data']
    
    def test_delete_option_success(self, api_client, sample_case_with_options):
        """测试成功删除选项"""
        metadata = sample_case_with_options['metadata']
        option_key = list(sample_case_with_options['options'].keys())[0]
        
        response = api_client.delete(
            f'/casebrowser/cases/options',
            params={
                'casespace': metadata.casespace,
                'case_name': metadata.case_name,
                'key': option_key
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        assert '成功删除选项' in data['data']['message']
        
        # 验证选项已从数据库中删除
        assert not CaseOption.objects.filter(
            metadata=metadata,
            key=option_key
        ).exists()
    
    def test_delete_nonexistent_option(self, api_client, sample_case_metadata):
        """测试删除不存在的选项"""
        metadata = sample_case_metadata
        
        response = api_client.delete(
            f'/casebrowser/cases/options',
            params={
                'casespace': metadata.casespace,
                'case_name': metadata.case_name,
                'key': 'nonexistent_key'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert '选项不存在' in data['data']['message']
    
    def test_delete_option_case_not_found(self, api_client):
        """测试删除选项时 case 不存在"""
        response = api_client.delete(
            f'/casebrowser/cases/options',
            params={
                'casespace': 'nonexistent_casespace',
                'case_name': 'nonexistent_case',
                'key': 'some_key'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 404
        assert 'Case 不存在' in data['data']


@pytest.mark.casebrowser
class TestCaseBrowserIntegration:
    """集成测试：完整的 case browser 工作流"""
    
    @pytest.mark.integration
    def test_complete_case_metadata_workflow(self, api_client, temp_casespace):
        """测试完整的 case 元数据管理流程"""
        casespace = temp_casespace['casespace']
        case_name = temp_casespace['case']
        
        # 1. 添加标签
        tags = ['smoke', 'regression', 'critical']
        for tag in tags:
            response = api_client.post(
                '/casebrowser/cases/tags',
                json={
                    'casespace': casespace,
                    'caseName': case_name,
                    'tag': tag
                }
            )
            assert response.status_code == 200
        
        # 2. 添加选项
        options = {
            'priority': 'high',
            'owner': 'qa_team',
            'environment': 'staging'
        }
        for key, value in options.items():
            response = api_client.post(
                '/casebrowser/cases/options',
                json={
                    'casespace': casespace,
                    'caseName': case_name,
                    'key': key,
                    'value': value
                }
            )
            assert response.status_code == 200
        
        # 3. 获取 case 详情并验证
        response = api_client.get(
            f'/casebrowser/casespaces/{casespace}/cases/{case_name}'
        )
        assert response.status_code == 200
        case_detail = response.json()['data']
        
        assert set(case_detail['tags']) == set(tags)
        returned_options = {opt['key']: opt['value'] for opt in case_detail['options']}
        assert returned_options == options
        
        # 4. 更新一个选项
        response = api_client.put(
            '/casebrowser/cases/options',
            json={
                'casespace': casespace,
                'caseName': case_name,
                'key': 'priority',
                'value': 'critical'
            }
        )
        assert response.status_code == 200
        
        # 5. 删除一个标签
        response = api_client.delete(
            '/casebrowser/cases/tags',
            params={
                'casespace': casespace,
                'case_name': case_name,
                'tag': 'smoke'
            }
        )
        assert response.status_code == 200
        
        # 6. 验证最终状态
        response = api_client.get(
            f'/casebrowser/casespaces/{casespace}/cases/{case_name}'
        )
        final_detail = response.json()['data']
        
        assert 'smoke' not in final_detail['tags']
        assert len(final_detail['tags']) == 2
        
        final_options = {opt['key']: opt['value'] for opt in final_detail['options']}
        assert final_options['priority'] == 'critical'

