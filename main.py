from fastapi import FastAPI, HTTPException
from pydantic import BaseModel #Import BaseModel to check types automatically, Reinforces required vs optional fields
from datetime import date #Import the library for dates. Prevents invalid dates
from typing import Optional #Allows for some fields to be missing
import uuid, sqlite3


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

#WorkoutUpdate class to have the client update the workout log
class WorkoutUpdate(BaseModel):
        date: Optional[date] = None
        calories_burned: Optional[int] = None
        length_minutes: Optional[int] = None

#---------------------------Database-------------------------#
conn = sqlite3.connect('workouts.db') # Creates workouts database
cursor = conn.cursor()
create_table = """
        CREATE TABLE IF NOT EXISTS logs (
        id VARCHAR(36) PRIMARY KEY,
        date TEXT,
        calories_burned INTEGER,
        length_minutes INTEGER
        );
        """
cursor.execute(create_table)
conn.commit()
conn.close() # Closes the connection to the database

#----------------Endpoints----------------#
@app.get("/")
def root():
        return {"status": "ok"}

# POST & INSERT a workout into the logs table
@app.post("/workouts/")
def create_workout(workout_in: WorkoutCreate):
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()
        
        workout = add_uuid(workout_in) # Assigns a UUID to the workout
        cursor.execute(
                 "INSERT INTO logs (id, date, calories_burned, length_minutes) VALUES (?, ?, ?, ?)",
                 (workout.id, workout.date, workout.calories_burned, workout.length_minutes)
                 )
        
        conn.commit()
        conn.close()
        return "Workout Logged!"

# GET all workouts in the logs table
@app.get("/workouts/")
def getWorkout():
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()  

        cursor.execute("SELECT * FROM logs")
        rows = cursor.fetchall()
        conn.close()
        return rows

# GET workout log by UUID
@app.get("/workouts/{id}")
def getWorkout(id: str):
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs WHERE id=?", (id,))
        row = cursor.fetchone()
        if row is None:
                conn.close()
                raise HTTPException(404, detail="Log ID not found", headers=None)
        else:
                conn.close()
                return row

# DELETE all workout logs from table
@app.delete("/workouts/")
def deleteWorkouts():
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM logs;")
        conn.commit()
        conn.close()
        return "All workout logs have been cleared."

# DELETE specific workout logs based on UUID
@app.delete("/workouts/{id}")
def deleteWorkouts(id: str):
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM logs WHERE id=?", (id,))
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        return rows



#Updates a workout log entry when provided a UUID
@app.patch("/workouts/{id}")
def update_workout(id:str, workoutUpdate: WorkoutUpdate):
        if id not in workoutdict:
                raise HTTPException(status_code=404, detail="Workout log not found")
        else:
                #Converts the pydantic model to a python dict and disregards fields with no input
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


