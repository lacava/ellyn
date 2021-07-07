# -*- coding: utf-8 -*-
"""
Copyright 2016 William La Cava

license: GNU/GPLv3

"""

import argparse
# from ._version import __version__

from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split
from sklearn.metrics import (r2_score, mean_squared_error, mean_absolute_error, 
                             mean_absolute_error, explained_variance_score, 
                             accuracy_score)
import numpy as np
import pandas as pd
import warnings
import copy
import itertools as it
import pdb
from ellyn.ellen import elgp 
from DistanceClassifier import DistanceClassifier
from functools import wraps
import inspect
import math

class ellyn(BaseEstimator):
    """ellyn uses GP to build its models.

    It uses a stack-based, syntax-free, linear genome for constructing 
    candidate equations. It is built to include different evolutionary methods 
    for system identification adapted from literature. The options include 
    normal tournament selection, deterministic crowding, (epsilon) lexicase 
    selection, and age-pareto fitness selection.

    All algorithm choices are accessible from the command line.

    """
    # @initializer
    def __init__(self,
		 # ============== Generation Settings
		 g=100, # number of generations (limited by default)
		 popsize=500, #population size
		 limit_evals=False, # limit evals instead of generations
		 max_evals=0, # maximum number of evals before termination (only active if limit_evals is true)
                 time_limit=None, # max time to run in seconds (zero=no limit)
		 init_trees= True,
                 selection='tournament',
		 tourn_size=2,
		 rt_rep=0, #probability of reproduction
		 rt_cross=0.6,
		 rt_mut=0.4,
		 cross_ar=0.025, #crossover alternation rate
		 mut_ar=0.025,
		 cross=3, # 1: ultra, 2: one point, 3: subtree
		 mutate=1, # 1: one point, 2: subtree
		 align_dev = False,
		 elitism = False,

		 # ===============   Data settings
		 init_validate_on=False, # initial fitness validation of individuals
		 train=False, # choice to turn on training for splitting up the data set
		 train_pct=0.5, # default split of data is 50/50
		 shuffle_data=False, # shuffle the data
		 test_at_end = False, # only run the test fitness on the population at the end of a run
		 pop_restart = False, # restart from previous population
		 pop_restart_path="", # restart population file path
		 AR = False,
		 AR_nb = 1,
		 AR_nkb = 0,
		 AR_na = 1,
		 AR_nka = 1,
		 AR_lookahead = False,
		 # ================ Results and printing
		 resultspath= './',
		 #savename
		 savename="",
		 #print every population
		 print_every_pop=False,
		 #print initial population
		 print_init_pop = False,
		 #print last population
		 print_last_pop = False,
		 # print homology
		 print_homology = False,
		 #print log
		 print_log = False,
		 #print data
		 print_data = False,
		 #print best individual at end
		 print_best_ind = False,
		 #print archive
		 print_archive = False,
		 # number of log points to print (with eval limitation)
		 num_log_pts = 0,
		 # print csv files of genome each print cycle
		 print_genome = False,
		 # print csv files of epigenome each print cycle
		 print_epigenome = False,
		 # print number of unique output vectors
		 print_novelty = False,
		 # print individuals for graph database analysis
		 print_db = False,
		 # verbosity
		 verbosity = 0,

		 # ============ Fitness settings
		 fit_type = "MSE", # 1: error, 2: corr, 3: combo
		 norm_error = False , # normalize fitness by the standard deviation of the target output
		 weight_error = False, # weight error vector by predefined weights from data file
		 max_fit = 1.0E20,
		 min_fit = 0.00000000000000000001,

		 # Fitness estimators
		 EstimateFitness=False,
		 FE_pop_size=0,
		 FE_ind_size=0,
		 FE_train_size=0,
		 FE_train_gens=0,
		 FE_rank=False,
		 estimate_generality=False,
		 G_sel=1,
		 G_shuffle=False,

		 # =========== Program Settings
                 # list of operators. choices:
                 # n (constants), v (variables), +, -, *, /  
                 # sin, cos, exp, log, sqrt, 2, 3, ^, =, !, <, <=, >, >=, 
                 # if-then, if-then-else, &, | 
                 op_list=['n','v','+','-','*','/'],
                 # weights associated with each operator (default: uniform)
                 op_weight=None,
		 ERC = True, # ephemeral random constants
		 ERCints = False ,
		 maxERC = 1,
		 minERC = -1,
		 numERC = 1,

		 min_len = 3,
		 max_len = 20,
		 max_len_init = 0,
                    
                 # 1: genotype size, 2: symbolic size, 3: effective genotype size
		 complex_measure=1, 


		 # Hill Climbing Settings

		 # generic line hill climber (Bongard)
		 lineHC_on =  False,
		 lineHC_its = 0,

		 # parameter Hill Climber
		 pHC_on =  False,
		 pHC_its = 1,
		 pHC_gauss = 0,

		 # epigenetic Hill Climber
		 eHC_on = False,
		 eHC_its = 1,
		 eHC_prob = 0.1,
		 eHC_init = 0.5,
		 eHC_mut = False, # epigenetic mutation rather than hill climbing
		 eHC_slim = False, # use SlimFitness

                 # stochastic gradient descent
                 SGD = False,
                 learning_rate = 1.0,
		 # Pareto settings

		 prto_arch_on = False,
		 prto_arch_size = 1,
		 prto_sel_on = False,

		 #island model
		 islands = True,
		 num_islands= 0,
		 island_gens = 100,
		 nt = 1,

		 # lexicase selection
		 lexpool = 1.0, # fraction of pop to use in selection events
		 lexage = False, # use afp survival after lexicase selection
		 lex_class = False, # use class-based fitness rather than error
                 # errors within fixed epsilon of the best error are pass, 
                 # otherwise fail
		 lex_eps_error = False, 
                 # errors within fixed epsilon of the target are pass, otherwise fail
		 lex_eps_target = False, 		 
                 # used w/ lex_eps_[error/target], ignored otherwise
		 lex_epsilon = 0.1, 
                 # errors in a standard dev of the best are pass, otherwise fail 
                 lex_eps_std = False, 		 
                 # errors in med abs dev of the target are pass, otherwise fail
                 lex_eps_target_mad=False, 		 
                 # errors in med abs dev of the best are pass, otherwise fail
                 lex_eps_error_mad=False, 
                 # pass conditions in lex eps defined relative to whole 
                 # population (rather than selection pool).
                 # turns on if no lex_eps_* parameter is True. 
                 # a.k.a. "static" epsilon-lexicase
		 lex_eps_global = False,                  
                 # epsilon is defined for each selection pool instead of globally
		 lex_eps_dynamic = False,
                 # epsilon is defined as a random threshold corresponding to 
                 # an error in the pool minus min error in pool 
		 lex_eps_dynamic_rand = False,
                 # with prob of 0.5, epsilon is replaced with 0
		 lex_eps_dynamic_madcap = False,

		 #pareto survival setting
		 PS_sel=1,

		 # classification
		 classification = False,
		 class_bool = False,
		 class_m4gp = False,
		 class_prune = False,

		 stop_condition=True,
		 stop_threshold = 0.000001,
		 print_protected_operators = False,

		 # return population to python
		 return_pop = False,
                 ################################# wrapper specific params
                 scoring_function=None,
                 random_state=None,
                 lex_meta=None,
                 seeds=None,    # seeding building blocks (equations)
                 ):
         self.g=g 
         self.popsize=popsize 
         self.limit_evals=limit_evals 
         self.max_evals=max_evals 
         self.time_limit=time_limit
         self.init_trees=init_trees
         # Generation Settings
         self.selection=selection
         self.tourn_size=tourn_size
         self.rt_rep=rt_rep 
         self.rt_cross=rt_cross
         self.rt_mut=rt_mut
         self.cross_ar=cross_ar 
         self.mut_ar=mut_ar
         self.cross=cross 
         self.mutate=mutate 
         self.align_dev =align_dev 
         self.elitism =elitism 

         # ===============   Data settings
         self.init_validate_on=init_validate_on 
         self.train=train 
         self.train_pct=train_pct 
         self.shuffle_data=shuffle_data 
         self.test_at_end =test_at_end  
         self.pop_restart =pop_restart  
         self.pop_restart_path=pop_restart_path 
         self.AR =AR 
         self.AR_nb =AR_nb 
         self.AR_nkb =AR_nkb 
         self.AR_na =AR_na 
         self.AR_nka =AR_nka 
         self.AR_lookahead =AR_lookahead 
         # ================ Results and printing
         self.resultspath=resultspath
         self.savename=savename
         self.print_every_pop=print_every_pop
         self.print_init_pop =print_init_pop 
         self.print_last_pop =print_last_pop 
         self.print_homology =print_homology 
         self.print_log =print_log 
         self.print_data =print_data 
         self.print_best_ind =print_best_ind 
         self.print_archive =print_archive 
         self.num_log_pts =num_log_pts 
         self.print_genome =print_genome 
         self.print_epigenome =print_epigenome 
         self.print_novelty =print_novelty 
         self.print_db =print_db 
         self.verbosity =verbosity 

         # ============ Fitness settings
         self.fit_type =fit_type  
         self.norm_error =norm_error  
         self.weight_error =weight_error  
         self.max_fit =max_fit 
         self.min_fit =min_fit 

         # Fitness estimators
         self.EstimateFitness = EstimateFitness
         self.FE_pop_size=FE_pop_size
         self.FE_ind_size=FE_ind_size
         self.FE_train_size=FE_train_size
         self.FE_train_gens=FE_train_gens
         self.FE_rank=FE_rank
         self.estimate_generality=estimate_generality
         self.G_sel=G_sel
         self.G_shuffle=G_shuffle

         # =========== Program Settings
         self.op_list = op_list
         self.op_weight = op_weight
         self.ERC =ERC  
         self.ERCints =ERCints 
         self.maxERC =maxERC 
         self.minERC =minERC 
         self.numERC =numERC 

         self.min_len =min_len 
         self.max_len =max_len 
         self.max_len_init =max_len_init 

         self.complex_measure=complex_measure 


         # Hill Climbing Settings

         # generic line hill climber (Bongard)
         self.lineHC_on =lineHC_on 
         self.lineHC_its =lineHC_its 

         # parameter Hill Climber
         self.pHC_on =pHC_on 
         self.pHC_its =pHC_its 
         self.pHC_gauss =pHC_gauss 

         # epigenetic Hill Climber
         self.eHC_on =eHC_on 
         self.eHC_its =eHC_its 
         self.eHC_prob =eHC_prob 
         self.eHC_init =eHC_init 
         self.eHC_mut =eHC_mut  # epigenetic mutation rather than hill climbing
         self.eHC_slim =eHC_slim  # use SlimFitness

         # stochastic gradient descent
         self.SGD =SGD 
         self.learning_rate =learning_rate 

         # Pareto settings
         self.prto_arch_on =prto_arch_on 
         self.prto_arch_size =prto_arch_size 
         self.prto_sel_on =prto_sel_on 
         self.PS_sel=PS_sel

         #island model
         self.islands =islands 
         self.num_islands=num_islands
         self.island_gens =island_gens 
         self.nt =nt 

         # lexicase selection
         self.lexpool =lexpool 
         self.lexage =lexage 
         self.lex_class =lex_class 
         self.lex_eps_error =lex_eps_error  
         self.lex_eps_target =lex_eps_target  
         self.lex_eps_std =lex_eps_std  
         self.lex_eps_target_mad=lex_eps_target_mad 
         self.lex_eps_error_mad=lex_eps_error_mad 
         self.lex_epsilon =lex_epsilon 
         self.lex_eps_global =lex_eps_global  
         self.lex_eps_dynamic =lex_eps_dynamic 
         self.lex_eps_dynamic_rand =lex_eps_dynamic_rand 
         self.lex_eps_dynamic_madcap =lex_eps_dynamic_madcap 
         self.lex_meta=lex_meta

         # classification
         self.classification =classification 
         self.class_bool =class_bool 
         self.class_m4gp =class_m4gp 
         self.class_prune =class_prune 
         self.stop_condition=stop_condition
         self.stop_threshold =stop_threshold 
         self.print_protected_operators =print_protected_operators 
         self.return_pop =return_pop 
         self.scoring_function=scoring_function
         self.selection=selection

         #seed
         self.random_state = random_state
         self.seeds = seeds


    # def get_params(self, deep=True):
    #     return {k:v for k,v in self.__dict__.items() if not k.endswith('_')}

    def _init(self):
        """Tweaks parameters to harmonize with ellen"""
        np.random.seed(self.random_state)

        ellen_params = self.get_params()
        # set sel number from selection
        ellen_params['sel'] = {'tournament': 1,
                            'dc':2,'lexicase': 3,
                            'epsilon_lexicase': 3,
                            'afp': 4,
                            'rand': 5,
                            None: 1}[self.selection]
        if self.scoring_function is None:
            if self.fit_type:
                self.scoring_function_ = {'MAE':mean_absolute_error,
                                         'MSE':mean_squared_error,
                                         'R2':r2_score,
                                         'VAF':explained_variance_score,
                                         'combo':mean_absolute_error,
                                         'F1':accuracy_score,
                                         'F1W':accuracy_score}[self.fit_type]
            elif self.classification:
                self.scoring_function_ = accuracy_score
            else:
                self.scoring_function_ = mean_squared_error
        else:
            self.scoring_function_ = self.scoring_function

        #default to M4GP in the case no classifier specified
        if self.classification and not self.class_m4gp and not self.class_bool:
            ellen_params['class_m4gp'] = True
        elif not self.classification:
            ellen_params['class_m4gp'] = False

        if self.op_weight:
            assert len(self.op_weight) == len(self.op_list)
            ellen_params['weight_ops_on'] = True

        if self.lex_meta:
            ellen_params['lex_metacases'] = self.lex_meta.split(',')

        if self.selection=='epsilon_lexicase':
            ellen_params['lex_eps_error_mad'] = True

        self.best_estimator_ = []
        self.hof_ = []

        for k in list(ellen_params.keys()):
            if ellen_params[k] is None:
                del ellen_params[k]

        if self.prto_arch_on:
            ellen_params['train'] = True
            ellen_params['train_pct'] = 0.8

        if self.verbosity > 0:
            print('ellen_params:',ellen_params)
        return ellen_params

    def fit(self, features, labels):
        """Fit model to data"""
        # get parameters
        self.ellen_params_ = self._init() 

        if self.prto_arch_on and self.classification:
            # if classification, make the train/test split even across class
            train_i, val_i = train_test_split(
                    np.arange(features.shape[0]),
                    stratify=labels,
                    train_size=0.8,
                    test_size=0.2,
                    random_state=self.random_state)
            features = features[list(train_i)+list(val_i)]
            labels = labels[list(train_i)+list(val_i)]

        result = []
        if self.verbosity>1:
            print(10*'=','params',10*'=',sep='\n')
            for key,item in self.ellen_params_.items():
                print(key,':',item)
        # run ellenGP
        elgp.runEllenGP(self.ellen_params_,
                        np.asarray(features,dtype=np.float32,order='C'),
                        np.asarray(labels,dtype=np.float32,order='C'),
                        result)
        # print("best program:",self.best_estimator_)

        if self.prto_arch_on or self.return_pop:
            # a set of models is returned. choose the best
            if self.verbosity>0: print('Evaluating archive set...')
            # unpack results into model, train and test fitness
            self.hof_ = [r[0] for r in result]
            self.fit_t = [r[1] for r in result]
            self.fit_v = [r[2] for r in result]
            # best estimator has lowest internal validation score
            self.best_estimator_ = self.hof_[np.argmin(self.fit_v)]
        else:
            # one model is returned
            self.best_estimator_ = result

        # if M4GP is used, call Distance Classifier and fit it to the best
        if self.class_m4gp:
            if self.verbosity > 0: print("Storing DistanceClassifier...")
            self.DC = DistanceClassifier()
            self.DC.fit(self._out(self.best_estimator_,features),labels)

        ####     
        # print final models
        if self.verbosity>0:
             print("final model(s):")
             if self.prto_arch_on or self.return_pop:
                 for m in self.hof_[::-1]:
                     if m is self.best_estimator_:
                         print('[best]',self.stack_2_eqn(m),sep='\t')
                     else:
                         print('',self.stack_2_eqn(m),sep='\t')
             else:
                 print('best model:',self.stack_2_eqn(self.best_estimator_))

        return self

    def predict(self, testing_features, ic=None):
        """predict on a holdout data set.
        ic: initial conditions, needed for dynamic models
        """
        # print("best_inds:",self._best_inds)
        # print("best estimator size:",self.best_estimator_.coef_.shape)
        # tmp = self._out(self.best_estimator_,testing_features)
        #
        if self.class_m4gp:
            return self.DC.predict(self._out(self.best_estimator_,testing_features))
        else:
            return self._out(self.best_estimator_,testing_features,ic)

    def fit_predict(self, features, labels):
        """Convenience function that fits a pipeline then predicts on the provided features

        Parameters
        ----------
        features: array-like {n_samples, n_features}
            Feature matrix
        labels: array-like {n_samples}
            List of class labels for prediction

        Returns
        ----------
        array-like: {n_samples}
            Predicted labels for the provided features

        """
        self.fit(features, labels)
        return self.predict(features)

    def score(self, testing_features, testing_labels,ic=None):
        """estimates accuracy on testing set"""
        # print("test features shape:",testing_features.shape)
        # print("testing labels shape:",testing_labels.shape)
        yhat = self.predict(testing_features,ic)
        return self.scoring_function_(testing_labels,yhat)

    def export(self, output_file_name):
        """does nothing currently"""

    def _eval(self,n, features, stack_float, stack_bool, y= None):
        """evaluation function for best estimator"""
        eval_dict = {
        # float operations
            '+': lambda n,features,stack_float,stack_bool: stack_float.pop() + stack_float.pop(),
            '-': lambda n,features,stack_float,stack_bool: stack_float.pop() - stack_float.pop(),
            '*': lambda n,features,stack_float,stack_bool: stack_float.pop() * stack_float.pop(),
            '/': lambda n,features,stack_float,stack_bool: self.divs(stack_float.pop(),stack_float.pop()),
            's': lambda n,features,stack_float,stack_bool: np.sin(stack_float.pop()),
            'a': lambda n,features,stack_float,stack_bool: np.arcsin(stack_float.pop()),
            'c': lambda n,features,stack_float,stack_bool: np.cos(stack_float.pop()),
            'd': lambda n,features,stack_float,stack_bool: np.arccos(stack_float.pop()),
            'e': lambda n,features,stack_float,stack_bool: np.exp(stack_float.pop()),
            'l': lambda n,features,stack_float,stack_bool: self.logs(np.asarray(stack_float.pop())),#np.log(np.abs(stack_float.pop())),
            'x':  lambda n,features,stack_float,stack_bool: features[:,n[2]],
            'k': lambda n,features,stack_float,stack_bool: np.ones(features.shape[0])*n[2],
            '2': lambda n,features,stack_float,stack_bool: stack_float.pop()**2,
            '3': lambda n,features,stack_float,stack_bool: stack_float.pop()**3,
            'q': lambda n,features,stack_float,stack_bool: np.sqrt(np.abs(stack_float.pop())),
            'xd': lambda n,features,stack_float,stack_bool: features[-1-n[3],n[2]],
            'kd': lambda n,features,stack_float,stack_bool: n[2],
        # bool operations
            '!': lambda n,features,stack_float,stack_bool: not stack_bool.pop(),
            '&': lambda n,features,stack_float,stack_bool: stack_bool.pop() and stack_bool.pop(),
            '|': lambda n,features,stack_float,stack_bool: stack_bool.pop() or stack_bool.pop(),
            '==': lambda n,features,stack_float,stack_bool: stack_bool.pop() == stack_bool.pop(),
            '>': lambda n,features,stack_float,stack_bool: stack_float.pop() > stack_float.pop(),
            '<': lambda n,features,stack_float,stack_bool: stack_float.pop() < stack_float.pop(),
            '}': lambda n,features,stack_float,stack_bool: stack_float.pop() >= stack_float.pop(),
            '{': lambda n,features,stack_float,stack_bool: stack_float.pop() <= stack_float.pop(),
            # '>_b': lambda n,features,stack_float,stack_bool: stack_bool.pop() > stack_bool.pop(),
            # '<_b': lambda n,features,stack_float,stack_bool: stack_bool.pop() < stack_bool.pop(),
            # '>=_b': lambda n,features,stack_float,stack_bool: stack_bool.pop() >= stack_bool.pop(),
            # '<=_b': lambda n,features,stack_float,stack_bool: stack_bool.pop() <= stack_bool.pop(),
        }

        def safe(x):
            """removes nans and infs from outputs."""
            x[np.isinf(x)] = 1
            x[np.isnan(x)] = 1
            return x

        np.seterr(all='ignore')
        if len(stack_float) >= n[1]:
            if n[0] == 'y': # return auto-regressive variable
                if len(y)>=n[2]:
                    stack_float.append(y[-n[2]])
                else:
                    stack_float.append(0.0)
            else:
                stack_float.append(safe(eval_dict[n[0]](n,features,stack_float,stack_bool)))
            try:
                if np.any(np.isnan(stack_float[-1])) or np.any(np.isinf(stack_float[-1])):
                    print("problem operator:",n)
            except Exception:
                raise(Exception)

    def _out(self,I,features,ic=None):
        """computes the output for individual I"""
        stack_float = []
        stack_bool = []
        # print("stack:",I.stack)
        # evaulate stack over rows of features,labels
        if self.AR:

            delay = self.AR_nb+self.AR_nkb+1

            if ic is not None:
                tmp_features = np.vstack([ic['features'],features])
            else:
                tmp_features = np.vstack([np.zeros((self.AR_nb,features.shape[1])),features])
            #for autoregressive models, need to evaluate each sample in a loop,
            # setting delayed outputs as you go
            y = np.zeros(features.shape[0])
            # evaluate models sample by sample
            for i,f in enumerate([tmp_features[j-delay:j] for j in np.arange(features.shape[0])+delay]):
                stack_float=[]
                stack_bool=[]

                # use initial condition if one exists
                if ic is not None:
                    tmpy = np.hstack((ic['labels'],y[:i]))
                else:
                    tmpy = y[:i]

                for n in I:
                    if n[0]=='x': pdb.set_trace()
                    if n[0]=='k':
                        n = ('kd',n[1],n[2])
                    self._eval(n,f,stack_float,stack_bool,tmpy)
                    # pdb.set_trace()
                try:
                    y[i] = stack_float[-1]
                except:
                    pdb.set_trace()
        else: # normal vectorized evaluation over all rows / samples
            for n in I:
                self._eval(n,features,stack_float,stack_bool)
                # print("stack_float:",stack_float)
        # pdb.set_trace()
        # if y.shape[0] != features.shape[0]:

        if self.class_m4gp:
            return np.asarray(stack_float).transpose()
        elif self.AR:
            #
            return np.array(y)
        else:
            return stack_float[-1]


    def stacks_2_eqns(self,stacks):
        """returns equation strings from stacks"""
        if stacks:
            return list(map(lambda p: self.stack_2_eqn(p), stacks))
        else:
            return []

    def stack_2_eqn(self,p):
        """returns equation string for program stack"""
        stack_eqn = []
        if p: # if stack is not empty
            for n in p:
                self.eval_eqn(n,stack_eqn)
        if self.class_m4gp:
            return stack_eqn
        else:
            return stack_eqn[-1]
        return []

    def eval_eqn(self,n,stack_eqn):
        if n[0] == '<':
            pdb.set_trace()
        if len(stack_eqn) >= n[1]:
            stack_eqn.append(eqn_dict[n[0]](n,stack_eqn))

    # def delay_feature(self,feature,delay):
    #     """returns delayed feature value for auto-regressive models"""
    #     # ar_feat = np.vstack((np.zeros(delay+self.AR_nkb), np.array([feature[j-(delay+self.AR_nkb)] for j in feature if j >= delay + self.AR_nkb]) ))
    #     pdb.set_trace()
    #     if len(feature)>=delay:
    #         return feature[-delay]
    #     else:
    #         return 0.0

    def divs(self,x,y):
        """safe division"""
        # pdb.set_trace()

        if type(x) == np.ndarray:
            tmp = np.ones(y.shape)
            nonzero_y = np.abs(y) >= 0.000001
            # print("nonzero_y.sum:", np.sum(nonzero_y))
            tmp[nonzero_y] = x[nonzero_y]/y[nonzero_y]
            return tmp
        else:
            # pdb.set_trace()
            if abs(y) >= 0.000001:
                return x/y
            else:
                return 1


    def logs(self,x):
        """safe log"""
        tmp = np.zeros(x.shape)
        nonzero_x = np.abs(x) >= 0.000001
        tmp[nonzero_x] = np.log(np.abs(x[nonzero_x]))
        return tmp

    def plot_archive(self):
        """plots pareto archive in terms of model accuracy and complexity"""
        if not self.hof_:
            raise(ValueError,"no archive to print")
        else:
            import matplotlib.pyplot as plt

            f_t = np.array(self.fit_t)[::-1]
            f_v = np.array(self.fit_v)[::-1]
            m_v = self.hof_[::-1]

            # lines
            plt.plot(f_t,np.arange(len(f_t)),'b')
            plt.plot(f_v,np.arange(len(f_v)),'r')
            plt.legend()

            for i,(m,f1,f2) in enumerate(zip(m_v,f_t,f_v)):
                plt.plot(f1,i,'sb',label='Train')
                plt.plot(f2,i,'xr',label='Validation')
                plt.text((min(f_v))*0.9,i,self.stack_2_eqn(m))
                if f2 == max(f_v):
                    plt.plot(f2,i,'ko',markersize=4)
            plt.ylabel('Complexity')
            plt.gca().set_yticklabels('')
            plt.xlabel('Score')
            xmin = min([min(f_t),min(f_v)])
            xmax = max([max(f_t),max(f_v)])
            plt.xlim(xmin*.8,xmax*1.2)
            plt.ylim(-1,len(m_v)+1)

            return plt.gcf()

    def output_archive(self):
        """prints pareto archive in terms of model accuracy and complexity
        format:
            model\tcomplexity\ttrain\ttest\n
            x1\t0.05\t1\n
        """
        out = 'model\tcomplexity\ttrain\ttest\n'

        if not self.hof_:
            raise(ValueError,"no archive to print")
            return 0
           
        f_t = np.array(self.fit_t)[::-1]
        f_v = np.array(self.fit_v)[::-1]
        m_v = self.hof_[::-1]

        for i,(m,f1,f2) in enumerate(zip(m_v,f_t,f_v)):
            out += '\t'.join([str(self.stack_2_eqn(m)),
                             str(i),
                             str(f1),
                             str(f2)])+'\n'

        return out

