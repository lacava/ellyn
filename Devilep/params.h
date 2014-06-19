// header file for ind struct
#pragma once
#ifndef PARAMS_H
#define PARAMS_H
#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <array>
#include "op_node.h"
using namespace std;

struct params {
	
	int g; // number of generations
	int popsize; //population size
	int numits;  // number of trials
	
	// Generation Settings 
	int sel; // 1: tournament; 2: deterministic crowding; 3: NSGA
	int tourn_size;
	float rt_rep; //probability of reproduction
	float rt_cross; 
	float rt_mut;
	vector<float> rep_wheel;
	float cross_ar; //crossover alternation rate
	float mut_ar;
	int cross; // 1: ultra; 2: one point
	float stoperror; // stop condition / convergence condition

	bool init_validate_on; // initial fitness validation of individuals
	bool train; // choice to turn on training for splitting up the data set
	// Results
	string resultspath;
	bool loud;
	// Computer Settings
	//bool parallel;
	//int numcores;

	bool printeverypop;

	string sim_nom_mod; // embryo equation
	int nstates;    // state space modeling: number of states

	// Problem information
	vector <string> intvars; // internal variables
	vector <string> extvars; // external variables (external forces)
	vector <string> cons;
	vector <float> cvals;
	vector <string> seeds;
	vector <vector <shared_ptr<node>>> seedstacks;

	vector <string> allvars;// = intvars.insert(intvars.end(), extvars.begin(), extvars.end());
	vector <string> allblocks;// = allvars.insert(allvars.end(),consvals.begin(),convals.end());
	//allblocks = allblocks.insert(allblocks.end(),seeds.begin(),seeds.end());


	bool ERC; // ephemeral random constants
	bool ERCints;
	int maxERC;
	int minERC;
	int numERC;

	//vector <float> target;
	
	int fit_type; // 1: error, 2: corr, 3: combo
	float max_fit;
	float min_fit;

	vector <string> op_list;
	vector <int> op_choice; // map op list to pointer location in makeline() pointer function
	vector <float> op_weight;
	bool weight_ops_on;

	int min_len;
	int max_len;

	int max_dev_len;

	int complex_measure; // 1: genotype size; 2: symbolic size; 3: effective genotype size

	float precision;

	// Hill Climbing Settings

		// generic line hill climber (Bongard)
	bool lineHC_on;
	int lineHC_its;

		// parameter Hill Climber
	bool pHC_on;
	bool pHC_delay_on;
	float pHC_delay;
	int pHC_size;
	int pHC_its;
	float pHC_gauss;

		// epigenetic Hill Climber
	bool eHC_on;
	int eHC_its;
	float eHC_prob;
	bool eHC_size;
	bool eHC_cluster;
	bool eHC_dev;
	bool eHC_best;
	float eHC_prob_scale;
	float eHC_max_prob;
	float eHC_min_prob;
	float eHC_init;

	// Pareto settings

	bool prto_arch_on;
	int prto_arch_size;
	bool prto_sel_on;

	//island model
	int islands;
	int island_gens;

	int seed;

	// lexicase selection
	int numcases;
	int lexpool;
	bool lexage;
	params(){train=0;}
	~params(){}

	void clear()
	{
		
		rep_wheel.clear();
	
		// Problem information
		intvars.clear(); // internal variables
		extvars.clear(); // external variables (external forces)
		cons.clear();
		cvals.clear();
		seeds.clear();
	
		allvars.clear();// = intvars.insert(intvars.end(), extvars.begin(), extvars.end());
		allblocks.clear();// = allvars.insert(allvars.end(),consvals.begin(),convals.end());
		//allblocks = allblocks.insert(allblocks.end(),seeds.begin(),seeds.end());

		op_list.clear();
		op_choice.clear(); // map op list to pointer location in makeline() pointer function
		op_weight.clear();
	
	}

};
#endif