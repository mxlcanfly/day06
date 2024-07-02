#伪造当django启动，只有在启动之后，才能进行orm的写入(离线脚本)
import sys
import os
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'day06.settings')
django.setup()


from web import models
from utils.encrypt import md5

#用户要先创建级别

# level_object = models.Level.objects.create(title='VIP',precent=90)

models.Customer.objects.create(
    username='xinchen',
    password=md5('xinchen'),
    mobile='13333355555',
    level_id=1,
    creator_id=1
)
#
# for i in range(1, 302):
#     models.Customer.objects.create(
#         username='xinchen-{}'.format(i),
#         password=md5('xinchen-{}').format(),
#         mobile='19999999999',
#         level_id=4,
#         creator_id=1
#     )

# models.PricePolicy.objects.create(
#     count=1000,
#     price=8
# )