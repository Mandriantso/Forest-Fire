# -*- coding: utf-8 -*-
"""
Created on Sat Nov 8 11:35:14 2020

@author: MAEVA
"""

import sys, math, random
import pygame
import pygame.draw
import numpy as np

__screenSize__ = (800,500) 

__forestSize__ = (500,500)
__cellSize__ = 10 
__gridDim__ = tuple(map(lambda x: int(x/__cellSize__), __forestSize__)) # shape : (50, 50)
__density__ = 0.55     

# cell colors : void, resistant tree, normal tree, fire, water, inflammable tree                
__colors__ = [(255,255,255),(0,100,40),(0,160,40),(160,40,0),(30,30,255),(100,60,30)]  

# probabilities to get on fire if one neighbour is on fire
__normalTreeProba__ = 0.45
__resistantTreeProba__ = 0.25
__inflammableTreeProba__ = 1.0


def getColorCell(n):
    return __colors__[n]

class Grid:
    _grid= None
    _gridbis = None
    _dictNeighbourIndex = {"north" : (0,-1), "south" : (0,1), "east" : (1,0), "west" : (-1,0)}
   
    def __init__(self, north_wind=False, south_wind=False, east_wind=False, west_wind=False):
        print("Creating a grid of dimensions " + str(__gridDim__))
        # initializing the grid
        self._grid = np.zeros(__gridDim__, dtype='int8')    # first we create a grid of zeros
        self._gridbis = np.zeros(__gridDim__, dtype='int8') # we initialize gridbis in the same way, it will be usefull for updating the scene
        nx, ny = __gridDim__
        
        # initializing normal trees according to forest density
        ones = np.random.random((nx, ny)) <= __density__  
        self._grid[0:nx, 0:ny] = ones*2
        
        # initializing other sceneries
        self._initTreeCount = self.treeCount()
        self._initResistantTrees_()
        self._initInflammableTrees_()
        self._initWater_()
        
        # initializing winds
        self._north_wind = north_wind
        self._south_wind= south_wind
        self._east_wind = east_wind
        self._west_wind = west_wind
        
        # keep a count of tree numbers
        self._totalTreeCount=self.treeCount()
        self._normalTreeCount=self.normalTreeCount()
        self._resistantTreeCount=self.resistantTreeCount()
        self._inflammableTreeCount=self.inflammableTreeCount()
        self._percentageTreeLeft = self.percentageTreeLeft()


    def _initResistantTrees_(self):
        # Strong trees represent at most 20% of the trees in the forest
        maxIter = self._initTreeCount*0.2
        for _ in range(int(maxIter)):
            randomx = random.randint(0, __gridDim__[0]-1)
            randomy = random.randint(0, __gridDim__[1]-1)
            if self._grid[randomx, randomy]==2:
                self._grid[randomx, randomy]=1
                
                
    def _initInflammableTrees_(self):
        # Vulnerable trees represent at most 10% of the trees in the forest
        maxIter = self._initTreeCount*0.1
        for _ in range(int(maxIter)):
            randomx = random.randint(0, __gridDim__[0]-1)
            randomy = random.randint(0, __gridDim__[1]-1)
            if self._grid[randomx, randomy]==2:
                self._grid[randomx, randomy]=5
                
                
    def _initWater_(self):
        # Water represents at most 15% of blank space
        blankSpace=0
        for i in range(__gridDim__[0]):
            for j in range(__gridDim__[1]):
                if self._grid[i,j]==0:
                    blankSpace+=1
                    
        maxIter=blankSpace*0.15
        for _ in range(int(maxIter)):
            randomx = random.randint(0, __gridDim__[0]-1)
            randomy = random.randint(0, __gridDim__[1]-1)
            if self._grid[randomx, randomy]==0:
                self._grid[randomx, randomy]=4
        
    
        
    def treeCount(self):
        # counting total number of trees in the forest
        treeCount = 0
        for i in range(__gridDim__[0]):
            for j in range(__gridDim__[1]):
                if self._grid[i,j]!=0 and self._grid[i,j]!=3 and self._grid[i,j]!=4:
                    treeCount+=1
                    
        return treeCount
        
        
    def resistantTreeCount(self):
        # counting resistant trees in the forest
        treeCount=0
        for i in range(__gridDim__[0]):
            for j in range(__gridDim__[1]):
                if self._grid[i,j]==1:
                    treeCount+=1
        
        return treeCount
        
        
    def inflammableTreeCount(self):
        # counting inflammable trees in the forest
        treeCount=0
        for i in range(__gridDim__[0]):
            for j in range(__gridDim__[1]):
                if self._grid[i,j]==5:
                    treeCount+=1
        
        return treeCount
        
    def normalTreeCount(self):
        # counting normal trees in the forest
        treeCount=0
        for i in range(__gridDim__[0]):
            for j in range(__gridDim__[1]):
                if self._grid[i,j]==2:
                    treeCount+=1
        
        return treeCount
        
        
    def percentageTreeLeft(self):
        # computing the percentage of tree left
        percentage=(self._totalTreeCount*100)/self._initTreeCount
        return percentage
        
        
    def neighbourIndex(self, x,y):
        copyNeighbourIndex=self._dictNeighbourIndex.copy()
        neighbourIndex = copyNeighbourIndex
        # as cell gets on fire if its neighbours are on fire, we check neighbours from where the fire comes
        # for example, if wind is set to south, we check north neighbours and not south neighbours as fire comes from the north
        
        if self._north_wind:
            # remove north neighbours unless cell contains vulnerable tree
            if self._grid[x,y]!=5:
                del neighbourIndex["north"]
            # add south neighbour unless there is water or if south_wind is enabled
            # for simplification reasons, adverse winds cancel each other
            if y+1<__gridDim__[1] and self._grid[x,y+1]!=4 and self._south_wind==False:
                neighbourIndex["south2"]=(0,2)
            
        if self._south_wind:
            if self._grid[x,y]!=5:
                del neighbourIndex["south"]
            if y-1>0 and self._grid[x,y-1]!=4 and self._north_wind==False:
                neighbourIndex["north2"]=(0,-2)
        
        if self._east_wind: 
            if self._grid[x,y]!=5:
                del neighbourIndex["east"]
            if x-1>0 and self._grid[x-1,y]!=4 and self._west_wind==False:
                neighbourIndex["west2"]=(-2,0)
            
        if self._west_wind:
            if self._grid[x,y]!=5:
                del neighbourIndex["west"]
            if x+1<__gridDim__[0] and self._grid[x+1,y]!=4 and self._east_wind==False:
                neighbourIndex["east2"]=(2,0)
            
        neighbourList = list(neighbourIndex.values())
        return [(dx+x,dy+y) for (dx,dy) in neighbourList if dx+x >=0 and dx+x < __gridDim__[0] and dy+y>=0 and dy+y < __gridDim__[1]]


    def allCells(self): 
        # returns all cells from grid
        return [c for c, _ in np.ndenumerate(self._grid)]


    def countFireNeighbours(self,x,y):  
        # counts the number of trees on fire neighbouring the cell
        fireNeighbours=[self._grid[vx,vy] for (vx, vy) in self.neighbourIndex(x,y) if self._grid[vx,vy]==3]
        return np.sum(fireNeighbours)//3


