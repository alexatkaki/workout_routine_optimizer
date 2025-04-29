import os
import json
import random
import streamlit as st
from datetime import datetime
from auth import login_register_page, profile_page
from workout import get_exercise_progress_indicator
from workout import get_random_quote, history_path, generate_workout_page, save_workout, get_exercise_library
from constants import MUSCLE_GROUPS_COMB, PROGRESSION_LEVELS, TRAINING_GOALS, EQUIPMENT, MUSCLE_GROUPS

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Dashboard'
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.session_state['page'] = 'Login'
        

def main():
    # Initialize session state
    init_session_state()
    
    # Check if user is logged in
    if 'user_id' not in st.session_state and st.session_state['page'] != 'Login':
        set_page('Login')
        return
    
    # Show sidebar only if logged in
    if st.session_state.get('user_id'):
        show_sidebar()
    
    # Show main content area
    show_main_area()
    

def show_sidebar():
    """Display the sidebar navigation menu"""
    with st.sidebar:
        # Logo
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=60)
        else:
            st.title("WORKOUT ROUTINE")
            
        # User greeting if logged in
        if 'username' in st.session_state:
            st.write(f"👋 Hello, {st.session_state['username']}!")
            
        # st.markdown("---")
        
        # Navigation menu
        menu_items = {
            "Dashboard": "🏠",
            "Generate Workout": "⚡",
            "Exercise Library": "📚",
            "Progression Pathways": "📈",
            "Profile": "👤",
            "About & Sources": "ℹ️"
        }
        
        
        st.markdown("""
        <style>
            .stButton button {
                text-align: left !important;
                justify-content: flex-start !important;
                padding-left: 1rem !important;
            }
            .stButton button p {
                font-size: 1rem !important;
            }
            .logout-btn button {
                background-color: #ff4b4b !important;
                color: white !important;
            }
            .logout-btn button:hover {
                background-color: #ff3333 !important;
            }
        </style>
        """, unsafe_allow_html=True)

        # Display navigation buttons
        current_page = st.session_state.get('page')
        for page_name, icon in menu_items.items():
            button_type = "primary" if current_page == page_name else "secondary"
            
            with st.sidebar.container():
                if st.button(f"{icon} {page_name}", key=f"nav_{page_name}", 
                        use_container_width=True, type=button_type):
                    st.session_state['page'] = page_name
                    st.query_params["page"] = page_name
                    st.rerun()

        with st.sidebar.container():
            st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
            if st.button("🚪 Logout", use_container_width=True):
                # Clear session state but preserve certain app settings if needed
                for key in list(st.session_state.keys()):
                    if key not in ['app_settings']:
                        del st.session_state[key]
                st.session_state['page'] = 'Login'
                st.query_params["page"] = "Login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# Page routing
def show_main_area():
    """Display the main content area based on selected page"""
    user_id = st.session_state.get('user_id')
    page = st.session_state.get('page', 'Dashboard')
    
    # Routing
    if page == "Login":
        login_register_page()
    elif page == "Dashboard":
        dashboard_page(user_id)
    elif page == "Generate Workout":
        generate_workout_page(user_id)
    elif page == "Exercise Library":
        exercise_library_page(user_id)
    elif page == "Progression Pathways":
        progression_pathways_page(user_id)
    elif page == "Profile":
        profile_page(user_id)
    elif page == "About & Sources":
        about_sources_page(user_id)
    else:
        st.error(f"Page '{page}' not found.")
        st.button("Return to Dashboard", on_click=lambda: set_page("Dashboard"))


def set_page(page_name):
    """Helper function to set the current page"""
    st.session_state['page'] = page_name
    st.rerun()


def get_user_settings(user_id):
    """Get settings for a specific user"""
    # TBD -  load this from a database
    return st.session_state.get('user_settings', {})


def update_user_settings(user_id, settings):
    """Update settings for a specific user"""
    # TBD - save this to a database
    st.session_state['user_settings'] = settings
    return True


# Image File Handling
def get_image_path(filename):
    """Get the correct path for an image in Streamlit"""
    # For local development
    local_path = os.path.join("assets", "images", filename)
    if os.path.exists(local_path):
        return local_path
    
    # For deployed app
    return os.path.join(".", "assets", "images", filename)


