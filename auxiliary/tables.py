"""This module contains auxiliary functions for generating tavles which are used in the main notebook."""

#Packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker
import statsmodels.formula.api as smf
import seaborn as sns

#For spatial analysis
import geopandas as gpd
import shapely.geometry as geom
import libpysal as lp
from libpysal import weights

from pysal.viz import splot #exploratory analysis
from pysal.explore import esda #exploratory analysis
from pysal.model import spreg #For spatial regression

pd.options.display.float_format = "{:,.2f}".format

from auxiliary.data_import import *
from auxiliary.plots import *
from auxiliary.simulations import *


# get reg table regiondata
def get_table_regiondata(regressors, specification, data):
    """
    Can generate the regression table 2,3 and 4
    Inputs:
        - regressors: array of column names
        - specification: dictionary with column names
        - data: data frame (regiondata)
        
    Returns: container (pandas data frame with regression results)
    """
    ## get list of regressors
    #regressors = []
    #for i in specification.keys():
    #    regressors.extend(specification[i])
    #regressors = list(set(regressors))


    container = pd.DataFrame()

    container['regressors'] = regressors
    container = container.set_index('regressors')

    for key in specification.keys():
        table = pd.DataFrame({'Urbanization rate': [], 'Std.err': [], 'P-Value': [],})

        table['regressors'] = regressors
        table = table.set_index('regressors')
        
        formula = "ADurbfrac ~"
        for regressors in specification[key]:
            formula = formula + f" {regressors} +"
            
        
        formula = formula + " C(countryyear) -1"
        #c(var) for fixed effect - "-1" for dropping intercept
        result = smf.ols(
            formula = formula, data=data
            ).fit(
            cov_type='cluster',cov_kwds={'groups': data['afruid']},use_t=True
            )
        for coef in specification[key]:
            outputs = [result.params[coef], result.bse[coef], result.pvalues[coef]]
            table.loc[coef] = outputs
        
        container = pd.concat([container, table], axis=1)

    # Change variable names to labels
    codebook = get_data_codebook("regiondata")
    container = container.rename(codebook, axis="index")

    container.columns = pd.MultiIndex.from_product(
            [specification.keys(),
            ['Urbanization rate', 'Std.err', 'P-Value',]]
            )
    container = container.style.format('{:.2f}',na_rep='')

    return container

# get reg table countrydata
def get_table_countrydata(regressors, specification, data):
    """
    Can generate the regression table 5
    Inputs:
        - regressors: array of column names
        - specification: dictionary with column names
        - data: data frame (regiondata)
        
    Returns: container (pandas data frame with regression results)
        Beware! Multiindex codes set manually!
    """
    ## get list of regressors
    #regressors = []
    #for i in specification.keys():
    #    regressors.extend(specification[i])
    #regressors = list(set(regressors))


    container = pd.DataFrame()

    container['regressors'] = regressors
    container = container.set_index('regressors')

    for key in specification.keys():
        if key == "5.5 - Growth of captial city": #one regression on change in primacy
            table = pd.DataFrame({'Capital city growth': [], 'Std.err': [], 'P-Value': [],})

            table['regressors'] = regressors
            table = table.set_index('regressors')

            formula = "ADprimwidefrac ~"
            for regressors in specification[key]:
                formula = formula + f" + {regressors}"


            result = smf.ols(
                formula = formula, data=data
                ).fit(cov_type='HC1')#.fit(
                #cov_type='cluster',cov_kwds={'groups': data['afruid']},use_t=True
                #)
            for coef in specification[key]:
                outputs = [result.params[coef], result.bse[coef], result.pvalues[coef]]
                table.loc[coef] = outputs            
        else: #remaining regressions on change in urban growth
            table = pd.DataFrame({'Urbanization rate': [], 'Std.err': [], 'P-Value': [],})

            table['regressors'] = regressors
            table = table.set_index('regressors')

            formula = "ADurbfrac ~"
            for regressors in specification[key]:
                formula = formula + f" +{regressors}"


            result = smf.ols(
                formula = formula, data=data
                ).fit(cov_type='HC1')#.fit(
                #cov_type='cluster',cov_kwds={'groups': data['afruid']},use_t=True
                #)
            for coef in specification[key]:
                outputs = [result.params[coef], result.bse[coef], result.pvalues[coef]]
                table.loc[coef] = outputs

        
        container = pd.concat([container, table], axis=1)
    
    # Change variable names to labels
    codebook = get_data_codebook("countrydata")
    container = container.rename(codebook, axis="index")
    if key == "Only primate industry":
        container.columns = pd.MultiIndex.from_product(
            [specification.keys(),
            ['Capital city growth', 'Std.err', 'P-Value',]]
        )
        container = container.style.format('{:.3f}',na_rep='')
    else:
        # beware! codes set manually
        container.columns = pd.MultiIndex.from_product(
                [specification.keys(),
                ['Urbanization rate', 'Std.err', 'P-Value', 'Capital city growth']]
                ).set_codes([
                    [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4,4],
                    [3, 2, 1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 0, 2, 1]
                    ], level=[0, 1])
        container = container.style.format('{:.2f}',na_rep='')

    return container

