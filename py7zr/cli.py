#!/usr/bin/env python
#
#    Pure python p7zr implementation
#    Copyright (C) 2019 Hiroshi Miura
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
from __future__ import absolute_import

import argparse
import os
import sys

import py7zr
import texttable

from py7zr.properties import SupportedMethods

try:
    import lzma
except ImportError:
    from backports import lzma


class Cli():
    def __init__(self):
        parser = argparse.ArgumentParser(prog='py7zr', description='py7zr',
                                         formatter_class=argparse.RawTextHelpFormatter, add_help=True)
        subparsers = parser.add_subparsers(title='subcommands', help='subcommand for py7zr l .. list, x .. extract,'
                                                                     ' t .. check integrity, i .. information')
        list_parser = subparsers.add_parser('l')
        list_parser.set_defaults(func=self.run_list)
        list_parser.add_argument("arcfile", help="7z archive file")
        extract_parser = subparsers.add_parser('x')
        extract_parser.set_defaults(func=self.run_extract)
        extract_parser.add_argument("arcfile", help="7z archive file")
        extract_parser.add_argument("odir", nargs="?", help="output directory")
        create_parser = subparsers.add_parser('c')
        create_parser.set_defaults(func=self.run_create)
        create_parser.add_argument("arcfile", help="7z archive file")
        create_parser.add_argument("filenames", nargs="*", help="filenames to archive")
        test_parser = subparsers.add_parser('t')
        test_parser.set_defaults(func=self.run_test)
        test_parser.add_argument("arcfile", help="7z archive file")
        info_parser = subparsers.add_parser("i")
        info_parser.set_defaults(func=self.run_info)
        parser.set_defaults(func=self.show_help)
        self.parser = parser

    def show_help(self, args):
        self.parser.print_help()
        return(0)

    def run(self, arg=None):
        args = self.parser.parse_args(arg)
        return args.func(args)

    def run_info(self, args):
        print("py7zr version {} {}".format(py7zr.__version__, py7zr.__copyright__))
        print("Formats:")
        table = texttable.Texttable()
        table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_dtype(['t', 't'])
        table.set_cols_align(["l", "r"])
        for f in SupportedMethods.formats:
            if sys.version_info.major > 2:
                m = ''.join(' {:02x}'.format(x) for x in f['magic'])
            else:
                m = ''.join(' {:02x}'.format(ord(x)) for x in f['magic'])
            table.add_row([f['name'], m])
        print(table.draw())
        print("\nCodecs:")
        table = texttable.Texttable()
        table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_dtype(['t', 't'])
        table.set_cols_align(["l", "r"])
        for c in SupportedMethods.codecs:
            if sys.version_info.major > 2:
                m = ''.join('{:02x}'.format(x) for x in c['id'])
            else:
                m = ''.join('{:02x}'.format(ord(x)) for x in c['id'])
            table.add_row([m, c['name']])
        print(table.draw())
        print("\nChecks:")
        print("CHECK_NONE")
        print("CHECK_CRC32")
        if lzma.is_check_supported(lzma.CHECK_CRC64):
            print("CHECK_CRC64")
        if lzma.is_check_supported(lzma.CHECK_SHA256):
            print("CHECK_SHA256")

    def run_list(self, args):
        target = args.arcfile
        if not py7zr.is_7zfile(target):
            print('not a 7z file')
            return(1)
        with open(target, 'rb') as f:
            a = py7zr.SevenZipFile(f)
            a.list()
        return(0)

    def run_test(self, args):
        target = args.arcfile
        if not py7zr.is_7zfile(target):
            print('not a 7z file')
            return(1)
        with open(target, 'rb') as f:
            a = py7zr.SevenZipFile(f)
            res = a.test()
        if res:
            return(0)
        else:
            return(1)

    def run_extract(self, args):
        target = args.arcfile
        if not py7zr.is_7zfile(target):
            print('not a 7z file')
            return(1)

        with open(target, 'rb') as f:
            a = py7zr.SevenZipFile(f)
            if args.odir:
                a.extractall(path=args.odir)
            else:
                a.extractall()
        return(0)

    def run_create(self, args):
        sztarget = args.arcfile
        with py7zr.SevenZipFile(sztarget, 'w') as szf:
            for path in args.filenames:
                zippath = os.path.basename(path)
                if not zippath:
                    zippath = os.path.basename(os.path.dirname(path))
                if zippath in ('', os.curdir, os.pardir):
                    zippath = ''
                szf.writeall(path, zippath)
        return(0)


def main():
    cli = Cli()
    return cli.run()
