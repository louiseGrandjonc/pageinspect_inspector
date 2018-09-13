---------------------
PageInspect inspector
---------------------

Hello and welcome,

For some reason you're here wondering if you can use this tool to visualize the internal structure of an index of yours.

It requires python3.6.*. 
You'll also have to install pageinspect (https://www.postgresql.org/docs/10/static/pageinspect.html) extension.
If you want to use this tool for GiST indexes, you'll have to install gevel (http://www.sai.msu.su/~megera/wiki/Gevel) postgres extensions. 

You can clone this and then run

::
   
   python setup.py develop


The command line is then

::
   
   python inspector/command.py --host <host> --port <port> --db <your_db> --user <youruser> --index <index_name> --path <your_path>

It will generate a wonderful html. The ``path`` is the path of the html file to be saved.

Right now it only works with BTree and GiST. I will add BRIN index eventually :)
