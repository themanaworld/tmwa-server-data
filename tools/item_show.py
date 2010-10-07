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
            name=array[1]
            mbonus=array[10]
            try:
                int(mbonus)
                items+=[(int(mbonus),name)]
            except:
                print line
    return items;

global_items=[]
global_items=make_items();

global_items.sort()
for item in global_items:
    print item
