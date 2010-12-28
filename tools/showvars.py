#!/usr/bin/python


# must be started in the npc dir

import os
import re
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
                  help="show the occurrences of that var", metavar="FILE")

(options, args) = parser.parse_args()

def handleFile(fname):
	f = open(fname)
	lines = f.readlines();
	f.close()
	for l in lines:
		#remove comments
		line = l.split(r"//")[0]

		sp = line.split()

		# no set command?
		if not "set" in sp:
			continue

		# ignore those lines printing messages
		if 'mes "' in line:
			continue

		#ignore anything before the "set" command:
		sp = sp[sp.index("set")+1:]
		line = "".join(sp)
		endpos = line.find(",")

		#check for comma
		if endpos>0:
			#ok its a oneliner, the comma is in the same line:
			varname = line[0:endpos].strip()
			if varname.startswith("@"):
				continue
			if varname.startswith("$"):
				continue
			if varname in allvars:
				if not fname in allvars[varname]:
					allvars[varname] += [fname]
			else:
				allvars[varname] = [fname]
		else:
			# ok error, you need to check manually:
			print "\tline:\t",line

allvars = {}

print "please check manully for vars in here:"
os.chdir(".."+os.sep+"npc")
for tpl in os.walk("."):
	for fname in tpl[2]:
		handleFile(tpl[0]+os.sep+fname)

# now check if the variable is not in npc/functions/clear_vars.txt, if so remove it
checkstring = "." + os.sep + "functions" + os.sep + "clear_vars.txt"
rm = []
for var in allvars:
	if checkstring in allvars[var]:
		rm += [var]

#now really remove these vars
for var in rm:
	del allvars[var]

print "These variables are valid variables of the scripts:"
for var in allvars:
	print "\t",var
	if options.verbose:
		for fname in allvars[var]:
			print "\t","\t", fname

print "number of vars:", len(allvars)
