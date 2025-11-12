"""
测试计划相关模型
"""
from django.db import models
from xadmin_db.models import BaseModel


class TestPlan(BaseModel):
    """测试计划模型"""
    
    class Meta:
        db_table = "sys_test_plan"
        verbose_name = "测试计划"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]
    
    # 文件信息
    file_name = models.CharField(max_length=255, verbose_name="文件名")
    file_path = models.CharField(max_length=500, verbose_name="文件路径", null=True, blank=True)
    file_content = models.TextField(verbose_name="文件内容")
    
    # 测试计划基本信息
    plan_name = models.CharField(max_length=255, verbose_name="计划名称", null=True, blank=True)
    test_type = models.CharField(max_length=100, verbose_name="测试类型", null=True, blank=True)
    cpu = models.CharField(max_length=100, verbose_name="CPU型号", null=True, blank=True)
    gpu = models.CharField(max_length=100, verbose_name="GPU型号", null=True, blank=True)
    
    # 分析结果（JSON格式存储）
    analysis_result = models.JSONField(verbose_name="分析结果", null=True, blank=True)
    validation_status = models.CharField(
        max_length=20, 
        verbose_name="验证状态",
        choices=[
            ('valid', '有效'),
            ('warning', '警告'),
            ('error', '错误')
        ],
        default='valid'
    )
    
    # 兼容性信息
    compatible_machines = models.JSONField(verbose_name="兼容机器列表", null=True, blank=True)
    incompatible_machines = models.JSONField(verbose_name="不兼容机器列表", null=True, blank=True)
    
    # 警告和错误信息
    warnings = models.JSONField(verbose_name="警告信息", null=True, blank=True)
    errors = models.JSONField(verbose_name="错误信息", null=True, blank=True)
    
    def __str__(self):
        return f"{self.plan_name or self.file_name} - {self.test_type or 'Unknown'}"

