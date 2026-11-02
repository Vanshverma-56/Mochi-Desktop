
from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.task_service import TaskService


# Initialise the database and task service.
db = Database()
initialise_database(db)

tasks = TaskService(db)

print("\n--- MOCHI TASK SERVICE TEST ---")

# 1. Create a task.
task = tasks.create_task(
    title="Complete Mochi development",
    description="Test the task management system.",
    priority="High",
    category="Development",
)

task_id = task["id"]

print("\n1. Task created:")
print(task)

# 2. Retrieve the task.
retrieved = tasks.get_task(task_id)

print("\n2. Task retrieved:")
print(retrieved["title"])

# 3. Update the task.
updated = tasks.update_task(
    task_id,
    title="Complete Mochi development milestone",
    description="Updated task description.",
    priority="Medium",
    category="Development",
)

print("\n3. Task updated:")
print(updated["title"])
print("Priority:", updated["priority"])

# 4. Mark task as completed.
tasks.set_task_completed(task_id, True)

completed = tasks.get_task(task_id)

print("\n4. Task completion:")
print("Completed:", bool(completed["is_completed"]))

# 5. Retrieve all tasks.
all_tasks = tasks.get_all_tasks()

print("\n5. Total tasks in database:", len(all_tasks))

# 6. Delete the test task.
deleted = tasks.delete_task(task_id)

print("\n6. Test task deleted:", deleted)

# Verify deletion.
print("Task still exists:", tasks.get_task(task_id) is not None)

db.close()

print("\n--- ALL TESTS COMPLETED ---")
