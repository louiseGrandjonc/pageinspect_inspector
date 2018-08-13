import sys

from psycopg2._range import DateTimeTZRange

from inspector.tree import *
from inspector.utils import get_index_info


def generate_gist_tree(connection, index_name, table_name,
                       columns, primary_key_columns):
    nb_levels = get_gist_data(connection, index_name)
    root = retrieve_page(connection, nb_levels, index_name, columns, 1)
    root.is_root = True

    return Tree(root, index_name, table_name, columns, index_type='gist')


def get_gist_data(connection, index_name):

    query = '''select gist_stat(%s);'''
    cursor = connection.cursor()

    cursor.execute(query, (index_name, ))

    data = cursor.fetchone()
    data = data[0].split('\n')

    nb_levels = data[0].split('Number of levels:          ')

    return int(nb_levels[1])


def retrieve_page(connection, nb_levels, index_name, columns,
                  current_level, current_blkno=None, current_offset=0):

    query = '''select gist_tree(%s, %s);'''

    cursor = connection.cursor()

    cursor.execute(query, (index_name, current_blkno or current_level))

    gist_tree_page_level = cursor.fetchone()

    gist_tree_page_level = gist_tree_page_level[0].split('\n')

    (level, _, blkno, _, nb_items, _, free_space,
     rightlink, invalid) = gist_tree_page_level[current_level-1].split()

    level = int(level.split('(l:')[1].split(')')[0])

    if 'InvalidBlockNumber' in invalid:
        next_page_id = None
    else:
        next_page_id = int(rightlink.split('rightlink:')[1])

    page = Page(int(current_blkno or blkno), level,
                nb_items=int(nb_items),
                items=[],
                next_page_id=next_page_id)

    children_page = gist_tree_page_level[current_level:]

    test = order_by_right_link(children_page)
    if current_level == 1:
        test = test[50:60]
    else:
        test = test[:20]

    page.items = retrieve_items(connection, page, index_name, columns,
                                nb_levels, current_level,
                                current_offset, int(nb_items),
                                test)
    return page


def retrieve_items(connection, page, index_name, columns, nb_levels, level,
                   current_offset, nb_items, tree_data):
    data = get_item_values(connection, index_name, columns[0], level,
                           current_offset, nb_items)

    offset_children = 0

    items = []

    for item in tree_data:
        if level == 1:
            print(item)

        offset_data = int(item[0].split('(')[0])
        value = data[offset_data-1][2]
        if isinstance(value, DateTimeTZRange):
            value = [value.lower.__str__(), value.upper.__str__()]

        item_obj = Item(value)

        if not level == nb_levels:
            item_obj.child = retrieve_page(
                connection, nb_levels, index_name,
                columns,
                level+1,
                current_offset=offset_children,
                current_blkno=int(item[2]))

            offset_children += int(item[4])
        else:
            page.is_leaf = True

        items.append(item_obj)

    return items


def get_item_values(connection, index_name, column, level, offset, nb_items):
    data_type_query = '''
    SELECT data_type
    FROM information_schema.columns
    WHERE column_name = %s;
    '''

    cursor = connection.cursor()
    cursor.execute(data_type_query, (column, ))
    column_type = cursor.fetchone()[0]

    if column_type == 'tsvector':
        column_type = 'gtsvector'

    query = '''
    SELECT * FROM  gist_print(%s)
    as t(level int, valid bool, a {})
    WHERE level = %s
    OFFSET %s
    LIMIT %s;
    '''.format(column_type)

    cursor.execute(query, (index_name, level, offset, nb_items))
    data = cursor.fetchall()

    return data


def order_by_right_link(pages):
    ordered_list = []
    for page in pages:
        if not page:
            continue
        ordered_list.append(page.split())


    # rightlink_dict = {}
    # blkno_dict = {}

    # for page in pages:
    #     data = page.split()
    #     if not data:
    #         continue

    #     if 'InvalidBlockNumber' in data[8]:
    #         rightlink_dict['rightmost'] = data
    #     else:
    #         rightlink_dict[int(data[7].split('rightlink:')[1])] = data

    #     blkno_dict[int(data[2])] = data

    # current = rightlink_dict['rightmost']
    # ordered_list = [current]
    # while len(ordered_list) != len(pages):
    #     try:
    #         current = rightlink_dict[int(current[2])]
    #         ordered_list.insert(0, current)
    #     except:
    #         current = blkno_dict[int(current[2])]
    #         break

    # if current not in ordered_list:
    #     ordered_list.insert(0, current)
    return ordered_list
