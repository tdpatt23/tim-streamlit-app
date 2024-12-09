"""Class: CS230--Section 1
Name: Timothy Patterson
Description: Final Project - Fortune 500 Companies Analysis
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student. """

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import pydeck as pdk

st.title("Fortune 500 Companies Analysis")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview / National Comparison", "State Comparison"])

def overview_and_national():
    st.header("Overview & National Comparison")

    data = pd.read_csv("fortune_500_hq.csv") #loads the data from the main csv file
    industry_data = pd.read_csv("companies_industries.csv") #loads the data from the csv file I made with industries

    data["NAME"] = data["NAME"].str.strip().str.upper() #this "preps" the data so it just makes it easier to find and reference
    industry_data["COMPANY"] = industry_data["COMPANY"].str.strip().str.upper()

    map_data = data[["NAME", "LATITUDE", "LONGITUDE", "REVENUES", "EMPLOYEES"]].dropna()

    map_layer = pdk.Layer(   #this defines the pydeck layer (reference the youtube video you watched)
        "ScatterplotLayer",
        data=map_data,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=600,  #radius of the scatter points on the map (want to change this so it is dynamic with the zoom level)
        get_color=[255, 0, 0],  #color for pins on the map
        pickable=True,
    )

    initial_view = pdk.ViewState(   #this gives the initial view of the map when you open or refresh the page
        latitude=map_data["LATITUDE"].mean(),
        longitude=map_data["LONGITUDE"].mean(),
        zoom=2,
        pitch=0,
    )

    tooltip = {   #the tooltip gives the basic company data when we hover over a point on the map (again, reference the youtube video)
        "html": "<b>Company:</b> {NAME}<br>"
                "<b>Revenue:</b> ${REVENUES}M<br>"
                "<b>Employees:</b> {EMPLOYEES}",
        "style": {"color": "white", "backgroundColor": "black"},
    }

    deck = pdk.Deck(   #I think of this as basically "calling" the pydeck map
        layers=[map_layer],
        initial_view_state=initial_view,
        tooltip=tooltip,
    )

    st.pydeck_chart(deck) #puts the pydeck map in streamlit

    st.subheader("National Industry Revenue Concentration")

    # Aggregate revenues by industry for the entire dataset
    national_industry_revenue = industry_data.groupby("INDUSTRY")["REVENUES"].sum()

    if not national_industry_revenue.empty:
        # Create a pie chart
        fig, ax = plt.subplots()
        ax.pie(
            national_industry_revenue,
            labels=national_industry_revenue.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Set3.colors  # Use another colormap for variety
        )
        ax.set_title("National Revenue Concentration by Industry")
        st.pyplot(fig)
    else:
        st.warning("No industry data available.")


    st.subheader("Top 10 Companies by Revenue")

    top_10_revenue = data.nlargest(10, "REVENUES") #this sorts the data by the 10 companies with the highest revenue

    fig, ax = plt.subplots() #bar chart for the companies with the 10 highest revenues
    ax.barh(top_10_revenue["NAME"], top_10_revenue["REVENUES"], color="blue")
    ax.set_xlabel("Revenue (in Millions)")
    ax.set_ylabel("Company Name")
    ax.set_title("Top 10 Companies by Revenue")
    ax.invert_yaxis()  #learned about this method instead of doing the ascending or descending
    st.pyplot(fig)

    filtered_data = data[data["REVENUES"] < data["REVENUES"].max()] #for the national comparison scatterplot I wanted to exclude the point with the highest revenue because it made the graph look weird with most of the points bunched at the bottom

    fig, ax = plt.subplots() #makes the scatterplot comparing company revenue to the number of employees it has
    ax.scatter(filtered_data["EMPLOYEES"], filtered_data["REVENUES"], alpha=0.7, color="green") #also had to look up what alpha does
    ax.set_xlabel("Number of Employees")
    ax.set_ylabel("Revenue (in Millions)")
    ax.set_title("Revenue vs. Number of Employees (Excluding Highest Revenue)")
    st.pyplot(fig)

    min_revenue, max_revenue = st.slider(   #this makes the slider so we can select a range of revenues to look at (like companies between 10 and 20 billion for example)
        "Select Revenue Range (in Millions)",   #the user doesn't need to actually use the slider (they can just have the slider at the farthest left or right)
        min_value=int(industry_data["REVENUES"].min()),
        max_value=int(industry_data["REVENUES"].max()),
        value=(int(industry_data["REVENUES"].min()), int(industry_data["REVENUES"].max())),
        step=1000,
    )

    industries = ["All"] + industry_data["INDUSTRY"].dropna().unique().tolist() #the dropdown to select an industry from the other csv file I made
    selected_industry = st.selectbox("Select an Industry", industries)

    filtered_data = industry_data[  #filters the data by revenue from highest to lowest once a range is given from the slider
        (industry_data["REVENUES"] >= min_revenue) &
        (industry_data["REVENUES"] <= max_revenue)
        ]
    if selected_industry != "All": #the user doesn't need to select an industry of they don't want to
        filtered_data = filtered_data[filtered_data["INDUSTRY"] == selected_industry]

    st.subheader("Top 10 Companies by Revenue (Filtered)") #this makes the bar chart for the filtered data
    top_10_filtered = filtered_data.nlargest(10, "REVENUES")
    fig, ax = plt.subplots()
    ax.barh(top_10_filtered["COMPANY"], top_10_filtered["REVENUES"], color="orange")
    ax.set_xlabel("Revenue (in Millions)")
    ax.set_ylabel("Company Name")
    ax.set_title("Top 10 Companies by Revenue (Filtered)")
    ax.invert_yaxis() #use the same invert as above
    st.pyplot(fig)

    st.subheader("Scatterplot: Number of Employees vs. Revenue (Filtered)") #this makes the scatterplot for the filtered data
    if not filtered_data.empty:
        fig, ax = plt.subplots()
        ax.scatter(filtered_data["EMPLOYEES"], filtered_data["REVENUES"], alpha=0.7, color="purple")
        ax.set_xlabel("Number of Employees")
        ax.set_ylabel("Revenue (in Millions)")
        ax.set_title("Revenue vs. Number of Employees (Filtered)")
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters.")


