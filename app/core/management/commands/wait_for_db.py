import time
from django.core.management.base import BaseCommand
from django.db import OperationalError
from psycopg2 import OperationalError as Psycopg2Error

"""Custom command to wati for db"""


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """EntryPoint for Command"""
        self.stdout.write("Waiting for db")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (OperationalError, Psycopg2Error):
                self.stdout.write("Database unavailable , waiting 1 second....")  # noqa
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
