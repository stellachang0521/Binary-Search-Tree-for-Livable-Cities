import requests
import json

### Trees are constructed throughout interactions with the users, so most of the project code was retained in this file

########################## Data Manipulation ############################
# loading dataDict and city_coors from local json file
# note the difference between json.load() and json.loads()
with open('dataDict.json') as f:
    dataDict = json.load(f)
    
with open('city_coors.json') as f:
    city_coors = json.load(f)

living = []
house = []
for i in dataDict['living costs']:
    living.append(i['contributors_cost_of_living'])
    house.append(i['contributors_property'])

July_temp = []
December_temp = []
for i in dataDict['July weather']:
    July_temp.append(i['temp']['mean'])
    
for i in dataDict['December weather']:
    December_temp.append(i['temp']['mean'])
    
valueDict = {}
valueDict['city'] = dataDict['city']
valueDict['cost of living'] = living
valueDict['property'] = house
valueDict['July temp'] = July_temp
valueDict['December temp'] = December_temp


###################### Binary Search Tree Class #########################
class TreeNode:

    def __init__(self, key, value, left = None, right = None, parent = None):
        self.key = key # key == ID
        self.payload = value
        self.leftChild = left
        self.rightChild = right
        self.parent = parent

    def hasLeftChild(self):
        return self.leftChild

    def hasRightChild(self):
        return self.rightChild

    def isLeftChild(self):
        return self.parent and self.parent.leftChild == self

    def isRightChild(self):
        return self.parent and self.parent.rightChild == self

    def isRoot(self):
        return not self.parent

    def isLeaf(self):
        return not (self.rightChild or self.leftChild)

    def hasAnyChildren(self):
        return self.rightChild or self.leftChild

    def hasBothChildren(self):
        return self.rightChild and self.leftChild

    def replaceNodeData(self, key, value, left, right):
        self.key = key
        self.payload = value
        self.leftChild = left
        self.rightChild = right
        if self.hasLeftChild():
            self.leftChild.parent = self
        if self.hasRightChild():
            self.rightChild.parent = self
            
            
