### SAURA INTRODUCTION
# Printed Circuit Boards aka PCBs are generally made of sheets of copper-plated fiberglass, whose copper has been strategically removed, leaving behind thin lines of copper, called traces. Componenets like LEDS, microcontrollers, and resistors, are then soldered to onto the PCB to create electrical connections. 
# Copper is often abbreviated to its atomic symbol cu
# The 'schematic'  lays out what parts are connected to other parts
# The 'board' lays out the physical design of the PCB

# Voltage is a difference in electrical potential between two points. Voltage is also called electromotive force EMF. Voltage is always taken between two points. Most often, we take the voltage between some point, and ground.
# The analogy of voltage, current, to a river.

# A net is a region of electrical connectivity. Note that all a region of electrical connectivity physically is, is some copper. Right now, its voltage is undefined, but we can drive regions of copper to different voltages using batteries. Any items soldered to the same area of copper all share the same net. A net will generally be at the same potential; the same voltage, maybe, 0V, or 5V. Anything connected to this 0V net, would also be at 0V.  Without any voltage sources, that net isn't doing much. We can power the net with a voltage source, like a battery. To put that net at 9V, we would take a 9V battery, and connect batt+ to the one net, driving it to 9V, and batt- to our net thats supposed to be at gnd, driving that net to 0V, or gnd. 

# Electrically connected items should have just one net, say, 0V. If you connected two nets, say 0V connected to 5V, that would be a short circuit, and would probably fry the PCB. DRC will detect such short circuits and throw an error. In a working design, something such as a resistor would separate the 5V net from the 0V net

# Connecting 0V directly to 5V would cause a short circuit

# To make connections in the schematic, while in schematic view, press 'AddWireMode', and use the mouse to electrically connect items with wires. When a wiring is complete, double click to exit addWireMode.

# Internally, Saura will track the wires we lay. When a wiring is completed, via double click, all these wires are added to the scene. Next, wiring is 'tidied up'.
# 'Tidying up' removes redundant, overlapping wires. We would never want to move a wire, only to uncover a second wire hidden beneath the moved wire. 
# Tidying up also removes collinear adjacent lines, if there are no perpendicular lines at the vertex. (adjacent lines are lines that share a vertex) Collinear adjacent lines are at 180 degrees, and should be merged, if there isn't any pependicular 'L' junction at the vertex
# vein = wireVein(event.scenePos()) back-follows all connected wires to assemble the vein, remaking any existing veins which this wiring may have connected to 
# So, 'tidying up' involves merging some wires, and splitting others. Saura knows which lines to merge/split, by checking the type of junction a wire has with other wires. process_junction() uses the three point orientation algorithm to detect which of six kinds of intersection two wires have: Tee, L, Plus, collinear overlap, collinear adjacent, no intersection.  
# The 'wiring tidying up' algorithm took me a a month and involves queues, the rtree, and the threePointOrientation algorithm. We recursively back-follow any wires who eventually connect to to pos, while detecting for cases where wires should be broken into two(Tee connection) or merged( multiple cases incl collinear overlapped.)
Tee                 : One of the wires in the tee should be split into two 
L                   : No action needed 
Plus                : No action needed 
Collinear overlap   : merge these wires together
collinear adjacent  : Test if there are any L-type intersections at vertex. If no L, merge these wires together
No Intersection     : This case should not occur during wireVein, because rtree used with line hitboxes. 

# Here is a rough run through of the wiring tidying up algo:
# position_queue initially includes position of double click which terminated addWireMode. Start there. 
# query rtree for position. rtree includes wires, symbols, and netsymbols. 
# if its a wire, if able, merge/split, add the POSITIONS of the merged/splitted wires to the position queue, if we haven't already checked those positions, & stop considering this particular wire, & move to the next wire. 
# if its a wire, and it don't need merge/split, we know this wire is 'tidy'. Add wire to vein, add its distal point to the position queue, if the wire has an assigned vein(the case if wire existed before this wiring was laid), track it in connected_veins. 
# In this way, we back-follow all connected positions/wires, splitting/merging where needed, and only adding to vein, wires which were checked for 'tidyness'
# distal is a anatomical term for 'furthest away'. 

# See code for exactly how its done




# MW.veins          Holds all info about veins 
# {0: { 'vein': {NetPriority.Wire:[WireItem1, WireItemN]} , 'net': ['3v3', '0V'] , 'pads': [Pad1, PadN]}}
# Mw.nets           Tracks all info about nets 
# { '3v3' : [0,6] , 'C1-1': [3] }
# Mw.ratsnest       Holds ratsnest lines. Destroyed&remade with each run of MW.generateRatsnest. Uses MW.veins['pads']. 
# {QGLI1 , QGLI2} 
    # The 'ratsnest' hints to the user where the nearest pad which should be connected to this pad is. Note for a pad to be part of the ratsnest, it is both belonging to net & unwired. Bc once user wires to a pad its not in the ratsnets anymore. 
    #     adjacency_matrix = squareform( pdist( points )) # Use scipy to form weighted adjacency matrix, a precursor to the minimum spanning tree. See sparse matrices, compressed sparse matrices,  scipy.pdist, scipy.squareform, adjacency matrices, minimum spanning tree(everyone uses KruskalMST including me here). adj matrix aka 'graph' in compSci 
    #     coo = adjacency_matrix.tocoo() # squareform & pdist use sparse matrices, csr flavor. Convert to COOrdinate flavor so that we can use coo.row & coo.col to make our graph edges-- Note these edges are made of indices of points, corresponding to how they were ordered in 'points'. So edge(0,2) corresponds to points[0] to points[2]
    #     edges = list(zip(coo.row , coo.col)) 