# equation conversion
eqn_dict = {
    '+': lambda n,stack_eqn: '(' + stack_eqn.pop() + '+' + stack_eqn.pop() + ')',
    '-': lambda n,stack_eqn: '(' + stack_eqn.pop() + '-' + stack_eqn.pop()+ ')',
    '*': lambda n,stack_eqn: '(' + stack_eqn.pop() + '*' + stack_eqn.pop()+ ')',
    '/': lambda n,stack_eqn: '(' + stack_eqn.pop() + '/' + stack_eqn.pop()+ ')',
    's': lambda n,stack_eqn: 'sin(' + stack_eqn.pop() + ')',
    'a': lambda n,stack_eqn: 'arcsin(' + stack_eqn.pop() + ')',
    'c': lambda n,stack_eqn: 'cos(' + stack_eqn.pop() + ')',
    'd': lambda n,stack_eqn: 'arccos(' + stack_eqn.pop() + ')',
    'e': lambda n,stack_eqn: 'exp(' + stack_eqn.pop() + ')',
    'l': lambda n,stack_eqn: 'log(' + stack_eqn.pop() + ')',
    '2': lambda n,stack_eqn: '(' + stack_eqn.pop() + '^2)',
    '3': lambda n,stack_eqn: '(' + stack_eqn.pop() + '^3)',
    'q': lambda n,stack_eqn: 'sqrt(|' + stack_eqn.pop() + '|)',
    # 'rbf': lambda n,stack_eqn: 'exp(-||' + stack_eqn.pop()-stack_eqn.pop() '||^2/2)',
    'x':  lambda n,stack_eqn: 'x_' + str(n[2]),
    'k': lambda n,stack_eqn: str(round(n[2],3)),
    'y': lambda n,stack_eqn: 'y_{t-' + str(n[2]) + '}',
    'xd': lambda n,stack_eqn: 'x_' + str(n[2]) + '_{t-' + str(n[3]) + '}'
}



