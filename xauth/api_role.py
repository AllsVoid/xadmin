from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest
from ninja import responses #noqa
from http import HTTPStatus
from ninja_extra import Router
from xauth import models
from xutils import utils
from xauth import schemas
from . import auth


router = Router()

@router.get('', auth=auth.XadminPermAuth('system:role:list'))
def list_roles(request: HttpRequest, page: int=1, size: int=10, sort: str='createTime,desc'):
    # 获取搜索参数
    description = request.GET.get("description", "")
    
    # 排序处理
    sort_field, sort_order = sort.split(',')
    sort_field = utils.camel_to_snake(sort_field)
    sort_order = '-' if sort_order == 'desc' else ''
    order_by = f'{sort_order}{sort_field}'
    
    # 构建过滤条件
    filter_query = Q()
    
    # 搜索名称/编码/描述（模糊匹配）
    if description:
        filter_query = filter_query & (
            Q(name__icontains=description) | 
            Q(code__icontains=description) | 
            Q(description__icontains=description)
        )
    
    # 查询角色（先过滤，再排序，最后分页）
    _data = models.SysRole.objects.filter(filter_query).order_by(order_by)
    total = _data.count()
    _page_data = _data[(page-1)*size:page*size]
    data = list()
    for item in _page_data:
        data.append(
            dict(
                id = item.id,
                createUserString = item.create_user,
                createTime = utils.dateformat(item.create_time),
                updateUserString = item.update_user,
                updateTime = item.update_time,
                disabled = False,
                name = item.name,
                code = item.code,
                dataScope = item.data_scope,
                sort = item.sort,
                isSystem = bool(item.is_system),
                description = item.description,
            )
        )
    resp = utils.RespSuccessTempl()
    resp.data = dict(list=data, total=total)
    return resp.as_dict()


@router.post('', auth=auth.XadminPermAuth('system:role:add'))
def add_role(request, role: schemas.SysRoleAdd):
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    data = role.dict()
    menu_ids = data.pop('menu_ids')
    dept_ids = data.pop('dept_ids')
    try:
        with transaction.atomic():
            _role = models.SysRole.objects.create(**data)
            role_id = _role.id
            models.SysRoleDept.set_role_depts(role_id, dept_ids)
            models.SysRoleMenu.set_role_menus(role_id, menu_ids)
    except Exception as e:
        transaction.rollback()
        resp.data = dict(error=str(e))
        resp.code = 400
        resp.msg = '操作失败'
        return resp.as_dict()
    return resp.as_dict()

@router.get('/{id}', auth=auth.XadminPermAuth('system:role:list'))
def get_role(request, id: int):
    data = models.SysRole.get_role_info(id)
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()

@router.put('/{id}', auth=auth.XadminPermAuth('system:role:add'))
def update_role(request, id: int, role: schemas.SysRoleIn):
    resp = utils.RespSuccessTempl()
    menu_ids = role.menu_ids
    dept_ids = role.dept_ids
    role_id = int(role.id)
    exclude = ('id', 'menu_ids', 'dept_ids',
                    'create_time', 'update_time',
                    'create_user', 'update_user',
    )
    try:
        with transaction.atomic():
            _role = models.SysRole.objects.get(id=id)
            for k,v in role.dict().items():
                if k not in exclude:
                    setattr(_role, k, v)
            _role.save()
            models.SysRoleDept.set_role_depts(role_id, dept_ids)
            models.SysRoleMenu.set_role_menus(role_id, menu_ids)
    except Exception as e:
        transaction.rollback()
        resp.data = dict(error=str(e))
        resp.code = 500
        resp.msg = '操作失败'
        return resp.as_dict()
    resp.data = dict()
    return resp.as_dict()

@router.delete('/{id}', auth=auth.XadminPermAuth('system:role:list'))
def delete_role(request, id: int):
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    user_count = models.SysUserRole.objects.filter(
        role_id=id
    ).count()
    if user_count > 0:
        resp.code = HTTPStatus.CONFLICT
        resp.msg = '操作失败, 该角色已经被赋予一些用户，请先删除这些用户或修改这些用户的角色'
    else:
        models.SysRole.objects.filter(
            id=id
        ).delete()
        models.SysRoleDept.objects.filter(
            role_id=id
        ).delete()
        models.SysRoleMenu.objects.filter(
            role_id=id
        ).delete()
    return resp.as_dict()
