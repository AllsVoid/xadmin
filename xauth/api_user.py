from base64 import b64decode, b64encode

from django.conf import settings
from django.db.models import OuterRef, Q, Subquery
from django.http import HttpRequest
from loguru import logger
from ninja import File
from ninja.files import UploadedFile
from ninja_extra import Router

from xauth import models, schemas
from xutils import utils

from . import auth

router = Router()


@router.post("/avatar")
def upload_avatar(request, file: UploadedFile = File(..., alias="avatarFile")):
    avatar = b64encode(file.read()).decode()
    avatar = f"data:image/png;base64,{avatar}"
    request.user.avatar = avatar
    request.user.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict(avatar=avatar)
    return resp.as_dict()


@router.get("/avatar")
def get_avatar(request):
    resp = utils.RespSuccessTempl()
    resp.data = dict(avatar=request.user.avatar)
    return resp.as_dict()


@router.get("/info")
def get_user_info(request: HttpRequest):
    user: models.SysUser = request.user
    dept = models.SysDept.objects.get(id=user.dept_id)
    role_ids = models.SysUserRole.objects.filter(user_id=user.id).values_list(
        "role_id", flat=True
    )
    role_names = models.SysRole.objects.filter(id__in=role_ids).values_list(
        "code", flat=True
    )
    menu_ids = models.SysRoleMenu.objects.filter(
        role_id__in=list(role_ids)
    ).values_list("menu_id", flat=True)
    # 系统用户拥有所有权限
    if user.is_system == 1:
        permissions = ("*:*:*",)
    else:
        permissions = models.SysMenu.objects.filter(
            Q(id__in=menu_ids) & Q(type=3)
        ).exclude(permission__isnull=True).exclude(permission='').values_list("permission", flat=True)
    data = dict(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        gender=user.gender,
        email=user.email or "",
        phone=user.phone or "",
        avatar=user.avatar or "",
        description=user.description or "",
        deptId=user.dept_id,
        deptName=dept.name,
        permissions=list(permissions),
        roles=list(role_names),
    )
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@router.get("/list", auth=auth.XadminPermAuth("system:user:list"))
def user_list(request: HttpRequest):
    # 获取查询参数
    description = request.GET.get("description", "")  # 搜索关键词（用户名/昵称/描述）
    status = request.GET.get("status", "")
    create_time = request.GET.getlist("createTime")  # 创建时间范围（数组）
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 10))

    result = dict()
    _list = []
    
    # 获取部门ID，如果没有传递则使用根部门ID
    dept_id_param = request.GET.get("deptId")
    if dept_id_param is None or dept_id_param == '':
        # 如果没有传递部门ID，查询根部门（parent_id=0）
        root_dept = models.SysDept.objects.filter(parent_id=0).first()
        dept_id = root_dept.id if root_dept else 1  # 默认为1以防万一
    else:
        dept_id = int(dept_id_param)
    
    dept_ids = models.SysDept.objects.filter(ancestors__contains=str(dept_id)).values(
        "id"
    )
    dept_name_subquery = models.SysDept.objects.filter(id=OuterRef("dept_id")).values(
        "name"
    )[:1]

    # 构建过滤条件
    filter = Q(dept_id__in=dept_ids) | Q(dept_id=dept_id)
    
    # 搜索用户名/昵称/描述（模糊匹配）
    if description:
        filter = filter & (
            Q(username__icontains=description) | 
            Q(nickname__icontains=description) | 
            Q(description__icontains=description)
        )
    
    # 按状态过滤
    if status:
        filter = filter & Q(status=int(status))
    
    # 按创建时间范围过滤
    if create_time and len(create_time) == 2:
        start_time = create_time[0]
        end_time = create_time[1]
        if start_time:
            filter = filter & Q(create_time__gte=start_time)
        if end_time:
            filter = filter & Q(create_time__lte=end_time)
    
    # 查询用户（先获取总数，再分页）
    all_users = models.SysUser.objects.filter(filter)
    total = all_users.count()  # 过滤后的总数
    
    users = all_users.annotate(
        dept_name=Subquery(dept_name_subquery)
    )[(page - 1) * size : page * size]
    for user in users:
        # 系统用户不需要分配角色，直接显示"系统管理员"
        if user.is_system == 1:
            role_ids = []
            role_names = ["系统管理员"]
        else:
            roles = models.SysUserRole.objects.filter(user_id=user.id).values_list(
                "role_id", flat=True
            )
            role_names = models.SysRole.objects.filter(id__in=roles).values_list(
                "name", flat=True
            )
            role_ids = list(roles)
            role_names = list(role_names)
        
        create_user = models.SysUser.objects.get(id=user.create_user)
        _list.append(
            dict(
                id=str(user.id),
                createUserString=create_user.username,
                createTime=utils.dateformat(user.create_time),
                disabled=False,
                updateUserString=user.update_user,
                updateTime=user.update_time,
                username=user.username,
                nickname=user.nickname,
                gender=user.gender,
                avatar=user.avatar or "",
                email=user.email,
                phone=user.phone,
                status=user.status,
                isSystem=user.is_system,
                description=user.description,
                deptId=user.dept_id,
                deptName=user.dept_name,
                roleIds=role_ids,
                roleNames=role_names,
            )
        )

    result["total"] = total  # 使用过滤后的总数
    result["list"] = _list
    resp = utils.RespSuccessTempl()
    resp.data = result
    return resp.as_dict()


