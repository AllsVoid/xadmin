from django.db import models

class SutDevice(models.Model):
    """SUT 测试设备模型 - 映射 tpdb.public.sut_devices 表"""
    
    id = models.BigAutoField(primary_key=True)  # BIGSERIAL
    hostname = models.CharField(max_length=255, unique=True, verbose_name='设备主机名')
    asic_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='ASIC名称')  # 关键字段
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    device_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='设备ID')
    rev_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='版本ID')
    gpu_series = models.CharField(max_length=100, null=True, blank=True, verbose_name='GPU系列')
    gpu_model = models.CharField(max_length=100, null=True, blank=True, verbose_name='GPU型号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'sut_devices'
        managed = False  # 表已存在，不由 Django 管理
        verbose_name = 'SUT测试设备'
        verbose_name_plural = 'SUT测试设备列表'
        ordering = ['hostname']
    
    def __str__(self):
        return self.hostname