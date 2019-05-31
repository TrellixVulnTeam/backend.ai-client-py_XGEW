import sys
from typing import Iterable

import click
from tabulate import tabulate

from . import admin
from ..pretty import print_error, print_fail
from ...session import Session


@admin.command()
@click.argument('gid', type=str)
def group(gid):
    '''
    Show the information about the given group.

    \b
    GID: Group ID.
    '''
    fields = [
        ('ID', 'id'),
        ('Name', 'name'),
        ('Description', 'description'),
        ('Active?', 'is_active'),
        ('Created At', 'created_at'),
        ('Domain Name', 'domain_name'),
    ]
    with Session() as session:
        try:
            resp = session.Group.detail(gid=gid,
                                        fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        rows = []
        if resp is None:
            print('There is no such group.')
            sys.exit(1)
        for name, key in fields:
            if key in resp:
                rows.append((name, resp[key]))
        print(tabulate(rows, headers=('Field', 'Value')))


@admin.group(invoke_without_command=True)
@click.pass_context
@click.option('-d', '--domain-name', type=str, default=None,
              help='Domain name to list groups belongs to it.')
def groups(ctx, domain_name):
    '''
    List and manage groups.
    (admin privilege required)

    \b
    DOMAIN_NAME: Domain name to list groups belongs to it.
    '''
    if ctx.invoked_subcommand is not None:
        return
    if domain_name is None:
        print('Domain name should be given with "-d" option. '
              'If you want to see help for groups command, append "-h" option.')
        sys.exit(1)
    fields = [
        ('ID', 'id'),
        ('Name', 'name'),
        ('Description', 'description'),
        ('Active?', 'is_active'),
        ('Created At', 'created_at'),
        ('Domain Name', 'domain_name'),
    ]
    with Session() as session:
        try:
            resp = session.Group.list(domain_name=domain_name,
                                      fields=(item[1] for item in fields))
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if len(resp) < 1:
            print('There is no group.')
            return
        fields = [field for field in fields if field[1] in resp[0]]
        print(tabulate((item.values() for item in resp),
                        headers=(item[0] for item in fields)))


@groups.command()
@click.argument('domain_name', type=str, metavar='DOMAIN_NAME')
@click.argument('name', type=str, metavar='NAME')
@click.option('-d', '--description', type=str, default='',
              help='Description of new group.')
@click.option('-i', '--inactive', is_flag=True,
              help='New group will be inactive.')
def add(domain_name, name, description, inactive):
    '''
    Add new group. A group must belong to a domain, so DOMAIN_NAME should be provided.

    \b
    DOMAIN_NAME: Name of the domain where new group belongs to.
    NAME: Name of new group.
    '''
    with Session() as session:
        try:
            data = session.Group.create(
                domain_name, name,
                description=description,
                is_active=not inactive,
            )
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if not data['ok']:
            print_fail('Group creation has failed: {0}'.format(data['msg']))
            sys.exit(1)
        item = data['group']
        print('Group name {0} is created in domain {1}.'.format(item['name'], item['domain_name']))


@groups.command()
@click.argument('gid', type=str, metavar='GROUP_ID')
@click.option('-n', '--name', type=str, help='New name of the group')
@click.option('-d', '--description', type=str, help='Description of the group')
@click.option('--is-active', type=bool, help='Set group inactive.')
def update(gid, name, description, is_active):
    '''
    Update an existing group. Domain name is not necessary since group ID is unique.

    GROUP_ID: Group ID to update.
    '''
    with Session() as session:
        try:
            data = session.Group.update(
                gid,
                name=name,
                description=description,
                is_active=is_active,
            )
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if not data['ok']:
            print_fail('Group update has failed: {0}'.format(data['msg']))
            sys.exit(1)
        print('Group {0} is updated.'.format(name))


@groups.command()
@click.argument('gid', type=str, metavar='GROUP_ID')
def delete(gid):
    """
    Delete an existing group.

    GROUP_ID: Group ID to delete.
    """
    with Session() as session:
        try:
            data = session.Group.delete(gid)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if not data['ok']:
            print_fail('Group deletion has failed: {0}'.format(data['msg']))
            sys.exit(1)
        print('Group is deleted: ' + gid + '.')


@groups.command()
@click.argument('gid', type=str, metavar='GROUP_ID')
@click.argument('user_uuids', type=str, metavar='USER_UUIDS', nargs=-1)
def add_users(gid, user_uuids):
    '''
    Add users to a group.

    GROUP_ID: Group ID where users will be belong to.
    USER_UUIDS: List of users' uuids to be added to the group.
    '''
    with Session() as session:
        try:
            data = session.Group.add_users(gid, user_uuids)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if not data['ok']:
            print_fail('Error on adding users to group: {0}'.format(data['msg']))
            sys.exit(1)
        print('Users are added to the group')


@groups.command()
@click.argument('gid', type=str, metavar='GROUP_ID')
@click.argument('user_uuids', type=str, metavar='USER_UUIDS', nargs=-1)
def remove_users(gid, user_uuids):
    '''
    Remove users from a group.

    GROUP_ID: Group ID where users currently belong to.
    USER_UUIDS: List of users' uuids to be removed from the group.
    '''
    with Session() as session:
        try:
            data = session.Group.remove_users(gid, user_uuids)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if not data['ok']:
            print_fail('Error on removing users to group: {0}'.format(data['msg']))
            sys.exit(1)
        print('Users are removed from the group')
