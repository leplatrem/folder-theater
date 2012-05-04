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

On *Debian* or *Ubuntu*, install these with ::

    sudo apt-get install python-jinja2 python-imdbpy

On *Windows*, follow `Czarek's tutorial <https://github.com/leplatrem/folder-theater/wiki>`_.

*(Help for Mac OS instructions is welcome)*

Make sure you run a recent version of python-imdbpy (like > 4.8).


=====
USAGE
=====

**I have no idea what I'm doing with a python file**

It is a lot more stupid that was you think ! You run it in order to
generate a static `.html` file ! It has two files : a python file that
scraps *imdb* and provides the input data to the other file, a template.

**How do I run it on my web server ?** 

You run it in a command-line ! For example, in a crontab : 

::

    0 5,17 * * * /usr/bin/python /home/user/folder-theater.py --all /home/data/ > /var/www/index.html

You can then protect its access is protected by a basic `.htaccess` file.



Options
-------

::

    python folder-theater.py [options] FOLDER

    Options:
      -h, --help            show this help message and exit
      -o OUTPUT, --output=OUTPUT
                            Output to file
      -a, --all             Include unknown movies
      -x EXCLUDE, --exclude=EXCLUDE
                            Exclude files or folders by name (comma-separated)
      -s MINSIZE, --minsize=MINSIZE
                            Exclude files smaller than this size (MB)
      -l LIMIT, --limit=LIMIT
                            Limit list of found filenames
      -u URLPREFIX, --url=URLPREFIX
                            Add a link to movie titles with this URL prefix
      -t TITLE, --title=TITLE
                            Specify page title

Examples
--------

Add links for movies on local filesystem ::

    python folder-theater.py --url="file" /path/to/folder/

Add HTTP links for movies ::

    python folder-theater.py --url="http://server/example/" /path/to/folder/

Full example ::

   python folder-theater.py --all \
                            --title="Personal VOD" \
                            --exclude=".session" \
                            --url="http:/server.com/files/ \
                            /home/data/ > /var/www/index.html


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
* `Smewt <http://www.smewt.com/>`_ a *full-featured* media manager in python. No static output.
