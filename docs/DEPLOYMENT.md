# Deployment Guide

## Production Checklist

- [ ] Set strong database credentials
- [ ] Configure HTTPS/SSL
- [ ] Set up environment variables
- [ ] Enable CORS properly
- [ ] Set up logging
- [ ] Configure backup strategy
- [ ] Set up monitoring
- [ ] Enable rate limiting
- [ ] Set up CI/CD pipeline

## Backend Deployment

### Environment Variables

Create `.env` with production values:

```env
DATABASE_URL=postgresql://user:password@host:5432/empower
SECRET_KEY=your-secret-key-here
DEBUG=false
ALLOWED_HOSTS=yourdomain.com
```

### Using Docker

```bash
docker-compose -f docker-compose.yml up -d
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Frontend Deployment

### Build for Production

```bash
cd frontend
npm run build
```

### Serve Static Files

The `dist/` directory contains all files to serve. Options:

1. **Nginx**
   ```nginx
   server {
     listen 80;
     server_name yourdomain.com;
     
     location / {
       root /path/to/frontend/dist;
       try_files $uri $uri/ /index.html;
     }
     
     location /api {
       proxy_pass http://localhost:8000;
     }
   }
   ```

2. **Apache**
   - Serve `dist/` directory as document root
   - Enable mod_rewrite for SPA routing

3. **Cloud Storage (S3, CloudFront)**
   - Upload `dist/` contents to S3
   - Configure CloudFront for caching

## Database

### PostgreSQL Setup

```bash
# Create database
createdb empower

# Run migrations
alembic upgrade head
```

### Backup Strategy

```bash
# Daily backup
pg_dump empower > backup_$(date +%Y%m%d).sql

# Restore from backup
psql empower < backup_20240101.sql
```

## SSL/HTTPS

### Using Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Monitoring & Logging

### Application Logging

Configure logging in `backend/app/core/config.py`:

```python
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
```

### Log Rotation

Use `logrotate` for log file management:

```
/var/log/empower/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

## Performance Optimization

1. **Database Indexing**: Add indexes on frequently queried fields
2. **Caching**: Configure Redis for session/response caching
3. **CDN**: Use CDN for static assets
4. **Compression**: Enable gzip compression
5. **Database Connection Pooling**: Use pgbouncer

## Health Checks

### Application Health

Monitor `/api/v1/health` endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

### Automated Monitoring

Set up alerts for:
- Server uptime
- Response times
- Error rates
- Database connection issues

## Troubleshooting

### 502 Bad Gateway
- Check if backend is running
- Verify proxy configuration
- Check logs: `backend.log`

### Database Connection Errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify network connectivity

### Slow Performance
- Check database query performance
- Monitor system resources (CPU, memory)
- Review application logs for errors

## Security

- Use HTTPS only
- Keep dependencies updated
- Implement rate limiting
- Validate all user inputs
- Use parameterized queries
- Implement CORS restrictions
- Regular security audits

See [ARCHITECTURE.md](ARCHITECTURE.md) for more details.
