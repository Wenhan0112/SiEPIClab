# -*- coding: utf-8 -*-
"""
Abort Automeasurement

@author: Wenhan
"""

ABORTION_FILE = "ABORTION_FILE.txt"

def abort(fn=ABORTION_FILE):
    f = open(fn, "w")
    f.write("abort")
    f.close()
    
if __name__ == "__main__":
    abort()