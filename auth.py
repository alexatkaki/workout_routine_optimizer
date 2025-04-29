import streamlit as st
import os
import re
import json
import hashlib
from constants import PROGRESSION_LEVELS, TRAINING_GOALS, EQUIPMENT


USERS_FILE = "data/users.json"
PASSWORD_REGEX = r"^[A-Za-z0-9]{6}$"  # 6 chars, letters or numbers

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_password(password):
    return bool(re.match(PASSWORD_REGEX, password))

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            data = f.read().strip()
            if not data:
                return {}
            return json.loads(data)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_next_user_id(users):
    if not users:
        return 1
    return max(int(u["user_id"]) for u in users.values()) + 1

def login_register_page():
    st.header("🔑 Login / Register")
    users = load_users()
    tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])

    with tab1:
        login_username = st.text_input("Username:", key="login_username")
        login_password = st.text_input("Password:", type="password", key="login_password")
        if st.button("Login"):
            user = None
            for u in users.values():
                if u["username"] == login_username:
                    user = u
                    break

            if user and user["password_hash"] == hash_password(login_password):
                # Set session state for logged in user
                st.session_state["user_id"] = user["user_id"]
                st.session_state["username"] = login_username
                st.session_state["profile"] = user
                
                st.session_state["page"] = "Dashboard"
                
                st.success("Logged in successfully! Redirecting to Dashboard...")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        reg_username = st.text_input("Username:", key="reg_username")
        reg_password = st.text_input("Password (6 letters/numbers):", type="password", key="reg_password")
        
        prog_labels = [lvl["label"] for lvl in PROGRESSION_LEVELS]
        prog_values = [lvl["value"] for lvl in PROGRESSION_LEVELS]
        reg_level_label = st.selectbox("Progression Level:", prog_labels, key="reg_level")
        reg_level = prog_values[prog_labels.index(reg_level_label)]

        goal_labels = [g["label"] for g in TRAINING_GOALS]
        goal_values = [g["value"] for g in TRAINING_GOALS]
        reg_goal_label = st.selectbox("Training Goal:", goal_labels, key="reg_goal")
        reg_goal = goal_values[goal_labels.index(reg_goal_label)]

        reg_equipment = st.multiselect("Equipment:", EQUIPMENT, key="reg_equipment")

        if st.button("Register"):
            if reg_username in users:
                st.error("Username already exists.")
            elif not reg_username or not reg_password:
                st.error("Please fill out username and password.")
            elif not is_valid_password(reg_password):
                st.error("Password must be exactly 6 letters or numbers (no symbols).")
            else:
                user_id = get_next_user_id(users)
                users[str(user_id)] = {
                    "user_id": user_id,
                    "username": reg_username,
                    "password_hash": hash_password(reg_password),
                    "progression_level": reg_level,
                    "training_goal": reg_goal,
                    "equipment": reg_equipment
                }
                save_users(users)
                st.success("Registration successful! Please log in.")
                # Switch to login tab after successful registration
                st.rerun()

def check_login():
    return 'username' in st.session_state and 'user_id' in st.session_state

