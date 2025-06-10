from django.core.management.base import BaseCommand
from apps.passenger_management.models import PassengerTag


class Command(BaseCommand):
    help = '初始化默认旅客标签'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化默认旅客标签...')
        
        # 默认旅客标签列表
        default_tags = [
            {
                'name': 'vip',
                'description': 'VIP旅客',
                'color': '#ff9900'
            },
            {
                'name': 'frequent_flyer',
                'description': '常旅客',
                'color': '#67C23A'
            },
            {
                'name': 'new_user',
                'description': '新用户',
                'color': '#409EFF'
            },
            {
                'name': 'need_assistance',
                'description': '需要特殊关注',
                'color': '#F56C6C'
            },
            {
                'name': 'international',
                'description': '国际旅客',
                'color': '#E6A23C'
            },
            {
                'name': 'business',
                'description': '商务旅客',
                'color': '#6366f1'
            }
        ]
        
        # 创建或更新标签
        for tag_data in default_tags:
            tag, created = PassengerTag.objects.get_or_create(
                name=tag_data['name'],
                defaults={
                    'description': tag_data['description'],
                    'color': tag_data['color']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建标签: {tag.name}'))
            else:
                # 更新现有标签的描述和颜色
                tag.description = tag_data['description']
                tag.color = tag_data['color']
                tag.save()
                self.stdout.write(f'更新标签: {tag.name}')
        
        self.stdout.write(self.style.SUCCESS('默认旅客标签初始化完成！')) 