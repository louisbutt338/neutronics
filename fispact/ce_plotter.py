import os
import numpy as np 
import sys
import statistics
import matplotlib.font_manager
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import seaborn
import json
from matplotlib.pyplot import cm
#plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Helvetica"
plt.rcParams["font.size"] = 22
plt.rcParams["font.weight"] = "normal"
from collections import Counter
from itertools import count
from random import randint
from pathlib import Path
import math

################# DIRECTORY INPUTS #################

image_directory = '/Users/ljb841@student.bham.ac.uk/fispact/WORKSHOP/uBB/analysis'
calc_data_directory = f"{image_directory}/calculated_activities"
exp_data_directory =  f"{image_directory}/experimental_activities"

################# FLUX NORMALISATION CALCS ################# 

flux_norm_mean = 0.02756
flux_norm_error = 0.004
calculated_flux_uncertainty_frac = flux_norm_error/flux_norm_mean
n_per_s_norm_mean = 0.0751237
n_per_s_error = 0.0751237* np.sqrt((1147.24/199358.77)**2+(0.004/0.02756)**2+(59186.1/73137.1)**2)

def estimated_10ua_flux(flux):
    return flux*6.24151e13*1.37267e-05
def estimated_10ua_li_n_per_s(flux):
    return flux*6.24151e13*3.28565E-03
print(f"max flux at 10uA proton current: {estimated_10ua_flux(flux_norm_mean):.3e} +- {estimated_10ua_flux(flux_norm_error):.3e} n/cm2/s")
print(f"max n/s from lithium at 10uA proton current: {estimated_10ua_li_n_per_s(n_per_s_norm_mean):.3e} +- {estimated_10ua_li_n_per_s(n_per_s_error):.3e} n/s")

################# LIST OF ANALYSED ISOTOPES ################# 

isotope_list = [
'$^{56}Mn$',
'$^{196}Au$',
'$^{198}Au$', 
'$^{24}Na$',
'$^{65}Ni$',
'$^{64}Cu$',
'$^{111m}Cd$',
'$^{115}Cd$',
'$^{115m}In$',
'$^{116m}In$',
'$^{57}Ni$',
'$^{165}Dy$', 
'$^{157}Dy$', 
'$^{92m}Nb$',
'$^{7}Be$ *'] 

################# CALCULATED RESULTS FOR ALL THREE LIBRARIES ################# 

# calibration experiment model results (iron foil)

# calculated_endfb8_activities = [
# 1.4440*8.976E+02 ,
# 0.1498*9.205E+01 ,
# 0.1498*3.86E+03 ,
# 0.2334*4.504E+02 ,
# 0.7877*5.596E+01 ,
# 0.7877*7.597E+02 ,
# 1e6              , # reaction missing
# 0.1328*1.003E+02 ,
# 1e6              , # reaction missing
# 1e6 , # reaction missing in116m product 
# 1.5845*5.830E+00 ,
# 0.0435*1.334E+04 ,
# 0.0435*2.183E+01 ,
# 1e6              , # reaction missing
# (4.110146e-02*1.500E+06) + (1.342088e-02*4.948e6)]
# 
# calculated_endfb8_uncertainties = [
# 1.4440*1.71E+01,
# 0.1498*0.00E+00,
# 0.1498*7.79E+01,
# 0.2334*0.00E+00,
# 0.7877*0.00E+00,
# 0.7877*0.00E+00,
# 0.1328*0.00E+00,
# 0.1328*0.00E+00,
# 0.6452*0.00E+00,
# 0.6452*0.00E+00,
# 1.5845*1.11E-01,
# 0.0435*0.00E+00,
# 0.0435*0.00E+00,
# 0.7317*0.00E+00,
# 4.110146e-02*0.00E+00]
# 
# calculated_irdff2_activities = [
# 1.4440*8.972E+02,
# 0.1498*9.350E+01,
# 0.1498*4.306E+03,
# 0.5*0.2334*9.043E+02, #    only half the Na24 generated here is from (n,a), hence multiplication factor
# 1e6,        #    reaction missing
# 0.7877*7.788E+02,
# 1e6,        #    reaction missing
# 1e6,        #    reaction missing
# 1e6*0.6452*3210.0877645615906,        #    reaction missing
# 0.6452*0.33334*7.031E+05,
# 1.5845*5.584E+00,
# 1e6,        #   reaction missing,
# 1e6,        #   reaction missing,
# 1e6*0.7317*20.127675759159207,        #   reaction missing]
# 1e6]
# 
# calculated_irdff2_uncertainties = [
# 1.4440*0,
# 0.1498*0,
# 0.1498*0,
# 0.2334*0,
# 0.7877*0,
# 0.7877*0,
# 0.1328*0,
# 0.1328*0,
# 0.6452*0,
# 0.6452*0,
# 1.5845*0,
# 0.0435*0,
# 0.0435*0,
# 0.7317*0,
# 4.110146e-02*0]
# 
# calculated_tendl21_activities = [
# 1.4440*8.920E+02 ,
# 0.1498*8.845E+01 ,
# 0.1498*3.594E+03 ,
# 0.2334*4.503E+02 ,
# 0.7877*8.772E+01 ,
# 0.7877*7.645E+02 ,
# 0.1328*3.870E+03 ,
# 0.1328*7.802E+01 ,
# 0.6452*4.379E+03 ,
# 0.6452*2.769E+05 ,
# 1.5845*5.624E+00 ,
# 0.0435*1.299E+04 ,
# 0.0435*2.406E+01 ,
# 0.7317*2.479E+01 ,
# (4.110146e-02*2.422E+06) + (1.342088e-02*2.123e7)]
# 
# calculated_tendl21_uncertainties = [
# 1.4440*9.14E+01 ,
# 0.1498*3.71E+00 ,
# 0.1498*5.34E+01 ,
# 0.2334*0.00E+00 ,
# 0.7877*6.44E+00 ,
# 0.7877*3.22E+01 ,
# 0.1328*1.54E+02 ,
# 0.1328*5.50E+00 ,
# 0.6452*2.03E+02 ,
# 0.6452*7.51E+03 ,
# 1.5845*8.51E-01 ,
# 0.0435*9.36E+02 ,
# 0.0435*1.78E+00 ,
# 0.7317*1.50E+00 ,
# (4.110146e-02*1.96E+06) + (1.342088e-02*2.94e6)]


