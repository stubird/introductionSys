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
from random import random

import numpy as np

class Tree:

    def __init__(self, dataSet):
        self.root = self.buildTreeByData(dataSet)

    def buildTreeByData(self, dataSet):
        root = branch(self, dataSet, dimension=0)
        root.getConstraint(root)
        return root

class branch:

    def __init__(self, tree, dataSet, dimension=0, parent = None):
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
        #print ("new branch,param: dataSet:",dataSet, " , dimension = ", dimension)
        if len(dataSet) > 1:
            self.buildSonByData(tree, dataSet, dimension)
        else:
            self.right = None
            self.left = None

        if parent == None:
            self.parent = 'root'
        else:
            self.parent = parent

        self.coordinate = self.getCoordinate(dataSet, dimension)
        self.value = self.coordinate[-1]
        self.tree = tree
        self.space = None


    def buildSonByData(self, tree, dataSet, dimension):
        nextDimension = dimension + 1 if dimension < len(dataSet[0]) - 2 else 0
        leftIndices = self.getLeftIndices(dataSet, dimension)

        leftSetIndices = leftIndices[:-1]
        leftSet = [dataSet[x] for x in leftSetIndices]
        if len(leftSet) == 0:
            #print("have no left")
            self.left = None
        else:
            #print("build left")
            self.left = branch(tree, leftSet, dimension=nextDimension, parent=self)

        rightIndices = range(len(dataSet))
        rightIndices = set(rightIndices).difference(set(leftIndices))
        rightSet = [dataSet[x] for x in rightIndices]
        if len(rightSet) == 0:
            #print("have no right")
            self.right = None
        else:
            #print("build right")
            self.right = branch(tree, rightSet, dimension=nextDimension, parent=self)

    def getConstraint(self, root, dimension = 0):
        """calculate every point constraint. We can also say calculate the
            super space the point hold
        """
        nextDimension = self.getNextDimension(dimension, len(root.coordinate) - 2)
        border = root.coordinate[dimension]
        if root.parent == 'root':
            root.space = [[float('-inf'), float('inf')] for i in range(len(root.coordinate) - 1)]
        if root.left != None:
            root.left.space = [x[:] for x in root.space]
            root.left.space[dimension][1] = border
            self.getConstraint(root.left, dimension = nextDimension)
        if root.right != None:
            root.right.space = [x[:] for x in root.space]
            root.right.space[dimension][0] = border
            self.getConstraint(root.right, dimension = nextDimension)

    def getCoordinate(self, dataSet, dimension):
        """
        get coordinate by data set
        choose median number in the dimension of the data set
        """
        dataindex = self.getLeftIndices(dataSet, dimension)
        #return coordinate array
        return dataSet[dataindex[-1]][:]

    def getLeftIndices(self, dataSet, dimension):
        array = [x[dimension] for x in dataSet]
        sortIndex = np.argsort(array, axis=0)
        #get median number
        midnum = int(len(sortIndex) / 2) + len(sortIndex) % 2
        #get median number index
        dataindex = sortIndex[0:midnum]
        return dataindex


    def printNode(self, node, pad = '', dimension = 0):
        global index4prt
        index = index4prt + 1
        index4prt = index4prt + 1
        print ('node',index,' is : ', node.coordinate, 'space:', node.space, 'dimension = ',dimension)
        pad = pad + '|    '
        if node.left == None and node.right == None:
            print (pad, 'node',index,' is leave')
            return

        nextDimension = self.getNextDimension(dimension, len(node.coordinate) - 2)
        if node.left != None:
            print (pad, 'node',index ,' left is ',end="" )
            self.printNode(node.left,pad = pad, dimension = nextDimension)
        else:
            print (pad, 'node',index,' have no left ')

        if node.right != None:
            print(pad, 'node',index,' right is ',end="")
            self.printNode(node.right, pad = pad, dimension = nextDimension)
        else:
            print(pad, 'node',index,' have no right ')
        return

    def getNextDimension(self, dimension, gate):
        return dimension + 1 if dimension < gate else 0

    def verifyTree(self, root, dimension = 0):
        maxDimension = len(self.coordinate)
        next = self.getNextDimension(dimension, maxDimension - 2)

        sign1 = "have no right"
        sign2 = "have no left"

        if root.left != None:
            sign2 = True if root.left.coordinate[dimension] < root.coordinate[dimension] else False
            self.verifyTree(root.left, next)

        if root.right != None:
            sign1 = True if root.right.coordinate[dimension] > root.coordinate[dimension] else False
            self.verifyTree(root.right, next)

        print("1", sign1, " 2", sign2)

    def findPointSpace(self, parent, point):
        dimension = 0
        while True:
            if point[dimension] > parent.coordinate[dimension]:
                if parent.right != None:
                    parent = parent.right
                else:
                    return parent
            else:
                if parent.left != None:
                    parent = parent.left
                else:
                    return parent
            dimension = self.getNextDimension(dimension, len(parent.coordinate) - 2)

    def findNearestPoint(self, root, point):
        spacepoint = root.findPointSpace(root, point)
        # range
        superSphere = [[min([point.coordinate[y] - point.coordinate[y] + spacepoint.coordinate[y],
                    point.coordinate[y] + point.coordinate[y] - spacepoint.coordinate[y]]),
                    max([point.coordinate[y] - point.coordinate[y] + spacepoint.coordinate[y],
                    point.coordinate[y] + point.coordinate[y] - spacepoint.coordinate[y]])]
                   for y in range(len(point) - 1)]

        sibling = spacepoint.findSibling()
        distance = [abs(spacepoint.space[i] - point.space[i]) for i in range(len(spacepoint.coordinate) - 1)]
        distance = sum(distance)

        while sibling.parent != 'root' and sibling.parent.parent != 'root':
            bestPoint, superSphere, distance = \
                sibling.findBestFromOneNode(self, point, spacepoint, superSphere, distance)
            bestPoint, superSphere, distance = \
                sibling.parent.testNearPoint(bestPoint, superSphere, distance)
            sibling = sibling.parent.parent.left\
                if sibling != sibling.parent.parent.left else sibling.parent.parent.right

    def findBestFromOneNode(self, targetPoint, bestPoint, superSphere, distance):
        if self.isOverlap(superSphere) == False:
            return bestPoint, superSphere, distance

        selfDistance = [abs(self.space[i] - targetPoint.space[i]) for i in range(len(self.coordinate) - 1)]
        selfDistance = sum(selfDistance)
        if selfDistance < distance:
            distance = selfDistance
            bestPoint = self
            superSphere = [[min([bestPoint.coordinate[y], 2 * targetPoint.coordinate[y] - bestPoint.coordinate[y]]),
                        max([bestPoint.coordinate[y], 2 * targetPoint.coordinate[y] - bestPoint.coordinate[y]])]
                       for y in range(len(bestPoint.coordinate) - 1)]

        if self.left != None:
            bestPoint, superSphere, distance = \
                self.left.findBestFromOneNode(targetPoint, bestPoint, superSphere, distance)
        if self.right != None:
            bestPoint, superSphere, distance = \
                self.right.findBestFromOneNode(targetPoint, bestPoint, superSphere, distance)

        return bestPoint, superSphere, distance

    def testNearPoint(self, targetPoint, bestPoint, superSphere, distance):
        selfDistance = [abs(self.space[i] - targetPoint.space[i]) for i in range(len(self.coordinate) - 1)]
        selfDistance = sum(selfDistance)
        if selfDistance < distance:
            distance = selfDistance
            bestPoint = self
            superSphere = [[min([bestPoint.coordinate[y], 2 * targetPoint.coordinate[y] - bestPoint.coordinate[y]]),
                        max([bestPoint.coordinate[y], 2 * targetPoint.coordinate[y] - bestPoint.coordinate[y]])]
                       for y in range(len(bestPoint.coordinate) - 1)]
        return bestPoint, superSphere, distance

    def loopForSons(self, point):
        if self.left != None and self.left.isOverlap(point):
            self.left.testNearPoint()

    def findSibling(self):
        ret = 'over'
        if self.parent != 'root' and self.parent.left != None and self.parent.left != self:
            return self.parent.left
        elif self.parent != 'root' and self.parent.right != None and self.parent.right != self:
            return self.parent.right
        elif self.parent != 'root':
            self.parent.findSibing()

        return ret

    def isOverlap(self, node):
        for x in range(len(self.coordinate) - 1):
            if (self.space[0] > node[0] and self.space[0] < node[1]) or \
                    (self.space[0] > node[0] and self.space[0] < node[1]):
                return True

        return False

index4prt = 0

def test():

    dataSet = [[int(random()*100) for x in range(3)] for y in range(2000)]

    tree = Tree(dataSet)
    #tree.root.printNode(tree.root)

    #tree.root.verifyTree(tree.root)

    point = branch(tree, [22,5,4])

    tree.root.findNearestPoint(tree.root, point)

test()