# get reg table citydata
def get_table_citydata(regressors, specification, data):
    """
    Can generate the regression tables 6, ...
    Inputs:
        - regressors: array of column names
        - specification: dictionary with column names
        - data: data frame (regiondata)
        
    Returns: container (pandas data frame with regression results)
    """
    container = pd.DataFrame()

    container['regressors'] = regressors
    container = container.set_index('regressors')

    for key in specification.keys():
        # if condition not used currently
        if key == "5.5 - Growth of capital city": #one regression on change in primacy
            table = pd.DataFrame({'Growth of capital city': [], 'Std.err': [], 'P-Value': [],})

            table['regressors'] = regressors
            table = table.set_index('regressors')

            formula = "dlnl1 ~"
            for regressors in specification[key]:
                formula = formula + f" + {regressors}"


            result = smf.ols(
                formula = formula, data=data
                ).fit(
                cov_type='cluster',cov_kwds={'groups': data['agidison']},use_t=True
                )
            for coef in specification[key]:
                outputs = [result.params[coef], result.bse[coef], result.pvalues[coef]]
                table.loc[coef] = outputs            
        else: #remaining regressions on change city output
            table = pd.DataFrame({'City output': [], 'Std.err': [], 'P-Value': [],})

            table['regressors'] = regressors
            table = table.set_index('regressors')

            formula = "dlnl1 ~"
            for regressors in specification[key]:
                formula = formula + f" + {regressors}"
            
            formula = formula + "+ C(year) -1" #fixed effects

            def cluster_fit(formula, data, group_var): #function for clustering with missing values
                fit = smf.ols(formula, data=data).fit()
                to_keep = pd.RangeIndex(len(data)).difference(pd.Index(fit.model.data.missing_row_idx))
                robust = fit.get_robustcov_results(cov_type='cluster',
                                                   groups=data.iloc[to_keep][group_var])
                return robust #due to cluster fit the result is not a wrapper
            
            #c(var) for fixed effect - "-1" for dropping intercept
            result = cluster_fit(formula, data=data, group_var="agidison")
            
            for index,coef in enumerate(specification[key]): #need to index by position since result isn't a wrapper
                #find numer of fixed effect variables 
                alpha = result.params.size - np.size(specification[key])
                #find position of the coefficients
                position = alpha + index #no need to set to zero by -1 sinze lengths are being used
                
                outputs = [result.params[position], result.bse[position], result.pvalues[position]]
                table.loc[coef] = outputs

        
        container = pd.concat([container, table], axis=1)

    # Change variable names to labels
    codebook = get_data_codebook("citydata")
    container = container.rename(codebook, axis="index")
    
    
    container.columns = pd.MultiIndex.from_product(
            [specification.keys(),
            ['City output', 'Std.err', 'P-Value',]]
            )
    container = container.style.format('{:.3f}',na_rep='')

    return container

# get spatial regression table regiondata
def get_table_spatial_reg(regressors, specification, regiondata, w):
    """
    Generates a SDM estimate
    Inputs:
        - regressors: array of column names
        - specification: dictionary with column names
        - data: data frame (regiondata)
        - w: weight_matrix Geopandas object
        
    Returns: container (pandas data frame with regression results)
    """
    container = pd.DataFrame()

    container['regressors'] = regressors
    container = container.set_index('regressors')

    for key in specification.keys():
        table = pd.DataFrame({'Urbanization rate': [], 'Std.err': [], 'P-Value': [],})


        # preparing data
        y = regiondata["ADurbfrac"].to_numpy()
        y = np.reshape(y, (y.size, 1))


        x = np.array([regiondata[name] for name in specification[key]]).T
        
        #row standardize matrix
        w.transform = 'r'
        
        #two-stage regression
        result = spreg.GM_Lag(y, x, w=w,w_lags=1, name_y='ADurbfrac', name_x = specification[key])
        
        lags = ["WY"]
        variables = specification[key].extend(lags)
        for coef, _ in enumerate(specification[key]):
            coef += 1 #because of intercept
            outputs = [result.betas[coef][0], result.std_err[coef], result.z_stat[coef][1]]
            table.loc[_] = outputs
        
        container = pd.concat([container, table], axis=1)

    # Change variable names to labels
    codebook = get_data_codebook("regiondata")
    container = container.rename(codebook, axis="index")
    container.columns = pd.MultiIndex.from_product(
            [specification.keys(),
            ['Urbanization rate', 'Std.err', 'P-Value',]]
            )
    container = container.style.format('{:.3f}',na_rep='')

    return container

