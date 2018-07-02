# PageInspect inspector

Hello and welcome,

For some reason you're here wondering if you can use this tool to visualize the internal structure of an index of yours.

You can clone this and then run `python setup.py develop`


The command line is then

`python inspector/command.py --host <host> --port <port> --db <your_db> --user <youruser> --index <index_name> --path <your_path>`

It will generate a wonderful html. The `path` is where you want the html file to be saved.

Right now it only works with BTree but I'm going to add BRIN and GIN indexes as well :)
