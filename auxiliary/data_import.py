"""This module contains auxiliary functions for importing data which are used in the main notebook."""

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

from auxiliary.plots import *
from auxiliary.simulations import *
from auxiliary.tables import *

# Importing data
def importing_regiondata():
    """
    Loads the regiondata
        Should convert the year column to proper year
        
        Should immediately create geopandas dataframe
    Returns: a dataframe
    """
    regiondata = pd.read_stata("data/regiondata.dta")
    return regiondata

# Get spatial data
def get_spatialdata():
    """
    Converts regiondata and citydata into GeoPandas DF and projects it

    Returns: two GeoPandas dataframes (regiondata, citydata)
    """
    #district level
    ##creating pandas dataframe
    regiondata = pd.read_stata("data/regiondata.dta") #--> need to also do for other 
    #regiondata = regiondata.query("abspctileADsm0_2moistu > 6 & abspctileADurbfrac > 6")

    ##creating geopandas dataframe
    regiondata["geometry"] = regiondata[["lon", "lat"]].apply(geom.Point, axis=1) #take each row
    regiondata = gpd.GeoDataFrame(regiondata)
    regiondata.crs = "EPSG:4326"
    
    #city level
    ##creating pandas dataframe
    citydata = pd.read_stata("data/citydata.dta")
    #regiondata = regiondata.query("abspctileADsm0_2moistu > 6 & abspctileADurbfrac > 6")

    ##creating geopandas dataframe
    citydata["geometry"] = citydata[["lon", "lat"]].apply(geom.Point, axis=1) #take each row
    citydata = gpd.GeoDataFrame(citydata)
    citydata.crs = "EPSG:4326"
    
    return regiondata, citydata


# Get shape file
def get_shapefile():
    #creating relevant shapefile
    #--------------------
    regiondata = pd.read_stata("data/regiondata.dta") 

    ###creating geopandas dataframe
    regiondata["geometry"] = regiondata[["lon", "lat"]].apply(geom.Point, axis=1) #take each row
    regiondata = gpd.GeoDataFrame(regiondata)
    regiondata.crs = "EPSG:4326"

    ### districts shapefile
    areg = gpd.read_file("data/Henderson_shapefile/afrregnew.gdb")
    areg.crs = "EPSG:4326"

    ### coastlien shapefile
    coast = gpd.read_file("data/afr_g2014_2013_0.shp")
    coast.crs = "EPSG:4326"

    ### Joining region data and districts
    gdb_join = gpd.sjoin(regiondata, areg, how="right", op="within")

    return gdb_join, coast

# Creating table 1 a (regiondata)
def table_1_a(data):
    """
    Input regiondata from "importing_regiondata()"

    Returns: ?
    """
    df = data.query("abspctileADsm0_2moistu > 6 & abspctileADurbfrac > 6")
    
    var_list = ["ADsm0_2moistu", "mean_moistu1950_69", "ADurbfrac", "firsturbfrac", "lndiscst",
            "areasqkm", "extent_agE", "extent_agH", "D_moist_GT1"]

    df = df[var_list].sort_values(by = var_list)
    
    df = df.rename(columns={"ADsm0_2moistu" : "Annualized moisture growth"})

    return df

# Creating Figure 4 (Variability of climate change in Africa)
def figure_4(data):
    
    #Moisture, three-year moving average  normalized by country 1950-69 mean
    data["sm0_2normarid"] = data["sm0_2moistu"]/ data["mean_moistu1950_69"]
    
    fig, ax = plt.subplots(figsize=(10,4))
    for key, grp in data.groupby(['iso3v10']):
        ax.plot(grp['year'], grp['sm0_2normarid'], label=key)

    ax.legend(bbox_to_anchor=(0, 0, 1, -0.1), ncol=5, mode="expand", borderaxespad=0.)
    #ax.legend(bbox_to_anchor=(0, -0,5))#, loc="lower center")
    figure = plt.show()
    return figure

