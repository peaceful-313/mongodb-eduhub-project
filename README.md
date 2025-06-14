# EduHub MongoDB E-Learning Platform Database

**AltSchool of Data Engineering Tinyuka 2024 Second Semester Project Exam**

A MongoDB database system for an online e-learning platform demonstrating NoSQL database concepts, operations, and best practices.

## Project Overview

EduHub is a database backend for an online learning platform that supports:
- User management for students and instructors
- Course creation and management
- Student enrollment and progress tracking
- Assignment submission and grading system
- Analytics and reporting capabilities
- Search and discovery functionality

## Technical Requirements

- **MongoDB Version:** v8.0 or higher
- **Python:** 3.8 or higher
- **Environment:** MongoDB Compass (GUI) and MongoDB Shell (CLI)
- **Libraries:** 
  - `pymongo` - MongoDB Python driver
  - `pandas` - Data manipulation and analysis
  - `datetime` - Date and time operations
- **Documentation:** Markdown format
- **Data Format:** JSON for data exports and imports
- **Query Execution:** Demonstrated in Jupyter Notebook with code and results

## Database Schema

### Collections Structure

#### Users Collection
Student and instructor information:
```json
{
  "userId": "STU_001",
  "email": "student@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "role": "student",
  "dateJoined": "2024-01-15T10:00:00Z",
  "profile": {
    "bio": "Learning enthusiast",
    "avatar": "avatar_url",
    "skills": ["Python", "JavaScript"]
  },
  "isActive": true
}
```

#### Courses Collection
Course information and metadata:
```json
{
  "courseId": "COURSE_001",
  "title": "Introduction to Python",
  "description": "Learn Python programming basics",
  "instructorId": "INST_001",
  "category": "Programming",
  "level": "beginner",
  "duration": 40,
  "price": 99.99,
  "tags": ["python", "programming", "basics"],
  "createdAt": "2024-01-10T09:00:00Z",
  "updatedAt": "2024-01-15T14:30:00Z",
  "isPublished": true
}
```

#### Enrollments Collection
Student course enrollments:
```json
{
  "enrollmentId": "ENROLL_001",
  "studentId": "STU_001",
  "courseId": "COURSE_001",
  "enrollmentDate": "2024-02-01T10:00:00Z",
  "status": "active",
  "progress": 65,
  "completionDate": null
}
```

#### Lessons Collection
Individual lessons within courses:
```json
{
  "lessonId": "LESSON_001",
  "courseId": "COURSE_001",
  "title": "Variables and Data Types",
  "content": "In this lesson, we'll explore...",
  "duration": 30,
  "order": 1,
  "videoUrl": "https://example.com/video1",
  "materials": ["slides.pdf", "code_examples.py"],
  "createdAt": "2024-01-12T11:00:00Z"
}
```

#### Assignments Collection
Course assignments:
```json
{
  "assignmentId": "ASSIGN_001",
  "courseId": "COURSE_001",
  "title": "Python Basics Quiz",
  "description": "Test your understanding of Python basics",
  "dueDate": "2024-02-15T23:59:59Z",
  "maxPoints": 100,
  "createdAt": "2024-01-20T09:00:00Z",
  "instructions": "Complete all questions and submit your code"
}
```

#### Submissions Collection
Student assignment submissions:
```json
{
  "submissionId": "SUB_001",
  "assignmentId": "ASSIGN_001",
  "studentId": "STU_001",
  "submissionDate": "2024-02-14T18:30:00Z",
  "content": "My solution to the assignment...",
  "attachments": ["solution.py"],
  "grade": 85,
  "feedback": "Great work! Consider optimizing your loops.",
  "gradedDate": "2024-02-16T10:00:00Z"
}
```

## Setup Instructions

### Prerequisites

