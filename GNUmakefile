.PHONY: all maps conf mobxp mobxp-impl indent indent-items indent-mobs news updates
# Can't be parallel due to the mobxp/indent-mobs conflict
.NOTPARALLEL:
all: maps conf news updates
maps:
	tools/tmx_converter.py client-data/ world/map/

% : | %.example
	cp "$|" "$@"
conf: world/map/conf/magic-secrets.sex \
login/conf/login_local.conf login/conf/ladmin_local.conf login/save/gm_account.txt login/save/account.txt \
world/conf/char_local.conf \
world/map/conf/map_local.conf world/map/conf/battle_local.conf world/map/conf/atcommand_local.conf world/map/db/const-debugflag.txt \
world/map/npc/functions/motd.txt

world/map/conf/magic-secrets.sex: world/map/conf/magic-secrets.sex.template world/map/conf/secrets-build
	cd world/map/conf && ./build-magic.sh
world/map/conf/secrets-build:

mobxp: mobxp-impl indent-mobs
mobxp-impl:
	mv world/map/db/mob_db.txt world/map/db/mob_db.old
	tools/mobxp < world/map/db/mob_db.old > world/map/db/mob_db.txt
	rm world/map/db/mob_db.old
indent: indent-mobs indent-items
indent-items: tools/aligncsv
	tools/aligncsv world/map/db/item_db.txt
indent-mobs: tools/aligncsv
	tools/aligncsv world/map/db/mob_db.txt

world/map/news.txt world/map/news.html: tools/news.py tools/_news_colors.py world/map/news.d/* world/map/news.d/
	tools/news.py world/map/ world/map/news.d/
	chmod a+r world/map/news.txt world/map/news.html

news: world/map/news.txt world/map/news.html
updates:
	cd client-data && tools/make-updates
