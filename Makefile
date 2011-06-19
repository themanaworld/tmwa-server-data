.PHONY: maps
maps:
	ant -f tools/tmwcon/build.xml
	java -jar tools/tmwcon/converter.jar client-data/ world/map/
