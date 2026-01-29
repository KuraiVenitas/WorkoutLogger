from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel #Import BaseModel to check types automatically, Reinforces required vs optional fields
#from pydantic import Field
from datetime import date #Import the library for dates. Prevents invalid dates
from typing import Optional #Allows for some fields to be missing
import uuid


#----------------Variables----------------#
app = FastAPI()
workoutdict = {} #Holds workout logs

#----------------Classes----------------#
#WorkoutCreate Class includes three fields: Date, Calories burned and Workout Length
class WorkoutCreate(BaseModel):
        #date: date = Field(default_factory=date.today)
        date: date
        calories_burned: Optional[int] = None
        length_minutes: Optional[int] = None

#Workout Class includes the addition of a UID
class Workout(BaseModel):
        id: str
        date: date
        calories_burned: Optional[int] = None
        length_minutes: Optional[int] = None

#WorkoutUpdate class to have the client update the workout log
class WorkoutUpdate(BaseModel):
        date: Optional[date] = None
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
        if id not in workoutdict:
                raise HTTPException(status_code=404, detail="Workout log not found")
        else:
                return workoutdict[id]

#Add a workout to the dictionary
@app.post("/workouts/")
def create_workout(workout_in: WorkoutCreate):
        workout = add_uuid(workout_in) # Returns a workout object
        add_workout_to_dict(workout)
        return workout

#Delete all workout logs
@app.delete("/workouts/")
def deleteWorkouts():
        workoutdict.clear()
        return "All workout logs have been cleared."

#Delete specific workout logs based on UUID
@app.delete("/workouts/{id}")
def deleteWorkouts(id: str):
        if id not in workoutdict:
                raise HTTPException(status_code=404, detail="Workout log not found")
        else:
                del workoutdict[id]
                return workoutdict

#Updates a workout log entry when provided a UUID
@app.patch("/workouts/{id}")
def update_workout(id:str, workoutUpdate: WorkoutUpdate):
        if id not in workoutdict:
                raise HTTPException(status_code=404, detail="Workout log not found")
        else:
                #Converts the pydantic model to a python dict and removes unneccesary fields
                update_data = workoutUpdate.model_dump(exclude_unset=True) 
                workoutdict[id] = workoutdict[id].model_copy(update=update_data)
                return workoutdict[id]



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