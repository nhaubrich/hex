import numpy as np
import h5py
from keras.models import Sequential,load_model
from keras.layers import Dense
from keras.activations import tanh 
from board import *

def initialize_model(N):
    #Initialize model with a bit of random data
    data = np.random.random((1,N*N+1))
    #maybe someday we'll have better data
    X = data[:,:-1]
    y = data[:,-1]
   
    print(X.shape)
    print(y.shape)

    model = Sequential()
    model.add(Dense(N*N, input_dim=N*N, activation=tanh))
    model.add(Dense(N*N, input_dim=N*N, activation=tanh))
    model.add(Dense(N, activation=tanh))
    model.add(Dense(1, activation=tanh))
    
    model.compile(loss="binary_crossentropy", optimizer='adam', metrics=['accuracy'])
    model.fit(X, y>0, epochs=1, batch_size=1)
    
    _, accuracy = model.evaluate(X, y>0)
    print('Accuracy: %.2f' % (accuracy*100))
    
    model.save("hex_ai_%i.h5" % N)

def update_model(N,epochs):

    dataFile = h5py.File("data_%i.h5" % N,'r')
    data = dataFile['data'][:]
    X = data[:,:-1]
    y = data[:,-1]>0
    
    # load model
    model = load_model('hex_ai_%i.h5' % N)
    
    for x in range(epochs):
        print("Epoch ",x)
        #should shuffle/chunk the data
        model.train_on_batch(X, y, sample_weight=None, class_weight=None)
    
    _, accuracy = model.evaluate(X, y)
    print('Accuracy: %.2f' % (accuracy))
    print('White wins: %s out of %s' % (sum(y),len(y)))   
    model.save("hex_ai_%i.h5" % N)
    dataFile.close()

def make_data(N,matches,semirandom=False):
    #run some matches on NxN board
    #save to data.h5 (todo folder with numbered data so it isn't overwitten)
    
    hf = h5py.File('data_%i.h5'%N, 'w')

    allGames = []

    for i in range(matches):
        print "game",i
        Board = board(N)
        while Board.win==0:
            if semirandom:
                if Board.turn % 2 == 0:
                    Board.minmax_and_move(1) #4 minutes on 4x4 with depth=3 
                else:
                    #move random
                    Board.move(list(Board.legalMoves)[np.random.randint(len(Board.legalMoves))])
            
            else:
                Board.minmax_and_move(1) #4 minutes on 4x4 with depth=3 
        Board.view()
        #replay and save each position
        newBoard = board(N)
        
        matchData = np.zeros((Board.turn,N*N+1))
        matchData[0,:-1] = np.ravel(newBoard.makeBoardState())
        
        for i,move in enumerate(Board.moveList):
            newBoard.move(move)
            matchData[i,:-1] = np.ravel(newBoard.makeBoardState())

        matchData[:,-1] = Board.win
        allGames.append(matchData)

    hf.create_dataset('data', data=np.vstack(allGames))
    hf.close()

def selftrain(N):
    make_data(N,10)
    update_model(N,3)

def semirandomtrain(N):
    make_data(N,10,semirandom=True)
    update_model(N,3)


N=2
initialize_model(N)
for batch in range(10):
    semirandomtrain(N)
    selftrain(N)

