import os

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(loader=PackageLoader('inspector', 'templates'),
                  autoescape=select_autoescape(['html', 'xml']))


def child_level_pages(pages):
    if not isinstance(pages, list):
        pages = [pages]
    children = []
    for page in pages:
        if page.is_leaf:
            return []
        for item in page.items:
            if item.child:
                children.append(item.child)

    return children

env.globals['child_level_pages'] = child_level_pages


def render_tree(tree, path):
    template = env.get_template('render_tree.html')

    file_path = os.path.join(path, '%s.html' % tree.index_name)
    with open(file_path, 'w') as html_file:
        html_file.write(template.render(tree=tree))
