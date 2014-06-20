#!/bin/sh

CURR_DIR=`pwd`

for FN in `find $CURR_DIR -maxdepth 1 -type f -size +1024k -name "*.md"`
do
	fn=$(basename $FN)
	name="${fn%.*}"
	echo $fn $name
	split -l 4000 -a 1 -d $fn "${name}_" --filter='cat > $FILE.md'
	rm $fn
done

