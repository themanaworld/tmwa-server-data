#!/usr/bin/python


# must be started in the npc dir

import os
import re
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
                  help="show the occurrences of that var")

parser.add_option("-f", "--file", dest="fname", default="",
                  help="inspect that file", metavar="FILE")

parser.add_option("-l", "--localvariables", dest="localvars", action="store_true", default=False,
                  help="show local variables as well")

(options, args) = parser.parse_args()

def handleFile(fname):
	f = open(fname)
	lines = f.readlines();
	f.close()
	rm=[]
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
			assignment = line[endpos+1:].strip()[:-1] # remove semicolon
			if assignment != "0":
				if varname.startswith("@") and not options.localvars:
					continue
				if varname.startswith("$"):
					continue
				if varname in allvars:
					if not fname in allvars[varname]:
						allvars[varname] += [fname]
				else:
					allvars[varname] = [fname]
			else:
				#print fname
				if fname == "." + os.sep + "functions" + os.sep + "clear_vars.txt":
					rm += [varname]

		else:
			# ok error, you need to check manually:
			print "\tline:\t",line
	return rm

if options.fname:
	path=options.fname
else:
	path=".."+os.sep+"npc"

allvars = {}
rmvars = []
print "please check manully for vars in here:"
os.chdir(path)

for tpl in os.walk("."):
	for fname in tpl[2]:
		rmvars += handleFile(tpl[0]+os.sep+fname)

unusedcounter=0
usedcounter=0
print "These variables are found in the scripts, which are deleted in clear_vars"
for var in allvars:
	if not var in rmvars:
		continue

	unusedcounter+=1
	print "\t",var
	if options.verbose:
		for fname in allvars[var]:
			print "\t","\t", fname


print "These variables are valid variables of the scripts:"
for var in allvars:
	if var in rmvars:
		continue

	usedcounter+=1
	print "\t",var
	if options.verbose:
		for fname in allvars[var]:
			print "\t","\t", fname

print "number of vars used:", usedcounter
print "number of vars cleared:", unusedcounter