# calibration experiment model results (seperated foils)

calculated_endfb8_activities = [
1.4440*9.157E+02 ,
0.1498*8.255E+01 ,
0.1498*1.683E+03 ,
0.2334*4.290E+02 ,
0.7877*5.498E+01 ,
0.7877*6.946E+02 ,
1e6              , # reaction missing
0.1328*8.556E+01 ,
1e6              , # reaction missing
1e6 , # reaction missing in116m product 
1.5845*5.333E+00 ,
0.0435*1.010E+04 ,
0.0435*2.487E+01 ,
1e6              , # reaction missing
(4.110146e-02*1.500E+06) + (1.342088e-02*4.948e6)]

calculated_endfb8_uncertainties = [
1.4440*1.75E+01,
0.1498*0.00E+00,
0.1498*2.62E+01,
0.2334*0.00E+00,
0.7877*0.00E+00,
0.7877*0.00E+00,
0.1328*0.00E+00,
0.1328*0.00E+00,
0.6452*0.00E+00,
0.6452*0.00E+00,
1.5845*1.01E-01,
0.0435*0.00E+00,
0.0435*0.00E+00,
0.7317*0.00E+00,
4.110146e-02*0.00E+00]

calculated_irdff2_activities = [
1.4440*9.152E+02,
0.1498*8.385E+01,
0.1498*1.546E+03,
0.5*0.2334*8.614E+02, #    only half the Na24 generated here is from (n,a), hence multiplication factor
1e6,        #    reaction missing
0.7877*7.181E+02,
1e6,        #    reaction missing
1e6,        #    reaction missing
1e6*0.6452*3210.0877645615906,        #    reaction missing
0.6452*0.33334*9.133E+05,
1.5845*5.104E+00,
1e6,        #   reaction missing,
1e6,        #   reaction missing,
1e6*0.7317*20.127675759159207,        #   reaction missing]
1e6]

calculated_irdff2_uncertainties = [
1.4440*0,
0.1498*0,
0.1498*0,
0.2334*0,
0.7877*0,
0.7877*0,
0.1328*0,
0.1328*0,
0.6452*0,
0.6452*0,
1.5845*0,
0.0435*0,
0.0435*0,
0.7317*0,
4.110146e-02*0]

calculated_tendl21_activities = [
1.4440*9.099E+02 ,
0.1498*7.932E+01 ,
0.1498*1.418E+03 ,
0.2334*4.289E+02 ,
0.7877*8.617E+01 ,
0.7877*7.025E+02 ,
0.1328*3.358E+03 ,
0.1328*6.376E+01 ,
0.6452*3.784E+03 ,
0.6452*3.655E+05 ,
1.5845*5.141E+00 ,
0.0435*9.821E+03 ,
0.0435*2.664E+01 ,
0.7317*2.123E+01 ,
(4.110146e-02*2.422E+06) + (1.342088e-02*2.123e7)]

