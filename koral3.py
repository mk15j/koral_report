import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os

def load_image(image_path="koral6.png"):
    """Load and process the image."""
    if not os.path.exists(image_path):
        st.error(f"Error: Image file not found at {image_path}!")
        return None
    
    image = cv2.imread(image_path)
    if image is None:
        st.error("Error: Failed to load image!")
        return None
    
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def plot_markers(image, data):
    """Plot markers with different colors based on 'values'."""
    if image is None or data.empty:
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(image)

    # Ensure data contains necessary columns
    required_columns = {'x', 'y', 'values', 'points'}
    if not required_columns.issubset(data.columns):
        st.error(f"Missing required columns: {required_columns - set(data.columns)}")
        return

    # Get unique (x, y) locations
    unique_positions = data.groupby(['x', 'y'])['values'].max().reset_index()

    for _, row in unique_positions.iterrows():
        x, y, value = row['x'], row['y'], row['values']

        # Determine color based on value
        if pd.isna(value):  # If empty (NaN)
            color = '#FFBF00'  # Amber
        elif value == 1:
            color = '#FF0000'  # Red
        else:
            color = '#008000'  # Green

        # Draw circle at unique coordinates
        ax.add_patch(plt.Circle((x, y), 9, color=color, fill=True))

        # Get all point numbers associated with this (x, y)
        points_at_location = data[(data['x'] == x) & (data['y'] == y)]
        point_numbers = ', '.join(map(str, points_at_location['points']))

        # Display point numbers above the circle
        ax.text(x, y - 15, point_numbers, color=color, fontsize=12, ha='center')

    ax.axis('off')
    st.pyplot(fig)

# Streamlit App
st.title("Listeria Detection at Koral")

# Upload Excel file
uploaded_file = st.file_uploader("Upload an Excel file with Date, Points, X, Y, Values, Description", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()
    
    required_columns = {'date', 'points', 'x', 'y', 'values', 'description'}
    if not required_columns.issubset(df.columns):
        st.error(f"Excel file must contain columns: {required_columns}")
    else:
        df['date'] = pd.to_datetime(df['date']).dt.date  # Ensure date format consistency
        unique_dates = df['date'].unique()
        selected_date = st.selectbox("Select a Date", unique_dates)
        
        if selected_date:
            filtered_data = df[df['date'] == selected_date]
            if not filtered_data.empty:
                image = load_image()
                plot_markers(image, filtered_data)
            else:
                st.warning("No markers found for the selected date.")
