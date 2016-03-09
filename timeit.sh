#!/bin/bash
REPEAT=100
END=900

COMMAND="$@"
TIMEFORMAT=%R
MIN="1E10"
function loop {
    VAR=`{ time ./$COMMAND > /dev/null; } 2>&1`
    # echo "Average this loop: $VAR s"
    MIN=`bc <<< "scale=3; if ($VAR<$MIN) $VAR else $MIN"`
}

echo "$COMMAND"
i=0
while (( SECONDS < END )) && (( ++i <= REPEAT)); do
    loop $@
    printf "$i "
done
echo "Fastest out of $i runs: $MIN s"