class BinarySearchTree:

    def __init__(self):
        self.root = None
        self.size = 0 # size == number of levels of the tree

    def length(self):
        return self.size

    # magic method: overwrites original len() method
    def __len__(self):
        return self.size
    
    # returns iterator object
    def __iter__(self):
        return self.root.__iter__()
        
    def put(self, key, value):
        '''
        Checks to see if the tree already has a root.
        If there is not a root (= tree has no node at all) then put will create a new TreeNode and install it as the root of the tree.
        '''
        if self.root:
            self._put(key, value, self.root) # calls the helper _put function to search the tree
        else:
            self.root = TreeNode(key, value)
            self.size = self.size + 1
    
    def _put(self, key, value, currentNode):
        '''
        If the put method discovers that a root node is already in place then put calls the private, recursive, helper function _put to search the tree.
        *_ denotes private
        '''
        
        # if new key < current node, search the left subtree
        if key < currentNode.key:
            if currentNode.hasLeftChild():
                self._put(key, value, currentNode.leftChild)
            else:
                currentNode.leftChild = TreeNode(key, value, parent = currentNode)
        # if new key >= current node, search the right subtree
        else:
            if currentNode.hasRightChild():
                self._put(key, value, currentNode.rightChild)
            else:
                currentNode.rightChild = TreeNode(key, value, parent = currentNode)

    def get(self, key):
        '''
        Returns the value for a given key.
        '''
        if self.root:
            res = self._get(key, self.root)
            if res:
                return res.payload
            else:
                return None
        else:
            return None
        
    def _get(self, key, currentNode):
        if not currentNode: # starts at self.root
            return None
        elif currentNode.key == key:
            return currentNode
        elif key < currentNode.key:
            return self._get(key, currentNode.leftChild)
        else:
            return self._get(key, currentNode.rightChild)

    # magic method
    def __getitem__(self, key):
        return self.get(key)
        
    def delete(self, key):
        if self.size > 1:
            node_to_remove = self._get(key, self.root)
            if node_to_remove:
                self.remove(node_to_remove)
                self.size = self.size -1
                return
        elif self.size == 1 and self.root.key == key:
            self.root = None
            self.size = self.size -1
            return

        raise KeyError('Error, key is not in the tree.')

    def __delitem__(self, key):
        self.delete(key)
        
    def remove(self, node):
        if node._is_leaf() and node.parent is not None:
            if node == node.parent.left:  # if node is ‘a’
                node.parent.left = None  # b.left = none
            else: ##if node is c
                node.parent.right = None # b.right = none
        elif node.has_one_child():
            promoted_node = node.left or node.right
            if node.is_left_child():  # if node is g
                promoted_node.parent = node.parent # set parent of h as k
                node.parent.left = promoted_node # set child of k as h
            if node.is_right_child(): # if node is j
                promoted_node.parent = node.parent # set parent of i as h
                node.parent.right = promoted_node # set h.right as i
            else: # node is the root
                node.replace_node_data(promoted_node.key, promoted_node.payload, promoted_node.left, promoted_node.right)  # if node is y
                # y's attributes were replaced by z's attributes so only z exists now
        else: # has 2 children
            successor = node.find_sucessor()
            if successor:
                successor.splice_out()
                node.key = successor.key
                node.payload = successor.payload
                
    def findSuccessor(self):
        succ = None
        if self.hasRightChild():
            succ = self.rightChild.findMin() # find minimum value in the right subtree to succeed current node's position
        else:
            if self.parent:
                if self.isLeftChild():
                    succ = self.parent
                else: # if self is a right child
                    self.parent.rightChild = None # temporarily remove self to search for successor
                    succ = self.parent.findSuccessor()
                    self.parent.rightChild = self
        return succ
        
    def findMin(self):
        '''
        Searches the left subtree to find the minimum value.
        '''
        current = self
        while current.hasLeftChild():
            current = current.leftChild
        return current

    def spliceOut(self):
        if self.isLeaf():
            if self.isLeftChild():
                self.parent.leftChild = None
            else:
                self.parent.rightChild = None
        elif self.hasAnyChildren():
            if self.hasLeftChild():
                if self.isLeftChild():
                    self.parent.leftChild = self.leftChild
                else:
                    self.parent.rightChild = self.leftChild
                self.leftChild.parent = self.parent
            else:
                if self.isLeftChild():
                    self.parent.leftChild = self.rightChild
                else:
                    self.parent.rightChild = self.rightChild
                self.rightChild.parent = self.parent
                
    def search_range(self, v1, v2):
        nodes = []

        def recursive_search(node):
            if node is None:
                return None

            # search from left to right
            if node.key >= v1:
                recursive_search(node.hasLeftChild()) # until node.key == v1 then != v1
            if v1 <= node.key <= v2:
                nodes.append(node.payload)
            if node.key <= v2: # until node.key == v2 then != v2
                recursive_search(node.hasRightChild())

        recursive_search(self.root)
        return sorted(list(set(nodes)))
        

########################## Tree Construction ############################
living_bst = BinarySearchTree()
property_bst = BinarySearchTree()
july_bst = BinarySearchTree()
dec_bst = BinarySearchTree()

# 2092 nodes per tree
#for i in range(len(valueDict['city'])):
#    living_bst.put(valueDict['cost of living'][i], valueDict['city'][i])
#    property_bst.put(valueDict['property'][i], valueDict['city'][i])
#    july_bst.put(valueDict['July temp'][i], valueDict['city'][i])
#    dec_bst.put(valueDict['December temp'][i], valueDict['city'][i])

def buildTree(cities, values, bst):
    for i in range(len(cities)):
        bst.put(values[i], cities[i])
    return bst


def filter_values(pipein, criteria):
    values = []
    for j in pipein:
        for i in range(len(valueDict['city'])):
            if valueDict['city'][i] == j:
                values.append(valueDict[criteria][i])
    return values


########################### Data Visualization ###############################
import plotly.graph_objects as go

def table(values_list):
    fig = go.Figure(data = [go.Table(header = dict(values = ['Livable Cities', 'Cost of Living', 'Property Index', 'July Temperature', 'December Temperature']),
                 cells = dict(values = values_list))
                     ])
    fig.show()

def barchart(cities, values, title):
    bar_data = go.Bar(x=cities, y=values)
    basic_layout = go.Layout(title=title)
    fig = go.Figure(data=bar_data, layout=basic_layout)
    fig.show()

