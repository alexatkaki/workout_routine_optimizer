# Workout Routine Optimizer

A personalized workout routine generator and progress tracker built with Streamlit.

## TLDR
Online Demo Here (username: kk | password: 123321)
https://workoutroutineoptimizer-dlaxfaoyjdboxybx4nmnde.streamlit.app/

## Description

Workout Routine Optimizer helps users create customized workout routines based on their fitness level, available equipment, and target muscle groups. The application provides exercise progressions, visual demonstrations, and tracks workout history to help users achieve their fitness goals.

## Features

- User authentication system
- Personalized workout routine generation
- Exercise progression tracking
- Visual exercise demonstrations (GIFs)
- Workout history logging
- Motivational quotes

## Folder Structure

workout_routine_optimizer
* assets
  * images
  * logo.png
* data
  * exercises.json
  * motivational_quote.json
  * progression_map.json
  * users.json
  * workout_history.json
* uth.py
* constants.py
* data_structures.py
* main.py
* README.md
* requirements.txt
* ui.py
* workout.py


## Installation

1. Clone the repository:
```sh
git clone https://github.com/alexatkaki/workout_routine_optimizer.git 
```

```
cd workout_routine_optimizer
```

2. Create and activate a virtual environment: 

```
python3 -m venv venv
```

```
source venv/bin/activate
``` 

Or on Windows
```
venv\Scripts\activate
``` 

3. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

1. Run the application:
```
streamlit run main.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3. Create an account or log in with existing credentials

4. Generate a personalized workout routine by selecting:
- Fitness level
- Available equipment
- Target muscle groups
- Workout duration

5. Follow the exercises with visual guidance and track your progress

## Data Files

- **exercises.json**: Contains exercise details including name, description, difficulty, and muscle groups
- **progression_map.json**: Maps exercise progressions for different equipment types
- **users.json**: Stores user account information
- **workout_history.json**: Records user workout sessions
- **motivational_quote.json**: Collection of motivational fitness quotes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
