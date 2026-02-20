import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from learning.models import Question


class Command(BaseCommand):
    help = 'Seed questions from dataset/questions.csv.'

    def handle(self, *args, **options):
        root = Path(__file__).resolve().parents[4]
        questions_path = root / 'dataset' / 'questions.csv'
        if not questions_path.exists():
            self.stdout.write(self.style.ERROR(f'questions.csv not found at {questions_path}'))
            return

        Question.objects.all().delete()

        created = 0
        with questions_path.open('r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Question.objects.create(
                    topic=row['topic'],
                    difficulty=row['difficulty'],
                    text=row['text'],
                    option_a=row['option_a'],
                    option_b=row['option_b'],
                    option_c=row['option_c'],
                    option_d=row['option_d'],
                    correct_option=row['correct_option'],
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Questions seeded. Created: {created}'))
