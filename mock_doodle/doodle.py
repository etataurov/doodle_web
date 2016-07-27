#!/usr/bin/env python3
#
# Neural Doodle!
# Copyright (c) 2016, Alex J. Champandard.
#
# Research and Development sponsored by the nucl.ai Conference!
#   http://events.nucl.ai/
#   July 18-20, 2016 in Vienna/Austria.
#

import os
import argparse

# Configure all options first so we can custom load other libraries (Theano) based on device specified by user.
parser = argparse.ArgumentParser(description='Generate a new image by applying style onto a content image.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
add_arg = parser.add_argument

add_arg('--content',        default=None, type=str,         help='Content image path as optimization target.')
add_arg('--content-weight', default=10.0, type=float,       help='Weight of content relative to style.')
add_arg('--content-layers', default='4_2', type=str,        help='The layer with which to match content.')
add_arg('--style',          default=None, type=str,         help='Style image path to extract patches.')
add_arg('--style-weight',   default=25.0, type=float,       help='Weight of style relative to content.')
add_arg('--style-layers',   default='3_1,4_1', type=str,    help='The layers to match style patches.')
add_arg('--semantic-ext',   default='_sem.png', type=str,   help='File extension for the semantic maps.')
add_arg('--semantic-weight', default=10.0, type=float,      help='Global weight of semantics vs. features.')
add_arg('--output',         default='output.png', type=str, help='Output image path to save once done.')
add_arg('--output-size',    default=None, type=str,         help='Size of the output image, e.g. 512x512.')
add_arg('--phases',         default=3, type=int,            help='Number of image scales to process in phases.')
add_arg('--slices',         default=2, type=int,            help='Split patches up into this number of batches.')
add_arg('--cache',          default=0, type=int,            help='Whether to compute matches only once.')
add_arg('--smoothness',     default=1E+0, type=float,       help='Weight of image smoothing scheme.')
add_arg('--variety',        default=0.0, type=float,        help='Bias toward selecting diverse patches, e.g. 0.5.')
add_arg('--seed',           default='noise', type=str,      help='Seed image path, "noise" or "content".')
add_arg('--seed-range',     default='16:240', type=str,     help='Random colors chosen in range, e.g. 0:255.')
add_arg('--iterations',     default=100, type=int,          help='Number of iterations to run each resolution.')
add_arg('--device',         default='cpu', type=str,        help='Index of the GPU number to use, for theano.')
add_arg('--print-every',    default=10, type=int,           help='How often to log statistics to stdout.')
add_arg('--save-every',     default=10, type=int,           help='How frequently to save PNG into `frames`.')
args = parser.parse_args()



if __name__ == "__main__":
    basename, _ = os.path.splitext(args.style)
    input_file = basename + args.semantic_ext
    with open(input_file, 'rb') as annotation:
        with open(args.output, 'wb') as output:
            for byte in annotation:
                output.write(byte)
