# Smart Attendance Management - AI Development Rules

## 1. Project Overview

This repository contains the Smart Attendance Management System.

The project should be developed in a modular, maintainable, secure, and scalable way.

Do not make major architectural decisions without documenting them first.

---

## 2. AI Agent Responsibilities

### ChatGPT

Use ChatGPT primarily for:

- Project planning

- Requirement analysis

- Architecture decisions

- Database design

- API design

- Task breakdown

- Code review

- Debugging guidance

- Testing strategy

- Documentation review

### Cursor

Use Cursor primarily for:

- Day-to-day coding

- Implementing assigned tasks

- Refactoring

- Debugging

- Writing tests

- Running the application locally

- Reviewing changes before committing

### Antigravity

Use Antigravity primarily for:

- Large multi-file implementation tasks

- Independent feature development

- Repository analysis

- Test execution

- Automated debugging

- Implementation of clearly defined tasks

---

## 3. Source of Truth

The following files are the project's planning documents:

- `REQUIREMENTS.md` — functional and non-functional requirements

- `ARCHITECTURE.md` — system architecture and technical decisions

- `TASKS.md` — development tasks and progress

- `AGENTS.md` — AI development rules

Do not contradict these documents.

If a requirement or architecture decision needs to change:

1. Identify the change.

2. Update the appropriate documentation.

3. Then modify the implementation.

---

## 4. Coding Principles

Follow these principles:

- Keep code simple and readable.

- Use modular architecture.

- Avoid unnecessary complexity.

- Avoid duplicate code.

- Use meaningful names.

- Keep functions focused on one responsibility.

- Validate user input.

- Handle errors properly.

- Do not hard-code secrets.

- Use environment variables for sensitive configuration.

- Do not modify unrelated files.

- Do not introduce unnecessary dependencies.

---

## 5. Security Rules

Never:

- Commit passwords.

- Commit API keys.

- Commit database credentials.

- Commit authentication tokens.

- Hard-code secrets.

Use environment variables for sensitive information.

Always validate and sanitize user-controlled input.

---

## 6. Database Rules

Before modifying the database:

- Check the existing schema.

- Preserve existing relationships.

- Avoid unnecessary duplicate fields.

- Use appropriate constraints.

- Maintain data integrity.

Database changes must be documented.

---

## 7. API Rules

Every API should have:

- Clear endpoint naming

- Input validation

- Proper HTTP methods

- Appropriate status codes

- Error handling

- Consistent response structure

Do not expose sensitive information through API responses.

---

## 8. Testing Rules

Before considering a feature complete:

1. Run the application.

2. Test the feature.

3. Test normal inputs.

4. Test invalid inputs.

5. Test important edge cases.

6. Fix errors.

7. Run existing tests again.

Do not remove tests just because they fail.

---

## 9. Git Rules

Use meaningful commits.

Examples:

- `feat: add student registration`

- `feat: add attendance API`

- `fix: resolve attendance calculation`

- `test: add student API tests`

- `docs: update architecture`

Do not commit unrelated changes together.

Before committing:

- Review changed files.

- Remove unnecessary files.

- Check for secrets.

- Run relevant tests.

---

## 10. AI Agent Safety Rules

Before making a large change:

- Inspect the existing code.

- Understand the current architecture.

- Identify affected files.

- Avoid overwriting working functionality.

Do not:

- Rewrite the entire project unnecessarily.

- Change the technology stack without approval.

- Delete working functionality without a reason.

- Create duplicate implementations.

- Modify unrelated modules.

If requirements are unclear, stop and ask for clarification instead of guessing.

---

## 11. Task Completion Format

When completing a task, report:

### What was implemented

- List the changes.

### Files changed

- List modified/created files.

### Testing

- Explain what was tested.

### Issues

- Mention remaining problems.

### Next step

- Suggest the next logical task.

---

## 12. Important Rule

The goal is not simply to make the code work.

The goal is to build a project that is:

- Correct

- Maintainable

- Secure

- Testable

- Understandable

- Scalable

- Suitable for demonstration and evaluation