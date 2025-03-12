import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import numpy as np

def load_image():
    image_path = "D:\Koral\koral6.png"  # Fixed image path
    image = cv2.imread(image_path)
    if image is None:
        st.error("Error: Image file not found! Check the file path.")
        return None
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

# Function to plot unique markers
def plot_markers(image, data):
    if image is None or data.empty:
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(image)
    
    # Get unique (x, y) locations and determine color
    unique_positions = data.groupby(['x', 'y'])['values'].max().reset_index()
    
    for _, row in unique_positions.iterrows():
        x, y, value = row['x'], row['y'], row['values']
        color = 'red' if value == 1 else 'blue'
        
        # Draw circle at unique coordinates
        ax.add_patch(plt.Circle((x, y), 9, color=color, fill=True))
        
        # Get all point numbers associated with this (x, y)
        points_at_location = data[(data['x'] == x) & (data['y'] == y)]
        point_numbers = ', '.join(map(str, points_at_location['points']))
        
        # Display colored point numbers above the circle
        ax.text(x, y - 15, point_numbers, color=color, fontsize=12, ha='center')
    
    ax.axis('off')
    st.pyplot(fig)

st.title("Listeria Detection at Koral")

# Upload Excel file
uploaded_file = st.file_uploader("Upload an Excel file with Date, Points, X, Y, Values, Description", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    if {'Date', 'points', 'x', 'y', 'values', 'description'}.issubset(df.columns):
        df['Date'] = pd.to_datetime(df['Date']).dt.date  # Ensure date format consistency
        unique_dates = df['Date'].unique()
        selected_date = st.selectbox("Select a Date", unique_dates)
        
        if selected_date:
            filtered_data = df[df['Date'] == selected_date]
            if not filtered_data.empty:
                image = load_image()
                plot_markers(image, filtered_data)
            else:
                st.warning("No markers found for the selected date.")
    else:
        st.error("Excel file must contain 'Date', 'points', 'x', 'y', 'values', and 'description' columns.")
