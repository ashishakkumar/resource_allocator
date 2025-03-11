import json
import datetime
import random
from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from collections import defaultdict

class ResourceAllocator:
    def __init__(self, action_plan_file: str, availability_data_file: str):
        """
        Initialize the Resource Allocator with action plan and availability data.
        
        Args:
            action_plan_file: Path to the JSON file containing the action plan
            availability_data_file: Path to the JSON file containing availability data
        """
        # Load data
        with open(action_plan_file, 'r') as f:
            self.action_plan = json.load(f)
        
        with open(availability_data_file, 'r') as f:
            self.availability_data = json.load(f)
        
        # Parse dates in availability data
        self.start_date = min(datetime.datetime.strptime(date, '%Y-%m-%d').date() 
                              for date in self.availability_data['client_schedule'].keys())
        self.end_date = max(datetime.datetime.strptime(date, '%Y-%m-%d').date() 
                            for date in self.availability_data['client_schedule'].keys())
        
        # Initialize schedule
        self.schedule = {}
        
    def _get_activity_frequency_details(self, activity: Dict[str, Any]) -> Tuple[int, int]:
        """
        Parse the frequency string and return number of occurrences and interval in days.
        
        Args:
            activity: Activity dictionary
            
        Returns:
            Tuple of (occurrences_per_interval, interval_in_days)
        """
        frequency = activity['frequency']
        
        if frequency == "Daily":
            return 1, 1
        elif frequency == "Twice daily":
            return 2, 1
        elif frequency == "Three times daily":
            return 3, 1
        elif frequency == "Every other day":
            return 1, 2
        elif frequency == "Twice a week":
            return 2, 7
        elif frequency == "Three times a week":
            return 3, 7
        elif frequency == "Weekly":
            return 1, 7
        elif frequency == "Biweekly":
            return 1, 14
        elif frequency == "Monthly":
            return 1, 30
        elif frequency == "Every 3 months":
            return 1, 90
        elif frequency == "Every 6 months":
            return 1, 180
        elif frequency == "Yearly":
            return 1, 365
        else:
            # Default to weekly if unknown
            return 1, 7
    
    def _is_date_available(self, date: datetime.date, activity: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if the given date is available for the activity based on all constraints.
        
        Args:
            date: Date to check
            activity: Activity to schedule
            
        Returns:
            Tuple of (is_available, available_hours)
        """
        date_str = date.strftime('%Y-%m-%d')
        
        # Check if client is available
        if date_str not in self.availability_data['client_schedule'] or not self.availability_data['client_schedule'][date_str]['available']:
            return False, []
        
        client_hours = self.availability_data['client_schedule'][date_str]['available_hours']
        
        # Check facilitator availability if it's a specialist or allied health professional
        facilitator = activity['facilitator']
        facilitator_hours = []
        
        if facilitator in self.availability_data['specialist_availability']:
            # It's a specialist
            if date_str not in self.availability_data['specialist_availability'][facilitator] or not self.availability_data['specialist_availability'][facilitator][date_str]['available']:
                return False, []
            facilitator_hours = self.availability_data['specialist_availability'][facilitator][date_str]['available_hours']
        
        elif facilitator in self.availability_data['allied_health_availability']:
            # It's an allied health professional
            if date_str not in self.availability_data['allied_health_availability'][facilitator] or not self.availability_data['allied_health_availability'][facilitator][date_str]['available']:
                return False, []
            facilitator_hours = self.availability_data['allied_health_availability'][facilitator][date_str]['available_hours']
        
        # If activity requires equipment, check equipment availability
        required_equipment = []
        if activity['type'] == "Fitness routine / exercise":
            # Assign equipment based on activity name
            if "strength" in activity['name'].lower() or "weight" in activity['name'].lower():
                required_equipment = ["Weight Bench", "Dumbbells"]
            elif "cardio" in activity['name'].lower() or "running" in activity['name'].lower():
                required_equipment = ["Treadmill"]
            elif "cycling" in activity['name'].lower():
                required_equipment = ["Stationary Bike"]
            elif "yoga" in activity['name'].lower() or "pilates" in activity['name'].lower():
                required_equipment = ["Yoga Mat"]
        
        elif activity['type'] == "Therapy":
            if "sauna" in activity['name'].lower():
                required_equipment = ["Sauna"]
            elif "ice bath" in activity['name'].lower():
                required_equipment = ["Ice Bath Tub"]
            elif "massage" in activity['name'].lower():
                required_equipment = ["Massage Table"]
        
        # Check each required equipment
        equipment_hours_lists = []
        for equipment in required_equipment:
            if equipment in self.availability_data['equipment_availability']:
                if date_str not in self.availability_data['equipment_availability'][equipment] or not self.availability_data['equipment_availability'][equipment][date_str]['available']:
                    return False, []
                equipment_hours_lists.append(self.availability_data['equipment_availability'][equipment][date_str]['available_hours'])
        
        # Find overlapping hours between client, facilitator, and equipment
        available_hours = set(client_hours)
        
        if facilitator_hours:
            available_hours &= set(facilitator_hours)
        
        for equipment_hours in equipment_hours_lists:
            available_hours &= set(equipment_hours)
        
        if not available_hours:
            return False, []
        
        return True, sorted(list(available_hours))
    
    def _find_available_backup_activity(self, date: datetime.date, activity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find an available backup activity for the given date.
        
        Args:
            date: Date to check
            activity: Original activity that needs a backup
            
        Returns:
            Backup activity if found, None otherwise
        """
        if not activity.get('backup_activities'):
            return None
        
        # Create backup activities
        for backup_name in activity['backup_activities']:
            backup_activity = activity.copy()
            backup_activity['name'] = backup_name
            backup_activity['is_backup'] = True
            
            is_available, _ = self._is_date_available(date, backup_activity)
            if is_available:
                return backup_activity
        
        return None
    
    def _select_time_slot(self, available_hours: List[str], activity: Dict[str, Any], date: datetime.date) -> str:
        """
        Select an appropriate time slot from available hours, considering
        existing scheduled activities to prevent overlap.
        
        Args:
            available_hours: List of available hours
            activity: Activity to schedule
            date: Date for which the time slot is being selected
            
        Returns:
            Selected time slot (e.g., "09:00") or None if no suitable slot found
        """
        if not available_hours:
            return None
        
        date_str = date.strftime('%Y-%m-%d')
        
        # Calculate activity duration in minutes
        duration_minutes = 60  # Default duration
        if 'details' in activity and 'minutes' in activity['details'].lower():
            # Extract duration from details like "Session of 45 minutes"
            details = activity['details'].lower()
            if 'session of ' in details and ' minutes' in details:
                try:
                    duration_str = details.split('session of ')[1].split(' minutes')[0]
                    duration_minutes = int(duration_str)
                except (ValueError, IndexError):
                    pass
        
        # Check for temporal conflicts with already scheduled activities
        occupied_time_slots = set()
        if date_str in self.schedule:
            for scheduled_activity in self.schedule[date_str]:
                scheduled_time = scheduled_activity['time']
                scheduled_hour, scheduled_minute = map(int, scheduled_time.split(':'))
                
                # Calculate scheduled activity duration
                scheduled_duration = 60  # Default duration
                if 'details' in scheduled_activity and 'minutes' in scheduled_activity['details'].lower():
                    details = scheduled_activity['details'].lower()
                    if 'session of ' in details and ' minutes' in details:
                        try:
                            duration_str = details.split('session of ')[1].split(' minutes')[0]
                            scheduled_duration = int(duration_str)
                        except (ValueError, IndexError):
                            pass
                
                # Mark time slots as occupied based on activity duration
                scheduled_start_minutes = scheduled_hour * 60 + scheduled_minute
                scheduled_end_minutes = scheduled_start_minutes + scheduled_duration
                
                # Add buffer time before and after activity (15 min)
                buffer_minutes = 15
                scheduled_start_minutes -= buffer_minutes
                scheduled_end_minutes += buffer_minutes
                
                # Mark all hours that overlap with this activity as occupied
                for i in range(scheduled_start_minutes, scheduled_end_minutes, 15):
                    conflict_hour, conflict_minute = divmod(i, 60)
                    conflict_time = f"{conflict_hour:02d}:{conflict_minute:02d}"
                    occupied_time_slots.add(conflict_time)
        
        # Filter available hours to remove occupied ones
        filtered_hours = [h for h in available_hours if h not in occupied_time_slots]
        
        # If no hours are available after filtering, return None
        if not filtered_hours:
            return None
        
        # Try to schedule at appropriate times based on activity type
        activity_type = activity['type']
        
        morning_hours = [h for h in filtered_hours if int(h.split(':')[0]) < 12]
        afternoon_hours = [h for h in filtered_hours if 12 <= int(h.split(':')[0]) < 17]
        evening_hours = [h for h in filtered_hours if int(h.split(':')[0]) >= 17]
        
        # Activity type-specific time preferences
        if activity_type == "Fitness routine / exercise":
            # Prefer morning or evening for exercise
            preferred_hours = morning_hours + evening_hours
            if preferred_hours:
                return random.choice(preferred_hours)
        
        elif activity_type == "Food consumption":
            # Specific meal timing preferences
            if "breakfast" in activity['name'].lower() and morning_hours:
                early_morning = [h for h in morning_hours if int(h.split(':')[0]) < 9]
                if early_morning:
                    return random.choice(early_morning)
                return random.choice(morning_hours)
            elif "lunch" in activity['name'].lower() and afternoon_hours:
                midday = [h for h in afternoon_hours if 11 <= int(h.split(':')[0]) < 14]
                if midday:
                    return random.choice(midday)
                return random.choice(afternoon_hours)
            elif "dinner" in activity['name'].lower() and evening_hours:
                early_evening = [h for h in evening_hours if 17 <= int(h.split(':')[0]) < 20]
                if early_evening:
                    return random.choice(early_evening)
                return random.choice(evening_hours)
            elif morning_hours:  # For supplements or other food items, prefer morning
                return random.choice(morning_hours)
        
        elif activity_type == "Medication consumption":
            # Morning preference for most medications
            if morning_hours and "sleep" not in activity['name'].lower():
                early_morning = [h for h in morning_hours if int(h.split(':')[0]) < 9]
                if early_morning:
                    return random.choice(early_morning)
                return random.choice(morning_hours)
            # Evening preference for sleep aids
            elif evening_hours and "sleep" in activity['name'].lower():
                late_evening = [h for h in evening_hours if int(h.split(':')[0]) >= 20]
                if late_evening:
                    return random.choice(late_evening)
                return random.choice(evening_hours)
            # Fallback to any available hour
            elif filtered_hours:
                return random.choice(filtered_hours)
        
        elif activity_type == "Therapy":
            # Prefer midday for therapy sessions
            if afternoon_hours:
                return random.choice(afternoon_hours)
            elif morning_hours:
                return random.choice(morning_hours)
        
        elif activity_type == "Consultation":
            # Prefer business hours for consultations
            business_hours = [h for h in filtered_hours if 9 <= int(h.split(':')[0]) < 17]
            if business_hours:
                return random.choice(business_hours)
        
        # Default: select a random available hour from filtered list
        if filtered_hours:
            return random.choice(filtered_hours)
        
        # Fallback: if all hours are occupied, return None
        return None
    
    def generate_schedule(self) -> Dict[str, Any]:
        """
        Generate a personalized schedule based on the action plan and availability.
        
        Returns:
            Dictionary containing the schedule
        """
        # Sort activities by priority
        sorted_activities = sorted(self.action_plan, key=lambda x: x['priority'])
        
        # Initialize schedule dictionary and occupied time slots tracker
        schedule = defaultdict(list)
        self.schedule = schedule  # Initialize self.schedule to be used by _select_time_slot
        
        # Process each activity
        for activity in sorted_activities:
            # Get frequency details
            occurrences, interval_days = self._get_activity_frequency_details(activity)
            
            # Calculate total occurrences needed during the schedule period
            days_in_period = (self.end_date - self.start_date).days + 1
            total_occurrences = (days_in_period // interval_days) * occurrences
            
            # Skip activities that don't occur in our time frame
            if interval_days > days_in_period:
                # Handle special case for 3-month, 6-month or yearly activities
                if interval_days >= 90:
                    # Try to schedule at least once if it's an important activity (high priority)
                    if activity['priority'] <= 20:
                        random_offset = random.randint(0, min(days_in_period - 1, 30))
                        target_date = self.start_date + datetime.timedelta(days=random_offset)
                        
                        is_available, available_hours = self._is_date_available(target_date, activity)
                        if is_available:
                            time_slot = self._select_time_slot(available_hours, activity, current_date)
                            if time_slot:
                                date_str = target_date.strftime('%Y-%m-%d')
                                schedule[date_str].append({
                                    **activity,
                                    'time': time_slot
                                })
                continue
            
            # Generate potential dates for this activity
            scheduled_count = 0
            current_date = self.start_date
            
            while current_date <= self.end_date and scheduled_count < total_occurrences:
                # For activities that occur multiple times per day
                daily_occurrences = occurrences if interval_days == 1 else 1
                daily_scheduled = 0
                
                # Check if this is a scheduled day for the activity
                if (current_date - self.start_date).days % interval_days == 0:
                    # Check availability
                    is_available, available_hours = self._is_date_available(current_date, activity)
                    
                    # If available, schedule the activity
                    if is_available and daily_scheduled < daily_occurrences and available_hours:
                        time_slot = self._select_time_slot(available_hours, activity, current_date)
                        if time_slot:
                            date_str = current_date.strftime('%Y-%m-%d')
                            
                            # Calculate estimated duration for the activity
                            duration_minutes = 60  # Default duration
                            if 'details' in activity and 'minutes' in activity['details'].lower():
                                # Extract duration from details like "Session of 45 minutes"
                                details = activity['details'].lower()
                                if 'session of ' in details and ' minutes' in details:
                                    try:
                                        duration_str = details.split('session of ')[1].split(' minutes')[0]
                                        duration_minutes = int(duration_str)
                                    except (ValueError, IndexError):
                                        pass
                            
                            # Add activity to schedule
                            schedule[date_str].append({
                                **activity,
                                'time': time_slot,
                                'is_backup': False,
                                'duration_minutes': duration_minutes
                            })
                            daily_scheduled += 1
                            scheduled_count += 1
                    
                    # If not available or additional occurrences needed, try backup activities
                    while daily_scheduled < daily_occurrences:
                        backup_activity = self._find_available_backup_activity(current_date, activity)
                        if backup_activity:
                            date_str = current_date.strftime('%Y-%m-%d')
                            is_available, available_hours = self._is_date_available(current_date, backup_activity)
                            if is_available and available_hours:
                                time_slot = self._select_time_slot(available_hours, backup_activity, current_date)
                                if time_slot:
                                    # Calculate estimated duration for the backup activity
                                    duration_minutes = 60  # Default duration
                                    if 'details' in backup_activity and 'minutes' in backup_activity['details'].lower():
                                        details = backup_activity['details'].lower()
                                        if 'session of ' in details and ' minutes' in details:
                                            try:
                                                duration_str = details.split('session of ')[1].split(' minutes')[0]
                                                duration_minutes = int(duration_str)
                                            except (ValueError, IndexError):
                                                pass
                                    
                                    # Add backup activity to schedule
                                    schedule[date_str].append({
                                        **backup_activity,
                                        'time': time_slot,
                                        'is_backup': True,
                                        'original_activity': activity['name'],
                                        'duration_minutes': duration_minutes
                                    })
                                    daily_scheduled += 1
                                    scheduled_count += 1
                                else:
                                    # No suitable time slot found, try next date
                                    break
                            else:
                                # Backup activity not available, try next date
                                break
                        else:
                            # No backup available, try next date
                            break
                
                # Move to the next day
                current_date += datetime.timedelta(days=1)
        
        # Sort schedule by date and time
        sorted_schedule = {}
        for date_str in sorted(schedule.keys()):
            sorted_schedule[date_str] = sorted(schedule[date_str], key=lambda x: x['time'])
        
        self.schedule = sorted_schedule
        return self.schedule
    
    def validate_schedule(self) -> List[Dict[str, Any]]:
        """
        Validate the generated schedule to detect any remaining temporal conflicts.
        
        Returns:
            List of identified conflicts
        """
        conflicts = []
        
        for date_str, activities in self.schedule.items():
            # Sort activities by time
            sorted_activities = sorted(activities, key=lambda x: x['time'])
            
            # Check for overlaps
            for i in range(len(sorted_activities) - 1):
                current_activity = sorted_activities[i]
                next_activity = sorted_activities[i + 1]
                
                # Extract times
                current_time = current_activity['time']
                next_time = next_activity['time']
                
                # Convert to minutes for comparison
                current_hour, current_minute = map(int, current_time.split(':'))
                next_hour, next_minute = map(int, next_time.split(':'))
                
                current_minutes = current_hour * 60 + current_minute
                next_minutes = next_hour * 60 + next_minute
                
                # Get durations
                current_duration = current_activity.get('duration_minutes', 60)
                
                # Check if activities overlap (with 10-min buffer between activities)
                if current_minutes + current_duration + 10 > next_minutes:
                    conflicts.append({
                        'date': date_str,
                        'activity1': current_activity['name'],
                        'time1': current_time,
                        'duration1': current_duration,
                        'activity2': next_activity['name'],
                        'time2': next_time
                    })
        
        return conflicts

    def generate_calendar_view(self, output_file: str = "calendar.html"):
        """
        Generate a readable calendar view of the schedule with comprehensive
        status indication for all days, including explicit representation of 
        unscheduled periods and their causative factors.
        
        Args:
            output_file: Path to save the HTML calendar
        """
        if not self.schedule:
            self.generate_schedule()
            
        # Validate schedule for overlaps
        conflicts = self.validate_schedule()
        if conflicts:
            print(f"Warning: {len(conflicts)} temporal conflicts detected in schedule.")
            for conflict in conflicts[:5]:  # Show first 5 conflicts
                print(f"  {conflict['date']}: {conflict['activity1']} ({conflict['time1']}) overlaps with {conflict['activity2']} ({conflict['time2']})")
            if len(conflicts) > 5:
                print(f"  ... and {len(conflicts) - 5} more conflicts.")
            print("Attempting to resolve conflicts...")
            
            # Regenerate schedule with stricter time slot selection
            self.schedule = {}
            self.generate_schedule()
        
        # Create a DataFrame for each month
        start_month = self.start_date.replace(day=1)
        end_month = self.end_date.replace(day=1)
        current_month = start_month
        
        html_output = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Personalized Health Plan Calendar</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #0066cc; margin-top: 30px; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
                th { background-color: #0066cc; color: white; padding: 8px; text-align: center; }
                td { border: 1px solid #ddd; padding: 8px; vertical-align: top; min-height: 100px; }
                .date { font-weight: bold; margin-bottom: 5px; }
                .activity { margin-bottom: 8px; padding: 5px; border-radius: 4px; }
                .fitness { background-color: #d4f1f9; }
                .food { background-color: #e2f0cb; }
                .medication { background-color: #ffebb5; }
                .therapy { background-color: #f9d2d2; }
                .consultation { background-color: #d2d2f9; }
                .backup { font-style: italic; border-left: 3px solid #ff9900; }
                .unavailable { background-color: #f0f0f0; color: #666; }
                .travel { background-color: #ffe6cc; padding: 5px; margin-bottom: 8px; border-radius: 4px; }
                .resource-unavailable { background-color: #f9d2e7; padding: 5px; margin-bottom: 8px; border-radius: 4px; }
                .facilitator-unavailable { background-color: #d2e7f9; padding: 5px; margin-bottom: 8px; border-radius: 4px; }
                .equipment-unavailable { background-color: #e7f9d2; padding: 5px; margin-bottom: 8px; border-radius: 4px; }
                .rest-day { background-color: #f5f5f5; padding: 5px; margin-bottom: 8px; border-radius: 4px; }
                .legend { margin-top: 20px; padding: 10px; border: 1px solid #ddd; margin-bottom: 20px; }
                .legend-item { display: inline-block; margin: 5px 15px; }
                .legend-color { display: inline-block; width: 20px; height: 20px; margin-right: 5px; vertical-align: middle; }
                .day-status { font-size: 0.8em; font-style: italic; margin-bottom: 5px; }
            </style>
        </head>
        <body>
            <h1>Personalized Health Plan Calendar</h1>
            
            <div class="legend">
                <h3>Activity Types</h3>
                <div class="legend-item"><span class="legend-color" style="background-color: #d4f1f9;"></span> Fitness routine / exercise</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #e2f0cb;"></span> Food consumption</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #ffebb5;"></span> Medication consumption</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #f9d2d2;"></span> Therapy</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #d2d2f9;"></span> Consultation</div>
                <div class="legend-item"><span class="legend-color" style="border-left: 3px solid #ff9900; padding-left: 17px;"></span> Backup activity</div>
                
                <h3>Day Status</h3>
                <div class="legend-item"><span class="legend-color" style="background-color: #ffe6cc;"></span> Client Travel / Unavailable</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #f9d2e7;"></span> Specialist/Resource Unavailable</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #d2e7f9;"></span> Facilitator Unavailable</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #e7f9d2;"></span> Equipment Unavailable</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #f5f5f5;"></span> Rest Day (No Activities Scheduled)</div>
            </div>
        """
        
        # Generate a calendar for each month
        month_names = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
        
        while current_month <= end_month:
            # Calculate the last day of the month
            if current_month.month == 12:
                last_day = current_month.replace(year=current_month.year + 1, month=1, day=1) - datetime.timedelta(days=1)
            else:
                last_day = current_month.replace(month=current_month.month + 1, day=1) - datetime.timedelta(days=1)
            
            html_output += f"<h2>{month_names[current_month.month - 1]} {current_month.year}</h2>"
            html_output += "<table>"
            html_output += "<tr><th>Sunday</th><th>Monday</th><th>Tuesday</th><th>Wednesday</th><th>Thursday</th><th>Friday</th><th>Saturday</th></tr>"
            
            # Calculate the first day of the week
            first_day_weekday = current_month.weekday()
            first_day_weekday = (first_day_weekday + 1) % 7  # Convert Monday=0 to Sunday=0
            
            # Start with the first week
            html_output += "<tr>"
            
            # Add empty cells for days before the first day of the month
            for _ in range(first_day_weekday):
                html_output += "<td></td>"
            
            # Add days of the month
            current_day = current_month
            day_count = first_day_weekday
            
            while current_day <= last_day:
                date_str = current_day.strftime('%Y-%m-%d')
                
                # Start a new row at the beginning of each week
                if day_count % 7 == 0:
                    html_output += "</tr><tr>"
                
                # Determine day status
                day_status = "Available"
                day_status_class = ""
                day_status_reason = ""
                
                # Check client availability first
                client_available = True
                if date_str in self.availability_data['client_schedule']:
                    if not self.availability_data['client_schedule'][date_str]['available']:
                        client_available = False
                        day_status = "Client Unavailable"
                        day_status_class = " class='unavailable'"
                        if 'reason' in self.availability_data['client_schedule'][date_str]:
                            day_status_reason = self.availability_data['client_schedule'][date_str]['reason']
                
                # Check if there are activities scheduled for this day
                has_activities = date_str in self.schedule and len(self.schedule[date_str]) > 0
                
                # If client is available but no activities, determine why
                if client_available and not has_activities:
                    # Check specialist availability
                    specialist_unavailable = False
                    for specialist in self.availability_data['specialist_availability']:
                        if date_str in self.availability_data['specialist_availability'][specialist]:
                            if not self.availability_data['specialist_availability'][specialist][date_str]['available']:
                                specialist_unavailable = True
                                day_status = "Specialist Unavailable"
                                day_status_class = " class='unavailable'"
                                day_status_reason = f"{specialist} unavailable"
                                break
                    
                    # Check allied health availability
                    if not specialist_unavailable:
                        for professional in self.availability_data['allied_health_availability']:
                            if date_str in self.availability_data['allied_health_availability'][professional]:
                                if not self.availability_data['allied_health_availability'][professional][date_str]['available']:
                                    day_status = "Allied Health Professional Unavailable"
                                    day_status_class = " class='unavailable'"
                                    day_status_reason = f"{professional} unavailable"
                                    break
                    
                    # Check equipment availability
                    if day_status == "Available":
                        for equipment in self.availability_data['equipment_availability']:
                            if date_str in self.availability_data['equipment_availability'][equipment]:
                                if not self.availability_data['equipment_availability'][equipment][date_str]['available']:
                                    day_status = "Equipment Unavailable"
                                    day_status_class = " class='unavailable'"
                                    day_status_reason = f"{equipment} unavailable"
                                    break
                    
                    # If all resources available but still no activities, mark as rest day
                    if day_status == "Available":
                        day_status = "Rest Day"
                        day_status_reason = "No activities scheduled for this day"
                
                # Add cell with appropriate class
                html_output += f"<td{day_status_class}><div class='date'>{current_day.day}</div>"
                
                # Add day status
                status_class = ""
                if day_status == "Client Unavailable":
                    status_class = "travel"
                elif day_status == "Specialist Unavailable" or day_status == "Allied Health Professional Unavailable":
                    status_class = "facilitator-unavailable"
                elif day_status == "Equipment Unavailable":
                    status_class = "equipment-unavailable"
                elif day_status == "Rest Day":
                    status_class = "rest-day"
                
                if day_status != "Available" or not has_activities:
                    html_output += f"<div class='{status_class}'><strong>{day_status}:</strong> {day_status_reason}</div>"
                
                # Add activities for this day
                if has_activities:
                    for activity in self.schedule[date_str]:
                        activity_type = activity['type'].lower().split()[0]
                        is_backup = activity.get('is_backup', False)
                        backup_class = " backup" if is_backup else ""
                        
                        html_output += f"<div class='activity {activity_type}{backup_class}'>"
                        html_output += f"<strong>{activity['time']}</strong>: {activity['name']}"
                        
                        if is_backup:
                            html_output += f" <em>(backup for {activity.get('original_activity', 'unknown')})</em>"
                        
                        html_output += f"<br><small>{activity['details']}</small>"
                        html_output += "</div>"
                
                html_output += "</td>"
                
                current_day += datetime.timedelta(days=1)
                day_count += 1
            
            # Add empty cells for days after the last day of the month
            for _ in range((7 - day_count % 7) % 7):
                html_output += "<td></td>"
            
            html_output += "</tr></table>"
            
            # Move to the next month
            if current_month.month == 12:
                current_month = current_month.replace(year=current_month.year + 1, month=1)
            else:
                current_month = current_month.replace(month=current_month.month + 1)
        
        html_output += """
        </body>
        </html>
        """
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write(html_output)
        
        print(f"Calendar view saved to {output_file}")

def main():
    """Run the Resource Allocator."""
    allocator = ResourceAllocator("action_plan.json", "availability_data.json")
    schedule = allocator.generate_schedule()
    
    # Save schedule to JSON
    with open("personalized_schedule.json", 'w') as f:
        json.dump(schedule, f, indent=2)
    
    # Generate calendar view
    allocator.generate_calendar_view("personalized_schedule.html")
    
    print("Resource allocation completed successfully")
    print(f"Scheduled {sum(len(activities) for activities in schedule.values())} activities")
    print("Results saved to personalized_schedule.json and personalized_schedule.html")

if __name__ == "__main__":
    main()