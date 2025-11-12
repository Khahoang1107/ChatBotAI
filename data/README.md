# Data Directory

This folder contains all data-related files and configurations.

## Structure

```
data/
├── uploads/          # User uploaded files (images, documents)
│   └── *.png, *.jpg  # Invoice images, receipts, etc.
└── services/         # Service configurations
    └── auth-service/ # Authentication service config
```

## uploads/

Contains files uploaded by users through the application:

- Invoice images for OCR processing
- Receipt images
- Document scans

**Note:** This folder may contain sensitive user data. Ensure proper access controls in production.

## services/

Contains configuration files for external services:

- Authentication service configurations
- API endpoints
- Service discovery settings

## Management

### Cleanup

Regular cleanup of old upload files:

```bash
# Remove files older than 30 days
find uploads/ -type f -mtime +30 -delete
```

### Backup

Important data folders to backup:

- `uploads/` - User data
- `services/` - Service configurations

### Security

- `uploads/` should have restricted access
- `services/` may contain sensitive configuration
- Consider encryption for sensitive data folders
