# Do not Keep working on rerturning all shortest paths: I figure the best use of all shortest paths is to choose btwn either first shortest path found, or the shortest path with the least vertices... so for now, I can just work with first shortest path found.
# Modify AStar to return all shortest paths. Strategy: when neighbor_node is revisited, IF its g is equal to stored g, find it in the open_dict or closed_dict( may ALWAYS be in open dict?) , and append it's predecessors. Then, after first time goal_node == current_node, reconstruct_paths based on predecessors
import heapq 
import math
from PySide6.QtCore import QPointF

def create_node(position, g= float('inf') , h = 0.0 , predecessors = []):
    return {
        'position' : position , 
        'g' : g , 
        'h' : h , 
        'f' : g + h ,
        'predecessors' : predecessors,
    }

def calculate_distance(position1 , position2) :
    print('POSITION1:', position1)
    print('POSITION2:', position2)
    x1 , y1 = position1 
    x2 , y2 = position2 
    return math.sqrt( (x2 - x1) ** 2 + (y2 - y1) ** 2 )

def calculate_heuristic(position1, position2) :
    return calculate_distance(position1 , position2)

def get_neighbor_positions(grid, position): 
    num_rows , num_columns = grid.shape
    x , y = position
    
    all_neighbor_indices = [  # All possible moves (eight total)
        (x+1 , y) , (x-1 , y), 
        (x , y+1) , (x , y-1),
        (x+1 , y+1) , (x-1 , y-1), 
        (x+1 , y-1) , (x-1 , y+1)
    ]
    valid_neighbor_indices = []
    # if self.is_occluded( QPointF( x*self.board_grid_step , y*self.board_grid_step ) ) else 0
    for neighbor_x , neighbor_y in all_neighbor_indices:
        if 0 <= neighbor_x < num_columns and 0 <= neighbor_y < num_rows: 
            if grid[neighbor_x , neighbor_y] == 0: 
                valid_neighbor_indices.append((neighbor_x , neighbor_y) )
    return valid_neighbor_indices 

# v2
def get_neighbor_positions(grid, position): 
    # num_rows , num_columns = grid.shape
    # num_rows , num_columns = int(self.sceneRect().width() / self.board_grid_step) , int(self.sceneRect().height() / self.board_grid_step)
    width , height = self.width() , self.height()
    x , y = position.toTuple()
    
    all_neighbor_positions = [  # All possible moves (eight total)
        (x+self.board_grid_step , y) , (x-self.board_grid_step , y), 
        (x , y+self.board_grid_step) , (x , y-self.board_grid_step),
        (x+self.board_grid_step , y+self.board_grid_step) , (x-self.board_grid_step , y-self.board_grid_step), 
        (x+self.board_grid_step , y-self.board_grid_step) , (x-self.board_grid_step , y+self.board_grid_step)
    ]
    valid_neighbor_positions = []
    # if self.is_occluded( QPointF( x*self.board_grid_step , y*self.board_grid_step ) ) else 0
    footprint_items = [fp for fp in self.items() if isinstance(fp , MyFootprintItem) ]
    for neighbor_position in all_neighbor_positions:
        if 0 <= neighbor_position.x() < width and 0 <= neighbor_position.y() < height: 
            pad = self.is_occluded_by_pad_item( position , footprint_items)
            if pad:
                if pad.net() == self.net(): 
                    self.seeker.setPos(pad.center())
            else:
                self.seeker.setPos(self.snap_to_grid(event.scenePos()))
                
                valid_neighbor_positions.append(position)
    return valid_neighbor_positions 

def reconstruct_path(goal_node, closed_dict):
    paths = []
    current_node = goal_node 
    path = [] 
    while current_node: 
        current_position = current_node['position']
        path.append(current_position)
        # current_node = current_node['predecessor']
        predecessors = closed_dict[current_position]['predecessors']
        if predecessors: # bc the start nodes predecessors is []
            predecessor_position = closed_dict[current_position]['predecessors'][0]
            current_node = closed_dict.get(predecessor_position) 
            if len(predecessors) > 1: 
                print()
                print('PREDECESSORS:', type(predecessors) , predecessors)
        else:
            print('PATH:', path)
            return path[::-1]



