'''
Created on Aug 7, 2016

@author: robertday
'''

import numpy as np
import numpy.random as random
import pickle

def construct_tiling(N_dim,tile_per_dim,nb_of_tiling,range_per_dim):
    '''
    Constructs tiling for uniform grids. 
    N_dim: number of dimensions
    tile_per_dim: number of tiles per dimension (passed as a N_dim dimensional list)
    nb_of_tiling: number of tiling to generate
    range_per_dim: range per dimension given as (N_dim,2) dimensions list
    
    Returns a nb_of_tiling dimensional list of N_dim dimensional list. Each of the latter list is a N_dim dimensional list
    of numpy arrays representing the centers of the tiling along the various dimensions
    '''
    
    all_tiling=[]    
    for i in range(nb_of_tiling):
    
        tiling_centers=[]
    
        for d in range(N_dim):
            d1=(range_per_dim[d][1]-range_per_dim[d][0])/tile_per_dim[d]
            tiling_centers_dim1=np.arange(range_per_dim[d][0],range_per_dim[d][1],d1)+d1/2
            tiling_centers_dim1+=(np.random.rand()*d1-d1*0.5)
            tiling_centers.append(tiling_centers_dim1)
        all_tiling.append(tiling_centers)
    
    all_tiling2=[]
    
    for d in range(N_dim):
        tmp=np.zeros((nb_of_tiling,tile_per_dim[d]))
        for i in range(nb_of_tiling):
            tmp[i]=all_tiling[i][d]
        all_tiling2.append(tmp)
    
    
    # Returned object : first index is dimension, second index is tiling
    return all_tiling2


def find_closest_index(value,tiling):
    pos=np.searchsorted(tiling,value)
    if pos==0:
        return 0
    elif pos==len(tiling):
        return len(tiling)-1
    else:
        return pos-1+np.argmin([abs(tiling[pos-1]-value),abs(tiling[pos]-value)])

def real_to_tiling(state_real,tiling):
    dim=0
    ind_state=[]
    ind=0
    for s in state_real:
        tile_begin=0
        tmp=[]
        l=len(tiling[dim])
        for tile in range(l):
            ind=find_closest_index(s,tiling[dim][tile])+tile_begin
            tmp.append(ind)
            tile_begin+=len(tiling[dim][tile])
        ind_state.append(tmp)
        dim+=1
        ind=0
    return ind_state

#===============================================================================
# tiling=construct_tiling(2,[3,3],10,[[-1.2,0.5],[-0.07,0.07]])
# print(tiling)
# print(real_to_tiling([0.1,-0.03],tiling))
# exit()
#===============================================================================



global action_set
action_set=[-1,0,1]

def update_state(current_state,action):
    
    '''
    
    Return fidelity
    Put in variables, 
    
    '''
    
    
    terminate=False
    old_pos,old_v=current_state
    
    # Updating velocity:
    new_velocity=old_v+0.001*action_set[action]-0.0025*np.cos(3.*old_pos)
    
    # Maximum velocity ! (presence of friction)
    if new_velocity < -0.07:
        new_velocity=-0.07
    elif new_velocity > 0.07:
        new_velocity=0.07
    
    # Updating position:
    new_pos=old_pos+new_velocity
    
    if new_pos < -1.2:
        new_pos=-1.2
        new_velocity=0.0
    elif new_pos > 0.5:
        terminate=True
    
    return (new_pos,new_velocity),terminate
 
 
def select_action(Theta,indTheta,eps):
    ''' 
     epsilon-greedy function for selecting action
     Q is the state action value function
     indTheta are the non-zero feature for the current state
     eps is the exploration rate
    '''
    if random.uniform() < eps:
        #Explore
        new_action=random.randint(0,3)
        
    else: 
        #Greedy
        set_action=np.array([compute_Q(Theta,indTheta,a) for a in range(3)])
        new_action=np.argmax(set_action)
        #print(set_action,new_action)
        
    Q_new_action=compute_Q(Theta,indTheta,new_action)
    
    return new_action,Q_new_action
    
        
def compute_Q(Theta,indTheta,action):
    '''
    Can concatenate dimensions too ... just add 100 to second dimension 
    '''
    
    val=np.sum(Theta[0,indTheta[0],action])
    return val+np.sum(Theta[1,indTheta[1],action])

  
