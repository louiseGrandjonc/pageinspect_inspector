from inspector.utils import get_index_info

from inspector.gist.generator import generate_gist_tree
from inspector.btree.generator import generate_btree


def generate_tree(connection, index_name):
    (table_name, columns,
     primary_key_columns, index_type) = get_index_info(connection, index_name)

    if index_type == 'btree':
        return generate_btree(connection, index_name, table_name,
                              columns, primary_key_columns)

    if index_type == 'gist':
        return generate_gist_tree(connection, index_name, table_name,
                                  columns, primary_key_columns)
