"""
Default matrix (login) script for x/84.

This script is the default session entry point for all connections.

Or simply put, the login program. It is configured in default.ini file,
under section 'matrix'. Alternative matrices may be considered by their
connection type, using script_{telnet,ssh}

In legacy era, a matrix script might be something to fool folk not in the
know, meant to divert agents from underground boards, require a passcode,
or even swapping the modem into a strange stop/bit/parity configuration,
callback mechanisms, etc..

Read all about it in old e-zines.
"""
# std
import logging
import os

from x84.bbs import getterminal, get_ini, goto
from x84.bbs import echo, showart, syncterm_setfont
from x84.bbs import User
from x84.engine import __url__

log = logging.getLogger()
here = os.path.dirname(__file__)

#: which login names that trigger anonymous login.
anonymous_names = get_ini(
    section='matrix', key='anoncmds', split=True
) or ['anonymous']

#: name of bbs
system_bbsname = get_ini(
    section='system', key='bbsname'
) or 'Unnamed'


#: on-connect fontset for SyncTerm emulator
syncterm_font = get_ini(
    section='matrix', key='syncterm_font'
) or 'topaz'

#: on-connect banner
art_file = get_ini(
    section='matrix', key='art_file'
) or os.path.join(here, 'art', 'matrix.ans')

#: encoding on banner
art_encoding = get_ini(
    section='matrix', key='art_encoding'
) or 'cp437'

#: primary color (highlight)
color_primary = get_ini(
    section='matrix', key='color_primary'
) or 'red'

#: secondary color (lowlight)
color_secondary = get_ini(
    section='matrix', key='color_secondary'
) or 'green'

def display_banner(term):
    """ Display on-connect banner and set a few sequences. """

    # reset existing SGR attributes
    echo(term.normal)

    # set syncterm font, if any
    if syncterm_font and term.kind.startswith('ansi'):
        echo(syncterm_setfont(syncterm_font))

    # http://www.termsys.demon.co.uk/vtansi.htm
    # disable line-wrapping (SyncTerm does not honor, careful!)
    echo(u'\x1b[7l')

    if term.kind.startswith('xterm'):
        # http://www.xfree86.org/4.5.0/ctlseqs.html
        # Save xterm icon and window title on stack.
        echo(u'\x1b[22;0t')

    # move to beginning of line and clear, in case syncterm_setfont
    # has been mis-interpreted, as it follows CSI with space, which
    # causes most terminal emulators to receive literally after CSI.
    echo(term.move_x(0) + term.clear_eol)

    # display name of bbs and url to sourcecode.
    highlight = getattr(term, color_primary)
    sep = getattr(term, color_secondary)(u'-/-')

    echo(u'{sep} You have connected to jesseward.com/X BBS. San Jose, California {sep}\r\n'.format(sep=sep))
    echo(u'{name} / telnet port 49152\r\n'.format(name=highlight(system_bbsname)))
    # display on-connect banner (`art_file`)
    map(echo, showart(art_file, encoding=art_encoding, center=True))

    sep = getattr(term, color_secondary)(u'::')
    echo(u'{sep} Connecting as user {user}.\r\n'.format(sep=sep, user=highlight(anonymous_names[0])))
    echo(u'{sep} Terminal : {term}\r\n'.format(term=term.kind, sep=sep))


    echo(u'{sep} Press [ENTER] to continue.'.format(sep=sep))

    inp = term.inkey()
    user = User('anonymous')

    goto('main-menu')

def main(anonymous=False, new=False):
    """
    Script entry point.

    This is the default login matrix for the bbs system.

    It takes no arguments or keyword arguments, because it assumes
    the user should now be authenticated, such as occurs for example
    on telnet.
    """
    term = getterminal()

    display_banner(term)

    goto('main-menu')

    # do_login will goto/gosub various scripts, if it returns, then
    # either the user entered 'bye', or had too many failed attempts.
    do_login(term)

    log.debug('Disconnecting.')

    # it is necessary to provide sufficient time to send any pending
    # output across the transport before disconnecting.
    term.inkey(1.5)
