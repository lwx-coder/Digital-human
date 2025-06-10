from django.core.management.base import BaseCommand
from apps.informations.models import AnnouncementType

class Command(BaseCommand):
    help = '创建默认的公告类型'

    def handle(self, *args, **options):
        self.stdout.write('开始创建默认公告类型...')
        
        default_types = [
            {
                'name': 'emergency',
                'description': '紧急通知',
                'icon': 'el-icon-warning',
                'color': '#F56C6C'
            },
            {
                'name': 'regular',
                'description': '常规通知',
                'icon': 'el-icon-info',
                'color': '#409EFF'
            },
            {
                'name': 'congestion',
                'description': '拥堵区预警',
                'icon': 'el-icon-warning-outline',
                'color': '#E6A23C'
            },
            {
                'name': 'gate_change',
                'description': '登机口变更',
                'icon': 'el-icon-position',
                'color': '#67C23A'
            }
        ]
        
        for type_data in default_types:
            obj, created = AnnouncementType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建公告类型: {type_data["description"]}'))
            else:
                self.stdout.write(f'公告类型已存在: {type_data["description"]}')
        
        self.stdout.write(self.style.SUCCESS('默认公告类型创建完成!')) 