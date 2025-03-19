# MinflixBackend

The backend is controlled with FastAPI routing in Python.  
Utilizes JWT + OAuth2 for session management.  
This is then served as a Docker container and deployed through Google Cloud Platform  

<br />

### Google Cloud Deployment Instructions
---

- Enable and use Google Cloud Run:
1. Deploy a "service"
2. Continuosly deploy from Github repository
3. Setup with Cloudbuild and select branch and buildtype (Dockerfile)
4. Service Name: minflixbackend
5. Region: us-west2 (Los Angeles)
6. Check Allow unauthenticated invocations
7. Under Networking, Connect to a VPC and use created VPC with associated subnet
8. Add appropriate environment variables:  
   DB_NAME=  
   DB_PASSWORD=  
   SECRET_KEY=
9. Add Cloud SQL connection and select your created SQL Instance
10. Deploy