def temp_diff(cities, july, dec):
    fig = go.Figure()
    fig.add_trace(go.Bar(x = cities, y = july,
                base = dec,
                marker_color = 'blueviolet',
                name = 'Temperature Difference'))
    fig.show()

import geopandas as gpd
import geoplot as gplt
import geoplot.crs as gcrs
%matplotlib inline
import matplotlib.pyplot as plt

def mapping(cityfile):

    # reading geojson file for states
    ## data source: https://eric.clst.org/tech/usgeojson/
    states = gpd.read_file('us_states.json')

    with open(cityfile) as f:
        city_coors = json.load(f)

    # constructing geojson-formatted dictionary for city points
    city_geodict = {}
    city_geodict['type'] = 'FeatureCollection'
    features = []
    for city in city_coors.keys():
        features.append(
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [city_coors[city][0], city_coors[city][1]]
      },
      "properties": {
        "NAME": city
      }
    })
    city_geodict['features'] = features

    # transforming dictionary into geojson file
    city_json = json.dumps(city_geodict)
    with open('city.json', 'w') as f:
        f.write(city_json)

    # reading geojson file for city points
    points = gpd.read_file('city.json')

    # plotting figure
    plt.rcParams["figure.figsize"] = (200, 100)

    # drawing state borders
    #ax = gplt.polyplot(states)
    ax = states.plot(color='cornflowerblue')

    #ax.autoscale()

    # annotating city names
    for city in city_coors.keys():
        x, y = city_coors[city][0], city_coors[city][1]
        ax.annotate(city, # this is the text
                     xy = (x, y), # these are the coordinates to position the label
                     xytext=(0, 10), # distance from text to points (x,y)
                     textcoords="offset points", # how to position the text
                     ha='center')

    # plotting city points
    #gplt.pointplot(points, ax=ax)
    points.plot(ax=ax)
    
    plt.show()
    
    
############################ Interaction Prompt ############################
def yes(prompt):
    status = True
    while status:
        boolean = input(prompt)
        if boolean.lower() == 'yes' or boolean.lower() == 'y' or boolean.lower() == 'yeah' or boolean.lower() == 'yup' or boolean.lower() == 'sure':
            return True
        elif boolean.lower() == 'no' or boolean.lower() == 'n' or boolean.lower() == 'nah' or boolean.lower() == 'nope' or boolean.lower() == 'wrong':
            return False
        else:
            print('Please enter a valid answer.')

