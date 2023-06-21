import sys
import os
import copy
import time


class node:
    def __init__(self, not_loaded, loaded, pos_boat, cont_p1, cont_p2, mapa, cost, father):
        """Defines all the attributes needed for the problem"""
        self.not_loaded = not_loaded
        self.loaded = loaded
        self.pos_boat = pos_boat
        self.cont_p1 = cont_p1
        self.cont_p2 = cont_p2
        self.mapa = mapa
        self.cost = cost
        self.father = father

    def __eq__(self, other):
        """Returns True if two nodes are equal and False in other case"""
        for i in self.not_loaded:
            if i not in other.not_loaded:
                return False
        for i in other.not_loaded:
            if i not in self.not_loaded:
                return False
        for i in self.loaded:
            if i not in other.loaded:
                return False
        for i in other.loaded:
            if i not in self.loaded:
                return False
        if self.pos_boat != other.pos_boat:
            return False
        for i in self.cont_p1:
            if i not in other.cont_p1:
                return False
        for i in other.cont_p1:
            if i not in self.cont_p1:
                return False
        for i in self.cont_p2:
            if i not in other.cont_p2:
                return False
        for i in other.cont_p2:
            if i not in self.cont_p2:
                return False
        if self.mapa != other.mapa:
            return False
        return True

    def __str__(self):
        """Returns a string with the all the relevant information of a node"""
        return str(self.not_loaded) + ' | ' + str(self.loaded) + ' | ' + str(self.pos_boat) + ' | ' + str(
            self.cont_p1) + ' | ' + str(self.cont_p2) + ' | ' + str(self.mapa) + ' | ' + str(self.cost)

    def __lt__(self, other):
        """Less than operator. Returns True if a node's cost is less than other's cost"""
        return self.cost < other.cost


def check_parameters():
    """Checks if all the parameters are correct"""
    if len(sys.argv) != 5:
        print('ERROR: incorrect number of parameters.')
        return False

    path = sys.argv[1] + '/' + sys.argv[2]
    if not os.path.isfile(path):
        print('ERROR: map file not found.')
        return False

    path = sys.argv[1] + '/' + sys.argv[3]
    if not os.path.isfile(path):
        print('ERROR: containers file not found.')
        return False

    if str(sys.argv[4]) != "heuristica1" and str(sys.argv[4]) != "heuristica2":
        print('ERROR: heuristic not valid.')
        return False

    return True


def check_space(mapa, containers):
    """Checks if there is enough space to solve the problem"""
    cont_energy = 0
    cont_normal = 0
    for depth in range(len(mapa)):
        for stack in range(len(mapa[0])):
            if mapa[depth][stack] == 'E':
                cont_energy += 1
            elif mapa[depth][stack] == 'N':
                cont_normal += 1
    total_positions = cont_normal + cont_energy
    if total_positions < len(containers):
        print('ERROR: There are more containers than cells in the boat.')
        return False
    else:
        cont_standar = 0
        cont_refrigerate = 0
        for i in containers:
            if i[1] == 'S':
                cont_standar += 1
            elif i[1] == 'R':
                cont_refrigerate += 1
            else:
                print('ERROR: There is one container whose type is not valid.')
                return False
        if cont_energy < cont_refrigerate:
            print('ERROR: There are more refrigerated containers than energy cells in the boat.')
            return False
    return True


def read_cells(path):
    """Reads the cells file and stores all the information in a list"""
    mapa = []
    aux1 = []
    with open(path) as f:
        lines = f.readlines()
    for i in lines:
        for c in i:
            if c != ' ' and c != '\n':
                aux1.append(c)
        mapa.append(aux1)
        aux1 = []
    return mapa


def read_containers(path):
    """Reads the containers file and stores all the information in a list"""
    containers = []
    aux2 = []
    with open(path) as f:
        lines = f.readlines()
    for i in lines:
        for c in i:
            if c != ' ' and c != '\n':
                aux2.append(c)
        containers.append(aux2)
        aux2 = []
    return containers


