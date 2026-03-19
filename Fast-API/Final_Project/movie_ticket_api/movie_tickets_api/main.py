from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="Movie Ticket Booking System")

# --- DATABASE (In-Memory) ---
movies = [
    {"id": 1, "title": "Inception", "genre": "Sci-Fi", "price": 12.0, "seats": 50},
    {"id": 2, "title": "The Dark Knight", "genre": "Action", "price": 15.0, "seats": 30},
]
bookings = []

# --- PYDANTIC MODELS ---
class Movie(BaseModel):
    id: int
    title: str = Field(..., min_length=1)
    genre: str
    price: float = Field(..., gt=0)
    seats: int

class BookingRequest(BaseModel):
    movie_id: int
    user_name: str
    tickets: int = Field(..., gt=0)

# --- HELPER FUNCTIONS ---
def find_movie(movie_id: int):
    return next((m for m in movies if m["id"] == movie_id), None)

# --- DAY 1-3: GET & POST APIs ---

@app.get("/")
def home():
    return {"message": "Welcome to the Movie Ticket Booking API"}

@app.get("/movies")
def list_movies():
    return movies

@app.get("/movies/summary")
def get_summary():
    return {"total_movies": len(movies), "total_bookings": len(bookings)}

# Fixed route before variable route (Rule Check!)
@app.get("/movies/search")
def search_movies(keyword: str = Query(None)):
    if keyword:
        return [m for m in movies if keyword.lower() in m["title"].lower()]
    return movies

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.post("/movies", status_code=201)
def add_movie(movie: Movie):
    movies.append(movie.dict())
    return {"message": "Movie added successfully", "data": movie}

# --- DAY 4: CRUD OPERATIONS ---

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, updated_movie: Movie):
    for index, m in enumerate(movies):
        if m["id"] == movie_id:
            movies[index] = updated_movie.dict()
            return {"message": "Movie updated"}
    raise HTTPException(status_code=404, detail="Movie not found")

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    global movies
    movies = [m for m in movies if m["id"] != movie_id]
    return {"message": "Movie deleted"}

# --- DAY 5: MULTI-STEP WORKFLOW (Booking -> Payment -> History) ---

@app.post("/booking/reserve")
def reserve_seat(request: BookingRequest):
    movie = find_movie(request.movie_id)
    if not movie or movie["seats"] < request.tickets:
        raise HTTPException(status_code=400, detail="Not enough seats")
    
    booking_id = len(bookings) + 1
    new_booking = {**request.dict(), "id": booking_id, "status": "Reserved"}
    bookings.append(new_booking)
    return {"booking_id": booking_id, "status": "Reserved. Please proceed to payment."}

@app.post("/booking/payment/{booking_id}")
def process_payment(booking_id: int):
    for b in bookings:
        if b["id"] == booking_id:
            b["status"] = "Confirmed"
            # Reduce inventory
            movie = find_movie(b["movie_id"])
            movie["seats"] -= b["tickets"]
            return {"message": "Payment successful!", "ticket": b}
    raise HTTPException(status_code=404, detail="Booking not found")

@app.get("/booking/history")
def get_history():
    return bookings

# --- DAY 6: ADVANCED APIs (Pagination & Sorting) ---

@app.get("/browse")
def browse_movies(
    sort_by: str = "title", 
    page: int = Query(1, gt=0), 
    size: int = Query(5, gt=0)
):
    sorted_list = sorted(movies, key=lambda x: x.get(sort_by, "title"))
    start = (page - 1) * size
    end = start + size
    return sorted_list[start:end]