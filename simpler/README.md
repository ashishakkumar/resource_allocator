# HealthSpan Resource Allocator

A system that transforms health recommendations into daily, weekly, monthly, or yearly tasks based on resource availability.

## Overview

The Resource Allocator is a system that transforms the recommendations into a personalized schedule of health activities. It coordinates with resources such as equipment, specialists, and allied health professionals to adapt the plan based on their availability and the client's schedule.

## System Components

1. **Action Plan Generator**: Creates realistic health action plan data with priority-ordered activities
2. **Resource Availability Generator**: Creates realistic availability data for all resources
3. **Resource Allocator**: Schedules activities based on priorities and constraints
4. **Output Generator**: Creates readable calendar output

## Features

- Handles 5 types of health activities: fitness routines, food consumption, medication, therapy, and consultations
- Schedules activities based on their priority and frequency
- Considers availability constraints from the client, specialists, equipment, and allied health professionals
- Uses backup activities when primary activities cannot be scheduled
- Makes adjustments when activities are skipped
- Generates a readable calendar view of the schedule

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/healthspan-resource-allocator.git
cd healthspan-resource-allocator
cd simple
```

2. Install requirements:
```
pip install -r requirements.txt
```

## Usage

Run the main script to generate sample data and a personalized schedule:

```
python main.py
```

This will:
1. Generate sample action plan data (100 activities)
2. Generate availability data for 3 months
3. Create a personalized schedule
4. Generate a calendar view

The outputs will be saved to:
- `data/action_plan.json`: The generated action plan
- `data/availability_data.json`: The generated availability data
- `output/personalized_schedule.json`: The detailed schedule
- `output/personalized_schedule.html`: The calendar view

Open `output/personalized_schedule.html` in a web browser to view the calendar.



## Implementation Notes

- The system is designed for a single client at a time
- Resources are updated after each run for a client
- Priorities are based on what is most important to the client's health
- The system is not designed for emergency situations and assumes a 2-day lead time for most activities
- The scheduler runs once per execution and does not dynamically update during the run

## GenAI Prompts Used

This project was developed with the assistance of generative AI. The provided file (pdf) and the (QnA) were sufficient to generate the entire project.
Claude 3.7 Sonnet was used for the code generation.



