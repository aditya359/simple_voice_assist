import tkinter as tk
import speech_recognition as sr
import pyttsx3
import requests
from googlesearch import search
from bs4 import BeautifulSoup
import webbrowser
import pyjokes
import datetime
import os

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Global variables to keep track of input and response modes
is_speech_mode = True  # Input mode
is_response_mode_speech = True  # Response mode

# Function to speak the response
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to perform a Google search and return the text response
def google_search(query):
    search_results = list(search(query, num_results=1))
    if not search_results:
        return "No results found."

    url = search_results[0]
    print(f"First result URL: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        paragraphs = soup.find_all('p')
        text_response = ' '.join(paragraph.text for paragraph in paragraphs)

        if not text_response:
            title = soup.title.string if soup.title else "No title found."
            text_response = title

        return text_response if text_response else "No text found."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

# Function to tell a joke
def tell_joke():
    joke = pyjokes.get_joke()
    return joke

# Function to open applications
def open_application(app_name):
    try:
        if app_name.lower() == "notepad":
            os.system("notepad.exe")
        elif app_name.lower() == "calculator":
            os.system("calc.exe")
        else:
            return f"Application '{app_name}' not recognized."
        return f"Opening {app_name}..."
    except Exception as e:
        return f"Failed to open {app_name}: {e}"

# Function to handle the speech recognition
def recognize_speech():
    if is_speech_mode:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            response = process_command(command)
            display_response(response)  # Display response
        except sr.UnknownValueError:
            response = "Sorry, I did not understand that."
            print(response)
        except sr.RequestError:
            response = "Could not request results from Google."
            print(response)

# Function to process the command
def process_command(command):
    query = command.strip()

    if "joke" in query:
        return tell_joke()
    elif "open" in query:
        app_name = query.split("open")[-1].strip()
        return open_application(app_name)
    elif "search for" in query:
        search_term = query.split("search for")[-1].strip()
        webbrowser.open(f"https://www.google.com/search?q={search_term}")
        return f"Searching for {search_term}..."
    elif "time" in query or "date" in query:
        return tell_time_date()
    elif "hello" in query:
        return "Hello! How can I assist you today?"
    elif "my name is" in query:
        name = query.split("my name is")[-1].strip()
        return f"Nice to meet you, {name}!"
    elif "what is your name" in query:
        return "I am your voice assistant."
    else:
        return google_search(query)  # Default to Google search

# Function to tell the current date and time
def tell_time_date():
    now = datetime.datetime.now()
    return f"The current date and time is: {now.strftime('%Y-%m-%d %H:%M:%S')}"

# Function to handle text input from the text box
def handle_text_query():
    if not is_speech_mode:
        query = input_box.get("1.0", tk.END).strip()
        if query:
            response = process_command(query)
            display_response(response)

# Function to display the response in the text area and speak if toggled
def display_response(response):
    response_text.delete(1.0, tk.END)
    condensed_response = condense_response(response)
    response_text.insert(tk.END, condensed_response)
    if is_response_mode_speech:
        speak(condensed_response)

# Function to condense the response text
def condense_response(text):
    condensed = ' '.join(text.split()[:50])
    return condensed + '...'

# Function to toggle input mode between speech and text
def toggle_input_mode():
    global is_speech_mode
    is_speech_mode = not is_speech_mode
    if is_speech_mode:
        mode_button.config(text="Switch to Text Input Mode")
        input_box.config(state=tk.DISABLED)
        listen_button.config(state=tk.NORMAL)
    else:
        mode_button.config(text="Switch to Speech Input Mode")
        input_box.config(state=tk.NORMAL)
        listen_button.config(state=tk.DISABLED)

# Function to toggle response mode between text and speech
def toggle_response_mode():
    global is_response_mode_speech
    is_response_mode_speech = not is_response_mode_speech
    if is_response_mode_speech:
        response_mode_button.config(text="Switch to Speech Response")
    else:
        response_mode_button.config(text="Switch to Text Response")

# Function to generate Google search page for the query
def open_google_search_page():
    query = input_box.get("1.0", tk.END).strip()
    if query:
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)

# Function to exit the application
def exit_application():
    root.destroy()

# Create the GUI
root = tk.Tk()
root.title("Voice Assistant")
root.geometry("800x600")

# Define colors for the application
bg_color = "#f8f9fa"  # Light gray background for the main area
sidebar_color = "#343a40"  # Dark gray for the sidebar
content_color = "#1c1c1c"  # Lighter black for the main content area (search and response)
icon_color = "#6c757d"  # Color for buttons

# Set the background color for the main area
root.configure(bg=bg_color)

# Frame for sidebar
sidebar = tk.Frame(root, width=200, bg=sidebar_color)
sidebar.pack(side=tk.LEFT, fill=tk.Y)

# Exit button in sidebar (width set to 25)
exit_button = tk.Button(sidebar, text="Exit", command=exit_application, width=25, bg=icon_color, fg="white")
exit_button.pack(pady=5, padx=10)

# Frame for sidebar buttons
sidebar_button_frame = tk.Frame(sidebar, bg=sidebar_color)
sidebar_button_frame.pack(pady=5)

# Main content area frame
main_content_frame = tk.Frame(root, bg=content_color)
main_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Input box for user query
input_box = tk.Text(main_content_frame, height=2, width=50, bg="#2c2c2c", fg="white")  # Darker gray for input box
input_box.pack(pady=10, padx=10)

# Button frame for Listen and Search buttons
button_frame = tk.Frame(main_content_frame, bg=content_color)
button_frame.pack(pady=5)

# Listen button
listen_button = tk.Button(button_frame, text="Listen", command=recognize_speech, width=10, bg=icon_color, fg="white")
listen_button.pack(side=tk.LEFT, padx=5)

# Search button
search_button = tk.Button(button_frame, text="Search", command=open_google_search_page, width=10, bg=icon_color, fg="white")
search_button.pack(side=tk.LEFT, padx=5)

# Toggle buttons for modes
mode_button = tk.Button(sidebar_button_frame, text="Switch to Text Input Mode", command=toggle_input_mode, width=25, bg=icon_color, fg="white")
mode_button.pack(pady=5, padx=10)

response_mode_button = tk.Button(sidebar_button_frame, text="Switch to Speech Response", command=toggle_response_mode, width=25, bg=icon_color, fg="white")
response_mode_button.pack(pady=5, padx=10)

# Response area
response_text = tk.Text(main_content_frame, height=15, width=70, wrap=tk.WORD, bg="#2c2c2c", fg="white")  # Darker gray for response area
response_text.pack(pady=10, padx=10)

# Start the GUI main loop
root.mainloop()