def main():

    print('Welcome to Livable Cities Search Tool! Please input your ideal range for the following criterias.')
    #print(valueDict['city'])

    # First Criteria: Cost of Living
    status = True
    col_min = min(valueDict['cost of living'])
    col_max = max(valueDict['cost of living'])

    while status:
        print(f'Please enter your ideal range for the Cost of Living of a city. The minimum is {col_min} while the maximum is {col_max}.')

        c_min = input('Please enter your ideal minimum Cost of Living: ')
        c_max = input('Please enter your ideal maximum Cost of Living: ')

        try:
            c_min = float(c_min)
            c_max = float(c_max)
            if c_min <= c_max and col_min <= c_min <= col_max and col_min <= c_max <= col_max:
                status = False
            else:
                print('Error in input data. Please enter numbers within the given range and make sure that the minimum value does not exceed the maximum value.')
        except:
            print('Error in input data. Please enter valid numbers.')

    buildTree(valueDict['city'], valueDict['cost of living'], living_bst)
    living_cities = living_bst.search_range(c_min, c_max)

    #print(living_cities)

    # Second Criteria: Property Indices
    property_values = filter_values(living_cities, 'property')

    status = True
    ppty_min = min(property_values)
    ppty_max = max(property_values)

    while status:
        print(f'Please enter your ideal range for the Property Index of a city. The minimum is {ppty_min} while the maximum is {ppty_max}.')

        p_min = input('Please enter your ideal minimum Property Index: ')
        p_max = input('Please enter your ideal maximum Property Index: ')

        try:
            p_min = float(p_min)
            p_max = float(p_max)
            if p_min <= p_max and ppty_min <= p_min <= ppty_max and ppty_min <= p_max <= ppty_max:
                status = False
            else:
                print('Error in input data. Please enter numbers within the given range and make sure that the minimum value does not exceed the maximum value.')
        except:
            print('Error in input data. Please enter valid numbers.')

    buildTree(living_cities, property_values, property_bst)
    property_cities = property_bst.search_range(p_min, p_max)

    #print(property_cities)

    # Third Criteria: July Temperature
    july_values = filter_values(property_cities, 'July temp')

    status = True
    july_min = min(july_values)
    july_max = max(july_values)

    while status:
        print(f'Please enter your ideal range for the Average Temperature of July of a city. The minimum is {july_min} while the maximum is {july_max}.')

        j_min = input('Please enter your ideal minimum July Temperature: ')
        j_max = input('Please enter your ideal maximum July Temperature: ')

        try:
            j_min = float(j_min)
            j_max = float(j_max)
            if j_min <= j_max and july_min <= j_min <= july_max and july_min <= j_max <= july_max:
                status = False
            else:
                print('Error in input data. Please enter numbers within the given range and make sure that the minimum value does not exceed the maximum value.')
        except:
            print('Error in input data. Please enter valid numbers.')

    buildTree(property_cities, july_values, july_bst)
    july_cities = july_bst.search_range(j_min, j_max)

    #print(july_cities)

    # Fourth Criteria: December Temperature
    dec_values = filter_values(july_cities, 'December temp')

    status = True
    dec_min = min(dec_values)
    dec_max = max(dec_values)

    while status:
        print(f'Please enter your ideal range for the Average Temperature of December of a city. The minimum is {dec_min} while the maximum is {dec_max}.')

        d_min = input('Please enter your ideal minimum December Temperature: ')
        d_max = input('Please enter your ideal maximum December Temperature: ')

        try:
            d_min = float(d_min)
            d_max = float(d_max)
            if d_min <= d_max and dec_min <= d_min <= dec_max and dec_min <= d_max <= dec_max:
                status = False
            else:
                print('Error in input data. Please enter numbers within the given range and make sure that the minimum value does not exceed the maximum value.')
        except:
            print('Error in input data. Please enter valid numbers.')

    buildTree(july_cities, dec_values, dec_bst)
    dec_cities = dec_bst.search_range(d_min, d_max)

    cost_of_living = filter_values(dec_cities, 'cost of living')
    property_index = filter_values(dec_cities, 'property')
    july_temp = filter_values(dec_cities, 'July temp')
    dec_temp = filter_values(dec_cities, 'December temp')

    #print(dec_cities)

    status = True
    while status:
        chart_type = input('Please choose your preferred data visualization type: Table(t), Bar Chart(b), Temperature Difference Chart(d), Map(m): ')
        if chart_type.lower() == 't':
            table([dec_cities, cost_of_living, property_index, july_temp, dec_temp])
            again = yes('Do you want to view another type of visualization?(y/n)')
            if again == False:
                status = False
        elif chart_type.lower() == 'b':
            bar = True
            while bar:
                criteria = input('Please choose from one of the following four criterias: Cost of Living(c), Property Index(p), July Temperature(j), December Temperature(d): ')
                if criteria.lower() == 'c':
                    barchart(dec_cities, cost_of_living, 'Cost of Living')
                    bar = False
                elif criteria.lower() == 'p':
                    barchart(dec_cities, property_index, 'Property Index')
                    bar = False
                elif criteria.lower() == 'j':
                    barchart(dec_cities, july_temp, 'July Temperature')
                    bar = False
                elif criteria.lower() == 'd':
                    barchart(dec_cities, dec_temp, 'December Temperature')
                    bar = False
                else:
                    print('Please enter a valid option.')
            again = yes('Do you want to view another type of visualization?(y/n)')
            if again == False:
                status = False
        elif chart_type.lower() == 'd':
            temp_diff(dec_cities, july_temp, dec_temp)
            again = yes('Do you want to view another type of visualization?(y/n)')
            if again == False:
                status = False
        elif chart_type.lower() == 'm':
            final_coors = {}
            for city in dec_cities:
                final_coors[city] = city_coors[city]

            # downloading final_coors into a local json file
            final_coors_json = json.dumps(final_coors)
            with open('final_coors.json', 'w') as f:
                f.write(final_coors_json)

            mapping('final_coors.json')
            again = yes('Do you want to view another type of visualization?(y/n)')
            if again == False:
                status = False
        else:
            print('Please enter valid option.')

    print('Thank you!')



if __name__ == '__main__':
    main()
