from django.core.management.base import BaseCommand
from staking_app.models import StackingPool, PoolConditions


class Command(BaseCommand):
    help = 'Create example StackingPool and PoolConditions objects'

    def handle(self, *args, **options):
        conditions1, conditions1_created = PoolConditions.objects.get_or_create(min_amount=100, max_amount=500)
        if conditions1 and conditions1_created:
            self.stdout.write(self.style.SUCCESS(f"Created example PoolConditions: ({conditions1})"))
        elif conditions1 and not conditions1_created:
            self.stdout.write(self.style.WARNING(f"Already exists example PoolConditions: ({conditions1})"))

        conditions2, conditions2_created = PoolConditions.objects.get_or_create(min_amount=200, max_amount=600)
        if conditions2 and conditions2_created:
            self.stdout.write(self.style.SUCCESS(f"Created example PoolConditions: ({conditions2})"))
        elif conditions2 and not conditions2_created:
            self.stdout.write(self.style.WARNING(f"Already exists example PoolConditions: ({conditions2})"))

        pool1, pool1_created = StackingPool.objects.get_or_create(name="Example Pool 1", conditions=conditions1)
        if pool1 and pool1_created:
            self.stdout.write(self.style.SUCCESS(f"Created example StackingPool: ({pool1})"))
        elif pool1 and not pool1_created:
            self.stdout.write(self.style.WARNING(f"Already exists example StackingPool: ({pool1})"))

        pool2, created = StackingPool.objects.get_or_create(name="Example Pool 2", conditions=conditions2)
        if pool2 and created:
            self.stdout.write(self.style.SUCCESS(f"Created example StackingPool: ({pool2})"))
        elif pool2 and not created:
            self.stdout.write(self.style.WARNING(f"Already exists example StackingPool: ({pool2})"))
