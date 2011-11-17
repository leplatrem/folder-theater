Folder-Theater
##############

Generates a fancy Web page from a folder with movies files. 

All movies details are gathered from IMDb (cover, year, rating, plot, 
director, actors).

.. image:: http://mathieu-leplatre.info/media/folder-theatre.png

=======
INSTALL
=======

It requires `jinja2 <http://jinja.pocoo.org/>`_ and `imdbpy <http://imdbpy.sourceforge.net>`_.

On Ubuntu, install these with ::

    sudo apt-get install python-jinja2 python-imdbpy


*(Help for Windows and Mac OS instructions is welcome)*

=====
USAGE
=====

::

    python folder-theater.py [options] FOLDER

    Options:
      -h, --help            show this help message and exit
      -o OUTPUT, --output=OUTPUT
                            Output to file
      -a, --all             Include unknown movies
      -x EXCLUDE, --exclude=EXCLUDE
                            Comma-separated list of folders to exclude
      -l LIMIT, --limit=LIMIT
                            Limit list of found filenames


=======
LICENSE
=======

* Beer-ware License

=======
AUTHORS
=======

* Mathieu Leplatre <contact@mathieu-leplatre.info>


================
Related Software
================

Before to start writing the first line of code, I had found these projects :

* `movie.js <http://www.gosu.pl/movies-en.html>`_ by Czarek Tomczak. Exactly what I needed, but *Windows only*.
* `Smewt <www.smewt.com/>`_ a *full-featured* media manager in python. No static output.
