import sys, getopt

import psycopg2

from inspector.generator import generate_tree
from inspector.renderer import render_tree


def main(argv):
    try:
        opts, args = getopt.getopt(argv,'hi:o:',['host=','port=', 'user=',
                                                 'db=', 'password=', 'index=',
                                                 "path="])
    except getopt.GetoptError:
        print('test.py --host <host> --port <port> --db <database_name> --password <password> --index <index> --path <file_path>')
        sys.exit(2)

    password = None

    for opt, arg in opts:
        if opt == '--help':
            print('test.py --host <host> --port <port> --db <database_name> --user <user> --password <password> --index <index>')
            sys.exit()
        elif opt in ('-h', '--host'):
            host = arg
        elif opt in ('-p', '--port'):
            port = arg
        elif opt in ('-db', '--db'):
            db = arg
        elif opt in ('-u', '--user'):
            user = arg
        elif opt in ('-pw', '--password'):
            password = arg
        elif opt in ('-i', '--index'):
            index = arg
        elif opt in ('-pa', '--path'):
            file_path = arg


    conn = psycopg2.connect(host=host, port=port,
                            dbname=db, user=user,
                            password=password)

    tree = generate_tree(conn, index)

    # render_tree
    render_tree(tree, file_path)


if __name__ == '__main__':
   main(sys.argv[1:])
