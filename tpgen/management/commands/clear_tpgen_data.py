"""
清理 TPGen 示例数据 Management Command
"""
from django.core.management.base import BaseCommand
from tpgen import models


class Command(BaseCommand):
    help = '清理 TPGen 示例数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='删除所有 TPGen 数据（包括非示例数据）',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='确认删除操作',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING("⚠️  警告: 此操作将删除数据！"))
            self.stdout.write("如果确定要删除，请添加 --confirm 参数")
            self.stdout.write("\n示例:")
            self.stdout.write("  python manage.py clear_tpgen_data --confirm")
            return
        
        if options['all']:
            self.clear_all_data()
        else:
            self.clear_sample_data()

    def clear_sample_data(self):
        """清理示例数据"""
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.WARNING("清理 TPGen 示例数据"))
        self.stdout.write("=" * 80)
        
        try:
            # 删除示例 SutDevice
            self.stdout.write("\n🗑️  删除示例 SutDevice...")
            sample_devices = [
                "test-gpu-001", "test-gpu-002", "test-gpu-003",
                "test-gpu-004", "test-gpu-005"
            ]
            deleted_devices = models.SutDevice.objects.filter(
                hostname__in=sample_devices
            ).delete()
            self.stdout.write(f"  ✓ 删除了 {deleted_devices[0]} 条 SutDevice 记录")
            
            # 删除示例 TestType 及相关数据
            self.stdout.write("\n🗑️  删除示例 TestType...")
            sample_types = ["功能测试", "性能测试", "接口测试"]
            deleted_types = models.TestType.objects.filter(
                type_name__in=sample_types
            ).delete()
            self.stdout.write(f"  ✓ 删除了 {deleted_types[0]} 条 TestType 记录（包括相关的 TestComponent 和 TestCase）")
            
            # 删除示例 OsConfig 及相关数据
            self.stdout.write("\n🗑️  删除示例 OsConfig...")
            sample_os = [
                ("Ubuntu", "22.04"),
                ("Ubuntu", "20.04"),
                ("CentOS", "8"),
                ("RedHat", "9"),
            ]
            deleted_os = 0
            for os_family, version in sample_os:
                count = models.OsConfig.objects.filter(
                    os_family=os_family,
                    version=version
                ).delete()[0]
                deleted_os += count
            self.stdout.write(f"  ✓ 删除了 {deleted_os} 条 OsConfig 记录（包括相关的内核版本）")
            
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write(self.style.SUCCESS("✅ 示例数据清理完成！"))
            self.stdout.write("=" * 80)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ 清理数据时出错: {e}"))
            import traceback
            traceback.print_exc()

    def clear_all_data(self):
        """清理所有数据"""
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.ERROR("清理所有 TPGen 数据"))
        self.stdout.write("=" * 80)
        
        try:
            # 删除所有 TestCase
            count = models.TestCase.objects.all().delete()[0]
            self.stdout.write(f"  ✓ 删除了 {count} 条 TestCase 记录")
            
            # 删除所有 TestComponent
            count = models.TestComponent.objects.all().delete()[0]
            self.stdout.write(f"  ✓ 删除了 {count} 条 TestComponent 记录")
            
            # 删除所有 TestType
            count = models.TestType.objects.all().delete()[0]
            self.stdout.write(f"  ✓ 删除了 {count} 条 TestType 记录")
            
            # 删除所有 OsSupportedKernel
            count = models.OsSupportedKernel.objects.all().delete()[0]
            self.stdout.write(f"  ✓ 删除了 {count} 条 OsSupportedKernel 记录")
            
            # 删除所有 OsConfig
            count = models.OsConfig.objects.all().delete()[0]
            self.stdout.write(f"  ✓ 删除了 {count} 条 OsConfig 记录")
            
            # 删除所有 SutDevice
            count = models.SutDevice.objects.all().delete()[0]
            self.stdout.write(f"  ✓ 删除了 {count} 条 SutDevice 记录")
            
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write(self.style.SUCCESS("✅ 所有数据清理完成！"))
            self.stdout.write("=" * 80)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ 清理数据时出错: {e}"))
            import traceback
            traceback.print_exc()