calculated_tendl21_uncertainties = [
1.4440*9.32E+01 ,
0.1498*3.36E+00 ,
0.1498*4.64E+01 ,
0.2334*0.00E+00 ,
0.7877*6.33E+00 ,
0.7877*3.16E+01 ,
0.1328*1.34E+02 ,
0.1328*4.76E+00 ,
0.6452*1.75E+02 ,
0.6452*9.79E+03 ,
1.5845*7.78E-01 ,
0.0435*7.32E+02 ,
0.0435*1.81E+00 ,
0.7317*1.28E+00 ,
(4.110146e-02*1.96E+06) + (1.342088e-02*2.94e6)]

################# CALCULATED UNCERTAINTIES FUNCTION ################# 

def total_calculated_uncerts(calc_fispact_uncerts,calc_activities):
    calculated_uncertainties_frac = []
    for i in np.linspace(0,len(calc_activities)-1,len(calc_activities)):
        frac_fispact_uncerts = calc_fispact_uncerts[int(i)]/calc_activities[int(i)]
        squares_calc_uncerts = frac_fispact_uncerts**2 + calculated_flux_uncertainty_frac**2 
        calculated_uncertainties_frac.append(np.sqrt((squares_calc_uncerts)))
    return calculated_uncertainties_frac

################# EXPERIMENTAL RESULTS ################# 

experimental_activities = [
1283.5748064185852
,9.56701857731642
,1059.8534636660463
,109.78571243006984
,47.354279028165536
,976.9745223250458
,564.0136821965442
,24.055053741543887
,3925.6667358315044
,225978.3770850294
,8.641203390990839
,1480.475164225852
,3.545378049582069
,16.443880490456756
,199358.7712541107]

experimental_uncertainties = [
11.505019860224916
,1.0468470175786961
,15.256182909717403
,1.2092403652867434
,5.588082663030442
,158.1728263407352
,4.923370766254835
,1.7118933951037367
,35.22751978312062
,1950.6765618229635
,0.12161693661394514
,15.892505341164915
,0.1323696495059722
,0.28527178050358687
,1147.2464970510382]

# ROOT activities

experimental_activities = [
1277.7785213432978
,9.860120003910335
,970.0399189999137
,108.67576641718234 
,44.41869640318654 
,940.0388828554179
,568.8332961651257
,24.41799508342217
,3964.671247446269 # copied from interspec 
,224230.89280539454 # copied from interspec
,8.56731053307205 # copied from interspec
,2322.42753
,3.5299517227162998
,16.243051418817277
,202421.90327452912] 

experimental_uncertainties = [
11.553077365500107
,1.1389062662744531
,9.474808511161948
,1.1937521218344695
,6.396292282058862
,186.79684862084045
,5.0104487226979995
,1.7894984576503246
,35.577532226102235
,1935.592036168745
,0.11740388508283918
,99.925
,0.1575763183253717
,0.28396943039890343
,964.8790137193216]


################# C/E FUNCTIONS ################# 

def c_over_e(calculated_activities):
    c_over_e_array = []
    for i in np.linspace(0,len(experimental_activities)-1,len(experimental_activities)):
        c_over_e =  calculated_activities[int(i)]/experimental_activities[int(i)]
        c_over_e_array.append(c_over_e)
    return c_over_e_array

def c_over_e_uncerts(calculated_uncertainties_frac):
    c_over_e_uncerts = []
    for i in np.linspace(0,len(experimental_activities)-1,len(experimental_activities)):
        c_error = calculated_uncertainties_frac[int(i)]
        e_error = experimental_uncertainties[int(i)]/experimental_activities[int(i)]

        ce_error =  np.sqrt( c_error**2 + e_error**2 )
        #ce_error =  np.sqrt( c_error**2 + e_error**2 ) * c_over_e[int(i)]
        #ce_error =  ( c_error + e_error ) * c_over_e[int(i)]
    
        c_over_e_uncerts.append(ce_error)
    return c_over_e_uncerts

################# PLOTTING ################# 

new_order = [9,2,11,12, 7,5,6,  8,4,1,13,3,0,10,14]

new_isotope_list = [isotope_list[i] for i in new_order]
new_ce_results    = [c_over_e(calculated_tendl21_activities)[i] for i in new_order]
ce_results_irdff  =  [c_over_e(calculated_irdff2_activities)[i] for i in new_order]
ce_results_endfb8 =  [c_over_e(calculated_endfb8_activities)[i] for i in new_order]