def positive_integer(value):
    """Ensures that the provided value is a positive integer; throws an exception otherwise

    Parameters
    ----------
    value: int
        The number to evaluate

    Returns
    -------
    value: int
        Returns a positive integer
    """
    try:
        value = int(value)
    except Exception:
        raise argparse.ArgumentTypeError('Invalid int value: \'{}\''.format(value))
    if value < 0:
        raise argparse.ArgumentTypeError('Invalid positive int value: \'{}\''.format(value))
    return value

def float_range(value):
    """Ensures that the provided value is a float integer in the range (0., 1.); throws an exception otherwise

    Parameters
    ----------
    value: float
        The number to evaluate

    Returns
    -------
    value: float
        Returns a float in the range (0., 1.)
    """
    try:
        value = float(value)
    except:
        raise argparse.ArgumentTypeError('Invalid float value: \'{}\''.format(value))
    if value < 0.0 or value > 1.0:
        raise argparse.ArgumentTypeError('Invalid float value: \'{}\''.format(value))
    return value

# main functions
def main():
    """Main function that is called when ellyn is run on the command line"""
    parser = argparse.ArgumentParser(description='A genetic programming '
                                                 'system for regression and classification.',
                                     add_help=False)

    parser.add_argument('INPUT_FILE', type=str, help='Data file to run ellyn on; ensure that the target/label column is labeled as "label".')

    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.')

    parser.add_argument('-is', action='store', dest='INPUT_SEPARATOR', default=None,
                        type=str, help='Character used to separate columns in the input file.')

