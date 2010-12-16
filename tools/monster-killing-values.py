#!/usr/bin/python
#has to be executed in place, this folder


def make_items():
    items_file=open("../db/item_db.txt","r")
    lines=items_file.readlines()
    items_file.close();

    items=[]
    for line in lines:
        array=line.split(",")
        if len(array)>6 and not line.startswith("#") and not line.startswith("//"):
            id=array[0]
            sellprize=array[5]
            try:
                int(sellprize)
                items+=[(int(id),int(sellprize))]
            except:
                print line
    return items;

def getvalueof(id):
    for x in global_items:
        if x[0]==id:
            return int(x[1])
    return 0

def make_mobs():
    mobfile=open("../db/mob_db.txt","r")
    lines=mobfile.readlines()
    mobfile.close();

    mobs=[]
    for line in lines:
        array=line.split(",")
        if len(array)>6 and not line.startswith("#"):
            id=array[0]
            name=array[1]
            print name
            print array[29:44]
            sellprize = 0
            #hardcoded -.- fix it !
            sellprize += getvalueof(int(array[29]))*int(array[30])
            sellprize += getvalueof(int(array[31]))*int(array[32])
            sellprize += getvalueof(int(array[33]))*int(array[34])
            sellprize += getvalueof(int(array[35]))*int(array[36])
            sellprize += getvalueof(int(array[37]))*int(array[38])
            sellprize += getvalueof(int(array[39]))*int(array[40])
            sellprize += getvalueof(int(array[41]))*int(array[32])
            sellprize += getvalueof(int(array[43]))*int(array[44])
            mobs+=[(name,sellprize/1000.0)]
    return mobs

global_items=[]
global_items=make_items();

mobs=make_mobs();

for mob in mobs:
    print mob[1],mob[0]
