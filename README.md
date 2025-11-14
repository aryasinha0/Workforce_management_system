# ManPowerHandling_Gujarat
This is the project for Man Power Management, useful in meter-installation supervision.

For running the backend project

``` python app.py```


---


# API Documentation

## Authentication

**Endpoint**: `POST /auth/register`

### Request
```json
{
  "phone_number": "string (required, unique)",
  "password": "string (required, min 8 chars)",
  "name": "string (required)",
  "role": "string (required, one of: installer, supervisor, admin)",
  "supervisor_id": "integer (required if role=installer)"
}
```


**Endpoint**: `POST /auth/login`

### Request
```json
{
    "phone_number": "+919876543210",
    "password": "installer123"
}
```

## Installer endpoints
### Installer Attendance
**Endpoint**: `POST installer/attendance`

### Request

```json
{
    "latitude" : 23.0225,
    "longitude": 72.5714,
    "location": "Ahmedabad Office",
    "selfie": "image.jpg"
}
```
### Installer location tracking at the interval of 30 minutes
**Endpoint**: `POST installer/tracking`

### Request

```json
{
  "latitude": 23.0225,
  "longitude": 72.5714,
  "location": "Ahmedabad Office"
}
```
### Uploading the faulty-meter information
**Endpoint**: `POST installer/faulty-meter`

### Request
```json
{
  "serial_no": "MTR123456",
  "meter_image": "https://your-bucket.s3.amazonaws.com/meters/photo123.jpg",
  "remark": "Display not working"
}
```
### Uploading information of not installing the meter when meter is OK.
**Endpoint**: `POST installer/adverse-condition`

### Request
```json
{
  "condition": "Consumer not available",
  "consumer_id": "CONS12345678"
}
```
## Supervisor endpoints

### Supervisor get the information about installers under him.
**Endpoint**: `GET /supervisor/installers`

### Supervisor get the attendance of the installers under him.

**Endpoint**: `GET /supervisor/attendances`

### Get the information about the faulty-meter
**Endpoint**: `PATCH supervisor/tracking/<int:installer_id>`


### Supervisor can get to know about the faulty-meters punched by installer under him.
**Endpoint**: `GET /supervisor/faulty-meters`

### Can update the status of faulty-meter (whether it is received or not)
**Endpoint**: `PATCH /supervisor/faulty-meters/<int:meter_id>`
### Request
```json
{
    "status": "Received"
}
```

### Supervisor can get to know about the adverse field conditions (interruptions in meter installation)
**Endpoint**: `GET /supervisor/adverse-conditions`

## Admin endpoints

### Know about all the users
**Endpoint**:`GET admin/users`

### Know about the attendances of all the installers
**Endpoint**:`GET admin/attendances`

### See the tracking of an installer
**Endpoint**:`GET admin/tracking/<int:user_id>`


### See the faulty meters information
**Endpoint**:`GET admin/faulty-meters`

### Update faulty meters status and remark with respect to meter id
**Endpoint**:`PATCH admin/faulty-meters/<int:meter_id>`
```json
{
  "status":"Submitted to Godown",
  "remark":"Display broken"
}
```

### Admin can get to know about the adverse field conditions (interruptions in meter installation)
**Endpoint**:`GET admin/adverse-conditions`