def all_ids(containers):
    """Returns a list with all the ids"""
    ids = []
    for i in containers:
        ids.append(i[0])
    return ids


def ids_port(containers, port):
    """Returns a list with the ids of all the containers that should be unloaded in a particular port"""
    ids = []
    if port == '1':
        for i in containers:
            if i[2] == '1':
                ids.append(i[0])
    else:
        for i in containers:
            if i[2] == '2':
                ids.append(i[0])
    return ids


def calculate_port(containers, container_id):
    """Returns the port of a concrete container given its id as a parameter"""
    for i in containers:
        if i[0] == container_id:
            port = i[2]
            return port


def navigate(N, dest_port):
    """Creates a new node which simulates the navigation of the boat to the next port"""
    new_node = copy.deepcopy(N)
    new_node.pos_boat = dest_port
    new_node.cost = 3500
    new_node.father = N

    return new_node


def load(N, id, depth, stack):
    """Creates a new node which simulates a container's load"""
    new_node = copy.deepcopy(N)
    new_node.not_loaded.remove(id)
    new_node.loaded.append(id)
    new_node.mapa[depth][stack] = id
    new_node.cost = 10 + depth
    new_node.father = N

    return new_node


def unload_port1(b, N, id, upper_pos, depth, stack):
    """Creates a new node which simulates a container's unload at the port 1"""
    if b == 1:
        # In case that there is an upper container that goes to port 2, it is unloaded and stored in the not_loaded list
        new_node = copy.deepcopy(N)
        new_node.loaded.remove(upper_pos)
        new_node.not_loaded.append(upper_pos)
        new_node.father = N
        new_node.mapa[depth - 1][stack] = original_map[depth - 1][stack]
        new_node.cost = 15 + 2 * (depth - 1)

    else:
        # In case that there is not an upper container, it unloads the actual one in port 1
        new_node = copy.deepcopy(N)
        new_node.loaded.remove(id)
        new_node.cont_p1.append(id)
        new_node.father = N
        new_node.mapa[depth][stack] = original_map[depth][stack]
        new_node.cost = 15 + 2 * depth

    return new_node


def unload_port2(N, id):
    """Creates a new node which simulates a container's unload at the port 2"""
    new_node = copy.deepcopy(N)
    new_node.loaded.remove(id)
    new_node.cont_p2.append(id)
    new_node.father = N
    for depth in range(len(N.mapa)):
        for stack in range(len(N.mapa[0])):
            if N.mapa[depth][stack] == id:
                new_node.mapa[depth][stack] = original_map[depth][stack]
                new_node.cost = 15 + 2 * depth
    return new_node


def heuristic(N, t_heuristic):
    """Depending on the given heuristic, it calculates h(n)"""
    if t_heuristic == 'heuristica1':
        estimated_cost = 0
        # If there are containers which have not been loaded yet, they will have to be loaded and unloaded
        estimated_cost += (len(N.not_loaded) * 10)
        estimated_cost += (len(N.not_loaded) * 15)

        # If there are containers loaded containers on the ship, they will have to be unloaded
        estimated_cost += (len(N.loaded) * 15)

        # Checks if it is necessary to relocate any container
        for depth in range(len(N.mapa)):
            for stack in range(len(N.mapa[0])):
                if N.mapa[depth][stack] in list_ids:
                    id = N.mapa[depth][stack]
                    port = calculate_port(containers, id)
                    if port == '1':
                        upper_pos = N.mapa[depth - 1][stack]
                        if upper_pos in list_ids:
                            puerto_sup = calculate_port(containers, upper_pos)
                            if puerto_sup == '2':
                                # The relocation of a container consists of unloading it and reloading it
                                estimated_cost += 15
                                estimated_cost += 15

        if len(ids_port(containers, '2')) == 0:
            if N.pos_boat == '0':
                estimated_cost += 3500
        else:
            if N.pos_boat == '0':
                estimated_cost += 7000

        return estimated_cost

    else:
        pass