def Q_learning(nb_episode=100,alpha=0.05,eps=0.1,gamma=1.0,lmbda=0.9):
    ''' SARSA
    alpha is the learning rate (for gradient descent)
    eps is the exploration rate
    gamma is the discount factor
    lmbda is the trace decay rate    
     '''
    
    tiling=construct_tiling(2,[10,10],10,[[-1.2,0.5],[-0.07,0.07]])
    Theta=np.zeros((2,100,3),dtype=np.float32)
    R=-1
    
    #print("Tiling\n",tiling)
    #print("Tiling,shape:\t",np.shape(tiling))
    #print("Theta, shape:\t",np.shape(Theta))
    #theta=np.empty((2,100),dtype=np.int8) 
    
    #indTheta=real_to_tiling(init_state_real,tiling)
    for Ep in range(nb_episode):
        #print("Episode",Ep)
        
        trace=np.zeros(Theta.shape,dtype=np.float32)
        current_state_real=(random.uniform(-1.2,0.5),random.uniform(-0.07,0.07))
        
        indTheta=real_to_tiling(current_state_real,tiling)
        
        action=np.random.randint(0,3)
        #print("trace\t",trace)
        #print("current_state_real\t",current_state_real)
        #print("indTheta\t",indTheta)
        #print("action\t",action)
        
        i=0
        while True:
            #print("ITERATION NO:\t",i)
            #if(i>5): break
            
            ### UNWRAP this a bit .... divergence.
            trace[0,indTheta[0],action]=1. # use replacing traces !
            trace[1,indTheta[1],action]=1.
            #print("TRACE:\n",trace) 
            #if (i+1)%1000==0: print(i)#"\t",current_state_real)
            #if i>100: break
            #i+=1
            
            # Take action
            new_state_real,terminate=update_state(current_state_real,action)
            #print("new_state_real\t",new_state_real)
        
            indTheta_new=real_to_tiling(new_state_real,tiling)
            Q=compute_Q(Theta,indTheta,action)
            #print("Q estimate:\t",Q)
            
            delta=R-Q
            
            # Terminate here
            if terminate:
                Theta+=alpha*delta*trace
                break
            
            new_action,Q_new_action=select_action(Theta,indTheta_new,eps)
            
            delta+=gamma*Q_new_action
            Theta+=alpha*delta*trace
            trace*=gamma*lmbda
            
            current_state_real=new_state_real   
            indTheta=indTheta_new
            action=new_action
            
            i+=1
    
        #print("Episode Length:\t",i)
        #print(Theta)
    
    #print(Theta)
    return Theta,tiling

#===============================================================================
# random.seed(10)       
# Theta,tiling=Q_learning(nb_episode=9000,alpha=0.05,eps=0.1,gamma=1.0,lmbda=0.9)
# resultfile = open('res9000.pkl', 'wb')
# 
# pickle.dump((Theta,tiling),resultfile)
# resultfile.close()
#===============================================================================

qvalue=[]
np.random.seed()
for ep in [10,40,100,150,200,500,1000,2000]:
    Theta,tiling=Q_learning(nb_episode=ep,alpha=0.05,eps=0.1,gamma=1.0,lmbda=0.9)
    qvalue.append([ep,select_action(Theta,real_to_tiling((-0.523599,0.0),tiling),0.0)[1]])
    print(qvalue)

qvalue=np.array(qvalue)
np.savetxt("convergence.txt",qvalue)

exit()



######### PLOTTINGGGGGGGGGGGGGG ###############
 
pkl_file = open('res1000.pkl', 'rb')
t1,til1 = pickle.load(pkl_file)

data=[]
dx=(0.5+1.2)/50
dv=(0.14)/50

for x in np.arange(-1.2,0.5,dx):
    for v in np.arange(-0.07,0.07,dv):
        data.append([x,v,select_action(t1,real_to_tiling((x,v),til1),0.0)[1]])

data=np.array(data)

#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.gca(projection='3d')

ax.plot_trisurf(data[:,0], data[:,1], abs(data[:,2]), cmap=cm.jet, linewidth=0.2)

plt.show()


ax.set_xlabel(r'Position')
ax.set_ylabel(r'Velocity')
ax.set_zlabel(r'max_a{Q(x,v,a)}')

plt.show()

#print(t1==Theta)
#print(til1)
#print(tiling)
pkl_file.close()



# Check if things make sense !
# Try to reproduce book plots !
#perform_greedy(initpos,Theta,tiling)






#tiling=construct_tiling(2,[9,9],10,[[-1.2,0.5],[-0.07,0.07]])


#===============================================================================
# print(tiling[0][0])
# print(find_closest_index(0.129,tiling[0][0]))
# print(np.argmin([0,1,2,3]))    
#===============================================================================
#===============================================================================
# def find_tiling_index(state,tiling):
#     
#     nb_tiling=len(tiling)
#     for i in range(tiling):
#         for 
#     
#===============================================================================


#===============================================================================
# print(tiling[0])
#===============================================================================
#print(construct_tiling(2,[9,9],1,[[-1.2,0.5],[-0.07,0.07]]))
#===============================================================================
# print(tuple([2,2]+[2]))
# a=0,1
# print(a)
# np.arange(a[0])
# print(a[0])
#===============================================================================

#print(np.arange(0.,1,0.05))
#construct_tiling(2,[10,10],1,(1.0,1.0))
        