def profile_page(user_id):
    st.header("\U0001F464 Profile")
    
    # Check if user is logged in
    if not check_login():
        st.error("You must be logged in to view this page.")
        st.session_state["page"] = "Login"
        st.rerun()
        return
    
    if "profile" in st.session_state:
        prof = st.session_state["profile"]
        
        # Create two main tabs
        tab1, tab2 = st.tabs(["Profile Settings", "Workout Log"])
        
        with tab1:
            # Profile preferences section
            st.subheader("\U0001F4DD Edit Info")
            with st.form("profile_form"):
                username = st.text_input("Username:", value=prof.get('username', ''), disabled=True)
                
                # Progression level selection
                prog_labels = [lvl["label"] for lvl in PROGRESSION_LEVELS]
                prog_values = [lvl["value"] for lvl in PROGRESSION_LEVELS]
                prog_names = [lvl["name"] for lvl in PROGRESSION_LEVELS]
                
                try:
                    current_level_index = prog_values.index(prof.get('progression_level', prog_values[0]))
                except ValueError:
                    current_level_index = 0
                    
                level_name = st.selectbox(
                    "Progression Level:", 
                    prog_names,
                    index=current_level_index
                )
                
                # Training goal selection
                goal_labels = [g["label"] for g in TRAINING_GOALS]
                goal_values = [g["value"] for g in TRAINING_GOALS]
                
                try:
                    current_goal_index = goal_values.index(prof.get('training_goal', goal_values[0]))
                except ValueError:
                    current_goal_index = 0
                    
                goal_label = st.selectbox(
                    "Training Goal:", 
                    goal_labels,
                    index=current_goal_index
                )
                
                # Equipment selection
                equipment = st.multiselect(
                    "Equipment:", 
                    EQUIPMENT, 
                    default=prof.get('equipment', [])
                )
                
                # Submit button
                profile_submit = st.form_submit_button("Save Profile Changes")
                
                if profile_submit:
                    # Find the value corresponding to the selected name/label
                    selected_level_index = prog_names.index(level_name)
                    selected_level_value = prog_values[selected_level_index]
                    
                    selected_goal_index = goal_labels.index(goal_label)
                    selected_goal_value = goal_values[selected_goal_index]
                    
                    # Update the profile in session state
                    st.session_state["profile"].update({
                        'progression_level': selected_level_value,
                        'training_goal': selected_goal_value,
                        'equipment': equipment
                    })
                    
                    # Save the updated profile to users.json
                    users = load_users()
                    user_id = str(st.session_state["user_id"])
                    if user_id in users:
                        users[user_id].update(st.session_state["profile"])
                        save_users(users)
                        st.success("Profile updated successfully!")
                    else:
                        st.error("Failed to save profile changes. User not found.")
            
            st.markdown("---")
            
            # Password change section
            st.subheader("\U0001F510 Change Password")
            with st.form("password_form"):
                current_password = st.text_input("Current Password:", type="password")
                new_password = st.text_input("New Password (6 letters/numbers):", type="password")
                confirm_password = st.text_input("Confirm New Password:", type="password")
                
                password_submit = st.form_submit_button("Update Password")
                
                # Process password change if requested
                if password_submit:
                    if not (current_password and new_password and confirm_password):
                        st.error("All password fields are required.")
                    elif hash_password(current_password) != prof.get('password_hash', ''):
                        st.error("Current password is incorrect.")
                    elif new_password != confirm_password:
                        st.error("New passwords don't match.")
                    elif not is_valid_password(new_password):
                        st.error("Password must be exactly 6 letters or numbers (no symbols).")
                    else:
                        # Update password
                        st.session_state["profile"]["password_hash"] = hash_password(new_password)
                        
                        # Save the updated profile to users.json
                        users = load_users()
                        user_id = str(st.session_state["user_id"])
                        if user_id in users:
                            users[user_id].update(st.session_state["profile"])
                            save_users(users)
                            st.success("Password updated successfully!")
                        else:
                            st.error("Failed to save password. User not found.")
        
        with tab2:
            st.subheader("📋 Workout Log")
            
            # Load workout history from the same file the dashboard uses
            history_path = os.path.join("data", "workout_history.json")
            
            try:
                if os.path.exists(history_path):
                    with open(history_path, "r") as f:
                        workout_history = json.load(f)
                else:
                    workout_history = []
            except Exception as e:
                st.error(f"Error loading workout history: {str(e)}")
                workout_history = []
            
            # Filter workout history for current user
            user_id = st.session_state.get('user_id')
            user_workouts = [w for w in workout_history if w.get('user_id') == user_id]
            
            if not user_workouts:
                st.info("You haven't saved any workouts yet. Generate a workout and save it to see it here!")
                if st.button("Generate a New Workout"):
                    st.session_state["page"] = "Generate Workout"
                    st.rerun()
                return
            
            # Display workouts in reverse chronological order (newest first)
            for workout in sorted(user_workouts, key=lambda x: x.get('date', ''), reverse=True):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Get workout type with fallback
                        routine_type = workout.get('workout_type', workout.get('routine_name', 'Unnamed Workout'))
                        
                        # Extract unique levels from all exercises
                        exercise_levels = []
                        for exercise in workout.get('exercises', []):
                            level = exercise.get('level')
                            if level and level not in exercise_levels:
                                exercise_levels.append(level)
                        
                        # Sort levels for consistent display
                        exercise_levels.sort()
                        
                        # Format the display string
                        if exercise_levels:
                            level_str = " | ".join(exercise_levels)
                            formatted_name = f"{routine_type} - {level_str}"
                        else:
                            formatted_name = routine_type
                        
                        st.write(f"**{formatted_name}**")
                        
                        # Display exercises
                        exercises = workout.get('exercises', [])
                        if exercises:
                            exercise_names = [ex.get('name', 'Unknown Exercise') for ex in exercises]
                            st.write(f"Exercises: {', '.join(exercise_names)}")
                    
                    with col2:
                        # Display duration and date
                        duration = workout.get('workout_duration', workout.get('duration_min', ''))
                        if duration:
                            st.write(f"{duration}min")
                        
                        # Format date
                        date_str = workout.get('date', '')
                        if date_str:
                            try:
                                from datetime import datetime
                                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                st.write(date_obj.strftime('%Y-%m-%d'))
                            except:
                                st.write(date_str)

    
    else:
        st.write("Profile data not found. Please log in again.")
        st.session_state["page"] = "Login"
        st.rerun()

    