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
from time import time
import numpy as np

import logging



class Tree:

    def __init__(self, dataSet):
        self.name = 'Tree'
        self.nodeNum = 0
        self.root = self.buildTreeByData(dataSet)


    def buildTreeByData(self, dataSet):
        root = branch(self, dataSet, dimension=0)
        root.getConstraint(root)
        return root


class branch:

    def __init__(self, tree, dataSet, dimension=0, parent=None, type = 'root'):
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
        #logger.debug ("new branch,param: dataSet:%s, dimension = %d",dataSet, dimension)
        if len(dataSet) > 1:
            self.buildSonByData(tree, dataSet, dimension)
        else:
            self.right = None
            self.left = None

        if parent == None:
            self.parent = 'root'
            self.name = type + tree.nodeNum.__str__()
            tree.nodeNum = tree.nodeNum + 1
        else:
            self.parent = parent
            self.name = type + tree.nodeNum.__str__()
            tree.nodeNum = tree.nodeNum + 1

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
            self.left = None
        else:
            self.left = branch(tree, leftSet, dimension=nextDimension, parent=self, type = 'left')

        rightIndices = range(len(dataSet))
        rightIndices = set(rightIndices).difference(set(leftIndices))
        rightSet = [dataSet[x] for x in rightIndices]
        if len(rightSet) == 0:
            self.right = None
        else:
            self.right = branch(tree, rightSet, dimension=nextDimension, parent=self, type = 'right')

    def getConstraint(self, root, dimension=0):
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
            self.getConstraint(root.left, dimension=nextDimension)
        if root.right != None:
            root.right.space = [x[:] for x in root.space]
            root.right.space[dimension][0] = border
            self.getConstraint(root.right, dimension=nextDimension)

    def getCoordinate(self, dataSet, dimension):
        """
        get coordinate by data set
        choose median number in the dimension of the data set
        """
        dataindex = self.getLeftIndices(dataSet, dimension)
        # return coordinate array
        return dataSet[dataindex[-1]][:]

    def getLeftIndices(self, dataSet, dimension):
        array = [x[dimension] for x in dataSet]
        sortIndex = np.argsort(array, axis=0)
        # get median number
        midnum = int(len(sortIndex) / 2) + len(sortIndex) % 2
        # get median number index
        dataindex = sortIndex[0:midnum]
        return dataindex

    def printNode(self, node, pad='', dimension=0):
        pad = pad + '|    '
        logger.debug('%s%s is :%s ,space:%s,dimension = %d',pad, node.name, node.coordinate,node.space, dimension)
        if node.left == None and node.right == None:
            logger.debug('%s%s is leave',pad, node.name)
            return

        nextDimension = self.getNextDimension(dimension, len(node.coordinate) - 2)
        if node.left != None:
            logger.debug('%s%s left is ',pad, node.name)
            self.printNode(node.left, pad=pad, dimension=nextDimension)
        else:
            logger.debug('%s%s have no left ',pad, node.name)

        if node.right != None:
            logger.debug('%s%s right is ', pad, node.name)
            self.printNode(node.right, pad=pad, dimension=nextDimension)
        else:
            logger.debug('%s%s have no right ', pad, node.name)
        return

    def getNextDimension(self, dimension, gate):
        return dimension + 1 if dimension < gate else 0

    def verifyTree(self, root, dimension=0):
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

        logger.debug("1", sign1, " 2", sign2)

    def findPointSpace(self, parent, point):
        # find the space match to the point
        dimension = 0
        while True:
            if point.coordinate[dimension] > parent.coordinate[dimension]:
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
        bestPoint = root.findPointSpace(root, point)
        # range

        distance = [abs(bestPoint.coordinate[i] - point.coordinate[i]) for i in range(len(bestPoint.coordinate) - 1)]
        distance = sum(distance)

        if bestPoint.left != None:
            bestPoint, distance = \
                bestPoint.left.testNearPoint(point, bestPoint, distance)
        elif bestPoint.right != None:
            bestPoint, distance = \
                bestPoint.right.testNearPoint(point, bestPoint, distance)

        bestPoint, distance, sibling = bestPoint.findSibling(point, bestPoint, distance)
        logger.debug("begin find nearest:\n\
                        bestpoint: %s,distance:%d ,sibing:%s", bestPoint.name, distance, sibling.name)
        while True:
            bestPoint, distance = \
                sibling.findBestFromOneNode(point, bestPoint, distance)
            bestPoint, distance = \
                sibling.parent.testNearPoint(point, bestPoint, distance)
            if sibling.parent == 'root' or sibling.parent.parent == 'root':
                break
            sibling = sibling.parent.parent.left \
                if sibling.parent != sibling.parent.parent.left else sibling.parent.parent.right
            logger.debug("loop find nearest:\n\
                bestpoint: %s,distance:%d ,sibing:%s",bestPoint.name,  distance, sibling.name)

        return bestPoint, distance

    def findBestFromOneNode(self, targetPoint, bestPoint, distance):
        if self.isOverlap(targetPoint, distance) == False:
            logger.debug("think overlap, %s self,space: %s", self.name, self.space)
            return bestPoint, distance

        selfDistance = [abs(self.coordinate[i] - targetPoint.coordinate[i]) for i in range(len(self.coordinate) - 1)]
        selfDistance = sum(selfDistance)
        logger.debug("%s's distance = %d", self.name, selfDistance)
        if selfDistance < distance:
            distance = selfDistance
            bestPoint = self

        if self.left != None:
            bestPoint, distance = \
                self.left.findBestFromOneNode(targetPoint, bestPoint, distance)
        if self.right != None:
            bestPoint, distance = \
                self.right.findBestFromOneNode(targetPoint, bestPoint, distance)

        return bestPoint, distance

    def testNearPoint(self, targetPoint, bestPoint, distance):
        selfDistance = [abs(self.coordinate[i] - targetPoint.coordinate[i]) for i in range(len(self.coordinate) - 1)]
        selfDistance = sum(selfDistance)
        if selfDistance < distance:
            distance = selfDistance
            bestPoint = self
        return bestPoint, distance

    def loopForSons(self, point):
        if self.left != None and self.left.isOverlap(point):
            self.left.testNearPoint()

    def findSibling(self,point, bestPoint, distance):
        ret = 'over'
        if self.parent != 'root' and self.parent.left != None and self.parent.left != self:
            logger.debug("find parent's left")
            return bestPoint, distance,self.parent.left
        elif self.parent != 'root' and self.parent.right != None and self.parent.right != self:
            logger.debug("find parent's right")
            return bestPoint, distance,self.parent.right
        elif self.parent != 'root':
            logger.debug("parent have no other sibling, find up layer")
            bestPoint, distance = self.parent.testNearPoint(point, bestPoint, distance)
            bestPoint, distance, ret = self.parent.findSibling(point, bestPoint, distance)
        return bestPoint, distance, ret

    def isOverlap(self, point, distance):
        def shortest(array, point):
            if point < array[0]:
                return array[0] - point
            if point > array[1]:
                return point - array[1]
            return 0
        thisdistance = 0
        for x in range(len(self.coordinate) - 1):
            thisdistance = thisdistance + shortest(self.space[x], point.coordinate[x])
        if thisdistance < distance:
            return  True
        return False

