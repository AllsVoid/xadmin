class TpdbRouter:
    """将 test_plan app 的模型路由到 tpdb 数据库"""
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'test_plan':
            return 'tpdb'
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'test_plan':
            return 'tpdb'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'test_plan':
            return db == 'tpdb'
        return None