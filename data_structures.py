class ExerciseNode:
    """Node in the progression linked list"""
    def __init__(self, exercise_data):
        self.exercise = exercise_data
        self.next = None

class ProgressionLinkedList:
    """Linked list of exercises in progression order"""
    def __init__(self):
        self.head = None
    
    def add_exercise(self, exercise_data):
        """Add exercise to progression path"""
        new_node = ExerciseNode(exercise_data)
        
        if not self.head:
            self.head = new_node
            return
        
        # Add to end of list
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def find_by_level(self, level):
        """Find exercise at specific level"""
        current = self.head
        level_count = 1
        
        while current:
            if level_count == level:
                return current.exercise
            current = current.next
            level_count += 1
        
        return None
    
    def get_progression(self, current_exercise_id):
        """Get next exercise in progression"""
        current = self.head
        
        # Find current exercise
        while current and current.exercise["id"] != current_exercise_id:
            current = current.next
        
        # Return next exercise if exists
        if current and current.next:
            return current.next.exercise
        
        return None

class ExerciseHashTable:
    """Hash table for O(1) exercise lookups"""
    def __init__(self):
        self.table = {}
    
    def add_exercise(self, exercise):
        """Add exercise to hash table"""
        self.table[exercise["id"]] = exercise
    
    def get_exercise(self, exercise_id):
        """Get exercise by ID"""
        return self.table.get(exercise_id)
    
    def filter(self, muscle_groups=None, equipment=None, level=None):
        """Filter exercises by multiple criteria"""
        filtered = list(self.table.values())
        
        if muscle_groups:
            filtered = [e for e in filtered if any(m in e["muscle_groups"] for m in muscle_groups)]
        
        if equipment:
            filtered = [e for e in filtered if any(eq in e["equipment"] for eq in equipment)]
        
        if level:
            filtered = [e for e in filtered if e["level"] == level]
        
        return filtered

class WorkoutHistoryStack:
    """Stack for tracking workout history"""
    def __init__(self):
        self.stack = []
    
    def push(self, workout):
        """Add workout to history"""
        self.stack.append(workout)
    
    def pop(self):
        """Remove most recent workout"""
        if self.stack:
            return self.stack.pop()
        return None
    
    def recent(self, n=3):
        """Get n most recent workouts"""
        return self.stack[-n:] if len(self.stack) >= n else self.stack[:]
    
    def get_exercise_completion_count(self, exercise_id):
        """Count how many times an exercise has been completed"""
        count = 0
        for workout in self.stack:
            for exercise in workout.get("exercises", []):
                if exercise["id"] == exercise_id:
                    count += 1
        return count

class WorkoutQueue:
    pass
