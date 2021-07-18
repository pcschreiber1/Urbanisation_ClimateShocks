"""This module contains auxiliary functions for generating graphs which are used in the main notebook."""

#Packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import geopandas as gpd
import shapely.geometry as geom
import libpysal as lp #For spatial weights

from auxiliary.data_import import *

pd.options.display.float_format = "{:,.2f}".format

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
        if key == "5.5 - Growth of capital city": #one regression on change in primacy
            table = pd.DataFrame({'Growth of capital city': [], 'Std.err': [], 'P-Value': [],})

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


            #c(var) for fixed effect - "-1" for dropping intercept
            result = smf.ols(
                formula = formula, data=data
                ).fit(cov_type='HC1')#.fit(
                #cov_type='cluster',cov_kwds={'groups': data['afruid']},use_t=True
                #)
            for coef in specification[key]:
                outputs = [result.params[coef], result.bse[coef], result.pvalues[coef]]
                table.loc[coef] = outputs

        
        container = pd.concat([container, table], axis=1)


    # beware! codes set manually
    container.columns = pd.MultiIndex.from_product(
            [specification.keys(),
            ['Urbanization rate', 'Std.err', 'P-Value', 'Growth in capital city']]
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


    
    container.columns = pd.MultiIndex.from_product(
            [specification.keys(),
            ['City output', 'Std.err', 'P-Value',]]
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