# GP Runtime Options
    parser.add_argument('-g', action='store', dest='g', default=None,
                        type=positive_integer, help='Number of generations to run ellyn.')

    parser.add_argument('-p', action='store', dest='popsize', default=None,
                        type=positive_integer, help='Number of individuals in the GP population.')

    parser.add_argument('--limit_evals', action='store_true', dest='limit_evals', default=None,
                    help='Limit evaluations instead of generations.')

    parser.add_argument('-me', action='store', dest='max_evals', default=None,
                        type=float_range, help='Max point evaluations.')

    parser.add_argument('-sel', action='store', dest='selection', default='tournament', choices = ['tournament','dc','lexicase','epsilon_lexicase','afp','rand'],
                        type=str, help='Selection method (Default: tournament)')

    parser.add_argument('-PS_sel', action='store', dest='PS_sel', default=None, choices = [1,2,3,4,5],
                        type=str, help='objectives for pareto survival. 1: age + fitness; 2: age+fitness+generality; 3: age+fitness+complexity; 4: class fitnesses (classification ONLY); 5: class fitnesses+ age (classification ONLY)')

    parser.add_argument('-tourn_size', action='store', dest='tourn_size', default=None,
                        type=positive_integer, help='Tournament size for tournament selection (Default: 2)')

    parser.add_argument('-mr', action='store', dest='rt_mut', default=None,
                        type=float_range, help='GP mutation rate in the range [0.0, 1.0].')

    parser.add_argument('-xr', action='store', dest='rt_cross', default=None,
                        type=float_range, help='GP crossover rate in the range [0.0, 1.0].')

    parser.add_argument('-rr', action='store', dest='rt_rep', default=None,
                        type=float_range, help='GP reproduction rate in the range [0.0, 1.0].')

    parser.add_argument('--elitism', action='store_true', dest='elitism', default=None,
                help='Flag to force survival of best individual in GP population.')

    parser.add_argument('--init_validate', action='store_true', dest='init_validate_on', default=None,
                help='Flag to guarantee initial population outputs are valid (no NaNs or Infs).')

    parser.add_argument('--no_stop', action='store_false', dest='stop_condition', default=None,
                    help='Flag to keep running even though fitness < 1e-6 has been reached.')
    parser.add_argument('-stop_threshold', action='store', dest='stop_threshold', default=None,
                    type=float, help='Fitness theshold for stopping execution.')
