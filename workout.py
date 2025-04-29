import os
import sys
import stat
import json
import random
import logging
import traceback
import streamlit as st
from datetime import datetime, timedelta
from data_structures import ExerciseHashTable, ProgressionLinkedList, WorkoutHistoryStack
from constants import MUSCLE_GROUPS_COMB, PROGRESSION_LEVELS, TRAINING_GOALS, EQUIPMENT, EXERCISES, PROGRESSION_LEVELS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
history_path = os.path.join(BASE_DIR, "data", "workout_history.json")
logging.info(f"history_path: {history_path}")


# Load motivational quotes from JSON file
quotes_path = os.path.join(BASE_DIR, "data", "motivational_quote.json")
with open(quotes_path, "r") as f:
    motivational_quotes = json.load(f)


# Load workout history from JSON file
try:
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            workout_history = json.load(f)
    else:
        workout_history = []
        # Create the file with an empty array
        with open(history_path, "w") as f:
            json.dump([], f)
except Exception as e:
    logging.error(f"Error loading workout history: {str(e)}")
    workout_history = []

# Load exercise data from JSON file
exercises_path = os.path.join(BASE_DIR, "data", "exercises.json")
with open(exercises_path, "r") as f:
    data = json.load(f)
    # Extract the exercises list from the data dictionary
    all_exercises = data["exercises"]

# Create a lookup dictionary for quick access by exercise name
exercise_lookup = {exercise["name"]: exercise for exercise in all_exercises}


# For Debugging
# print(f"Type of all_exercises: {type(all_exercises)}")
# print(f"First item: {all_exercises[0] if isinstance(all_exercises, list) and len(all_exercises) > 0 else all_exercises}")


## Global fn ##
# Pick a random quote
def get_random_quote():
    return random.choice(motivational_quotes)


# Helper functions 
def get_user_profile(user_id):
    """Load user profile from the main users file"""
    try:
        with open(os.path.join("data", "users.json"), "r") as f:
            all_users = json.load(f)
        
        # Get user by ID, converting to str as JSON keys are
        user_data = all_users.get(str(user_id))
        
        if user_data:
            return user_data
        else:
            # Return default if user not found
            return {
                "user_id": user_id,
                "progression_level": user_data.PROGRESSION_LEVELS,
                "training_goal": user_data.TRAINING_GOALS[3]["value"],
                "equipment": ["Bodyweight"]
            }
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default profile if file issues
        return {
            "user_id": user_id,
            "progression_level": PROGRESSION_LEVELS[0]["value"],
            "training_goal": TRAINING_GOALS[3]["value"],
            "equipment": ["Bodyweight"]
        }


def get_exercise_progress_indicator(user_id, exercise_name):
    """
    Returns an emoji indicator based on user's history with an exercise:
    🏆 - Completed 3+ times
    ❤️‍🔥 - Completed 1-2 times
    🔜 - Never completed
    
    Args:
        user_id (int): The current user's ID
        exercise_name (str): Name of the exercise to check
    
    Returns:
        str: Emoji indicator
    """
    try:
        # Load workout history
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                history = json.load(f)
        else:
            return "🔜"  # No history file means no completed exercises
        
        # Count occurrences of this exercise for this user
        count = 0
        for workout in history:
            if workout.get("user_id") == user_id:
                for exercise in workout.get("exercises", []):
                    if exercise.get("name") == exercise_name:
                        count += 1
        
        # Return appropriate emoji
        if count >= 3:
            return "🏆"
        elif count > 0:
            return "❤️‍🔥"
        else:
            return "🔜"
    except Exception as e:
        logging.error(f"Error checking exercise progress: {e}")
        return ""  # Return empty string if there's an error
    
    
