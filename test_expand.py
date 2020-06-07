
import time
import sys
import ast
from myhdl import *
from fcompact_hdl import fexpand

@block
def test_mux(arr):

    z0,z1,z2,z3,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11 = [Signal(intbv(0)) for i in range(16)]

    fexpand_1 = fexpand(z0,z1,z2,z3,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11)

    @instance
    def stimulus():
        print("z0 z1 z2 z3 a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11")

        start_time=time.time()
        a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11 = arr[0],arr[1],arr[2],arr[3],arr[4],arr[5],arr[6],arr[7],arr[8],arr[9],arr[10],arr[11]
        yield delay(0)
        
        
        print("%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" % (z0,z1,z2,z3,a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11))
        print(time.time()-start_time)


    return fexpand_1, stimulus



brr=ast.literal_eval(sys.argv[1])
tb = test_mux(brr)
tb.run_sim()





