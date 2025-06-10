from django.core.management.base import BaseCommand
from apps.items_management.models import ItemCategory


class Command(BaseCommand):
    help = '初始化默认物品类别'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化默认物品类别...')
        
        # 调用模型类方法创建默认类别
        ItemCategory.get_or_create_default_categories()
        
        self.stdout.write(self.style.SUCCESS('默认物品类别初始化完成！')) 