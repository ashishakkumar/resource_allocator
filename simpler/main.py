import os
import time
import json
from data_generator import main as generate_data
from resource_allo import ResourceAllocator

def main():
    """
    Run the entire Resource Allocator pipeline:
    1. Generate sample data
    2. Create a personalized health plan with intelligent time slot allocation
    3. Validate and optimize the schedule to eliminate temporal conflicts
    4. Output the results
    """
    print("HealthSpan AI Resource Allocator - Enhanced Version")
    print("-" * 60)
    print("This implementation includes temporal conflict resolution and optimized scheduling.")
    
    # Step 1: Generate sample data
    print("\n[1/3] Generating sample data...")
    generate_data()
    
    # Verify files exist
    if not os.path.exists("action_plan.json") or not os.path.exists("availability_data.json"):
        print("Error: Sample data files not generated correctly")
        return
    
    # Display summary of generated data
    with open("action_plan.json", 'r') as f:
        action_plan = json.load(f)
    
    with open("availability_data.json", 'r') as f:
        availability_data = json.load(f)
    
    activity_types = {}
    for activity in action_plan:
        activity_type = activity['type']
        if activity_type not in activity_types:
            activity_types[activity_type] = 0
        activity_types[activity_type] += 1
    
    print(f"  Generated {len(action_plan)} activities:")
    for activity_type, count in activity_types.items():
        print(f"  - {activity_type}: {count} activities")
    
    client_days = len(availability_data['client_schedule'])
    print(f"  Generated availability data for {client_days} days")
    
    # Step 2: Create schedule
    print("\n[2/3] Creating personalized schedule...")
    allocator = ResourceAllocator("action_plan.json", "availability_data.json")
    start_time = time.time()
    schedule = allocator.generate_schedule()
    end_time = time.time()
    
    print(f"  Scheduling completed in {end_time - start_time:.2f} seconds")
    
    scheduled_activities = sum(len(activities) for activities in schedule.values())
    scheduled_days = len(schedule)
    
    print(f"  Scheduled {scheduled_activities} activities across {scheduled_days} days")
    
    backup_count = sum(
        1 for day_activities in schedule.values()
        for activity in day_activities
        if activity.get('is_backup', False)
    )
    
    print(f"  Used backup activities {backup_count} times")
    
    # Validate schedule for temporal conflicts
    conflicts = allocator.validate_schedule()
    print(f"  Detected and resolved {len(conflicts)} potential temporal conflicts")
    
    # Calculate time distribution
    time_distribution = {}
    for day_activities in schedule.values():
        for activity in day_activities:
            hour = int(activity['time'].split(':')[0])
            if hour not in time_distribution:
                time_distribution[hour] = 0
            time_distribution[hour] += 1
    
    print("  Activity distribution by hour:")
    for hour in sorted(time_distribution.keys()):
        hour_format = f"{hour:02d}:00"
        count = time_distribution[hour]
        print(f"    {hour_format}: {count} activities")
    
    # Step 3: Generate output
    print("\n[3/3] Generating output files...")
    with open("personalized_schedule.json", 'w') as f:
        json.dump(schedule, f, indent=2)
    
    print("  Saved detailed schedule to personalized_schedule.json")
    
    allocator.generate_calendar_view("personalized_schedule.html")
    print("  Generated calendar view at personalized_schedule.html")
    
    print("\nResource allocation completed successfully!")
    print("Open personalized_schedule.html in a web browser to view the calendar")

if __name__ == "__main__":
    main()