def expandir(N):
    """Returns a list of all the possible son nodes of a given node at the port 2"""
    node_list = []
    # CASE 1: if there are containers that had not been loaded yet, they have to be loaded onto the boat
    if len(N.not_loaded) > 0:
        if N.pos_boat == '0' or N.pos_boat == '1':

            # the list not_loaded is ordered according to each container's port to load first those going to port 2
            aux = []
            for i in N.not_loaded:
                port = calculate_port(containers, i)
                aux.append((i, port))
            aux = sorted(aux, key=lambda x: x[1])
            N.not_loaded = []
            for i in aux:
                N.not_loaded.append(i[0])
            N.not_loaded.reverse()

            # All containers are loaded one by one according to storage restrictions
            for id in N.not_loaded:
                for c in containers:
                    if c[0] == id:
                        type = c[1]

                        # Storage restrictions depend on the type of container
                        if type == 'R':
                            for depth in range(len(N.mapa)):
                                for stack in range(len(N.mapa[0])):
                                    if N.mapa[depth][stack] == 'E':
                                        if N.mapa[depth + 1][stack] == 'X' or N.mapa[depth + 1][stack] in list_ids:
                                            # Creates a new node for each new container loaded
                                            new_node = load(N, id, depth, stack)
                                            node_list.append(new_node)
                        else:
                            for depth in range(len(N.mapa)):
                                for stack in range(len(N.mapa[0])):
                                    if N.mapa[depth][stack] != 'X' and N.mapa[depth][stack] not in list_ids:
                                        if N.mapa[depth + 1][stack] == 'X' or N.mapa[depth + 1][stack] in list_ids:
                                            new_node = load(N, id, depth, stack)
                                            node_list.append(new_node)

    # CASE 2: if there are not containers to load
    if len(N.not_loaded) == 0:
        # But there are containers to unload
        if len(N.loaded) != 0:

            # If the boat is at port 0, it navigates to port 1
            if N.pos_boat == '0':
                new_node = navigate(N, '1')
                node_list.append(new_node)

            # If the boat is at port 1, it unloads all the containers whose port is 1
            elif N.pos_boat == '1':
                for depth in range(len(N.mapa)):
                    for stack in range(len(N.mapa[0])):
                        if N.mapa[depth][stack] in list_ids:
                            id = N.mapa[depth][stack]
                            port = calculate_port(containers, id)
                            if port == '1':
                                upper_pos = N.mapa[depth - 1][stack]
                                # If the upper position is another container, it checks its port
                                if upper_pos in list_ids:
                                    puerto_sup = calculate_port(containers, upper_pos)
                                    # If the upper container port is 2, it unloads and adds it to the not_loaded list
                                    if puerto_sup == '2':
                                        new_node = unload_port1(1, N, id, upper_pos, depth, stack)
                                        node_list.append(new_node)

                                # If there is not any upper container, it unloads it
                                else:
                                    new_node = unload_port1(2, N, id, upper_pos, depth, stack)
                                    node_list.append(new_node)

                # If the boat still has containers whose port is 1, it cannot navigate to port 2
                a = True
                for depth in range(len(N.mapa)):
                    for stack in range(len(N.mapa[0])):
                        if N.mapa[depth][stack] in list_ids:
                            id = N.mapa[depth][stack]
                            port = calculate_port(containers, id)
                            if port == '1':
                                a = False
                # Otherwise, it navigates to port 2
                if a is True:
                    new_node = navigate(N, '2')
                    node_list.append(new_node)

            # If the boat is at port 2, it unloads all the remaining containers
            else:
                for id in N.loaded:
                    new_node = unload_port2(N, id)
                    node_list.append(new_node)

    return node_list


"""=======================================================MAIN======================================================="""
# Calculate the start time of the program
start_time = time.time()

# First, checks if all the parameters are correct. If not, it prints an error message and finishes the program
if not check_parameters():
    quit()