def find_path(grid, start_position: QPointF, goal_position: QPointF):
    start_position = start_position.toTuple()
    goal_position = goal_position.toTuple()
    
    start_node = create_node(start_position, g = 0, h = calculate_heuristic(start_position , goal_position))
    open_list = [ ( start_node['f'], start_position ) ]
    open_dict = { start_position : start_node }
    # closed_set = set()
    closed_dict = {} # Gotta know both position AND node

    while open_list: 
        _ , current_position = heapq.heappop(open_list)  
        current_node = open_dict.pop(current_position)
        closed_dict[current_position] = current_node
        # current_node = open_dict[current_position]    # Um why are some nodes both open and closed? Oh, its bc I was open_dict[current_position] not open_dict.pop(current_position)
        # closed_set.add(current_position)
        
        if current_position == goal_position: 
            print('current_position == goal_position')
            path = reconstruct_path(current_node, closed_dict)
            print('PATH:', path)
            return open_dict, closed_dict, path


        for neighbor_position in get_neighbor_positions(grid , current_position):
            g = current_node['g'] + calculate_distance(current_position , neighbor_position)
            
            # if neighbor_position in closed_set: 
                # continue  #
            # Nodes can be closed, open, or new. if closed or open, maybe we'll update predecessors. if new, we'll push node into queue.
            closed_neighbor= closed_dict.get(neighbor_position , None)
            
            if closed_neighbor: # If we already visited this node: We'll update its predecessors, if g is equal to stored g
                continue
            #     # print('G:', g)
            #     # print('CLOSED_G:', closed_neighbor['g'])
            #     # print(f'NEIGHBOR_POSITION: {neighbor_position} IS IN CLOSED DICT') # Trad A* would completely ignore nodes in closed_set, but we have to consider them if g-value is equal 
            #     if g == closed_neighbor['g']: 
            #         print('This path is an equal') 
            #         closed_dict[neighbor_position]['predecessors'].append(current_position)
                    
            open_neighbor = open_dict.get(neighbor_position, None) 
            if open_neighbor: #This never happens on most graphs, because it happens when revisiting a node, with equal path, which only happens if there is a symmetric obstacle in the way, and when this circumstance happens, the node will not yet have been popped.
                # print(f'NEIGHBOR_POSITION: {neighbor_position} IS IN OPEN DICT') # Trad A* would completely ignore nodes in closed_set, but we have to consider them if g-value is equal 
                if g == open_neighbor['g']:
                    # print('THIS PATH IS AN EQUAL')
                    open_neighbor['predecessors'].append(current_position)

            elif neighbor_position not in open_dict: # THIS LINE EXEMPT CAUSES WANDERING PATH
                h = calculate_heuristic(neighbor_position , goal_position)
                neighbor_node = create_node(neighbor_position , g , h , [current_position] )
                heapq.heappush(open_list, ( neighbor_node['f'] , neighbor_position))
                open_dict[neighbor_position] = neighbor_node

    return [] 

# ! pip install matplotlib 
import matplotlib.pyplot as plt
import numpy as np

def visualize_path(grid, path, closed_dict , open_dict):
    # print('CLOSED_DICT:', type(closed_dict), closed_dict)
    # print('OPEN_DICT:', type(open_dict), open_dict)
    """
    Visualize the grid and found path.
    """
    plt.figure(figsize=(10, 10))
    plt.imshow(grid, cmap='binary')
    
    closed_positions = np.array(list(closed_dict.keys()))
    open_positions = np.array(list(open_dict.keys()))
    print('closed_positions', list(closed_positions))
    print('OPEN_POSITIONS:', list(open_positions))
    print('CLOSED_DICT[(17, 17)]', closed_dict[(17,17)])
    if path:
        path = np.array(path)
        plt.plot(path[:, 0], path[:, 1], 'b-', linewidth=3, label='Path')
        plt.plot(path[0, 0], path[0, 1], 'go', markersize=15, label='Start')
        plt.plot(path[-1, 0], path[-1, 1], 'ro', markersize=15, label='Goal')
        plt.plot(open_positions[:, 0] , open_positions[:, 1] , 'gx' , markersize = 10, label = 'Open')
        plt.plot(closed_positions[:, 0] , closed_positions[:, 1] , 'r+' , markersize = 10, label = 'Closed')
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.title("A* Pathfinding Result")
    plt.show()
        

### TESTING ###
# # Create a sample grid
# grid = np.zeros((20, 20))  # 20x20 grid, all free space initially
# # Add some obstacles
# # grid[5:15, 10] = 1  # Vertical wall
# # grid[5, 5:15] = 1   # Horizontal wall
# grid[10,10] = 1 
# # Define start and goal positions
# start_pos = (2, 2)
# goal_pos = (18, 18)
# # Find the path
# open_dict, closed_dict, path = find_path(grid, start_pos, goal_pos)

# if path:
#     print(f"Path found with {len(path)} steps!")
#     visualize_path(grid, path, closed_dict, open_dict)
# else:
#     print("No path found!")
