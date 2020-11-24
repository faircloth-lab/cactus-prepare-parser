#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(c) 2020 Brant Faircloth || http://faircloth-lab.org/

All rights reserved.

This code is distributed under a 3-clause BSD license. Please see
LICENSE.txt for more information.

Created on 24 November 2020 10:55 CST (-0600)
"""

import os
import pdb
import shlex
import shutil
import argparse
from collections import defaultdict
from itertools import zip_longest


class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


class CreateDir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # get the full path
        d = os.path.abspath(os.path.expanduser(values))
        # check to see if directory exists
        if os.path.exists(d):
            answer = input("[WARNING] Output directory exists, REMOVE [Y/n]? ")
            if answer == "Y":
                shutil.rmtree(d)
            else:
                print("[QUIT]")
                sys.exit()
        # create the new directory
        os.makedirs(d)
        # return the full path
        setattr(namespace, self.dest, d)

def is_file(filename):
    if not os.path.isfile:
        msg = "{0} is not a file".format(filename)
        raise argparse.ArgumentTypeError(msg)
    else:
        return filename


def get_args():
    parser = argparse.ArgumentParser(
        description="""Parse a cactus-prepared stdout file""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--cactus-prepare',
        required=True,
        type=is_file,
        action=FullPaths,
        help="""The file containing cactus-prepare stdout."""
    )
    parser.add_argument(
        '--output-dir',
        required=True,
        action=CreateDir,
        help="""The directory in which to store the resulting alignments."""
    )
    return parser.parse_args()

def group(n, iterable, fillvalue=None): 
    args = [iter(iterable)] * n 
    z=  zip_longest(fillvalue=fillvalue, *args)
    return [i for i in z]

def main():
    args = get_args()
    pre = []
    aln = defaultdict(list)
    hal = []
    with open(args.cactus_prepare) as infile:
        stage, rnd = None, None
        for line in infile:
            ls = line.strip()
            if ls == "## Preprocessor":
                stage = "pre"
                rnd = ""
            elif ls == "## Alignment":
                stage = "aln"
            elif stage == "aln" and ls.startswith("### Round"):
                rnd = ls.lstrip("### Round ")
            elif ls == "## HAL merging":
                stage = "hal"
                rnd = ""
            if stage == "pre" and ls != "## Preprocessor" and ls != "":
                pre.append(ls)
            elif stage == "aln" and not ls.startswith("## Alignment") and not ls.startswith("### Round") and ls != "":
                aln[rnd].append(ls)
            elif stage == "hal" and ls != "## HAL merging" and ls!= "":
                hal.append(ls)
        # pre-process files
        pre_process_dir = os.path.join(args.output_dir, "pre-process")
        os.makedirs(pre_process_dir)
        for item in pre:
            header_template = open('align_header.txt').read()
            cli = shlex.split(item)
            name = cli[cli.index("--inputNames") + 1]
            name2 = "{}_preprocess".format(name)
            header = header_template.format(name2)
            output_file = "prep-{}.slurm".format(name2)
            with open(os.path.join(pre_process_dir, output_file), 'w') as outfile:
                    outfile.write(header)
                    outfile.write("""$SING {} &&\n""".format(item))
                    outfile.write("date &&\nexit 0\n")
        # alignment files
        alignment_dir = os.path.join(args.output_dir, "alignment")
        os.makedirs(alignment_dir)
        new_items = {}
        for k,v in aln.items():
            new_items[k] = group(3, v)
        for rnd, command_sets in new_items.items():
            for command_set in command_sets:
                header_template = open('align_header.txt').read()
                cli = shlex.split(command_set[0])
                name = cli[cli.index("--root") + 1]
                header = header_template.format(name)
                output_file = "Round-{}_{}.slurm".format(rnd, name)
                with open(os.path.join(alignment_dir, output_file), 'w') as outfile:
                    outfile.write(header)
                    outfile.write("""$SING {} &&\necho "BLAST DONE" &&\n""".format(command_set[0]))
                    outfile.write("""$SING {} &&\necho "ALIGN DONE" &&\n""".format(command_set[1]))
                    outfile.write("""$SING {} &&\necho "HAL2FASTA DONE" &&\n""".format(command_set[2]))
                    outfile.write("date &&\nexit 0\n")
        # hal merging
        hal_dir = os.path.join(args.output_dir, "hal")
        os.makedirs(hal_dir)
        header_template = open('align_header.txt').read()
        cli = shlex.split(item)
        name = "hal-merge".format(name)
        header = header_template.format(name)
        output_file = "hal-merge.slurm"
        with open(os.path.join(hal_dir, output_file), 'w') as outfile:
                outfile.write(header)
                for item in hal:
                    outfile.write("""$SING {} &&\n""".format(item))
                outfile.write("date &&\nexit 0\n")



            



if __name__ == '__main__':
	main()