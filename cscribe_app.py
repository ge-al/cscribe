import streamlit as st
from annotated_text import annotated_text, parameters
import pycantonese
import pandas as pd
import json
import re

st.set_page_config(layout="wide")


# Function to clear input fields
def clear_input():
    st.session_state['term'] = ""
    st.session_state['definition'] = ""


def load_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        return json.load(file)

def separate_characters_and_jyutping(input_text):
    # Extract Chinese characters
    characters = ''.join(re.findall(r'[\u4e00-\u9fff]', input_text))
    # Extract Jyutping
    jyutping = ' '.join(re.findall(r'[a-zA-Z0-9]+', input_text))
    return characters, jyutping

# Load csh_dict.json
csh_dict = load_json("csh_dict.json")


with st.sidebar:
    
    # ***YouTube Video Embed***
    st.header("Embed YouTube Video")
    youtube_url = st.text_input("Enter YouTube URL")
    if youtube_url:
        st.video(youtube_url)
        
    # ***Word lookup***
    st.header("Define term:")
    # Look-up web dictionaries
    honzi = st.text_input("Add characters below, then press \"enter\"", "")
    if honzi:

        if honzi in csh_dict:
            sheik_url = csh_dict[honzi]["link"]
            cantowords_link = f"[Look up {honzi} on Sheik]({sheik_url})"
            st.markdown(cantowords_link, unsafe_allow_html=True)

        wiki_url = f"https://en.wiktionary.org/wiki/{honzi}#Chinese"
        wiki_link = f"[Look up {honzi} on Wiktionary]({wiki_url})"
        st.markdown(wiki_link, unsafe_allow_html=True)

        cantowords_url = f"https://cantowords.com/dictionary/{honzi}"
        cantowords_link = f"[Look up {honzi} on CantoWords]({cantowords_url})"
        st.markdown(cantowords_link, unsafe_allow_html=True)
    
    st.divider()

    # ***Vocabulary list***
    st.header("Create vocabulary list:")
    # Initialize the vocabulary list in session state if it doesn't exist
    if 'vocabulary' not in st.session_state:
        st.session_state['vocabulary'] = []

    # Input fields for term and definition using session state values to reset them
    term = st.text_input("Add Term", value=st.session_state.get('term', ''))
    definition = st.text_input("Add Your Definition", value=st.session_state.get('definition', ''))

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
    
    st.divider()
    # ***JP / HZ separate***
    st.header("Separate hon3zi6 and jyutping")
    separate_input = st.text_input("Paste text here for separation", key="separate_input")

    if separate_input:
        characters, jyutping = separate_characters_and_jyutping(separate_input)
        st.write("Hon3zi6:")
        st.write(characters)
        st.write("Jyutping:")
        st.write(jyutping)

    st.divider()
    
    # ***Export Lesson***
    st.header("Export Lesson")
    if st.button("Export Lesson"):
        lesson_data = {
            "text": st.session_state.get('user_input', ''),
            "vocab": st.session_state.get('vocabulary', [])
        }
        lesson_json = json.dumps(lesson_data, ensure_ascii=False, indent=4)
        st.download_button(label="Download JSON", data=lesson_json, file_name="lesson.json", mime='application/json')

    st.divider()

    # ***Import Lesson***
    st.header("Import Lesson")
    uploaded_file = st.file_uploader("Choose a .json file", type="json")
    if uploaded_file is not None:
        lesson_data = json.load(uploaded_file)
        st.session_state['user_input'] = lesson_data.get('text', '')
        st.session_state['vocabulary'] = lesson_data.get('vocab', [])
        st.success("Lesson imported successfully!")

    

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
st.title("HauYu (cscribe 3.1)")

user_input = st.text_area("Enter text here", value=st.session_state.get('user_input', ''), label_visibility='collapsed')

# Update session state whenever the user types
st.session_state['user_input'] = user_input

# Correct pycantonese transliteration errors
jp_adjustments = load_json("jp_adjustments.json")


if user_input:
    input_lines = user_input.split("\n")
    for line in input_lines:
        output = []
        score = pycantonese.characters_to_jyutping(line)
        for hz, jp in score:
            if not jp:
                output.append(hz)
            elif hz in jp_adjustments:
                output.append((jp_adjustments[hz], hz, "#FFFCFF"))
            else:
                output.append((jp, hz, "#FFFCFF"))
        annotated_text(*output)
