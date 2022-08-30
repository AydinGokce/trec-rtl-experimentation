from tkinter import *
import redis
import msgpack

class TrajectoryPublisher(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_LINE_WIDTH = 1.0
    DEFAULT_COLOR = 'black'
    REDIS_PUBLISH_CHANNEL = 'trajectory'

    def __init__(self):
        self.root = Tk()
        self.red = redis.Redis(host='localhost', port=6379)

        self.reset_button = Button(self.root, text='reset', command=self.use_reset)
        self.reset_button.grid(row=0, column=0)

        self.c = Canvas(self.root, bg='white', width=600, height=600)
        self.c.grid(row=1, columnspan=1)

        self.setup()
        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.DEFAULT_LINE_WIDTH
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def use_reset(self):
        self.c.delete('all')

    def paint(self, event):
        paint_color = self.DEFAULT_COLOR
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
        data = {
            "command": "track",
            "payload": {
                "x": event.x,
                "y": event.y,
                "xmax": self.c.winfo_width(),
                "ymax": self.c.winfo_height(),
                "xmin": 0,
                "ymin": 0
            }
        }
        self.red.publish("trajectory", msgpack.packb(data))
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None


if __name__ == '__main__':
    TrajectoryPublisher()
