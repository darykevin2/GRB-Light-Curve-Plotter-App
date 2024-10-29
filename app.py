import streamlit as st
from astropy.io import fits
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import io
import os

# Load CSS from the style file
def load_css(file_path):
    with open(file_path) as f:
        return f"<style>{f.read()}</style>"

# Apply the CSS
st.markdown(load_css("style.css"), unsafe_allow_html=True)

def load_fits_data(file):
    try:
        with fits.open(file, memmap=True) as hdul:
            all_count_data = np.array(hdul[2].data)
        return all_count_data['TIME'].astype(float)
    except (IndexError, KeyError) as e:
        st.error(f"Error reading FITS data: {e}")
        return None

def format_header(filename):
    match = re.match(r'glg_tte_n\d+_bn(\d+)_v\d+.fit', filename)
    if match:
        return f"Light Curve for GRB{match.group(1)}", f"GRB{match.group(1)}"
    return f"File: {filename}", "LightCurve"

# Apply custom title
st.markdown('<h1 class="custom-title">Light Curve Plotter</h1>', unsafe_allow_html=True)

# Apply custom description
st.markdown('<p class="custom-description">This App allows you to visualize GRB light curves. You can either upload a FITS file or select one from the list to explore the app\'s functionalities.</p>', unsafe_allow_html=True)
st.markdown('----')

# Option to upload a file or select from Datasets folder
option = st.radio("Choose an option:", ("Upload a FITS file", "Select a file from Datasets"))

if option == "Upload a FITS file":
    uploaded_file = st.file_uploader("Upload a FITS file", type="fit")
    if uploaded_file is not None:
        file_name = uploaded_file.name
else:
    dataset_files = os.listdir('Datasets')
    selected_file = st.selectbox("Select a FITS file from Datasets", dataset_files)
    if selected_file:
        file_name = selected_file
        uploaded_file = open(os.path.join('Datasets', selected_file), 'rb')

if uploaded_file is not None:
    status_message = st.empty()
    status_message.text("Processing....")
    times = load_fits_data(uploaded_file)
    if times is not None:
        header, base_filename = format_header(file_name)
        st.header(header)
        
        # Input fields for binning
        col1, col2 = st.columns([1, 4])
        with col1:
            begin_value = st.number_input("Begin value", value=float(np.min(times)))
            end_value = st.number_input("End value", value=float(np.max(times)))
            bin_width = st.number_input("Bin width", value=0.1, step=0.1, min_value=0.1)
            color = st.color_picker("Choose a color", "#4f46e5")
        
        # Ensure that end_value is greater than begin_value
        if begin_value < end_value:
            # Plotting
            bin_edges = np.arange(begin_value, end_value + bin_width, bin_width)
            with col2:
                sns.set(style="whitegrid")  # Set the style to whitegrid for light gridlines
                plt.figure(figsize=(12, 6))
                sns.histplot(times, bins=bin_edges, kde=False, color=color)
                plt.xlabel('Time')
                plt.ylabel('Counts')
                plt.title(header)
                
                st.pyplot(plt)
                
                # Save plot to a buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='jpeg')
                buf.seek(0)
                
                # Download button
                st.download_button(
                    label="Download image",
                    data=buf,
                    file_name=f"{base_filename}.jpeg",
                    mime="image/jpeg"
                )
                
                # Clear the "Processing..." message
                status_message.empty()
        else:
            st.error("Ensure that the 'End value' is greater than the 'Begin value'.")
            status_message.empty()