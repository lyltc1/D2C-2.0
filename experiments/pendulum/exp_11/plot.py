# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import matplotlib.pyplot as plt
import brewer2mpl
import matplotlib as mpl
from scipy import signal 
    
def perfcheck(nstart=0,nend=100,noisemax=100):
    
    bmap = brewer2mpl.get_map('Set2','qualitative', 7)
    colors = bmap.mpl_colors

    params = {
    'axes.labelsize': 15,
    'font.size': 12,
    'legend.fontsize': 15,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'text.usetex': True ,
    'figure.figsize': [8, 6], # instead of 4.5, 4.5
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'ps.useafm' : True,
    'pdf.use14corefonts':True,
    'pdf.fonttype': 42,
    'ps.fonttype': 42
     }
    mpl.rcParams.update(params)

    #D2C-2.0
    i, x, y = np.loadtxt('pendulum_testing_data.txt', dtype=np.float64, delimiter=',\t',  unpack=True, usecols=(0,1,2))
    i = 100*i
    plt.figure(1)
    plt.plot(i,x,color=colors[1], linewidth=4)
    #plt.plot(i, (x+y), alpha=0.3, color='orange')
    #plt.plot(i, (x-y), alpha=0.3, color='orange')
    plt.fill_between(i, (x+y), (x-y), alpha=0.3, color=colors[1])


    #DDPG
    DDPG_testing_data_location = "/media/karthikeya/Elements/DDPG_D2C/results/Pendulum/exp_9/"
    i, x, y, z, a = np.loadtxt(DDPG_testing_data_location + 'data.txt', dtype=np.float64, delimiter=',\t',  unpack=True, usecols=(0,1,2,3,4))
    i = 100*i
    
    plt.plot(i,x,color=colors[2], linewidth=4)
    #plt.plot(i, (x+y), alpha=0.3, color='orange')
    #plt.plot(i, (x-y), alpha=0.3, color='orange')
    plt.fill_between(i, (x+y), (x-y), alpha=0.2, color=colors[2])

    #plt.xlabel(" Percent of max. control (Std dev of perturbed noise)", fontsize=16)
    #plt.ylabel("Terminal state MSE (Avergaed over {} samples)".format(n_samples), fontsize=16)
    plt.grid(axis='y', color='.910', linestyle='-', linewidth=1.5)
    plt.grid(axis='x', color='.910', linestyle='-', linewidth=1.5)
    #plt.tight_layout()
    plt.legend(['D2C','DDPG'], loc='upper left', fontsize='xx-large')
    
    plt.xlabel('Std dev of perturbed noise (Percent of max. control)', fontweight='bold',fontsize=22)
    plt.ylabel('L2-norm of terminal state error', fontweight='bold', fontsize=25)
    plt.grid(True)
    plt.show()  
    print('averaged by {value1} rollouts'.format(value1=y.shape[1]))

perfcheck()