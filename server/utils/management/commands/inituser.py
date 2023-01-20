from django.core.management.base import BaseCommand

from account.models import AdminType, ProblemPermission, User, UserProfile
from utils.shortcuts import rand_str  # NOQA


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--username", type=str)
        parser.add_argument("--password", type=str)
        parser.add_argument("--name", type=str)
        parser.add_argument("--email", type=str)
        parser.add_argument("--teamname", type=str)
        parser.add_argument("--action", type=str)

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        name = options["name"]
        email = options["email"]
        team_name = options["teamname"]
        action = options["action"]

        team_members = [{"name": name, "email": email}]

        if not (username and password and action):
            self.stdout.write(self.style.ERROR("Invalid args"))
            exit(1)

        if action == "create_super_admin":
            if User.objects.filter(id=1).exists():
                self.stdout.write(self.style.SUCCESS(f"User {username} exists, operation ignored"))
                exit()

            user = User.objects.create(username=username, email=email, admin_type=AdminType.SUPER_ADMIN, problem_permission=ProblemPermission.ALL)
            user.set_password(password)
            user.save()
            UserProfile.objects.create(user=user, team_members=team_members, team_name=team_name)

            self.stdout.write(self.style.SUCCESS("User created"))
        elif action == "reset":
            try:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS("Password is reseted"))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User {username} doesnot exist, operation ignored"))
                exit(1)
        else:
            raise ValueError("Invalid action")