# Data Options
    parser.add_argument('--validate', action='store_true', dest='train', default=None,
                help='Flag to split data into training and validation sets.')

    parser.add_argument('-train_split', action='store', dest='train_pct', default=None, type = float_range,
                help='Fraction of data to use for training in [0,1]. Only used when --validate flag is present.')

    parser.add_argument('--shuffle', action='store_true', dest='shuffle_data', default=None,
                help='Flag to shuffle data samples.')

    parser.add_argument('--restart', action='store_true', dest='pop_restart_path', default=None,
                help='Flag to restart from previous population.')

    parser.add_argument('-pop', action='store_true', dest='pop_restart', default=None,
                help='Population to use in restart. Only used when --restart flag is present.')

    parser.add_argument('--AR', action='store_true', dest='AR', default=None,
                    help='Flag to use auto-regressive variables.')

    parser.add_argument('--AR_lookahead', action='store_true', dest='AR_lookahead', default=None,
                    help='Flag to only estimate on step ahead of data when evaluating candidate models.')

    parser.add_argument('-AR_na', action='store', dest='AR_na', default=None,
                    type=positive_integer, help='Order of auto-regressive output (y).')
    parser.add_argument('-AR_nb', action='store', dest='AR_nb', default=None,
                    type=positive_integer, help='Order of auto-regressive inputs (x).')
    parser.add_argument('-AR_nka', action='store', dest='AR_nka', default=None,
                    type=positive_integer, help='AR state (output) delay.')
    parser.add_argument('-AR_nkb', action='store', dest='AR_nkb', default=None,
                    type=positive_integer, help='AR input delay.')

