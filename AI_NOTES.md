# AI_NOTES.md

## 1. Which parts were AI-generated vs. written by me

- AI-generated (Claude): Initial version of `src/storage.py`, `src/main.py`, `tests/test_api.py`, `README.md`, and the initial structure of this file.
- Written/decided by me: I reviewed the generated code, understood how it worked, and verified that it met all the assignment requirements. I verified the project structure, tested all the required API endpoints, confirmed that the README commands worked correctly, and completed this AI_NOTES file based on my actual development and testing process. I also used ChatGPT for code review, testing guidance, and final verification before submission.

## 2. What I validated, tested, or changed in the AI's output, and why

- I created a clean virtual environment, installed the dependencies, and ran:

  ```bash
  python -m unittest discover -s tests -v
  ```

  to confirm that all 15 unit tests passed successfully.

- I manually tested every required API endpoint using PowerShell (`Invoke-RestMethod`), including adding expenses, viewing all expenses, filtering by category, calculating total expenses, and deleting expenses.

- I verified that invalid inputs such as missing required fields, negative amounts, and non-numeric amounts returned appropriate `400 Bad Request` responses instead of causing the application to fail.

- I reviewed the project structure and confirmed that it matched the assignment requirements. I also verified that the commands provided in the README worked correctly before submission.

- I kept the implementation simple, readable, and focused on the assignment requirements instead of adding unnecessary complexity.

## 3. AI suggestions I decided not to use, and why

- Claude suggested using SQLite instead of a JSON file. I chose to keep JSON file storage because the assignment explicitly stated that a database was not required.

- I chose not to add unnecessary features beyond the assignment requirements, except for the optional search endpoint, so that the project remained simple, focused, and easy to understand.

- I kept the Flask implementation instead of switching to another framework because it fully satisfied the assignment requirements and was easier to verify and maintain.

## Known limitations (optional but honest)

- The application stores data in a local JSON file, which is suitable for this take-home assignment but is not intended for production-scale concurrent usage. A production application would typically use a database.

- Authentication and authorization are outside the scope of this assignment.