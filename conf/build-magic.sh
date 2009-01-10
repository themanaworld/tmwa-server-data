#! /bin/sh

RSCRIPT="spells-build.sh"

if [ -a $RSCRIPT ]; then printf ""; else
    echo '#! /bin/sh' > $RSCRIPT;
    echo 'cat \' >> $RSCRIPT;
    chmod a+x $RSCRIPT
fi

for n in `grep -o '"#..."' magic.conf.template`; do
    if grep $n $RSCRIPT; then printf ""; else
        CHANGES=1
        echo "|sed 's/${n}/${n}/' \\" >> $RSCRIPT;
    fi
done

if [ x$CHANGES == x1 ]
then echo "spells-build.sh has been updated; please provide invocations for spells and/or teleport anchors.";
else cat magic.conf.template | ./$RSCRIPT > magic.conf;
fi