#what's the plan?
#
#have a hex board object that:
#	can be viewed with state()
#	can be updated with move(x,y)
#	can test if a move is legal ???
#	can detect if a side has won
import random

class board():

    def __init__(self,size = 0):
        self.size = size
        self.boardState = [[0 for x in range(size)] for y in range(size)]
        self.moveList = []

    def isWhiteToMove(self):
        return self.turn % 2 == 0
    
    def isAdjacent(self,x1,y1,x2,y2):
        isAdjacent = False
        
        if all(val<self.size for val in [x1,y1,x2,y2]) and all(val>=0 for val in [x1,y1,x2,y2]):
            if y1==y2 and abs(x2-x1)==1:
                isAdjacent = True
            if x1==x2 and abs(y2-y1)==1:
                isAdjacent = True
            elif abs(y2-y1)==1 and abs(x2-x1)==1 and y2-y1==x1-x2:
                isAdjacent = True
        return isAdjacent

    def getConnected(self,x1,y1):
        connected = []
        if self.boardState[y1][x1]!=0:
            for x in range(-1,2):
                for y in range(-1,2):
                    if self.isAdjacent(x1,y1,x1+x,y1+y) and self.boardState[y1+y][x1+x]==self.boardState[y1][x1]:
                        connected.append((x1+x,y1+y))
            return connected
        else:
            return []
    

    def view(self):
        for i,row in enumerate(self.boardState[::-1]):
            print((self.size-i)*" "+" ".join(str(x) for x in row))

    def getSize(self):
        return self.size
            
    turn = 0
    lastMove = (50,50)

    def move(self,x,y):
        if x<self.size and y<self.size:
            if self.boardState[y][x]==0:
                if self.isWhiteToMove():
                    self.boardState[y][x] = 1
                else:
                    self.boardState[y][x] = 2
                self.boardState
                self.turn+=1
                self.moveList.append((x,y))
                #print(self.moveList)
                return self.turn
            else:
                #print("Move already played")
                return -2
        else:
            print("Out of bounds!")
            return -1

    def undo(self):
        if self.turn<0:
            return
        else:
            #print('lastmove:',self.moveList[-1])
            lastMove = self.moveList[-1]
            self.boardState[lastMove[1]][lastMove[0]] = 0
            self.turn-=1
            self.moveList.pop()

    def recurse(self,path,color):
        #check if any of path are in bottom row for win
        
        newpath = path
        for p in path:
            connections = self.getConnected(p[0],p[1])
            if set(connections) - set(path)==set():
                continue
            else:
                newpath+= list(set(connections)-set(path))
        
        if 0 in [p[1] for p in path] and color==1:
            return True
        if 0 in [p[0] for p in path] and color==2:
            return True
        if path == newpath:
            return False
        else:
            self.recurse(newpath)

    def findWin(self):
        #start with white (ones, vertical)
        
        #start at top edge
        for x in range(len(self.boardState[-1])):
            if self.boardState[-1][x]==1:
                if self.recurse([(x,self.size-1)],1):
                    #print("White Wins!")
                    return 1
        
        #for black, start at right edge
        for y in range(self.size):
            if self.boardState[y][-1]==2:
                if self.recurse([(self.size-1,y)],2):
                    #print("Black Wins!")
                    return 2
        
        return False

    def getLegalMoves(self):
        moves = []
        for x in range(self.size):
            for y in range(self.size):
                if self.boardState[y][x]==0:
                    moves.append((x,y))
        return moves
                
def evaluator(board):
    win = board.findWin()
    if win==1:
        return 1
    elif win==2:
        return -1
    #if win>0:
    #    return -1*int(2*(win-1.5))
    else:
        return  (random.random()-.5)

                
def minmax(depth, board):
    
    #returns the 'best' move and score
    #evaluator gives + as good for white, - good for black

    #print("depth:",depth,"turn",board.turn)
    moves = board.getLegalMoves()
    
    if len(moves)==0:
        return []

    evaluatedMoves = []
    for move in moves:
        turn = board.turn
        output = board.move(move[0],move[1])
        if depth<=0 or len(moves)==1:
            evaluatedMoves.append( [evaluator(board), move] )
        else:
            evaluatedMoves.append( [ minmax(depth-1,board)[0],move] )
        board.undo()
        #board.view()
        board.turn = turn
    
    #print(evaluatedMoves)
    #board.view()
    random.shuffle(evaluatedMoves)#pick ties randomly
    if board.isWhiteToMove():
        bestScore = max([eMove[0] for eMove in evaluatedMoves])
    else:
        bestScore = min([eMove[0] for eMove in evaluatedMoves])

    bestMove = [eMove[1] for eMove in evaluatedMoves if eMove[0]==bestScore][0]


    return [bestScore, bestMove]




for size in [3]:
    white_wins = 0
    games = 20
    for i in range(games):
        aBoard = board(size)
    
        for x in range(size**2):
            print("turn",aBoard.turn) 
            score, move = minmax(4, aBoard)
            #moves = aBoard.getLegalMoves()
            #move = moves[random.randint(0,len(moves)-1)]
            aBoard.move(move[0],move[1])
            aBoard.view()
            print("MOVE SCORE:",score) 
            #aBoard.move(random.randint(0,aBoard.getSize()-1),random.randint(0,aBoard.getSize()-1))
            #print("")
            #aBoard.view()

            win = aBoard.findWin()
            if win>0:
                aBoard.view()
                print("WIN!\n")
                break
        if win==1:
            white_wins+=1
        #print(aBoard.getConnected(1,1))
    
    print("summary")
    print(size,white_wins,games-white_wins)
#aBoard.view()
#aBoard.move(0,0)
#aBoard.view()
#aBoard.move(1,1)
#aBoard.view()
