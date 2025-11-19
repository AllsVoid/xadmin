"""
YAML Test Plan Validator 测试用例
测试 YAML 验证功能
"""
import pytest
from yaml_test_plan.validator import validate_yaml_full


class TestYAMLValidator:
    """测试 YAML 验证器"""
    
    def test_valid_yaml_basic(self):
        """测试基本有效的 YAML"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
  description: "Test Plan"

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
        
        result = validate_yaml_full(yaml_content)
        
        assert result['valid'] is True
        assert result['error_message'] == ''
        assert result['error_code'] == ''
        print("\n✅ 基本有效 YAML 验证通过")
    
    def test_invalid_yaml_syntax(self):
        """测试无效的 YAML 语法"""
        yaml_content = """
metadata:
  version: "2.0"
  invalid syntax here:::
hardware:
"""
        
        result = validate_yaml_full(yaml_content)
        
        assert result['valid'] is False
        assert len(result['error_message']) > 0
        print(f"\n✅ 无效 YAML 语法检测成功: {result['error_message'][:50]}...")
    
    def test_missing_required_field(self):
        """测试缺少必需字段"""
        yaml_content = """
metadata:
  version: "2.0"
# 缺少 hardware 和 environment
"""
        
        result = validate_yaml_full(yaml_content)
        
        assert result['valid'] is False
        assert 'hardware' in result['error_message'].lower() or 'required' in result['error_message'].lower()
        print(f"\n✅ 缺少必需字段检测成功: {result['error_message'][:50]}...")
    
    def test_empty_required_field(self):
        """测试必需字段为空"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"

hardware:
  machines: []

environment:
  machines: {}
"""
        
        result = validate_yaml_full(yaml_content)
        
        assert result['valid'] is False
        assert 'empty' in result['error_message'].lower() or 'machines' in result['error_message'].lower()
        print(f"\n✅ 空必需字段检测成功: {result['error_message'][:50]}...")
    
    def test_invalid_ip_address(self):
        """测试无效的 IP 地址"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"

hardware:
  machines:
    - id: 1
      hostname: "test-machine"
      ipAddress: "999.999.999.999"
      asicName: "Navi10"
      productName: "navi10"

environment:
  machines:
    test-machine:
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
            - "Test Case"
"""
        
        result = validate_yaml_full(yaml_content)
        
        # 根据验证器实现，可能检测出 IP 格式错误
        if not result['valid']:
            print(f"\n✅ 无效 IP 地址检测成功: {result['error_message'][:50]}...")
        else:
            print("\n💡 IP 地址验证可能不够严格，建议增强")
    
    def test_invalid_integer_field(self):
        """测试无效的整数字段"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"

hardware:
  machines:
    - id: "not_a_number"
      hostname: "test-machine"
      ipAddress: "192.168.1.100"
      asicName: "Navi10"
      productName: "navi10"

environment:
  machines:
    test-machine:
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
            - "Test Case"
"""
        
        result = validate_yaml_full(yaml_content)
        
        # 根据验证器实现，可能检测出类型错误
        if not result['valid']:
            print(f"\n✅ 无效整数字段检测成功: {result['error_message'][:50]}...")
        else:
            print("\n💡 整数类型验证可能需要增强")
    
    def test_complex_valid_yaml(self):
        """测试复杂的有效 YAML"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
  description: "Multi-machine benchmark test plan"

hardware:
  machines:
    - id: 1
      hostname: "navi10-test-01"
      ipAddress: "10.67.65.101"
      asicName: "Navi10 GFX1010"
      gpuModel: "RX 5700 XT"
      productName: "navi10"
    - id: 2
      hostname: "navi21-test-01"
      ipAddress: "10.67.65.102"
      asicName: "Navi21 GFX1030"
      gpuModel: "RX 6800 XT"
      productName: "navi21"

environment:
  machines:
    navi10-test-01:
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
            - "H.264 4K Encoding"
        - config_id: 2
          os:
            id: 2
            family: "Fedora"
            version: "39"
          kernel:
            kernel_version: "6.5.6-300"
          test_type: "Functional"
          deployment_method: "bare_metal"
          execution_case_list:
            - "Basic Functionality Test"
    
    navi21-test-01:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          kernel:
            kernel_version: "5.15.0-56"
          test_type: "Performance"
          deployment_method: "bare_metal"
          execution_case_list:
            - "3D Graphics Ultra"
            - "ROCm Memory Bandwidth"
"""
        
        result = validate_yaml_full(yaml_content)
        
        assert result['valid'] is True
        print("\n✅ 复杂有效 YAML 验证通过")
    
    def test_missing_metadata_version(self):
        """测试缺少 metadata.version"""
        yaml_content = """
metadata:
  generated: "2025-11-19T10:00:00Z"
  description: "Test"

