import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from learning.models import Course


class Command(BaseCommand):
    help = 'Seed courses from dataset/courses.csv.'

    def handle(self, *args, **options):
        root = Path(__file__).resolve().parents[4]
        courses_path = root / 'dataset' / 'courses.csv'
        if not courses_path.exists():
            self.stdout.write(self.style.ERROR(f'courses.csv not found at {courses_path}'))
            return

        Course.objects.all().delete()

        created = 0
        with courses_path.open('r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Course.objects.create(
                    title=row['title'],
                    topic=row['topic'],
                    difficulty=row['difficulty'],
                    description=row['description'],
                    url=row['url'],
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Courses seeded. Created: {created}'))
