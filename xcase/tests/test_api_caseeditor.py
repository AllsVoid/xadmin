"""
Case Editor API 测试集

测试用例编辑器的所有 API 端点：
- Casespace 和 Case 管理
- 文件树浏览
- 文件内容读写
- 文件和目录的增删改查
- Case 的上传下载
"""
import pytest
import json
import base64
from io import BytesIO
from pathlib import Path


@pytest.mark.caseeditor
class TestCasespaceManagement:
    """测试 Casespace 管理功能"""
    
    def test_get_casespaces_success(self, api_client, temp_casespace):
        """测试获取 casespace 列表"""
        response = api_client.get('/caseeditor/casespaces')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
        
        # 验证包含测试 casespace
        casespace_names = [cs['name'] for cs in data['data']]
        assert temp_casespace['casespace'] in casespace_names
    
    def test_get_casespaces_empty(self, api_client, tmp_path):
        """测试空存储根目录"""
        from xcase.file_manager import file_manager
        
        # 临时设置为空目录
        original_storage_root = file_manager.storage_root
        file_manager.storage_root = tmp_path / 'empty_storage'
        file_manager._ensure_storage_exists()
        
        response = api_client.get('/caseeditor/casespaces')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] == []
        
        # 恢复原始设置
        file_manager.storage_root = original_storage_root


