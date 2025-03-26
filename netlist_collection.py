netlist_data = {
    1: """
    c1 net1 out1
    c2 net2 out2
    m1 net3 net4 gnd! gnd! nmos
    m2 net4 ibias vdd! vdd! pmos
    m3 net5 ibias vdd! vdd! pmos
    m4 net6 net6 gnd! gnd! nmos
    m5 net7 net7 gnd! gnd! nmos
    m6 net8 net3 net9 net9 pmos
    m7 net9 ibias vdd! vdd! pmos
    m8 net10 net3 net11 net11 pmos
    m9 net11 ibias vdd! vdd! pmos
    m10 net6 out2 net8 net8 pmos
    m11 net7 vref net8 net8 pmos
    m12 net6 out1 net10 net10 pmos
    m13 net7 vref net10 net10 pmos
    m14 net1 net7 gnd! gnd! nmos
    m15 net2 net7 gnd! gnd! nmos
    m16 net12 ibias vdd! vdd! pmos
    m17 net1 in1 net12 net12 pmos
    m18 net2 in2 net12 net12 pmos
    c3 out1 gnd!
    c4 out2 gnd!
    m19 out1 net5 net13 net13 nmos
    m20 net13 net1 gnd! gnd! nmos
    m21 out1 ibias vdd! vdd! pmos
    m22 out2 net5 net14 net14 nmos
    m23 net14 net2 gnd! gnd! nmos
    m24 out2 ibias vdd! vdd! pmos
    m25 net4 net4 gnd! gnd! nmos
    m26 net5 net5 gnd! gnd! nmos
    m27 net3 net3 vdd! vdd! pmos
    m28 ibias ibias vdd! vdd! pmos
""",
2: """
c1 net1 out 
m1 net2 net3 gnd! gnd! nmos
m2 net3 ibias vdd! vdd! pmos
m3 net4 ibias vdd! vdd! pmos
m4 net5 ibias vdd! vdd! pmos
m5 net6 net6 gnd! gnd! nmos
m6 net1 net5 net7 net7 nmos
m7 net7 net6 gnd! gnd! nmos
m8 net8 ibias vdd! vdd! pmos
m9 net6 in1 net8 net8 pmos
m10 net1 in2 net8 net8 pmos
c2 out gnd! 
m11 out net4 net9 net9 nmos
m12 net9 net9 gnd! gnd! nmos
m13 out net2 net10 net10 pmos
m14 net10 net1 vdd! vdd! pmos
m15 net3 net3 gnd! gnd! nmos
m16 net4 net4 net11 net11 nmos
m17 net11 net9 gnd! gnd! nmos
m18 net5 net5 gnd! gnd! nmos
m19 net2 net2 vdd! vdd! pmos
m20 ibias ibias vdd! vdd! pmos""",

3: """
c1 net1 out
m1 net2 net3 gnd! gnd! nmos
m2 net3 ibias vdd! vdd! pmos
m3 net4 net4 net5 net5 nmos
m4 net5 net5 gnd! gnd! nmos
m5 net1 net4 net6 net6 nmos
m6 net6 net5 gnd! gnd! nmos
m7 net7 ibias vdd! vdd! pmos
m8 net4 in1 net7 net7 pmos
m9 net1 in2 net7 net7 pmos
c2 out net8
m10 out net1 gnd! gnd! nmos
m11 out net2 net9 net9 pmos
m12 net9 net9 vdd! vdd! pmos
m13 net3 net3 gnd! gnd! nmos
m14 net2 net2 net10 net10 pmos
m15 net10 net9 vdd! vdd! pmos
m16 ibias ibias vdd! vdd! pmos
""",

4: """
c1 net1 out
m1 net2 net3 gnd! gnd! nmos
m2 net4 net3 gnd! gnd! nmos
m3 net5 net5 net6 net6 nmos
m4 net6 net7 gnd! gnd! nmos
m5 net1 net5 net7 net7 nmos
m6 net7 net7 gnd! gnd! nmos
m7 net8 net4 vdd! vdd! pmos
m8 net5 in1 net8 net8 pmos
m9 net1 in2 net8 net8 pmos
c2 out net9
m10 out ibias net3 net3 nmos
m11 net3 net3 gnd! gnd! nmos
m12 out net2 net10 net10 pmos
m13 net10 net1 vdd! vdd! pmos
m14 ibias ibias net11 net11 nmos
m15 net11 net3 gnd! gnd! nmos
m16 net2 net2 vdd! vdd! pmos
m17 net4 net4 vdd! vdd! pmos
""",

5: """
c1 net1 out
m1 net2 ibias vdd! vdd! pmos
m2 net3 net3 net4 net4 nmos
m3 net4 net4 gnd! gnd! nmos
m4 net1 net3 net5 net5 nmos
m5 net5 net4 gnd! gnd! nmos
m6 net6 ibias vdd! vdd! pmos
m7 net3 in1 net6 net6 pmos
m8 net1 in2 net6 net6 pmos
c2 out net7
m9 out net2 net8 net8 nmos
m10 net8 net8 gnd! gnd! nmos
m11 out net1 vdd! vdd! pmos
m12 net2 net2 net9 net9 nmos
m13 net9 net8 gnd! gnd! nmos
m14 ibias ibias vdd! vdd! pmos
""",
6: """
c1 net1 out1
c2 net2 out2
m1 net3 net4 gnd! gnd! nmos
m2 net5 ibias vdd! vdd! pmos
m3 net4 ibias vdd! vdd! pmos
m4 net6 net6 gnd! gnd! nmos
m5 net7 net7 gnd! gnd! nmos
m6 net8 ibias vdd! vdd! pmos
m7 net9 ibias vdd! vdd! pmos
m8 net6 out2 net8 net8 pmos
m9 net7 vref net8 net8 pmos
m10 net6 out1 net9 net9 pmos
m11 net7 vref net9 net9 pmos
m12 net1 net5 net10 net10 nmos
m13 net10 net7 gnd! gnd! nmos
m14 net2 net5 net11 net11 nmos
m15 net11 net7 gnd! gnd! nmos
m16 net1 net3 net12 net12 pmos
m17 net12 ibias vdd! vdd! pmos
m18 net2 net3 net13 net13 pmos
m19 net13 ibias vdd! vdd! pmos
m20 net14 ibias vdd! vdd! pmos
m21 net10 in1 net14 net14 pmos
m22 net11 in2 net14 net14 pmos
c3 out1 net15
c4 out2 net15
m23 out1 net4 gnd! gnd! nmos
m24 out1 net1 vdd! vdd! pmos
m25 out2 net4 gnd! gnd! nmos
m26 out2 net2 vdd! vdd! pmos
m27 net5 net5 gnd! gnd! nmos
m28 net4 net4 gnd! gnd! nmos
m29 net3 net3 vdd! vdd! pmos
m30 ibias ibias vdd! vdd! pmos
""",
7: """
c1 net1 out1
c2 net2 out2
m1 net3 net4 gnd! gnd! nmos
m2 net5 ibias vdd! vdd! pmos
m3 net4 ibias vdd! vdd! pmos
m4 net6 net6 gnd! gnd! nmos
m5 net7 net7 gnd! gnd! nmos
m6 net8 ibias vdd! vdd! pmos
m7 net9 ibias vdd! vdd! pmos
m8 net6 out2 net8 net8 pmos
m9 net7 vref net8 net8 pmos
m10 net6 out1 net9 net9 pmos
m11 net7 vref net9 net9 pmos
m12 net1 net5 net10 net10 nmos
m13 net10 net7 gnd! gnd! nmos
m14 net2 net5 net11 net11 nmos
m15 net11 net7 gnd! gnd! nmos
m16 net1 net3 net12 net12 pmos
m17 net12 ibias vdd! vdd! pmos
m18 net2 net3 net13 net13 pmos
m19 net13 ibias vdd! vdd! pmos
m20 net14 ibias vdd! vdd! pmos
m21 net10 in1 net14 net14 pmos
m22 net11 in2 net14 net14 pmos
c3 out1 net15
c4 out2 net15
m23 out1 net5 net16 net16 nmos
m24 net16 net4 gnd! gnd! nmos
m25 out1 net3 net17 net17 pmos
m26 net17 net1 vdd! vdd! pmos
m27 out2 net5 net18 net18 nmos
m28 net18 net4 gnd! gnd! nmos
m29 out2 net3 net19 net19 pmos
m30 net19 net2 vdd! vdd! pmos
m31 net5 net5 gnd! gnd! nmos
m32 net4 net4 gnd! gnd! nmos
m33 net3 net3 vdd! vdd! pmos
m34 ibias ibias vdd! vdd! pmos
""",

8: """
c1 net1 out1
c2 net2 out2
m1 net3 net4 gnd! gnd! nmos
m2 net5 net4 gnd! gnd! nmos
m3 net6 net4 gnd! gnd! nmos
m4 net4 ibias vdd! vdd! pmos
m5 net7 ibias vdd! vdd! pmos
m6 net8 net8 gnd! gnd! nmos
m7 net9 net9 gnd! gnd! nmos
m8 net10 ibias vdd! vdd! pmos
m9 net11 ibias vdd! vdd! pmos
m10 net8 out2 net10 net10 pmos
m11 net9 vref net10 net10 pmos
m12 net8 out1 net11 net11 pmos
m13 net9 vref net11 net11 pmos
m14 net1 net6 net12 net12 pmos
m15 net2 net6 net13 net13 pmos
m16 net1 net9 gnd! gnd! nmos
m17 net2 net9 gnd! gnd! nmos
m18 net14 ibias vdd! vdd! pmos
m19 net12 in1 net14 net14 pmos
m20 net13 in2 net14 net14 pmos
c3 out1 net15
c4 out2 net15
m21 out1 net7 net16 net16 nmos
m22 net16 net1 gnd! gnd! nmos
m23 out1 net3 net17 net17 pmos
m24 net17 net17 vdd! vdd! pmos
m25 out2 net7 net18 net18 nmos
m26 net18 net2 gnd! gnd! nmos
m27 out2 net5 net19 net19 pmos
m28 net19 net19 vdd! vdd! pmos
m29 net4 net4 gnd! gnd! nmos
m30 net7 net7 gnd! gnd! nmos
m31 net3 net3 net20 net20 pmos
m32 net20 net17 vdd! vdd! pmos
m33 net5 net5 net21 net21 pmos
m34 net21 net19 vdd! vdd! pmos
m35 net6 net6 net14 net14 pmos
m36 ibias ibias vdd! vdd! pmos
""",
9:"""
c1 net1 out1
c2 net2 out2
m1 net3 net4 gnd! gnd! nmos
m2 net5 net4 gnd! gnd! nmos
m3 net4 ibias vdd! vdd! pmos
m4 net6 ibias vdd! vdd! pmos
m5 net7 net7 gnd! gnd! nmos
m6 net8 net8 gnd! gnd! nmos
m7 net9 ibias vdd! vdd! pmos
m8 net10 ibias vdd! vdd! pmos
m9 net7 out2 net9 net9 pmos
m10 net8 vref net9 net9 pmos
m11 net7 out1 net10 net10 pmos
m12 net8 vref net10 net10 pmos
m13 net1 net6 net11 net11 nmos
m14 net11 net8 gnd! gnd! nmos
m15 net2 net6 net12 net12 nmos
m16 net12 net8 gnd! gnd! nmos
m17 net1 ibias vdd! vdd! pmos
m18 net2 ibias vdd! vdd! pmos
m19 net13 ibias vdd! vdd! pmos
m20 net11 in1 net13 net13 pmos
m21 net12 in2 net13 net13 pmos
c3 out1 net14
c4 out2 net14
m22 net15 net1 gnd! gnd! nmos
m23 net15 ibias vdd! vdd! pmos
m24 net16 net2 gnd! gnd! nmos
m25 net16 ibias vdd! vdd! pmos
m26 out1 net15 gnd! gnd! nmos
m27 out1 net3 net17 net17 pmos
m28 net17 net17 vdd! vdd! pmos
m29 out2 net16 gnd! gnd! nmos
m30 out2 net5 net18 net18 pmos
m31 net18 net18 vdd! vdd! pmos
m32 net4 net4 gnd! gnd! nmos
m33 net6 net6 gnd! gnd! nmos
m34 net3 net3 net19 net19 pmos
m35 net19 net17 vdd! vdd! pmos
m36 net5 net5 net20 net20 pmos
m37 net20 net18 vdd! vdd! pmos
m38 ibias ibias vdd! vdd! pmos
""",

10: """
c1 net1 out1
c2 net2 out2
m1 net3 net4 gnd! gnd! nmos
m2 net5 ibias vdd! vdd! pmos
m3 net4 ibias vdd! vdd! pmos
m4 net6 net6 gnd! gnd! nmos
m5 net7 net7 gnd! gnd! nmos
m6 net8 net3 net9 net9 pmos
m7 net9 ibias vdd! vdd! pmos
m8 net10 net3 net11 net11 pmos
m9 net11 ibias vdd! vdd! pmos
m10 net6 out2 net8 net8 pmos
m11 net7 vref net8 net8 pmos
m12 net6 out1 net10 net10 pmos
m13 net7 vref net10 net10 pmos
m14 net1 net5 net12 net12 nmos
m15 net12 net7 gnd! gnd! nmos
m16 net2 net5 net13 net13 nmos
m17 net13 net7 gnd! gnd! nmos
m18 net1 ibias vdd! vdd! pmos
m19 net2 ibias vdd! vdd! pmos
m20 net14 ibias vdd! vdd! pmos
m21 net12 in1 net14 net14 pmos
m22 net13 in2 net14 net14 pmos
c3 out1 net15
c4 out2 net15
m23 net16 net1 gnd! gnd! nmos
m24 net16 ibias vdd! vdd! pmos
m25 net17 net2 gnd! gnd! nmos
m26 net17 ibias vdd! vdd! pmos
m27 out1 net5 net18 net18 nmos
m28 net18 net4 gnd! gnd! nmos
m29 out1 net16 vdd! vdd! pmos
m30 out2 net5 net19 net19 nmos
m31 net19 net4 gnd! gnd! nmos
m32 out2 net17 vdd! vdd! pmos
m33 net5 net5 gnd! gnd! nmos
m34 net4 net4 gnd! gnd! nmos
m35 net3 net3 vdd! vdd! pmos
m36 ibias ibias vdd! vdd! pmos
"""

}

groundtruth = {
    1: ['m4', 'm5', 'm28', 'm26', 'm27', 'm25'],
    2: ['m5', 'm18', 'm19', 'm15', 'm12', 'm20', 'm16'],
    3: ['m4', 'm16', 'm13', 'm14', 'm3', 'm12'],
    4:['m16', 'm11', 'm17', 'm6', 'm14', 'm3'],
    5: ['m14', 'm12', 'm10', 'm2', 'm3'],
    6: ['m4', 'm5', 'm27', 'm29', 'm30', 'm28'],
    7: ['m31', 'm5', 'm32', 'm34', 'm33', 'm4'],
    8: ['m28', 'm29', 'm30', 'm24', 'm35', 'm31', 'm6', 'm7', 'm36', 'm33'],
    9: ['m5', 'm34', 'm28', 'm38', 'm36', 'm32', 'm6', 'm31', 'm33'],
    10: ['m4', 'm35', 'm34', 'm5', 'm33', 'm36']
}
def get_netlist(id):
    return netlist_data[id]

def get_groundtruth(id):
    return {"number_of_diode_connected_transistors": len(groundtruth[id]), "transistor_names": groundtruth[id]}