## Dashboard ##
def dashboard_page(user_id):
    st.header("🏠 Dashboard")
    quote = get_random_quote()
    
    # Reload workout history from file to get latest data
    with open(history_path, "r") as f:
        current_workout_history = json.load(f)
            
    user_workouts = [w for w in current_workout_history if w.get('user_id') == user_id]
    total_workouts = len(user_workouts)
    
    streak = get_streak(user_id, current_workout_history)

    st.markdown(f'💬 {quote}')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Workouts", total_workouts)
    with col2:
        st.metric("Current Streak", f"{streak} days")
    with col3:
        st.metric("Weekly Goal", f"{min(total_workouts, 5)}/5")
    
    # Quick action btn
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Let's Workout", use_container_width=True):
            st.session_state.page = "Generate Workout"
            st.rerun()
    with col2:
        if st.button("📚 Exercise Library", use_container_width=True):
            st.session_state.page = "Exercise Library"
            st.rerun()
    
    st.subheader("🕒 Recent Workouts")
    
    recent = get_recent_workouts(user_id)
    if recent:
        for workout in recent:
            dt = datetime.strptime(workout.get('date', datetime.now().strftime("%Y-%m-%dT%H:%M:%S")), 
                                "%Y-%m-%dT%H:%M:%S")
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Display routine name with fallback
                    routine_type = workout.get('workout_type', 'Unnamed Workout')
                    
                    # Extract unique levels from all exercises
                    exercise_levels = []
                    for exercise in workout.get('exercises', []):
                        level = exercise.get('level')
                        if level and level not in exercise_levels:
                            exercise_levels.append(level)
                    
                    # Sort levels (optional, for consistent display)
                    exercise_levels.sort()
                    
                    # Format the display string
                    if exercise_levels:
                        level_str = " | ".join(exercise_levels)
                        formatted_name = f"{routine_type} - {level_str}"
                    else:
                        formatted_name = routine_type
                        
                    st.write(f"**{formatted_name}**")
                    
                    # Display muscle groups if available
                    muscle_groups = workout.get('train', {}).get('muscle_groups', [])
                    if muscle_groups:
                        if isinstance(muscle_groups, list):
                            st.write(f"Targets: {', '.join(muscle_groups)}")
                        else:
                            st.write(f"Targets: {muscle_groups}")
                    
                    # Display exercises if available
                    exercises = workout.get('exercises', [])
                    if exercises:
                        exercise_names = [ex.get('name', 'Unknown') for ex in exercises]
                        if exercise_names:
                            st.write(f"**Exercises:** {', '.join(exercise_names[:3])}" + 
                                    ("..." if len(exercise_names) > 3 else ""))
                
                with col2:
                    # Display duration with fallback
                    duration = workout.get('workout_duration', 0)
                    st.write(f"**{duration}min**")
                    st.write(f"{dt.strftime('%Y-%m-%d')}")
    else:
        st.info("No recent workouts found. Time to get started!")

# Recent workout - dashboard
def get_recent_workouts(user_id, limit=3):
    """Get the most recent workouts for a user."""
    try:
        # Load workout history
        with open(history_path, "r") as f:
            workout_history = json.load(f)
        
        # Filter workouts for the current user
        user_workouts = [w for w in workout_history if w.get('user_id') == user_id]
        
        # Sort by date in descending order (newest first)
        def parse_date(date_str):
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return datetime.min
        
        sorted_workouts = sorted(
            user_workouts,
            key=lambda w: parse_date(w.get('date', '')),
            reverse=True
        )
        
        #  Limit number of workouts
        return sorted_workouts[:limit]
    
    except Exception as e:
        print(f"Error getting recent workouts: {str(e)}")
        return []

