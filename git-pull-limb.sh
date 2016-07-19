#!/bin/sh -e

if [ "x$*" != "x" ]; then
	echo "Do a get fetch on origin an merge all branches in the limb."
	echo "This program takes no parameters.  If any merge fails to"
	echo "fast forward, or any other problem occurs, the program will"
	echo "stop immediately."
	exit 1
fi

LIMB_LIST=`git limb | sed 's/^[^ ][^ ]*//'`
if [ "x$LIMB_LIST" = "x" ]; then
	echo "Problem listing the limb, are you on a limb?" >&2
	exit 1
fi

CURR_BRANCH=`git limb | grep '^[*]' | sed 's/[*]//'`
if [ "x$CURR_BRANCH" = "x" ]; then
	echo "Unable to find the current branch on the limb" >&2
	exit 1
fi

git fetch

for i in $LIMB_LIST; do
	git checkout $i
	git merge --ff-only origin/$i
done

git checkout $CURR_BRANCH