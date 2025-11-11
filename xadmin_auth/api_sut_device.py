from ninja_extra import Router
from xadmin_utils import utils
from test_plan.models import SutDevice
from typing import List, Dict

router = Router()


@router.get('/gpu-options')
def get_gpu_options(request):
    """
    获取 GPU 选项列表（从 sut_devices.asic_name 列）
    
    返回格式：
    {
        "code": 200,
        "msg": "success",
        "data": [
            {"label": "Navi 31 GFX1100", "value": "Navi 31 GFX1100"},
            {"label": "Navi 21", "value": "Navi 21"},
            ...
        ]
    }
    """
    try:
        # 获取所有唯一的 asic_name，排除空值
        asic_names = SutDevice.objects.filter(
            asic_name__isnull=False
        ).exclude(
            asic_name=''
        ).values_list('asic_name', flat=True).distinct().order_by('asic_name')
        
        # 转换为前端需要的格式
        gpu_options = [
            {'label': name, 'value': name} 
            for name in asic_names
        ]
        
        resp = utils.RespSuccessTempl()
        resp.data = gpu_options
        return resp.as_dict()
        
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'查询 GPU 选项失败: {str(e)}'
        return resp.as_dict()


@router.get('/devices')
def get_devices(request):
    """
    获取设备列表（支持按 asic_name、gpu_series、gpu_model 筛选）
    
    参数：
    - asic_name: ASIC 名称筛选
    - gpu_series: GPU 系列筛选
    - gpu_model: GPU 型号筛选
    - hostname: 主机名搜索
    """
    try:
        # 获取查询参数
        asic_name = request.GET.get('asic_name', '')
        gpu_series = request.GET.get('gpu_series', '')
        gpu_model = request.GET.get('gpu_model', '')
        hostname = request.GET.get('hostname', '')
        
        # 构建查询
        query = SutDevice.objects.all()
        
        if asic_name:
            query = query.filter(asic_name=asic_name)
        if gpu_series:
            query = query.filter(gpu_series__icontains=gpu_series)
        if gpu_model:
            query = query.filter(gpu_model__icontains=gpu_model)
        if hostname:
            query = query.filter(hostname__icontains=hostname)
        
        # 执行查询
        devices = query.values(
            'id', 'hostname', 'asic_name', 'ip_address', 
            'device_id', 'rev_id', 'gpu_series', 'gpu_model'
        )
        
        resp = utils.RespSuccessTempl()
        resp.data = list(devices)
        return resp.as_dict()
        
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'查询设备失败: {str(e)}'
        return resp.as_dict()


@router.get('/gpu-series-options')
def get_gpu_series_options(request):
    """获取 GPU 系列选项（从 gpu_series 列）"""
    try:
        gpu_series_list = SutDevice.objects.filter(
            gpu_series__isnull=False
        ).exclude(
            gpu_series=''
        ).values_list('gpu_series', flat=True).distinct().order_by('gpu_series')
        
        options = [{'label': series, 'value': series} for series in gpu_series_list]
        
        resp = utils.RespSuccessTempl()
        resp.data = options
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'查询失败: {str(e)}'
        return resp.as_dict()


@router.get('/gpu-model-options')
def get_gpu_model_options(request):
    """获取 GPU 型号选项（从 gpu_model 列）"""
    try:
        gpu_model_list = SutDevice.objects.filter(
            gpu_model__isnull=False
        ).exclude(
            gpu_model=''
        ).values_list('gpu_model', flat=True).distinct().order_by('gpu_model')
        
        options = [{'label': model, 'value': model} for model in gpu_model_list]
        
        resp = utils.RespSuccessTempl()
        resp.data = options
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'查询失败: {str(e)}'
        return resp.as_dict()