import sys

from tabulate import tabulate

from ...session import Session
from ..pretty import print_error
from . import admin


@admin.register_command
def sessions(args):
    '''
    List and manage compute sessions.
    '''
    fields = [
        ('Session ID', 'sess_id'),
        ('Lang/runtime', 'lang'),
        ('Tag', 'tag'),
        ('Created At', 'created_at',),
        ('Terminated At', 'terminated_at'),
        ('Status', 'status'),
        ('CPU Cores', 'cpu_slot'),
        ('CPU Used (ns)', 'cpu_used'),
        ('Total Memory (MiB)', 'mem_slot'),
        ('Used Memory (MiB)', 'mem_cur_bytes'),
        ('GPU Cores', 'gpu_slot'),
    ]
    if args.access_key is None:
        q = 'query($status:String) {' \
            '  compute_sessions(status:$status) { $fields }' \
            '}'
    else:
        q = 'query($ak:String, $status:String) {' \
            '  compute_sessions(access_key:$ak, status:$status) { $fields }' \
            '}'
    q = q.replace('$fields', ' '.join(item[1] for item in fields))
    v = {
        'status': args.status if args.status != 'ALL' else None,
        'ak': args.access_key,
    }
    with Session() as session:
        try:
            resp = session.Admin.query(q, v)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if len(resp['compute_sessions']) == 0:
            print('There are no compute sessions currently running.')
            return
        for item in resp['compute_sessions']:
            item['mem_cur_bytes'] = round(item['mem_cur_bytes'] / 2 ** 20, 1)
        print(tabulate((item.values() for item in resp['compute_sessions']),
                       headers=(item[0] for item in fields)))


sessions.add_argument('--status', type=str, default='RUNNING',
                      choices={'PREPARING', 'BUILDING', 'RUNNING',
                               'RESTARTING', 'RESIZING', 'SUSPENDED',
                               'TERMINATING', 'TERMINATED', 'ERROR', 'ALL'},
                      help='Filter by the given status')
sessions.add_argument('--access-key', type=str, default=None,
                      help='Get sessions for a specific access key '
                           '(only works if you are a super-admin)')


@admin.register_command
def session(args):
    '''
    Show detailed information for a running compute session.
    '''
    fields = [
        ('Session ID', 'sess_id'),
        ('Role', 'role'),
        ('Lang/runtime', 'lang'),
        ('Tag', 'tag'),
        ('Created At', 'created_at',),
        ('Terminated At', 'terminated_at'),
        ('Agent', 'agent'),
        ('Status', 'status',),
        ('Status Info', 'status_info',),
        ('CPU Cores', 'cpu_slot'),
        ('CPU Used (ns)', 'cpu_used'),
        ('Total Memory (MiB)', 'mem_slot'),
        ('Used Memory (MiB)', 'mem_cur_bytes'),
        ('Max Used Memory (MiB)', 'mem_max_bytes'),
        ('GPU Cores', 'gpu_slot'),
        ('Number of Queries', 'num_queries'),
        ('Network RX Bytes', 'net_rx_bytes'),
        ('Network TX Bytes', 'net_tx_bytes'),
        ('IO Read Bytes', 'io_read_bytes'),
        ('IO Write Bytes', 'io_write_bytes'),
        ('IO Max Scratch Size', 'io_max_scratch_size'),
        ('IO Current Scratch Size', 'io_cur_scratch_size'),
    ]
    q = 'query($sess_id:String) {' \
        '  compute_session(sess_id:$sess_id) { $fields }' \
        '}'
    q = q.replace('$fields', ' '.join(item[1] for item in fields))
    v = {'sess_id': args.sess_id_or_alias}
    with Session() as session:
        try:
            resp = session.Admin.query(q, v)
        except Exception as e:
            print_error(e)
            sys.exit(1)
        if resp['compute_session']['sess_id'] is None:
            print('There is no such running compute session.')
            return
        print('Session detail:\n---------------')
        for i, value in enumerate(resp['compute_session'].values()):
            if fields[i][1] in ['mem_cur_bytes', 'mem_max_bytes']:
                value = round(value / 2 ** 20, 1)
            print(fields[i][0] + ': ' + str(value))


session.add_argument('sess_id_or_alias', metavar='NAME',
                     help='The session ID or its alias '
                          'given when creating the session.')