# Results and Printing Options
    parser.add_argument('-op', action='store', dest='resultspath', default=None,
                        type=str, help='Path where results will be saved.')
    parser.add_argument('-on', action='store', dest='savename', default=None,
                        type=str, help='Name of the file where results will be saved.')
    parser.add_argument('--print_log', action='store_true', dest='print_log', default=False,
                    help='Flag to print log to terminal.')

    parser.add_argument('--print_every_pop', action='store_true', dest='print_every_pop', default=None,
                    help='Flag to seed initial GP population with components of the ML model.')

    parser.add_argument('--print_genome', action='store_true', dest='print_genome', default=None,
                    help='Flag to prints genome for visualization.')

    parser.add_argument('--print_novelty', action='store_true', dest='print_novelty', default=None,
                    help='Flag to print number of unique output vectors.')

    parser.add_argument('--print_homology', action='store_true', dest='print_homology', default=None,
                    help='Flag to print genetic homology in programs.')

    parser.add_argument('--print_db', action='store_true', dest='print_db', default=None,
                    help='Flag to print individuals for graph database analysis.')

    parser.add_argument('-num_log_pts', action='store', dest='num_log_pts', default=None,
                        type=positive_integer, help='number of log points to print (0 means print each generation)')

# Classification Options

    parser.add_argument('--class', action='store_true', dest='classification', default=None,
                    help='Flag to define a classification problem instead of regression (the default).')

    parser.add_argument('--class_bool', action='store_true', dest='class_bool', default=None,
                    help='Flag to interpret class labels as bit-string conversion of boolean stack output.')

    parser.add_argument('--class_m4gp', action='store_true', dest='class_m4gp', default=False,
                    help='Flag to use the M4GP algorithm.')

    parser.add_argument('--class_prune', action='store_true', dest='class_prune', default=None,
                        help='Flag to prune the dimensions of the best individual each generation.')

