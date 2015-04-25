# Can't be parallel due to the mobxp/indent-mobs conflict
.NOTPARALLEL:
.PHONY: all
all: maps conf news updates
.PHONY: maps
maps: quests
	tools/tmx_converter.py client-data/ world/map/

% : | %.example
	cp "$|" "$@"
.PHONY: conf
conf: world/map/conf/magic-secrets.sex \
login/conf/login_local.conf login/conf/ladmin_local.conf login/save/gm_account.txt login/save/account.txt \
world/conf/char_local.conf \
world/map/conf/map_local.conf world/map/conf/battle_local.conf world/map/conf/motd.txt world/map/conf/atcommand_local.conf world/map/db/const-debugflag.txt \
conf/monitor_local.conf

world/map/conf/magic-secrets.sex: world/map/conf/magic-secrets.sex.template world/map/conf/secrets-build
	cd world/map/conf && ./build-magic.sh
world/map/conf/secrets-build:

.PHONY: mobxp mobxp-impl
mobxp: mobxp-impl indent-mobs
mobxp-impl:
	mv world/map/db/mob_db.txt world/map/db/mob_db.old
	tools/mobxp < world/map/db/mob_db.old > world/map/db/mob_db.txt
	rm world/map/db/mob_db.old
.PHONY: indent indent-items indent-mobs
indent: indent-mobs indent-items
indent-items: tools/aligncsv
	tools/aligncsv world/map/db/item_db.txt
indent-mobs: tools/aligncsv
	tools/aligncsv world/map/db/mob_db.txt

world/map/news.txt world/map/news.html: tools/news.py tools/_news_colors.py world/map/news.d/* world/map/news.d/
	tools/news.py world/map/ world/map/news.d/
	chmod a+r world/map/news.txt world/map/news.html

.PHONY: news
news: world/map/news.txt world/map/news.html
.PHONY: updates
updates:
	cd client-data && tools/make-updates
.PHONY: quests
quests: world/map/npc/functions/quest-log.txt
world/map/npc/functions/quest-log.txt: world/map/db/quest-log.py
	$< world/map/npc/variables.conf > $@