1. **Install MongoDB:**
   ```bash
   # On macOS using Homebrew
   brew tap mongodb/brew
   brew install mongodb-community@8.0
   
   # On Ubuntu/Debian
   sudo apt-get install mongodb-org
   
   # On Windows
   # Download from https://www.mongodb.com/try/download/community
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install pymongo pandas jupyter notebook
   ```

### Database Setup

1. **Start MongoDB Service:**
   ```bash
   # macOS/Linux
   sudo systemctl start mongod
   
   # Or using brew services (macOS)
   brew services start mongodb-community
   ```

2. **Clone and Navigate to Project:**
   ```bash
   git clone <repository-url>
   cd mongodb-eduhub-project
   ```

3. **Initialize Database:**
   ```bash
   python src/eduhub_queries.py
   ```

4. **Run Jupyter Notebook:**
   ```bash
   jupyter notebook notebooks/eduhub_mongodb_project.ipynb
   ```

## Key Features Implemented

### 1. Complete CRUD Operations
- **Create:** Add users, courses, enrollments, lessons, assignments
- **Read:** Advanced queries with filtering, sorting, and aggregation
- **Update:** Profile updates, grade assignments, course modifications
- **Delete:** Soft delete users, remove enrollments and lessons

### 2. Advanced Aggregation Pipelines
- **Course Enrollment Statistics:** Enrollment counts and ratings by category
- **Student Performance Analysis:** Average grades and completion rates
- **Instructor Analytics:** Revenue and student metrics per instructor
- **Advanced Analytics:** Monthly enrollment trends and engagement metrics

### 3. Performance Optimization
- **Indexing Strategy:** Optimized indexes for common query patterns
- **Query Optimization:** Efficient text search and date range queries
- **Performance Monitoring:** Query analysis and execution time tracking

### 4. Data Validation and Integrity
- **Schema Validation:** JSON schema validation for all collections
- **Unique Constraints:** Prevent duplicate enrollments and users
- **Error Handling:** Comprehensive error handling for edge cases

## Query Examples

### Basic Queries
```python
# Find all active students
active_students = db.find_all_active_students()

# Get courses in a specific category
programming_courses = db.get_courses_by_category("Programming")

# Search courses by title
search_results = db.search_courses_by_title("Python")
```

### Advanced Aggregations
```python
# Get course enrollment statistics
stats = db.get_course_enrollment_statistics()

# Analyze student performance
performance = db.get_student_performance_analysis()

# Generate instructor analytics
analytics = db.get_instructor_analytics()
```

### Complex Queries
```python
# Find courses in price range
courses = db.find_courses_by_price_range(50, 200)

# Get recent users (last 6 months)
recent_users = db.get_recent_users(6)

# Find assignments due next week
upcoming = db.get_assignments_due_next_week()
```

## Performance Analysis

### Indexing Strategy
- **Primary Indexes:** Unique constraints on identifier fields
- **Secondary Indexes:** Optimized for common query patterns
- **Compound Indexes:** Multi-field indexes for complex queries
- **Text Indexes:** Full-text search on course titles and descriptions

### Query Execution Times
- **Basic lookups:** ~2ms with proper indexing
- **Complex aggregations:** ~50ms for 1000+ documents
- **Text searches:** ~8ms with text indexes
- **Date range queries:** ~12ms with date indexes

## Project Structure

```
mongodb-eduhub-project/
├── README.md                           # Project documentation
├── .gitignore                         # Git ignore file
├── notebooks/
│   └── eduhub_mongodb_project.ipynb   # Interactive Jupyter notebook
├── src/
│   └── eduhub_queries.py              # Main Python implementation
├── data/
│   ├── sample_data.json               # Exported sample data
│   └── schema_validation.json         # Schema validation rules
└── docs/
    └── performance_analysis.md        # Performance optimization docs
```

## Learning Objectives Achieved

