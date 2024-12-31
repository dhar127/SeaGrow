# courses/management/commands/cleanup_files.py
from django.core.management.base import BaseCommand
from courses.models import Course
import os

class Command(BaseCommand):
    help = 'Cleans up orphaned files in media directory'

    def handle(self, *args, **kwargs):
        media_root = settings.MEDIA_ROOT
        for root, dirs, files in os.walk(media_root):
            for filename in files:
                filepath = os.path.join(root, filename)
                if not Course.objects.filter(pdf_file=filepath).exists():
                    os.remove(filepath)
                    self.stdout.write(f'Removed: {filepath}')