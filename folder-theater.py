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
from urlparse import urlparse, urljoin

try:
    from imdb import IMDb, Movie
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

MOVIE_EXT = ('ogm', 'avi', 'mp4', 'mkv', 'mpg', 'mpeg', 'divx', 'vob', 
             'mt2s', '3gp', 'rmvb', 'rmv', 'wmv', 'mov')


def list_titles(path, excludes=[], minsize=-1):
    """ Returns a list of files/folders names ordered by time desc. """
    titleslist = []
    for name in os.listdir(path):
        if name in excludes:
            continue
        filename = os.path.join(path, name)
        stats = os.stat(filename)
        mtime = time.localtime(stats.st_mtime)
        if os.path.isdir(filename):
            basename = name
        else:
            if stats.st_size < minsize*1024*1024:
                continue
            basename, ext = os.path.splitext(name)
            if ext[1:] not in MOVIE_EXT:
                continue
        titleslist.append((mtime, basename.decode('utf-8'), name.decode('utf-8')))
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


def fetch_movie(name, basename, filename, added, allow_empty=False):
    """ Scrap IMDB and returns a imdb.Movie object """
    ia = IMDb()
    movie = ia.search_movie(name)
    empty = Movie.Movie(title=name)
    
    if not movie:
        logger.warning(_("No result for '%s'") % name)
        if allow_empty:
            movie = empty
        else:
            return None
    else:
        movie = movie[0]
        movie = ia.get_movie(movie.movieID)
        movie.imdb = ia.get_imdbURL(movie)
    
    # Ignore movies whose found title are too far from searched title
    fulltitle = movie.get('title', '')
    akas = [fulltitle] + movie.get('akas', [])
    fuzzy = 0
    for aka in akas:
        aka = aka.split('::')[0]
        ratio = SequenceMatcher(None, name.lower(), aka.lower()).ratio()
        if ratio > fuzzy:
            fulltitle = aka
            fuzzy = ratio
    movie.title = fulltitle
    if fuzzy <= MIN_FUZZY_RATIO:
        logger.warning(_("Possible mismatch '%s' for '%s'") % (fulltitle, name))
        if allow_empty:
            movie = empty
        else:
            return None
    # Post process plot string
    p = movie.get('plot', [''])[0]
    movie.plot = p.split('::')[0]
    # Additional fields
    movie.search = name
    movie.added = datetime.fromtimestamp(time.mktime(added))
    movie.ageweek = (datetime.now() - movie.added).days // 7
    movie.basename = basename
    movie.filename = urllib.quote(filename.encode('utf-8'))
    movie.allocine = ALLOCINE_URL % urllib.quote_plus(fulltitle.encode('utf-8'))
    return movie


def build_movies(titles, all=False):
    """ Return a list of imdb.Movie objects for a list of tuples with """
    chosen = []
    uniq = []
    for (datetime, basename, filename) in titles:
        # Guess movie names from filenames
        title = movie_name(basename)    
        # Uniquify titles list
        if title not in uniq:
            m = fetch_movie(title, basename, filename, datetime, allow_empty=all)
            if not m:
                continue
            logger.info(_("Found '%s' for '%s' (%s)") % (m['title'], title, filename))
            chosen.append(m)
            uniq.append(title)
    return chosen


def render_page(movies, output=None, title="", urlprefix=""):
    """ Render the movies list to specified output """
    env = Environment(extensions=['jinja2.ext.i18n'])
    env.install_null_translations()
    with open(TEMPLATE_PATH) as tpl:
        template = env.from_string(tpl.read().decode('utf-8'))
    # Default output is stdout
    out = sys.stdout
    if output:
        out = open(output, 'w')
    page = template.render(movies=movies, title=title, urlprefix=urlprefix)
    out.write(page.encode('ascii', 'xmlcharrefreplace'))
    out.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)

    parser = optparse.OptionParser(usage='%prog [options] FOLDER',
                                   description=_("Generates a fancy Web page from a folder with movies."))
    parser.add_option("-o", "--output",
                      dest="output", default=None,
                      help=_("Output to file"))
    parser.add_option("-a", "--all",
                      dest="all", default=False, action="store_true",
                      help=_("Include unknown movies"))
    parser.add_option("-x", "--exclude",
                      dest="exclude", default="",
                      help=_("Comma-separated list of folders to exclude"))
    parser.add_option("-s", "--minsize",
                      dest="minsize", type='int', default=-1,
                      help=_("Exclude files smaller than this size (in MB)"))
    parser.add_option("-l", "--limit",
                      dest="limit", type='int', default=-1,
                      help=_("Limit list of found filenames"))
    parser.add_option("-u", "--url",
                      dest="urlprefix", default="",
                      help=_("Add a link to movie titles with this URL prefix"))
    parser.add_option("-t", "--title",
                      dest="title", default="Folder Threater",
                      help=_("Specify page title"))

    (options, args) = parser.parse_args(sys.argv)
    if len(args) < 2:
        parser.print_help()
        parser.exit()
    folder = args[1]

    # Sanity checks on urlprefix
    url = options.urlprefix
    if url:
        if not urlparse(url).scheme:
            url += "://"
        if not urlparse(url).path:
            url += os.path.abspath(folder)
        if not url.endswith("/"):
            url += "/"
        options.urlprefix = url

    # List files/folders
    filenames = list_titles(folder, excludes=options.exclude.split(","), minsize=options.minsize)
    if options.limit > 0:
        filenames = filenames[:options.limit]
    # Convert to HTML
    render_page(build_movies(filenames, options.all), 
                options.output,
                options.title.decode('utf-8'),
                options.urlprefix)
