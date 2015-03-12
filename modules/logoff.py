""" logoff script with 'automsg' for x/84. """


def main():
    """ Main procedure. """
    # pylint: disable=R0914,R0912
    #         Too many local variables
    #         Too many branches
    from x84.bbs import getsession, getterminal, echo
    from x84.bbs import disconnect, getch

    session, term = getsession(), getterminal()
    session.activity = 'logging off'
    goodbye_msg = term.bold_blue(u'NO CARRIER\r\n')
    echo(goodbye_msg)

    # http://www.xfree86.org/4.5.0/ctlseqs.html
    # Restore xterm icon and window title from stack.
    echo(unichr(27) + u'[23;0t')
    getch(1.5)
    disconnect('+++')
