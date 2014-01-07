from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from finial.util import add_flag_to_all_users, remove_flag_from_all_users


class Command(BaseCommand):
    args = 'flag_name'
    help = 'Adds or removes a finial flag to all known users.'

    option_list = (
        BaseCommand.option_list + (
            make_option(
                '--remove',
                action='store_true',
                dest='remove',
                default=False,
                help='Remove flag from all users'
            ),
            make_option(
                '--add',
                action='store_true',
                dest='add',
                default=False,
                help='Add flag from all users'
            ),
            make_option(
                '--batch-size',
                dest='batch_size',
                default=1000,
            ),
            make_option(
                '--silent',
                action='store_true',
                dest='silent',
                default=False,
                help='Do not ask for confirmation',
            )
        )
    )

    def handle(self, *args, **options):
        try:
            flag_name = args[0]
        except IndexError:
            raise CommandError("Must provide a finial flag to add")

        add = options['add']
        remove = options['remove']
        silent = options['silent']
        batch_size = options['batch_size']

        if add:
            add_flag_to_all_users(
                flag_name,
                silent=silent,
                batch_size=batch_size
            )
        elif remove:
            remove_flag_from_all_users(flag_name, silent=silent)
        else:
            raise CommandError("Must use either --add or --remove")