## Generate Workout ##
def generate_workout_page(user_id):
    st.header("⚡ Generate Workout Routine")
    
    # Initialize session state for workout data if not exists
    if "current_workout" not in st.session_state:
        st.session_state.current_workout = None
    if "save_status" not in st.session_state:
        st.session_state.save_status = None
    
    try:
        # Get user profile data
        user_profile = get_user_profile(user_id)
        # Get pre-set values from user profile
        progression_level = user_profile.get("progression_level", "Beginner 1")
        training_goal = user_profile.get("training_goal", "Strength")
        available_equipment = user_profile.get("equipment", ["Bodyweight"])
        
        # Convert IDs to display labels
        level_label = next((level["name"] for level in PROGRESSION_LEVELS if level["value"] == progression_level), progression_level)
        goal_label = next((goal["label"].split(" (")[0] for goal in TRAINING_GOALS if goal["value"] == training_goal), training_goal)
        
        # Add muscle focus dropdown using MUSCLE_GROUPS_COMB
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Focus Muscle Groups")
            muscle_focus = st.selectbox(
                label="Focus Muscle Groups",
                options=[group["name"] for group in MUSCLE_GROUPS_COMB],
                index=0,
                label_visibility="collapsed"
            )
        
        # Get the selected muscle group combination
        selected_group = next((g for g in MUSCLE_GROUPS_COMB if g["name"] == muscle_focus), MUSCLE_GROUPS_COMB[0])
        focus_muscles = selected_group["muscle_groups"]
        
        # Add workout duration slider
        with col2:
            st.write("Workout Duration (minutes)")
            duration = st.slider(
                label="Workout Duration (minutes)",
                min_value=15,
                max_value=90,
                value=35,
                label_visibility="collapsed"
            )
        
        # Check duration constraints
        duration_warning = None
        min_duration = 0
        
        if len(focus_muscles) >= 5 and duration < 50:
            duration_warning = "For 5+ muscle groups, a minimum of 50 minutes is recommended. Adjusting duration..."
            min_duration = 50
        elif len(focus_muscles) >= 3 and duration < 40:
            duration_warning = "For 3+ muscle groups, a minimum of 40 minutes is recommended. Adjusting duration..."
            min_duration = 40
        
        # Generate button
        if st.button("Generate Workout Routine", type="primary", key="generate_btn"):
            # Reset save status
            st.session_state.save_status = None
            
            # Check if duration warning exists and adjust duration
            if duration_warning:
                st.warning(duration_warning)
                duration = min_duration
            
            # Create workout parameters
            workout_params = {
                "user_id": user_id,
                "progression_level": progression_level,
                "training_goal": training_goal,
                "equipment": available_equipment,
                "level_name": level_label,
                "goal_label": goal_label
            }
            
            # Generate the workout
            workout = generate_workout(workout_params, focus_muscles, duration)
            
            if "error" in workout:
                st.error(workout["error"])
                return
            
            # Store the workout in session state for saving later
            st.session_state.current_workout = {
                "workout": workout,
                "muscle_focus": muscle_focus,
                "level_label": level_label,
                "goal_label": goal_label,
                "duration": duration,
                "focus_muscles": focus_muscles
            }
        
        # Display workout if available in session state
        if st.session_state.current_workout:
            workout = st.session_state.current_workout["workout"]
            muscle_focus = st.session_state.current_workout["muscle_focus"]
            level_label = st.session_state.current_workout["level_label"]
            goal_label = st.session_state.current_workout["goal_label"]
            duration = st.session_state.current_workout["duration"]
            focus_muscles = st.session_state.current_workout["focus_muscles"]
            
            # Display the workout
            st.subheader(f"Your {muscle_focus} Workout")
            st.write(f"Level: {level_label} | Goal: {goal_label} | Duration: ~{duration} minutes")
            
            # Check for progression messages
            has_progression = any("progression_message" in exercise for exercise in workout["exercises"])
            
            if has_progression:
                # Create progression message text
                new_exercises = []
                for exercise in workout["exercises"]:
                    if "progression_message" in exercise:
                        new_exercises.append(f"- {exercise['name']} ({exercise['difficulty']})")
                
                progression_text = "🔥 Time to push your limit with a new exercise! " + ", ".join(new_exercises)
                
                # Display progression message instead of motivational quote
                with st.container(border=True):
                    st.info(progression_text)
            else:
                # Display motivational quote if no progression
                quote = get_random_quote()
                with st.container(border=True):
                    st.info(f"💪💪 {quote}")
                        
            # Display training tip
            if workout.get("messages"):
                with st.container(border=True):
                    st.info(f"💡{workout['messages'][0]}")
            
            # Create exercise cards
            for i, exercise in enumerate(workout["exercises"], 1):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([1, 3, 4])
                    full_exercise_data = exercise_lookup.get(exercise['name'])
                    with col1:
                        st.markdown(f"### {i}.")
                    with col2:
                        st.markdown(f"### {exercise['name']}")
                        st.write(f"**Sets:** {exercise['sets']} | **Reps:** {exercise['reps']} | **Rest:** {exercise['rest_sec']}s")
                        st.write(f"**Targets:** {', '.join(exercise['muscle_groups'])}")
                        
                        if 'equipment' in full_exercise_data and full_exercise_data['equipment']:
                            st.write(f"**Equipment:** {(full_exercise_data['equipment'])}")
                            
                        # Show progression message if available
                        if "progression_message" in exercise:
                            st.success(exercise["progression_message"])
                    with col3:
                        st.markdown("**Instructions**")
                        
                        # Look up the full exercise data from our dictionary
                        full_exercise_data = exercise_lookup.get(exercise['name'])
                        
                        if full_exercise_data and "instructions" in full_exercise_data and full_exercise_data["instructions"]:
                            for step in full_exercise_data["instructions"]:
                                st.write(step)
                        else:
                            st.write("No instructions available")
                            
                        if 'tips' in full_exercise_data and full_exercise_data['tips']:
                            st.write(f"**Tips:** {(full_exercise_data['tips'])}")
            
            # Display save button and status message
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Save Workout", type="primary", key="save_btn"):
                    try:
                        # Format exercises for saving in the format expected by save_workout()
                        formatted_exercises = []
                        all_equipment = []
                        
                        for ex in workout["exercises"]:
                            ex_data = exercise_lookup.get(ex['name'], {})
                            
                            # Get equipment and add to all_equipment list
                            equipment = ex_data.get('equipment', "Bodyweight")
                            if isinstance(equipment, str):
                                all_equipment.append(equipment)
                            else:
                                all_equipment.extend(equipment)
                            
                            # Format instructions
                            instructions = ex_data.get('instructions', [])
                            if isinstance(instructions, str):
                                instructions = [instructions]
                            
                            # Format tips
                            tips = ex_data.get('tips', [])
                            if isinstance(tips, str):
                                tips = [tips]
                            
                            # Create exercise record in the format expected by save_workout()
                            exercise_record = {
                                "name": ex['name'],
                                "level": ex.get('difficulty', level_label),
                                "sets": ex['sets'],
                                "reps": ex['reps'],
                                "rest_seconds": ex['rest_sec'],
                                "muscle_groups": ex['muscle_groups'],
                                "equipment": equipment,
                                "instructions": instructions,
                                "tips": tips
                            }
                            formatted_exercises.append(exercise_record)
                        
                        # Create tips list from workout messages
                        tips = []
                        if workout.get("messages"):
                            for msg in workout["messages"]:
                                tips.append({"text": msg})
                        
                        # Format workout data for save_workout()
                        workout_data = {
                            "workout_type": f"{muscle_focus} Workout",
                            "workout_duration": duration,
                            "focus_areas": focus_muscles,
                            "equipment": list(set(all_equipment)),  # Remove duplicates
                            "exercises": formatted_exercises,
                            "tips": tips
                        }
                        
                        # Save the workout using the existing save_workout function
                        save_success = save_workout(user_id, workout_data)
                        st.session_state.save_status = "success" if save_success else "error"
                    except Exception as e:
                        logging.error(f"Error saving workout: {str(e)}")
                        logging.error(traceback.format_exc())
                        st.session_state.save_status = "error"
            
            # Show save status message
            with col2:
                if st.session_state.save_status == "success":
                    st.success("Workout saved successfully! You can view it in your workout history.")
                elif st.session_state.save_status == "error":
                    st.error("Failed to save workout. Please try again.")

    except Exception as e:
        logging.error(f"Error in generate_workout_page: {str(e)}")
        logging.error(traceback.format_exc())
        st.error(f"An error occurred: {str(e)}")

