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
# Contain the QuadTree implementation as well as the helper class ImgBuffRgb
#

__author__ = 'Chang'


class ImgBuffRgb(object):
    """ Represents the raw buffer extracted from the image.

    Attributes:
        height : height of image
        width : width of image
        buff : list of pixels of size width *height. Each pixel is a tuple of (R, G, B) value
    """
    def __init__(self, buff, width, height):
        """ ctor
        :param buff: list of pixels of size width *height. Each pixel must be a tuple of
                     (R, G, B) value
        :param width: width of image
        :param height: height of image
        """
        self.height = height
        self.width = width
        self._buff = buff

    def calc_stats_est(self, x_offset, y_offset, w, h):
        """ Calculate the average colour and variance for a particular sub-block in the buffer.
        Thw variance is an estimation but it is faster to generate.

        :param x_offset: x-offset to the start of the sub-block
        :param y_offset: y-offset to the start of the sub-block
        :param w: width of sub-block
        :param h: height of sub-block
        :return: two tuples representing the average colour and variance. Each tuple
                represents (R, G, B)
        """
        # calculate average value and variance in one shot
        av_r, av_g, av_b = 0, 0, 0
        var_r, var_g, var_b = 0, 0, 0
        for y in xrange(y_offset, y_offset + h):
            for x in xrange(x_offset, x_offset + w):
                px = self._buff[y * self.width + x]
                av_r, av_g, av_b = av_r + px[0], av_g + px[1], av_b + px[2]
                var_r, var_g, var_b = var_r + px[0]**2, var_g + px[1]**2, var_b + px[2]**2

        px_num = w * h if (w * h) else 1
        av_r, av_g, av_b = av_r/px_num, av_g/px_num, av_b/px_num

        var_r = var_r/px_num - av_r**2
        var_g = var_g/px_num - av_g**2
        var_b = var_b/px_num - av_b**2

        return (av_r, av_g, av_b), (var_r, var_g, var_b)

    def calc_stats_acc(self, x_offset, y_offset, w, h):
        """ Calculate the average colour and variance for a particular sub-block in the buffer

        :param x_offset: x-offset to the start of the sub-block
        :param y_offset: y-offset to the start of the sub-block
        :param w: width of sub-block
        :param h: height of sub-block
        :return: two tuples representing the average colour and variance. Each tuple
                represents (R, G, B)
        """
        # calculate average value
        av_r, av_g, av_b = 0, 0, 0
        for y in xrange(y_offset, y_offset + h):
            for x in xrange(x_offset, x_offset + w):
                px = self._buff[y * self.width + x]
                av_r, av_g, av_b = av_r + px[0], av_g + px[1], av_b + px[2]

        px_num = w * h if (w * h) else 1
        av_r, av_g, av_b = av_r/px_num, av_g/px_num, av_b/px_num

        # calculate variance
        var_r, var_g, var_b = 0, 0, 0
        for y in xrange(y_offset, y_offset + h):
            for x in xrange(x_offset, x_offset + w):
                px = self._buff[y * self.width + x]
                var_r += (px[0] - av_r) ** 2
                var_g += (px[1] - av_g) ** 2
                var_b += (px[2] - av_b) ** 2

        var_r, var_g, var_b = var_r/px_num, var_g/px_num, var_b/px_num

        return (av_r, av_g, av_b), (var_r, var_g, var_b)


class QuadTree(object):
    """ QuadTree representing the image.

    Attributes:
        width: width of sub-block
        height: height of sub-block
        x:  x-offset to the start of the sub-block
        y: y-offset to the start of the sub-block
        children: list of quadtree children
        ave_color:  average colour of this sub-block
        _tolerance: tolerance used to determine if sub-block whould be divided further.

        sq_num: static counter to track number of quadtrees generated
    """
    sq_num = 0

    def __init__(self, tolerance):
        """ ctor

        :param tolerance: tolerance used to determine if sub-block whould be divided further.
        """
        self.width = -1
        self.height = -1
        self.x = -1
        self.y = -1
        self.children = []
        self.ave_color = None
        self._tolerance = tolerance
        QuadTree.sq_num += 1

    def process_img(self, img_buff, x, y, width, height):
        """ Process the image and generate the quad-trees.

        This is a recursive call.

        :param img_buff: ImgBufferRgb object
        :param x: x-offset to the start of the sub-block
        :param y: y-offset to the start of the sub-block
        :param width: width of sub-block
        :param height: height of sub-block
        """
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.ave_color, var = img_buff.calc_stats_acc(x, y, width, height)

        if sum(var) <= self._tolerance:
            return

        top_width, top_height = width / 2, height / 2
        low_width, low_height = width - top_width, height - top_height

        q1, q2, q3, q4 = [QuadTree(self._tolerance) for _ in xrange(4)]
        q1.process_img(img_buff, x, y, top_width, top_height)
        q2.process_img(img_buff, x + top_width, y, top_width, top_height)
        q3.process_img(img_buff, x, y + top_height, low_width, low_height)
        q4.process_img(img_buff, x + top_width, y + top_height, low_width, low_height)
        self.children += [q1, q2, q3, q4]
