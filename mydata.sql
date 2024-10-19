CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    batch TEXT NOT NULL,
    academic_performance INTEGER NOT NULL,
    hackathon_participation INTEGER NOT NULL,
    papers_presented INTEGER NOT NULL,
    overall_score REAL
);
