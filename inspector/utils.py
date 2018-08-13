def get_index_info(connection, index_name):
    query = """
    SELECT
    t.relname as table_name,
    i.relname as index_name,
    am.amname,
    array_to_string(array_agg(a.attname), ', ') as column_names

    FROM pg_index ix
    JOIN pg_class t ON (t.oid = ix.indrelid AND t.relkind = 'r')
    JOIN pg_class i ON (i.oid = ix.indexrelid)
    JOIN pg_am am ON (am.oid = i.relam)
    JOIN pg_attribute a ON (a.attrelid = t.oid AND a.attnum = ANY(ix.indkey))

    WHERE i.relname = %s
    GROUP BY t.relname, i.relname, am.amname;"""

    cursor = connection.cursor()
    cursor.execute(query, (index_name, ))

    data = cursor.fetchone()

    columns = data[3]
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

    return data[0], columns, pk_data[0], data[2]


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
