from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.auth.models import Permission, Role, UserRole

User = get_user_model()


class Command(BaseCommand):
    help = '初始化RBAC权限和角色数据'
    
    def handle(self, *args, **options):
        self.stdout.write('开始初始化RBAC数据...')
        
        # 创建基本权限
        permissions = [
            # 用户管理权限
            {'name': '查看用户', 'codename': 'view_user', 'description': '查看用户信息'},
            {'name': '添加用户', 'codename': 'add_user', 'description': '添加新用户'},
            {'name': '编辑用户', 'codename': 'change_user', 'description': '编辑用户信息'},
            {'name': '删除用户', 'codename': 'delete_user', 'description': '删除用户'},
            
            # 角色管理权限
            {'name': '查看角色', 'codename': 'view_role', 'description': '查看角色信息'},
            {'name': '添加角色', 'codename': 'add_role', 'description': '添加新角色'},
            {'name': '编辑角色', 'codename': 'change_role', 'description': '编辑角色信息'},
            {'name': '删除角色', 'codename': 'delete_role', 'description': '删除角色'},
            
            # 权限管理权限
            {'name': '查看权限', 'codename': 'view_permission', 'description': '查看权限信息'},
            {'name': '添加权限', 'codename': 'add_permission', 'description': '添加新权限'},
            {'name': '编辑权限', 'codename': 'change_permission', 'description': '编辑权限信息'},
            {'name': '删除权限', 'codename': 'delete_permission', 'description': '删除权限'},
            
            # 用户角色管理权限
            {'name': '分配角色', 'codename': 'assign_role', 'description': '为用户分配角色'},
            {'name': '移除角色', 'codename': 'remove_role', 'description': '移除用户的角色'},
        ]
        
        created_permissions = []
        for perm_data in permissions:
            perm, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data['description']
                }
            )
            if created:
                created_permissions.append(perm)
                self.stdout.write(f'创建权限: {perm.name}')
            else:
                self.stdout.write(f'权限已存在: {perm.name}')
        
        # 创建基本角色
        admin_role, created = Role.objects.get_or_create(
            code='admin',
            defaults={
                'name': '管理员',
                'description': '系统管理员，拥有所有权限'
            }
        )
        if created:
            self.stdout.write(f'创建角色: {admin_role.name}')
        else:
            self.stdout.write(f'角色已存在: {admin_role.name}')
        
        # 为管理员角色分配所有权限
        admin_role.permissions.set(Permission.objects.all())
        self.stdout.write(f'为角色 {admin_role.name} 分配所有权限')
        
        # 创建普通用户角色
        user_role, created = Role.objects.get_or_create(
            code='user',
            defaults={
                'name': '普通用户',
                'description': '普通用户，拥有基本查看权限'
            }
        )
        if created:
            self.stdout.write(f'创建角色: {user_role.name}')
        else:
            self.stdout.write(f'角色已存在: {user_role.name}')
        
        # 为普通用户角色分配基本查看权限
        view_permissions = Permission.objects.filter(codename__startswith='view_')
        user_role.permissions.set(view_permissions)
        self.stdout.write(f'为角色 {user_role.name} 分配基本查看权限')
        
        # 为超级用户分配管理员角色
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            if not UserRole.objects.filter(user=user, role=admin_role).exists():
                UserRole.objects.create(user=user, role=admin_role)
                self.stdout.write(f'为超级用户 {user.username} 分配管理员角色')
        
        self.stdout.write(self.style.SUCCESS('RBAC数据初始化完成!')) 