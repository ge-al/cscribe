import streamlit as st
from annotated_text import annotated_text, parameters
import pycantonese
import pandas as pd

st.set_page_config(layout="wide")


# Function to clear input fields
def clear_input():
    st.session_state['term'] = ""
    st.session_state['definition'] = ""


with st.sidebar:
    # Initialize the vocabulary list in session state if it doesn't exist
    if 'vocabulary' not in st.session_state:
        st.session_state['vocabulary'] = []

    # Input fields for term and definition using session state values to reset them
    term = st.text_input("Input Term", value=st.session_state.get('term', ''))
    definition = st.text_input("Definition", value=st.session_state.get('definition', ''))

    # Button to add the term and definition to the vocabulary list
    if st.button("Add to Vocab List"):
        if term and definition:  # Check if both fields are filled
            st.session_state['vocabulary'].append((term, definition))
            clear_input()  # Clear the input fields manually
        else:
            st.warning("Both term and definition must be filled.")

    # Display the current vocabulary list
    st.write("Vocabulary List:")
    for idx, (stored_term, stored_definition) in enumerate(st.session_state['vocabulary'], start=1):
        st.text(f"{idx}. {stored_term}: {stored_definition}")

    # Button to show filename input for CSV export
    if st.button("Export CSV"):
        if st.session_state['vocabulary']:
            st.session_state['show_filename_input'] = True  # Set the flag to show input field
        else:
            st.warning("No vocabulary to export.")

# Show filename input and download button if flag is set
if st.session_state.get('show_filename_input', False):
    with st.sidebar:
        file_name = st.text_input("Enter filename for CSV", value="vocabulary_list.csv")
        if file_name:  # Once filename is entered, prepare for download
            df = pd.DataFrame(st.session_state['vocabulary'], columns=["Term", "Definition"])
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download CSV", data=csv, file_name=file_name, mime='text/csv')
            st.session_state['show_filename_input'] = False  # Reset the flag

# Customize the appearance of annotated text
parameters.BORDER_RADIUS = 0
parameters.PADDING = "5px 20px 5px 5px"

# Set up the title of the app
st.title("CantoScribe v1")

user_input = st.text_area("Enter text here", value=st.session_state.get('user_input', ''), label_visibility='collapsed')

# Update session state whenever the user types
st.session_state['user_input'] = user_input


if user_input:
    input_lines = user_input.split("\n")
    for line in input_lines:
        output = []
        score = pycantonese.characters_to_jyutping(line)
        for hz, jp in score:
            if not jp:
                output.append(hz)
            else:
                output.append((jp, hz, "#FFFCFF"))
        annotated_text(*output)
