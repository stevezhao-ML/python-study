# Day 4 – Student Management System (OOP Refactor)

This project is an upgraded version of my Day 3 Student Management System.
On Day 4, I refactored the code into an **object-oriented design** using a `StudentManager` class, improved code structure, and kept data persistence and CSV export.

---

## ✅ Features

- Add a student (with input validation)
- View all students in an aligned table
- Search students by name (case-insensitive, partial match)
- Delete a student by index (with confirmation)
- Persist data using `students.json`
- Export data to `students_in_d3.csv`

---

## 🧱 Project Structure

Day04-Student-Management-System/
├── main.py
├── student_manager.py
├── students.json
└── students_in_d3.csv


- `main.py` — CLI entry point (menu + routing)
- `student_manager.py` — core logic in `StudentManager` class
- `students.json` — local data storage (auto-created/updated)
- `students_in_d3.csv` — exported CSV file

---

## ▶️ How to Run

Make sure Python 3 is installed, then run:

```bash
python main.py
🧠 What I Practiced (Day 4)
Object-Oriented Programming (OOP): classes, methods, self

Encapsulation: keeping data and logic inside StudentManager

Clean project structure: separating entry point and business logic

File I/O:

JSON persistence (json.load / json.dump)

CSV export (csv.DictWriter)

Defensive programming: empty checks, input validation

🔧 Notes
Data files are stored in the same directory as the Python code using __file__-based paths.

Student age is stored as an integer for future analytics.

🔮 Possible Next Improvements
Add “Edit student” feature

Add sorting (by name / age)

Add basic statistics (average age, min/max, distribution)

Use Pandas for data analysis

Add automated tests

👤 Author
Steve Zhao
Day 4 of Python-to-AI Application Learning Path