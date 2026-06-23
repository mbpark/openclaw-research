#!/bin/zsh
# Test 3 - Session Length Testing
# Run these queries in order for Gemini

CONTEXT="We're building a Flask app with user authentication using SQLAlchemy, SQLite, Flask-Login, and WTForms for forms. Requirements: (1) username/email/password fields, (2) login/logout, (3) session management, (4) password hashing, (5) SQLite storage, (6) CSRF protection, (7) Python 3.11+"

# Turn 1 - User Model (DONE)
echo "=== Turn 1 ==="
gemini -p "${CONTEXT}. What would a SQLAlchemy user model look like?" 2>/dev/null | head -40

# Turn 2 - Login View (DONE)
echo "=== Turn 2 ==="
gemini -p "${CONTEXT}. We've created the User model. Now let's add the login view function with proper validation." 2>/dev/null | head -40

# Turn 3 - Continue building
echo "=== Turn 3 ==="
gemini -p "${CONTEXT}. Great login view. Now let's add the database setup code and migration commands for the initial migration." 2>/dev/null | head -40

# Turn 4 - CHECK-IN 1: Verify context retention
echo "=== Turn 4 - CHECK-IN ==="
gemini -p "${CONTEXT}. Before continuing, can you remind me what requirements we had from the start?" 2>/dev/null | head -20

# Turn 5 - CSRF Protection
echo "=== Turn 5 ==="
gemini -p "${CONTEXT}. Now let's add CSRF protection - how do we integrate WTForms CSRF?" 2>/dev/null | head -40

# Turn 6 - Routes
echo "=== Turn 6 ==="
gemini -p "${CONTEXT}. Let's write the route decorators and URL configuration for all our views." 2>/dev/null | head -40

# Turn 7 - CHECK-IN 2: What's remaining?
echo "=== Turn 7 - CHECK-IN ==="
gemini -p "${CONTEXT}. What are all the requirements we still need to implement?" 2>/dev/null | head -20

# Turn 8 - Session Management
echo "=== Turn 8 ==="
gemini -p "${CONTEXT}. Now the session management piece - setting sessions on login, clearing on logout." 2>/dev/null | head -40

# Turn 9 - Templates
echo "=== Turn 9 ==="
gemini -p "${CONTEXT}. Let's create basic HTML templates for the forms and dashboard." 2>/dev/null | head -40

# Turn 10 - FINAL: Reference turn 1
echo "=== Turn 10 - FINAL ==="
gemini -p "${CONTEXT}. I want to make sure we've hit all our original requirements. Can you review the list from the start and tell me what we've covered and what's still missing?" 2>/dev/null | head -20