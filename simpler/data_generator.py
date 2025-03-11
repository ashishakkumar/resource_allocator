import json
import random
import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

# Constants for generating realistic data
ACTIVITY_TYPES = [
    "Fitness routine / exercise",
    "Food consumption",
    "Medication consumption",
    "Therapy",
    "Consultation"
]

FITNESS_ACTIVITIES = [
    "High-intensity interval training", "Strength training", "Yoga", "Swimming", 
    "Cycling", "Running", "Walking", "Pilates", "Tai Chi", "Eye exercises", 
    "Balance training", "Flexibility training", "Core strengthening", "Cardio workout",
    "Circuit training", "Resistance band exercises", "Bodyweight exercises", "Functional training"
]

FOOD_ACTIVITIES = [
    "Protein shake consumption", "Omega-3 supplement", "Probiotics", "Vitamin D", 
    "Antioxidant-rich meal", "Anti-inflammatory diet meal", "Low-glycemic meal", 
    "Mediterranean diet meal", "Intermittent fasting", "Ketogenic meal", 
    "Plant-based meal", "High-fiber meal", "Low-sodium meal", "Calorie-restricted meal"
]

MEDICATION_ACTIVITIES = [
    "Blood pressure medication", "Cholesterol medication", "Thyroid medication", 
    "Anti-inflammatory medication", "Sleep aid", "Vitamin B complex", "Vitamin C", 
    "Magnesium supplement", "Calcium supplement", "Iron supplement", 
    "Zinc supplement", "Melatonin", "Antihistamine", "Pain reliever"
]

THERAPY_ACTIVITIES = [
    "Sauna session", "Ice bath", "Cryotherapy", "Heat therapy", "Massage therapy", 
    "Acupuncture", "Physical therapy", "Cognitive behavioral therapy", 
    "Mindfulness meditation", "Deep breathing exercises", "Light therapy", 
    "Hydrotherapy", "Float tank session", "Infrared therapy"
]

CONSULTATION_ACTIVITIES = [
    "Nutritionist consultation", "Personal trainer session", "Medical doctor checkup", 
    "Blood test analysis", "Sleep specialist consultation", "Physical therapist consultation", 
    "Mental health counseling", "Dermatologist consultation", "Ophthalmologist checkup", 
    "Dentist checkup", "Endocrinologist consultation", "Cardiologist checkup", 
    "Stress management counseling", "Wellness coach session"
]

FREQUENCY_OPTIONS = [
    "Daily", "Twice daily", "Three times daily", 
    "Every other day", "Twice a week", "Three times a week", 
    "Weekly", "Biweekly", "Monthly", "Every 3 months", "Every 6 months", "Yearly"
]

FACILITATORS = [
    "Personal Trainer", "Nutritionist", "Medical Doctor", "Physiotherapist", 
    "Massage Therapist", "Yoga Instructor", "Meditation Coach", "Self-administered", 
    "Nurse", "Dietitian", "Naturopath", "Exercise Physiologist", "Sleep Specialist", 
    "Mental Health Counselor", "Wellness Coach"
]

LOCATIONS = [
    "Home", "Gym", "Medical Clinic", "Wellness Center", "Park", "Swimming Pool", 
    "Yoga Studio", "Physical Therapy Clinic", "Hospital", "Health Food Store", 
    "Office", "Specialized Facility", "Community Center", "Tennis Court", 
    "Track Field", "Beach", "Forest Trail", "Mountain Trail"
]

EQUIPMENT = [
    "Treadmill", "Stationary Bike", "Rowing Machine", "Elliptical Trainer", 
    "Weight Bench", "Dumbbells", "Resistance Bands", "Yoga Mat", "Foam Roller", 
    "Medicine Ball", "Stability Ball", "Jump Rope", "Pull-up Bar", "Kettlebell", 
    "TRX Suspension Trainer", "Sauna", "Ice Bath Tub", "Massage Table", 
    "Blood Pressure Monitor", "Heart Rate Monitor", "Sleep Tracker", "Fitness Tracker"
]

SPECIALISTS = [
    "Dr. Smith (Cardiologist)", "Dr. Johnson (Endocrinologist)", "Dr. Williams (Neurologist)", 
    "Dr. Brown (Gastroenterologist)", "Dr. Jones (Dermatologist)", "Dr. Miller (Ophthalmologist)", 
    "Dr. Davis (Rheumatologist)", "Dr. Wilson (Orthopedist)", "Sarah Green (Nutritionist)", 
    "Michael Taylor (Personal Trainer)", "Emma White (Physiotherapist)", "Daniel Black (Sleep Specialist)", 
    "Olivia Thomas (Mental Health Counselor)", "Noah Martin (Massage Therapist)", 
    "Sophia Anderson (Yoga Instructor)", "James Jackson (Exercise Physiologist)"
]

