employees = [
    {
        "id": 1,
        "name": "Prajwal",
        "email": "prajwal@example.com",
        "role": "Backend Developer",
        "salary": 45000
    },
    {
        "id": 2,
        "name": "Rahul",
        "email": "rahul@example.com",
        "role": "Tester",
        "salary": 35000
    },
    {
        "id": 3,
        "name": "Manu",
        "email": "manu@example.com",
        "role": "Backend Developer",
        "salary": 55000
    }
]


def get_employees_by_role(role):
    matching_employees = []

    for employee in employees:
        if employee["role"].lower() == role.lower():
            matching_employees.append(employee)

    if not matching_employees:
        print("No employees found for this role.")

    return matching_employees


for employee in employees:
    print(f"ID: {employee['id']}, Name: {employee['name']}, Email: {employee['email']}, Role: {employee['role']}, Salary: {employee['salary']}")
employee_id = int(input("Enter the employee ID to search: "))

found_employee = None

for employee in employees:
    if employee['id'] == employee_id:
        found_employee = employee
        break
if found_employee:
    print(f"Employee found: ID: {found_employee['id']}, Name: {found_employee['name']}, Email: {found_employee['email']}, Role: {found_employee['role']}, Salary: {found_employee['salary']}")
else:
    print("Employee not found.")

append_employees = input("Do you want to append a new employee? (yes/no): ").strip().lower()
if append_employees == 'yes':
    new_employee = {}
    new_employee['id'] = int(input("Enter employee ID: "))
    new_employee['name'] = input("Enter employee name: ")
    new_employee['email'] = input("Enter employee email: ")
    new_employee['role'] = input("Enter employee role: ")
    new_employee['salary'] = int(input("Enter employee salary: "))
    
    employees.append(new_employee)
    print("New employee added successfully.")

for employee in employees:
    print(f"ID: {employee['id']}, Name: {employee['name']}, Email: {employee['email']}, Role: {employee['role']}, Salary: {employee['salary']}")