@router.post("", auth=auth.XadminPermAuth("system:user:add"))
def add_user(request, user_in: schemas.SysUserAdd):
    data = user_in.dict()
    role_ids = data.pop("role_ids")
    user = models.SysUser.objects.create(**data)
    user.create_user = request.user.id
    password = b64decode(user_in.password)
    logger.info(f"User created with password: {password.decode()}")
    user.set_password(password)
    user.save()
    models.SysUserRole.set_user_roles(user.id, role_ids)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.get("/{id}", auth=auth.XadminPermAuth("system:user:list"))
def get_user(request, id: int):
    _user = models.SysUser.get_user_and_roles_by_id(id)
    resp = utils.RespSuccessTempl()
    resp.data = _user
    return resp.as_dict()


@router.delete("/{id}", auth=auth.XadminPermAuth("system:user:delete"))
def delete_user(request, id: int):
    user = models.SysUser.objects.get(id=id)
    user.delete()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.put("/{id}", auth=auth.XadminPermAuth("system:user:update"))
def update_user(request, id: int, user_in: schemas.SysUserUpdate):
    exclude_fields = [
        "role_ids",
    ]
    _user = models.SysUser.objects.get(id=id)
    for k, v in user_in.dict().items():
        if k not in exclude_fields:
            setattr(_user, k, v)
    _user.save()
    models.SysUserRole.set_user_roles(id, user_in.role_ids)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.patch("/{id}/password", auth=auth.XadminPermAuth("system:user:resetPwd"))
def reset_user_password(request, id: int, password: schemas.ResetUserPassword):
    user = models.SysUser.objects.get(id=id)
    user.set_password(b64decode(password.new_password))
    user.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.patch("/{id}/role")
def reset_user_roles(request, id: int, role_ids: schemas.SetUserRoles):
    models.SysUserRole.set_user_roles(id, role_ids.role_ids)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.patch("/basic/info")
def update_user_profile(request, profile: schemas.SysUserProfile):
    user = models.SysUser.objects.get(id=request.user.id)
    for k, v in profile.dict().items():
        setattr(user, k, v)
    user.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.patch("/password")
def update_user_password(request, password_data: schemas.UpdateUserPassword):
    """用户修改自己的密码（需要验证旧密码）"""
    from django.utils import timezone
    
    user = request.user
    
    # 验证旧密码
    old_password = b64decode(password_data.old_password)
    if not user.check_password(old_password):
        resp = utils.RespFailedTempl()
        resp.msg = "当前密码不正确"
        resp.code = 400
        return resp.as_dict()
    
    # 验证新密码不能与旧密码相同
    new_password = b64decode(password_data.new_password)
    if old_password == new_password:
        resp = utils.RespFailedTempl()
        resp.msg = "新密码不能与当前密码相同"
        resp.code = 400
        return resp.as_dict()
    
    # 设置新密码
    user.set_password(new_password)
    user.pwd_reset_time = timezone.now()
    user.save()
    
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    resp.msg = "密码修改成功"
    return resp.as_dict()
