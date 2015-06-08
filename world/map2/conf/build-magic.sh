#! /bin/bash

OUTPUT=magic-secrets.sex
INPUT=$OUTPUT.template
RSCRIPT=secrets-build

if ! grep -q -s '/bin/sed' $RSCRIPT; then
    echo '#! /bin/sed -f' > $RSCRIPT;
    chmod a+x $RSCRIPT
fi

for n in `grep -o '"#..."' $INPUT`; do
    if ! grep -q $n $RSCRIPT; then
        echo "New secret ${n} needs to be set in $RSCRIPT!"
        echo "s/${n}/${n}/" >> $RSCRIPT;
    fi
done

./$RSCRIPT $INPUT > $OUTPUT
