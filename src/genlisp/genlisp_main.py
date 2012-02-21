from __future__ import print_function

from optparse import OptionParser

import os
import sys
import traceback
import genmsg
import genmsg.command_line

from genmsg import MsgGenerationException
from . generate import generate_msg, generate_msg_asd, generate_srv, generate_srv_asd

def usage(progname):
    print("%(progname)s file(s)"%vars())

def fix_search_path(search_path):
    """Removes invalid entries from search_path."""
    result = {}
    for package, path in search_path.iteritems():
        if path != '':
            result[package] = path
    return result
        
def genmain(argv, progname):
    parser = OptionParser("%s file"%(progname))
    parser.add_option('--msg-asd', dest='msg_asd', action='store_true',
                      default=False)
    parser.add_option('--srv-asd', dest='srv_asd', action='store_true',
                      default=False)
    parser.add_option('-p', dest='package')
    parser.add_option('-o', dest='outdir')
    parser.add_option('-I', dest='includepath', action='append', default=[])
    options, args = parser.parse_args(argv)
    try:
        if len(args) < 2:
            parser.error("please specify args")
        if not os.path.exists(options.outdir):
            # This script can be run multiple times in parallel. We
            # don't mind if the makedirs call fails because somebody
            # else snuck in and created the directory before us.
            try:
                os.makedirs(options.outdir)
            except OSError as e:
                if not os.path.exists(options.outdir):
                    raise
        search_path = fix_search_path(genmsg.command_line.includepath_to_dict(options.includepath))
        filename = args[1]
        if options.msg_asd:
            retcode = generate_msg_asd(options.package, args[1:], options.outdir, search_path)
        elif options.srv_asd:
            retcode = generate_srv_asd(options.package, args[1:], options.outdir, search_path)
        elif filename.endswith('.msg'):
            retcode = generate_msg(options.package, args[1:], options.outdir, search_path)
        else:
            retcode = generate_srv(options.package, args[1:], options.outdir, search_path)
    except genmsg.InvalidMsgSpec as e:
        print("ERROR: ", e, file=sys.stderr)
        retcode = 1
    except MsgGenerationException as e:
        print("ERROR: ", e, file=sys.stderr)
        retcode = 2
    except Exception as e:
        traceback.print_exc()
        print("ERROR: ",e)
        retcode = 3
    sys.exit(retcode or 0)
