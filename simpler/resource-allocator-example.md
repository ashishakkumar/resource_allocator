# Resource Allocator: Core Functionality Explained

## Purpose

The Resource Allocator is the central component of a health activity scheduling system. It takes health-related activities and availability constraints as input and produces an optimized, conflict-free schedule.

## Input Data

The Resource Allocator processes two primary data sources:

1. **Action Plan Data**: A collection of health activities including:
   - Activity name and type (e.g., "Yoga", "Medication consumption")
   - Frequency (e.g., "Daily", "Twice weekly")
   - Required facilitators or specialists
   - Duration and priority level

2. **Availability Data**: Constraints on when activities can be scheduled:
   - Client availability (dates and hours)
   - Specialist/facilitator availability
   - Equipment availability

## Core Algorithm Steps

The ResourceAllocator follows these key steps to generate a personalized schedule:

### 1. Initialization
```python
def __init__(self, action_plan_file, availability_data_file):
    # Load JSON data files
    # Parse dates
    # Initialize empty schedule
```

This constructor loads and parses the input data files, establishing the scheduling parameters and constraints.

### 2. Schedule Generation
```python
def generate_schedule(self):
    # Sort activities by priority
    # For each activity:
    #   Determine required occurrences based on frequency
    #   Find available dates and times
    #   Schedule the activity
    #   If not possible, try backup activities
    # Return the completed schedule
```

The schedule generation process prioritizes activities, then attempts to find suitable time slots for each occurrence based on all constraints.

### 3. Schedule Validation
```python
def validate_schedule(self):
    # Check for temporal overlaps
    # Identify conflicts between activities
    # Return list of conflicts for resolution
```

This step ensures no activities are scheduled too close together, preventing temporal conflicts.

### 4. Output Generation
```python
def generate_calendar_view(self, output_file):
    # Create HTML calendar representation
    # Color-code activities by type
    # Include status indicators
    # Save to HTML file
```

This produces a human-readable visualization of the schedule as an HTML calendar.

## Key Algorithmic Features

1. **Intelligent Time Slot Selection**: Chooses appropriate times based on activity type
   - Fitness routines → Morning or evening hours
   - Medications → Activity-specific timing (e.g., sleep aids in evening)
   - Meals → Aligned with typical meal times

2. **Backup Activity Resolution**: When a primary activity cannot be scheduled, the system attempts to schedule designated backup activities instead

3. **Constraint Satisfaction**: Ensures all scheduling respects the intersection of:
   - Client availability
   - Facilitator/specialist availability
   - Equipment availability
   - Existing scheduled activities

4. **Conflict Resolution**: Identifies and resolves temporal conflicts where activities might overlap

## Output Formats

The ResourceAllocator produces two output formats:

1. **JSON Schedule**: A structured representation of the complete schedule
2. **HTML Calendar**: A visual calendar representation with color-coding and status indicators

## Example Processing Flow

For an activity like "Strength training":

1. Determine it should occur 3 times per week
2. For each potential date:
   - Check if client is available
   - Check if personal trainer is available
   - Check if required equipment (weights, bench) is available
   - Find overlapping availability hours
3. Select an appropriate time slot (preferably morning or evening for exercise)
4. Add to schedule or try backup activity if constraints cannot be satisfied
5. Validate for conflicts with other scheduled activities
