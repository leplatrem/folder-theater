# -*- coding: utf-8 -*-
#!/usr/bin/python

# BEER-WARE LICENSE
# Mathieu Leplatre <contact@mathieu-leplatre.info> wrote this file. 
# As long as you retain this notice you can do whatever you want with this stuff. 
# If we meet some day, and you think this stuff is worth it, 
# you can buy me a beer in return.

import sys
import os
import time
from datetime import datetime
from operator import itemgetter
import re
import logging
from difflib import SequenceMatcher
import urllib
import optparse
from gettext import gettext as _

try:
    from imdb import IMDb
    from jinja2 import Environment
except ImportError, e:
    print _("Error: %s, install typing:") % e
    print "sudo apt-get install python-imdbpy python-jinja2"
    exit()


logger = logging.getLogger(__name__)

MIN_FUZZY_RATIO = .5
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'folder-theater.tmpl')
ALLOCINE_URL = "http://www.allocine.fr/recherche/?q=%s" 

BLACKLIST = ('dvdrip', 'bdrip',
             'pdtv', 'original', 'hdtv', 'hd',
             'french', 'fr', 'vo', 'vost',
             'xvid')


def list_titles(path, excludes=[]):
    """ Returns a list of files/folders names ordered by time desc. """
    titleslist = []
    for name in os.listdir(path):
        if name in excludes:
            continue
        filename = os.path.join(path, name)
        stats = os.stat(filename)
        mtime = time.localtime(stats[8])
        if not os.path.isdir(filename):
            basename, ext = os.path.splitext(name)
            name = basename
        titleslist.append((mtime, name.decode('utf-8')))
    titleslist.sort()
    titleslist.reverse()
    return titleslist


def movie_name(filepath):
    """ Returns the probable movie title from a filepath """
    tokens = re.compile("[.\s_\-\[\]\(\)]+").split(filepath)
    name = u''
    p = re.compile("|".join(BLACKLIST) +
                   "|([12][09][0-9][0-9])" + 
                   "|S[0-9]{1,2}(E[0-9]{1,2})?", re.IGNORECASE)
    for token in tokens:
        if not p.match(token):
            name += u"%s " % token
        else:
            break
    return name.strip()


def fetch_movie(name, filename, added):
    """ Scrap IMDB and returns a imdb.Movie object """
    ia = IMDb()
    movie = ia.search_movie(name)
    if not movie:
        logger.warning(_("No result for '%s'") % name)
        return None
    movie = movie[0]
    movie = ia.get_movie(movie.movieID)
    p = movie.get('plot')
    if not p:
        p = ['']
    p = p[0]
    i = p.find('::')
    if i != -1:
        p = p[:i]
    movie.plot = p
    movie.search = name
    movie.added = datetime.fromtimestamp(time.mktime(added))
    movie.ageweek = (datetime.now() - movie.added).days // 7
    movie.filename = filename
    movie.imdb = ia.get_imdbURL(movie)
    movie.allocine = ALLOCINE_URL % urllib.quote_plus(movie['title'].encode('utf-8'))
    return movie


def build_movies(titles):
    """ Return a list of imdb.Movie objects for a list of tuples with """
    chosen = []
    uniq = []
    for (datetime, filename) in titles:
        # Guess movie names from filenames
        title = movie_name(filename)    
        # Uniquify titles list
        if title not in uniq:
            m = fetch_movie(title, filename, datetime)
            if not m:
                continue
            # Ignore movies whose found title are too far from searched title
            fulltitle = m['title']
            fuzzy = SequenceMatcher(None, title.lower(), fulltitle.lower()).ratio()
            if fuzzy > MIN_FUZZY_RATIO:
                logger.info(_("Found '%s' for '%s' (%s)") % (fulltitle, title, filename))
                chosen.append(m)
            else:
                logger.warning(_("Rejected '%s' for '%s'") % (fulltitle, title))
            uniq.append(title)
    return chosen


def render_page(movies, output=None):
    """ Render the movies list to specified output """
    env = Environment(extensions=['jinja2.ext.i18n'])
    env.install_null_translations()
    with open(TEMPLATE_PATH) as tpl:
        template = env.from_string(tpl.read().decode('utf-8'))
    # Default output is stdout
    out = sys.stdout
    if output:
        out = open(output, 'w')
    page = template.render(movies=movies)
    out.write(page.encode('ascii', 'xmlcharrefreplace'))
    out.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)

    parser = optparse.OptionParser(usage='%prog [options] FOLDER',
                                   description=_("Generates a fancy Web page from a folder with movies."))
    parser.add_option("-o", "--output",
                      dest="output", default=None,
                      help=_("Output to file"))
    parser.add_option("-x", "--exclude",
                      dest="exclude", default="",
                      help=_("Comma-separated list of folders to exclude"))
    parser.add_option("-l", "--limit",
                      dest="limit", type='int', default=-1,
                      help=_("Limit list of found filenames"))

    (options, args) = parser.parse_args(sys.argv)
    if len(args) < 2:
        parser.print_help()
        parser.exit()

    # List files/folders
    filenames = list_titles(args[1], excludes=options.exclude)
    if options.limit > 0:
        filenames = filenames[:options.limit]
    # Convert to HTML
    render_page(build_movies(filenames), options.output)