def state_comparison():
    st.header("State-by-State Comparison")

    data = pd.read_csv("fortune_500_hq.csv")  #same as above
    industry_data = pd.read_csv("companies_industries.csv")

    data["NAME"] = data["NAME"].str.strip().str.upper() #same as above
    industry_data["COMPANY"] = industry_data["COMPANY"].str.strip().str.upper()

    unique_states = sorted(data["STATE"].dropna().unique().tolist()) #this gets the state IDs from the main data file

    selected_state = st.selectbox("Select a State (ID)", unique_states) #this is a dropdown to choose a state, there is no "all" option like on the first page with the industries, I want the user to have to select the state because that is the function of this page, comes before map so the map updates

    filtered_data = data[data["STATE"] == selected_state] #filters the data similar to above

    map_data = filtered_data[["NAME", "LATITUDE", "LONGITUDE", "REVENUES", "EMPLOYEES"]].dropna()

    map_layer = pdk.Layer(   #same as above, used the same pydeck map just different colors, only difference is that the only points that show up are for the points within the selected state
        "ScatterplotLayer",
        data=map_data,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=600,
        get_color=[200, 0, 255],  #purple color for the pins
        pickable=True,
    )

    initial_view = pdk.ViewState(
        latitude=map_data["LATITUDE"].mean() if not map_data.empty else 37.7749,  #basically the map will open to the center of the U.S., had to play around with this to get it right
        longitude=map_data["LONGITUDE"].mean() if not map_data.empty else -95.7134,
        zoom=2,
        pitch=0,
    )

    tooltip = {   #same as above, the info will pop up when you hover over a point
        "html": "<b>Company:</b> {NAME}<br>"
                "<b>Revenue:</b> ${REVENUES}M<br>"
                "<b>Employees:</b> {EMPLOYEES}",
        "style": {"color": "white", "backgroundColor": "black"},
    }

    deck = pdk.Deck(   #same as above
        layers=[map_layer],
        initial_view_state=initial_view,
        tooltip=tooltip,
    )

    st.pydeck_chart(deck)

    st.subheader("Industry Revenue Concentration in Selected State")

    industry_state_data = industry_data[industry_data["COMPANY"].isin(filtered_data["NAME"])] #filters the industry data for companies in the selected state

    industry_revenue_concentration = industry_state_data.groupby("INDUSTRY")["REVENUES"].sum() #adds up revenues by industry

    if not industry_revenue_concentration.empty:
        fig, ax = plt.subplots()   #creates a pie chart of industry concentration
        ax.pie(
            industry_revenue_concentration,
            labels=industry_revenue_concentration.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Paired.colors  #learned that this gives distinct colors for each section of the pie chart
        )
        ax.set_title("Revenue Concentration by Industry in Selected State")
        st.pyplot(fig)
    else:
        st.warning("No industry data available for the selected state.")

    st.subheader("Top 10 Companies by Revenue in Selected State") #bar chart of revenues for the filtered company data by state
    top_10_revenues = (
        filtered_data.nlargest(10, "REVENUES")[["NAME", "REVENUES"]]
        .sort_values(by="REVENUES", ascending=True) #filtered by highest to lowest revenue so I didn't have to use the invert again
    )
    fig, ax = plt.subplots()
    ax.barh(top_10_revenues["NAME"], top_10_revenues["REVENUES"], color="skyblue")
    ax.set_xlabel("Revenue (in Millions)")
    ax.set_ylabel("Company Name")
    ax.set_title("Top 10 Companies by Revenue")
    st.pyplot(fig)

    st.subheader("Scatterplot: Revenue vs. Employees in Selected State") #scatter plot of the filtered state data
    fig, ax = plt.subplots()
    ax.scatter(filtered_data["EMPLOYEES"], filtered_data["REVENUES"], color="purple", alpha=0.7)
    ax.set_xlabel("Employees")
    ax.set_ylabel("Revenue (in Millions)")
    ax.set_title("Revenue vs. Employees")
    st.pyplot(fig)

if page == "Overview / National Comparison": #this whole if function determines which function to operate and show based on the page that is selected
    overview_and_national()
elif page == "State Comparison":
    state_comparison()