new_ce_errors =     [c_over_e_uncerts(total_calculated_uncerts(calculated_tendl21_uncertainties,calculated_tendl21_activities))[i] for i in new_order]
ce_errors_irdff =   [c_over_e_uncerts(total_calculated_uncerts(calculated_irdff2_uncertainties, calculated_irdff2_activities ))[i] for i in new_order]
ce_errors_endfb8 =  [c_over_e_uncerts(total_calculated_uncerts(calculated_endfb8_uncertainties, calculated_endfb8_activities ))[i] for i in new_order]

fig, ax1 = plt.subplots()
ax1.set_xlabel('Neutron-transmuted isotopes') 
ax1.set_ylabel('C/E')
ax1.tick_params(axis='y')
ax1.set_xticks(np.arange(0, len(new_order), step=1))

#ax1.set_xscale("log")
ax1.set_ylim(0.1,2)
#ax1.set_ylim(0,4)
ax1.set_yticks([0.2,0.6,1,1.4,1.8])
#ax1.set_yscale("log")

ax1.scatter(new_isotope_list, new_ce_results, s=40 , c='b', linewidth=2,label='TENDL-2021')
ax1.errorbar(new_isotope_list,new_ce_results,new_ce_errors,fmt='none',lw=2,capsize=2,color='Black',zorder=-1)
ax1.set_xlim(-0.5,len(new_order)-0.5)

ax2 = ax1.twiny()
ax2.scatter(new_isotope_list, ce_results_irdff, s=40 , c='magenta', linewidth=2,label='IRDFF-II')
ax2.errorbar(new_isotope_list,ce_results_irdff,ce_errors_irdff,fmt='none',lw=2,capsize=2,color='black',zorder=-1)
ax2.tick_params(top=False, labeltop=False, bottom=True, labelbottom=False)
ax2.set_xlim(-0.3,len(new_order)-0.3)

ax3 = ax1.twiny()
ax3.scatter(new_isotope_list, ce_results_endfb8, s=40 , c='green', linewidth=2,label='ENDF/B-VIII')
ax3.errorbar(new_isotope_list,ce_results_endfb8,ce_errors_endfb8,fmt='none',lw=2,capsize=2,color='black',zorder=-1)
ax3.tick_params(top=False, labeltop=False, bottom=True, labelbottom=False)
ax3.set_xlim(-0.7,len(new_order)-0.7)

ax1.plot([-1,17], np.ones(2), 'Black', ls='--',linewidth=1.5)
ax1.fill_between([-1,17], 1-0.14513788, 1+0.14513788,facecolor='lightgrey',alpha=0.5)

ax1.set_xticklabels(new_isotope_list,rotation=45)
ax1.legend(loc="upper left", bbox_to_anchor=(0.02, 0.90),handlelength=0,borderaxespad=0, frameon=False,fontsize=18, fancybox=False,facecolor='white',framealpha=1)
ax2.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98),handlelength=0,borderaxespad=0, frameon=False,fontsize=18, fancybox=False,facecolor='white',framealpha=1)
ax3.legend(loc="upper left", bbox_to_anchor=(0.02, 0.82),handlelength=0,borderaxespad=0, frameon=False,fontsize=18, fancybox=False,facecolor='white',framealpha=1)
fig.set_size_inches((17, 6))
fig.savefig(os.path.join(f"{image_directory}/CE_plots", 'CE_plot_root_sep_foils.png'), transparent=False, bbox_inches='tight')

################# WEIGHTED AVES ################# 

def weighted_ce(ce_value_array,ce_error_array):
    weights = []
    weighted_values = []
    for i in np.linspace(0,len(ce_value_array)-1,len(ce_value_array)):
        iterator = int(i)
        weight = 1/((ce_error_array[iterator])**2)
        weighted_value = weight*ce_value_array[iterator]
        weights.append(weight)
        weighted_values.append(weighted_value)
    summed_weights = np.sum(weights)
    summed_weighted_values = np.sum(weighted_values)
    weighted_ce_result = summed_weighted_values/summed_weights
    weighted_ce_error = 1/np.sqrt(summed_weights)
    return weighted_ce_result,weighted_ce_error

print(f"weighted C/E for {new_isotope_list[6:14]} is {weighted_ce(new_ce_results[6:14],new_ce_errors[6:14])[0]} +- {weighted_ce(new_ce_results[6:14],new_ce_errors[6:14])[1]}")

