import urwid

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def main(archive_folder):
    txt = urwid.Text(f"Archive folder: {archive_folder}\nPress 'd' to download, 'q' to quit")
    fill = urwid.Filler(txt, 'top')
    loop = urwid.MainLoop(fill, unhandled_input=exit_on_q)
    loop.run()
