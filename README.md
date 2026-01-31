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

### Using the API

#### Create a Short Link
```bash
curl -X POST https://url-shortener-wu03.onrender.com/api/links \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://github.com/mkr-msk/devops-engineer-from-scratch-project-313",
    "short_name": "myproject"
  }'
```

Response:
```json
{
  "id": 1,
  "original_url": "https://github.com/mkr-msk/devops-engineer-from-scratch-project-313",
  "short_name": "myproject",
  "short_url": "https://url-shortener-wu03.onrender.com/myproject",
  "created_at": "2026-01-31T12:34:56Z"
}
```

#### Get All Links (with Pagination)
```bash
# Get first 10 links
curl "https://url-shortener-wu03.onrender.com/api/links?range=[0,9]"

# Get next 10 links
curl "https://url-shortener-wu03.onrender.com/api/links?range=[10,19]"
```

#### Get a Specific Link
```bash
curl https://url-shortener-wu03.onrender.com/api/links/1
```

#### Update a Link
```bash
curl -X PUT https://url-shortener-wu03.onrender.com/api/links/1 \
  -H "Content-Type: application/json" \
  -d '{
    "short_name": "portfolio"
  }'
```

#### Delete a Link
```bash
curl -X DELETE https://url-shortener-wu03.onrender.com/api/links/1
```

#### Use a Short Link

Simply visit the short URL in your browser:
```
https://url-shortener-wu03.onrender.com/myproject
```

Or use curl to see the redirect:
```bash
curl -I https://url-shortener-wu03.onrender.com/myproject
```