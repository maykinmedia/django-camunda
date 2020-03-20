from django.core.management import BaseCommand

from ...client import get_client


class Command(BaseCommand):
    help = "Delete process instances by ID"

    def add_arguments(self, parser):
        parser.add_argument("id", nargs="+", help="Process instance IDs to delete")

    def handle(self, **options):
        client = get_client()

        for _id in options["id"]:
            client.delete(f"process-instance/{_id}")
            self.stdout.write(f"Deleted {_id}")