# Streak logic - dashboard
def get_streak(user_id, workout_history_data=None):
    """
    Calculate the current workout streak for a user.
    Returns the number of consecutive days with workouts.
    """
    # Use provided data or load from file
    if workout_history_data is None:
        try:
            with open(history_path, "r") as f:
                workout_history_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0
            
    # Get unique workout dates for user, sorted descending
    user_workouts = [w for w in workout_history_data if w.get('user_id') == user_id]
    dates = sorted({w['date'][:10] for w in user_workouts}, reverse=True)
    
    if not dates:
        return 0
        
    streak = 0
    today = datetime.now().date()
    
    for i, d in enumerate(dates):
        day = datetime.strptime(d, "%Y-%m-%d").date()
        
        if i == 0:
            # If last workout was today or yesterday, start streak
            if (today - day).days > 1:
                break
        else:
            prev_day = datetime.strptime(dates[i-1], "%Y-%m-%d").date()
            if (prev_day - day).days != 1:
                break
        streak += 1
    
    return streak

def update_user_stats(user_id, workout):
    """Update user statistics after completing a workout"""
    stats_path = os.path.join("data", f"user_{user_id}_stats.json")
    
    try:
        with open(stats_path, "r") as f:
            stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats = {
            "total_workouts": 0,
            "current_streak": 0,
            "last_workout_date": None,
            "weekly_goal": 5,
            "weekly_completed": 0,
            "week_start_date": datetime.now().strftime("%Y-%m-%d"),
            "today_counted": False
        }
    
    # Update total workouts
    stats["total_workouts"] += 1
    
    # Update last workout date
    today = datetime.now().strftime("%Y-%m-%d")
    stats["last_workout_date"] = today
    
    # Use get_streak() for consistent streak calculation
    stats["current_streak"] = get_streak(user_id)
    
    # Update weekly progress
    week_start = datetime.strptime(stats["week_start_date"], "%Y-%m-%d")
    current_date = datetime.now()
    
    # If it's a new week, reset weekly completed
    if (current_date - week_start).days >= 7:
        stats["weekly_completed"] = 1
        stats["week_start_date"] = current_date.strftime("%Y-%m-%d")
        stats["today_counted"] = True
    else:
        # Only increment if it's a new day
        if stats.get("today_counted", False) == False:
            stats["weekly_completed"] += 1
            stats["today_counted"] = True
    
    # Save updated stats
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    return stats

