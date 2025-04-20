import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px

import streamlit as st
from streamlit_gsheets import GSheetsConnection


st.title("Moods of the Patient Queue")
st.markdown("Enter the vibe of a new ticket below.")

# Establish Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)


# List of Emojis options for the mood
mood_options = [
    "😄", "🙂", "😐", "🙁", "😢", "😡", "😂", "👍", "👎"
]

with st.form(key="mood_entry", clear_on_submit=True):
    # Form options
    mood = st.selectbox("Mood?", options=mood_options, index=None)
    notes = st.text_area(label="Notes (optional)", height=68)
    
    submit_button = st.form_submit_button(label="Submit")
    
    if submit_button:
        if not mood:
            st.warning("Ticket mood was not selected")
            st.stop()
        else:
            timestamp = datetime.now()
            new_data = pd.DataFrame([{
                "timestamp": timestamp,
                "mood": mood,
                "notes": notes
            }])
        
        # Retrieve old data
        data = conn.read(worksheet="Moods", usecols=list(range(3)), ttl=0) 
        updated_df = pd.concat([data, new_data], ignore_index=True)

        # Update Google Sheet
        conn.update(worksheet="Moods", data=updated_df)
            
        st.success("Ticket mood successfully submitted!")
       
    
data = conn.read(worksheet="Moods", usecols=list(range(3)), ttl=0)
data["timestamp"] = pd.to_datetime(data["timestamp"])

# Get today's date
today = datetime.now().date()
today_data = data[data['timestamp'].dt.date == today]

# Filter plot based on +/- mood
positive_moods = ["😄", "🙂", "👍", "😂"]
negative_moods = ["🙁", "😢", "😡", "👎"]

st.divider()

mood_filter = st.selectbox("Select mood category", options=["All", "Positive", "Negative"])

if mood_filter == "Positive":
    filtered_data = today_data[today_data["mood"].isin(positive_moods)]
elif mood_filter == "Negative":
    filtered_data = today_data[today_data["mood"].isin(negative_moods)]
else:
    filtered_data = today_data
    


if not filtered_data.empty:
    # Aggregate mood data
    mood_counts = filtered_data["mood"].value_counts().reset_index()
    mood_counts.columns = ["mood", "count"]

    # Bar chart
    fig = px.bar(
        mood_counts,
        x="mood",
        y="count",
        color="mood",
        title="Today's Moods",
        text="count"
    )
    
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=14),
        width=0.5  
    )
    
    max_count = mood_counts["count"].max()
    y_buffer = max_count * 0.25 
    
    
    fig.update_layout(
        yaxis=dict(
            title="Count",
            range=[0, max_count + y_buffer]
        ),
        xaxis=dict(
            title="Mood",
            tickmode='linear',
            tickfont=dict(size=24) 
        ),
        showlegend=False
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_title="Count", xaxis_title="Mood", showlegend=False)

    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.write("No moods logged for today.")
    
    
    