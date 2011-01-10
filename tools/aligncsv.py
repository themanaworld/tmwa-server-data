#!/usr/bin/python
# this formats a csv file to a serious whitespace intended format.

import os
import sys

tabs=True
additionalspaces = 5

fname = sys.argv[1]
if not os.path.exists(fname):
	print "that file doesn't exist"
	exit(0);

f=open(fname,"r");
lines=f.readlines()
f.close();
length=0

for line in lines:
	length=max(length, len(line.split(",")))

print "# number of entries =",length


#setup text array
textarray=range(len(lines)+1)
for x in range(len(lines)+1):
	textarray[x] = range(length)

for x in range(length):
	textarray[-1][x] = 0

#find the longest entry in each line in each position
for lineno in range(len(lines)):
	if not lines[lineno].strip().startswith("//") or lines[lineno].strip().startswith("//id"):
		sp=lines[lineno].split(",")
		for pieceno in range(len(sp)):
			sp[pieceno] = sp[pieceno].strip() + "," #for the comma add a char
			textarray[-1][pieceno] = max(len(sp[pieceno]),textarray[-1][pieceno])

if tabs:
	#make it divisable by 8 (tabs work then)
	for pieceno in range(length):
		if (textarray[-1][pieceno] %8) !=0:
			textarray[-1][pieceno] = (((textarray[-1][pieceno])/8)*8)+8

for lineno in range(len(lines)):
	if not lines[lineno].strip().startswith("//") or lines[lineno].strip().startswith("//id"):
		sp=lines[lineno].split(",")
		for pieceno in range(length):
			textarray[lineno][pieceno] = ""
			if pieceno<len(sp):
				sp[pieceno]= sp[pieceno].strip()
				if pieceno<len(sp)-1:
					sp[pieceno]= sp[pieceno] + ","

				if (tabs):
					n=(textarray[-1][pieceno]-len(sp[pieceno]))
					textarray[lineno][pieceno] = sp[pieceno]
					if (n%8) != 0:
						textarray[lineno][pieceno] += "\t"*((n/8)+1)
					else:
						textarray[lineno][pieceno] += "\t"*((n/8))
				else:
					n=(textarray[-1][pieceno]-len(sp[pieceno])+additionalspaces)
					textarray[lineno][pieceno] = " "*(n) + sp[pieceno]
	else:
		for pieceno in range(length):
			textarray[lineno][pieceno] = ""
		textarray[lineno][0]=lines[lineno].strip()


fname = sys.argv[2]
if not os.path.exists(fname):
	print "that file doesn't exist"
	exit(0);
else:
	f=open(fname,"w");
	for line in textarray[:-1]:
		for piece in line:
			f.write(piece)
		f.write("\n")
	f.close()