# Terminal and Operator Options
    parser.add_argument('-ops', action='store', dest='ops', default=None,
                    type=str, help='Operator list separated by commas (no spaces!). Default: +,-,*,/,n,v. available operators: n v + - * / sin cos log exp sqrt = ! < <= > >= if-then if-then-else & |')

    parser.add_argument('-op_weight', action='store', dest='op_weight', default=None,
                    help='Operator weights for each element in operator list, separated by commas (no spaces!). If not specified all operators have the same weights.')

    parser.add_argument('-constants', nargs = '*', action='store', dest='cvals', default=None,
                        type=float, help='Seed GP initialization with constant values.')

    parser.add_argument('-seeds', nargs = '*', action='store', dest='seeds', default=None,
                        type=str, help='Seed GP initialization with partial solutions, e.g. (x+y). Each partial solution must be enclosed in parentheses.')

    parser.add_argument('-min_len', action='store', dest='min_len', default=None,
                        type=positive_integer, help='Minimum length of GP programs.')

    parser.add_argument('-max_len', action='store', dest='max_len', default=None,
                        type=positive_integer, help='Maximum number of nodes in GP programs.')

    parser.add_argument('-max_len_init', action='store', dest='max_len_init', default=None,
                        type=positive_integer, help='Maximum number of nodes in initialized GP programs.')

    parser.add_argument('--erc_ints', action='store_true', dest='erc_ints', default=None,
                help='Flag to use integer instead of floating point ERCs.')

    parser.add_argument('--no_erc', action='store_false', dest='ERC', default=None,
                help='Flag to turn of ERCs. Useful if you are specifying constant values and don''t want random ones.')

    parser.add_argument('-min_erc', action='store', dest='minERC', default=None,
                    help='Minimum ERC value.')

    parser.add_argument('-max_erc', action='store', dest='maxERC', default=None, type = int,
                    help='Maximum ERC value.')

    parser.add_argument('-num_erc', action='store', dest='numERC', default=None, type = int,
                    help='Number of ERCs to use.')

    parser.add_argument('--trees', action='store_true', dest='init_trees', default=None,
                    help='Flag to initialize genotypes as syntactically valid trees rather than randomized stacks.')
# Fitness Options
    parser.add_argument('-fit', action='store', dest='fit_type', default=None, choices = ['MSE','MAE','R2','VAF','combo','F1','F1W'],
                    type=str, help='Fitness metric (Default: mse). combo is mae/r2')

    parser.add_argument('--norm_error', action='store_true', dest='ERC_ints', default=None,
                help='Flag to normalize error by the standard deviation of the target data being used.')

    parser.add_argument('--fe', action='store_true', dest='estimate_fitness', default=None,
            help='Flag to coevolve fitness estimators.')

    parser.add_argument('-fe_p', action='store', dest='FE_pop_size', default=None, type = positive_integer,
                    help='fitness estimator population size.')

    parser.add_argument('-fe_i', action='store', dest='FE_ind_size', default=None, type = positive_integer,
                    help='number of fitness cases for FE to use.')

    parser.add_argument('-fe_t', action='store', dest='FE_train_size', default=None, type = positive_integer,
                    help='trainer population size. Trainers are evaluated on the entire data set.')

    parser.add_argument('-fe_g', action='store', dest='FE_train_gens', default=None, type = positive_integer,
                    help='Number of generations between trainer selections.')

    parser.add_argument('--fe_rank', action='store_true', dest='FE_rank', default=None,
            help='User rank for FE fitness rather than error.')

# Parameter hillclimbing
    parser.add_argument('--phc', action='store_true', dest='pHC_on', default=None,
                        help='Flag to use parameter hillclimbing.')

    parser.add_argument('-phc_its', action='store', dest='pHC_its', default=None, type = positive_integer,
                        help='Number of iterations of parameter hill climbing each generation.')
# Epigenetic hillclimbing
    parser.add_argument('--ehc', action='store_true', dest='eHC_on', default=None,
                        help='Flag to use epigenetic hillclimbing.')

    parser.add_argument('-ehc_its', action='store', dest='eHC_its', default=None, type = positive_integer,
                    help='Number of iterations of epigenetic hill climbing each generation.')

    parser.add_argument('-ehc_init', action='store', dest='eHC_init', default=None, type = positive_integer,
                        help='Fraction of initial population''s genes that are silenced.')

    parser.add_argument('--emut', action='store_true', dest='eHC_mut', default=None,
                        help='Flag to use epigenetic mutation. Only works if ehc flag is present.')

    parser.add_argument('--e_slim', action='store_true', dest='eHC_slim', default=None,
                        help='Flag to store partial program outputs such that point evaluations are minimized during eHC.')
