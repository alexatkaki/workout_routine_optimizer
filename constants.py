PROGRESSION_LEVELS = [
    {"value": "1", "label": "Level 1 - ⚪️ Beginner 1", "name": "Beginner 1"},
    {"value": "2", "label": "Level 2 - 🟡 Beginner 2", "name": "Beginner 2"},
    {"value": "3", "label": "Level 3 - 🟠 Intermediate", "name": "Intermediate"},
    {"value": "4", "label": "Level 4 - 🟤 Advanced", "name": "Advanced"},
    {"value": "5", "label": "Level 5 - ⚫️ Expert", "name": "Expert"}
]

TRAINING_GOALS = [
    {
        "value": "Maintaining/Bulking",
        "label": "Maintaining/Bulking (higher volume, moderate-to-high reps, focus on muscle growth)"
    },
    {
        "value": "Cutting/Weight Loss",
        "label": "Cutting/Weight Loss (lower calories, higher reps, shorter rest, more cardio)"
    },
    {
        "value": "Strength",
        "label": "Strength (lower reps, higher weight, longer rest, focus on compound lifts)"
    },
    {
        "value": "General Fitness",
        "label": "General Fitness (balanced routine, all-around improvement, moderate sets/reps/weight)"
    },
]


EXERCISES = [
    # Push
    {"name": "Wall Push-up", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Bodyweight"]},
    {"name": "Knee Push-up", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Bodyweight"]},
    {"name": "Push-up", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Bodyweight"]},
    {"name": "Diamond Push-up", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Bodyweight"]},
    {"name": "Archer Push-up", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Bodyweight"]},

    # Push (Gym)
    {"name": "Chest Press Machine", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Machine"]},
    {"name": "Dumbbell Bench Press", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Dumbbell"]},
    {"name": "Barbell Bench Press", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Barbell"]},
    {"name": "Incline Dumbbell Press", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Dumbbell"]},
    {"name": "Weighted Push-up", "muscle_groups": ["Chest", "Triceps", "Shoulders"], "equipment": ["Weight Plate"]},

    # Shoulders (Gym, part of Push)
    {"name": "Pike Push-up", "muscle_groups": ["Shoulders", "Triceps", "Chest"], "equipment": ["Bodyweight"]},
    {"name": "Dumbbell Shoulder Press", "muscle_groups": ["Shoulders", "Triceps"], "equipment": ["Dumbbell"]},
    {"name": "Barbell Shoulder Press", "muscle_groups": ["Shoulders", "Triceps"], "equipment": ["Barbell"]},
    {"name": "Arnold Press", "muscle_groups": ["Shoulders", "Triceps"], "equipment": ["Dumbbell"]},
    {"name": "Lateral Raise", "muscle_groups": ["Shoulders"], "equipment": ["Dumbbell"]},

    # Pull
    {"name": "Door Row", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Smith", "TRX"]},
    {"name": "Inverted Row", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Smith", "Barbell", "TRX"]},
    {"name": "Chin-up", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Pull-up Bar"]},
    {"name": "Pull-up", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Pull-up Bar"]},
    {"name": "Archer Pull-up", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Pull-up Bar"]},

    # Pull (Gym)
    {"name": "Lat Pulldown", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Cable Machine"]},
    {"name": "Seated Row", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Machine"]},
    {"name": "Assisted Pull-up", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Machine"]},
    {"name": "Weighted Pull-up", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Pull-up Bar"]},
    {"name": "One-arm Pull-up", "muscle_groups": ["Back", "Biceps", "Shoulders"], "equipment": ["Pull-up Bar"]},

    # Legs
    {"name": "Box Squat", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Bench"]},
    {"name": "Bodyweight Squat", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Bodyweight"]},
    {"name": "Split Squat", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Bodyweight"]},
    {"name": "Bulgarian Split Squat", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Bench"]},
    {"name": "Pistol Squat", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Bodyweight"]},

    # Legs (Gym)
    {"name": "Leg Press", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Machine"]},
    {"name": "Goblet Squat", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Dumbbell"]},
    {"name": "Barbell Back Squat", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Barbell"]},
    {"name": "Romanian Deadlift", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Barbell"]},
    {"name": "Barbell Front Squat", "muscle_groups": ["Legs", "Glutes"], "equipment": ["Barbell"]},

    # Core
    {"name": "Dead Bug", "muscle_groups": ["Abs"], "equipment": ["Bodyweight"]},
    {"name": "Plank", "muscle_groups": ["Abs"], "equipment": ["Bodyweight"]},
    {"name": "Hanging Knee Raise", "muscle_groups": ["Abs"], "equipment": ["Pull-up Bar"]},
    {"name": "Hanging Leg Raise", "muscle_groups": ["Abs"], "equipment": ["Pull-up Bar"]},
    {"name": "Toes-to-bar", "muscle_groups": ["Abs"], "equipment": ["Pull-up Bar"]},

    # Core (Gym)
    {"name": "Cable Crunch", "muscle_groups": ["Abs"], "equipment": ["Cable Machine"]},
    {"name": "Roman Chair Sit-up", "muscle_groups": ["Abs"], "equipment": ["Roman Chair"]},
    {"name": "Medicine Ball Russian Twist", "muscle_groups": ["Abs"], "equipment": ["Medicine Ball"]},
    {"name": "Ab Wheel Rollout", "muscle_groups": ["Abs"], "equipment": ["Ab Wheel"]},
    {"name": "Weighted Plank", "muscle_groups": ["Abs"], "equipment": ["Weight Plate"]}
]


MUSCLE_GROUPS = [
    "Chest", "Triceps", "Shoulders", "Back", "Biceps", "Legs", "Glutes", "Abs"
]

MUSCLR_CATEGORIES = [
    {"value": "Upper Body", "label": "Upper Body"},
    {"value": "Lower Body", "label": "Lower Body"},
    {"value": "Core", "label": "Core"},
    {"value": "Full Body", "label": "Full Body"},
    {"value": "Push", "label": "Push Muscles"},
    {"value": "Pull", "label": "Pull Muscles"}
]

MUSCLE_GROUPS_COMB = [
    {
        "value": '1',
        "name": "Full Body",
        "muscle_groups": ["Chest", "Triceps", "Shoulders", "Back", "Biceps", "Legs", "Glutes", "Abs"],
        "count": 8
    },
    {
        "value": '2',
        "name": "Upper Body",
        "muscle_groups": ["Chest", "Triceps", "Shoulders", "Back", "Biceps"],
        "count": 5
    },
    {
        
        "value": '3',
        "name": "Lower Body",
        "muscle_groups": ["Legs", "Glutes"],
        "count": 2
    },
    {
        "value": '4',
        "name": "Push Muscles",
        "muscle_groups": ["Chest", "Triceps", "Shoulders"],
        "count": 3
    },
    {
        "value": '5',
        "name": "Pull Muscles",
        "muscle_groups": ["Back", "Biceps", "Shoulders"],
        "count": 3
    },
    {
        "value": '6',
        "name": "Core",
        "muscle_groups": ["Abs"],
        "count": 1
    }
]


EQUIPMENT = [
    "Bodyweight",
    "Bench",
    "Smith/TRX",
    "Smith/Barbell",
    "Pull-up Bar",
    "Dumbbell",
    "Barbell",
    "Weight Plate",
    "Lever Chest Press Machine",
    "Cable Lat Pulldown Machine",
    "Cable Row Machine",
    "Assisted Pull-up Machine",
    "45° Leg Press Machine",
    "Cable Machine",
    "Roman Chair",
    "Medicine Ball",
    "Ab Wheel",
    "Mat"
]