ALLIED_HEALTH = [
    "Emma Clark (Physiotherapist)", "John Lewis (Occupational Therapist)", 
    "Jessica Moore (Dietitian)", "Ryan Thompson (Speech Therapist)", 
    "Madison Harris (Podiatrist)", "Ethan Martinez (Chiropractor)", 
    "Ava Robinson (Exercise Physiologist)", "William Lee (Psychologist)", 
    "Sophia King (Social Worker)", "Lucas Scott (Audiologist)", 
    "Mia Nelson (Art Therapist)", "Benjamin Baker (Respiratory Therapist)", 
    "Charlotte Hill (Rehabilitation Counselor)", "Samuel Allen (Orthopedic Technician)"
]

TRAVEL_DESTINATIONS = [
    "New York", "Los Angeles", "Chicago", "Miami", "London", "Paris", "Tokyo", 
    "Sydney", "Toronto", "Rome", "Barcelona", "Berlin", "Hong Kong", "Singapore", 
    "Dubai", "Beijing", "Moscow", "Stockholm", "Zurich", "Vienna"
]

def generate_activity_details(activity_type: str) -> Dict[str, Any]:
    """Generate a realistic activity based on type with explicit duration."""
    # Generate appropriate details with duration for each activity type
    if activity_type == "Fitness routine / exercise":
        activity_name = random.choice(FITNESS_ACTIVITIES)
        # Fitness activities typically take 30-60 minutes
        duration = random.randint(30, 60)
        details = f"Session of {duration} minutes. Maintain HR between {random.randint(110, 150)}-{random.randint(160, 180)} bpm"
        facilitator = random.choice(["Personal Trainer", "Self-administered", "Yoga Instructor", "Exercise Physiologist"])
        metrics = f"Heart rate, duration, {random.choice(['calorie burn', 'perceived effort', 'repetitions', 'sets'])}"
        
    elif activity_type == "Food consumption":
        activity_name = random.choice(FOOD_ACTIVITIES)
        # Food consumption typically takes 15-30 minutes
        duration = random.randint(15, 30)
        details = f"Session of {duration} minutes. Consume {random.randint(1, 4)} {random.choice(['serving(s)', 'capsule(s)', 'tablespoon(s)', 'oz'])}"
        facilitator = random.choice(["Nutritionist", "Dietitian", "Self-administered"])
        metrics = f"Adherence, {random.choice(['energy levels', 'digestive response', 'satiety', 'taste satisfaction'])}"
        
    elif activity_type == "Medication consumption":
        activity_name = random.choice(MEDICATION_ACTIVITIES)
        # Medication consumption typically takes 5-10 minutes
        duration = random.randint(5, 10)
        details = f"Session of {duration} minutes. Take {random.randint(1, 2)} {random.choice(['pill(s)', 'capsule(s)', 'dose(s)', 'tablet(s)'])}"
        facilitator = random.choice(["Medical Doctor", "Nurse", "Self-administered"])
        metrics = f"Adherence, {random.choice(['side effects', 'symptom reduction', 'blood markers', 'effectiveness'])}"
        
    elif activity_type == "Therapy":
        activity_name = random.choice(THERAPY_ACTIVITIES)
        # Therapy sessions typically take 30-90 minutes
        duration = random.randint(30, 90)
        details = f"Session of {duration} minutes"
        facilitator = random.choice(["Massage Therapist", "Physiotherapist", "Mental Health Counselor", "Naturopath"])
        metrics = f"Effectiveness, {random.choice(['comfort level', 'pain reduction', 'relaxation', 'recovery'])}"
        
    else:  # Consultation
        activity_name = random.choice(CONSULTATION_ACTIVITIES)
        # Consultations typically take 30-60 minutes
        duration = random.randint(30, 60)
        details = f"Session of {duration} minutes"
        facilitator = random.choice(SPECIALISTS)
        metrics = f"Action items identified, {random.choice(['insights gained', 'recommendations', 'test results', 'progress assessment'])}"
    
    # Common fields
    frequency = random.choice(FREQUENCY_OPTIONS)
    location = random.choice(LOCATIONS)
    remote_capable = random.choice([True, False])
    
    # Generate backup activities (1-3)
    num_backups = random.randint(1, 3)
    if activity_type == "Fitness routine / exercise":
        backup_options = [a for a in FITNESS_ACTIVITIES if a != activity_name]
    elif activity_type == "Food consumption":
        backup_options = [a for a in FOOD_ACTIVITIES if a != activity_name]
    elif activity_type == "Medication consumption":
        backup_options = [a for a in MEDICATION_ACTIVITIES if a != activity_name]
    elif activity_type == "Therapy":
        backup_options = [a for a in THERAPY_ACTIVITIES if a != activity_name]
    else:  # Consultation
        backup_options = [a for a in CONSULTATION_ACTIVITIES if a != activity_name]
    
    backups = random.sample(backup_options, min(num_backups, len(backup_options)))
    
    # Prep work needed
    if activity_type == "Fitness routine / exercise":
        prep = f"Prepare exercise clothes, {random.choice(['fill water bottle', 'charge fitness tracker', 'prepare equipment', 'warm up'])}"
    elif activity_type == "Food consumption":
        prep = f"{random.choice(['Prepare meal', 'Purchase supplements', 'Stock ingredients', 'Organize meal prep'])}"
    elif activity_type == "Medication consumption":
        prep = f"{random.choice(['Refill prescription', 'Set reminder', 'Take with food if needed', 'Check medication interactions'])}"
    elif activity_type == "Therapy":
        prep = f"{random.choice(['Book appointment', 'Prepare comfortable clothes', 'Hydrate before session', 'Complete pre-session questionnaire'])}"
    else:  # Consultation
        prep = f"{random.choice(['Gather medical records', 'Prepare questions', 'Complete intake forms', 'Fast if required for tests'])}"
    
    # Adjustments if skipped
    if activity_type == "Fitness routine / exercise":
        adjustments = f"{random.choice(['Increase intensity in next session', 'Add extra session later in week', 'Substitute with alternative exercise', 'Extend next session by 15 minutes'])}"
    elif activity_type == "Food consumption":
        adjustments = f"{random.choice(['Double next dose', 'Adjust timing of next meal', 'Substitute with alternative food', 'Add extra nutrients in next meal'])}"
    elif activity_type == "Medication consumption":
        adjustments = f"{random.choice(['Take as soon as remembered if same day', 'Skip if next dose due within 12 hours', 'Consult doctor if consecutive doses missed', 'Adjust timing of other medications'])}"
    elif activity_type == "Therapy":
        adjustments = f"{random.choice(['Reschedule within same week', 'Extend next session', 'Do home exercises instead', 'Use self-therapy techniques'])}"
    else:  # Consultation
        adjustments = f"{random.choice(['Reschedule ASAP', 'Consider telehealth option', 'Request summary of missed information', 'Prepare more thoroughly for next appointment'])}"
    
    return {
        "name": activity_name,
        "type": activity_type,
        "frequency": frequency,
        "details": details,
        "facilitator": facilitator,
        "location": location,
        "remote_capable": remote_capable,
        "prep_needed": prep,
        "backup_activities": backups,
        "adjustments_if_skipped": adjustments,
        "metrics": metrics,
        "duration_minutes": duration
    }

