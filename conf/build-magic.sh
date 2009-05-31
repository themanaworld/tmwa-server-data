#! /bin/bash

RSCRIPT="spells-build"

if [ -a $RSCRIPT ]; then printf ""; else
    echo '#! /bin/bash' > $RSCRIPT;
    echo 'sed \' >> $RSCRIPT;
    chmod a+x $RSCRIPT
fi

for n in `grep -o '"#..."' magic.conf.template`; do
    if grep $n $RSCRIPT; then printf ""; else
        CHANGES=1
        echo "'s/${n}/${n}/;'\\" >> $RSCRIPT;
    fi
done

if [ x$CHANGES == x1 ]
then echo "${RSCRIPT} has been updated; please provide invocations for spells and/or teleport anchors.";
else cat magic.conf.template | ./$RSCRIPT > magic.conf;
fi
