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
# Parse an image and display its quadtree representation. This is the main program used to run
# the entire demo.
#
# Most image formats should be supported, at least .png and .jpg. The images cannot be
# monochrome or contain transparency. It expects the pixels to be RBG and tries to convert
# it if not.
#
# To show the final quadtree representation of the image, e.g.
#   >> python main.py -f/path/to/image -v3000
#
# To view an animation of the quadtree being build,.
#   >> python main.py -f/path/to/image -v3000 -a
#
# Press the "Stop" button to stop the animation before quitting the program.
#

__author__ = 'Chang'

import sys
from contextlib import closing
from PIL import Image
from qtree import QuadTree, ImgBuffRgb
from display_qtree import DisplayQuadTree


def _extract_buffer(img_path):
    """ Read the image file passed in and extract the buffer.

    :param img_path:  path to the image file
    :return: ImgBufferRgb object containing the buffer, None if unsuccessful.
    """
    img_buff = None
    width, height = 0, 0
    try:
        with closing(Image.open(img_path)) as img:
            if img.mode == 'RGB':
                pass
            elif img.mode in ['RGBA', 'CMYK', 'YCbCr']:
                img = img.convert('RGB')
            else:
                print "Error: Unsupport mode {}".format(img.mode)
                return

            width, height = img.size
            img_buff = img.getdata()
            assert len(img_buff) == width * height

    except IOError:
        print "Error: File {} does not exist".format(img_path)
        return None

    return ImgBuffRgb(img_buff, width, height)


def _get_qtree(img_path, tolerance):
    """ Generate a quadtree representing the image

    :param img_path: path to image file.
    :param tolerance: tolerance used to determine if quadtree should be split further
    :return: QuadTree object, None if unsuccessful
    """
    img_buff = _extract_buffer(img_path)
    if not img_buff:
        return None

    q = QuadTree(tolerance)
    q.process_img(img_buff, 0, 0, img_buff.width, img_buff.height)
    return q


def main(img_path, tolerance, scale=1, show_grid=False, is_animate=False):
    """ main program.

    First generate the quadtree from the image, then display it

    :param img_path: path to image file.
    :param tolerance: tolerance used to determine if quadtree should be split further
    :param scale: integer which represent how much to scale the display image by
    :param show_grid: True to display the grid lines for the blocks.
    :param is_animate: True to animate the generation of the quadtree, False to show the
                       final results
    """
    q = _get_qtree(img_path, tolerance)
    if not q:
        return

    print "Number of quadtrees generated: {0}".format(q.sq_num)

    drawing = DisplayQuadTree(q.width, q.height, scale, show_grid)
    if is_animate:
        drawing.animate(q)
    else:
        drawing.static(q)
    drawing.show()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file',
                      action='store',
                      type='string',
                      dest='img_path',
                      help='Path to image to load.')

    parser.add_option('-v', '--var',
                      action='store',
                      type='int',
                      dest='var',
                      help='Maximum variance in colour tolerated. The smaller the value, '
                           'the less "pixelated" the quadtree will appear')

    parser.add_option('-s', '--scale',
                      action='store',
                      type='int',
                      default=1,
                      dest='scale',
                      help='Scale the image. Must be an integer Default is no scaling.')

    parser.add_option('-g', '--show-grid',
                      action='store_true',
                      default=False,
                      dest='is_display_grid',
                      help='Show the grids. Default is not to show.')

    parser.add_option('-a', '--animate',
                      action='store_true',
                      default=False,
                      dest='is_animate',
                      help='Show the splitting of the quadtree in action.'
                           ' Default is to show the final output.')

    options, args = parser.parse_args()

    if options.img_path is None or options.var is None:
        print "Error: Program requires both the image path and variance. Exiting."
        sys.exit(1)

    main(options.img_path,
         options.var,
         options.scale,
         options.is_display_grid,
         options.is_animate)

