from django.db import migrations


def create_default_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    default_roles = [
        {'name': 'student', 'description': '学生'},
        {'name': 'teacher', 'description': '教师'},
        {'name': 'admin', 'description': '管理员'},
    ]
    for role_data in default_roles:
        Role.objects.get_or_create(name=role_data['name'], defaults=role_data)


def remove_default_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    Role.objects.filter(name__in=['student', 'teacher', 'admin']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_role_customuser_roles'),
    ]

    operations = [
        migrations.RunPython(create_default_roles, remove_default_roles),
    ] 