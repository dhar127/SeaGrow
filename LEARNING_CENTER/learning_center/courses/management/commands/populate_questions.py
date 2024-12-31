# courses/management/commands/populate_questions.py
from django.core.management.base import BaseCommand
from courses.models import Question
from sample_questions import QUESTIONS

class Command(BaseCommand):
    help = 'Populates the database with sample questions'

    def handle(self, *args, **kwargs):
        for topic_data in QUESTIONS:
            for q in topic_data['questions']:
                q['topic'] = topic_data['topic']
                q['level'] = topic_data['level']
                Question.objects.create(**q)
        self.stdout.write(self.style.SUCCESS('Successfully populated questions'))