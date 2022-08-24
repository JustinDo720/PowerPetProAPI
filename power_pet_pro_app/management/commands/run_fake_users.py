from faker import Faker
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from users.models import Profile
from users.models import CustomUser
import random


USERNAMES = [
    'DarkenBlue',
    'DarkenMuffin',
    'DarkenSnow',
    'DarkenJacob',
    'DarkenLogan',
    'LightenBlue',
    'LightenMuffin',
    'LightenSnow',
    'LightenJacob',
    'LightenLogan',
    'DarkenJustin',
    'LightenJustin',
    'BlueBot',
    'NavyBot',
    'Admin',

]

DEFAULT_PASSWORD = 'testing123'


class Command(BaseCommand):
    help = 'Build random users with names.'

    def handle(self, *args, **options):
        # Building Faker
        fake = Faker()

        for name in USERNAMES:
            # we will make up our random number
            phone_number = ''.join([str(random.randint(1, 9)) for turns in range(10)]) # don't use int as phone number

            # Make sure to .save() each object
            try:
                # We are going to set this user as superuser
                if name.lower() == 'admin':
                    # Creating Admin User Instance
                    # We need to add email asap if not users_customuser.email will have integrityError
                    email = 'fakeadminuser@gmail.com'
                    admin_user = CustomUser.objects.create_user(username=name, password=DEFAULT_PASSWORD, email=email,
                                                                is_superuser=True, is_staff=True)
                    admin_user.first_name = 'Admin'
                    admin_user.last_name = 'User'
                    admin_user.save()

                    # Profile User
                    admin_profile = Profile.objects.get(id=admin_user.id)
                    admin_profile.phone_number = phone_number
                    admin_profile.address = fake.unique.street_address()
                    admin_profile.city = fake.city()
                    admin_profile.country = fake.current_country()
                    admin_profile.state = fake.country_code()
                    admin_profile.zip_code = int(fake.postcode())
                    admin_profile.save()
                    print('Registered admin: ' + name)
                    print(admin_user)
                else:
                    # Creating Default User Instance
                    email = fake.unique.email()
                    default_user = CustomUser.objects.create_user(username=name, password=DEFAULT_PASSWORD, email=email)
                    default_user.first_name = fake.first_name()
                    default_user.last_name = fake.last_name()
                    default_user.save()

                    # Profile User
                    default_profile = Profile.objects.get(id=default_user.id)
                    default_profile.phone_number = phone_number
                    default_profile.address = fake.unique.street_address()
                    default_profile.city = fake.city()
                    default_profile.country = fake.current_country()
                    default_profile.state = fake.country_code()
                    default_profile.zip_code = int(fake.postcode())
                    default_profile.save()
                    print('Register user: ' + name)
                    print(default_user)
            except IntegrityError:
                print('User %s has already been created' % name)
                continue