def test():


    dataSet = [[6, 28, 73, 55, 4, 44, 38, 29], [38, 91, 85, 25, 72, 11, 48, 0], [74, 40, 74, 50, 72, 32, 56, 77], [30, 59, 51, 61, 20, 50, 30, 54], [49, 33, 78, 24, 65, 18, 91, 71], [14, 92, 95, 59, 24, 94, 24, 26], [96, 58, 56, 56, 89, 16, 57, 25], [6, 66, 92, 4, 89, 78, 69, 73], [17, 69, 88, 62, 27, 0, 72, 65], [39, 68, 96, 41, 76, 66, 71, 19], [9, 84, 2, 48, 96, 22, 93, 95], [8, 11, 81, 11, 67, 98, 54, 56], [48, 31, 80, 68, 2, 1, 25, 87], [17, 28, 6, 46, 19, 57, 50, 67], [15, 39, 56, 20, 67, 90, 75, 37], [85, 61, 34, 71, 32, 33, 84, 81], [83, 50, 3, 41, 51, 8, 75, 89], [30, 99, 10, 89, 16, 35, 84, 17], [67, 10, 62, 31, 73, 14, 33, 3], [13, 45, 37, 60, 57, 59, 72, 68]]
    dataSet = [[int(random() * 100) for x in range(50)] for y in range(200000)]

    tree = Tree(dataSet)
    tree.root.printNode(tree.root)

    # tree.root.verifyTree(tree.root)
    point = branch(tree, [[82, 63, 97, 4, 26, 74, 74, 68]], type = 'test')
    point = branch(tree, [[int(random() * 100) for x in range(50)]], type = 'test')

    ttime = time()
    bestPoint, distance = tree.root.findNearestPoint(tree.root, point)
    ttime = time() - ttime

    space = tree.root.findPointSpace(tree.root, point)

    selfDistance = float('inf')
    coord = []
    for vector in dataSet:
        tmpDistance = [abs(point.coordinate[i] - vector[i]) for i in range(len(point.coordinate) - 1)]
        tmpDistance = sum(tmpDistance)
        if tmpDistance < selfDistance:
            selfDistance = tmpDistance
            coord = vector

    #print("point", point.name,"bestPoint:", bestPoint.name, ", distance:", distance)
    #print("real distance = ", selfDistance, coord,", space:", space.name)
    if distance == selfDistance:
        return True, ttime
    else:
        print(dataSet)
        print("point", point.name,"bestPoint:", bestPoint.name, ", distance:", distance,\
            "real distance = ", selfDistance, "coord",coord,"point",point.coordinate,", space:", space.name)
        return False, ttime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
count = 1
miss = 0
timeavg = 0
while count > 0:
    jug,ttime = test()
    if False == jug:
        break
        miss = miss + 1
    count = count - 1
    timeavg = (ttime + timeavg)/2
print(miss, timeavg)