# Core Workout Generation Logic
def generate_workout(user_profile, focus_muscles, duration, workout_history=None):
    """
    Generate a workout routine based on user profile and preferences

    Parameters:
    - user_profile: User's profile with level, goals, equipment
    - focus_muscles: List of muscle groups to focus on
    - duration: Workout duration in minutes
    - workout_history: Optional workout history stack
    
    Returns:
    - Workout routine with exercises, sets, reps, rest times
    """
    # Validate duration based on muscle group count
    if len(focus_muscles) >= 5 and duration < 50:
        return {"error": "For 5+ muscle groups, minimum duration is 50 minutes"}
    elif len(focus_muscles) >= 3 and duration < 30:
        return {"error": "For 3+ muscle groups, minimum duration is 30 minutes"}
    
    # Initialize data structures if not yet done
    exercise_table, progression_lists = initialize_data_structures()
    
    # If no workout history provided, create empty one
    if workout_history is None:
        workout_history = WorkoutHistoryStack()
    
    # Filter exercises by equipment
    available_equipment = user_profile.get("equipment", ["Bodyweight"])
    if not available_equipment:
        available_equipment = ["Bodyweight"]
    
    # Use the constant EXERCISES instead of filtered_exercises
    filtered_exercises = []
    for exercise in EXERCISES:
        # Check if any of the user's equipment matches any of the exercise's equipment
        if any(eq in available_equipment for eq in exercise["equipment"]):
            # Create a copy to avoid modifying the original
            exercise_copy = exercise.copy()
            # Add default values
            if "default_sets" not in exercise_copy:
                exercise_copy["default_sets"] = 3
            if "default_reps" not in exercise_copy:
                exercise_copy["default_reps"] = 10
            if "default_rest_sec" not in exercise_copy:
                exercise_copy["default_rest_sec"] = 60
            if "id" not in exercise_copy:
                exercise_copy["id"] = exercise_copy["name"].lower().replace(" ", "_")
            if "level" not in exercise_copy:
                exercise_copy["level"] = "Beginner"
            
            filtered_exercises.append(exercise_copy)
    
    # Filter by muscle groups
    muscle_filtered = [e for e in filtered_exercises if any(m in e["muscle_groups"] for m in focus_muscles)]
    
    # If no exercises match the criteria, return error
    if not muscle_filtered:
        return {"error": "No exercises found matching your equipment and muscle focus. Try different options."}
    
    # Group exercises by muscle group
    muscle_group_exercises = {}
    for muscle in focus_muscles:
        muscle_group_exercises[muscle] = [e for e in muscle_filtered if muscle in e["muscle_groups"]]
    
    # Select exercises based on level and progression
    selected_exercises = []
    
    # Get the user's level name - use the one passed in the user_profile if available
    user_level_name = user_profile.get("level_name", "Beginner 1")
    
    # Determine how many exercises to include based on duration
    # Roughly 10-15 minutes per exercise including rest
    target_exercise_count = max(2, min(8, duration // 12))
    
    # Distribute exercises across muscle groups
    exercises_per_group = max(1, target_exercise_count // len(focus_muscles))
    
    for muscle, exercises in muscle_group_exercises.items():
        if not exercises:
            continue
        
        # Select exercises for this muscle group
        for _ in range(min(exercises_per_group, len(exercises))):
            if not exercises:
                break
                
            # Choose a random exercise for this muscle group
            selected = random.choice(exercises)
            
            # Remove from list to avoid duplicates
            exercises.remove(selected)
            
            # Add to selected exercises
            if selected not in selected_exercises:  # Double-check to avoid duplicates
                selected_exercises.append(selected)
    
    # If we still need more exercises to reach target count
    while len(selected_exercises) < target_exercise_count and muscle_filtered:
        # Choose a random exercise from all filtered exercises
        remaining = [e for e in muscle_filtered if e not in selected_exercises]
        if not remaining:
            break
            
        selected = random.choice(remaining)
        selected_exercises.append(selected)
    
    # Adjust sets/reps based on training goal
    training_goal = user_profile.get("training_goal", "General Fitness")
    adjust_sets_reps_by_goal(selected_exercises, training_goal)
    
    # Get the goal label - use the one passed in the user_profile if available
    goal_label = user_profile.get("goal_label", training_goal)
    
    # Generate tip message
    training_tip = get_training_tip(training_goal)
    
    # Create final workout with formatted exercise details
    formatted_exercises = []
    for exercise in selected_exercises:
        # Create a formatted version of each exercise with the adjusted values
        formatted_exercise = exercise.copy()
        
        # Ensure the adjusted values are included in the formatted exercise
        if "sets" not in formatted_exercise:
            formatted_exercise["sets"] = formatted_exercise.get("default_sets", 3)
        if "reps" not in formatted_exercise:
            formatted_exercise["reps"] = formatted_exercise.get("default_reps", 10)
        if "rest_sec" not in formatted_exercise:
            formatted_exercise["rest_sec"] = formatted_exercise.get("default_rest_sec", 60)
        
        
        if "instructions" in exercise:
            formatted_exercise["instructions"] = exercise["instructions"]
            
        # Add a formatted display string for the exercise
        is_timed = formatted_exercise.get("is_timed", False)
        if is_timed:
            formatted_exercise["display"] = f"{formatted_exercise['sets']} sets × {formatted_exercise['reps']} seconds, {formatted_exercise['rest_sec']}s rest"
        else:
            formatted_exercise["display"] = f"{formatted_exercise['sets']} sets × {formatted_exercise['reps']} reps, {formatted_exercise['rest_sec']}s rest"
            
        formatted_exercises.append(formatted_exercise)
    
    workout = {
        "user_id": user_profile.get("user_id", "default_user"),
        "date": datetime.now().isoformat(),
        "routine_name": f"{', '.join(focus_muscles[:2])} Workout",
        "focus_muscles": focus_muscles,
        "level": user_level_name,
        "duration_min": duration,
        "equipment": list(set([item for exercise in selected_exercises for item in exercise["equipment"]])),
        "training_goal": goal_label,
        "messages": [training_tip],
        "exercises": formatted_exercises
    }
    
    return workout

# Save generated routine to workout_history.json    
def save_workout(user_id, workout_data):
    try:
        # Load users data
        users_path = os.path.join(BASE_DIR, "data", "users.json")
        with open(users_path, "r") as f:
            users_data = json.load(f)
        
        # Convert user_id to string for dictionary lookup
        user_id_str = str(user_id)
        
        # Check if user exists
        if user_id_str not in users_data:
            logging.error(f"User ID {user_id} not found in users database")
            return False
        
        # Add timestamp and user_id to workout data
        workout_data["user_id"] = int(user_id)
        workout_data["date"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        # Load existing workout history
        with open(history_path, "r") as f:
            workout_history = json.load(f)
        
        # Add new workout to history
        workout_history.append(workout_data)
        
        # Save updated history
        with open(history_path, "w") as f:
            json.dump(workout_history, f, indent=2)
        
        return True
        
    except Exception as e:
        logging.error(f"Error saving workout: {str(e)}")
        logging.error(traceback.format_exc())
        return False


## Exercise library ##
def get_exercise_library(muscle_groups=None, equipment=None, progression_level=None, category=None):
    # Load exercises from the JSON file
    exercises_path = os.path.join(BASE_DIR, "data", "exercises.json")
    
    # Load the exercises
    with open(exercises_path, "r") as f:
        exercises_data = json.load(f)
    
    # Get the exercises list
    exercises = exercises_data["exercises"]
    
    # Add progression level label to each exercise
    for exercise in exercises:
        prog_value = exercise.get("progression_level", "")
        # Find matching progression level label
        for level in PROGRESSION_LEVELS:
            if level["value"] == prog_value:
                exercise["progression_label"] = level["label"].split(" - ")[1]  # Just get "Beginner 1" part
                break
        else:
            exercise["progression_label"] = "Unknown"
    
    # Apply filters if provided
    filtered_exercises = exercises
    
    if muscle_groups:
        filtered_exercises = [
            ex for ex in filtered_exercises 
            if any(mg in ex["muscle_groups"] for mg in muscle_groups)
        ]
    
    if equipment:
        filtered_exercises = [
            ex for ex in filtered_exercises 
            if ex["equipment"] in equipment
        ]
    
    if progression_level:
        filtered_exercises = [
            ex for ex in filtered_exercises 
            if ex["progression_level"] in progression_level
        ]
    
    if category:
        filtered_exercises = [
            ex for ex in filtered_exercises 
            if ex["category"] == category
        ]
    
    return filtered_exercises

# Training goal-specific tips
def get_training_tip(training_goal):
    tips = {
        "Maintaining/Bulking": [
            " Stay hydrated. For muscle gain, eat protein and carbs within 30 minutes after your workout.",
            " Focus on progressive overload - gradually increase weight or reps to continue building muscle.",
            " Aim for 1.6-2.2g of protein per kg of bodyweight daily to support muscle growth.",
            " Don't skip rest days! Muscles grow during recovery, not during workouts.",
            " For bulking, ensure you're in a caloric surplus of 250-500 calories above maintenance."
        ],
        "Cutting/Weight Loss": [
            " Keep protein high while cutting to preserve muscle mass during weight loss.",
            " Circuit training with minimal rest maximizes calorie burn during and after workouts.",
            " Stay in a moderate caloric deficit (300-500 calories) for sustainable fat loss.",
            " Consider fasted cardio in the morning for enhanced fat utilization.",
            " Track your calories and maintain a high protein intake to prevent muscle loss while cutting."
        ],
        "Strength": [
            " Focus on compound movements and progressive overload for maximum strength gains.",
            " Don't rush between sets - full recovery (2-5 minutes) is essential for maximal strength output.",
            " Proper form is crucial for strength training - prioritize technique over weight.",
            " Consider creatine supplementation - it's well-researched for improving strength performance.",
            " Track your lifts to ensure progressive overload - aim to increase weight by 2.5-5% when possible."
        ],
        "General Fitness": [
            " Consistency beats intensity - regular moderate workouts produce better results than occasional intense ones.",
            " Mix cardio and resistance training for well-rounded fitness improvements.",
            " Stay hydrated before, during, and after your workout for optimal performance.",
            " Listen to your body - push yourself but recognize when you need rest or recovery.",
            " For overall fitness, aim for a balanced diet with adequate protein and plenty of fruits and vegetables."
        ]
    }
    
    # Default to General Fitness if goal not found
    goal_tips = tips.get(training_goal, tips["General Fitness"])
    
    # Return a random tip for the selected goal
    return random.choice(goal_tips)

# Initialize workout data structures
def initialize_data_structures():
    """Initialize exercise data structures"""
    # Use the EXERCISES constant instead of loading from file if available
    exercises = EXERCISES
    
    # Create hash table for quick lookups
    exercise_table = ExerciseHashTable()
    
    # Create progression linked list
    progression_lists = ProgressionLinkedList()
    
    for exercise in exercises:
        # Add default values if not present
        if "default_sets" not in exercise:
            exercise["default_sets"] = 3
        if "default_reps" not in exercise:
            exercise["default_reps"] = 10
        if "default_rest_sec" not in exercise:
            exercise["default_rest_sec"] = 60
        if "id" not in exercise:
            exercise["id"] = exercise["name"].lower().replace(" ", "_")
        if "level" not in exercise:
            exercise["level"] = "Beginner"
            
        exercise_table.add_exercise(exercise)
        
    return exercise_table, progression_lists

# Adjust sets/reps based on training goal
def adjust_sets_reps_by_goal(exercises, training_goal):
    """
    Adjust sets, reps, and rest times based on training goal
    
    Args:
        exercises: List of exercises to adjust
        training_goal: The user's training goal
    """
    for exercise in exercises:
        if training_goal == "Maintaining/Bulking":
            # Higher volume for muscle growth
            exercise["sets"] = exercise.get("default_sets", 3) + 1
            exercise["reps"] = max(8, exercise.get("default_reps", 10) - 2)  # Moderate reps
            exercise["rest_sec"] = 90  # Moderate rest
        
        elif training_goal == "Cutting/Weight Loss":
            # Higher reps, shorter rest for calorie burn
            exercise["sets"] = exercise.get("default_sets", 3)
            exercise["reps"] = exercise.get("default_reps", 10) + 5  # Higher reps
            exercise["rest_sec"] = 30  # Short rest
        
        elif training_goal == "Strength":
            # Lower reps, longer rest for strength
            exercise["sets"] = exercise.get("default_sets", 3) + 1
            exercise["reps"] = max(5, exercise.get("default_reps", 10) - 5)  # Lower reps
            exercise["rest_sec"] = 120  # Longer rest
        
        else:  # General Fitness
            # Default values
            exercise["sets"] = exercise.get("default_sets", 3)
            exercise["reps"] = exercise.get("default_reps", 10)
            exercise["rest_sec"] = exercise.get("default_rest_sec", 60)