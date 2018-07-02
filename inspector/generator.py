from inspector.tree import *

def generate_tree(connection, index_name):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM bt_metap(%s)', (index_name,))

    metapage_data = cursor.fetchone()

    metapage = Metapage(metapage_data[1], metapage_data[2],
                        metapage_data[3], metapage_data[4],
                        metapage_data[5])

    table_name, columns, primary_key_columns = get_index_info(connection, index_name)
    root, _ = retrieve_page(connection, metapage_data[2], index_name, table_name, columns, primary_key_columns)

    return Tree(metapage, root, index_name, table_name, columns)


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
            row_id, value = rows[item[1]]
            values_dict[item[5]] = value
            items.append(Item(value, pointer=item[1], obj_id=row_id))

        else:
            next_page_pointer = int(item[1][1:-1].split(',')[0])
            child, values_dict = retrieve_page(connection, next_page_pointer, index_name, table_name, columns, primary_key_columns, values_dict=values_dict)
            value = None
            if item[5]:
                value = values_dict.get(item[5], item[5])
            items.append(Item(value, page=child, pointer=item[1]))

    prev_item = None
    next_item = None

    # the first two items of each page are pointers to the next page first item (high key), and to the previous page last item
    if page.next_page_id:
        next_item = items.pop(0)
    if page.prev_page_id or (not page.prev_page_id
                             and not page.is_leaf
                             and not page.is_root):
        prev_item = items.pop(0)

    return items, prev_item, next_item, values_dict


def get_rows(connection, ctids, table_name, columns, primary_key_columns):
    in_query = ['%s::tid'] * len(ctids)

    query = "SELECT ctid, {}, {} FROM {} WHERE ctid IN ({});".format(
        ', '.join(primary_key_columns),
        ', '.join(columns),
        table_name,
        ', '.join(in_query))

    cursor = connection.cursor()
    cursor.execute(query, ctids)

    rows_data = cursor.fetchall()
    rows = {}
    index_pk = len(primary_key_columns) + 1

    for row in rows_data:
        rows[row[0]] = (row[1:index_pk],
                        row[index_pk:])

    return rows


def get_index_info(connection, index_name):
    query = """
    select
    t.relname as table_name,
    i.relname as index_name,
    array_to_string(array_agg(a.attname), ', ') as column_names

    from
    pg_class t,
    pg_class i,
    pg_index ix,
    pg_attribute a

    where
    t.oid = ix.indrelid
    and i.oid = ix.indexrelid
    and a.attrelid = t.oid
    and a.attnum = ANY(ix.indkey)
    and t.relkind = 'r'
    and i.relname = %s

    group by
    t.relname,
    i.relname;"""

    cursor = connection.cursor()
    cursor.execute(query, (index_name, ))

    data = cursor.fetchone()

    columns = data[2]
    if not isinstance(columns, list):
        columns = [columns]


    query = """
    SELECT array_agg(a.attname)
    FROM   pg_index i
    JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
    WHERE  i.indrelid = %s::regclass
    AND    i.indisprimary;
    """

    cursor.execute(query, (data[0], ))
    pk_data = cursor.fetchone()

    return data[0], columns, pk_data[0]
