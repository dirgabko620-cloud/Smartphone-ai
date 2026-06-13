# Smartphone AI - Architecture & Development Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                           │
│                  (Port 3000 - Termux)                        │
│         Chat | Generate Images | Generate Code              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend                            │
│                 (Port 8000 - Python)                         │
│    Auth | Chat | Generation | Analytics | WebSocket          │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQL
┌──────────────────────▼──────────────────────────────────────┐
│                  SQLAlchemy ORM                              │
│         SQLite (Dev) / PostgreSQL (Prod)                    │
│    Users | Chat Messages | Generated Content                │
└─────────────────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼──┐      ┌───▼──┐      ┌───▼──┐
    │Ollama│   │OpenAI│   │Hugging│
    │Local │   │  API  │   │ Face  │
    │LLM  │   │       │   │       │
    └──────┘      └──────┘      └──────┘
```

## Data Flow

### Chat Flow
1. User sends message from frontend
2. Frontend validates and sends to `/api/chat`
3. Backend receives with JWT auth
4. Backend processes with selected AI model
5. Response saved to database
6. Response sent back to frontend in real-time
7. Frontend displays with markdown formatting

### Image Generation Flow
1. User submits prompt and size preference
2. Frontend sends to `/api/generate/image`
3. Backend routes to appropriate model
4. Model generates image (async)
5. Result saved to database
6. Webhook/polling for completion
7. Frontend displays result

### Authentication Flow
1. User registers/logs in
2. Backend verifies credentials
3. JWT token generated with user ID
4. Token sent to frontend (localStorage)
5. Frontend includes token in all requests
6. Backend verifies token for protected routes

## Database Schema

### Users Table
```
id (INT) - Primary Key
username (STRING) - Unique
email (STRING) - Unique
hashed_password (STRING)
created_at (DATETIME)
updated_at (DATETIME)
```

### ChatMessages Table
```
id (INT) - Primary Key
user_id (INT) - Foreign Key
message (TEXT) - User input
response (TEXT) - AI response
model_used (STRING) - Which AI model
created_at (DATETIME)
```

### GeneratedContent Table
```
id (INT) - Primary Key
user_id (INT) - Foreign Key
content_type (STRING) - image/code/text
prompt (TEXT)
result (TEXT/BLOB)
created_at (DATETIME)
```

## API Contract

### Request Format
```json
{
  "Authorization": "Bearer <JWT_TOKEN>",
  "Content-Type": "application/json"
}
```

### Response Format
```json
{
  "status": "success|error",
  "data": {},
  "message": "Description",
  "timestamp": "2024-01-13T10:30:00Z"
}
```

## Deployment

### Docker Deployment
```bash
docker-compose up --build
```

### Termux Deployment
```bash
bash setup-termux.sh
bash start.sh
```

### Production Checklist
- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Setup rate limiting
- [ ] Configure CORS properly
- [ ] Setup logging
- [ ] Enable caching
- [ ] Setup monitoring
- [ ] Configure backups

## Performance Optimization

### Backend
- Use async/await for I/O operations
- Implement caching with Redis
- Database query optimization
- Connection pooling
- Request rate limiting

### Frontend
- Code splitting with React.lazy
- Image optimization
- Bundle size reduction
- Service workers for offline support
- Virtual scrolling for long lists

### Database
- Proper indexing
- Query optimization
- Connection pooling
- Regular backups
- Archiving old data

## Security Best Practices

1. **Authentication**
   - Use strong JWT secrets
   - Implement token refresh
   - Secure password hashing (bcrypt)

2. **Authorization**
   - Verify user ownership of resources
   - Role-based access control
   - Rate limiting per user

3. **Data Protection**
   - Validate all inputs
   - Sanitize outputs
   - Use HTTPS in production
   - Encrypt sensitive data

4. **API Security**
   - CORS configuration
   - Request validation
   - Response sanitization
   - Error message safety

## Testing

### Unit Tests
```bash
# Backend
cd backend
pytest tests/

# Frontend
cd frontend
npm test
```

### Integration Tests
```bash
# Test full flow
pytest tests/integration/
```

### Load Testing
```bash
# Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health
```

## Monitoring & Logging

### Backend Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Chat message received")
logger.error("Database error", exc_info=True)
```

### Frontend Logging
```javascript
console.log('State:', state);
console.error('API Error:', error);
```

## Troubleshooting Guide

### Common Issues

1. **Connection Refused**
   - Check if backend is running
   - Verify port numbers
   - Check firewall settings

2. **Authentication Failed**
   - Verify SECRET_KEY matches
   - Check token expiration
   - Validate JWT format

3. **Database Errors**
   - Check connection string
   - Verify database exists
   - Check migrations

4. **AI Model Issues**
   - Verify Ollama is running
   - Check model is downloaded
   - Verify API keys

## Contributing

See CONTRIBUTING.md for guidelines.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Ollama Documentation](https://ollama.ai/)
- [Tailwind CSS](https://tailwindcss.com/)
