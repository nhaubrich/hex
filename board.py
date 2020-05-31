#have a hex board object that:
#	can be viewed with state()
#	can be updated with move(x,y)
#	can test if a move is legal ???
#	can detect if a side has won
from random import randrange,random
import numpy as np
from time import time
import pickle
from keras.models import Sequential,load_model


model = load_model('hex_ai_2.h5')
def nn_evaluate(boardState):
    evaluation = model.predict(np.reshape(np.ravel(boardState),(1,-1)))
    return evaluation

def isAdjacent(stone1,stone2):
    x1,y1 = stone1
    x2,y2 = stone2

    isAdjacent = False
    if (y1==y2 and abs(x2-x1)==1):
        isAdjacent = True
    elif(x1==x2 and abs(y2-y1)==1):
        isAdjacent = True
    elif abs(y2-y1)==1 and abs(x2-x1)==1 and y2-y1==x1-x2:
        isAdjacent = True
    
    return isAdjacent


class board():
    #keep track of moves and connections as we go
    def __init__(self,size,importBoard=None):
        self.size = size
        self.allMoves = set([(x,y) for x in range(self.size) for y in range(self.size)])
        
        if importBoard==None:
            self.turn = 0
            #initialize white with chains at top and bottom: (x,-1) and (x,size)
            self.wChains = [set([(x,-1) for x in range(self.size)]), set([(x,self.size) for x in range(self.size)])]
            self.bChains = [set([(-1,y) for y in range(self.size)]), set([(self.size,y) for y in range(self.size)])]
            self.moveList = []
            self.legalMoves = self.allMoves 
            self.win = 0 #1 for white, -1 for black

        else:
            self.turn = importBoard['turn']
            self.wChains = importBoard['wChains']
            self.bChains = importBoard['bChains']
            self.moveList = importBoard['moveList']
            self.legalMoves = importBoard['legalMoves']
            self.win = importBoard['win']

    
    def export(self):
        return {'size': self.size,
         'turn': self.turn,
         'wChains': self.wChains,
         'bChains': self.bChains,
         'moveList': self.moveList,
         'legalMoves': self.legalMoves,
         'win': self.win}
                

    #try to speed up move
    #unify chain merging?
    #maybe generate a dict of connections to replace isAdjacent?
    def move(self,move):
        #self.view()
        #print(move)
        x,y = move

        if move not in self.legalMoves:
            raise ValueError("Illegal move:",move,self.legalMoves)

            return 0 #a better return value?
        else:
            self.moveList.append(move)
            self.legalMoves = self.allMoves - set(self.moveList)
            self.turn+=1
            
            #todo unify white/black moving
            if self.turn%2==1: #white
                #check if move has neighbors in wChains
                chainsToAddMoveTo = []
                for i,chain in enumerate(self.wChains):
                    for stone in chain:
                        if isAdjacent(stone,move):
                            chainsToAddMoveTo.append(i)
                            break
                
                for i in chainsToAddMoveTo:
                    self.wChains[i].add(move)
                    
                if len(chainsToAddMoveTo)==0:
                    #awkward, is there better?
                    newChain = set()
                    newChain.add(move)
                    self.wChains.append(newChain)

                #if the new stone added to multiple chains, merge them
                if len(chainsToAddMoveTo)>1:
                    mergedChain = set()
                    
                    for i in chainsToAddMoveTo[::-1]: #reversed so largest indices are removed first
                        mergedChain |= self.wChains.pop(i) #remove existing chain, but add it to mergedChain
                
                    #check for win
                    #mergedChain contains (x,-1) and (x,size)
                    if (0,-1) in mergedChain and (0,self.size) in mergedChain:
                        self.win=1
                    self.wChains.append(mergedChain)
                
            if self.turn%2==0: #black
                #check if move has neighbors in wChains
                chainsToAddMoveTo = []
                for i,chain in enumerate(self.bChains):
                    for stone in chain:
                        if isAdjacent(stone,move):
                            chainsToAddMoveTo.append(i)
                            break
                for i in chainsToAddMoveTo:
                    self.bChains[i].add(move)
                
                if len(chainsToAddMoveTo)==0:
                    newChain = set()
                    newChain.add(move)
                    self.bChains.append(newChain)
                #if the new stone added to multiple chains, merge them
                if len(chainsToAddMoveTo)>1:
                    mergedChain = set()
                    
                    for i in chainsToAddMoveTo[::-1]: #reversed so largest indices are removed first
                        mergedChain |= self.bChains.pop(i) #remove existing chain, but add it to mergedChain
                
                    #check for win
                    #mergedChain contains (x,-1) and (x,size)
                    if (-1,0) in mergedChain and (self.size,0) in mergedChain:
                        self.win=-1

                    self.bChains.append(mergedChain)

            return self.win

    def makeBoardState(self): #doesn't line up with view, oh well
        boardState = np.zeros((self.size,self.size))
        for i,move in enumerate(self.moveList):
            x,y = move
            if i%2==0:
                boardState[y][x] = 1
            else:
                boardState[y][x] = 2
        return boardState


    #given a symmetry, check if boardState has it, then use it to limit the legal moves
    def trimLegalMoves(self):
        boardState = self.makeBoardState()
        if np.array_equal(boardState,boardState[::-1]):#reflect across x-axis
            trimmedLegalMoves = set()
            for move in self.legalMoves:
                x,y = move
                if (x,self.size-1-y) in self.legalMoves:
                    if y<=(self.size-1-y): #save move with lower y value
                        trimmedLegalMoves.add(move)
                    else:
                        pass
                else:
                    trimmedLegalMoves.add(move)
            self.legalMoves = trimmedLegalMoves

        if np.array_equal(boardState,boardState[:,::-1]):#reflect across y-axis
            trimmedLegalMoves = set()
            for move in self.legalMoves:
                x,y = move
                if (self.size-1-x,y) in self.legalMoves:
                    if x<=(self.size-1-x): #save move with lower x value
                        trimmedLegalMoves.add(move)
                    else:
                        pass
                else:
                    trimmedLegalMoves.add(move)
            self.legalMoves = trimmedLegalMoves



    def view(self,depth=5):
        boardState =  [[0 for x in range(self.size)] for y in range(self.size)]
        for i,move in enumerate(self.moveList):
            x,y = move
            if i%2==0:
                boardState[y][x] = 1
            else:
                boardState[y][x] = 2

        for i,row in enumerate(boardState[::-1]):
            print("\t"*(5-depth)+ (self.size-i)*" "+" ".join(str(x) for x in row))
        
        return



    def evaluate(self):       #map boardstate to a score
        if self.win==0:
            return nn_evaluate(self.makeBoardState())
        else:
            return self.win    
    

    def minmax(self,depth=3):
        #self.view(depth)
        if depth<=0 or self.win!=0:
            score = self.evaluate()
            return score

        self.trimLegalMoves()
        if self.turn%2==0:  #white, maximizing
            score = -np.inf
            for move in self.legalMoves:
                tmpBoard = pickle.loads(pickle.dumps(self,-1))
                tmpBoard.move(move)

                moveValue = tmpBoard.minmax(depth-1)
                if moveValue>score:
                    score = moveValue
            return score
            
        else: #black, minimizing
            score = np.inf
            for move in self.legalMoves:
                tmpBoard = pickle.loads(pickle.dumps(self,-1))
                tmpBoard.move(move)

                moveValue = tmpBoard.minmax(depth-1)
                #self.undo()
                if moveValue<score:
                    score = moveValue
            return score

    def minmax_and_move(self,depth=2):
        
        self.trimLegalMoves() 
        
        #calculate minmax of every move, then play highest/lowest score
        if self.turn%2==0: #white, select highest-scoring move
            score = -np.inf
            bestmove = (-1,-1)
            for move in self.legalMoves:
                
                tmpBoard = pickle.loads(pickle.dumps(self,-1))
                tmpBoard.move(move)

                moveValue = tmpBoard.minmax(depth)
                #self.undo()
                #print(move,moveValue,"MAX")
                if moveValue>score:
                    bestmove = move
                    score = moveValue

        else: #black, select lowest-scoring move
            score = np.inf
            bestmove = (-1,-1)
            for move in self.legalMoves:
                
                tmpBoard = pickle.loads(pickle.dumps(self,-1))
                tmpBoard.move(move) 
                moveValue = tmpBoard.minmax(depth)
                #self.undo()
                #print(move,moveValue,"MIN")
                if moveValue<score:
                    bestmove = move
                    score = moveValue

        #print(bestmove,score)
        self.move(bestmove)
        return

def test():
    wwins = 0
    bwins = 0
    
    for size in [5]:
        start = time()
        for x in range(1):
            testBoard = board(size)
            while testBoard.win==0:
                if testBoard.turn%2==0:
    
                    testBoard.minmax_and_move(1) #4 minutes on 4x4 with depth=3 
                else:
                    move_ind = randrange(len(testBoard.legalMoves))
                    move = list(testBoard.legalMoves)[move_ind]
                    testBoard.move(move)
    
                if testBoard.win==1:
                    wwins+=1
                elif testBoard.win==-1:
                    bwins+=1
            print("")
            testBoard.view()
    
        end = time()
        print("time {:4.2f}".format( end-start))
        print(size,wwins,bwins)
        p=wwins/(wwins+bwins)
        print(p,"+/-",(p*(1-p)*(wwins+bwins)**-1)**.5)
