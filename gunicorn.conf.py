# gunicorn.conf.py

bind = '0.0.0.0:9527'  # 绑定到所有接口的8000端口
workers = 3  # 工作进程数
timeout = 120  # 请求超时时间
reload = False  # 当代码变化时自动重新加载

