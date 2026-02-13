from fastapi import FastAPI, HTTPException
from pydantic import Field, BaseModel #Import BaseModel to check types automatically, Reinforces required vs optional fields
from datetime import date as dt_date #Import the library for dates. Prevents invalid dates
from typing import Optional #Allows for some fields to be missing
import uuid, sqlite3

app = FastAPI()

#----------------Classes----------------#
#WorkoutCreate Class includes three fields: Date, Calories burned and Workout Length
class WorkoutCreate(BaseModel):
        date: dt_date = Field(default_factory = dt_date.today) # Note: Defaults the date to today's date if the client send no date in their request
        calories_burned: Optional[int] = None
        length_minutes: Optional[int] = None

#Workout Class includes the addition of a UID
class Workout(BaseModel):
        id: str
        date: dt_date
        calories_burned: Optional[int] = None
        length_minutes: Optional[int] = None

#WorkoutUpdate class to have the client update the workout log
class WorkoutUpdate(BaseModel):
        date: Optional[dt_date] = None
        calories_burned: Optional[int] = None
        length_minutes: Optional[int] = None

#---------------------------Database Setup-------------------------#
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
conn.commit() # Commits changes to the database
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

        workout = add_uuid(workout_in) # Assigns a UUID and date to the workout

        # Workout values tuple. Info inserts in a structure-safe manner.
        data =  workout.model_dump()
        workout_values = (
                data["id"],
                data["date"],
                data["calories_burned"],
                data["length_minutes"]
        ) 
        
        cursor.execute("INSERT INTO logs (id, date, calories_burned, length_minutes) VALUES (?, ?, ?, ?)", workout_values)
        
        conn.commit()
        conn.close()
        return workout

# GET all workouts in the logs table
@app.get("/workouts/")
def get_all_workouts():
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()  

        cursor.execute("SELECT * FROM logs")
        rows = cursor.fetchall()

        conn.close()
        return [
                {               
                        "id": row[0],
                        "date": row[1],
                        "calories_burned": row[2],
                        "length_minutes": row[3],
                } for row in rows
        ]

# GET workout log by UUID
@app.get("/workouts/{id}")
def get_workout_by_id(id: str):
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs WHERE id=?", (id,))
        row = cursor.fetchone()
        if row is None:
                conn.close()
                raise HTTPException(404, detail="Log ID not found", headers=None)
        else:
                conn.close()
                return {
                        "id": row[0],
                        "date": row[1],
                        "calories_burned": row[2],
                        "length_minutes": row[3],
                }

# DELETE all workout logs from table
@app.delete("/workouts/")
def delete_all_workouts():
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs")
        rows = cursor.fetchall()

        cursor.execute("DELETE FROM logs;")
        conn.commit()
        
        conn.close()
        return [
                {
                        "message": f"The following logs have been deleted"
                }
                ],[
                {               
                        "id": row[0],
                        "date": row[1],
                        "calories_burned": row[2],
                        "length_minutes": row[3],
                } for row in rows
        ]

# DELETE specific workout logs based on UUID
@app.delete("/workouts/{id}")
def delete_workout_by_id(id: str):
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs WHERE id=?", (id,))
        row = cursor.fetchone()

        if row is None:
                conn.close()
                raise HTTPException(404, detail="Log ID not found", headers=None)
        else:
                cursor.execute("DELETE FROM logs WHERE id=?", (id,))
                conn.commit()

                conn.close()
                return [
                                {
                                        "message": f"Log {id} deleted"
                                },
                                {
                                        "id": row[0],
                                        "date": row[1],
                                        "calories_burned": row[2],
                                        "length_minutes": row[3],
                                }
                ]
        

# Updates a workout log entry when provided a UUID
@app.patch("/workouts/{id}")
def update_workout_by_id(id:str, workoutUpdate: WorkoutUpdate):
        conn = sqlite3.connect("workouts.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM logs WHERE id=?", (id,))
        row = cursor.fetchone()

        if row is None:
                conn.close()
                raise HTTPException(status_code=404, detail="Workout log not found")
        else:
                updates = workoutUpdate.model_dump(exclude_unset=True)
                if not updates:
                        conn.close()
                        return {"message": "No information provided."}
                else:
                        set_clause = ", ".join([f"{col}=?" for col in updates.keys()])
                        values = list(updates.values())
                        values.append(id)

                        cursor.execute(f"UPDATE logs SET {set_clause} WHERE id=?", values)
                        conn.commit()
                        conn.close()
                        return [
                                {"message": f"Log {id} successfully updated!"},
                                {
                                        "id": row[0],
                                        "date": row[1],
                                        "calories_burned": row[2],
                                        "length_minutes": row[3],
                                }
                        ]


#---------------------------Functions-------------------------#
#Creates a UUID and assigns it to the new workout
def add_uuid(workout_in: WorkoutCreate) -> Workout:
        return Workout(
                id = str(uuid.uuid4()),
                date = workout_in.date,
                calories_burned = workout_in.calories_burned,
                length_minutes = workout_in.length_minutes
        )
