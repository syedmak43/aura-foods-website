import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aurafoods.settings')
django.setup()
from shop.models import Bundle

bundles_data = [
    ('One Pinch Bundle', 'Signature spice blend', 600, 1000, 40),
    ('Kitchen Essentials Bundle', 'Premium spice collection', 750, 1200, 38),
    ('Khalis Zaiqa Bundle', 'Traditional spice selection', 550, 900, 39),
    ('Zaiqay Ki Pehchan Bundle', 'Aura Foods special combo', 850, 1400, 39),
]
for name, items, price, old_price, save in bundles_data:
    Bundle.objects.create(name=name, items=items, price=price, old_price=old_price, save_percent=save)
    print(f'Created: {name}')
print('Done')