class Scene:
    _grid = None
    _font = None

    def __init__(self, north_wind=False, south_wind=False, east_wind=False, west_wind=False):
        # initializing pygame
        pygame.init()
        pygame.font.init()
        self._screen = pygame.display.set_mode(__screenSize__)
        self._font = pygame.font.SysFont('Arial',20, bold=True)
        
        # Wind
        self._north_wind = north_wind
        self._south_wind= south_wind
        self._east_wind = east_wind
        self._west_wind = west_wind
        # Images
        self._north_wind_image = pygame.image.load("Images/N.png").convert_alpha()
        self._south_wind_image = pygame.image.load("Images/S.png").convert_alpha()
        self._east_wind_image = pygame.image.load("Images/E.png").convert_alpha()
        self._west_wind_image = pygame.image.load("Images/W.png").convert_alpha()
        self._northWest_wind_image = pygame.image.load("Images/NW.png").convert_alpha()
        self._northEast_wind_image = pygame.image.load("Images/NE.png").convert_alpha()
        self._southWest_wind_image = pygame.image.load("Images/SW.png").convert_alpha()
        self._southEast_wind_image = pygame.image.load("Images/SE.png").convert_alpha()
        self._all_winds_image = pygame.image.load("Images/all.png").convert_alpha()
        
        # initializing grid
        self._grid = Grid(north_wind=self._north_wind, south_wind=self._south_wind, east_wind=self._east_wind, west_wind=self._west_wind)
        

    def drawMe(self):
        # drawing cells on screen
        if self._grid._grid is None:
            return
        self._screen.fill((255,255,255))  # fill screen in white
        for x in range(__gridDim__[0]):
            for y in range(__gridDim__[1]):
                pygame.draw.rect(self._screen, 
                        getColorCell(self._grid._grid.item(x,y)),
                        (x*__cellSize__ + 1, y*__cellSize__ + 1, __cellSize__-2, __cellSize__-2))
                        
         
        # writing count for each type of tree, total number of trees, remaining number of trees and percentage of remaining trees
        self.drawText("Click on a tree to start a fire !", (515,10), (160,40,40))
        pygame.draw.rect(self._screen, (230,230,230),(510,60,280, 210))
        self.drawText(f"Initial number of trees : {self._grid._initTreeCount}", (515,60), (0,40,40))
        self.drawText(f"Total Trees : {self._grid._totalTreeCount}", (515,95), (40,0,40))
        self.drawText(f"Normal Trees : {self._grid._normalTreeCount}", (515,130), (0,160,40))
        self.drawText(f"Resistant Trees : {self._grid._resistantTreeCount}", (515,165), (0,100,40))
        self.drawText(f"Inflammable Trees : {self._grid._inflammableTreeCount}", (515,200), (100,60,30))
        self.drawText(f"Tree Left : {round(self._grid._percentageTreeLeft,2)}%", (515,235), (255,100,40))
        
        # writing the type of wind
        self.drawText("Wind : ", (515, 350), (160,40,40))
        if self._north_wind:
            self.drawText("North", (570,350), (0,40,40))
        else:
            self.drawText("North", (570,350), (200,200,200))
        if self._south_wind:
            self.drawText("South", (620,350), (0,40,40))
        else:
            self.drawText("South", (620,350), (200,200,200))
        if self._east_wind:
            self.drawText("East", (675,350), (0,40,40))
        else:
            self.drawText("East", (675,350), (200,200,200))
        if self._west_wind:
            self.drawText("West", (715,350), (0,40,40))
        else:
            self.drawText("West", (715,350), (200,200,200))
            
        # wind images
        if self._north_wind and self._east_wind==False and self._west_wind==False:
            self._screen.blit(self._north_wind_image, (600,400))
        if self._north_wind and self._east_wind:
            self._screen.blit(self._northEast_wind_image, (600,400))
        if self._north_wind and self._west_wind:
            self._screen.blit(self._northWest_wind_image, (600,400))
        if self._south_wind and self._east_wind==False and self._west_wind==False:
            self._screen.blit(self._south_wind_image, (600,400))
        if self._south_wind and self._east_wind:
            self._screen.blit(self._southEast_wind_image, (600,400))
        if self._south_wind and self._west_wind:
            self._screen.blit(self._southWest_wind_image, (600,400))
        if self._east_wind and self._north_wind==False and self._south_wind==False:
            self._screen.blit(self._east_wind_image, (600,400))
        if self._west_wind and self._north_wind==False and self._south_wind==False:
            self._screen.blit(self._west_wind_image, (600,400))
        if self._east_wind and self._north_wind and self._south_wind and self._west_wind:
            self._screen.blit(self._all_winds_image, (540,400))


    def drawText(self, text, position, color):
        # writing text on screen
        surface=self._font.render(text,1,color)
        self._screen.blit(surface,position)
        
        
    def update(self):
        # updating grid
        self._grid._gridbis = np.copy(self._grid._grid)
        for c in self._grid.allCells():
            # count number of neighbouring fire trees
            nbFire = self._grid.countFireNeighbours(c[0],c[1])
            if self._grid._grid[c[0],c[1]]==2:
                # cell can get on fire if proba * nbFire >= 0.45
                if __normalTreeProba__*nbFire>=0.45:
                    self._grid._gridbis[c[0],c[1]]=3
            elif self._grid._grid[c[0],c[1]]==1:
                # resistant trees can only totally get on fire if proba*nbFire >=0.60
                # if 0.45 <= proba*nbFire <0.60, resistant tree only become more vulnerable but don't get totally burned
                if __resistantTreeProba__*nbFire>=0.45:
                    self._grid._gridbis[c[0],c[1]]==2
                if __resistantTreeProba__*nbFire>=0.70:
                    self._grid._gridbis[c[0],c[1]]=3
            elif self._grid._grid[c[0],c[1]]==5:
                if __inflammableTreeProba__*nbFire>=0.45:
                    self._grid._gridbis[c[0],c[1]]=3
            elif self._grid._grid[c[0],c[1]]==3:
                self._grid._gridbis[c[0],c[1]]=0
        self._grid._grid=np.copy(self._grid._gridbis)

        # update tree counts
        self._grid._totalTreeCount=self._grid.treeCount()
        self._grid._normalTreeCount=self._grid.normalTreeCount()
        self._grid._resistantTreeCount=self._grid.resistantTreeCount()
        self._grid._inflammableTreeCount=self._grid.inflammableTreeCount()
        
        # update percentage of trees left
        self._grid._percentageTreeLeft=self._grid.percentageTreeLeft()


    def startFire(self):
        # starting fire on click : click near inflammable trees for better results
        # resistant trees don't get on fire on first click
        x,y = pygame.mouse.get_pos()
        x=x//__cellSize__
        y=y//__cellSize__
        if self._grid._grid[x,y]==2 or self._grid._grid[x,y]==5:
            self._grid._gridbis[x,y]=3
        elif self._grid._grid[x,y]==1:
            self._grid._gridbis[x,y]=2
        self._grid._grid = np.copy(self._grid._gridbis)
        self.update()
            
        
        

def main():
    # initializing scene
    scene = Scene(north_wind=True, east_wind=True)
    done = False
    clock = pygame.time.Clock()
    while done == False:
        scene.drawMe()
        pygame.display.flip()
        scene.update()
        # pygame.display.update()
        clock.tick(2)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                scene.startFire()
            if event.type == pygame.QUIT: 
                print("Exiting")
                done=True

    pygame.quit()

if not sys.flags.interactive: main()
