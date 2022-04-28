from tkinter import ttk

import chat_refresher

bar = None


# initializing new progressbar
def init():
    pb_style = ttk.Style()
    pb_style.theme_use('clam')
    pb_style.configure("red.Horizontal.TProgressbar", foreground='#212121', background='#212121',
                       throughcolor='#212121')
    global bar
    bar = ttk.Progressbar(chat_refresher.ROOT, orient='horizontal', mode='determinate', length=450,
                          style='red.Horizontal.TProgressbar')


# showing the bar (need to be initialized)
def show():
    global bar
    if bar is not None:
        bar.place(x=25, y=576, height=10)


# removing the bar
def dispose():
    global bar
    if bar is not None:
        bar.destroy()
    bar = None
