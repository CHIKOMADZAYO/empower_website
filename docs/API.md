# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/auth/login`, `/auth/signup`, `/health`) require a Bearer token:

```
Authorization: Bearer <token>
```

## Endpoints

### Health Check

```
GET /health
Response: { "status": "ok" }
```

### Authentication

#### Login
```
POST /auth/login
Body: {
  "email": "user@example.com",
  "password": "password"
}
Response: {
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

#### Signup
```
POST /auth/signup
Body: {
  "email": "user@example.com",
  "password": "password",
  "full_name": "User Name"
}
Response: {
  "id": 1,
  "email": "user@example.com",
  "full_name": "User Name"
}
```

### Projects

#### List Projects
```
GET /projects
Response: [
  {
    "id": 1,
    "title": "Project Title",
    "description": "Description",
    "status": "active"
  }
]
```

#### Get Project
```
GET /projects/{id}
Response: {
  "id": 1,
  "title": "Project Title",
  "description": "Description",
  "status": "active"
}
```

#### Create Project
```
POST /projects
Body: {
  "title": "New Project",
  "description": "Description"
}
Response: { "id": 1, ... }
```

### Stories

#### List Stories
```
GET /stories
Response: [...]
```

#### Get Story
```
GET /stories/{id}
Response: {...}
```

#### Create Story
```
POST /stories
Body: {
  "title": "Story Title",
  "content": "Story content",
  "project_id": 1
}
Response: { "id": 1, ... }
```

### Contacts

#### Submit Contact Form
```
POST /contact
Body: {
  "name": "Name",
  "email": "email@example.com",
  "message": "Message content"
}
Response: { "id": 1, "status": "received" }
```

## Error Responses

```json
{
  "detail": "Error message"
}
```

Common status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Server Error

## Rate Limiting

No rate limiting currently implemented. See deployment guide for production considerations.