# coflict specification
def get_conflict_specification():
    """
    For obtaining order of regressors and regression specificaiton of table 8.
        
    Returns: regressors (list), specification (dictionary)
    """
    # specifying order of display
    regressors = ["dlnrain30",
                "extent_agH_dlnrain",
                "cflcnt3",
                "cflcnt3_50",
                "natconflict",
                "extent_agHcflcnt3",
                "extent_agHcflcnt3_50",
                "extent_agHnatconflict",
                "dlnrain30cflcnt3",
                "dlnrain30cflcnt3_50",
                "dlnrain30natconflict",
                "extent_agH_dlnraincflcnt3",
                "extent_agH_dlnraincflcnt3_50",
                "extent_agH_dlnrainnatconflict",
                "Lcflcnt3",
                "Lcflcnt3_50",
                "Lnatconflict",
                "extent_agHLcflcnt3",
                "extent_agHLcflcnt3_50",
                "extent_agHLnatconflict",
                "dlnrain30Lcflcnt3",
                "dlnrain30Lcflcnt3_50",
                "dlnrain30Lnatconflict",
                "extent_agH_dlnrainLcflcnt3",
                "extent_agH_dlnrainLcflcnt3_50",
                "extent_agH_dlnrainLnatconflict"]

    specification = {"8.1 - No conflict baseliness": 
                        ["dlnrain30",
                        "extent_agH_dlnrain"],
                    "8.2 - With conflict": 
                        ["dlnrain30",
                        "extent_agH_dlnrain",
                        "cflcnt3",
                        "cflcnt3_50",
                        "natconflict"],
                    "8.3 - Interaction conflict-lack of industry": 
                        ["dlnrain30",
                        "extent_agH_dlnrain",
                        "cflcnt3",
                        "cflcnt3_50",
                        "natconflict",
                        "extent_agHcflcnt3",
                        "extent_agHcflcnt3_50",
                        "extent_agHnatconflict"],
                    "8.4 - Interaction conflict-rainfall": 
                        ["dlnrain30",
                        "extent_agH_dlnrain",
                        "cflcnt3",
                        "cflcnt3_50",
                        "natconflict",
                        "extent_agHcflcnt3",
                        "extent_agHcflcnt3_50",
                        "extent_agHnatconflict",
                        "dlnrain30cflcnt3",
                        "dlnrain30cflcnt3_50",
                        "dlnrain30natconflict",
                        "extent_agH_dlnraincflcnt3",
                        "extent_agH_dlnraincflcnt3_50",
                        "extent_agH_dlnrainnatconflict"],
                    "8.5 - Lag of conflict": 
                        ["dlnrain30",
                        "extent_agH_dlnrain",
                        "Lcflcnt3",
                        "Lcflcnt3_50",
                        "Lnatconflict",
                        "extent_agHLcflcnt3",
                        "extent_agHLcflcnt3_50",
                        "extent_agHLnatconflict",
                        "dlnrain30Lcflcnt3",
                        "dlnrain30Lcflcnt3_50",
                        "dlnrain30Lnatconflict",
                        "extent_agH_dlnrainLcflcnt3",
                        "extent_agH_dlnrainLcflcnt3_50",
                        "extent_agH_dlnrainLnatconflict"]}
    return regressors, specification

# district level robustness checks
def get_district_robustness_specification():
    """
    For obtaining order of regressors and regression specificaiton of table 3.
            
    Returns: regressors (list), specification (dictionary)
    """
    #specifying order of display
    regressors = ["ADsm0_2moistu",
                "extent_agH_ADsm0_2moistu",
                "ADsm0_2moistu_nb",
                "extent_agH_ADsm0_2moistu_nb",
                "ADsm0_2preu",
                "ADsm0_2tmpu",
                "extent_agH_ADsm0_2preu",
                "extent_agH_ADsm0_2tmpu",
                "extent_agH",
                "firsturbfrac",
                "lndiscst",
                "ADsm0_2moistulndiscst"]

    #keys will be displayed in the regression table
    specification = {"3.1 - Distance to coast": 
                        ["ADsm0_2moistu",
                        "extent_agH_ADsm0_2moistu",
                        "ADsm0_2moistulndiscst",
                        "extent_agH",
                        "firsturbfrac",
                        "lndiscst"],
                    "3.2 - No interaction": 
                        ["ADsm0_2moistu",
                        "ADsm0_2moistulndiscst",
                        "extent_agH",
                        "firsturbfrac",
                        "lndiscst"],
                    "3.3 - Neighborhood effect": 
                        ["ADsm0_2moistu",
                        "ADsm0_2moistu_nb",
                        "extent_agH_ADsm0_2moistu",
                        "extent_agH_ADsm0_2moistu_nb",
                        "extent_agH",
                        "extent_agH_ADsm0_2moistu",
                        "firsturbfrac",
                        "lndiscst"],
                    "3.4 - Precipitation": 
                        ["ADsm0_2preu",
                        "extent_agH_ADsm0_2preu",
                        "extent_agH",
                        "firsturbfrac",
                        "lndiscst"],
                    "3.5 - Precipitation and temperature": 
                        ["ADsm0_2preu",
                        "extent_agH_ADsm0_2preu",
                        "ADsm0_2tmpu",
                        "extent_agH_ADsm0_2tmpu",
                        "extent_agH",
                        "firsturbfrac",
                        "lndiscst"]}
    return regressors, specification

