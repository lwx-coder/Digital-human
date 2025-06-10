from django.db import migrations


def update_default_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    
    # 删除原有角色
    Role.objects.filter(name__in=['student', 'teacher']).delete()
    
    # 创建或更新默认角色
    default_roles = [
        {'name': 'passenger', 'description': '旅客'},
        {'name': 'admin', 'description': '管理员'},
    ]
    for role_data in default_roles:
        Role.objects.get_or_create(name=role_data['name'], defaults=role_data)


def revert_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    
    # 删除新角色
    Role.objects.filter(name__in=['passenger']).delete()
    
    # 恢复原有角色
    old_roles = [
        {'name': 'student', 'description': '学生'},
        {'name': 'teacher', 'description': '教师'},
    ]
    for role_data in old_roles:
        Role.objects.get_or_create(name=role_data['name'], defaults=role_data)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_create_default_roles'),
    ]

    operations = [
        migrations.RunPython(update_default_roles, revert_roles),
    ] 