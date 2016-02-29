#!/usr/bin/env python
"""Usage: git-external-pull-mv [--sub-repo <origrepo>,<subrepo>]

Go through the branch dependency file (for the current limb) and pull
all external repositories.  This script expects external repositories
to be in the form:

#git://<repo> <extern branch>
external.<branch>:

or

#https://<repo> <extern branch>
external.<branch>:

and it will pull https://<repo> <extern branch> into fetch head and
merge it (fast-forward only) into external.<branch>.  Any error
terminates the script.

        [opts]
        --sub-repo <origrepo>,<subrepo>
                If a repository being pulled starts with <origrepo>,
                then substitute <subrepo> for <origrepo>.  This allow
                git forwarding to external repositories.

"""

import sys
import getopt
import mvgitlib as git

def extern_branch(s):
    """If the string is in the form '^external.<str>:' return the
    string without the final colon, otherwise return None.
    """
    if s.startswith("external.") and s.endswith(":"):
        return s[:-1]
    return None

def get_source(s):
    """If the line is in one of the following forms:
    #git://repo branch
    #https://repo branch
    then return a vector with the full repo and branch, otherwise
    return None.
    """
    if not s.startswith("#"):
        return None
    v = s[1:].strip().split()
    if len(v) != 2:
        return None
    if not (v[0].startswith("git://") or v[0].startswith("https://")):
        return None
    return v

def git_call_with_err(cmd, errstart):
    try:
        strout = git.call(cmd)
    except git.GitError, e:
        sys.stderr.write(errstart + ": " + e.msg + "\n")
        sys.exit(1)
    return strout

def usage(msg=None):
    """
    Print a usage message and exit with an error code
    """

    if msg:
	sys.stderr.write("%s\n" % str(msg).rstrip())

    sys.stderr.write("\n%s\n" % __doc__.strip())
    sys.exit(1)

def process_options():
    short_opts = "h"
    long_opts = [ "help", "version", "sub-repo=" ]

    try:
        options, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)

    except getopt.GetoptError, err:
        usage(err)

    for option, value in options:
        if option == "--help" or option == "-h":
	    usage()
	elif option == '--version':
	    sys.stdout.write('mvgit version %s\n' % "@@MVGIT_VERSION@@")
	    sys.exit(0)
	elif option == "--sub-repo":
            s = value.split(",")
            if len(s) != 2:
                sys.stderr.write("Invalid sub-repo value: " + value + "\n")
                sys.exit(1)
            sub_repos.append(s)
        else:
            sys.stderr.write("Unknown option: " + option + "\n")
            sys.exit(1)
    
    return

sub_repos = []

def do_sub_repos(r):
    for v in sub_repos:
        if r[0].startswith(v[0]):
            r[0] = r[0].replace(v[0], v[1], 1)
            break

    return r

process_options()

limb = git.current_limb()

depfile = git_call_with_err(['git', 'show',
                            limb.name + "/limb-info:MONTAVISTA/branch_dependencies" ],
                           "Error opening branch dependency file for " + limb.name)

deplines = depfile.split("\n")
for i in range(1, len(deplines)):
    branch = extern_branch(deplines[i])
    if branch is None:
        continue
    src = get_source(deplines[i - 1])
    if src is None:
        continue
    branch = limb.name + "/" + branch

    # If we get here we have an external branch.

    git_call_with_err(["git", "checkout", branch],
                      "Could not check out " + branch)

    src = do_sub_repos(src)
    
    git_call_with_err(["git", "fetch", src[0], src[1]],
                      "Could not pull " + src[0] + " " + src[1])

    git_call_with_err(["git", "merge", "--ff-only", "FETCH_HEAD"],
                      "Could not merge " + src[0] + " " + src[1])
