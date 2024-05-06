'''
Azhar Peerzde Final Project
Anqui Xu
Sunday, may 5
'''

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pandas as pd
import pydeck as pdk

#takes a list and coversts it into a string
def listToStrings(lst):
    result_str = ""
    for item in lst:
        result_str += item + ", "
    return result_str[:-2]


#takes a dictionary and makes a pie plot with the keys and values
def piePlotFromDict(dict):
    labels = list(dict.keys())
    sizes = list(dict.values())

    plt.figure()
    plt.pie(sizes,labels = labels, autopct = "%.2f")
    plt.title("Distribution of vehicles involved in each crash")
    plt.show()
    return plt

#creates a bar plot of crashes per hour
def barPlot(hourDict):
    labels = list(hourDict.keys())
    values = list(hourDict.values())
    plt.figure()
    plt.bar(labels,values)
    plt.xticks(rotation = 45)
    plt.ylabel("Number of Crashes")
    plt.xlabel("Hour of the Day")
    plt.title("Distribution of Crashes by Hour")
    plt.show()
    return plt

#creates a dictionary of all the times for each crash
def countTimes(times):
    hours = {}
    for time in times:
        accTime, amPm = time.split()
        hour = accTime.split(":")[0]
        currentHour = f"{hour}:00 {amPm}"

        if currentHour not in hours:
            hours[currentHour] = 1
        else:
            hours[currentHour] += 1

    return hours

#filters the data by specfic inputs
def filterData(df, towns, district, raodCondition):
    df = df[df["CITY_TOWN_NAME"].isin(towns)]

    df = df[df["DISTRICT_NUM"] == district]
    df = df[df["ROAD_SURF_COND_DESCR"] == raodCondition]

    df = df.sort_values(by="OBJECTID", ascending=True)
    return df

#counts the items in a list
def counting(list):
    counted = {}
    for i in list:
        if i not in counted:
            counted[i] = 1
        else:
            counted[i] += 1
    return counted

#generates a map of all the crashes
def generate_map(df):
    map_df = df[["LAT", "LON"]]

    view_state = pdk.ViewState(
        latitude=map_df["LAT"].mean(),
        longitude=map_df["LON"].mean(),
        zoom=12
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["LON", "LAT"],
        get_radius=100,
        get_color=[200, 30, 0, 160]
    )

    map = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9"
    )
    st.pydeck_chart(map)


#calculates max and min of non fatal crashes
def maxMinCrashes(df, column, towns=None):
    if towns is not None:
        df = df[df["CITY_TOWN_NAME"].isin(towns)]
    maxCrashes = df[column].max()
    minCrashes = df[column].min()
    return maxCrashes, minCrashes

def main():
    #basic set up and definiton of variables
    st.set_page_config(page_title="Crash Data Analysis", layout="wide")
    df = pd.read_csv("2017_Crashes_10000_sample.csv", header=0, low_memory=False).set_index("OBJECTID")
    towns = df["CITY_TOWN_NAME"].unique().tolist()
    districts = df["DISTRICT_NUM"].unique().tolist()
    conditions = df["ROAD_SURF_COND_DESCR"].unique().tolist()
    #input
    townsSelected = st.sidebar.multiselect("Select the towns you want to see:", towns)
    district = st.sidebar.slider("Select a district", min_value=min(districts), max_value=max(districts),value=(min(districts)))
    roadCondition = st.sidebar.selectbox("Select a road condition:", conditions)

    # Filter data based on user input
    townData = filterData(df, townsSelected if townsSelected else towns, district, roadCondition)

    if not townData.empty:
        generate_map(townData)
        times = townData["CRASH_TIME"].tolist()
        hourCounts = countTimes(times)
        st.pyplot(barPlot(hourCounts))

        numV = townData["NUMB_VEHC"]

        st.pyplot(piePlotFromDict(counting(numV)))

        maxInjuries, minInjuries = maxMinCrashes(townData, "NUMB_NONFATAL_INJR", townsSelected)
        st.write(f"Maximum Non-Fatal Injuries: {maxInjuries}")
        st.write(f"Minimum Non-Fatal Injuries: {minInjuries}")

        totalNonFatalInj = {}

        for index, row in townData.iterrows():
            town = row["CITY_TOWN_NAME"]
            nonFatalInj = row["NUMB_NONFATAL_INJR"]

            if town in totalNonFatalInj:
                totalNonFatalInj[town] += nonFatalInj
            else:
                totalNonFatalInj[town] = nonFatalInj

        dfDict = pd.DataFrame.from_dict(totalNonFatalInj, orient="index", columns=["TotalNonFatalInjuries"])
        dfDict.reset_index(inplace=True)
        dfDict.rename(columns={"index": "Town"}, inplace=True)

        pivot_table = dfDict.pivot_table(index="Town", values="TotalNonFatalInjuries", aggfunc="sum")

        st.write(pivot_table)

        st.write(townData)



    else:
        st.error("No data available for the selected criteria.")


main()
