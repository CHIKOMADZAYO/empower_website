"""Mock data for local development and demos."""

MOCK_USERS = [
    {
        "username": "alice",
        "email": "alice@empower.org",
        "password": "admin-pass-123",
        "role": "admin",
    },
    {
        "username": "william",
        "email": "william@empower.org",
        "password": "editor-pass-123",
        "role": "editor",
    },
    {
        "username": "ben",
        "email": "ben@empower.org",
        "password": "viewer-pass-123",
        "role": "viewer",
    },
]

MOCK_PROJECTS = [
    {
        "name": "Learning",
        "category": "Education",
        "summary": "Open doors to opportunity.",
        "description": (
            "We support mentors, teachers, and young people with learning spaces, "
            "practical skills, and pathways into work."
        ),
    },
    {
        "name": "Wellbeing",
        "category": "Health",
        "summary": "Care that meets people where they are.",
        "description": (
            "Local health champions connect families to trusted information, care, and "
            "one another."
        ),
    },
    {
        "name": "Opportunity",
        "category": "Livelihoods",
        "summary": "Ideas with room to grow.",
        "description": (
            "We help community enterprises build resilient livelihoods through training, "
            "networks, and patient support."
        ),
    },
]

MOCK_STORIES = [
    {
        "title": "The library became our meeting place.",
        "category": "Learning",
        "excerpt": (
            "A community reading room became a place for young people to study, meet, "
            "and see new possibilities."
        ),
        "year": 2025,
    },
    {
        "title": "We are growing something that is ours.",
        "category": "Opportunity",
        "excerpt": (
            "A cooperative of local makers is building reliable incomes while keeping "
            "traditional knowledge alive."
        ),
        "year": 2024,
    },
    {
        "title": "A safe space changed how we show up.",
        "category": "Wellbeing",
        "excerpt": (
            "Support groups and mentorship helped young adults rebuild confidence, find "
            "care, and connect with local resources."
        ),
        "year": 2023,
    },
]

MOCK_CONTACT_MESSAGES = [
    {
        "name": "Amina Yusuf",
        "email": "amina@example.com",
        "message": (
            "Hi, we are looking for partners to run a community skills workshop for young "
            "people this autumn."
        ),
    },
    {
        "name": "Daniel Brooks",
        "email": "daniel@example.com",
        "message": (
            "Can you tell us more about how we can volunteer for the wellbeing and youth "
            "support programmes?"
        ),
    },
]
