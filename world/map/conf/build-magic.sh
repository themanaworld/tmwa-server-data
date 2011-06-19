#! /bin/bash

RSCRIPT="spells-build"

if ! grep -q -s '/bin/sed' $RSCRIPT; then
    echo '#! /bin/sed -f' > $RSCRIPT;
    chmod a+x $RSCRIPT
fi

for n in `grep -o '"#..."' magic.conf.template`; do
    if ! grep -q $n $RSCRIPT; then
        CHANGES=1
        echo "s/${n}/${n}/" >> $RSCRIPT;
    fi
done

if [ x$CHANGES == x1 ]
then echo "${RSCRIPT} has been updated; please provide invocations for spells and/or teleport anchors.";
else ./$RSCRIPT magic.conf.template > magic.conf;
fi