def reset_daily_flags(user_id):
    """Reset daily flags if it's a new day"""
    stats_path = os.path.join("data", f"user_{user_id}_stats.json")
    
    try:
        with open(stats_path, "r") as f:
            stats = json.load(f)
            
        # Check if last_workout_date is from a previous day
        if stats.get("last_workout_date") is not None:
            last_date = datetime.strptime(stats["last_workout_date"], "%Y-%m-%d").date()
            today = datetime.now().date()
            
            if last_date < today:
                stats["today_counted"] = False
                
                # Save updated stats
                with open(stats_path, "w") as f:
                    json.dump(stats, f, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        # TBD - No stats file yet, nothing to reset
        pass


## Exercise Library Page ##
def exercise_library_page(user_id=None):
    st.header("📚 Exercise Library")
    
    # Styling for responsive layout
    st.markdown("""
    <style>
    .exercise-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #dee2e6;
        transition: transform 0.3s ease;
    }
    .exercise-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* Media query for smaller screens */
    @media (max-width: 768px) {
        .stHorizontal {
            flex-direction: column;
        }
        .stHorizontal > div {
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        muscle_groups = st.multiselect("Filter by Muscle Groups", MUSCLE_GROUPS)
    with col2:
        equipment_list = st.multiselect("Filter by Equipment", EQUIPMENT)
            
    # Search box
    search_query = st.text_input("Search Exercises")
    
    # Apply filters - no need for the "Choose an option" handling with multiselect
    muscle_filter = muscle_groups if muscle_groups else None
    equipment_filter = equipment_list if equipment_list else None
    
    # Get filtered exercises
    exercises = get_exercise_library(
        muscle_groups=muscle_filter,
        equipment=equipment_filter
    )
    
    # Filter by search query
    if search_query:
        exercises = [ex for ex in exercises if search_query.lower() in ex["name"].lower()]
    
    # Display count
    st.write(f"Showing {len(exercises)} exercises")
    
    # Display exercises as expandable cards
    for exercise in exercises:
        with st.expander(f"**{exercise['name']}** - {', '.join(exercise['muscle_groups'])}      " f"{exercise.get('progression_label', 'Unknown')}"):
            cols = st.columns([1, 2])
            
            with cols[0]:
                try:
                    if "media" in exercise and exercise["media"]:
                        image_path = f"assets/images/{exercise['media']}"
                        st.image(image_path, use_column_width=True)
                    else:
                        # No media specified, use logo
                        logo_path = "assets/logo.png"
                        st.image(logo_path, use_column_width=True)
                except Exception as e:
                    # If any error occurs, show the logo
                    logo_path = "assets/logo.png"
                    try:
                        st.image(logo_path, use_column_width=True)
                    except:
                        st.write("Logo image also not found")
            
            # Right column for details
            with cols[1]:
                st.subheader(exercise["name"])
                st.write(f"**Description:** {exercise.get('description', 'No description available')}")
                
                st.write(f"**Muscle Groups:** {', '.join(exercise['muscle_groups'])}")
                st.write(f"**Equipment:** {exercise['equipment']}")
                st.write(f"**Category:** {exercise.get('category', 'Not specified')}")
                st.write(f"**Progression Level:** {exercise.get('progression_level', 'Not specified')}")
                st.write(f"**Progression Pathway:** {exercise.get('progression_pathway', 'Not specified')}")
                
                # Instructions
                if "instructions" in exercise and exercise["instructions"]:
                    st.write("**Instructions:**")
                    for instruction in exercise["instructions"]:
                        st.write(f"{instruction}")
                
                # Tips
                if "tips" in exercise and exercise["tips"]:
                    st.write(f"**Tips:** {exercise['tips']}")
                
                # TBD - Add to routine button
                # if st.button(f"Add to Routine", key=f"add_{exercise['id']}"):
                #     # Function to add exercise to user's routine
                #     # This would need to be implemented
                #     st.success(f"Added {exercise['name']} to your routine!")


## Progression Pathways Page ##
def progression_pathways_page(user_id=None):
    st.header("📈 Progression Pathways")
    
    st.write("""
    Progression is the key to continued improvement in fitness. Below are exercise progressions from beginner to advanced levels for different movement patterns.
    
    As you master exercises at your current level, we will suggest you trying next levle progressively to push your training progress.
    
    🏆 Completed 3+ times | ❤️‍🔥 Completed 1-2 times | 🔜 Never completed
    
    """)
    
    # Progression pathways
    progressions = {
        "Push": [
            {"name": "Wall Push-up", "level": "1", "description": "Chest, Triceps, Shoulders; Bodyweight", "equipment": "Bodyweight", "detailed_description": "Performed standing against a wall, pushing away with arms extended. Great for beginners to develop pushing strength with minimal resistance."},
            {"name": "Knee Push-up", "level": "2", "description": "Chest, Triceps, Shoulders; Bodyweight", "equipment": "Bodyweight", "detailed_description": "Push-up performed with knees on the ground instead of toes, reducing the amount of bodyweight you're pushing and making the exercise more accessible."},
            {"name": "Push-up", "level": "3", "description": "Chest, Triceps, Shoulders; Bodyweight", "equipment": "Bodyweight", "detailed_description": "Standard push-up with full body weight supported on toes and hands, maintaining a straight line from head to heels throughout the movement."},
            {"name": "Diamond Push-up", "level": "4", "description": "Chest, Triceps, Shoulders; Bodyweight", "equipment": "Bodyweight", "detailed_description": "Push-up with hands close together forming a diamond shape with thumbs and index fingers, placing greater emphasis on the triceps."},
            {"name": "Archer Push-up", "level": "5", "description": "Chest, Triceps, Shoulders; Bodyweight", "equipment": "Bodyweight", "detailed_description": "One arm performs a push-up while the other extends sideways, shifting more weight to the working arm and creating unilateral resistance."}
        ],
        "Push (Gym)": [
            {"name": "Chest Press Machine", "level": "1", "description": "Chest, Triceps, Shoulders", "equipment": "Machine", "detailed_description": "Fixed-path machine exercise that guides the movement, allowing beginners to learn proper pushing mechanics with adjustable resistance."},
            {"name": "Dumbbell Bench Press", "level": "2", "description": "Chest, Triceps, Shoulders", "equipment": "Dumbbell", "detailed_description": "Lying on a bench, pressing dumbbells from chest level to full arm extension, requiring more stabilization than machine exercises."},
            {"name": "Barbell Bench Press", "level": "3", "description": "Chest, Triceps, Shoulders", "equipment": "Barbell", "detailed_description": "Classic strength exercise using a barbell pressed from chest level to full arm extension while lying on a bench, allowing for heavier loads."},
            {"name": "Incline Dumbbell Press", "level": "4", "description": "Chest, Triceps, Shoulders", "equipment": "Dumbbell", "detailed_description": "Dumbbell press performed on an inclined bench (30-45 degrees), emphasizing the upper chest and requiring greater shoulder stability."},
            {"name": "Weighted Push-up", "level": "5", "description": "Chest, Triceps, Shoulders", "equipment": "Weight Plate", "detailed_description": "Standard push-up with added resistance from weight plates placed on the back, combining bodyweight mechanics with external load."}
        ],
        "Press - Shoulders Focused (Gym)": [
            {"name": "Pike Push-up", "level": "1", "description": "Shoulders, Triceps, Chest", "equipment": "Bodyweight", "detailed_description": "Push-up variation with hips raised high, forming an inverted V-shape that shifts emphasis to the shoulders, mimicking aspects of a handstand push-up."},
            {"name": "Dumbbell Shoulder Press", "level": "2", "description": "Shoulders, Triceps", "equipment": "Dumbbell", "detailed_description": "Pressing dumbbells from shoulder level to overhead while seated or standing, developing shoulder strength with independent arm movement."},
            {"name": "Barbell Shoulder Press", "level": "3", "description": "Shoulders, Triceps", "equipment": "Barbell", "detailed_description": "Also known as the overhead press, involves pressing a barbell from shoulder level to full extension overhead, targeting deltoids and triceps."},
            {"name": "Arnold Press", "level": "4", "description": "Shoulders, Triceps", "equipment": "Dumbbell", "detailed_description": "Dynamic shoulder press starting with palms facing the body, rotating to face forward during the press, increasing range of motion and deltoid activation."},
            {"name": "Lateral Raise", "level": "5", "description": "Shoulders", "equipment": "Dumbbell", "detailed_description": "Isolation exercise raising dumbbells directly out to the sides to shoulder height, specifically targeting the lateral deltoids with strict form."}
        ],
        "Pull": [
            {"name": "Door Row", "level": "1", "description": "Back, Biceps, Shoulders", "equipment": "Smith/TRX", "detailed_description": "Row performed using a door, Smith machine, or TRX suspension trainer, allowing beginners to pull at an angle that reduces the resistance."},
            {"name": "Inverted Row", "level": "2", "description": "Back, Biceps, Shoulders", "equipment": "Smith/Barbell", "detailed_description": "Horizontal pulling exercise performed under a bar set at waist to chest height, with body suspended underneath, pulling chest to bar."},
            {"name": "Chin-up", "level": "3", "description": "Back, Biceps, Shoulders", "equipment": "Pull-up Bar", "detailed_description": "Vertical pulling exercise with palms facing toward you (supinated grip), emphasizing biceps while working the back muscles."},
            {"name": "Pull-up", "level": "4", "description": "Back, Biceps, Shoulders", "equipment": "Pull-up Bar", "detailed_description": "Vertical pulling exercise with palms facing away (pronated grip), placing greater emphasis on the latissimus dorsi and requiring more back strength."},
            {"name": "Archer Pull-up", "level": "5", "description": "Back, Biceps, Shoulders", "equipment": "Pull-up Bar", "detailed_description": "Unilateral pull-up variation where one arm pulls while the other extends sideways, creating asymmetrical loading that builds toward one-arm pull-ups."}
        ],
        "Pull (Gym)": [
            {"name": "Lat Pulldown", "level": "1", "description": "Back, Biceps, Shoulders", "equipment": "Cable Machine", "detailed_description": "Machine exercise mimicking the pull-up motion by pulling a bar down to the chest while seated, with adjustable weight to build vertical pulling strength."},
            {"name": "Seated Row", "level": "2", "description": "Back, Biceps, Shoulders", "equipment": "Machine", "detailed_description": "Horizontal pulling exercise using a machine with a seated position, pulling a handle toward the abdomen to target the middle back muscles."},
            {"name": "Assisted Pull-up", "level": "3", "description": "Back, Biceps, Shoulders", "equipment": "Machine", "detailed_description": "Pull-up performed with machine assistance that counterbalances a portion of bodyweight, allowing progression toward unassisted pull-ups."},
            {"name": "Weighted Pull-up", "level": "4", "description": "Back, Biceps, Shoulders", "equipment": "Pull-up Bar", "detailed_description": "Standard pull-up with additional weight attached via belt or held between the feet, increasing resistance beyond bodyweight."},
            {"name": "One-arm Pull-up", "level": "5", "description": "Back, Biceps, Shoulders", "equipment": "Pull-up Bar", "detailed_description": "Extremely challenging variation performing a pull-up with a single arm, requiring exceptional strength, control, and body awareness."}
        ],
        "Legs": [
            {"name": "Box Squat", "level": "1", "description": "Legs, Glutes", "equipment": "Bench", "detailed_description": "Squat performed to a box or bench, allowing beginners to develop proper form with a defined depth and momentary pause at the bottom."},
            {"name": "Bodyweight Squat", "level": "2", "description": "Legs, Glutes", "equipment": "Bodyweight", "detailed_description": "Fundamental lower body exercise descending into a sitting position and returning to standing, using only bodyweight for resistance."},
            {"name": "Split Squat", "level": "3", "description": "Legs, Glutes", "equipment": "Bodyweight", "detailed_description": "Single-leg focused squat with one foot stepped forward and one back, both feet remaining in contact with the ground throughout the movement."},
            {"name": "Bulgarian Split Squat", "level": "4", "description": "Legs, Glutes", "equipment": "Bench", "detailed_description": "Challenging single-leg squat with the rear foot elevated on a bench, placing greater emphasis on the front leg and requiring more balance."},
            {"name": "Pistol Squat", "level": "5", "description": "Legs, Glutes", "equipment": "Bodyweight", "detailed_description": "Advanced single-leg squat performed with one leg extended forward, descending to full depth on the supporting leg with perfect balance."}
        ],
        "Legs (Gym)": [
            {"name": "Leg Press", "level": "1", "description": "Legs, Glutes", "equipment": "Machine", "detailed_description": "Machine exercise pushing a weighted platform away with the feet while in a seated or reclined position, allowing safe loading with controlled range of motion."},
            {"name": "Goblet Squat", "level": "2", "description": "Legs, Glutes", "equipment": "Dumbbell", "detailed_description": "Squat performed while holding a dumbbell or kettlebell close to the chest, promoting proper depth and upright posture."},
            {"name": "Barbell Back Squat", "level": "3", "description": "Legs, Glutes", "equipment": "Barbell", "detailed_description": "Fundamental strength exercise with a barbell positioned across the upper back, squatting to parallel or below and standing back up."},
            {"name": "Romanian Deadlift", "level": "4", "description": "Legs, Glutes", "equipment": "Barbell", "detailed_description": "Hip-hinge movement lowering a barbell along the legs with minimal knee bend, targeting the posterior chain (hamstrings and glutes)."},
            {"name": "Barbell Front Squat", "level": "5", "description": "Legs, Glutes", "equipment": "Barbell", "detailed_description": "Squat variation with barbell held at the front of the shoulders, requiring significant core strength, mobility, and upper back stability."}
        ],
        "Core": [
            {"name": "Dead Bug", "level": "1", "description": "Abs", "equipment": "Mat", "detailed_description": "Lying on back with arms and legs extended upward, then lowering opposite arm and leg with control while maintaining lower back contact with the floor."},
            {"name": "Plank", "level": "2", "description": "Abs", "equipment": "Mat", "detailed_description": "Isometric core exercise holding a push-up position on forearms with body forming a straight line from head to heels, engaging the entire core."},
            {"name": "Hanging Knee Raise", "level": "3", "description": "Abs", "equipment": "Pull-up Bar", "detailed_description": "Core exercise performed hanging from a bar, raising the knees toward the chest with control, targeting the lower abdominals."},
            {"name": "Hanging Leg Raise", "level": "4", "description": "Abs", "equipment": "Pull-up Bar", "detailed_description": "Progression from knee raises, keeping legs straight while raising them to parallel with the ground or higher, requiring greater core strength."},
            {"name": "Toes-to-bar", "level": "5", "description": "Abs", "equipment": "Pull-up Bar", "detailed_description": "Advanced hanging exercise lifting straight legs all the way up to touch the toes to the bar, demanding exceptional core strength and control."}
        ],
        "Core (Gym)": [
            {"name": "Cable Crunch", "level": "1", "description": "Abs", "equipment": "Cable Machine", "detailed_description": "Kneeling exercise using a cable machine to add resistance to the abdominal crunch movement, allowing progressive loading of the rectus abdominis."},
            {"name": "Roman Chair Sit-up", "level": "2", "description": "Abs", "equipment": "Roman Chair", "detailed_description": "Sit-ups performed on a specialized bench that anchors the feet, allowing a greater range of motion and emphasis on the hip flexors and abdominals."},
            {"name": "Medicine Ball Russian Twist", "level": "3", "description": "Abs", "equipment": "Medicine Ball", "detailed_description": "Seated rotation exercise holding a medicine ball, twisting from side to side while maintaining an elevated torso position to target obliques."},
            {"name": "Ab Wheel Rollout", "level": "4", "description": "Abs", "equipment": "Ab Wheel", "detailed_description": "Challenging exercise using a wheel device rolled forward from a kneeling position, requiring significant core stability and control."},
            {"name": "Weighted Plank", "level": "5", "description": "Abs", "equipment": "Weight Plate", "detailed_description": "Standard plank with added resistance from weight plates placed on the back, intensifying the isometric contraction of the entire core."}
        ]
    }
    
    # Display progressions
    for movement, exercises in progressions.items():
        st.subheader(movement)
        
        # Create three columns for the 5 difficulty levels
        beginner1, beginner2, intermediate, advanced, expert = st.columns(5)
        
        with beginner1:
            st.markdown("##### ⚪️ Beginner 1")
            for ex in [e for e in exercises if e["level"] == "1"]:
                with st.container(border=True):
                    # Get progress indicator for  exercise
                    progress_indicator = get_exercise_progress_indicator(user_id, ex["name"]) if user_id else ""
                    
                    # Display exercise name with progress indicator
                    st.write(f"**{ex['name']}** {progress_indicator}")
                    st.write(ex["description"])
        
        with beginner2:
            st.markdown("##### 🟡 Beginner 2")
            for ex in [e for e in exercises if e["level"] == "2"]:
                with st.container(border=True):
                    progress_indicator = get_exercise_progress_indicator(user_id, ex["name"]) if user_id else ""
                    st.write(f"**{ex['name']}** {progress_indicator}")
                    st.write(ex["description"])
        
        with intermediate:
            st.markdown("##### 🟠 Intermediate")
            for ex in [e for e in exercises if e["level"] == "3"]:
                with st.container(border=True):
                    progress_indicator = get_exercise_progress_indicator(user_id, ex["name"]) if user_id else ""
                    st.write(f"**{ex['name']}** {progress_indicator}")
                    st.write(ex["description"])
                    
        with advanced:
            st.markdown("##### 🟤 Advanced")
            for ex in [e for e in exercises if e["level"] == "4"]:
                with st.container(border=True):
                    progress_indicator = get_exercise_progress_indicator(user_id, ex["name"]) if user_id else ""
                    st.write(f"**{ex['name']}** {progress_indicator}")
                    st.write(ex["description"])
        
        with expert:
            st.markdown("##### ⚫️ Expert")
            for ex in [e for e in exercises if e["level"] == "5"]:
                with st.container(border=True):
                    progress_indicator = get_exercise_progress_indicator(user_id, ex["name"]) if user_id else ""
                    st.write(f"**{ex['name']}** {progress_indicator}")
                    st.write(ex["description"])
        
        st.markdown("---")
  
        
## About & Sources Page ##
def about_sources_page(user_id=None):
    st.header("ℹ️ About & Sources")
    
    st.subheader("About US")
    st.write("""
    **Workout Routine Optimizer** is a personalized fitness app built on exercisescience principles and optimized data structures. We help you create effective, personalized exercise routines based on your fitness level, available equipment, and training goals.
    """)

    st.subheader("Our Mission")
    st.write("""
        Our mission is to solve the most common challenges in fitness:

        - Finding appropriate exercises for your specific fitness level
        - Understanding when and how to progress to more challenging exercises
        - Discovering effective exercises effortlessly
        - Following a structured program that ensures balanced development
        
        Research shows approximately 65% of individuals abandon fitness programs within 3-6 months (Sperandei, 2014). **Workout Routine Optimizer** focuses on these challenges through optimized exercise organization and personalized progression pathways.
    """)

    st.subheader("How It Works")
    with st.expander("**Workout Generation Algorithm**"):
        st.write("""
            Our proprietary algorithm uses three key data structures to create optimal workouts:

            1. Linked Progression Pathways: Exercises are organized in connected progression sequences, allowing you to follow clear advancement paths from beginner to advanced levels.

            2. Hash Table Implementation: We utilize O(1) time complexity for exercise searches, providing significantly faster and more relevant exercise selection than traditional methods.

            3. Supporting Structures: Your workout history is tracked in a stack data structure, while upcoming workouts are managed in a queue, ensuring comprehensive progress monitoring.

            The system analyzes your profile, exercise history, and preferences to generate workouts that are appropriately challenging and balanced across your target muscle groups.
        """)
    
    with st.expander("**Progression System**"):
        st.write("""
            The key to continued improvement in fitness is progressive overload - gradually increasing the demands placed on your body. **Workout Routine Optimizer** automatically tracks your exercise history and suggests appropriate progressions when you're ready to advance.

            Each exercise in our database exists within a progression pathway, connecting related movements from easiest to most challenging. As you master exercises at your current level, we'll guide you to the next appropriate challenge.
        """)
    
    with st.expander("**Data Sources**"):
        st.write("""
            Our exercise database is compiled from reputable fitness sources including:

            - American College of Sports Medicine (ACSM) guidelines
            - National Strength and Conditioning Association (NSCA) resources
            - Peer-reviewed exercise science journals
            - Expert fitness professionals' input
            
            All exercises include proper form guidance and progression pathways to ensure safe and effective training.
        """)
    
        
    st.subheader("References")
    st.write("""
	
    Garay, L. C., Sperandei, S., & Palma, A. (2014). The impact of individual characteristics on maintaining physical activity programs in a fitness gym. Motricidade, 10(3), 3–3.
	
    Haff, G. G., & Triplett, N. T. (Eds.). (2016). Essentials of strength training and conditioning (4th ed.). Human Kinetics.	
    
    Schoenfeld, B. J., Grgic, J., Ogborn, D., & Krieger, J. W. (2017a). Strength and Hypertrophy Adaptations Between Low- vs. High-Load Resistance Training: A Systematic Review and Meta-analysis. Journal of Strength and Conditioning Research, 31(12), 3508–3523. https://doi.org/10.1519/JSC.0000000000002200
	
    Schoenfeld, B. J., Ogborn, D., & Krieger, J. W. (2017b). Dose-response relationship between weekly resistance training volume and increases in muscle mass: A systematic review and meta-analysis. Journal of Sports Sciences, 35(11), 1073–1082. https://doi.org/10.1080/02640414.2016.1210197
	
    Streamlit. (n.d.). Streamlit documentation. Retrieved April 24, 2025, from https://docs.streamlit.io/
    """)    
        
    
    # Contact information
    st.subheader("Contact & Feedback")
    st.write("We're constantly improving! Send feedback to: alexatangki@gmail.com")

  
if __name__ == "__main__":
    main()
