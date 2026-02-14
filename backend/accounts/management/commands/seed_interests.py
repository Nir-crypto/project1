from django.core.management.base import BaseCommand
from accounts.models import Interest
from accounts.constants import DEFAULT_INTERESTS


class Command(BaseCommand):
    help = 'Seed default interests.'

    def handle(self, *args, **options):
        created = 0
        for name in DEFAULT_INTERESTS:
            _, is_created = Interest.objects.get_or_create(name=name)
            if is_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Interests seeded. Created: {created}'))
