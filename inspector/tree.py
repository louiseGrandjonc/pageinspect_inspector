class Metapage(object):
    def __init__(self, version, root, level, fast_root, fast_level):
        self.version = version
        self.root = root
        self.level = level
        self.fast_root = fast_root
        self.fast_level = fast_level

class Page(object):
    def __init__(self, pk, level,is_leaf=False, is_root=False, items=None, prev_page_id=None, next_page_id=None, high_key=None, prev_item=None):
        self.id = pk
        self.is_leaf = is_leaf
        self.is_root = is_root
        self.items = items
        self.level = level
        self.prev_page_id = prev_page_id
        self.next_page_id = next_page_id
        self.high_key = high_key
        self.prev_item = prev_item

class Item(object):
    def __init__(self, value, page=None, pointer=None, obj_id=None):
        self.value = value
        self.child = page
        self.pointer = pointer
        self.obj_id = obj_id

class Tree(object):
    def __init__(self, metapage, root, index_name, table_name, columns):
        self.metapage = metapage
        self.root = root
        self.index_name=index_name
        self.columns=columns
        self.index_table=table_name