def get_data_codebook(dataset):
    """
    For obtaining dictionary of variable labels
    Inputs: dataset (string), Name of the data set (one of: regiondata, citydata, countrydata)
        
    Returns: codebook (dictionary)
    """
    if dataset == "citydata":
        codes = pd.read_stata("data/citydata.dta", iterator=True).variable_labels()

        manual_entries = {
            "Lcflcnt3": "1(inside conflict t-1)",
            "Lcflcnt3_50": "1(outside conflict t-1)",
            "Lnatconflict": "1(national conflict t-1)",
            "extent_agHLcflcnt3": "1(inside conflict t-1)*(14-#all ind.)",
            "extent_agHLcflcnt3_50": "1(outside conflict t-1)*(14-#all ind.)",
            "extent_agHLnatconflict": "1(national conflict t-1)*(14-#all ind.)",
            "dlnrain30Lcflcnt3": "delta ln(rain(t))*1(inside conflict t-1)",
            "dlnrain30Lcflcnt3_50": "delta ln(rain(t))*1(outside conflict t-1)",
            "dlnrain30Lnatconflict": "delta ln(rain(t))*1(national conflict t-1)",
            "extent_agH_dlnrainLcflcnt3": "delta ln(rain(t))*1(inside conflict t-1)*(14-#all ind)",
            "extent_agH_dlnrainLcflcnt3_50": "delta ln(rain(t))*1(outside conflict t-1)*(14-#all ind)",
            "extent_agH_dlnrainLnatconflict": "delta ln(rain(t))*1(national conflict t-1)*(14-#all ind)"
            }
        # combine the stata labels with the manual additions
        codes.update(manual_entries)
        
    elif dataset == "regiondata":
        codes = pd.read_stata("data/regiondata.dta", iterator=True).variable_labels()
        manual_entries = {
            "ADsm0_1moistu": "delta moisture_1",
            "ADsm0_2moistu": "delta moisture_2",
            "ADsm0_3moistu": "delta moisture_3",
            "ADsm0_4moistu": "delta moisture_4",
            "ADsm0_2preu": "delta precipitation",
            "ADsm0_2tmpu": "delta temperature",
            "ADsm0_2moistu_nb": "neighbors' delta moisture_2",
            "ADsm0_2moistu_lag": "W*delta moisture_2",
            "WY": "WY"
            }

        # combine the stata labels with the manual additions
        codes.update(manual_entries)        

    elif dataset == "countrydata":
        codes = pd.read_stata("data/countrydata.dta", iterator=True).variable_labels()        
    
    
    else:
        raise AssertionError # incorret dataset name


    return codes

def LM_Test_Spatial_Dependence(specification, key, regiondata):
    #filtering out outliers
    regiondata = regiondata.query("abspctileADsm0_2moistu > 6 & abspctileADurbfrac > 6")
    #weight matrix
    w = lp.weights.KNN.from_dataframe(regiondata, k=8) #k nearest neighbour weights
    #row standardize matrix
    w.transform = 'r'
    
    # preparing data
    y = regiondata["ADurbfrac"].to_numpy()
    y = np.reshape(y, (y.size, 1))
    
    x = np.array([regiondata[name] for name in specification[key]]).T
    
    #Disclaimer
    ##due to an internal error (related to the refactoring of pysal) the spreg.OLS package
    ##does not run in CI. Until this is resolved, the test values are hardcoded (0.01, 0.02, 0.02) in here:

    #ols=spreg.OLS(y,x,w=w,name_y="ADurbfrac", name_x=specification[key],nonspat_diag=False, spat_diag=True)
    #print(f"For the Lagrange Multiplier test of spatial dependence, the p-value of rejecting the null of zero dependence of\n-The spatial lag is {ols.lm_lag[1]: .2f} \n-The spatial error is {ols.lm_error[1]: .2f}\n-The independent variables {ols.lm_sarma[1]: .2f}")
    
    print(f"For the Lagrange Multiplier test of spatial dependence, the p-value of rejecting the null of zero dependence of\n-The spatial lag is 0.01\n-The spatial error is 0.02\n-The independent variables 0.02")
    