from fastapi import FastAPI
from pydantic import BaseModel #Import BaseModel to check types automatically, Reinforces required vs optional fields
from datetime import date #Import the library for dates. Prevents invalid dates
from typing import Optional #Allows for some fields to be missing
import uuid

#----------------Variables----------------#
app = FastAPI()
workoutdict = {} #Holds workout logs

#----------------Classes----------------#
#WorkoutCreate Class includes three fields: Date, Calories burned and Workout Length
class WorkoutCreate(BaseModel):
        date: date
        calories_burned: Optional[int] = None
        length_minutes: Optional[int] = None

#Workout Class includes the addition of a UID
class Workout(BaseModel):
        id: str
        date: date
        calories_burned: Optional[int] = None
        length_minutes: Optional[int] = None

#----------------Endpoints----------------#
@app.get("/")
def root():
        return {"status": "ok"}

#Return all workouts
@app.get("/workouts/")
def getWorkout():
        return workoutdict

#Return specific workout by UUID
@app.get("/workouts/{id}")
def getWorkout(id: str):
        return workoutdict[id]

#Add a workout to the dictionary
@app.post("/workouts/")
def create_workout(workout_in: WorkoutCreate):
        workout = add_uuid(workout_in) # Returns a workout object
        add_workout_to_dict(workout)
        return workout

@app.delete("/workouts/")
def deleteWorkouts():
        workoutdict.clear()
        return "All workout logs have been cleared."

@app.delete("/workouts/{id}")
def deleteWorkouts(id: str):
        del workoutdict[id]
        return workoutdict
        


#---------------------------Functions-------------------------#
#Creates a UUID and assigns it to the new workout
def add_uuid(workout_in: WorkoutCreate) -> Workout:
        return Workout(
                id = str(uuid.uuid4()),
                date = workout_in.date,
                calories_burned = workout_in.calories_burned,
                length_minutes = workout_in.length_minutes
                )

#Adds the workout to a workout dictionary
def add_workout_to_dict(workout_in:Workout):
        workoutdict.update({workout_in.id : workout_in})