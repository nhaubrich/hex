#randint(0,len(testBoard.legalMoves))what's the plan?
#
#have a hex board object that:
#	can be viewed with state()
#	can be updated with move(x,y)
#	can test if a move is legal ???
#	can detect if a side has won
from random import randrange,random
import numpy as np

def isAdjacent(stone1,stone2):
    x1,y1 = stone1
    x2,y2 = stone2

    isAdjacent = False
    if y1==y2 and abs(x2-x1)==1:
        isAdjacent = True
    if x1==x2 and abs(y2-y1)==1:
        isAdjacent = True
    elif abs(y2-y1)==1 and abs(x2-x1)==1 and y2-y1==x1-x2:
        isAdjacent = True
    
    return isAdjacent


class board():
    

    #keep track of moves and connections as we go

    #need full history of connections for undoing

    def __init__(self,size):
        self.size = size
        self.turn = 0

        #initialize white with chains at top and bottom: (x,-1) and (x,size)
        self.wChains = [set([(x,-1) for x in range(self.size)]), set([(x,self.size) for x in range(self.size)])]
        self.bChains = [set([(-1,y) for y in range(self.size)]), set([(self.size,y) for y in range(self.size)])]
        self.moveList = []
        self.legalMoves = set([(x,y) for x in range(self.size) for y in range(self.size)])
        self.win = 0 #1 for white, -1 for black
   
    def move(self,move):
        x,y = move

        if move not in self.legalMoves:
            print("Illegal move")
            return 0 #a better return value?
        else:
            self.moveList.append(move)
            self.legalMoves.remove(move)
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

    def view(self):
        boardState =  [[0 for x in range(self.size)] for y in range(self.size)]
        for i,move in enumerate(self.moveList):
            x,y = move
            if i%2==0:
                boardState[y][x] = 1
            else:
                boardState[y][x] = 2

        for i,row in enumerate(boardState[::-1]):
            print((self.size-i)*" "+" ".join(str(x) for x in row))
        
        return

    def undo(self):
        if self.turn>0:
            self.legalMoves.add(self.moveList.pop())
            self.turn-=1
            self.win = 0
            
            if (0,-1) in mergedChain and (0,self.size) in mergedChain:
                self.win=1
            if (-1,0) in mergedChain and (self.size,0) in mergedChain:
                self.win=-1
        else:
            print("No moves left")


    def evaluate(self):       #map boardstate to a score
        if self.win==0:
            return random()*2-1
        else:
            return self.win    
    #plan for NN:
    #return nn_evaluate(makeBoardState())
    

    def minmax(self,depth=3):
        if depth<=0 or self.win!=0:
            score = self.evaluate()
            return score

        if self.turn%2==0:  #white, maximizing
            score = -np.inf
            for move in self.legalMoves:
                self.move(move)
                moveValue = self.minmax(depth-1)
                self.undo()
                if moveValue>score:
                    score = moveValue
            return score
            
        else: #black, minimizing
            score = np.inf
            for move in self.legalMoves:
                self.move(move)
                moveValue = self.minmax(depth-1)
                self.undo()
                if moveValue<score:
                    score = moveValue
            return score

    def minmax_and_move(self):
        #calculate minmax of every move, then play highest/lowest score
        if self.turn%2==0: #white, select highest-scoring move
            score = -np.inf
            bestmove = (-1,-1)
            for move in self.legalMoves:
                self.move(move)
                moveValue = self.minmax(2)
                self.undo()
                print(move,moveValue,"MAX")
                if moveValue>score:
                    bestmove = move
                    score = moveValue

        else: #black, select lowest-scoring move
            score = np.inf
            bestmove = (-1,-1)
            for move in self.legalMoves:
                self.move(move)
                moveValue = self.minmax(2)
                self.undo()
                print(move,moveValue,"MIN")
                if moveValue<score:
                    bestmove = move
                    score = moveValue

        print(bestmove,score)
        self.move(bestmove)
        return


wwins = 0
bwins = 0

for size in [3]:
    for x in range(1):
        testBoard = board(size)
        testBoard.view()
        
        count = 0
        while testBoard.win==0:
            count+=1
            if count>16:
                print("BREAK!")
                break
            #move_ind = randrange(len(testBoard.legalMoves))
            #move = list(testBoard.legalMoves)[move_ind]
            
            
            
            testBoard.minmax_and_move()
            testBoard.view()
            
            print("")
            if testBoard.win==1:
                print("white won!")
                wwins+=1
            elif testBoard.win==-1:
                print("black won!")
                bwins+=1
                
    #print(size,wwins,bwins)
    #p=wwins/(wwins+bwins)
    #print(p,"+/-",(p*(1-p)*(wwins+bwins)**-1)**.5)


