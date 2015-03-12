""" dyamic news reader script for x/84. """
# std
import os
import codecs
import logging

# local
from x84.bbs import getterminal, getsession, echo
from x84.bbs import syncterm_setfont, decode_pipe
from common import display_banner, prompt_pager

#: filepath to folder containing this script
here = os.path.dirname(__file__)

#: filepath to news contents persisted to disk
news_path = os.path.join(os.path.dirname(__file__), 'contrib')

#: encoding of news_file
news_file_encoding = 'utf8'

#: filepath to artfile displayed for this script
art_path = news_path

#: encoding used to display artfile
art_encoding = 'cp437'

#: fontset for SyncTerm emulator
syncterm_font = 'topaz'

#: estimated art height (top of pager)
art_height = 8

log = logging.getLogger(__name__)


def main(filename=None, title=None, art_file=None):
    """
    Script entry point.

    """
    session, term = getsession(), getterminal()

    news_file = os.path.join(news_path, filename)

    if not os.path.exists(news_file):
        log.warn('Unable to open news file, {0}'.format(news_file))
        echo(u'\r\n\r\n' + term.center(u'No news.').rstrip() + u'\r\n')
        return

    # set syncterm font, if any
    if syncterm_font and term.kind == 'ansi':
        echo(syncterm_setfont(syncterm_font))

    session.activity = 'Reading {0}'.format(news_file)

    # display banner
    if art_file:
        art_file = os.path.join(art_path, art_file)
        line_no = display_banner(filepattern=art_file, encoding=art_encoding)
    else:
        line_no = 0

    # retrieve news_file contents (decoded as utf8)
    news = decode_pipe(codecs.open(
        news_file, 'rb', news_file_encoding).read()
    ).splitlines()
    echo(u'\r\n\r\n')

    # display file contents, decoded, using a command-prompt pager.
    prompt_pager(content=news,
                 line_no=line_no + 2,
                 colors={'highlight': term.yellow,
                         'lowlight': term.green,
                         },
                 width=min(80, term.width))
