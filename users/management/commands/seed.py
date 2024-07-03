# In seed_users.py

from django.conf import settings
from django.core.management.base import BaseCommand
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Seed users data using Faker library'

    def handle(self, *args, **kwargs):
        print(settings.INSTALLED_APPS)
