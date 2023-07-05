import urwid
from .dimjournal import download

def handle_input(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    elif key == 'd':
        archive_folder = edit.get_edit_text()
        download(archive_folder)

edit = urwid.Edit('Enter archive folder: ')
fill = urwid.Filler(edit, 'top')
loop = urwid.MainLoop(fill, unhandled_input=handle_input)

def main():
    loop.run()
