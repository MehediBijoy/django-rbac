# In seed_users.py

import random
from faker import Faker
from django.core.management.base import BaseCommand
from users.models import User, UserRole, UserStatus

fake = Faker()


class Command(BaseCommand):
    help = 'Seed users data using Faker library'

    def handle(self, *args, **kwargs):
        num_users = 100  # Specify the number of users you want to create

        for _ in range(num_users):
            email = fake.email()
            password = fake.password()  # You might want to generate secure passwords
            status = random.choice(
                [UserStatus.ACTIVE, UserStatus.INACTIVE, UserStatus.INVESTIGATE, UserStatus.BLOCKED])
            status_reason = fake.sentence()
            role = random.choice(
                [UserRole.USER, UserRole.ADMIN, UserRole.SUPER_ADMIN])
            is_active = fake.boolean()
            is_staff = fake.boolean()
            is_superuser = fake.boolean()

            # Create the user
            user = User.objects.create_user(
                email=email,
                password=password,
                status=status,
                status_reason=status_reason,
                role=role,
                is_active=is_active,
                is_staff=is_staff,
                is_superuser=is_superuser,
            )

            # You can add more fields as needed

            self.stdout.write(self.style.SUCCESS(f'User created: {user.email}'))
