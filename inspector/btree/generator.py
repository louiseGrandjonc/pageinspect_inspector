from inspector.tree import *
from inspector.utils import *


def generate_btree(connection, index_name, table_name,
                   columns, primary_key_columns):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM bt_metap(%s)', (index_name,))

    metapage_data = cursor.fetchone()

    metapage = Metapage(metapage_data[1], metapage_data[2],
                        metapage_data[3], metapage_data[4],
                        metapage_data[5])

    root, _ = retrieve_page(connection, metapage_data[2], index_name,
                            table_name, columns, primary_key_columns)

    return Tree(root, index_name, table_name, columns, metapage=metapage, index_type='btree')


def retrieve_page(connection, page_id, index_name, table_name, columns, primary_key_columns, values_dict={}):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM bt_page_stats(%s, %s)', (index_name, page_id))
    page_data = cursor.fetchone()

    is_leaf = page_data[1] == 'l'
    is_root = page_data[1] == 'r'

    page = Page(page_id, page_data[9], is_leaf=is_leaf, is_root=is_root, next_page_id=page_data[8],
                prev_page_id=page_data[7])

    items, prev_item, next_item, values_dict = retrieve_items(connection, page, index_name, table_name,
                                                             columns, primary_key_columns, values_dict=values_dict)
    page.items = items
    if next_item:
        page.high_key = next_item.value

    page.prev_item = prev_item

    return page, values_dict


def retrieve_items(connection, page, index_name, table_name, columns, primary_key_columns, values_dict={}):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM bt_page_items(%s, %s)', (index_name, page.id))
    items_data = cursor.fetchall()

    items = []

    if page.is_leaf:
        ctids = [item[1] for item in items_data]
        rows = get_rows(connection, ctids, table_name, columns, primary_key_columns)

    # if leaf, update items_data
    for item in items_data:
        if page.is_leaf:
            # this is a bug.
            # if this leaf page is not the rightmost page
            # so the first item is page higt key. 
            # but the ctid of item contained page higt key is not the ctid of row of table
            row_id, value = rows.get(item[1], (None, None))
            values_dict[item[5]] = value or item[5]
            items.append(Item(value or item[5], pointer=item[1], obj_id=row_id))

        else:
            next_page_pointer = int(item[1][1:-1].split(',')[0])
            child, values_dict = retrieve_page(connection, next_page_pointer, index_name, table_name, columns, primary_key_columns, values_dict=values_dict)
            value = None
            if item[5]:
                value = values_dict.get(item[5], item[5])
            else:
                value = ""
            items.append(Item(value, page=child, pointer=item[1]))

    prev_item = None
    next_item = None

    # the first two items of each page are pointers to the next page first item (high key), and to the previous page last item
    if page.next_page_id:
        next_item = items[0]
    if page.prev_page_id or (not page.prev_page_id
                             and not page.is_leaf
                             and not page.is_root):
        prev_item = items[0]

    return items, prev_item, next_item, values_dict
