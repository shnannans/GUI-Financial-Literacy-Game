#import libraries
import tkinter as tk
from tkinter import ttk, messagebox
import random
import pygame
import matplotlib.pyplot as plt
import os
import csv
from datetime import datetime
import json


# initialize pygame mixer for sounds
pygame.mixer.init()

# attributes to sound files
# Game background Music loop short by yummie -- https://freesound.org/s/410574/ -- License: Attribution 4.0
# correct.wav by StavSounds -- https://freesound.org/s/546084/ -- License: Creative Commons 0
# Dat's Wrong! by Beetlemuse -- https://freesound.org/s/587253/ -- License: Attribution 4.0
# quick woosh by florianreichelt -- https://freesound.org/s/683101/ -- License: Creative Commons 0
# Item Sparkle by Mr._Fritz_ -- https://freesound.org/s/545238/ -- License: Creative Commons 0
# Tap Notification by lucadialessandro -- https://pixabay.com/sound-effects/tap-notification-180637/ -- pixabay content licensed
# Button by Universefield -- https://pixabay.com/sound-effects/button-124476/ -- pixabay content licensed
# Thinking Time -- https://pixabay.com/music/build-up-scenes-thinking-time-148496/ -- pixabay content licensed

class QuizGame:
    # set all variables to be initialized
    def __init__(self, root):
        self.root = root
        self.root.title("🎉 Financial Friend Quiz! 🎉")
        self.root.geometry("1000x600+200+50")   # Increased window size
        self.root.resizable(True, True)        # Allow window to be resizable
        self.root.config(bg="#f0f8ff")

        self.username = ""
        self.money = 10
        self.points_possible = 1000  # Define points possible per question
        self.current_question = 0
        self.difficulty = "Rookie Earners"  # Default difficulty level (display name)
        self.difficulty_mapping = {
            "Rookie Earners": "Beginner",
            "Savings Strikers": "Intermediate",
            "Wealth Champions": "Advanced",
            "All-Star Challenge": "Master"
        }

        # Reverse mapping for display purposes
        self.internal_to_display = {v: k for k, v in self.difficulty_mapping.items()}

        # Initialize game points
        self.game_points = 0
        self.highest_game_points = {}

        # Initialize settings_window attribute
        self.settings_window = None

        # Setting up for spending visualization
        self.spending_categories = {"Quiz Earnings": 0, "Quiz Losses": 0, "Random Events": 0}

        # Timer tracking
        self.timer_label = None
        self.time_left = 30  # Default time for each question

        # Sound settings
        self.background_music_volume = 0.2
        self.sound_effects_on = True
        self.master_sound_volume = 1.0  # Initialize master sound volume

        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Initialize paths
        self.bg_music_path = os.path.join(self.script_dir, 'audio_files', 'background_music.mp3')
        self.correct_sound_path = os.path.join(self.script_dir, 'audio_files', 'correct.wav')
        self.wrong_sound_path = os.path.join(self.script_dir, 'audio_files', 'wrong.wav')
        self.random_accept_path = os.path.join(self.script_dir, 'audio_files', 'random_accept.wav')
        self.random_decline_path = os.path.join(self.script_dir, 'audio_files', 'random_decline.mp3')
        self.btn_click_path = os.path.join(self.script_dir, 'audio_files', 'button_click.mp3')
        self.radio_btn_path = os.path.join(self.script_dir, 'audio_files', 'radio_button_click.mp3')
        self.quiz_thinktime_path = os.path.join(self.script_dir, 'audio_files', 'quiz_thinktime.mp3')

        # Paths to quiz and random event scenario questions
        self.quiz_data_path = os.path.join(self.script_dir, 'in_game_files',  'quiz_data.csv')
        self.random_scenario_path = os.path.join(self.script_dir, 'in_game_files', 'random_scenario.csv')

        # Initialize data structures
        self.quiz_data = {
            "Beginner": [],
            "Intermediate": [],
            "Advanced": []
        }

        self.random_events = {
            "Beginner": [],
            "Intermediate": [],
            "Advanced": []
        }

        # Load quiz data and random events from CSV files
        self.load_quiz_data()
        self.load_random_events()

        # Initialize leaderboard storage
        self.leaderboard = []
        self.leaderboard_path = os.path.join(self.script_dir, 'user_&leaderboard_files',  'leaderboard.csv')
        self.initialize_leaderboard()

        # Path to the centralized user data JSON file
        self.user_data_path = os.path.join(self.script_dir, 'user_&leaderboard_files', 'quiz_user_data.json')
        self.initialize_user_data()

        # attribute to store username
        self.stored_username = None 

        # Initialize hint_used to False
        self.hint_used = False 

        # Initialize wrong answers counter
        self.wrong_answers = 0  

        # Initialize background music state
        self.background_music_on = True  # Music is enabled by default
        self.background_music_var = tk.BooleanVar(value=self.background_music_on)

        # Load Prohibited Words from External File
        self.prohibited_words = self.load_prohibited_words("prohibited_words.txt")

        # Define the protocol handler for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Initialize Pygame Mixer for sounds
        pygame.mixer.init()

        # Load background music
        self.load_background_music()

        # Load sound effects
        self.load_sound_effects()

        self.inventory = []
        self.equipped_items = {"hat": None, "accessory": None, "outfit": None, "shoes": None}

        # Initialize the my_profile_button attribute
        self.my_profile_button = None

        self.show_home_page()

    # load in all difficulty quiz questions from quiz_data.csv
    def load_quiz_data(self):
        """Load quiz data from the CSV file into self.quiz_data."""
        encodings_to_try = ['utf-8', 'cp1252']
        for enc in encodings_to_try:
            try:
                with open(self.quiz_data_path, mode='r', newline='', encoding=enc) as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        difficulty = row['difficulty'].strip().title()
                        question = row['question'].strip()
                        options = [opt.strip() for opt in row['options'].split(';')]
                        answer = row['answer'].strip()
                        explanation = row['explanation'].strip()

                        question_data = {
                            "question": question,
                            "options": options,
                            "answer": answer,
                            "explanation": explanation
                        }

                        # Dynamically add new difficulty levels if they don't exist
                        if difficulty not in self.quiz_data:
                            self.quiz_data[difficulty] = []
                            self.random_events[difficulty] = []  # Ensure corresponding random events are initialized

                        self.quiz_data[difficulty].append(question_data)
                print(f"Quiz data loaded successfully with encoding {enc}.")
                break  # Exit the loop if successful
            except UnicodeDecodeError as e:
                print(f"Unicode decode error with {enc}: {e}. Trying next encoding.")
                continue  # Try the next encoding
            except FileNotFoundError:
                print(f"File not found: {self.quiz_data_path}")
                messagebox.showerror("File Not Found", f"Could not find {self.quiz_data_path}. Please ensure the file exists.")
                return
            except Exception as e:
                print(f"An error occurred while loading quiz data with {enc} encoding: {e}")
                messagebox.showerror("Error", f"An error occurred while loading quiz data with {enc} encoding: {e}")
                return
        else:
            # If all encodings fail
            messagebox.showerror("Encoding Error", f"Failed to decode {self.quiz_data_path} with tried encodings.")

    # load in random event scenario questions from random_scenario.csv 
    def load_random_events(self):
        """Load random events from the CSV file into self.random_events."""
        encodings_to_try = ['utf-8', 'cp1252']
        for enc in encodings_to_try:
            try:
                with open(self.random_scenario_path, mode='r', newline='', encoding=enc) as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        difficulty = row['difficulty'].strip().title()
                        event_text = row['event'].strip()
                        try:
                            score_change = int(row['scoreIncrease'].strip())
                        except ValueError:
                            print(f"Invalid scoreIncrease value in random_scenario.csv: {row['scoreIncrease']}")
                            continue  # Skip this row

                        event = (event_text, score_change)

                        # Dynamically add new difficulty levels if they don't exist
                        if difficulty not in self.random_events:
                            self.random_events[difficulty] = []
                        self.random_events[difficulty].append(event)
                print(f"Random events loaded successfully with encoding {enc}.")
                break  # Exit the loop if successful
            except UnicodeDecodeError as e:
                print(f"Unicode decode error with {enc}: {e}. Trying next encoding.")
                continue  # Try the next encoding
            except FileNotFoundError:
                print(f"File not found: {self.random_scenario_path}")
                messagebox.showerror("File Not Found", f"Could not find {self.random_scenario_path}. Please ensure the file exists.")
                return
            except Exception as e:
                print(f"An error occurred while loading random events with {enc} encoding: {e}")
                messagebox.showerror("Error", f"An error occurred while loading random events with {enc} encoding: {e}")
                return
        else:
            # If all encodings fail
            messagebox.showerror("Encoding Error", f"Failed to decode {self.random_scenario_path} with tried encodings.")

    # load in upbeat background music
    def load_background_music(self):
        """Load and play background music."""
        try:
            print(f"Background music path: {self.bg_music_path}")
            pygame.mixer.music.load(self.bg_music_path)
            pygame.mixer.music.set_volume(self.background_music_volume)
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except pygame.error as e:
            print(f"Failed to load background music: {e}")
            messagebox.showerror("Audio Error", f"Failed to load background music: {e}")

    # load in various sound effects
    def load_sound_effects(self):
        """Load all sound effects."""
        try:
            print(f"Correct sound path: {self.correct_sound_path}")
            self.correct_sound = pygame.mixer.Sound(self.correct_sound_path)
            print(f"Wrong sound path: {self.wrong_sound_path}")
            self.wrong_sound = pygame.mixer.Sound(self.wrong_sound_path)
            self.correct_sound.set_volume(0.3)
            self.wrong_sound.set_volume(0.3)
        except pygame.error as e: 
            print(f"Failed to load correct or wrong sound effects: {e}")
            messagebox.showerror("Audio Error", f"Failed to load correct or wrong sound effects: {e}")

        try:
            # Load accept and decline sound effects
            self.random_accept_sound = pygame.mixer.Sound(self.random_accept_path)
            self.random_decline_sound = pygame.mixer.Sound(self.random_decline_path)
            # Load button click sound effect
            self.button_click_sound = pygame.mixer.Sound(self.btn_click_path)
            # Load radio button click sound effect
            self.radio_button_click_sound = pygame.mixer.Sound(self.radio_btn_path)

            # Set volume levels if needed
            self.random_accept_sound.set_volume(0.3)
            self.random_decline_sound.set_volume(0.3)
            self.button_click_sound.set_volume(0.3)
            self.radio_button_click_sound.set_volume(0.3) 
        except pygame.error as e:
            print(f"Failed to load additional sound effects: {e}")
            messagebox.showerror("Audio Error", f"Failed to load additional sound effects: {e}")
        
        try:
            # Quiz thinking sound effects
            self.quiz_thinktime_sound = pygame.mixer.Sound(self.quiz_thinktime_path)
            self.quiz_thinktime_sound.set_volume(0.02)  # Adjust volume as needed
            print(f"Quiz think time sound loaded from {self.quiz_thinktime_path}")
        except pygame.error as e:
            print(f"Failed to load quiz think time sound: {e}")
            messagebox.showerror("Audio Error", f"Failed to load quiz think time sound: {e}")

    # active specific sound effect for radio button only
    def play_radio_button_sound(self):
        """Play the radio button click sound effect."""
        if self.sound_effects_on:
            self.radio_button_click_sound.play()

        # initialize leaderboard file with headers
   
    # initialize the leaderboard.csv file with headers 
    def initialize_leaderboard(self):
        """Initialize the leaderboard.csv file with headers if it doesn't exist or update headers if missing."""
        headers = ['Datetime Captured', 'Username', 'Game Points', 'Difficulty Level', 'Current Rank']
        
        if not os.path.exists(self.leaderboard_path):
            try:
                with open(self.leaderboard_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)
                print("leaderboard.csv created with headers.")
            except Exception as e:
                print(f"An error occurred while initializing the leaderboard: {e}")
                messagebox.showerror("Error", f"Failed to initialize leaderboard: {e}")
        else:
            # Check if headers are present and correct
            try:
                with open(self.leaderboard_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    existing_headers = next(reader, None)
                
                if existing_headers != headers:
                    # Backup the existing leaderboard
                    backup_path = self.leaderboard_path + ".backup"
                    os.rename(self.leaderboard_path, backup_path)
                    print(f"Existing leaderboard headers are incorrect. Backup created at {backup_path}. Creating new leaderboard with correct headers.")
                    
                    # Create a new leaderboard with correct headers
                    with open(self.leaderboard_path, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(headers)
            except Exception as e:
                print(f"An error occurred while checking/updating the leaderboard headers: {e}")
                messagebox.showerror("Error", f"Failed to verify/update leaderboard headers: {e}")

    # initialize user data json file
    def initialize_user_data(self):
        """Initialize the centralized user data JSON file if it doesn't exist."""
        if not os.path.exists(self.user_data_path):
            try:
                with open(self.user_data_path, 'w', encoding='utf-8') as file:
                    json.dump({}, file, indent=4)
                print("quiz_user_data.json created as it did not exist.")
            except Exception as e:
                print(f"An error occurred while initializing user data: {e}")
                messagebox.showerror("Initialization Error", "Failed to initialize user data.")

    # load the player's data from the centralized JSON file
    def load_user_data(self):
        """Load the player's data from the centralized JSON file."""
        try:
            if os.path.exists(self.user_data_path):
                with open(self.user_data_path, 'r', encoding='utf-8') as file:
                    all_users_data = json.load(file)
            else:
                all_users_data = {}
            
            # Get user data or initialize if not present
            user_data = all_users_data.get(self.username, {})
            
            # Load data into class attributes
            self.inventory = user_data.get("inventory", [])
            self.equipped_items = user_data.get("equipped_items", {"hat": None, "accessory": None, "outfit": None, "shoes": None})
            self.money = user_data.get("money", 10)
            self.game_points = user_data.get("game_points", 0)
            self.last_played = user_data.get("last_played", "Never")
            self.highest_game_points = user_data.get("highest_game_points", {})
            
            print(f"Data loaded for user '{self.username}'.")
        except Exception as e:
            print(f"Failed to load user data: {e}")
            messagebox.showerror("Load Error", "Failed to load your data.")

    # save the player's data to the centralized JSON file
    def save_user_data(self, check_high_score=True):
        """Save the player's data to the centralized JSON file."""
        try:
            # Load existing data
            if os.path.exists(self.user_data_path):
                with open(self.user_data_path, 'r', encoding='utf-8') as file:
                    all_users_data = json.load(file)
            else:
                all_users_data = {}
            
            # Get user data or initialize if not present
            user_data = all_users_data.get(self.username, {})
            
            # Initialize highest_game_points as a dict if not present
            if 'highest_game_points' not in user_data or not isinstance(user_data['highest_game_points'], dict):
                user_data['highest_game_points'] = {}
            
            # Map the current difficulty to internal key
            internal_difficulty = self.difficulty_mapping.get(self.difficulty, self.difficulty)
            
            # Update highest_game_points for the current difficulty if required
            if check_high_score:
                current_high_score = user_data['highest_game_points'].get(internal_difficulty, 0)
                if self.game_points > current_high_score:
                    user_data['highest_game_points'][internal_difficulty] = self.game_points
                    messagebox.showinfo(
                        "New High Score!", 
                        f"Congratulations! You've achieved a new high score of {self.game_points} 🎯 Game Points for {self.difficulty} difficulty!"
                    )
            
            # Update other user data
            user_data.update({
                "inventory": self.inventory,
                "equipped_items": self.equipped_items,
                "money": self.money,
                "game_points": self.game_points,
                "last_played": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "highest_game_points": user_data['highest_game_points']
            })
            
            # Save back to the JSON
            all_users_data[self.username] = user_data
            
            with open(self.user_data_path, 'w', encoding='utf-8') as file:
                json.dump(all_users_data, file, indent=4)
            
            print(f"Data saved for user '{self.username}' to {self.user_data_path}")
        except Exception as e:
            print(f"Failed to save user data: {e}")
            messagebox.showerror("Save Error", "Failed to save your data.")

    # allow users to delete their data
    def delete_user_data(self):
        """Delete the current user's data from the centralized JSON file and remove from leaderboard."""
        try:
            # -------------------------
            # Step 1: Delete User Data from JSON
            # -------------------------
            with open(self.user_data_path, 'r', encoding='utf-8') as file:
                all_users_data = json.load(file)
            
            if self.username in all_users_data:
                del all_users_data[self.username]
                with open(self.user_data_path, 'w', encoding='utf-8') as file:
                    json.dump(all_users_data, file, indent=4)
                messagebox.showinfo("Success", "Your profile has been deleted successfully.")
                print(f"User '{self.username}' has been deleted from {self.user_data_path}.")

                # -------------------------
                # Step 2: Remove User from Leaderboard
                # -------------------------
                if os.path.exists(self.leaderboard_path):
                    try:
                        with open(self.leaderboard_path, mode='r', newline='', encoding='utf-8') as file:
                            reader = csv.DictReader(file)
                            # Filter out entries where Username matches the deleted user
                            updated_leaderboard = [
                                row for row in reader if row['Username'] != self.username
                            ]
                        
                        # Check if there are any entries left after deletion
                        if not updated_leaderboard:
                            # If leaderboard is empty, recreate it with headers
                            headers = ['Datetime Captured', 'Username', 'Game Points', 'Difficulty Level', 'Current Rank']
                            with open(self.leaderboard_path, mode='w', newline='', encoding='utf-8') as file:
                                writer = csv.DictWriter(file, fieldnames=headers)
                                writer.writeheader()
                            print("Leaderboard is now empty and has been reset with headers.")
                        else:
                            # Sort the updated leaderboard by Game Points in descending order
                            updated_leaderboard.sort(key=lambda x: int(x['Game Points']), reverse=True)
                        
                            # Reassign ranks based on sorted Game Points
                            for idx, entry in enumerate(updated_leaderboard, start=1):
                                entry['Current Rank'] = idx
                    
                            # Write the updated leaderboard back to the CSV
                            headers = ['Datetime Captured', 'Username', 'Game Points', 'Difficulty Level', 'Current Rank']
                            with open(self.leaderboard_path, mode='w', newline='', encoding='utf-8') as file:
                                writer = csv.DictWriter(file, fieldnames=headers)
                                writer.writeheader()
                                writer.writerows(updated_leaderboard)
                            print(f"User '{self.username}' has been removed from the leaderboard.")
                    except Exception as e:
                        print(f"An error occurred while updating the leaderboard: {e}")
                        messagebox.showerror("Error", "Failed to update the leaderboard.")
                else:
                    print(f"Leaderboard file '{self.leaderboard_path}' does not exist. No leaderboard entries to remove.")
            
                # -------------------------
                # Step 3: Reset User Attributes and Update UI
                # -------------------------
                self.username = ""  # Clear the username
                self.stored_username = None  # Clear stored username
                self.inventory = []  # Clear inventory
                self.equipped_items = {"hat": None, "accessory": None, "outfit": None, "shoes": None}  # Reset equipped items
                self.money = 10  # Reset money to default
                self.game_points = 0  # Reset game points
                self.highest_game_points = {}  # Reset highest game points
                self.show_home_page()  # Navigate back to home page
            else:
                messagebox.showwarning("Not Found", "No data found for your username.")
                print(f"No data found for username '{self.username}' during deletion.")
        except Exception as e:
            print(f"Failed to delete user data: {e}")
            messagebox.showerror("Error", "Failed to delete your profile.")

    # prompt the user to confirm profile deletion
    def confirm_delete_profile(self, profile_window):
        """Prompt the user to confirm profile deletion."""
        confirmation = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete your profile? This action cannot be undone."
        )
        if confirmation:
            # Call the delete_user_data method
            self.delete_user_data()
            # Close the profile window
            profile_window.destroy()
        else:
            # User canceled the deletion
            messagebox.showinfo("Cancellation", "Profile deletion has been canceled.")

    # loading in prohibited words from text file
    def load_prohibited_words(self, filepath):
        """Load prohibited words from a text file."""
        encodings_to_try = ['utf-8', 'cp1252']
        for enc in encodings_to_try:
            try:
                with open(os.path.join(self.script_dir, filepath), 'r', encoding=enc) as file:
                    words = [line.strip().lower() for line in file if line.strip()]
                print(f"Loaded {len(words)} prohibited words with encoding {enc}.")
                return words
            except UnicodeDecodeError as e:
                print(f"Unicode decode error with {enc}: {e}. Trying next encoding.")
                continue  # Try the next encoding
            except FileNotFoundError:
                print(f"Prohibited words file '{filepath}' not found. No words will be prohibited.")
                return []
            except Exception as e:
                print(f"An error occurred while loading prohibited words with {enc} encoding: {e}")
                messagebox.showerror("Error", f"An error occurred while loading prohibited words with {enc} encoding: {e}")
                return []
        else:
            # If all encodings fail
            messagebox.showerror("Encoding Error", f"Failed to decode {filepath} with tried encodings.")
            return []

    # check if username contains prohibited words    
    def is_username_valid(self, username):
        """Check if the username is valid: contains no prohibited words and meets length requirements."""
        if not (3 <= len(username) <= 20):
            return False
        username_lower = username.lower()
        for word in self.prohibited_words:
            if word in username_lower:
                return False
        return True

    # create general buttons
    def create_button(self, text, command, parent=None, width=None, height=3, font_size=14, wraplength=300, justify='center'):
        """Create a styled button with sound effects."""
        if parent is None:
            parent = self.root

        # Handle text wrapping
        max_chars_per_line = 25  # Adjust as needed
        if len(text) > max_chars_per_line:
            words = text.split()
            wrapped_text = ""
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > max_chars_per_line:
                    wrapped_text += line + "\n"
                    line = word
                else:
                    if line:
                        line += " " + word
                    else:
                        line = word
            wrapped_text += line
        else:
            wrapped_text = text

        # Play button click sound when clicked
        def play_sound_and_execute():
            if self.sound_effects_on:
                self.button_click_sound.play()  # Play click sound
            command()

        return tk.Button(
            parent,
            text=wrapped_text,
            command=play_sound_and_execute,  # Wrap the command with sound effect
            font=("Comic Sans MS", font_size),
            bg="#ff4500",
            fg="#f0f8ff",
            pady=5,
            width=width if width is not None else 25,  # Use provided width or default
            height=height,
            wraplength=wraplength,
            justify=justify
        )

    # display the settings window where users can adjust sound preferences
    def show_settings(self):
        """Display the settings window where users can adjust sound preferences."""
        # Check if the settings window is already open
        if self.settings_window and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.lift()  # Bring the existing window to the front
            return
        
        # Create a new settings window if it doesn't exist
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("450x500")  # Increased height to accommodate new slider
        self.settings_window.config(bg="#f0f8ff")
        
        # Handle the closing of the settings window properly
        self.settings_window.protocol("WM_DELETE_WINDOW", self.on_close_settings)
        
        # Volume bar for background music
        music_volume_label = tk.Label(
            self.settings_window, 
            text="Music Volume", 
            font=("Comic Sans MS", 16), 
            bg="#f0f8ff", 
            fg="#ff4500"
        )
        music_volume_label.pack(pady=(20, 5))
        
        music_volume_slider = ttk.Scale(
            self.settings_window, 
            from_=0, 
            to=1, 
            orient='horizontal', 
            length=300, 
            command=self.adjust_music_volume
        )
        music_volume_slider.set(self.background_music_volume)  # Set slider to current volume
        music_volume_slider.pack(pady=(0, 20))
        
        # Toggle button for background music
        background_music_checkbox = tk.Checkbutton(
            self.settings_window, 
            text="Enable Background Music", 
            font=("Comic Sans MS", 16), 
            variable=self.background_music_var, 
            bg="#f0f8ff", 
            fg="#ff4500", 
            command=self.toggle_background_music
        )
        background_music_checkbox.pack(pady=(0, 20))
        
        # Sound effects volume slider
        sound_effects_volume_label = tk.Label(
            self.settings_window, 
            text="Sound Effects Volume", 
            font=("Comic Sans MS", 16), 
            bg="#f0f8ff", 
            fg="#ff4500"
        )
        sound_effects_volume_label.pack(pady=(0, 5))
        
        sound_effects_volume_slider = ttk.Scale(
            self.settings_window, 
            from_=0, 
            to=1, 
            orient='horizontal', 
            length=300, 
            command=self.adjust_sound_effects_volume
        )
        sound_effects_volume_slider.set(self.master_sound_volume)  # Set slider to current master volume
        sound_effects_volume_slider.pack(pady=(0, 20))
        
        # Sound effects checkbox
        self.sound_effects_var = tk.BooleanVar(value=self.sound_effects_on)
        sound_effects_checkbox = tk.Checkbutton(
            self.settings_window, 
            text="Enable Sound Effects", 
            font=("Comic Sans MS", 16), 
            variable=self.sound_effects_var, 
            bg="#f0f8ff", 
            fg="#ff4500", 
            command=self.toggle_sound_effects
        )
        sound_effects_checkbox.pack(pady=(0, 20))
        
        # Close Button
        close_button = self.create_button(
            text="Close", 
            command=self.on_close_settings,  # Use on_close_settings method
            parent=self.settings_window, 
            width=15, 
            height=2
        )
        close_button.pack(pady=10)
        
        # Optionally, prevent resizing
        self.settings_window.resizable(False, False)

    def adjust_sound_effects_volume(self, volume):
        """Adjust the master volume for sound effects."""
        try:
            new_volume = float(volume)
            self.master_sound_volume = new_volume
            # Assuming all sound effects have a base volume of 0.3
            base_volume = 0.3
            self.correct_sound.set_volume(base_volume * self.master_sound_volume)
            self.wrong_sound.set_volume(base_volume * self.master_sound_volume)
            self.random_accept_sound.set_volume(base_volume * self.master_sound_volume)
            self.random_decline_sound.set_volume(base_volume * self.master_sound_volume)
            self.button_click_sound.set_volume(base_volume * self.master_sound_volume)
            self.radio_button_click_sound.set_volume(base_volume * self.master_sound_volume)
            print(f"Sound effects master volume set to {self.master_sound_volume}")
        except ValueError:
            print("Invalid volume value received.")

    # adjust the background music volume
    def adjust_music_volume(self, volume):
        """Adjust the background music volume."""
        self.background_music_volume = float(volume)
        pygame.mixer.music.set_volume(self.background_music_volume)
        print(f"Background music volume set to {self.background_music_volume}")

    # handles the cleanup when the settings window is closed
    def on_close_settings(self):
        """Handles the cleanup when the settings window is closed."""
        if self.settings_window and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.destroy()  # Destroy the window first
            self.settings_window = None    # Then reset the attribute
    
    # toggle sound effects
    def toggle_sound_effects(self):
        """Enable or disable sound effects."""
        self.sound_effects_on = self.sound_effects_var.get()
        print(f"Sound effects {'enabled' if self.sound_effects_on else 'disabled'}.")

    # toggle background music
    def toggle_background_music(self):
        """Enable or disable background music based on the checkbox."""
        if self.background_music_var.get():
            # Enable background music
            pygame.mixer.music.unpause()
            self.background_music_on = True
            print("Background music enabled.")
        else:
            # Disable background music
            pygame.mixer.music.pause()
            self.background_music_on = False
            print("Background music disabled.")

    # show home page
    def show_home_page(self):
        self.clear_screen()
        self.root.config(bg="#f0f8ff")

        # Create a container frame to hold the canvas and scrollbar
        container_frame = tk.Frame(self.root, bg="#f0f8ff")
        container_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas widget for scrolling
        self.canvas = tk.Canvas(container_frame, bg="#f0f8ff", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a vertical scrollbar linked to the canvas
        scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a frame inside the canvas for all content
        scrollable_frame = tk.Frame(self.canvas, bg="#f0f8ff")

        # Add the frame to a window in the canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Update scrollregion when the size of the scrollable_frame changes
        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Bind the canvas's <Configure> event to adjust the scrollable_frame's width
        def on_canvas_configure(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        self.canvas.bind("<Configure>", on_canvas_configure)

        # Title Label (centered)
        title_label = tk.Label(
            scrollable_frame,
            text="🎉 Finance Friends Quiz 🎉",
            font=("Comic Sans MS", 24),
            bg="#f0f8ff",
            fg="#ff4500",
            wraplength=800  # Adjusted wraplength for wider window
        )
        title_label.pack(pady=20)

        # Username Label and Entry (always present)
        username_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")
        username_frame.pack(pady=10)
        username_label = tk.Label(
            username_frame,
            text="What's your name?",
            font=("Comic Sans MS", 16),
            bg="#f0f8ff",
            fg="#ff4500"
        )
        username_label.pack(side="left", padx=5)
        self.username_entry = tk.Entry(username_frame, font=("Comic Sans MS", 16), width=20)

        # Pre-fill the username entry if stored_username exists
        self.username_entry.delete(0, tk.END)  # Clear any existing text
        if self.stored_username:
            self.username_entry.insert(0, self.stored_username)

        self.username_entry.pack(side="left", padx=5)

        # Difficulty selection (centered)
        difficulty_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")
        difficulty_frame.pack(pady=10)
        difficulty_label = tk.Label(
            difficulty_frame,
            text="Select Difficulty Level:",
            font=("Comic Sans MS", 16),
            bg="#f0f8ff",
            fg="#ff4500"
        )
        difficulty_label.pack(side="left", padx=5)

        self.difficulty_var = tk.StringVar(value="Rookie Earners")

        # Difficulty descriptions
        difficulty_descriptions = {
            "Rookie Earners": "Level 1: Rookies learning the basics of earning and saving.",
            "Savings Strikers": "Level 2: Players striking out expenses and scoring savings goals.",
            "Wealth Champions": "Level 3: Champions in managing and growing wealth.",
            "All-Star Challenge": "Level 4: Join the all-stars and tackle advanced financial challenges."
        }

        # Function to update the description label
        def update_description(*args):
            selected_difficulty = self.difficulty_var.get()
            description = difficulty_descriptions.get(selected_difficulty, "")
            description_label.config(text=description)

        self.difficulty_var.trace('w', update_description)

        # Create difficulty radio buttons (centered)
        button_row = tk.Frame(difficulty_frame, bg="#f0f8ff")
        button_row.pack(pady=5)
        difficulties = ["Rookie Earners", "Savings Strikers", "Wealth Champions", "All-Star Challenge"]
        for difficulty in difficulties:
            radio = tk.Radiobutton(
                button_row,
                text=difficulty,
                variable=self.difficulty_var,
                value=difficulty,
                font=("Comic Sans MS", 16),
                bg="#f0f8ff",
                fg="#ff4500",
                indicatoron=0,
                width=15,  # Increased width for better fitting
                pady=5,
                command=self.play_radio_button_sound  # Add command here
            )
            radio.pack(side="left", padx=5)

        # Description Label (below difficulty settings)
        description_label = tk.Label(
            scrollable_frame,
            text=difficulty_descriptions[self.difficulty_var.get()],
            font=("Comic Sans MS", 16),
            bg="#f0f8ff",
            fg="#000000",
            wraplength=800,
            justify="center"
        )
        description_label.pack(pady=10)

        # -------------------------
        # Buttons for additional actions (centered)
        # -------------------------
        self.button_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")  # Changed to instance attribute
        self.button_frame.pack(pady=20, anchor='center')

        # Define buttons including "My Profile" right after "Start Quiz"
        buttons = [
            ("🎮 Start Quiz", self.start_quiz),
            ("👤 My Profile", self.show_my_profile),  # Moved "My Profile" here
            ("👤 Customize Character", self.show_character_customization),
            ("🛒 Open Shop", self.open_shop),
            ("🏆 Show Leaderboard", self.show_leaderboard),
            ("⚙️ Settings", self.show_settings)
        ]

        for text, command in buttons:
            button = self.create_button(
                text=text,
                command=lambda cmd=command: [cmd()],
                parent=self.button_frame,
                width=20,      # Increased width for Home Page buttons
                height=2,      # Increased height for better visibility
                font_size=16,  # Increased font size
                justify='center'
            )
            button.pack(pady=10)
            
            # Assign the "My Profile" button to an instance attribute
            if text == "👤 My Profile":
                self.my_profile_button = button

        # -------------------------
        # Initially disable or enable the "My Profile" button based on user existence
        # -------------------------
        self.update_my_profile_button()

        # Bind mouse wheel to the root window for scrolling
        self.bind_mouse_wheel_home()

        self.center_content()

    # scrolling controls for home page
    def bind_mouse_wheel_home(self):
        """Enable scrolling with the mouse wheel on the canvas."""
        # Windows and macOS scrolling
        self.root.bind_all("<MouseWheel>", self._on_mouse_wheel_home)
        # Linux scrolling
        self.root.bind_all("<Button-4>", self._on_mouse_wheel_home)
        self.root.bind_all("<Button-5>", self._on_mouse_wheel_home)
    
    # scrolling controls for home page
    def _on_mouse_wheel_home(self, event):
        """Scroll the canvas with the mouse wheel."""
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 5:
                self.canvas.yview_scroll(1, "units")  # Scroll down
            elif event.num == 4:
                self.canvas.yview_scroll(-1, "units")  # Scroll up

    # Retrieve all usernames from the centralized user data JSON file
    def get_all_usernames(self):
        """Retrieve all usernames from the centralized JSON file."""
        try:
            with open(self.user_data_path, 'r', encoding='utf-8') as file:
                all_users_data = json.load(file)
            return list(all_users_data.keys())
        except Exception as e:
            print(f"Failed to retrieve usernames: {e}")
            return []

    # Display the user's profile with all detail after logging in
    def show_my_profile(self):
        """Display the user's profile with all details."""
        # Load user data to ensure it's up-to-date
        self.load_user_data()

        # Create a new top-level window
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"{self.username}'s Profile")
        profile_window.geometry("600x600")  # Adjusted height
        profile_window.config(bg="#f0f8ff")

        # Make the window modal
        profile_window.grab_set()

        # Title Label
        profile_title = tk.Label(
            profile_window,
            text="📋 My Profile",
            font=("Comic Sans MS", 24, "bold"),
            bg="#f0f8ff",
            fg="#ff4500"
        )
        profile_title.pack(pady=20)

        # Frame to hold profile details
        details_frame = tk.Frame(profile_window, bg="#f0f8ff")
        details_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Display Money
        money_label = tk.Label(
            details_frame,
            text=f"💰 Money Left: ${self.money}",
            font=("Comic Sans MS", 16),
            bg="#f0f8ff",
            fg="#ff4500",
            anchor="w"
        )
        money_label.pack(fill=tk.X, pady=5)

        # Display Highest Game Scores
        highest_scores = self.highest_game_points or {}
        if highest_scores:
            highest_label = tk.Label(
                details_frame,
                text="🏆 Highest Game Scores:",
                font=("Comic Sans MS", 16, "bold"),
                bg="#f0f8ff",
                fg="#ff4500",
                anchor="w"
            )
            highest_label.pack(fill=tk.X, pady=(10, 5))

            for difficulty, score in highest_scores.items():
                score_label = tk.Label(
                    details_frame,
                    text=f"{difficulty}: {score} 🎯",
                    font=("Comic Sans MS", 14),
                    bg="#f0f8ff",
                    fg="#000000",
                    anchor="w"
                )
                score_label.pack(fill=tk.X, padx=20, pady=2)
        else:
            highest_label = tk.Label(
                details_frame,
                text="🏆 Highest Game Scores: None",
                font=("Comic Sans MS", 16),
                bg="#f0f8ff",
                fg="#ff4500",
                anchor="w"
            )
            highest_label.pack(fill=tk.X, pady=5)

        # Display Purchased Items
        if self.inventory:
            items_label = tk.Label(
                details_frame,
                text="🛒 Purchased Items:",
                font=("Comic Sans MS", 16, "bold"),
                bg="#f0f8ff",
                fg="#ff4500",
                anchor="w"
            )
            items_label.pack(fill=tk.X, pady=(10, 5))

            # Define a new style for the Treeview with smaller font and row height
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Custom.Treeview",
                            font=("Arial", 12),          # Smaller font
                            rowheight=20)                # Smaller row height

            # Configure the heading style
            style.configure("Custom.Treeview.Heading",
                            font=("Comic Sans MS", 14, "bold"))  # Smaller heading font

            # Create a Treeview to display items in categories
            tree = ttk.Treeview(details_frame, columns=("Category", "Item"), show='headings', height=5, style="Custom.Treeview")
            tree.heading("Category", text="Category")
            tree.heading("Item", text="Item Name")
            tree.column("Category", width=100, anchor='center')  # Reduced width
            tree.column("Item", width=200, anchor='w')          # Reduced width

            # Insert items into the Treeview
            for item in self.inventory:
                item_type = self.get_item_type(item)
                tree.insert('', 'end', values=(item_type.capitalize(), item))

            tree.pack(pady=2, fill=tk.BOTH, expand=True)  # Reduced pady

            # Add a scrollbar to the Treeview
            tree_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=tree_scrollbar.set)
            tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,5))  # Added padx

        else:
            items_label = tk.Label(
                details_frame,
                text="🛒 Purchased Items: None",
                font=("Comic Sans MS", 16),
                bg="#f0f8ff",
                fg="#ff4500",
                anchor="w"
            )
            items_label.pack(fill=tk.X, pady=5)

        # Display Last Played Date
        last_played_label = tk.Label(
            details_frame,
            text=f"📅 Last Played: {self.last_played}",
            font=("Comic Sans MS", 14),
            bg="#f0f8ff",
            fg="#000000",
            anchor="w"
        )
        last_played_label.pack(fill=tk.X, pady=10)

        # -------------------------
        # Add Delete Profile Button
        # -------------------------
        delete_button = self.create_button(
            text="🗑 Delete Profile",
            command=lambda: self.confirm_delete_profile(profile_window),
            parent=details_frame,
            width=15,
            height=2,
            font_size=14
        )
        delete_button.pack(pady=10)

        # Close Button
        close_button = self.create_button(
            text="Close",
            command=profile_window.destroy,
            parent=details_frame,
            width=15,
            height=2,
            font_size=14
        )
        close_button.pack(pady=10)

        self.center_window(profile_window)

    # Enable or disable the 'My Profile' button based on user existence
    def update_my_profile_button(self):
        """Enable or disable the 'My Profile' button based on user existence."""
        if hasattr(self, 'my_profile_button') and self.my_profile_button and self.my_profile_button.winfo_exists():
            if self.username and self.username in self.get_all_usernames():
                self.my_profile_button.config(state=tk.NORMAL)
            else:
                self.my_profile_button.config(state=tk.DISABLED)
        else:
            # Optionally, handle cases where the button does not exist
            print("My Profile button does not exist on the current screen.")

    def get_item_type(self, item_name):
        """Retrieve the type of the item based on its name."""
        all_shop_items = self.get_all_shop_items()
        for item in all_shop_items:
            if item["name"] == item_name:
                return item["type"]
        return "unknown"

    # initialize challenge mode (adding all difficulty levels and randomizing 10)
    def start_challenge_mode(self):
        """Initialize the quiz with a randomized set of 10 questions from all difficulty levels."""
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showwarning("Input Error", "Please enter a name!")
            return

        self.money = 50  # Reset money to initial amount
        self.current_question = 0
        self.correct_streak = 0  # Reset streak
        self.difficulty = "All-Star Challenge"  # Set difficulty mode to Challenge
        print(f"Starting All-Star Challenge Mode for user '{self.username}'.")

        # Combine all questions from all difficulty levels
        all_questions = []
        for difficulty, questions in self.quiz_data.items():
            all_questions.extend(questions)
        print(f"Total questions available for All-Star Challenge: {len(all_questions)}")

        if not all_questions:
            messagebox.showerror("Error", "No questions available for All-Star Challenge.")
            return

        random.shuffle(all_questions)  # Shuffle all questions to randomize

        # Select only 10 random questions for the challenge mode
        self.questions = random.sample(all_questions, min(10, len(all_questions)))  # Select 10 unique random questions or less if not enough
        print(f"Selected {len(self.questions)} questions for All-Star Challenge.")

        # Combine random events from all difficulty levels
        all_events = []
        for difficulty, events in self.random_events.items():
            all_events.extend(events)
        print(f"Total random events available for All-Star Challenge: {len(all_events)}")

        if not all_events:
            messagebox.showerror("Error", "No random events available for All-Star Challenge.")
            return

        random.shuffle(all_events)
        self.events = all_events

        self.total_questions = len(self.questions)
        self.load_question()

    # start quiz
    def start_quiz(self):
        """Start the quiz based on selected difficulty, handling existing users."""
        # Get username based on user input
        self.username = self.username_entry.get().strip()

        if not self.username:
            messagebox.showwarning("Input Error", "Please enter a name!")
            return

        # Username Validation
        if not self.is_username_valid(self.username):
            messagebox.showerror("Invalid Username", "Your username contains inappropriate language. Please choose a different name.")
            return

        # Retrieve all usernames to ensure uniqueness
        existing_usernames = self.get_all_usernames()

        # Check if username already exists
        if self.username in existing_usernames:
            # Existing user
            response = messagebox.askyesno(
                "Welcome Back!",
                "Welcome back to Finance Friends!\nDo you want to start another quiz? Your current progress will be retained."
            )
            if response:
                # User chooses to start a new quiz without resetting data
                self.load_user_data()
                # Removed self.save_user_data() here to save data only after quiz completion
                messagebox.showinfo("New Quiz Started", "Starting a new quiz while retaining your progress.")
                # Reset necessary attributes for a new quiz
                self.spending_categories = {"Quiz Earnings": 0, "Quiz Losses": 0, "Random Events": 0}
                self.game_points = 0 
                self.current_question = 0
                self.correct_streak = 0  # Reset streak
                self.hint_used = False    # Reset hint_used
                self.wrong_answers = 0    # Reset wrong answers

                # Load questions and events based on selected difficulty
                self.difficulty = self.difficulty_var.get()
                print(f"Selected Difficulty: {self.difficulty}")  # Debugging line

                if self.difficulty == "All-Star Challenge":
                    # Initialize Challenge Mode with 10 random questions
                    self.start_challenge_mode()
                else:
                    # Map difficulty names to internal representations
                    difficulty_key = self.difficulty_mapping.get(self.difficulty, self.difficulty)
                    if difficulty_key not in self.quiz_data or not self.quiz_data[difficulty_key]:
                        messagebox.showerror("Error", f"No questions available for the selected difficulty: {self.difficulty}")
                        return

                    # Load only 10 random questions for the selected difficulty
                    if len(self.quiz_data[difficulty_key]) >= 10:
                        self.questions = random.sample(self.quiz_data[difficulty_key], 10)  # Select 10 unique random questions
                    else:
                        self.questions = self.quiz_data[difficulty_key].copy()  # Use all available questions if less than 10

                    # Load events and shuffle them
                    self.events = self.random_events[difficulty_key].copy()
                    random.shuffle(self.events)

                    self.total_questions = len(self.questions)  # This will now be 10 or less
                    self.load_question()

                # **Pause Background Music Before Starting Quiz Think Time Music**
                if self.background_music_on:
                    pygame.mixer.music.pause()
                    print("Background music paused.")

                # **Start the Quiz Thinking Sound Once Here**
                if self.sound_effects_on:
                    try:
                        self.quiz_thinktime_sound.play(-1)  # Loop the think time sound indefinitely
                        print("Quiz think time sound started playing.")
                    except pygame.error as e:
                        print(f"Failed to play quiz think time sound: {e}")

                # **Enable "My Profile" Button if User Exists**
                self.update_my_profile_button()

            else:
                # User chooses to stay on home screen
                messagebox.showinfo("Continue", "You can continue from your existing data.")
                self.stored_username = self.username  # Retain username in textbox
                self.show_home_page()
                return  # Prevent starting the quiz
        else:
            # New user; proceed normally
            # Ensure the username is unique (redundant as per current logic, but kept for clarity)
            if self.username in existing_usernames:
                messagebox.showerror("Username Exists", "This username is already taken. Please choose a different one.")
                return

            # Proceed with creating a new user
            self.load_user_data()  # This will initialize default data for new user
            # Removed self.save_user_data() here to save data only after quiz completion
            messagebox.showinfo("New Quiz Started", "Starting a new quiz for you!")
            # Reset necessary attributes for a new quiz
            self.spending_categories = {"Quiz Earnings": 0, "Quiz Losses": 0, "Random Events": 0}
            self.game_points = 0 
            self.current_question = 0
            self.correct_streak = 0  # Reset streak
            self.hint_used = False    # Reset hint_used
            self.wrong_answers = 0    # Reset wrong answers

            # Load questions and events based on selected difficulty
            self.difficulty = self.difficulty_var.get()
            print(f"Selected Difficulty: {self.difficulty}")  # Debugging line

            if self.difficulty == "All-Star Challenge":
                # Initialize Challenge Mode with 10 random questions
                self.start_challenge_mode()
            else:
                # Map difficulty names to internal representations
                difficulty_key = self.difficulty_mapping.get(self.difficulty, self.difficulty)
                if difficulty_key not in self.quiz_data or not self.quiz_data[difficulty_key]:
                    messagebox.showerror("Error", f"No questions available for the selected difficulty: {self.difficulty}")
                    return

                # Load only 10 random questions for the selected difficulty
                if len(self.quiz_data[difficulty_key]) >= 10:
                    self.questions = random.sample(self.quiz_data[difficulty_key], 10)  # Select 10 unique random questions
                else:
                    self.questions = self.quiz_data[difficulty_key].copy()  # Use all available questions if less than 10

                # Load events and shuffle them
                self.events = self.random_events[difficulty_key].copy()
                random.shuffle(self.events)

                self.total_questions = len(self.questions)  # This will now be 10 or less
                self.load_question()

            # **Pause Background Music Before Starting Quiz Think Time Music**
            if self.background_music_on:
                pygame.mixer.music.pause()
                print("Background music paused.")

            # **Start the Quiz Thinking Sound Once Here**
            if self.sound_effects_on:
                try:
                    self.quiz_thinktime_sound.play(-1)  # Loop the think time sound indefinitely
                    print("Quiz think time sound started playing.")
                except pygame.error as e:
                    print(f"Failed to play quiz think time sound: {e}")

            # **Enable "My Profile" Button if User Exists**
            self.update_my_profile_button()

    # load quiz questions
    def load_question(self):
        self.clear_screen()
        self.root.config(bg="#f0f8ff")
        self.question_in_progress = True
        # Reset hint usage for each question
        self.hint_used = False  
        print(f"Question {self.current_question + 1}: hint_used reset to {self.hint_used}")

        if self.current_question < self.total_questions:
            # Create a container frame for canvas and scrollbar to keep everything aligned
            container_frame = tk.Frame(self.root, bg="#f0f8ff")
            container_frame.pack(fill=tk.BOTH, expand=True)

            # Create a canvas widget to hold all quiz elements
            canvas = tk.Canvas(container_frame, bg="#f0f8ff", highlightthickness=0)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Add a scrollbar linked to the canvas
            scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Create a frame inside the canvas for scrollable content
            scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")
            scrollable_frame.pack(fill=tk.BOTH, expand=True)

            # Add the frame to a window in the canvas
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            # Configure canvas to work with the scrollbar
            canvas.configure(yscrollcommand=scrollbar.set)

            # Bind canvas resize event to adjust scroll region
            def configure_canvas(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.itemconfig("all", width=event.width)  # Adjust frame width with canvas

            # Reconfigure canvas on root window resize
            canvas.bind("<Configure>", configure_canvas)

            # Bind the mouse wheel to scroll vertically in the canvas
            canvas.bind_all("<MouseWheel>", lambda event: self._on_mouse_wheel_qn(event, canvas))

            # -------------------------
            # Timer Label placed at the top of the scrollable frame
            # -------------------------
            self.timer_label = tk.Label(
                scrollable_frame,
                text=f"Time Left: {self.time_left}s",
                font=("Comic Sans MS", 16),  # Standardized font size
                bg="#f0f8ff",
                fg="#ff4500"
            )
            self.timer_label.pack(pady=(8, 0))  # Top padding of 8, no bottom padding

            # -------------------------
            # Info Frame for Money and Game Points (Added)
            # -------------------------
            info_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")
            info_frame.pack(pady=(0, 8))  # Padding between Timer and Info Labels

            # Money Label
            money_label = tk.Label(
                info_frame,
                text=f"Money: ${self.money} 💰",
                font=("Comic Sans MS", 16),  # Standardized font size
                bg="#f0f8ff",
                fg="#ff4500"
            )
            money_label.pack(side=tk.LEFT, padx=10)  # Left side with horizontal padding

            # Game Points Label (Added)
            game_points_label = tk.Label(
                info_frame,
                text=f"Game Points: {self.game_points} 🎯",
                font=("Comic Sans MS", 16),  # Standardized font size
                bg="#f0f8ff",
                fg="#ff4500"
            )
            game_points_label.pack(side=tk.LEFT, padx=10)  # Left side with horizontal padding

            # -------------------------
            # Progress Label to Reflect Number of Questions Answered
            # -------------------------
            progress_label = tk.Label(
                scrollable_frame,
                text=f"Progress: {self.current_question + 1}/{self.total_questions}",
                font=("Comic Sans MS", 16),  # Standardized font size
                bg="#f0f8ff",
                fg="#ff4500"
            )
            progress_label.pack(pady=(0,8))

            # -------------------------
            # Timer Progress Bar
            # -------------------------
            self.timer_progress_bar = ttk.Progressbar(
                scrollable_frame,
                orient='horizontal',
                length=500,  # Adjusted length
                mode='determinate',
                maximum=30,  # Total time per question in seconds
                value=30,  # Initial value set to maximum
                style="Timer.Horizontal.TProgressbar"
            )
            self.timer_progress_bar.pack(pady=(0, 8))  # Bottom padding of 8

            # -------------------------
            # Display the Question Text
            # -------------------------
            question_data = self.questions[self.current_question]
            question_label = tk.Label(
                scrollable_frame,
                text=question_data["question"],
                font=("Comic Sans MS", 18),  # Increased font size for better readability
                bg="#f0f8ff",
                fg="#ff4500",
                wraplength=700,  # Increased wraplength for better readability
                justify="center"
            )
            question_label.pack(pady=(0, 20))  # Bottom padding of 20

            # -------------------------
            # Radio Buttons for Options
            # -------------------------
            self.options_var = tk.StringVar()

            # Initialize the list to hold option buttons
            self.option_buttons = []

            # Create a frame to hold the radio buttons for better alignment
            options_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")
            options_frame.pack(pady=(0, 20))  # Bottom padding of 20

            for option in question_data["options"]:
                option_button = tk.Radiobutton(
                    options_frame,
                    text=option,
                    variable=self.options_var,
                    value=option,
                    font=("Comic Sans MS", 16),
                    bg="#f0f8ff",
                    fg="#000000",  # Changed to black for better contrast
                    indicatoron=0,
                    width=50,  # Increased width for better button size
                    pady=10,
                    command=self.play_radio_button_sound  # Add command here
                )
                option_button.pack(pady=5, anchor='w')  # Left-align the buttons with padding
                self.option_buttons.append(option_button)

            # -------------------------
            # Submit and Hint Buttons with Consistent Styling (Modified)
            # -------------------------
            buttons_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")
            buttons_frame.pack(pady=(0, 20))  # Bottom padding of 20

            # Hint Button (Placed on the Left)
            self.hint_button = self.create_button(
                text="💡 Get a Hint",
                command=self.give_hint,
                parent=buttons_frame,
                font_size=16,  # Standardized font size
                width=15,       # Adjusted width
                height=2        # Increased height for better visibility
            )
            self.hint_button.pack(side=tk.LEFT, padx=10)  # Left side with padding

            # Submit Button (Placed on the Right)
            submit_button = self.create_button(
                text="Submit",
                command=self.check_answer,
                parent=buttons_frame,
                font_size=16,  # Standardized font size
                width=15,       # Adjusted width
                height=2        # Increased height for better visibility
            )
            submit_button.pack(side=tk.RIGHT, padx=10)  # Right side with padding

            # -------------------------
            # Start the Timer for Each Question
            # -------------------------
            self.start_timer(30)

            # Optional: Bind the Enter key to submit the answer
            self.root.bind('<Return>', lambda event: self.check_answer())

    # scrolling function for quiz
    def _on_mouse_wheel_qn(self, event, canvas):
        """Enable scrolling with the mouse wheel on the canvas."""
        if event.delta:
           canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # start the countdown timer for the quiz question
    def start_timer(self, seconds):
        """Start or reset the timer for the current question."""
        self.question_timer = seconds  # Store the total time for the question
        self.time_left = seconds
        if self.timer_label:
            self.timer_label.config(text=f"Time Left: {self.time_left}s")
        if self.timer_progress_bar:
            self.timer_progress_bar['value'] = self.time_left  # Reset timer progress bar to full
        self.update_timer()

    # update the timer every second and check for timeout
    def update_timer(self):
        """Update the timer every second and check for timeout."""
        if not self.question_in_progress:
            return  # Exit if no question is in progress
        if self.time_left > 0:
            self.time_left -= 1
            if self.timer_label.winfo_exists():
                self.timer_label.config(text=f"Time Left: {self.time_left}s")
            if self.timer_progress_bar:
                self.timer_progress_bar['value'] = self.time_left  # Update timer progress bar
            # Store the timer ID so we can cancel it later
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            messagebox.showwarning("Time's Up!", "You ran out of time!")
            self.money -= 5  # Penalize for running out of time
            self.spending_categories["Quiz Losses"] += 5
            self.question_in_progress = False  # Stop the timer
            self.go_to_next_question()

    # check the answers if correct or wrong
    def check_answer(self):
        if not self.question_in_progress:
            return

        selected_option = self.options_var.get()

        if not selected_option:
            messagebox.showwarning("Selection Error", "Please select an answer!")
            return

        question_data = self.questions[self.current_question]
        correct_answer = question_data["answer"]

        # Calculate response time
        response_time = self.question_timer - self.time_left  # Time taken to answer

        # Points calculation formula:
        points_earned = round((1 - ((response_time / self.question_timer) / 2)) * self.points_possible)

        # Ensure points earned are not negative
        points_earned = max(points_earned, 0)

        if selected_option == correct_answer:
            # Correct answer logic
            self.money += 10
            self.spending_categories["Quiz Earnings"] += 10
            self.correct_streak += 1

            self.game_points += points_earned  # Award points based on speed

            # Play correct answer sound
            if self.sound_effects_on:
                self.correct_sound.play()

            # Streak bonus
            if self.correct_streak >= 3:
                self.money += 10
                self.spending_categories["Quiz Earnings"] += 10
                self.correct_streak = 0
                self.show_feedback(f"Correct! 😊 Streak Bonus Earned! 🎉\n{question_data['explanation']}", True, points_earned)
            else:
                self.show_feedback(f"Correct! 😊\n{question_data['explanation']}", True, points_earned)
        else:
            # Incorrect answer logic
            self.money -= 5
            self.spending_categories["Quiz Losses"] += 5
            self.wrong_answers += 1
            self.correct_streak = 0

            # Play wrong answer sound
            if self.sound_effects_on:
                self.wrong_sound.play()

            # Optionally, deduct points for incorrect answers
            # self.game_points -= 5  # Uncomment if you want to penalize

            self.show_feedback(f"Incorrect! 😟\nCorrect answer: {correct_answer}\n{question_data['explanation']}", False, 0)

        self.question_in_progress = False

        # Cancel the timer since the question is answered
        if hasattr(self, 'timer_id'):
            self.root.after_cancel(self.timer_id)
            del self.timer_id

    # show feedback/explanation for the questions
    def show_feedback(self, message, is_correct, points_earned=0):
        self.clear_screen()

        # Green for correct, red for incorrect
        feedback_color = "#1ac41a" if is_correct else "#ff4500"
        feedback_bg_color = "#d4f8e8" if is_correct else "#ffe6e6"  

        # Change background color based on correctness
        self.root.config(bg=feedback_bg_color)  

        # Include points earned in the feedback message
        if is_correct:
            points_message = f"\nYou earned {points_earned} 🎯 Game Points!"
        else:
            points_message = ""

        feedback_label = tk.Label(
            self.root, 
            text=message + points_message, 
            font=("Comic Sans MS", 18), 
            bg=feedback_bg_color, 
            fg=feedback_color, 
            wraplength=600
        )
        feedback_label.pack(pady=20)

        # Button to go to the next question after review
        next_button = self.create_button("Next", self.go_to_next_question)
        next_button.pack(side=tk.TOP, padx=5, pady=5)  # Reduce padding
        next_button.config(width=10, height=2)  # Set custom width and height

        self.center_content()

    # quiz hint feature
    def give_hint(self):
        print(f"give_hint called. Current hint_used: {self.hint_used}")
        if self.hint_used:
            messagebox.showinfo("Hint Used", "You have already used a hint for this question!")
            return

        # Ensure there are questions loaded
        if not self.questions or self.current_question >= self.total_questions:
            messagebox.showwarning("No Active Question", "No active question to provide a hint for!")
            return

        question_data = self.questions[self.current_question]
        correct_answer = question_data["answer"]

        print(f"Correct answer: {correct_answer}")
        print("Option Buttons:")
        for btn in self.option_buttons:
            print(f" - {btn.cget('text')} (State: {btn.cget('state')})")

        # Collect incorrect options
        incorrect_options = [
            btn for btn in self.option_buttons 
            if btn.cget("text") != correct_answer and btn['state'] != tk.DISABLED
        ]

        print(f"Incorrect options count: {len(incorrect_options)}")
        if incorrect_options:
            # Randomly select an incorrect option to gray out
            option_to_disable = random.choice(incorrect_options)
            print(f"Selected option to disable: {option_to_disable.cget('text')}")

            # Disable and gray out the selected option
            option_to_disable.config(state=tk.DISABLED, disabledforeground="gray")
            print(f"Disabled option: {option_to_disable.cget('text')}")

            # Mark that the hint has been used for this question
            self.hint_used = True
            print(f"Hint used for question {self.current_question + 1}. hint_used set to {self.hint_used}")

            # Disable the hint button to prevent further use
            self.hint_button.config(state=tk.DISABLED)
            print("Hint button disabled.")

            # Provide visual feedback
            messagebox.showinfo("Hint Applied", f"One incorrect option has been eliminated: {option_to_disable.cget('text')}")
        else:
            messagebox.showinfo("Hint", "No more incorrect options to eliminate!")

    # go to next question after finishing previous question
    def go_to_next_question(self):
        self.current_question += 1

        if self.current_question < self.total_questions:
            # 30% chance of a random event
            if random.random() < 0.3:  
                self.random_event()
            else:
                self.load_question()
        else:
            self.end_quiz()

    # start a random event
    def random_event(self):
        """Display a random event, if any."""
        # Assuming "All-Star Challenge" is mapped to "master"
        if self.difficulty in ["Challenger", "All-Star Challenge"]:
            # For these modes, pick from all combined events
            event, amount = random.choice(self.events)
        else:
            # For specific difficulty, pick from that difficulty's events
            event, amount = random.choice(self.events)
            
        self.show_event_popup(event, amount)

    # show random event
    def show_event_popup(self, event, amount):
        self.clear_screen()
        self.root.config(bg="#f0f8ff")
    
        event_label = tk.Label(self.root, text=event, font=("Comic Sans MS", 18), bg="#f0f8ff", fg="#ff4500", wraplength=600)
        event_label.pack(pady=20)
    
        def handle_event(response):
            if response:
                if self.sound_effects_on:
                    self.random_accept_sound.play()  # Play accept sound
                self.money += amount
            else:
                if self.sound_effects_on:
                    self.random_decline_sound.play()  # Play decline sound

            # Track random event earnings or penalties
            if amount > 0:
                self.spending_categories["Random Events"] += amount  # Track earnings
            else:
                self.spending_categories["Quiz Losses"] += abs(amount)  # Track losses

            # After handling the event, go back to the quiz question
            self.load_question()

        # Modify event buttons in show_event_popup to use the new handle_event method
        yes_button = self.create_button("Yes", lambda: handle_event(True))
        yes_button.pack(side=tk.TOP, padx=5, pady=5)  # Reduce padding
        yes_button.config(width=20, height=2)  # Set custom width and height

        no_button = self.create_button("No", lambda: handle_event(False))
        no_button.pack(side=tk.TOP, padx=5, pady=5)  # Reduce padding
        no_button.config(width=20, height=2)  # Set custom width and height

        self.center_content()

    # end of quiz screen and updating leaderboard
    def end_quiz(self):
        """Display the end quiz screen and update leaderboard."""
        try:
            # Stop the timer updates
            self.question_in_progress = False 
            if hasattr(self, 'timer_id'):
                self.root.after_cancel(self.timer_id)
                del self.timer_id
            self.clear_screen()
            self.root.config(bg="#f0f8ff")

            if self.sound_effects_on:
                self.quiz_thinktime_sound.stop()  # Stop the think time sound
                print("Quiz think time sound stopped.")
            if self.background_music_on:
                pygame.mixer.music.unpause()
                print("Background music resumed.")

            # **Retrieve and Update Highest Game Points for Current Difficulty**
            internal_difficulty = self.difficulty_mapping.get(self.difficulty, self.difficulty)
            print(f"Internal Difficulty for Highest Score: {internal_difficulty}")  # Debugging line
            current_high_score = self.highest_game_points.get(internal_difficulty, 0)

            new_high_score = False
            if self.game_points > current_high_score:
                self.highest_game_points[internal_difficulty] = self.game_points
                new_high_score = True

            # **Update and Save Leaderboard**
            self.save_leaderboard_to_csv()
            print(f"Saving to Leaderboard: Difficulty Level - {internal_difficulty}")  # Debugging line

            # **Save User Data with High Score Check**
            self.save_user_data(check_high_score=True)

            # Display end of quiz message with game points
            end_message = f"Quiz Completed! 🎉\nYou finished with ${self.money} 💰 and {self.game_points} 🎯 Game Points!"
            end_label = tk.Label(
                self.root, 
                text=end_message, 
                font=("Comic Sans MS", 24), 
                bg="#f0f8ff", 
                fg="#ff4500",
                wraplength=800,
                justify="center"
            )
            end_label.pack(pady=20)

            # Display high score or regular completion message
            if new_high_score:
                high_score_label = tk.Label(
                    self.root,
                    text=f"🎯 New High Score: {self.game_points}!",
                    font=("Comic Sans MS", 20, "bold"),
                    bg="#f0f8ff",
                    fg="#1ac41a",
                    wraplength=800,
                    justify="center"
                )
                high_score_label.pack(pady=10)
            else:
                completion_label = tk.Label(
                    self.root,
                    text=f"Highest Score: {current_high_score} 🎯",
                    font=("Comic Sans MS", 18),
                    bg="#f0f8ff",
                    fg="#ff4500",
                    wraplength=800,
                    justify="center"
                )
                completion_label.pack(pady=5)

            # Check if the final score is negative
            if self.money < 0:
                # Display funny debt message
                debt_message = (
                    "Oh no! 😱 You're in debt! 💸\n"
                    "You'll need to play again to repay your debt. 💪🏽\n"
                    "Don't worry, we've got your back! 😊"
                )
                debt_label = tk.Label(
                    self.root, 
                    text=debt_message, 
                    font=("Comic Sans MS", 18), 
                    bg="#f0f8ff", 
                    fg="#ff4500",
                    wraplength=800,
                    justify="center"
                )
                debt_label.pack(pady=10)

            # **Generate Assessment Message**
            # Determine knowledge level based on wrong_answers
            if self.wrong_answers >= 5:
                knowledge_level = "fair"
            elif self.wrong_answers <= 2:
                knowledge_level = "excellent"
            else:
                knowledge_level = "good"

            # Map internal difficulty to display difficulty
            financial_level = self.internal_to_display.get(internal_difficulty, "unknown")

            # Create the assessment message
            assessment_message = (
                f"Based on your quiz results, you have a {knowledge_level} understanding of {financial_level} "
                f"financial understanding and planning!"
            )

            # Display the assessment message
            assessment_label = tk.Label(
                self.root,
                text=assessment_message,
                font=("Comic Sans MS", 18),
                bg="#f0f8ff",
                fg="#000000",
                wraplength=800,
                justify="center"
            )
            assessment_label.pack(pady=10)

            # Add button to let players play again
            play_again_text = "🔄 Play Again to Repay Debt" if self.money < 0 else "🔄 Play Again"
            play_again_button = self.create_button(
                text=play_again_text,
                command=self.show_home_page,  # Navigate back to home screen
                width=30,
                height=2
            )
            play_again_button.pack(pady=10)

            # Add button to show spending overview
            stats_button = self.create_button(
                text="📊 Show Spending Overview",
                command=self.show_spending_overview,
                width=30,   # Increased width
                height=2    # Increased height
            )
            stats_button.pack(pady=10)

            self.center_content()

        except Exception as e:
            print(f"An error occurred in end_quiz: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    # handle window music change
    def on_close(self):
        """Handle cleanup when the main window is closed."""
        if self.sound_effects_on:
            self.quiz_thinktime_sound.stop()
            pygame.mixer.music.stop()
        self.root.destroy()

    # open shop
    def open_shop(self):
        self.clear_screen()
        self.root.config(bg="#f0f8ff")
        # Load user data to ensure inventory is up-to-date
        self.load_user_data()

        # Create a main container frame to hold money label, categories, shop items, and back button
        main_container = tk.Frame(self.root, bg="#f0f8ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # -------------------------
        # Money Label (Outside Scrollable Frame)
        # -------------------------
        money_label = tk.Label(
            main_container,
            text=f"Money: ${self.money} 💰",
            font=("Comic Sans MS", 18),
            bg="#f0f8ff",
            fg="#ff4500"
        )
        money_label.pack(pady=10)

        # -------------------------
        # Categories Frame (Outside Scrollable Area)
        # -------------------------
        categories_frame = tk.Frame(main_container, bg="#f0f8ff")
        categories_frame.pack(fill=tk.X, pady=(0, 10))  # Add some padding below categories

        # Define fixed categories
        categories = ["Hats", "Outfits", "Accessories", "Shoes"]

        # Create category labels
        for category in categories:
            category_label = tk.Label(
                categories_frame,
                text=category,
                font=("Comic Sans MS", 16, "bold"),
                bg="#f0f8ff",
                fg="#ff4500",
                padx=10,
                pady=5
            )
            category_label.pack(side="left", expand=True, fill=tk.X, padx=10)

        # -------------------------
        # Scrollable Shop Items Area
        # -------------------------
        # Create a frame for the shop items (scrollable)
        shop_container = tk.Frame(main_container, bg="#f0f8ff")
        shop_container.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for the shop items
        self.shop_canvas = tk.Canvas(shop_container, bg="#f0f8ff", highlightthickness=0)
        self.shop_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a vertical scrollbar to the canvas
        scrollbar = ttk.Scrollbar(shop_container, orient="vertical", command=self.shop_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.shop_canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold shop items
        shop_frame = tk.Frame(self.shop_canvas, bg="#f0f8ff")
        self.shop_frame_id = self.shop_canvas.create_window((0, 0), window=shop_frame, anchor="nw")

        # Update scrollregion when the shop_frame size changes
        def on_frame_configure(event):
            self.shop_canvas.configure(scrollregion=self.shop_canvas.bbox("all"))

        shop_frame.bind("<Configure>", on_frame_configure)

        # Adjust the shop_frame width to match the canvas
        def on_canvas_configure(event):
            canvas_width = event.width
            self.shop_canvas.itemconfig(self.shop_frame_id, width=canvas_width)

        self.shop_canvas.bind("<Configure>", on_canvas_configure)

        # -------------------------
        # Display Shop Items
        # -------------------------
        categorized_shop_items = {
            "Hats": [
                {"name": "Fancy Hat 🎩", "price": 20, "type": "hat", "effect": "cool"},
                {"name": "Sun Visor 🧢", "price": 15, "type": "hat", "effect": "reduce glare"},
                {"name": "Wizard's Hat 🪄", "price": 40, "type": "hat", "effect": "increase magic"},
                {"name": "Stealth Hood 🕶️", "price": 35, "type": "hat", "effect": "improve stealth"},
                {"name": "Battle Helm 🪖", "price": 50, "type": "hat", "effect": "increase defense"},
            ],
            "Outfits": [
                {"name": "Invisibility Cloak 🧥", "price": 60, "type": "outfit", "effect": "invisible"},
                {"name": "Warrior Armor ⛊", "price": 80, "type": "outfit", "effect": "increase strength"},
                {"name": "Ranger Outfit 🏹", "price": 45, "type": "outfit", "effect": "increase agility"},
                {"name": "Sorcerer's Robe ✨", "price": 70, "type": "outfit", "effect": "mana regeneration"},
                {"name": "Shadow Suit 👻", "price": 55, "type": "outfit", "effect": "improve stealth"}
            ],
            "Accessories": [
                {"name": "Lucky Bracelet 🍀", "price": 15, "type": "accessory", "effect": "increase luck"},
                {"name": "Strength Amulet 💪", "price": 30, "type": "accessory", "effect": "boost attack"},
                {"name": "Mystic Pendant 🔮", "price": 40, "type": "accessory", "effect": "increase mana"},
                {"name": "Protection Ring 💍", "price": 35, "type": "accessory", "effect": "reduce damage"},
                {"name": "Speed Band 🏃", "price": 25, "type": "accessory", "effect": "increase speed"}
            ],
            "Shoes": [
                {"name": "Golden Shoes 👟", "price": 50, "type": "shoes", "effect": "fast"},
                {"name": "Winged Boots 🪶", "price": 70, "type": "shoes", "effect": "enable flight"},
                {"name": "Steel Greaves 🦿", "price": 60, "type": "shoes", "effect": "increase defense"},
                {"name": "Silent Sneakers 👣", "price": 40, "type": "shoes", "effect": "quiet movement"},
                {"name": "Flamewalkers 🔥", "price": 80, "type": "shoes", "effect": "fire resistance"}
            ]
        }

        # Create category columns
        for col, category in enumerate(categories):
            # Add items under each category
            for row, item in enumerate(categorized_shop_items.get(category, []), start=1):
                # Check if the item is already purchased
                is_purchased = item["name"] in self.inventory

                # Define button state
                state = tk.DISABLED if is_purchased else tk.NORMAL

                # Create the shop item button
                item_button = tk.Button(
                    shop_frame,
                    text=f"{item['name']} - ${item['price']}",
                    command=lambda i=item: self.buy_item(i),
                    font=("Comic Sans MS", 14),
                    bg="#ff4500",
                    fg="#f0f8ff",
                    pady=5,
                    width=25,
                    height=2,
                    state=state,
                    disabledforeground="gray"  # Grey out the text when disabled
                )
                item_button.grid(row=row, column=col, padx=10, pady=5, sticky="n")

        # Center the columns within the shop_frame
        for col in range(len(categories)):
            shop_frame.grid_columnconfigure(col, weight=1)

        # -------------------------
        # Fixed Back Button Area (Outside Scrollable Frame)
        # -------------------------
        back_button_frame = tk.Frame(main_container, bg="#f0f8ff")
        back_button_frame.pack(fill=tk.X, pady=10)

        back_button = self.create_button(
            "Back",
            self.show_home_page,
            parent=back_button_frame,
            width=20,
            height=2,
            font_size=14
        )
        back_button.pack(pady=5)  # Centered by default

        # Ensure the canvas scrolls correctly after all elements are packed
        self.shop_canvas.update_idletasks()
        self.shop_canvas.configure(scrollregion=self.shop_canvas.bbox("all"))

        # Bind mouse wheel to the shop_canvas for scrolling
        self.bind_mouse_wheel_shop()

        # Center content within the main_container
        self.center_content()

    # scrolling for shop menue
    def bind_mouse_wheel_shop(self):
        """Enable scrolling with the mouse wheel on the shop canvas."""
        self.shop_canvas.bind("<Enter>", self._bind_to_mousewheel_shop)
        self.shop_canvas.bind("<Leave>", self._unbind_from_mousewheel_shop)

    # scrolling for shop menue
    def _bind_to_mousewheel_shop(self, event):
        if self.root.tk.call('tk', 'windowingsystem') == 'win32':
            self.shop_canvas.bind_all("<MouseWheel>", self._on_mouse_wheel_shop)
        elif self.root.tk.call('tk', 'windowingsystem') == 'x11':
            self.shop_canvas.bind_all("<Button-4>", self._on_mouse_wheel_shop)
            self.shop_canvas.bind_all("<Button-5>", self._on_mouse_wheel_shop)
        elif self.root.tk.call('tk', 'windowingsystem') == 'aqua':
            self.shop_canvas.bind_all("<MouseWheel>", self._on_mouse_wheel_shop)

    # scrolling for shop menue
    def _unbind_from_mousewheel_shop(self, event):
        if self.root.tk.call('tk', 'windowingsystem') == 'win32':
            self.shop_canvas.unbind_all("<MouseWheel>")
        elif self.root.tk.call('tk', 'windowingsystem') == 'x11':
            self.shop_canvas.unbind_all("<Button-4>")
            self.shop_canvas.unbind_all("<Button-5>")
        elif self.root.tk.call('tk', 'windowingsystem') == 'aqua':
            self.shop_canvas.unbind_all("<MouseWheel>")

    # scrolling for shop menue
    def _on_mouse_wheel_shop(self, event):
        """Scroll the shop canvas with the mouse wheel."""
        if event.delta:
            self.shop_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 5:
                self.shop_canvas.yview_scroll(1, "units")  # Scroll down
            elif event.num == 4:
                self.shop_canvas.yview_scroll(-1, "units")  # Scroll up

    # allow players to buy items in the shop
    def buy_item(self, item):
        if self.money >= item["price"]:
            if item["name"] not in self.inventory:
                self.money -= item["price"]
                self.inventory.append(item["name"])
                messagebox.showinfo("Purchase Successful", f"You bought {item['name']}! Now you {item['effect']}!")
                self.equip_item(item["name"], item["type"])  # Automatically equip the item upon purchase
                self.save_user_data(check_high_score=False)  # Save inventory after purchase without checking high scores
            else:
                messagebox.showwarning("Already Owned", f"You already own {item['name']}!")
        else:
            messagebox.showwarning("Not Enough Money", "You don't have enough money to buy this item.")
        self.open_shop()  # Reload shop after buying

    # users can choose to equip and re-equip items from the shop
    def equip_item(self, item, item_type):
        """Equip the specified item of a given type."""
        # Check if the item is already equipped
        if self.equipped_items.get(item_type) == item:
            messagebox.showinfo("Already Equipped", f"{item} is already equipped.")
            return

        # Equip the new item
        self.equipped_items[item_type] = item
        messagebox.showinfo("Item Equipped", f"You have equipped {item}!")

        # Save user data without checking high scores
        self.save_user_data(check_high_score=False)

        # Refresh the customization page to update button states
        self.show_character_customization()

    # prompt the player to select an item of the specified item to equip
    def prompt_equip_item(self, item_type):
        """Prompt the player to select an item of the specified type to equip."""
        items_of_type = [item for item in self.inventory if any(itm["name"] == item and itm["type"] == item_type for itm in self.get_all_shop_items())]

        if not items_of_type:
            messagebox.showwarning("No Items", f"You have no {item_type.capitalize()}s to equip.")
            return

        # Create a new top-level window for item selection
        selection_window = tk.Toplevel(self.root)
        selection_window.title(f"Equip {item_type.capitalize()}")
        selection_window.geometry("400x300")
        selection_window.config(bg="#f0f8ff")

        # Title Label
        title_label = tk.Label(
            selection_window,
            text=f"Select a {item_type.capitalize()} to Equip",
            font=("Comic Sans MS", 18, "bold"),
            bg="#f0f8ff",
            fg="#ff4500"
        )
        title_label.pack(pady=20)

        # Variable to store the selected item
        selected_item_var = tk.StringVar(value=items_of_type[0])

        # Create radio buttons for each item
        for item in items_of_type:
            radio = tk.Radiobutton(
                selection_window,
                text=item,
                variable=selected_item_var,
                value=item,
                font=("Comic Sans MS", 14),
                bg="#f0f8ff",
                fg="#000000",
                indicatoron=0,
                width=30,
                pady=5
            )
            radio.pack(pady=5)

        # Function to handle equip action
        def equip_selected():
            selected_item = selected_item_var.get()
            self.equip_item(selected_item, item_type)
            selection_window.destroy()

        # Equip Button
        equip_button = self.create_button(
            text="Equip",
            command=equip_selected,
            width=15,
            height=2,
            font_size=14,
            parent=selection_window
        )
        equip_button.pack(pady=20)

        # Make sure the selection window is modal
        selection_window.grab_set()
        self.root.wait_window(selection_window)

    # Toggle equip/unequip for a given item type
    def toggle_equip_item(self, item_type):
        """Toggle equip/unequip for a given item type."""
        # Check if the user has items of this type in their inventory
        items_of_type = [item for item in self.inventory if any(itm["name"] == item and itm["type"] == item_type for itm in self.get_all_shop_items())]

        if not items_of_type:
            messagebox.showinfo("No Items Available", f"You do not own any {item_type.capitalize()}s to equip yet!")
            return

        currently_equipped = self.equipped_items.get(item_type)
        
        if currently_equipped:
            # Unequip the current item
            self.unequip_item(item_type)
        else:
            # Prompt to equip an item
            self.prompt_equip_item(item_type)

    # users can choose to unequip items purchased from the shop 
    def unequip_item(self, item_type):
        """Unequip an item of the specified type."""
        equipped_item = self.equipped_items.get(item_type)
        if equipped_item:
            confirm = messagebox.askyesno("Unequip Item", f"Do you want to unequip your {item_type.capitalize()}?")
            if confirm:
                self.equipped_items[item_type] = None
                messagebox.showinfo("Item Unequipped", f"You have unequipped your {item_type.capitalize()}.")
                self.save_user_data(check_high_score=False)  # Save data without checking high scores
                self.show_character_customization()
        else:
            messagebox.showinfo("No Item Equipped", f"No {item_type.capitalize()} is currently equipped.")

    # retrieve all shop items across all categories
    def get_all_shop_items(self):
        """Retrieve all shop items across all categories."""
        categorized_shop_items = {
        "hat": [{"name": "Fancy Hat 🎩", "price": 20, "type": "hat", "effect": "cool"},
        {"name": "Sun Visor 🧢", "price": 15, "type": "hat", "effect": "reduce glare"},
        {"name": "Wizard's Hat 🪄", "price": 40, "type": "hat", "effect": "increase magic"},
        {"name": "Stealth Hood 🕶️", "price": 35, "type": "hat", "effect": "improve stealth"},
        {"name": "Battle Helm 🪖", "price": 50, "type": "hat", "effect": "increase defense"},
            ],
        "outfit":[
        {"name": "Invisibility Cloak 🧥", "price": 60, "type": "outfit", "effect": "invisible"},
        {"name": "Warrior Armor 🛡️", "price": 80, "type": "outfit", "effect": "increase strength"},
        {"name": "Ranger Outfit 🏹", "price": 45, "type": "outfit", "effect": "increase agility"},
        {"name": "Sorcerer's Robe ✨", "price": 70, "type": "outfit", "effect": "mana regeneration"},
        {"name": "Shadow Suit 🖤", "price": 55, "type": "outfit", "effect": "improve stealth"}
            ], 
        "accessory":[
        {"name": "Lucky Bracelet 🍀", "price": 15, "type": "accessory", "effect": "increase luck"},
        {"name": "Strength Amulet 💪", "price": 30, "type": "accessory", "effect": "boost attack"},
        {"name": "Mystic Pendant 🔮", "price": 40, "type": "accessory", "effect": "increase mana"},
        {"name": "Protection Ring 💍", "price": 35, "type": "accessory", "effect": "reduce damage"},
        {"name": "Speed Band 🏃", "price": 25, "type": "accessory", "effect": "increase speed"}
            ], 
        "shoes":[
        {"name": "Golden Shoes 👟", "price": 50, "type": "shoes", "effect": "fast"},
        {"name": "Winged Boots 🕊️", "price": 70, "type": "shoes", "effect": "enable flight"},
        {"name": "Steel Greaves 🦵", "price": 60, "type": "shoes", "effect": "increase defense"},
        {"name": "Silent Sneakers 👣", "price": 40, "type": "shoes", "effect": "quiet movement"},
        {"name": "Flamewalkers 🔥", "price": 80, "type": "shoes", "effect": "fire resistance"}
            ]
        }
        all_items = []
        for items in categorized_shop_items.values():
            all_items.extend(items)
        return all_items

    # users can select their preferred purchased items
    def show_character_customization(self):
        self.clear_screen()
        self.root.config(bg="#f0f8ff")
        
        # Load user data to ensure inventory is up-to-date
        self.load_user_data()

        # Create a main container frame to hold all content
        main_container = tk.Frame(self.root, bg="#f0f8ff")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Title Label
        character_label = tk.Label(
            main_container, 
            text="Your Character", 
            font=("Comic Sans MS", 24), 
            bg="#f0f8ff", 
            fg="#ff4500"
        )
        character_label.pack(pady=(20, 10))  # Top padding of 20, bottom padding of 10

        # Equipped Items Label
        equipped_items_text = "Equipped Items:\n"
        for item_type, item_name in self.equipped_items.items():
            equipped_items_text += f"{item_type.capitalize()}: {item_name or 'None'}\n"

        equipped_label = tk.Label(
            main_container,
            text=equipped_items_text,
            font=("Comic Sans MS", 18),
            bg="#f0f8ff",
            fg="#ff4500",
            justify="center"  # Center-align the text within the label
        )
        equipped_label.pack(pady=(0, 20))  # Top padding of 0, bottom padding of 20

        # -------------------------
        # Equip/Unequip Buttons Area
        # -------------------------
        buttons_frame = tk.Frame(main_container, bg="#f0f8ff")
        buttons_frame.pack(pady=10)  # Adjust padding as necessary

        # Iterate through each item type to create Equip and Unequip buttons horizontally
        for item_type in self.equipped_items.keys():
            # Check if the user has items of this type in their inventory
            items_of_type = [
                item for item in self.inventory 
                if any(itm["name"] == item and itm["type"] == item_type for itm in self.get_all_shop_items())
            ]

            # Only create buttons if the user has items of this type
            if items_of_type:
                # Create a subframe for each item type to hold Equip and Unequip buttons horizontally
                subframe = tk.Frame(buttons_frame, bg="#f0f8ff")
                subframe.pack(pady=5, fill=tk.X)

                # Equip Button with item type in the text
                equip_button = self.create_button(
                    text=f"Equip {item_type.capitalize()}",
                    command=lambda it=item_type: self.prompt_equip_item(it),
                    parent=subframe,
                    width=20,
                    height=2,
                    font_size=16,
                    justify='center'
                )
                equip_button.pack(side=tk.LEFT, padx=10)

                # Unequip Button with item type in the text
                unequip_button = self.create_button(
                    text=f"Unequip {item_type.capitalize()}",
                    command=lambda it=item_type: self.unequip_item(it),
                    parent=subframe,
                    width=20,
                    height=2,
                    font_size=16,
                    justify='center'
                )
                unequip_button.pack(side=tk.LEFT, padx=10)

                # Set the button states based on equipped status
                if self.equipped_items.get(item_type):
                    equip_button.config(state=tk.DISABLED)
                    unequip_button.config(state=tk.NORMAL)
                else:
                    equip_button.config(state=tk.NORMAL)
                    unequip_button.config(state=tk.DISABLED)

        # -------------------------
        # Back Button Centered Below Equip/Unequip Buttons
        # -------------------------
        back_button = self.create_button(
            "Back",
            self.show_home_page,
            width=20,
            height=2,
            font_size=14,
            parent=main_container
        )
        back_button.pack(pady=20)  # Vertical padding to separate from equip buttons

        self.center_content()

    # display in-game leaderboard
    def show_leaderboard(self):
        """Display the leaderboard sorted by descending Game Points with Rank, Username, Game Points, Difficulty Level."""
        self.clear_screen()
        self.root.config(bg="#f0f8ff")

        leaderboard_label = tk.Label(
            self.root,
            text="Leaderboard",
            font=("Comic Sans MS", 24),
            bg="#f0f8ff",
            fg="#ff4500"
        )
        leaderboard_label.pack(pady=20)

        leaderboard = []

        if os.path.exists(self.leaderboard_path):
            try:
                with open(self.leaderboard_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    expected_headers = ['Datetime Captured', 'Username', 'Game Points', 'Difficulty Level', 'Current Rank']
                    if reader.fieldnames != expected_headers:
                        messagebox.showerror("Error", "Leaderboard headers are incorrect.")
                        return
                    for row in reader:
                        try:
                            leaderboard.append({
                                "datetime": row["Datetime Captured"],
                                "username": row["Username"],
                                "game_points": int(row["Game Points"]),
                                "difficulty": row["Difficulty Level"],
                                "current_rank": int(row["Current Rank"])
                            })
                        except ValueError:
                            print(f"Invalid data in leaderboard entry: {row}")
            except Exception as e:
                print(f"An error occurred while reading the leaderboard: {e}")
                messagebox.showerror("Error", "Failed to load leaderboard.")
                return

            if not leaderboard:
                no_entries_label = tk.Label(
                    self.root,
                    text="No entries in the leaderboard yet!",
                    font=("Comic Sans MS", 18),
                    bg="#f0f8ff",
                    fg="#ff4500"
                )
                no_entries_label.pack(pady=10)
            else:
                # Sort the leaderboard by Game Points in descending order (if not already sorted)
                leaderboard.sort(key=lambda x: x["game_points"], reverse=True)
                
                # Slice the top 10 entries
                top_leaderboard = leaderboard[:10]

                # Define a new style for the Treeview with desired font and size
                style = ttk.Style()
                style.theme_use("default")
                style.configure("Custom.Treeview",
                                font=("Arial", 14),  # Preferred font and size
                                rowheight=25)        # Adjust row height for better spacing

                # Configure the heading style
                style.configure("Custom.Treeview.Heading",
                                font=("Comic Sans MS", 16, "bold"))  # Change heading font and size

                # Create a Frame to hold the Treeview and scrollbars
                tree_frame = tk.Frame(self.root, bg="#f0f8ff")
                tree_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

                # Create a Treeview widget with the new style
                tree = ttk.Treeview(tree_frame, columns=("Rank", "Username", "Game Points", "Difficulty Level"), show='headings', style="Custom.Treeview")
                tree.heading("Rank", text="Rank")
                tree.heading("Username", text="Username")
                tree.heading("Game Points", text="Game Points")
                tree.heading("Difficulty Level", text="Difficulty Level")

                # Set column widths to accommodate more data
                tree.column("Rank", width=50, anchor='center')
                tree.column("Username", width=200, anchor='center')
                tree.column("Game Points", width=150, anchor='center')
                tree.column("Difficulty Level", width=200, anchor='center')

                # Add a vertical scrollbar
                vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                vsb.pack(side='right', fill='y')
                tree.configure(yscrollcommand=vsb.set)

                # Add a horizontal scrollbar
                hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
                hsb.pack(side='bottom', fill='x')
                tree.configure(xscrollcommand=hsb.set)

                # Insert only the top 10 entries into the Treeview
                for entry in top_leaderboard:
                    tree.insert('', 'end', values=(entry["current_rank"], entry["username"], f"{entry['game_points']}", entry["difficulty"]))

                tree.pack(pady=10, fill=tk.BOTH, expand=True)

        else:
            no_file_label = tk.Label(
                self.root,
                text="Leaderboard file not found!",
                font=("Comic Sans MS", 18),
                bg="#f0f8ff",
                fg="#ff4500"
            )
            no_file_label.pack(pady=10)

        # Button to go back to home page
        back_button = self.create_button("Back", self.show_home_page)
        back_button.pack(pady=20)

        self.center_content()

    # push leaderboard to csv file
    def save_leaderboard_to_csv(self):
        """Save the leaderboard to the CSV file with Current Rank based on Game Points."""
        headers = ['Datetime Captured', 'Username', 'Game Points', 'Difficulty Level', 'Current Rank']
        entries = []

        # Read existing entries
        if os.path.exists(self.leaderboard_path):
            try:
                with open(self.leaderboard_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        try:
                            entries.append({
                                "Datetime Captured": row["Datetime Captured"],
                                "Username": row["Username"],
                                "Game Points": int(row["Game Points"]),
                                "Difficulty Level": row["Difficulty Level"]
                            })
                        except ValueError:
                            print(f"Invalid data in leaderboard entry: {row}")
            except PermissionError as pe:
                print(f"Permission error while reading the leaderboard: {pe}")
                messagebox.showerror(
                    "Permission Error",
                    f"Cannot read the leaderboard file:\n{self.leaderboard_path}\nPlease ensure the application has read permissions to this file."
                )
                return
            except Exception as e:
                print(f"An unexpected error occurred while reading the leaderboard: {e}")
                messagebox.showerror(
                    "Error",
                    f"Failed to load leaderboard.\nError: {e}"
                )
                return

        # Add the new entry
        current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Map the display difficulty to internal representation and then back to display for consistency
        internal_difficulty = self.difficulty_mapping.get(self.difficulty, self.difficulty)
        display_difficulty = self.internal_to_display.get(internal_difficulty, self.difficulty)
        print(f"Saving leaderboard entry with Difficulty Level: {display_difficulty}")  # Optional: Remove if not needed

        new_entry = {
            "Datetime Captured": current_datetime,
            "Username": self.username,
            "Game Points": self.game_points,
            "Difficulty Level": display_difficulty
        }
        entries.append(new_entry)

        # Sort entries by Game Points in descending order
        entries.sort(key=lambda x: x["Game Points"], reverse=True)

        # Assign Current Rank
        for idx, entry in enumerate(entries, start=1):
            entry["Current Rank"] = idx

        # Write all entries back to the CSV
        try:
            with open(self.leaderboard_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                for entry in entries:
                    writer.writerow(entry)
            print("Leaderboard updated successfully with Current Rank.")  # Optional: Remove if not needed
        except PermissionError as pe:
            print(f"Permission error while writing to the leaderboard: {pe}")
            messagebox.showerror(
                "Permission Error",
                f"Cannot write to the leaderboard file:\n{self.leaderboard_path}\nPlease ensure the application has write permissions to this file."
            )
        except Exception as e:
            print(f"An unexpected error occurred while writing to the leaderboard: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to update leaderboard.\nError: {e}"
            )

    # show simple charts of the player's in-game decisions (spending overview)
    def show_spending_overview(self):
        """Display the spending overview in a pie chart."""
        # Get labels and values for the pie chart
        labels = ['Random Events', 'Quiz Earnings', 'Quiz Losses']
        sizes = [
            abs(self.spending_categories["Random Events"]), 
            self.spending_categories["Quiz Earnings"], 
            self.spending_categories["Quiz Losses"]
        ]
        colors = ['orange', 'green', 'red']

        # Handle cases where all sizes are zero to prevent errors in pie chart
        if all(size == 0 for size in sizes):
            messagebox.showinfo("Spending Overview", "No spending or earnings to display!")
            self.root.deiconify()
            return

        # Calculate percentage only for non-zero categories
        labels_filtered = []
        sizes_filtered = []
        colors_filtered = []
        for label, size, color in zip(labels, sizes, colors):
            if size > 0:
                labels_filtered.append(label)
                sizes_filtered.append(size)
                colors_filtered.append(color)

        # Calculate total for percentage
        total = sum(sizes_filtered)
        percentages = [size / total * 100 for size in sizes_filtered]

        # Prepare labels with amount and percentage
        labels_with_percent = [
            f"{label} (${size}) ({percentage:.1f}%)" 
            for label, size, percentage in zip(labels_filtered, sizes_filtered, percentages)
        ]

        # Ensure the root window doesn't show until the plot window is closed
        self.root.withdraw()

        # Create the pie chart
        fig, ax = plt.subplots()
        ax.pie(
            sizes_filtered, 
            labels=labels_with_percent, 
            colors=colors_filtered, 
            autopct='%1.1f%%',
            startangle=140
        )
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(f"Spending Overview for {self.username}")

        plt.tight_layout()
        plt.show()

        # Show the root window again after the plot is closed
        self.root.deiconify()

    # clear and reset screen
    def clear_screen(self):
        """Clear all widgets from the root window."""
        # Cancel any scheduled after callbacks
        if hasattr(self, 'timer_id'):
            self.root.after_cancel(self.timer_id)
            del self.timer_id
        for widget in self.root.winfo_children():
            widget.destroy()

    # centering a window on the screen
    def center_window(self, window):
        """Center a window on the screen."""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

   # centering content on the screen
    def center_content(self):
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")

# initialise game
if __name__ == "__main__":
    root = tk.Tk()
    game = QuizGame(root)
    root.mainloop()