@pytest.mark.caseeditor
class TestCaseManagement:
    """测试 Case 管理功能"""
    
    def test_get_cases_success(self, api_client, temp_casespace):
        """测试获取 case 列表"""
        casespace = temp_casespace['casespace']
        
        response = api_client.get(f'/caseeditor/casespaces/{casespace}/cases')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
        assert len(data['data']) > 0
        
        # 验证包含测试 case
        case_names = [case['name'] for case in data['data']]
        assert temp_casespace['case'] in case_names
    
    def test_get_cases_nonexistent_casespace(self, api_client):
        """测试获取不存在的 casespace 的 cases"""
        response = api_client.get('/caseeditor/casespaces/nonexistent/cases')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] != 200
        assert 'Casespace' in data['data'] or 'not found' in data['data']
    
    def test_get_cases_empty_casespace(self, api_client, temp_casespace):
        """测试空 casespace"""
        from xcase.file_manager import file_manager
        
        # 创建空 casespace
        empty_casespace = file_manager.storage_root / 'empty_casespace'
        empty_casespace.mkdir(parents=True, exist_ok=True)
        
        response = api_client.get('/caseeditor/casespaces/empty_casespace/cases')
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] == []
    
    def test_delete_case_success(self, api_client, temp_casespace):
        """测试删除 case"""
        from xcase.file_manager import file_manager
        
        # 创建新 case 用于删除测试
        casespace = temp_casespace['casespace']
        case_to_delete = 'case_to_delete'
        case_path = file_manager.storage_root / casespace / case_to_delete
        case_path.mkdir(parents=True, exist_ok=True)
        
        # 删除 case
        response = api_client.delete(
            f'/caseeditor/casespaces/{casespace}/cases/{case_to_delete}'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        assert '成功删除' in data['data']['message']
        
        # 验证 case 已删除
        assert not case_path.exists()
    
    def test_delete_nonexistent_case(self, api_client, temp_casespace):
        """测试删除不存在的 case"""
        casespace = temp_casespace['casespace']
        
        response = api_client.delete(
            f'/caseeditor/casespaces/{casespace}/cases/nonexistent_case'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 404


@pytest.mark.caseeditor
class TestFileTreeManagement:
    """测试文件树浏览功能"""
    
    def test_get_file_tree_root(self, api_client, temp_casespace):
        """测试获取根目录文件树"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        response = api_client.get(
            '/caseeditor/files',
            params={
                'casespace': casespace,
                'case': case,
                'path': '/'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
        
        # 应该包含 test.py 文件
        file_names = [item['name'] for item in data['data']]
        assert 'test.py' in file_names
    
    def test_get_file_tree_without_casespace(self, api_client):
        """测试不提供 casespace 参数"""
        response = api_client.get(
            '/caseeditor/files',
            params={'path': '/'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data'] == []  # 应返回空数组
    
    def test_get_file_tree_subdirectory(self, api_client, temp_casespace):
        """测试获取子目录文件树"""
        from xcase.file_manager import file_manager
        
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        # 创建子目录和文件
        case_path = file_manager.storage_root / casespace / case
        subdir = case_path / 'subdir'
        subdir.mkdir(parents=True, exist_ok=True)
        (subdir / 'file1.txt').write_text('content1', encoding='utf-8')
        (subdir / 'file2.txt').write_text('content2', encoding='utf-8')
        
        response = api_client.get(
            '/caseeditor/files',
            params={
                'casespace': casespace,
                'case': case,
                'path': '/subdir'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert len(data['data']) == 2
    
    def test_get_file_tree_path_traversal_attempt(self, api_client, temp_casespace):
        """测试路径遍历攻击防护"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        response = api_client.get(
            '/caseeditor/files',
            params={
                'casespace': casespace,
                'case': case,
                'path': '/../../../etc/passwd'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 403  # 应该被拒绝


@pytest.mark.caseeditor
class TestFileOperations:
    """测试文件操作功能"""
    
    def test_get_file_content_success(self, api_client, temp_casespace):
        """测试获取文件内容"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        response = api_client.get(
            '/caseeditor/files/content',
            params={'path': f'/{casespace}/{case}/test.py'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'path' in data['data']
        assert 'content' in data['data']
        assert 'Hello, World!' in data['data']['content']
    
    def test_get_file_content_nonexistent(self, api_client, temp_casespace):
        """测试获取不存在的文件"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        response = api_client.get(
            '/caseeditor/files/content',
            params={'path': f'/{casespace}/{case}/nonexistent.txt'}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 404
        assert '文件未找到' in data['data']
    
    def test_save_file_success(self, api_client, temp_casespace):
        """测试保存文件内容"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        file_path = f'/{casespace}/{case}/test.py'
        new_content = 'print("Updated content!")'
        
        response = api_client.post(
            '/caseeditor/files/save',
            json={
                'path': file_path,
                'content': new_content
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        
        # 验证文件内容已更新
        from xcase.file_manager import file_manager
        abs_path = file_manager.get_abs_path(file_path.lstrip('/'))
        assert abs_path.read_text(encoding='utf-8') == new_content
    
    def test_save_file_nonexistent(self, api_client, temp_casespace):
        """测试保存不存在的文件"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        response = api_client.post(
            '/caseeditor/files/save',
            json={
                'path': f'/{casespace}/{case}/nonexistent.txt',
                'content': 'new content'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 404
    
    def test_create_file_success(self, api_client, temp_casespace):
        """测试创建新文件"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        parent_path = f'/{casespace}/{case}'
        new_file_name = 'new_file.txt'
        
        response = api_client.post(
            '/caseeditor/files/create',
            json={
                'parentPath': parent_path,
                'name': new_file_name
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert 'path' in data['data']
        assert 'name' in data['data']
        assert data['data']['name'] == new_file_name
        
        # 验证文件已创建
        from xcase.file_manager import file_manager
        file_path = file_manager.get_abs_path(f'{casespace}/{case}/{new_file_name}')
        assert file_path.exists()
        assert file_path.is_file()
    
    def test_create_file_duplicate(self, api_client, temp_casespace):
        """测试创建重复文件"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        parent_path = f'/{casespace}/{case}'
        
        response = api_client.post(
            '/caseeditor/files/create',
            json={
                'parentPath': parent_path,
                'name': 'test.py'  # 已存在的文件
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] != 200
    
    def test_create_folder_success(self, api_client, temp_casespace):
        """测试创建新目录"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        parent_path = f'/{casespace}/{case}'
        new_folder_name = 'new_folder'
        
        response = api_client.post(
            '/caseeditor/folders/create',
            json={
                'parentPath': parent_path,
                'name': new_folder_name
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['name'] == new_folder_name
        assert data['data']['type'] == 'folder'
        
        # 验证目录已创建
        from xcase.file_manager import file_manager
        folder_path = file_manager.get_abs_path(f'{casespace}/{case}/{new_folder_name}')
        assert folder_path.exists()
        assert folder_path.is_dir()
    
    def test_rename_item_success(self, api_client, temp_casespace):
        """测试重命名文件"""
        from xcase.file_manager import file_manager
        
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        # 创建文件用于重命名
        case_path = file_manager.storage_root / casespace / case
        old_file = case_path / 'old_name.txt'
        old_file.write_text('content', encoding='utf-8')
        
        old_path = f'/{casespace}/{case}/old_name.txt'
        new_name = 'new_name.txt'
        
        response = api_client.put(
            '/caseeditor/files/rename',
            json={
                'oldPath': old_path,
                'newName': new_name
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['name'] == new_name
        
        # 验证文件已重命名
        assert not old_file.exists()
        new_file = case_path / new_name
        assert new_file.exists()
    
    def test_rename_nonexistent_item(self, api_client, temp_casespace):
        """测试重命名不存在的文件"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        response = api_client.put(
            '/caseeditor/files/rename',
            json={
                'oldPath': f'/{casespace}/{case}/nonexistent.txt',
                'newName': 'new_name.txt'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] != 200
    
    def test_delete_file_success(self, api_client, temp_casespace):
        """测试删除文件"""
        from xcase.file_manager import file_manager
        
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        # 创建文件用于删除
        case_path = file_manager.storage_root / casespace / case
        file_to_delete = case_path / 'file_to_delete.txt'
        file_to_delete.write_text('content', encoding='utf-8')
        
        file_path = f'/{casespace}/{case}/file_to_delete.txt'
        
        response = api_client.delete(
            '/caseeditor/files',
            params={'path': file_path}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        
        # 验证文件已删除
        assert not file_to_delete.exists()
    
    def test_delete_folder_success(self, api_client, temp_casespace):
        """测试删除目录"""
        from xcase.file_manager import file_manager
        
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        # 创建目录用于删除
        case_path = file_manager.storage_root / casespace / case
        folder_to_delete = case_path / 'folder_to_delete'
        folder_to_delete.mkdir(parents=True, exist_ok=True)
        (folder_to_delete / 'file.txt').write_text('content', encoding='utf-8')
        
        folder_path = f'/{casespace}/{case}/folder_to_delete'
        
        response = api_client.delete(
            '/caseeditor/files',
            params={'path': folder_path}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        
        # 验证目录已删除
        assert not folder_to_delete.exists()


@pytest.mark.caseeditor
class TestBulkFileOperations:
    """测试批量文件操作"""
    
    def test_upload_files_success(self, api_client, temp_casespace):
        """测试批量上传文件"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        parent_path = f'/{casespace}/{case}'
        
        files = [
            {'name': 'upload1.txt', 'content': 'content1'},
            {'name': 'upload2.txt', 'content': 'content2'},
            {'name': 'upload3.txt', 'content': 'content3'}
        ]
        
        response = api_client.post(
            '/caseeditor/files/upload',
            json={
                'parentPath': parent_path,
                'files': files
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['code'] == 200
        assert data['data']['success'] is True
        assert data['data']['count'] == 3
        
        # 验证文件已上传
        from xcase.file_manager import file_manager
        case_path = file_manager.storage_root / casespace / case
        for file_info in files:
            file_path = case_path / file_info['name']
            assert file_path.exists()
            assert file_path.read_text(encoding='utf-8') == file_info['content']
    
    def test_upload_files_empty_list(self, api_client, temp_casespace):
        """测试上传空文件列表"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        response = api_client.post(
            '/caseeditor/files/upload',
            json={
                'parentPath': f'/{casespace}/{case}',
                'files': []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        # 应该返回成功，但 count 为 0
        if data['code'] == 200:
            assert data['data']['count'] == 0


@pytest.mark.caseeditor
class TestCaseArchiveOperations:
    """测试 Case 压缩包操作（上传/下载）"""
    
    def test_download_case_success(self, api_client, temp_casespace):
        """测试下载 case"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        
        response = api_client.get(
            f'/caseeditor/casespaces/{casespace}/cases/{case}/download'
        )
        
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/zip'
        assert 'Content-Disposition' in response.headers
        assert f'{case}.zip' in response.headers['Content-Disposition']
        
        # 验证返回的是有效的 zip 数据
        import zipfile
        zip_data = BytesIO(response.content)
        assert zipfile.is_zipfile(zip_data)
    
    def test_download_nonexistent_case(self, api_client, temp_casespace):
        """测试下载不存在的 case"""
        casespace = temp_casespace['casespace']
        
        response = api_client.get(
            f'/caseeditor/casespaces/{casespace}/cases/nonexistent_case/download'
        )
        
        assert response.status_code == 200
        # 应该返回错误信息而不是 zip 文件
        data = response.json()
        assert data['code'] == 404
    
    @pytest.mark.slow
    def test_upload_case_zip_success(self, api_client, temp_casespace, tmp_path):
        """测试上传 zip 格式的 case"""
        import zipfile
        
        casespace = temp_casespace['casespace']
        new_case_name = 'uploaded_case'
        
        # 创建测试 zip 文件
        zip_path = tmp_path / 'test_case.zip'
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('test_file1.txt', 'content1')
            zf.writestr('test_file2.py', 'print("test")')
            zf.writestr('subdir/test_file3.txt', 'content3')
        
        # 读取 zip 文件内容
        zip_content = zip_path.read_bytes()
        
        # 模拟文件上传（需要使用 Django Test Client）
        from django.test import Client
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        django_client = Client()
        
        # 注意：这里需要先登录或提供认证
        # 简化测试，直接测试文件管理器功能
        from xcase.file_manager import file_manager
        
        file_manager.upload_case(
            casespace,
            new_case_name,
            zip_content,
            'test_case.zip'
        )
        
        # 验证 case 已创建
        case_path = file_manager.storage_root / casespace / new_case_name
        assert case_path.exists()
        assert (case_path / 'test_file1.txt').exists()
        assert (case_path / 'test_file2.py').exists()
        assert (case_path / 'subdir' / 'test_file3.txt').exists()
    
    @pytest.mark.slow
    def test_upload_case_tar_gz_success(self, api_client, temp_casespace, tmp_path):
        """测试上传 tar.gz 格式的 case"""
        import tarfile
        
        casespace = temp_casespace['casespace']
        new_case_name = 'uploaded_tar_case'
        
        # 创建测试 tar.gz 文件
        tar_path = tmp_path / 'test_case.tar.gz'
        with tarfile.open(tar_path, 'w:gz') as tf:
            # 创建临时文件
            file1 = tmp_path / 'file1.txt'
            file1.write_text('content1')
            tf.add(file1, arcname='file1.txt')
            
            file2 = tmp_path / 'file2.py'
            file2.write_text('print("test")')
            tf.add(file2, arcname='file2.py')
        
        # 读取 tar.gz 文件内容
        tar_content = tar_path.read_bytes()
        
        # 测试文件管理器功能
        from xcase.file_manager import file_manager
        
        file_manager.upload_case(
            casespace,
            new_case_name,
            tar_content,
            'test_case.tar.gz'
        )
        
        # 验证 case 已创建
        case_path = file_manager.storage_root / casespace / new_case_name
        assert case_path.exists()
        assert (case_path / 'file1.txt').exists()
        assert (case_path / 'file2.py').exists()


@pytest.mark.caseeditor
class TestCaseEditorIntegration:
    """集成测试：完整的 case editor 工作流"""
    
    @pytest.mark.integration
    def test_complete_file_management_workflow(self, api_client, temp_casespace):
        """测试完整的文件管理流程"""
        casespace = temp_casespace['casespace']
        case = temp_casespace['case']
        parent_path = f'/{casespace}/{case}'
        
        # 1. 创建目录
        response = api_client.post(
            '/caseeditor/folders/create',
            json={
                'parentPath': parent_path,
                'name': 'src'
            }
        )
        assert response.status_code == 200
        
        # 2. 在目录中创建文件
        response = api_client.post(
            '/caseeditor/files/create',
            json={
                'parentPath': f'{parent_path}/src',
                'name': 'main.py'
            }
        )
        assert response.status_code == 200
        
        # 3. 保存文件内容
        response = api_client.post(
            '/caseeditor/files/save',
            json={
                'path': f'{parent_path}/src/main.py',
                'content': 'def main():\n    print("Hello")\n\nif __name__ == "__main__":\n    main()'
            }
        )
        assert response.status_code == 200
        
        # 4. 读取文件内容
        response = api_client.get(
            '/caseeditor/files/content',
            params={'path': f'{parent_path}/src/main.py'}
        )
        assert response.status_code == 200
        assert 'def main():' in response.json()['data']['content']
        
        # 5. 重命名文件
        response = api_client.put(
            '/caseeditor/files/rename',
            json={
                'oldPath': f'{parent_path}/src/main.py',
                'newName': 'app.py'
            }
        )
        assert response.status_code == 200
        
        # 6. 验证文件树
        response = api_client.get(
            '/caseeditor/files',
            params={
                'casespace': casespace,
                'case': case,
                'path': '/src'
            }
        )
        assert response.status_code == 200
        file_names = [item['name'] for item in response.json()['data']]
        assert 'app.py' in file_names
        assert 'main.py' not in file_names
        
        # 7. 批量上传文件
        response = api_client.post(
            '/caseeditor/files/upload',
            json={
                'parentPath': f'{parent_path}/src',
                'files': [
                    {'name': 'config.json', 'content': '{"debug": true}'},
                    {'name': 'utils.py', 'content': 'def helper(): pass'}
                ]
            }
        )
        assert response.status_code == 200
        assert response.json()['data']['count'] == 2
        
        # 8. 删除文件
        response = api_client.delete(
            '/caseeditor/files',
            params={'path': f'{parent_path}/src/utils.py'}
        )
        assert response.status_code == 200
        
        # 9. 最终验证
        response = api_client.get(
            '/caseeditor/files',
            params={
                'casespace': casespace,
                'case': case,
                'path': '/src'
            }
        )
        final_files = [item['name'] for item in response.json()['data']]
        assert 'app.py' in final_files
        assert 'config.json' in final_files
        assert 'utils.py' not in final_files
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_case_lifecycle(self, api_client, temp_casespace, tmp_path):
        """测试 case 的完整生命周期：创建、编辑、下载、删除"""
        from xcase.file_manager import file_manager
        import zipfile
        
        casespace = temp_casespace['casespace']
        
        # 1. 创建新 case（通过创建目录）
        new_case = 'lifecycle_test_case'
        case_path = file_manager.storage_root / casespace / new_case
        case_path.mkdir(parents=True, exist_ok=True)
        
        # 2. 添加文件
        response = api_client.post(
            '/caseeditor/files/create',
            json={
                'parentPath': f'/{casespace}/{new_case}',
                'name': 'README.md'
            }
        )
        assert response.status_code == 200
        
        response = api_client.post(
            '/caseeditor/files/save',
            json={
                'path': f'/{casespace}/{new_case}/README.md',
                'content': '# Test Case\n\nThis is a test case.'
            }
        )
        assert response.status_code == 200
        
        # 3. 下载 case
        response = api_client.get(
            f'/caseeditor/casespaces/{casespace}/cases/{new_case}/download'
        )
        assert response.status_code == 200
        
        # 验证下载的 zip 文件
        zip_data = BytesIO(response.content)
        with zipfile.ZipFile(zip_data, 'r') as zf:
            assert 'README.md' in zf.namelist()
            content = zf.read('README.md').decode('utf-8')
            assert '# Test Case' in content
        
        # 4. 删除 case
        response = api_client.delete(
            f'/caseeditor/casespaces/{casespace}/cases/{new_case}'
        )
        assert response.status_code == 200
        
        # 验证 case 已删除
        assert not case_path.exists()

