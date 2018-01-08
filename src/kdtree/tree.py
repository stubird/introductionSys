"""
   Copyright 2018 (c) Jinxin Xie

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import numpy as np

class Tree:

    def __init__(self, dataSet):
        self.root = self.buildTreeByData(dataSet)

    def buildTreeByData(self, dataSet):
        return branch(self, dataSet, dimension=0)

class branch:

    def __init__(self, tree, dataSet, dimension=0):
        """
        :param tree: tree this branch belong of
        :param dataSet: dataSet the branch to build,
            the final column present class code
            e.x:
            dataSet = [
                [1,2,0],
                [3,1,1]
            ]
            array [1,2,0] Constraint is [1,2] and class code is 0
            array [3,1,1] Constraint is [3,1] and class code is 1
        :param dimension: dimension of the branch
        """

        if len(dataSet) > 1:
            self.buildSonByData(tree, dataSet, dimension)
        else:
            self.right = None
            self.left = None

        self.constraint = self.getConstraint(dataSet, dimension)
        self.coordinate = self.getCoordinate(dataSet, dimension)
        self.value = self.coordinate[-1]
        self.tree = tree



    def buildSonByData(self, tree, dataSet, dimension):
        nextDimension = dimension + 1 if dimension < len(dataSet[0]) - 2 else 0
        dataIndex = self.getMedianIndex(dataSet, dimension)

        leftSet = dataSet[:dataIndex]
        if len(leftSet) == 0:
            self.left = None
        else:
            self.left = branch(tree, leftSet, dimension=nextDimension)

        rightSet = dataSet[dataIndex+1:]
        if len(rightSet) == 0:
            self.right = None
        else:
            self.right = branch(tree, rightSet, dimension=nextDimension)

    def getConstraint(self, dataSet, dimension):
        #TODO
        pass

    def getCoordinate(self, dataSet, dimension):
        """
        get coordinate by data set
        choose median number in the dimension of the data set
        """
        dataindex = self.getMedianIndex(dataSet, dimension)
        #return coordinate array
        return dataSet[dataindex][:]

    def getMedianIndex(self, dataSet, dimension):
        array = [x[dimension] for x in dataSet]
        sortIndex = np.argsort(array, axis=0)
        #get median number
        midnum = int(len(sortIndex) / 2) + len(sortIndex) % 2 - 1
        #get median number index
        dataindex = sortIndex[midnum]
        return dataindex


    def printNode(self, node, pad = ''):
        global index4prt
        index = index4prt + 1
        index4prt = index4prt + 1
        print ('node',index,' is : ', node.coordinate)
        pad = pad + '|    '
        if node.left == None and node.right == None:
            print (pad, 'node',index,' is leave')
            return

        if node.left != None:
            print (pad, 'node',index ,' left is ',end="" )
            self.printNode(node.left,pad = pad)
        else:
            print (pad, 'node',index,' have no left ')

        if node.right != None:
            print(pad, 'node',index,' right is ',end="")
            self.printNode(node.right, pad = pad)
        else:
            print(pad, 'node',index,' have no right ')
        return

index4prt = 0

def test():

    dataSet = [
        [1,2,3,4],
        [2,3,5,8],
        [3,5,7,3],
        [1, 4, 6, 4],
        [24, 3, 6, 8],
        [1, 5, 6, 3],
        [12, 9, 4, 4],
        [8, 0, 7, 8],
        [4, 4, 5, 3]
    ]

    tree = Tree(dataSet)
    tree.root.printNode(tree.root)

test()