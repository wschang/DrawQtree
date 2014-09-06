#! /usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2014 Wen Shan Chang
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


#
# Class used to draw the quadtree. This was clobbered together to draw the quadtree and is
# fairly 'hacky'.
#

__author__ = 'Chang'

import time
import Queue
from Tkinter import Tk, Canvas, Button, Label, StringVar, NW, SE, FLAT


class DisplayQuadTree(object):
    def __init__(self, width, height, scale=1, show_grid=False):
        self._scale = scale
        self._grid_width = 1 if show_grid else 0
        self.size = (width*scale, height*scale)
        self._is_animate = False
        self._anime_time = 0.1

        self._tk_root = Tk()
        self._canvas = Canvas(self._tk_root, width=self.size[0], height=self.size[1])
        self._canvas.pack()

        self._button = Button(self._tk_root, text='Finished', command=self._stop_animate)
        self._button.configure(width=10, relief=FLAT)
        self._canvas.create_window(10, 10, anchor=NW, window=self._button)

        self._labelstr = StringVar()
        self._labelstr.set('0%')
        self._label = Label(self._tk_root, textvariable=self._labelstr)
        self._canvas.create_window(self.size[0] - 10,
                                   self.size[1] - 10,
                                   anchor=SE,
                                   window=self._label)

    def static(self, qtree):
        """ Draw the final output.
        """
        if qtree is None:
            return

        stack = [qtree]
        while len(stack):
            qnode = stack.pop()
            if qnode.children:
                for child in qnode.children:
                    stack.append(child)
            else:
                colour = '#{0:02x}{1:02x}{2:02x}'.format(*qnode.ave_color)
                self._canvas.create_rectangle(qnode.x * self._scale,
                                              qnode.y * self._scale,
                                              (qnode.x + qnode.width) * self._scale,
                                              (qnode.y + qnode.height) * self._scale,
                                              width=self._grid_width,
                                              outline='grey',
                                              fill=colour)
        self._labelstr.set('100%')

    def _stop_animate(self):
        """ Stop the animation. Called by the "Stop" button
        """
        self._is_animate = False
        self._button.configure(text='Finished')

    def animate(self, qtree):
        """ Animate the development of the quadtree as it was generated.
        Press the "Stop" to stop the animation
        """
        if qtree is None:
            return

        self._is_animate = True
        self._button.configure(text='Stop')

        q = Queue.Queue()
        q.put(qtree)
        count, max_qtrees = 0.0, qtree.sq_num
        while not q.empty() and self._is_animate:
            qnode = q.get()

            if qnode.children:
                for child in qnode.children:
                    q.put(child)

            count += 1.0
            colour = '#{0:02x}{1:02x}{2:02x}'.format(*qnode.ave_color)
            self._canvas.create_rectangle(qnode.x * self._scale,
                                          qnode.y * self._scale,
                                          (qnode.x + qnode.width) * self._scale,
                                          (qnode.y + qnode.height) * self._scale,
                                          width=self._grid_width,
                                          outline='grey',
                                          fill=colour)
            self._canvas.update()
            self._labelstr.set('{}%'.format(int(count/max_qtrees * 100)))
            time.sleep(self._anime_time)

        self._stop_animate()

    def show(self):
        """ Call this to start the display.
        """
        self._tk_root.mainloop()
