from django.core.management.base import BaseCommand
from recommendations.models import FeedbackQuestion


DEFAULT_QUESTIONS = [
    {
        'question_text': 'How relevant was this course to your skill goals?',
        'type': 'SCALE',
        'options': ['1', '2', '3', '4', '5'],
    },
    {
        'question_text': 'Was the difficulty level appropriate?',
        'type': 'RADIO',
        'options': ['Too Easy', 'Just Right', 'Too Hard'],
    },
    {
        'question_text': 'Would you recommend this course to others?',
        'type': 'RADIO',
        'options': ['Yes', 'Maybe', 'No'],
    },
    {
        'question_text': 'How satisfied are you with the final assessment quality?',
        'type': 'SCALE',
        'options': ['1', '2', '3', '4', '5'],
    },
]


class Command(BaseCommand):
    help = 'Seed feedback questions.'

    def handle(self, *args, **options):
        created = 0
        for item in DEFAULT_QUESTIONS:
            _, is_created = FeedbackQuestion.objects.get_or_create(
                question_text=item['question_text'],
                defaults={
                    'type': item['type'],
                    'options': item['options'],
                },
            )
            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Feedback questions seeded. Created: {created}'))
