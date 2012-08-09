#!/bin/bash

#
#Setup
#Prepare source filename file, should look like
#How.I.Met.Your.Mother.S06E01.HDTV.XviD-LOL.avi*175.02-MB
#It splits on the * so as long as the first part is correct thats all that matters
#
#Does not handle shows inside  folder currently
#


if [ $# -gt 2 ]
then
	TMPFILE=$1
	TMPFILE2=$1"2"
	SOURCEDIR=$2
	DESTDIR=$3
	cut -d* -f1 $TMPFILE > $TMPFILE2
	for i in `cat $TMPFILE2`
	do
		touch "$DESTDIR$i"
	done
	if [ -f "`which mytvrenamer`" ]
	then
		mytvrenamer "$SOURCEDIR"
		for j in $(echo "$SOURCEDIR"* | egrep -o '[[:digit:]]{2}');
		do
			ln -sfn "$SOURCEDIR$j"* "$DESTDIR"*$j*
		done
	else
		echo "Download mytvrenamer"
	fi
else
	echo "fail"
	echo "Usage instructions: $0 <file with filenames for episodes> <source folder, include last /> <dest folder, include last />";
	exit 1;
fi