#class board():
#
#    def __init__(self,size = 0):
#        self.size = size
#        self.boardState = [[0 for x in range(size)] for y in range(size)]
#        self.moveList = []
#
#    def isWhiteToMove(self):
#        return self.turn % 2 == 0
#    
#    def isAdjacent(self,x1,y1,x2,y2):
#        isAdjacent = False
#        
#        if all(val<self.size for val in [x1,y1,x2,y2]) and all(val>=0 for val in [x1,y1,x2,y2]):
#            if y1==y2 and abs(x2-x1)==1:
#                isAdjacent = True
#            if x1==x2 and abs(y2-y1)==1:
#                isAdjacent = True
#            elif abs(y2-y1)==1 and abs(x2-x1)==1 and y2-y1==x1-x2:
#                isAdjacent = True
#        return isAdjacent
#
#    def getConnected(self,x1,y1):
#        connected = []
#        if self.boardState[y1][x1]!=0:
#            for x in range(-1,2):
#                for y in range(-1,2):
#                    if self.isAdjacent(x1,y1,x1+x,y1+y) and self.boardState[y1+y][x1+x]==self.boardState[y1][x1]:
#                        connected.append((x1+x,y1+y))
#            return connected
#        else:
#            return []
#    
#
#    def view(self):
#        for i,row in enumerate(self.boardState[::-1]):
#            print((self.size-i)*" "+" ".join(str(x) for x in row))
#
#    def getSize(self):
#        return self.size
#            
#    turn = 0
#    lastMove = (50,50)
#
#    def move(self,x,y):
#        if x<self.size and y<self.size:
#            if self.boardState[y][x]==0:
#                if self.isWhiteToMove():
#                    self.boardState[y][x] = 1
#                else:
#                    self.boardState[y][x] = 2
#                self.boardState
#                self.turn+=1
#                self.moveList.append((x,y))
#                #print(self.moveList)
#                return self.turn
#            else:
#                #print("Move already played")
#                return -2
#        else:
#            print("Out of bounds!")
#            return -1
#
#    def undo(self):
#        if self.turn<0:
#            return
#        else:
#            #print('lastmove:',self.moveList[-1])
#            lastMove = self.moveList[-1]
#            self.boardState[lastMove[1]][lastMove[0]] = 0
#            self.turn-=1
#            self.moveList.pop()
#
#    def recurse(self,path,color):
#        #check if any of path are in bottom row for win
#        
#        newpath = path
#        for p in path:
#            connections = self.getConnected(p[0],p[1])
#            if set(connections) - set(path)==set():
#                continue
#            else:
#                newpath+= list(set(connections)-set(path))
#        
#        if 0 in [p[1] for p in path] and color==1:
#            return True
#        if 0 in [p[0] for p in path] and color==2:
#            return True
#        if path == newpath:
#            return False
#        else:
#            self.recurse(newpath)
#
#    def findWin(self):
#        #start with white (ones, vertical)
#        
#        #start at top edge
#        for x in range(len(self.boardState[-1])):
#            if self.boardState[-1][x]==1:
#                if self.recurse([(x,self.size-1)],1):
#                    #print("White Wins!")
#                    return 1
#        
#        #for black, start at right edge
#        for y in range(self.size):
#            if self.boardState[y][-1]==2:
#                if self.recurse([(self.size-1,y)],2):
#                    #print("Black Wins!")
#                    return 2
#        
#        return False
#
#    def getLegalMoves(self):
#        moves = []
#        for x in range(self.size):
#            for y in range(self.size):
#                if self.boardState[y][x]==0:
#                    moves.append((x,y))
#        return moves
#                
#def evaluator(board):
#    win = board.findWin()
#    if win==1:
#        return 1
#    elif win==2:
#        return -1
#    #if win>0:
#    #    return -1*int(2*(win-1.5))
#    else:
#        return  (random.random()-.5)
#
#                
#def minmax(depth, board):
#    
#    #returns the 'best' move and score
#    #evaluator gives + as good for white, - good for black
#
#    #print("depth:",depth,"turn",board.turn)
#    moves = board.getLegalMoves()
#    
#    if len(moves)==0:
#        return []
#
#    evaluatedMoves = []
#    for move in moves:
#        turn = board.turn
#        output = board.move(move[0],move[1])
#        if depth<=0 or len(moves)==1:
#            evaluatedMoves.append( [evaluator(board), move] )
#        else:
#            evaluatedMoves.append( [ minmax(depth-1,board)[0],move] )
#        board.undo()
#        #board.view()
#        board.turn = turn
#    
#    #print(evaluatedMoves)
#    #board.view()
#    random.shuffle(evaluatedMoves)#pick ties randomly
#    if board.isWhiteToMove():
#        bestScore = max([eMove[0] for eMove in evaluatedMoves])
#    else:
#        bestScore = min([eMove[0] for eMove in evaluatedMoves])
#
#    bestMove = [eMove[1] for eMove in evaluatedMoves if eMove[0]==bestScore][0]
#
#
#    return [bestScore, bestMove]
#
#
#
#
#for size in [3]:
#    white_wins = 0
#    games = 20
#    for i in range(games):
#        aBoard = board(size)
#    
#        for x in range(size**2):
#            print("turn",aBoard.turn) 
#            score, move = minmax(4, aBoard)
#            #moves = aBoard.getLegalMoves()
#            #move = moves[random.randint(0,len(moves)-1)]
#            aBoard.move(move[0],move[1])
#            aBoard.view()
#            print("MOVE SCORE:",score) 
#            #aBoard.move(random.randint(0,aBoard.getSize()-1),random.randint(0,aBoard.getSize()-1))
#            #print("")
#            #aBoard.view()
#
#            win = aBoard.findWin()
#            if win>0:
#                aBoard.view()
#                print("WIN!\n")
#                break
#        if win==1:
#            white_wins+=1
#        #print(aBoard.getConnected(1,1))
#    
#    print("summary")
#    print(size,white_wins,games-white_wins)
##aBoard.view()
##aBoard.move(0,0)
##aBoard.view()
##aBoard.move(1,1)
##aBoard.view()