# Opens all the arguments files and stores them in lists
mapa = read_cells(sys.argv[1] + '/' + sys.argv[2])
original_map = read_cells(sys.argv[1] + '/' + sys.argv[2])
containers = read_containers(sys.argv[1] + '/' + sys.argv[3])
heuristica = str(sys.argv[4])

# Checks if there is enough space in the boat to solve the problem
if not check_space(mapa, containers):
    quit()

# Stores in a list the ids of all the containers
list_ids = all_ids(containers)

# Implementation A* algorithm
initial_node = node(list_ids, [], '0', [], [], original_map, 0, None)
final_node = node([], [], '2', ids_port(containers, '1'), ids_port(containers, '2'), original_map, 0, None)
final_node1 = node([], [], '1', ids_port(containers, '1'), [], original_map, 0, None)

closed = []
success = False
opened = [initial_node]
expanded_nodes = 0

while len(opened) > 0 and success is False:
    # Remove the node with the lowest cost
    N = None
    min_index = 0
    for i in range(len(opened)):
        if i == 0:
            pass
        else:
            if opened[min_index].cost > opened[i].cost:
                min_index = i
    N = opened.pop(min_index)

    if N == final_node or N == final_node1:
        success = True
        solution_node = N
    else:
        S = expandir(N)
        for i in S:
            expanded_nodes += 1
        closed.append(N)

        for s in S:
            if s not in opened and s not in closed:
                opened.append(s)
            elif s in opened:
                i = opened.index(s)
                if opened[i].cost > s.cost:
                    opened.pop(i)
                    opened.append(s)

if success:
    final_solution = solution_node
else:
    final_solution = False
solution = []

while final_solution.father is not None:
    solution.insert(0, final_solution)
    final_solution = final_solution.father

# SOLUTION FILE
file_name_1 = sys.argv[2] + "-" + sys.argv[3]
file = open("ASTAR-tests/" + file_name_1 + ".output", "w")
cont = 1
for i in solution:
    if len(i.not_loaded) < len(i.father.not_loaded):
        for id in i.father.not_loaded:
            if id not in i.not_loaded:
                for depth in range(len(i.mapa)):
                    for stack in range(len(i.mapa[0])):
                        if i.mapa[depth][stack] == id:
                            position = (stack, depth)
                action = "cargar "
                file.write(str(cont) + ".- " + action + "('" + str(id) + "', " + str(position) + ")" + '\n')
                cont = cont + 1

    elif len(i.loaded) < len(i.father.loaded):
        for id in i.father.loaded:
            if id not in i.loaded:
                action = "descargar "
                file.write(str(cont) + ".- " + action + "('" + str(id) + "', " + str(i.pos_boat) + ")" + '\n')
                cont = cont + 1

    elif i.pos_boat != i.father.pos_boat:
        action = "navegar "
        file.write(str(cont) + ".- " + action + "('" + str(i.pos_boat) + "')" + '\n')
        cont = cont + 1

# STATISTICS FILE
file_name_1 = sys.argv[2] + "-" + sys.argv[3]
file = open("ASTAR-tests/" + file_name_1 + ".stat", "w")
# Calculates the total time of the solution
file.write("Tiempo total: " + str(round((time.time() - start_time), 3)) + '\n')
# Calculates the total cost of the solution
total_cost = 0
for i in solution:
    if i == final_node or i == final_node1:
        total_cost += heuristic(i, heuristica) + i.cost
    else:
        total_cost += i.cost

file.write("Coste total: " + str(total_cost) + '\n')
# Calculates the length of the solution
file.write("Longitud del plan: " + str(len(solution)) + '\n')
# Calculates the total number of expanded nodes
file.write("Nodos expandidos: " + str(expanded_nodes) + '\n')

# ASTAR-CALLS FILE
path = "ASTAR-calls.sh"
file = open(path, "a")
file.write("ASTARStowage.sh " + sys.argv[1] + " " + sys.argv[2] + " " + sys.argv[3] + '\n')
