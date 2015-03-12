""" Main menu script for x/84. """
# std imports
from __future__ import division
import collections
import os

# local
from x84.bbs import (
    syncterm_setfont,
    getterminal,
    getsession,
    LineEditor,
    get_ini,
    gosub,
    echo,
    ini,
)
from common import (
    render_menu_entries,
    display_banner,
    display_prompt,
)

#: MenuItem is a definition class for display, input, and target script.
MenuItem = collections.namedtuple(
    'MenuItem', ['inp_key', 'text', 'script', 'args', 'kwargs'])

#: When set False, menu items are not colorized and render much
#: faster on slower systems (such as raspberry pi).
colored_menu_items = get_ini(
    section='main', key='colored_menu_items', getter='getboolean'
) or True

#: color used for menu key entries
color_highlight = get_ini(
    section='main', key='color_highlight'
) or 'bold_magenta'

#: color used for prompt
color_backlight = get_ini(
    section='main', key='color_backlight',
) or 'magenta_reverse'

#: color used for brackets ``[`` and ``]``
color_lowlight = get_ini(
    section='main', key='color_lowlight'
) or 'bold_black'

#: filepath to artfile displayed for this script
art_file = get_ini(
    section='main', key='art_file'
) or 'art/main1.asc'

#: encoding used to display artfile
art_encoding = get_ini(
    section='main', key='art_encoding'
) or 'cp437'  # ascii, actually

#: fontset for SyncTerm emulator
syncterm_font = get_ini(
    section='main', key='syncterm_font'
) or 'topaz'




def get_menu_items(session):
    """ Returns list of MenuItem entries. """
    #: A declaration of menu items and their acting gosub script
    menu_items = [
        MenuItem(inp_key=u'resume',
                 text=u'resume viewer',
                 script='news',
                 args=('resume.txt', ), kwargs={}),
        MenuItem(inp_key=u'about',
                 text=u'About  Jesse',
                 script='news',
                 args=('about.txt', ), kwargs={}),
        MenuItem(inp_key=u'who',
                 text=u"who's online",
                 script='online',
                 args=(), kwargs={}),
        MenuItem(inp_key=u'weather',
                 text=u'weather forecast',
                 script='weather',
                 args=(), kwargs={}),
        MenuItem(inp_key=u'tetris',
                 text=u'tetris game',
                 script='tetris',
                 args=(), kwargs={}),
        MenuItem(inp_key=u'lc',
                 text=u'last callers',
                 script='lc',
                 args=(), kwargs={}),
        MenuItem(inp_key=u'ac',
                 text=u'adjust charset',
                 script='charset',
                 args=(), kwargs={}),

        MenuItem(inp_key=u'g',
                 text=u'logoff system',
                 script='logoff',
                 args=(), kwargs={}),

    ]

    return menu_items


def get_line_editor(term, menu):
    """ Return a line editor suitable for menu entry prompts. """
    # if inp_key's were CJK characters, you should use term.length to measure
    # printable length of double-wide characters ... this is too costly to
    # enable by default.  Just a note for you east-asian folks.
    max_inp_length = max([len(item.inp_key) for item in menu])
    return LineEditor(width=max_inp_length,
                      colors={'highlight': getattr(term, color_backlight)})


def main():
    """ Main menu entry point. """
    session, term = getsession(), getterminal()

    text, width, height, dirty = u'', -1, -1, 2
    menu_items = get_menu_items(session)
    editor = get_line_editor(term, menu_items)
    colors = {}
    if colored_menu_items:
        colors['backlight'] = getattr(term, color_backlight)
        colors['highlight'] = getattr(term, color_highlight)
        colors['lowlight'] = getattr(term, color_lowlight)

    while True:
        if dirty == 2:
            # set syncterm font, if any
            if syncterm_font and term.kind.startswith('ansi'):
                echo(syncterm_setfont(syncterm_font))
        if dirty:
            session.activity = 'main menu'
            top_margin = display_banner(art_file, encoding=art_encoding) + 1
            echo(u'\r\n')
            if width != term.width or height != term.height:
                width, height = term.width, term.height
                text = render_menu_entries(
                    term, top_margin, menu_items, colors)
            echo(u''.join((text,
                           display_prompt(term, colors),
                           editor.refresh())))
            dirty = 0

        event, data = session.read_events(('input', 'refresh'))

        if event == 'refresh':
            dirty = True
            continue

        elif event == 'input':
            session.buffer_input(data, pushback=True)

            # we must loop over inkey(0), we received a 'data'
            # event, though there may be many keystrokes awaiting for our
            # decoding -- or none at all (multibyte sequence not yet complete).
            inp = term.inkey(0)
            while inp:
                if inp.code == term.KEY_ENTER:
                    # find matching menu item,
                    for item in menu_items:
                        if item.inp_key == editor.content.strip():
                            echo(term.normal + u'\r\n')
                            gosub(item.script, *item.args, **item.kwargs)
                            editor.content = u''
                            dirty = 2
                            break
                    else:
                        if editor.content:
                            # command not found, clear prompt.
                            echo(u''.join((
                                (u'\b' * len(editor.content)),
                                (u' ' * len(editor.content)),
                                (u'\b' * len(editor.content)),)))
                            editor.content = u''
                            echo(editor.refresh())
                elif inp.is_sequence:
                    echo(editor.process_keystroke(inp.code))
                else:
                    echo(editor.process_keystroke(inp))
                inp = term.inkey(0)
