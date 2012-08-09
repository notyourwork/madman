#!/bin/bash
#FInd all files that share 10 characters together, not 100% accurate
if [ $# -gt 0 ]
then
	ls $1 | sort | uniq --check-chars=10 -d | less
else
	echo "Usage instructions: $0 </path/to/files/>";
	exit 1;
fi
exit 0
