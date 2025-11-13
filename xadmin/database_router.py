"""
数据库路由器 - 将 tpgen 相关应用路由到 tpdb 数据库
其他应用使用 xadmin 数据库
"""


class UnifiedTpdbRouter:
    """
    统一数据库路由器：将 tpgen 相关应用的所有数据库操作路由到 tpdb 数据库
    包括：tpgen, test_plan, xadmin_tpgen
    """

    # 使用 tpdb 数据库的应用列表
    tpdb_apps = ["tpgen", "test_plan", "xadmin_tpgen"]
    tpdb_db = "tpdb"
    default_db = "default"

    def db_for_read(self, model, **hints):
        """读操作路由"""
        if model._meta.app_label in self.tpdb_apps:
            return self.tpdb_db
        return None

    def db_for_write(self, model, **hints):
        """写操作路由"""
        if model._meta.app_label in self.tpdb_apps:
            return self.tpdb_db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        允许关系：同一数据库内的对象才能建立关系
        """
        obj1_in_tpdb = obj1._meta.app_label in self.tpdb_apps
        obj2_in_tpdb = obj2._meta.app_label in self.tpdb_apps
        
        # 如果两个对象都在 tpdb 应用中，允许关系
        if obj1_in_tpdb and obj2_in_tpdb:
            return True
        # 如果一个在 tpdb，一个不在，禁止关系
        if obj1_in_tpdb or obj2_in_tpdb:
            return False
        # 其他情况由 Django 默认处理
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        迁移权限：tpdb 应用只能迁移到 tpdb，其他应用只能迁移到 default
        """
        if app_label in self.tpdb_apps:
            # tpdb 应用只能迁移到 tpdb
            return db == self.tpdb_db
        # 其他应用只能迁移到 default
        return db == self.default_db


# 向后兼容：保留原有的 TpgenDatabaseRouter
class TpgenDatabaseRouter(UnifiedTpdbRouter):
    """
    向后兼容的路由器（已废弃，建议使用 UnifiedTpdbRouter）
    """
    pass