# Pareto Archive
    parser.add_argument('--archive', action='store_true', dest='prto_arch_on', default=None,
                        help='Flag to save the Pareto front of equations (fitness and complexity) during the run.')

    parser.add_argument('-arch_size', action='store', dest='prto_arch_size', default=None,
                        help='Minimum size of the Pareto archive. By default, ellyn will save the entire front, but more individuals will be added if the front is less than arch_size.')
# island model
    parser.add_argument('--no_islands', action='store_false', dest='islands', default=True,
                    help='Flag to turn off island populations. Parallel execution across codes on a single node.')

    parser.add_argument('-num_islands', action='store', dest='num_islands', default=None, type = positive_integer,
                help='Number of islands to use (limits number of cores).')

    parser.add_argument('-island_gens', action='store', dest='island_gens', default=None, type = positive_integer,
                    help='Number of generations between synchronized shuffling of island populations.')
# lexicase selection options
    parser.add_argument('-lex_pool', action='store', dest='lex_pool', default=None,
                        type=float_range, help='Fraction of population to use in lexicase selection events [0.0, 1.0].')

    parser.add_argument('-lex_meta', action='store', dest='lex_meta', default=None, choices=['age','complexity'],
                    type=str,help='Specify extra cases for selection. Options: age, complexity.')

    parser.add_argument('--lex_eps_error_mad', action='store_true', dest='lex_eps_error_mad', default=None,
                    help='Flag to use epsilon lexicase with median absolute deviation, error-based epsilons.')

    parser.add_argument('--lex_eps_target_mad', action='store_true', dest='lex_eps_target_mad', default=None,
                    help='Flag to use epsilon lexicase with median absolute deviation, target-based epsilons.')

    parser.add_argument('--lex_eps_semidynamic', action='store_true', dest='lex_eps_semidynamic', default=None,
                    help='Flag to use dynamically defined error in epsilon lexicase selection.')

    parser.add_argument('--lex_eps_dynamic', action='store_true', dest='lex_eps_dynamic', default=None,
                    help='Flag to use dynamic error and epsilon in epsilon lexicase selection.')

    parser.add_argument('--lex_eps_dynamic_rand', action='store_true', dest='lex_eps_dynamic_rand', default=None,
                help='Flag to use dynamic error and random thresholds in epsilon lexicase selection.')

    parser.add_argument('--lex_eps_dynamic_madcap', action='store_true', dest='lex_eps_dynamic_madcap', default=None,
                help='Flag to use dynamic error and mad capped thresholds in epsilon lexicase selection.')

    parser.add_argument('--lex_age', action='store_true', dest='lexage', default=None,
                help='Flag to use age-fitness Pareto survival after lexicase selection.')
# SGD
    parser.add_argument('--SGD', action='store_true', dest='SGD', default=None,
                help='Use stochastic gradient descent to update program constant values.')

    parser.add_argument('-lr', action='store', dest='learning_rate', default=None,
                        type=float_range, help='Learning rate for stochastic gradient descent.')

    parser.add_argument('-s', action='store', dest='random_state', default=np.random.randint(4294967295),
                        type=int, help='Random number generator seed for reproducibility. Note that using multi-threading may '
                                       'make exacts results impossible to reproduce.')

    parser.add_argument('-v', action='store', dest='verbosity', default=0, choices=[0, 1, 2, 3],
                        type=int, help='How much information ellyn communicates while it is running: 0 = none, 1 = minimal, 2 = lots, 3 = all.')

    parser.add_argument('--no-update-check', action='store_true', dest='DISABLE_UPDATE_CHECK', default=False,
                        help='Flag indicating whether the ellyn version checker should be disabled.')

    # parser.add_argument('--version', action='version', version='ellyn {version}'.format(version=__version__),
    #                     help='Show ellyn\'s version number and exit.')

    args = parser.parse_args()

    # load data from csv file
    if args.INPUT_SEPARATOR is None:
        input_data = pd.read_csv(args.INPUT_FILE, sep=args.INPUT_SEPARATOR,engine='python')
    else: # use c engine for read_csv is separator is specified
        input_data = pd.read_csv(args.INPUT_FILE, sep=args.INPUT_SEPARATOR)

    if 'Label' in input_data.columns.values:
        input_data.rename(columns={'Label': 'label'}, inplace=True)

    input_data.rename(columns={'target': 'label', 'class': 'label'}, inplace=True)


    random_state = args.random_state if args.random_state > 0 else None

    if args.AR:
        train_i = input_data.index[:round(0.75*len(input_data.index))]
        test_i = input_data.index[round(0.75*len(input_data.index)):]
    else:
        train_i, test_i = train_test_split(input_data.index,
                                           stratify = None,
                                           train_size=0.75,
                                           test_size=0.25,
                                           random_state=random_state)

    training_features = np.array(input_data.loc[train_i].drop('label', axis=1).values,dtype=np.float32, order='C')
    training_labels = np.array(input_data.loc[train_i, 'label'].values,dtype=np.float32,order='C')
    testing_features = input_data.loc[test_i].drop('label', axis=1).values
    testing_labels = input_data.loc[test_i, 'label'].values

    learner = ellyn(**args.__dict__)
    learner.fit(training_features, training_labels)

    if args.verbosity >= 1:
        print('\nTraining accuracy: {}'.format(learner.score(training_features, training_labels)))
        print('Holdout accuracy: {}'.format(learner.score(testing_features, testing_labels)))


if __name__ == '__main__':
    main()
