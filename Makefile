.PHONY: all maps conf
all: maps conf
maps:
	ant -f tools/tmwcon/build.xml
	java -jar tools/tmwcon/converter.jar client-data/ world/map/
% : | %.example
	cp "$|" "$@"
conf: \
login/conf/login_local.conf login/conf/ladmin_local.conf login/save/gm_account.txt login/save/account.txt \
world/map/conf/map_local.conf world/map/conf/battle_local.conf world/map/conf/motd.txt world/map/conf/help.txt world/map/conf/atcommand_local.conf \
world/conf/char_local.conf

mobxp:
	tools/mobxp < world/map/db/mob_db.txt  | tools/aligncsv.py /dev/stdin world/map/db/mob_db.txt
	sed 's/[[:space:]]*$$//' -i world/map/db/mob_db.txt
