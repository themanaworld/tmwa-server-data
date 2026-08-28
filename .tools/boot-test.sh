#!/bin/bash
# Boots tmwa-map against this repository's data to catch syntax errors in the
# NPC scripts and the databases. tmwa-map refuses to finish starting up when a
# script fails to parse, so a server that gets as far as talking to the
# char-server has loaded everything without complaints.
#
# Uses the tmwa-map on PATH, or else the container image from docker-compose.yml.
# Set TMWA_DOCKER=1 to use the image even when tmwa-map is installed.

set -u

cd "$(dirname "$0")/.."

image=${IMAGE:-ghcr.io/themanaworld/tmwa:latest}
timeout=${TIMEOUT:-300}
log=$PWD/map-server.log
# Only printed once startup succeeded and the main loop is running.
ready="Attempting to connect to char-server"

# These are normally created by "make conf", which needs make and does more
# than this test needs.
for target in \
    world/map/conf/map_local.conf \
    world/map/conf/battle_local.conf \
    world/map/conf/atcommand_local.conf \
    world/map/conf/permissions_local.txt \
    world/map/db/const-debugflag.txt \
    world/map/npc/functions/motd.txt
do
    [ -e "$target" ] || cp "$target.example" "$target"
done

run_map() {
    # Before doing anything else tmwa checks that it can read the directories
    # it was built to read and write the one it was built to write. Those are
    # absolute paths, and in the container image the writable one is a volume
    # owned by root, so when it is out of reach point tmwa at a scratch copy.
    if [ ! -w /var/tmwa ] && [ -d /etc/tmwa ] && [ -d /usr/share/tmwa ]; then
        TMWA_PORTABLE=$(mktemp -d)
        export TMWA_PORTABLE
        mkdir -p "$TMWA_PORTABLE/etc" "$TMWA_PORTABLE/usr/share" "$TMWA_PORTABLE/var/tmwa"
        ln -s /etc/tmwa "$TMWA_PORTABLE/etc/tmwa"
        ln -s /usr/share/tmwa "$TMWA_PORTABLE/usr/share/tmwa"
    fi
    cd world/map || exit 1
    # stdbuf keeps the output line buffered, so that the marker above turns up
    # as soon as it is printed rather than whenever a 4K block happens to fill.
    exec stdbuf -oL tmwa-map
}

: > "$log"
if [ "${TMWA_DOCKER:-0}" = 0 ] && command -v tmwa-map > /dev/null; then
    run_map > "$log" 2>&1 &
else
    echo "Using $image, since there is no tmwa-map on PATH."
    docker run --rm --name tmwa-boot-test --network none \
        --volume "$PWD:/var/tmwa:rw" --workdir /var/tmwa/world/map \
        --user "$(id -u):$(id -g)" --entrypoint stdbuf \
        "$image" -oL tmwa-map > "$log" 2>&1 &
fi
server=$!

stop() {
    kill "$server" 2> /dev/null
    docker rm -f tmwa-boot-test > /dev/null 2>&1
    wait "$server" 2> /dev/null
}

for _ in $(seq "$timeout"); do
    if grep -q "$ready" "$log"; then
        stop
        echo "The map-server started up fine."
        exit 0
    fi
    # A failed startup exits instead of ever reaching the line above.
    kill -0 "$server" 2> /dev/null || break
    sleep 1
done

stop
echo
echo "The map-server did not start up. Its output, without the progress"
echo "reports (map-server.log has all of it):"
echo
# Keep one progress line either side of anything interesting, since the errors
# themselves do not name the file they came from.
tr '\r' '\n' < "$log" | awk '
    /^[[:space:]]*$/ { next }
    /^(Loading (Maps|NPCs) \[|read db\/)/ {
        if (after) { print "  [" $0 "]"; after = 0 }
        before = $0
        next
    }
    {
        if (before != "") { print "  [" before "]"; before = "" }
        print
        after = 1
    }
'
exit 1
