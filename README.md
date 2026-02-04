### Hexlet tests and linter status:
[![Actions Status](https://github.com/mkr-msk/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/mkr-msk/devops-engineer-from-scratch-project-313/actions)
[![CI](https://github.com/mkr-msk/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/mkr-msk/devops-engineer-from-scratch-project-313/actions)

## Live Application

The application is deployed at: **https://url-shortener-wul3.onrender.com**

Test the health check endpoint:
```bash
curl https://url-shortener-wul3.onrender.com/ping
```

### Running the application locally

To run the application, execute:
```bash
make run
```

## API Usage Examples

### Health Check
```bash
curl https://url-shortener-wul3.onrender.com/ping
# Response: pong
```

### Create Short Link
```bash
curl -X POST https://url-shortener-wul3.onrender.com/api/links \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://example.com/very-long-url",
    "short_name": "example"
  }'
```

Response:
```json
{
  "id": 1,
  "original_url": "https://example.com/very-long-url",
  "short_name": "example",
  "short_url": "https://url-shortener-wul3.onrender.com/r/example",
  "created_at": "2024-02-04T12:00:00"
}
```

### Get All Links
```bash
curl https://url-shortener-wul3.onrender.com/api/links
```

### Get Link by ID
```bash
curl https://url-shortener-wul3.onrender.com/api/links/1
```

### Update Link
```bash
curl -X PUT https://url-shortener-wul3.onrender.com/api/links/1 \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://example.com/updated-url",
    "short_name": "updated"
  }'
```

### Delete Link
```bash
curl -X DELETE https://url-shortener-wul3.onrender.com/api/links/1
```

### Use Short Link (Redirect)
```bash
curl -L https://url-shortener-wul3.onrender.com/r/example
# Redirects to the original URL
```