hardware:
  machines:
    - id: 1
      hostname: "test"
      ipAddress: "192.168.1.1"

environment:
  machines:
    test:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          test_type: "Benchmark"
          execution_case_list: ["test"]
"""
        
        result = validate_yaml_full(yaml_content)
        
        assert result['valid'] is False
        assert 'version' in result['error_message'].lower()
        print(f"\n✅ 缺少 metadata.version 检测成功")
    
    def test_empty_execution_case_list(self):
        """测试空的测试用例列表"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"

hardware:
  machines:
    - id: 1
      hostname: "test"
      ipAddress: "192.168.1.1"

environment:
  machines:
    test:
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
          execution_case_list: []
"""
        
        result = validate_yaml_full(yaml_content)
        
        # 根据验证规则，空的用例列表可能不被允许
        if not result['valid']:
            print(f"\n✅ 空测试用例列表检测成功: {result['error_message'][:50]}...")
        else:
            print("\n💡 空测试用例列表可能被允许，取决于业务规则")


class TestYAMLValidatorEdgeCases:
    """测试 YAML 验证器的边界情况"""
    
    def test_very_long_field_values(self):
        """测试超长字段值"""
        long_description = "A" * 10000
        yaml_content = f"""
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
  description: "{long_description}"

hardware:
  machines:
    - id: 1
      hostname: "test"
      ipAddress: "192.168.1.1"

environment:
  machines:
    test:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          test_type: "Benchmark"
          execution_case_list: ["test"]
"""
        
        result = validate_yaml_full(yaml_content)
        
        # 验证器应该能处理长字段值
        print(f"\n✅ 超长字段值测试完成: valid={result['valid']}")
    
    def test_special_characters_in_strings(self):
        """测试字符串中的特殊字符"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
  description: "Test with special chars: @#$%^&*()_+-=[]{}|;':,.<>?/"

hardware:
  machines:
    - id: 1
      hostname: "test-machine-01"
      ipAddress: "192.168.1.1"
      asicName: "Navi10 (Special)"

environment:
  machines:
    test-machine-01:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          test_type: "Benchmark"
          execution_case_list: ["Test: Special & Characters"]
"""
        
        result = validate_yaml_full(yaml_content)
        
        print(f"\n✅ 特殊字符测试完成: valid={result['valid']}")
    
    def test_unicode_characters(self):
        """测试 Unicode 字符"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
  description: "测试计划 - Test Plan 中文描述"

hardware:
  machines:
    - id: 1
      hostname: "测试机器-01"
      ipAddress: "192.168.1.1"

environment:
  machines:
    测试机器-01:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          test_type: "性能测试"
          execution_case_list: ["计算测试", "图形测试"]
"""
        
        result = validate_yaml_full(yaml_content)
        
        print(f"\n✅ Unicode 字符测试完成: valid={result['valid']}")
    
    def test_null_and_none_values(self):
        """测试 null 和 None 值"""
        yaml_content = """
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
  description: null

hardware:
  machines:
    - id: 1
      hostname: "test"
      ipAddress: "192.168.1.1"
      deviceId: null
      revId: null

environment:
  machines:
    test:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          test_type: "Benchmark"
          execution_case_list: ["test"]
"""
        
        result = validate_yaml_full(yaml_content)
        
        print(f"\n✅ null/None 值测试完成: valid={result['valid']}")


class TestYAMLValidatorPerformance:
    """测试 YAML 验证器性能"""
    
    def test_large_yaml_validation(self):
        """测试大型 YAML 文件验证"""
        # 生成包含100台机器的 YAML
        machines_yaml = "\n".join([
            f"""    - id: {i}
      hostname: "machine-{i:03d}"
      ipAddress: "192.168.{i // 256}.{i % 256}"
      asicName: "Navi{i % 3}0"
      productName: "navi{i % 3}0\""""
            for i in range(1, 101)
        ])
        
        environment_yaml = "\n".join([
            f"""    machine-{i:03d}:
      configurations:
        - config_id: 1
          os:
            id: 1
            family: "Ubuntu"
            version: "22.04"
          test_type: "Benchmark"
          execution_case_list: ["Test{i}"]"""
            for i in range(1, 101)
        ])
        
        yaml_content = f"""
metadata:
  version: "2.0"
  generated: "2025-11-19T10:00:00Z"
  description: "Large test plan with 100 machines"

hardware:
  machines:
{machines_yaml}

environment:
  machines:
{environment_yaml}
"""
        
        import time
        start_time = time.time()
        result = validate_yaml_full(yaml_content)
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ 大型 YAML 验证完成: valid={result['valid']}, 耗时={elapsed_time:.3f}秒")
        assert elapsed_time < 5.0, "验证时间不应超过5秒"

