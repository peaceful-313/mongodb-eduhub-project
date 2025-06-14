"""
EduHub MongoDB Project
Data Engineering Project in AltSchool

This module contains MongoDB operations for the EduHub e-learning platform.
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import json
import random
import re 

class LearningPlatformDB:
    def __init__(self, connection_url="mongodb://localhost:27017/"):
        """
        Initialize the learning platform database connection
        
        Args:
            connection_url (str): MongoDB connection string
        """
        self.mongo_client = MongoClient(connection_url)
        self.platform_db = self.mongo_client['eduhub_db']
        self.setup_database_collections()
        
    def setup_database_collections(self):
        """Set up all collections with validation rules"""
        
        # User schema validation
        user_validation_rules = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["userId", "email", "firstName", "lastName", "role"],
                "properties": {
                    "userId": {"bsonType": "string"},
                    "email": {
                        "bsonType": "string",
                        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                    },
                    "firstName": {"bsonType": "string"},
                    "lastName": {"bsonType": "string"},
                    "role": {
                        "bsonType": "string",
                        "enum": ["student", "instructor"]
                    },
                    "dateJoined": {"bsonType": "date"},
                    "profile": {
                        "bsonType": "object",
                        "properties": {
                            "bio": {"bsonType": "string"},
                            "avatar": {"bsonType": "string"},
                            "skills": {
                                "bsonType": "array",
                                "items": {"bsonType": "string"}
                            }
                        }
                    },
                    "isActive": {"bsonType": "bool"}
                }
            }
        }

        
        # Course schema validation
        course_validation_rules = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["courseId", "title", "instructorId"],
                "properties": {
                    "courseId": {"bsonType": "string"},
                    "title": {"bsonType": "string"},
                    "description": {"bsonType": "string"},
                    "instructorId": {"bsonType": "string"},
                    "category": {"bsonType": "string"},
                    "level": {
                        "bsonType": "string",
                        "enum": ["beginner", "intermediate", "advanced"]
                    },
                    "duration": {"bsonType": "number"},
                    "price": {"bsonType": "number"},
                    "tags": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    },
                    "createdAt": {"bsonType": "date"},
                    "updatedAt": {"bsonType": "date"},
                    "isPublished": {"bsonType": "bool"}
                }
            }
        }
        
        # Create collections with validation
        try:
            self.platform_db.create_collection("users", validator=user_validation_rules)
            self.platform_db.create_collection("courses", validator=course_validation_rules)
            self.platform_db.create_collection("enrollments")
            self.platform_db.create_collection("lessons")
            self.platform_db.create_collection("assignments")
            self.platform_db.create_collection("submissions")
            print("Collections created with validation rules")
        except Exception as error:
            print(f"Collections may already exist: {error}")
        
        # Create performance indexes
        self.create_database_indexes()
        
    def create_database_indexes(self):
        """Create indexes for performance optimization"""
        
        # User collection indexes
        self.platform_db.users.create_index("userId", unique=True)
        self.platform_db.users.create_index("email", unique=True)
        self.platform_db.users.create_index("role")
        
        # Course collection indexes
        self.platform_db.courses.create_index("courseId", unique=True)
        self.platform_db.courses.create_index("title")
        self.platform_db.courses.create_index("category")
        self.platform_db.courses.create_index("instructorId")
        self.platform_db.courses.create_index([("title", "text"), ("description", "text")])
        
        # Enrollment collection indexes
        self.platform_db.enrollments.create_index("enrollmentId", unique=True)
        self.platform_db.enrollments.create_index([("studentId", 1), ("courseId", 1)], unique=True)
        self.platform_db.enrollments.create_index("enrollmentDate")
        
        # Lesson collection indexes
        self.platform_db.lessons.create_index("lessonId", unique=True)
        self.platform_db.lessons.create_index("courseId")
        
        # Assignment collection indexes
        self.platform_db.assignments.create_index("assignmentId", unique=True)
        self.platform_db.assignments.create_index("courseId")
        self.platform_db.assignments.create_index("dueDate")
        
        # Submission collection indexes
        self.platform_db.submissions.create_index("submissionId", unique=True)
        self.platform_db.submissions.create_index([("studentId", 1), ("assignmentId", 1)])
        
        print("Database indexes created successfully")
        
    # PART 1: DATABASE SETUP AND DATA MODELING

    def retrieve_database_info(self):
        """Get information about the database and collections"""
        database_information = {
            "database_name": self.platform_db.name,
            "collections": self.platform_db.list_collection_names(),
            "collection_stats": {}
        }
        
        for collection_name in database_information["collections"]:
            collection_stats = self.platform_db.command("collstats", collection_name)
            database_information["collection_stats"][collection_name] = {
                "count": collection_stats.get("count", 0),
                "size": collection_stats.get("size", 0),
                "avgObjSize": collection_stats.get("avgObjSize", 0)
            }
            
        return database_information
    
    # PART 2: DATA POPULATION

    def populate_sample_data(self):
        """Populate the database with sample data according to project requirements"""
        
        print("Beginning data population process...")
        
        # Clear existing data for fresh start
        self.remove_existing_data()
        
        # Generate and insert users (20 users: mix of students and instructors)
        user_records = self.build_user_records(20)
        self.platform_db.users.insert_many(user_records)
        print(f"Inserted {len(user_records)} user records")
        
        # Generate and insert courses (8 courses)
        course_records = self.build_course_records(8)
        self.platform_db.courses.insert_many(course_records)
        print(f"Inserted {len(course_records)} course records")
        
        # Generate and insert lessons (25 lessons)
        lesson_records = self.build_lesson_records(25)
        self.platform_db.lessons.insert_many(lesson_records)
        print(f"Inserted {len(lesson_records)} lesson records")
        
        # Generate and insert assignments (10 assignments)
        assignment_records = self.build_assignment_records(10)
        self.platform_db.assignments.insert_many(assignment_records)
        print(f"Inserted {len(assignment_records)} assignment records")
        
        # Generate and insert enrollments (15 enrollments)
        enrollment_records = self.build_enrollment_records(15)
        self.platform_db.enrollments.insert_many(enrollment_records)
        print(f"Inserted {len(enrollment_records)} enrollment records")
        
        # Generate and insert submissions (12 submissions)
        submission_records = self.build_submission_records(12)
        self.platform_db.submissions.insert_many(submission_records)
        print(f"Inserted {len(submission_records)} submission records")
        
        print("Data population process completed")

    def build_user_records(self, record_count):
        """Generate sample users with realistic data"""
        user_records = []
        
        # Name and email data
        given_names = ["Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery", "Blake", "Cameron", "Drew"]
        family_names = ["Parker", "Reed", "Brooks", "Hayes", "Cooper", "Bailey", "Ellis", "Gray", "Ward", "Stone"]
        email_domains = ["example.org", "test.com", "demo.edu", "sample.net"]
        technical_skills = ["Python", "Java", "React", "Vue", "Angular", "Node.js", "MongoDB", "PostgreSQL", "Docker", "AWS"]
        
        # Create instructors (25% of users)
        instructor_count = record_count // 4
        for idx in range(instructor_count):
            given_name = random.choice(given_names)
            family_name = random.choice(family_names)
            user_record = {
                "userId": f"INST_{str(idx+1).zfill(3)}",
                "email": f"{given_name.lower()}.{family_name.lower()}@{random.choice(email_domains)}",
                "firstName": given_name,
                "lastName": family_name,
                "role": "instructor",
                "dateJoined": datetime.now() - timedelta(days=random.randint(90, 900)),
                "profile": {
                    "bio": f"Professional instructor specializing in {random.choice(['software development', 'data analysis', 'web technologies'])}",
                    "avatar": f"https://avatars.example.com/instructor_{idx+1}.png",
                    "skills": random.sample(technical_skills, random.randint(4, 7))
                },
                "isActive": True
            }
            user_records.append(user_record)
            
        # Create students (75% of users)
        student_count = record_count - instructor_count
        for idx in range(student_count):
            given_name = random.choice(given_names)
            family_name = random.choice(family_names)
            user_record = {
                "userId": f"STU_{str(idx+1).zfill(3)}",
                "email": f"{given_name.lower()}.{family_name.lower()}{idx}@{random.choice(email_domains)}",
                "firstName": given_name,
                "lastName": family_name,
                "role": "student",
                "dateJoined": datetime.now() - timedelta(days=random.randint(10, 450)),
                "profile": {
                    "bio": f"Eager learner focusing on {random.choice(['programming', 'technology', 'software engineering'])}",
                    "avatar": f"https://avatars.example.com/student_{idx+1}.png",
                    "skills": random.sample(technical_skills, random.randint(2, 5))
                },
                "isActive": True
            }
            user_records.append(user_record)
        
        return user_records
    
    def build_course_records(self, record_count):
        """Generate sample courses with realistic data"""
        available_instructors = list(self.platform_db.users.find({"role": "instructor"}))
        
        course_titles = [
            "Complete Python Programming",
            "Modern Web Development",
            "Data Science Fundamentals",
            "JavaScript for Beginners",
            "Database Management Systems",
            "React Application Development",
            "Backend Development with Node",
            "Introduction to Machine Learning"
        ]
        
        course_categories = ["Programming", "Web Development", "Data Science", "Software Engineering"]
        proficiency_levels = ["beginner", "intermediate", "advanced"]
        
        course_records = []
        for idx in range(min(record_count, len(course_titles))):
            selected_instructor = random.choice(available_instructors)
            course_record = {
                "courseId": f"COURSE_{str(idx+1).zfill(3)}",
                "title": course_titles[idx],
                "description": f"Comprehensive training in {course_titles[idx].lower()} with practical applications and real-world projects.",
                "instructorId": selected_instructor["userId"],
                "category": random.choice(course_categories),
                "level": random.choice(proficiency_levels),
                "duration": random.randint(30, 90),
                "price": random.randint(120, 480),
                "tags": [word.lower() for word in course_titles[idx].split() if len(word) > 3],
                "createdAt": datetime.now() - timedelta(days=random.randint(10, 220)),
                "updatedAt": datetime.now() - timedelta(days=random.randint(1, 50)),
                "isPublished": random.choice([True, False])
            }
            course_records.append(course_record)
            
        return course_records
    
    def build_lesson_records(self, record_count):
        """Generate sample lessons"""
        available_courses = list(self.platform_db.courses.find())
        lesson_records = []
        
        lesson_topics = [
            "Course Introduction",
            "Core Concepts",
            "Data Structures",
            "Algorithms",
            "Best Practices",
            "Error Handling",
            "Testing Strategies",
            "Performance Optimization",
            "Advanced Techniques",
            "Final Project"
        ]
        
        for idx in range(record_count):
            selected_course = random.choice(available_courses)
            selected_topic = random.choice(lesson_topics)
            lesson_record = {
                "lessonId": f"LESSON_{str(idx+1).zfill(3)}",
                "courseId": selected_course["courseId"],
                "title": f"{selected_topic} - {selected_course['title']}",
                "content": f"This lesson explores {selected_topic.lower()} with detailed explanations and practical examples.",
                "duration": random.randint(25, 55),
                "order": (idx % 10) + 1,
                "videoUrl": f"https://videos.example.com/lesson_{idx+1}.mp4",
                "materials": [f"lesson_{idx+1}_notes.pdf", f"lesson_{idx+1}_code.zip"],
                "createdAt": datetime.now() - timedelta(days=random.randint(5, 120))
            }
            lesson_records.append(lesson_record)
        
        return lesson_records
    
    def build_assignment_records(self, record_count):
        """Generate sample assignments"""
        available_courses = list(self.platform_db.courses.find())
        assignment_records = []
        
        assignment_types = [
            "Quiz", "Project", "Exercise", "Case Study", "Lab Work"
        ]
        
        for idx in range(record_count):
            selected_course = random.choice(available_courses)
            assignment_type = random.choice(assignment_types)
            assignment_record = {
                "assignmentId": f"ASSIGN_{str(idx+1).zfill(3)}",
                "courseId": selected_course["courseId"],
                "title": f"{assignment_type}: {selected_course['title']}",
                "description": f"Complete this {assignment_type.lower()} to demonstrate mastery of course concepts.",
                "dueDate": datetime.now() + timedelta(days=random.randint(14, 45)),
                "maxPoints": random.choice([70, 85, 100]),
                "createdAt": datetime.now() - timedelta(days=random.randint(7, 90)),
                "instructions": f"Follow the guidelines to complete this {assignment_type.lower()}. Submit all required components."
            }
            assignment_records.append(assignment_record)
        
        return assignment_records
    
    def build_enrollment_records(self, record_count):
        """Generate sample enrollments"""
        available_students = list(self.platform_db.users.find({"role": "student"}))
        available_courses = list(self.platform_db.courses.find())
        enrollment_records = []
        
        used_combinations = set()
        
        for idx in range(record_count):
            # Ensure unique student-course combinations
            max_attempts = 50
            attempts = 0
            while attempts < max_attempts:
                selected_student = random.choice(available_students)
                selected_course = random.choice(available_courses)
                combination_key = (selected_student["userId"], selected_course["courseId"])
                
                if combination_key not in used_combinations:
                    used_combinations.add(combination_key)
                    break
                attempts += 1
            else:
                continue
            
            enrollment_record = {
                "enrollmentId": f"ENROLL_{str(idx+1).zfill(3)}",
                "studentId": selected_student["userId"],
                "courseId": selected_course["courseId"],
                "enrollmentDate": datetime.now() - timedelta(days=random.randint(7, 90)),
                "status": random.choice(["active", "completed", "dropped"]),
                "progress": random.randint(15, 100),
                "completionDate": datetime.now() - timedelta(days=random.randint(1, 50)) if random.choice([True, False]) else None
            }
            enrollment_records.append(enrollment_record)
        
        return enrollment_records
    
    def build_submission_records(self, record_count):
        """Generate sample submissions"""
        available_assignments = list(self.platform_db.assignments.find())
        available_enrollments = list(self.platform_db.enrollments.find())
        submission_records = []
        
        for idx in range(record_count):
            selected_assignment = random.choice(available_assignments)
            # Find enrollments for the same course
            course_enrollments = [enrollment for enrollment in available_enrollments 
                                if enrollment["courseId"] == selected_assignment["courseId"]]
            
            if course_enrollments:
                selected_enrollment = random.choice(course_enrollments)
                submission_record = {
                    "submissionId": f"SUB_{str(idx+1).zfill(3)}",
                    "assignmentId": selected_assignment["assignmentId"],
                    "studentId": selected_enrollment["studentId"],
                    "submissionDate": datetime.now() - timedelta(days=random.randint(1, 30)),
                    "content": f"Submission for {selected_assignment['title']}. All requirements have been met.",
                    "attachments": [f"submission_{idx+1}.pdf", f"source_code_{idx+1}.py"],
                    "grade": random.randint(55, 100) if random.choice([True, False]) else None,
                    "feedback": "Well done! Good understanding demonstrated." if random.choice([True, False]) else None,
                    "gradedDate": datetime.now() - timedelta(days=random.randint(1, 15)) if random.choice([True, False]) else None
                }
                submission_records.append(submission_record)
        
        return submission_records      
    
    def remove_existing_data(self):
        """Clear all data from collections"""
        collection_names = ["users", "courses", "lessons", "assignments", "enrollments", "submissions"]
        for collection_name in collection_names:
            self.platform_db[collection_name].delete_many({})
        print("Existing data cleared from all collections")

    # PART 3: BASIC CRUD OPERATIONS

    # Task 3.1: CREATE Operations
    def register_new_student(self, email_address, first_name, last_name, biography="", skill_list=None):
        """Add a new student user"""
        if skill_list is None:
            skill_list = []
            
        # Generate unique userId
        existing_students = list(self.platform_db.users.find({"role": "student"}).sort("userId", -1).limit(1))
        next_student_id = 1
        if existing_students:
            current_id = int(existing_students[0]["userId"].split("_")[1])
            next_student_id = current_id + 1
        
        new_student_record = {
            "userId": f"STU_{str(next_student_id).zfill(3)}",
            "email": email_address,
            "firstName": first_name,
            "lastName": last_name,
            "role": "student",
            "dateJoined": datetime.now(),
            "profile": {
                "bio": biography,
                "avatar": f"https://avatars.example.com/student_{next_student_id}.png",
                "skills": skill_list
            },
            "isActive": True
        }
        
        try:
            insert_result = self.platform_db.users.insert_one(new_student_record)
            print(f"New student registered with ID: {insert_result.inserted_id}")
            return insert_result.inserted_id
        except Exception as error:
            print(f"Error registering student: {error}")
            return None
    
    def create_new_course(self, course_title, course_description, instructor_id, course_category, difficulty_level, course_duration, course_price, tag_list=None):
        """Create a new course"""
        if tag_list is None:
            tag_list = []
            
        # Generate unique courseId
        existing_courses = list(self.platform_db.courses.find().sort("courseId", -1).limit(1))
        next_course_id = 1
        if existing_courses:
            current_id = int(existing_courses[0]["courseId"].split("_")[1])
            next_course_id = current_id + 1
        
        new_course_record = {
            "courseId": f"COURSE_{str(next_course_id).zfill(3)}",
            "title": course_title,
            "description": course_description,
            "instructorId": instructor_id,
            "category": course_category,
            "level": difficulty_level,
            "duration": course_duration,
            "price": course_price,
            "tags": tag_list,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "isPublished": False
        }
        
        try:
            insert_result = self.platform_db.courses.insert_one(new_course_record)
            print(f"New course created with ID: {insert_result.inserted_id}")
            return insert_result.inserted_id
        except Exception as error:
            print(f"Error creating course: {error}")
            return None
    
    def register_student_for_course(self, student_id, course_id):
        """Enroll a student in a course"""
        
        # Check if enrollment already exists
        existing_enrollment = self.platform_db.enrollments.find_one({"studentId": student_id, "courseId": course_id})
        if existing_enrollment:
            print("Student is already enrolled in this course")
            return None
        
        # Generate unique enrollmentId
        existing_enrollments = list(self.platform_db.enrollments.find().sort("enrollmentId", -1).limit(1))
        next_enrollment_id = 1
        if existing_enrollments:
            current_id = int(existing_enrollments[0]["enrollmentId"].split("_")[1])
            next_enrollment_id = current_id + 1
        
        new_enrollment_record = {
            "enrollmentId": f"ENROLL_{str(next_enrollment_id).zfill(3)}",
            "studentId": student_id,
            "courseId": course_id,
            "enrollmentDate": datetime.now(),
            "status": "active",
            "progress": 0,
            "completionDate": None
        }
        
        try:
            insert_result = self.platform_db.enrollments.insert_one(new_enrollment_record)
            print(f"Student enrolled with enrollment ID: {insert_result.inserted_id}")
            return insert_result.inserted_id
        except Exception as error:
            print(f"Error enrolling student: {error}")
            return None
    
    def add_lesson_to_course(self, course_id, lesson_title, lesson_content, lesson_duration, video_link="", resource_list=None):
        """Add a new lesson to an existing course"""
        if resource_list is None:
            resource_list = []
            
        # Generate unique lessonId
        existing_lessons = list(self.platform_db.lessons.find().sort("lessonId", -1).limit(1))
        next_lesson_id = 1
        if existing_lessons:
            current_id = int(existing_lessons[0]["lessonId"].split("_")[1])
            next_lesson_id = current_id + 1
        
        # Get the next order number for this course
        course_lessons = list(self.platform_db.lessons.find({"courseId": course_id}).sort("order", -1).limit(1))
        next_order_number = 1
        if course_lessons:
            next_order_number = course_lessons[0]["order"] + 1
        
        new_lesson_record = {
            "lessonId": f"LESSON_{str(next_lesson_id).zfill(3)}",
            "courseId": course_id,
            "title": lesson_title,
            "content": lesson_content,
            "duration": lesson_duration,
            "order": next_order_number,
            "videoUrl": video_link,
            "materials": resource_list,
            "createdAt": datetime.now()
        }
        
        try:
            insert_result = self.platform_db.lessons.insert_one(new_lesson_record)
            print(f"New lesson added with ID: {insert_result.inserted_id}")
            return insert_result.inserted_id
        except Exception as error:
            print(f"Error adding lesson: {error}")
            return None
    
    # Task 3.2: READ Operations
    def find_all_active_students(self):
        """Find all active students"""
        return list(self.platform_db.users.find({"role": "student", "isActive": True}))
    
    def get_course_with_instructor_details(self, course_id):
        """Retrieve course details with instructor information"""
        aggregation_pipeline = [
            {"$match": {"courseId": course_id}},
            {"$lookup": {
                "from": "users",
                "localField": "instructorId",
                "foreignField": "userId",
                "as": "instructor_info"
            }},
            {"$unwind": "$instructor_info"},
            {"$project": {
                "courseId": 1,
                "title": 1,
                "description": 1,
                "category": 1,
                "level": 1,
                "duration": 1,
                "price": 1,
                "tags": 1,
                "instructor_info.firstName": 1,
                "instructor_info.lastName": 1,
                "instructor_info.email": 1,
                "instructor_info.profile.bio": 1
            }}
        ]
        return list(self.platform_db.courses.aggregate(aggregation_pipeline))
    
    def get_courses_by_category(self, category_name):
        """Get all courses in a specific category"""
        return list(self.platform_db.courses.find({"category": category_name}))
    
    def find_enrolled_students_in_course(self, course_id):
        """Find students enrolled in a particular course"""
        aggregation_pipeline = [
            {"$match": {"courseId": course_id}},
            {"$lookup": {
                "from": "users",
                "localField": "studentId",
                "foreignField": "userId",
                "as": "student_info"
            }},
            {"$unwind": "$student_info"},
            {"$project": {
                "enrollmentId": 1,
                "enrollmentDate": 1,
                "status": 1,
                "progress": 1,
                "student_info.firstName": 1,
                "student_info.lastName": 1,
                "student_info.email": 1
            }}
        ]
        return list(self.platform_db.enrollments.aggregate(aggregation_pipeline))
    
    def search_courses_by_title(self, search_query):
        """Search courses by title (case-insensitive, partial match)"""
        search_pattern = re.compile(search_query, re.IGNORECASE)
        return list(self.platform_db.courses.find({"title": {"$regex": search_pattern}}))
    
    # Task 3.3: UPDATE Operations
    def update_user_profile(self, user_id, new_bio=None, new_skills=None, new_avatar=None):
        """Update a user's profile information"""
        update_fields = {}
        if new_bio is not None:
            update_fields["profile.bio"] = new_bio
        if new_skills is not None:
            update_fields["profile.skills"] = new_skills
        if new_avatar is not None:
            update_fields["profile.avatar"] = new_avatar
        
        if update_fields:
            try:
                update_result = self.platform_db.users.update_one(
                    {"userId": user_id},
                    {"$set": update_fields}
                )
                print(f"Profile updated for user {user_id}. Modified count: {update_result.modified_count}")
                return update_result.modified_count
            except Exception as error:
                print(f"Error updating profile: {error}")
                return 0
        else:
            print("No update data provided")
            return 0
    
    def mark_course_as_published(self, course_id):
        """Mark a course as published"""
        try:
            update_result = self.platform_db.courses.update_one(
                {"courseId": course_id},
                {"$set": {"isPublished": True, "updatedAt": datetime.now()}}
            )
            print(f"Course {course_id} marked as published. Modified count: {update_result.modified_count}")
            return update_result.modified_count
        except Exception as error:
            print(f"Error updating course: {error}")
            return 0
    
    def update_assignment_grade(self, submission_id, new_grade, instructor_feedback=None):
        """Update assignment grades"""
        update_fields = {
            "grade": new_grade,
            "gradedDate": datetime.now()
        }
        if instructor_feedback:
            update_fields["feedback"] = instructor_feedback
        
        try:
            update_result = self.platform_db.submissions.update_one(
                {"submissionId": submission_id},
                {"$set": update_fields}
            )
            print(f"Grade updated for submission {submission_id}. Modified count: {update_result.modified_count}")
            return update_result.modified_count
        except Exception as error:
            print(f"Error updating grade: {error}")
            return 0
    
    def add_tags_to_course(self, course_id, additional_tags):
        """Add tags to an existing course"""
        try:
            update_result = self.platform_db.courses.update_one(
                {"courseId": course_id},
                {"$addToSet": {"tags": {"$each": additional_tags}}, "$set": {"updatedAt": datetime.now()}}
            )
            print(f"Tags added to course {course_id}. Modified count: {update_result.modified_count}")
            return update_result.modified_count
        except Exception as error:
            print(f"Error adding tags: {error}")
            return 0
    
    # Task 3.4: DELETE Operations
    def deactivate_user(self, user_id):
        """Remove a user (soft delete by setting isActive to false)"""
        try:
            update_result = self.platform_db.users.update_one(
                {"userId": user_id},
                {"$set": {"isActive": False}}
            )
            print(f"User {user_id} deactivated. Modified count: {update_result.modified_count}")
            return update_result.modified_count
        except Exception as error:
            print(f"Error deactivating user: {error}")
            return 0
    
    def remove_enrollment(self, enrollment_id):
        """Delete an enrollment"""
        try:
            delete_result = self.platform_db.enrollments.delete_one({"enrollmentId": enrollment_id})
            print(f"Enrollment {enrollment_id} removed. Deleted count: {delete_result.deleted_count}")
            return delete_result.deleted_count
        except Exception as error:
            print(f"Error removing enrollment: {error}")
            return 0
    
    def delete_lesson_from_course(self, lesson_id):
        """Remove a lesson from a course"""
        try:
            delete_result = self.platform_db.lessons.delete_one({"lessonId": lesson_id})
            print(f"Lesson {lesson_id} deleted. Deleted count: {delete_result.deleted_count}")
            return delete_result.deleted_count
        except Exception as error:
            print(f"Error deleting lesson: {error}")
            return 0
    
    # PART 4: ADVANCED QUERIES AND AGGREGATION
    
    # Task 4.1: Complex Queries
    def find_courses_by_price_range(self, minimum_price, maximum_price):
        """Find courses with price between minimum_price and maximum_price"""
        return list(self.platform_db.courses.find({"price": {"$gte": minimum_price, "$lte": maximum_price}}))
    
    def get_users_joined_recently(self, months_back=6):
        """Get users who joined in the last N months"""
        cutoff_date = datetime.now() - timedelta(days=30 * months_back)
        return list(self.platform_db.users.find({"dateJoined": {"$gte": cutoff_date}}))
    
    def find_courses_with_tags(self, tag_list):
        """Find courses that have specific tags using $in operator"""
        return list(self.platform_db.courses.find({"tags": {"$in": tag_list}}))
    
    def get_assignments_due_next_week(self):
        """Retrieve assignments with due dates in the next week"""
        current_date = datetime.now()
        next_week_date = current_date + timedelta(weeks=1)
        return list(self.platform_db.assignments.find({
            "dueDate": {"$gte": current_date, "$lte": next_week_date}
        }))
    
    # Task 4.2: Aggregation Pipeline
    def get_course_enrollment_statistics(self):
        """Course Enrollment Statistics: Count total enrollments per course, calculate statistics, group by course category"""
        aggregation_pipeline = [
            # Join with enrollments to count enrollments per course
            {"$lookup": {
                "from": "enrollments",
                "localField": "courseId",
                "foreignField": "courseId",
                "as": "course_enrollments"
            }},
            # Group by category and calculate statistics
            {"$group": {
                "_id": "$category",
                "totalCourses": {"$sum": 1},
                "totalEnrollments": {"$sum": {"$size": "$course_enrollments"}},
                "averagePrice": {"$avg": "$price"},
                "courses": {
                    "$push": {
                        "courseId": "$courseId",
                        "title": "$title",
                        "enrollmentCount": {"$size": "$course_enrollments"},
                        "price": "$price"
                    }
                }
            }},
            # Sort by total enrollments descending
            {"$sort": {"totalEnrollments": -1}}
        ]
        return list(self.platform_db.courses.aggregate(aggregation_pipeline))
    
    def get_student_performance_analysis(self):
        """Student Performance Analysis: Average grade per student, completion rate by course, top-performing students"""
        aggregation_pipeline = [
            # Join submissions with assignments to get course info
            {"$lookup": {
                "from": "assignments",
                "localField": "assignmentId",
                "foreignField": "assignmentId",
                "as": "assignment_info"
            }},
            {"$unwind": "$assignment_info"},
            # Join with users to get student info
            {"$lookup": {
                "from": "users",
                "localField": "studentId",
                "foreignField": "userId",
                "as": "student_info"
            }},
            {"$unwind": "$student_info"},
            # Group by student to calculate average grade
            {"$group": {
                "_id": "$studentId",
                "studentName": {"$first": {"$concat": ["$student_info.firstName", " ", "$student_info.lastName"]}},
                "averageGrade": {"$avg": "$grade"},
                "totalSubmissions": {"$sum": 1},
                "coursesParticipated": {"$addToSet": "$assignment_info.courseId"}
            }},
            # Add calculated fields
            {"$addFields": {
                "coursesCount": {"$size": "$coursesParticipated"}
            }},
            # Sort by average grade descending
            {"$sort": {"averageGrade": -1}}
        ]
        return list(self.platform_db.submissions.aggregate(aggregation_pipeline))
    
    def get_instructor_analytics(self):
        """Instructor Analytics: Total students taught by each instructor, revenue generated per instructor"""
        aggregation_pipeline = [
            # Join courses with users to get instructor info
            {"$lookup": {
                "from": "users",
                "localField": "instructorId",
                "foreignField": "userId",
                "as": "instructor_info"
            }},
            {"$unwind": "$instructor_info"},
            # Join with enrollments to count students
            {"$lookup": {
                "from": "enrollments",
                "localField": "courseId",
                "foreignField": "courseId",
                "as": "course_enrollments"
            }},
            # Group by instructor
            {"$group": {
                "_id": "$instructorId",
                "instructorName": {"$first": {"$concat": ["$instructor_info.firstName", " ", "$instructor_info.lastName"]}},
                "totalCourses": {"$sum": 1},
                "totalStudents": {"$sum": {"$size": "$course_enrollments"}},
                "totalRevenue": {"$sum": {"$multiply": ["$price", {"$size": "$course_enrollments"}]}},
                "courses": {
                    "$push": {
                        "title": "$title",
                        "enrollments": {"$size": "$course_enrollments"},
                        "revenue": {"$multiply": ["$price", {"$size": "$course_enrollments"}]}
                    }
                }
            }},
            # Sort by total revenue descending
            {"$sort": {"totalRevenue": -1}}
        ]
        return list(self.platform_db.courses.aggregate(aggregation_pipeline))
    
    def get_advanced_analytics(self):
        """Advanced Analytics: Monthly enrollment trends, most popular course categories, student engagement metrics"""
        
        # Monthly enrollment trends
        monthly_enrollment_trends = list(self.platform_db.enrollments.aggregate([
            {"$group": {
                "_id": {
                    "year": {"$year": "$enrollmentDate"},
                    "month": {"$month": "$enrollmentDate"}
                },
                "enrollmentCount": {"$sum": 1},
                "activeEnrollments": {"$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}},
                "completedEnrollments": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]))
        
        # Most popular course categories
        popular_course_categories = list(self.platform_db.courses.aggregate([
            {"$lookup": {
                "from": "enrollments",
                "localField": "courseId",
                "foreignField": "courseId",
                "as": "course_enrollments"
            }},
            {"$group": {
                "_id": "$category",
                "totalEnrollments": {"$sum": {"$size": "$course_enrollments"}},
                "courseCount": {"$sum": 1}
            }},
            {"$sort": {"totalEnrollments": -1}}
        ]))
        
        # Student engagement metrics
        student_engagement_metrics = list(self.platform_db.enrollments.aggregate([
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "averageProgress": {"$avg": "$progress"}
            }}
        ]))
        
        return {
            "monthly_trends": monthly_enrollment_trends,
            "popular_categories": popular_course_categories,
            "engagement_metrics": student_engagement_metrics
        }
    
    # PART 5: PERFORMANCE OPTIMIZATION
    
    def analyze_query_performance(self, collection_name, query_filter, explain_mode="executionStats"):
        """Analyze query performance using explain() method"""
        target_collection = self.platform_db[collection_name]
        return target_collection.find(query_filter).explain(explain_mode)
    
    def optimize_slow_queries(self):
        """Optimize common slow queries and document performance improvements"""
        
        print("Analyzing and optimizing query performance...")
        
        # Query 1: Find courses by title (text search)
        print("\n1. Optimizing course title search...")
        start_time = datetime.now()
        course_results = list(self.platform_db.courses.find({"title": {"$regex": "Course", "$options": "i"}}))
        end_time = datetime.now()
        print(f"   Before optimization: {(end_time - start_time).total_seconds():.4f} seconds")
        
        # Create text index if not exists
        try:
            self.platform_db.courses.create_index([("title", "text"), ("description", "text")])
            print("   Text index created for title and description")
        except Exception:
            print("   Text index already exists")
        
        # Query 2: Find enrollments by student and date range
        print("\n2. Optimizing enrollment queries...")
        start_time = datetime.now()
        recent_enrollments = list(self.platform_db.enrollments.find({
            "enrollmentDate": {"$gte": datetime.now() - timedelta(days=30)}
        }))
        end_time = datetime.now()
        print(f"   Query time: {(end_time - start_time).total_seconds():.4f} seconds")
        
        # Query 3: Find assignments by due date
        print("\n3. Optimizing assignment due date queries...")
        start_time = datetime.now()
        upcoming_assignments = list(self.platform_db.assignments.find({
            "dueDate": {"$gte": datetime.now(), "$lte": datetime.now() + timedelta(days=7)}
        }))
        end_time = datetime.now()
        print(f"   Query time: {(end_time - start_time).total_seconds():.4f} seconds")
        
        print("\nPerformance optimization completed!")
    
    # PART 6: DATA VALIDATION AND ERROR HANDLING
    
    def validate_email_format(self, email_address):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email_address) is not None
    
    def handle_duplicate_key_error(self, collection_name, document_data):
        """Handle duplicate key errors"""
        try:
            insert_result = self.platform_db[collection_name].insert_one(document_data)
            print(f"Document inserted successfully: {insert_result.inserted_id}")
            return insert_result.inserted_id
        except Exception as error:
            if "duplicate key" in str(error).lower():
                print(f"Duplicate key error: {error}")
                print("Suggestion: Check for existing records with the same unique field values")
            else:
                print(f"Unexpected error: {error}")
            return None
    
    def validate_and_insert_user(self, user_data):
        """Validate user data before insertion"""
        validation_errors = []
        
        # Check required fields
        required_fields = ["userId", "email", "firstName", "lastName", "role"]
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                validation_errors.append(f"Missing required field: {field}")
        
        # Validate email format
        if "email" in user_data and not self.validate_email_format(user_data["email"]):
            validation_errors.append("Invalid email format")
        
        # Validate role enum
        if "role" in user_data and user_data["role"] not in ["student", "instructor"]:
            validation_errors.append("Role must be 'student' or 'instructor'")
        
        if validation_errors:
            print("Validation errors:")
            for error in validation_errors:
                print(f"   - {error}")
            return None
        
        # If validation passes, insert the user
        return self.handle_duplicate_key_error("users", user_data)
    
    # UTILITY METHODS
    
    def export_sample_data(self, output_filename="sample_data.json"):
        """Export sample data to JSON file"""
        
        exported_data = {}
        collection_names = ["users", "courses", "lessons", "assignments", "enrollments", "submissions"]
        
        for collection_name in collection_names:
            collection_cursor = self.platform_db[collection_name].find()
            document_list = []
            for document in collection_cursor:
                # Convert ObjectId to string for JSON serialization
                document["_id"] = str(document["_id"])
                # Convert datetime objects to ISO format
                for key, value in document.items():
                    if isinstance(value, datetime):
                        document[key] = value.isoformat()
                document_list.append(document)
            exported_data[collection_name] = document_list
        
        with open(output_filename, 'w') as output_file:
            json.dump(exported_data, output_file, indent=2, default=str)
        
        print(f"Sample data exported to {output_filename}")
    
    def get_collection_statistics(self):
        """Get statistics for all collections"""
        collection_stats = {}
        for collection_name in self.platform_db.list_collection_names():
            stats = self.platform_db.command("collstats", collection_name)
            collection_stats[collection_name] = {
                "count": stats.get("count", 0),
                "size": stats.get("size", 0),
                "avgObjSize": stats.get("avgObjSize", 0),
                "indexes": stats.get("nindexes", 0)
            }
        return collection_stats
    
    def close_connection(self):
        """Close the database connection"""
        self.mongo_client.close()
        print("Database connection closed")

if __name__ == "__main__":
    # Initialize the database
    learning_platform = LearningPlatformDB()
    
    # Populate sample data
    print("Starting EduHub Database Project...")
    learning_platform.populate_sample_data()
    
    # Display database info
    print("\nDatabase Information:")
    database_info = learning_platform.retrieve_database_info()
    for collection, stats in database_info["collection_stats"].items():
        print(f"   {collection}: {stats['count']} documents")
    
    # Export sample data
    learning_platform.export_sample_data()
    
    print("\nEduHub Database setup completed successfully!")