def generate_action_plan(num_activities: int = 100) -> List[Dict[str, Any]]:
    """Generate a prioritized action plan with varied activities."""
    action_plan = []
    
    # Ensure distribution across activity types
    activity_counts = {
        "Fitness routine / exercise": int(num_activities * 0.3),
        "Food consumption": int(num_activities * 0.25),
        "Medication consumption": int(num_activities * 0.2),
        "Therapy": int(num_activities * 0.15),
        "Consultation": int(num_activities * 0.1)
    }
    
    # Add remaining activities to make sure we hit the target
    remaining = num_activities - sum(activity_counts.values())
    for _ in range(remaining):
        activity_type = random.choice(ACTIVITY_TYPES)
        activity_counts[activity_type] += 1
    
    # Generate activities for each type
    for activity_type, count in activity_counts.items():
        for _ in range(count):
            activity = generate_activity_details(activity_type)
            action_plan.append(activity)
    
    # Assign priority (1 is highest priority)
    random.shuffle(action_plan)  # Shuffle first to avoid correlation between type and priority
    for i, activity in enumerate(action_plan):
        activity["priority"] = i + 1
    
    # Sort by priority
    action_plan.sort(key=lambda x: x["priority"])
    
    return action_plan

def generate_availability_data(start_date: datetime.date, months: int = 3) -> Dict[str, Any]:
    """Generate availability data for constraints with comprehensive coverage."""
    end_date = start_date + datetime.timedelta(days=30*months)
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Generate client schedule (available/unavailable days)
    client_schedule = {}
    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        # Client is generally available, but has some travel days
        if random.random() < 0.1:  # 10% chance of being unavailable due to travel
            destination = random.choice(TRAVEL_DESTINATIONS)
            client_schedule[date_str] = {
                "available": False,
                "reason": f"Travel to {destination}"
            }
        else:
            # Available hours (typically 7am-9pm with some variation)
            start_hour = random.randint(6, 9)
            end_hour = random.randint(19, 22)
            available_hours = [f"{h:02d}:00" for h in range(start_hour, end_hour)]
            
            client_schedule[date_str] = {
                "available": True,
                "available_hours": available_hours
            }
    
    # Generate equipment availability
    equipment_availability = {}
    for equipment in EQUIPMENT:
        equipment_availability[equipment] = {}
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            # Equipment is generally available
            if random.random() < 0.05:  # 5% chance of being unavailable
                equipment_availability[equipment][date_str] = {
                    "available": False,
                    "reason": random.choice(["Maintenance", "In use by another client", "Not operational", "Being replaced"])
                }
            else:
                # Available hours
                start_hour = random.randint(6, 10)
                end_hour = random.randint(17, 22)
                available_hours = [f"{h:02d}:00" for h in range(start_hour, end_hour)]
                
                equipment_availability[equipment][date_str] = {
                    "available": True,
                    "available_hours": available_hours
                }
    
    # Generate specialist availability
    specialist_availability = {}
    for specialist in SPECIALISTS:
        specialist_availability[specialist] = {}
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            # Weekend unavailability for some specialists
            if date.weekday() >= 5 and random.random() < 0.7:  # 70% chance specialists are unavailable on weekends
                specialist_availability[specialist][date_str] = {
                    "available": False,
                    "reason": "Weekend - not working"
                }
            elif random.random() < 0.2:  # 20% chance of being unavailable on weekdays
                specialist_availability[specialist][date_str] = {
                    "available": False,
                    "reason": random.choice(["Vacation", "Conference", "Other appointments", "Personal day"])
                }
            else:
                # Working hours (typically 9am-5pm with some variation)
                start_hour = random.randint(8, 10)
                end_hour = random.randint(16, 18)
                available_hours = [f"{h:02d}:00" for h in range(start_hour, end_hour)]
                
                specialist_availability[specialist][date_str] = {
                    "available": True,
                    "available_hours": available_hours
                }
    
    # Generate allied health availability
    allied_health_availability = {}
    for professional in ALLIED_HEALTH:
        allied_health_availability[professional] = {}
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            # Weekend unavailability
            if date.weekday() >= 5 and random.random() < 0.8:  # 80% chance allied health pros are unavailable on weekends
                allied_health_availability[professional][date_str] = {
                    "available": False,
                    "reason": "Weekend - not working"
                }
            elif random.random() < 0.15:  # 15% chance of being unavailable on weekdays
                allied_health_availability[professional][date_str] = {
                    "available": False,
                    "reason": random.choice(["Vacation", "Conference", "Other appointments", "Personal day"])
                }
            else:
                # Working hours (typically 8am-6pm with some variation)
                start_hour = random.randint(7, 9)
                end_hour = random.randint(16, 19)
                available_hours = [f"{h:02d}:00" for h in range(start_hour, end_hour)]
                
                allied_health_availability[professional][date_str] = {
                    "available": True,
                    "available_hours": available_hours
                }
    
    return {
        "client_schedule": client_schedule,
        "equipment_availability": equipment_availability,
        "specialist_availability": specialist_availability,
        "allied_health_availability": allied_health_availability,
        "date_range": {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }
    }

def save_to_json(data, filename):
    """Save data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    """Generate and save all required data"""
    # Set a seed for reproducibility
    random.seed(42)
    
    # Generate action plan with 100 activities
    action_plan = generate_action_plan(100)
    save_to_json(action_plan, "action_plan.json")
    
    # Generate availability data for 3 months
    start_date = datetime.date(2023, 1, 1)
    availability_data = generate_availability_data(start_date, months=3)
    save_to_json(availability_data, "availability_data.json")
    
    print(f"Generated action plan with {len(action_plan)} activities")
    print("Generated availability data for 3 months")
    print("Files saved: action_plan.json, availability_data.json")

if __name__ == "__main__":
    main()