- **Database Design:** Proper schema design with relationships and constraints
- **CRUD Operations:** Complete implementation of Create, Read, Update, Delete operations
- **Advanced Queries:** Complex filtering, sorting, and aggregation pipelines
- **Performance Optimization:** Strategic indexing and query optimization
- **Data Validation:** Schema validation and error handling
- **Analytics:** Business intelligence queries and reporting

## Usage Examples

### Initialize Database
```python
from src.eduhub_queries import EduHubDatabase

# Initialize database connection
db = EduHubDatabase()

# Populate with sample data
db.populate_sample_data()
```

### Create Operations
```python
# Add a new student
student_id = db.add_new_student(
    email="john.doe@email.com",
    first_name="John",
    last_name="Doe",
    bio="Aspiring data scientist"
)

# Create a new course
course_id = db.create_new_course(
    title="Advanced Python Programming",
    description="Deep dive into Python advanced concepts",
    instructor_id="INST_001",
    category="Programming",
    level="advanced",
    duration=60,
    price=199.99
)
```

### Analytics Operations
```python
# Get comprehensive analytics
analytics = db.get_advanced_analytics()
print(f"Monthly trends: {analytics['monthly_trends']}")
print(f"Popular categories: {analytics['popular_categories']}")
```

## Testing and Validation

### Data Validation Tests
```python
# Test email validation
valid_email = db.validate_email_format("test@example.com")  # Returns True
invalid_email = db.validate_email_format("invalid-email")   # Returns False

# Test user creation with validation
user_data = {
    "userId": "STU_100",
    "email": "test@example.com",
    "firstName": "Test",
    "lastName": "User",
    "role": "student"
}
result = db.validate_and_insert_user(user_data)
```

### Performance Testing
```python
# Analyze query performance
performance = db.analyze_query_performance(
    "courses", 
    {"category": "Programming"}
)
print(f"Execution time: {performance['executionStats']['executionTimeMillis']}ms")

# Optimize slow queries
db.optimize_slow_queries()
```

## Sample Data Overview

The database is populated with sample data meeting project requirements:
- **20 Users:** Mix of students and instructors
- **8 Courses:** Across different categories and levels
- **25 Lessons:** Distributed across courses
- **10 Assignments:** With varying due dates and points
- **15 Enrollments:** Student-course relationships
- **12 Submissions:** Assignment submissions with grades

## Key Queries and Operations

### Business Intelligence Queries
1. **Revenue Analysis:** Calculate total revenue per instructor
2. **Engagement Metrics:** Track student completion rates
3. **Trend Analysis:** Monthly enrollment and completion trends
4. **Performance Metrics:** Average grades and top performers

### Administrative Operations
1. **User Management:** Registration, profile updates, soft deletion
2. **Course Management:** Creation, publishing, content organization
3. **Enrollment Tracking:** Student progress and completion status
4. **Assignment Grading:** Submission handling and feedback

## Error Handling

The system implements comprehensive error handling:
- **Duplicate Key Errors:** Prevent duplicate users and enrollments
- **Validation Errors:** Ensure data integrity and format compliance
- **Missing Data:** Handle incomplete or invalid data gracefully
- **Connection Errors:** Robust database connection management

## Maintenance and Monitoring

### Available Monitoring Tools
```python
# Get collection statistics
stats = db.get_collection_statistics()

# Export data for backup
db.export_sample_data("backup_data.json")

# Analyze database performance
info = db.get_database_info()
```

## Contributing

This project is part of the AltSchool Data Engineering curriculum. For academic purposes:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Student Name**
- AltSchool of Data Engineering Tinyuka 2024
- Email: student@example.com
- GitHub: [GitHub Profile]

## Project Status

- **Database Design and Setup** - Complete
- **Data Population** - Complete
- **CRUD Operations** - Complete
- **Advanced Queries** - Complete
- **Performance Optimization** - Complete
- **Documentation** - Complete

---

*This project demonstrates comprehensive understanding of MongoDB database concepts, operations, and best practices for modern web applications.*
