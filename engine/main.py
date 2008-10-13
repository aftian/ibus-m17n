# vim:set et sts=4 sw=4:
# -*- coding: utf-8 -*-
#
# ibus-anthy - The Anthy engine for IBus
#
# Copyright (c) 2007-2008 Huang Peng <shawn.p.huang@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import sys
import getopt
import m17n
import ibus
import factory
import gobject

N_ = lambda x: x
N_("Hello")

class IMApp:
    def __init__(self, methods):
        self.__mainloop = gobject.MainLoop()
        self.__bus = ibus.Bus()
        self.__bus.connect("destroy", self.__bus_destroy_cb)

        self.__methods = []
        self.__factories = []
        for lang, name in methods:
            try:
                f = factory.EngineFactory(lang, name, self.__bus)
                self.__factories.append(f)
            except Exception, e:
                print e
        if self.__factories:
            self.__bus.register_factories(map(lambda f: f.get_object_path(), self.__factories))

    def run(self):
        self.__mainloop.run()

    def __bus_destroy_cb(self, bus):
        self.__mainloop.quit()


def launch_engine(methods):
    IMApp(methods).run()

def print_help(out, v = 0):
    print >> out, "./ibus-engine-m17n [options] [engines]"
    print >> out, "\t-h, --help             show this message."
    print >> out, "\t-d, --daemonize        daemonize ibus engine"
    print >> out, "\t-l, --list             list all m17n input methods"
    print >> out, "\t-a, --all              enable all m17n input methods"
    print >> out, "example:"
    print >> out, "\t./ibus-engine-m17n zh:py ja:trycode"
    print >> out, "\t./ibus-engine-m17n zh:py,pinyin hi:inscript"
    print >> out, "\t./ibus-engine-m17n -a"
    sys.exit(v)

def list_m17n_ims():
    print "list all m17n input methods:"
    print "\tlang\tname -- title"
    for name, lang in m17n.minput_list_ims():
        print "\t%s\t%s -- %s" % (lang, name, m17n.minput_get_title(lang, name))
    sys.exit(0)

def main():
    daemonize = False
    shortopt = "hdla"
    longopt = ["help", "daemonize", "list", "all"]
    all_methods = False
    methods = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopt, longopt)
    except getopt.GetoptError, err:
        print_help(sys.stderr, 1)

    for o, a in opts:
        if o in ("-h", "--help"):
            print_help(sys.stdout)
        elif o in ("-d", "--daemonize"):
            daemonize = True
        elif o in ("-l", "--list"):
            list_m17n_ims()
        elif o in ("-a", "--all"):
            all_methods = True
        else:
            print >> sys.stderr, "Unknown argument: %s" % o
            print_help(sys.stderr, 1)

    if daemonize:
        if os.fork():
            sys.exit()
    if all_methods:
        methods = map(lambda im:(im[1], im[0]), m17n.minput_list_ims())
    else:
        for m in args:
            lang, names = m.split(":")
            for name in names.split(","):
                methods.append((lang, name))

    launch_engine(methods)

if __name__ == "__main__":
    main()
