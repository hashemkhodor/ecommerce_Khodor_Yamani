# E-commerce Platform by Hashem Khodor & Mahmoud Yamani

An E-commerce platform designed to streamline online shopping experiences. This project implements a microservices architecture for modularity and scalability, covering key functionalities such as customer management, inventory tracking, sales processing, and reviews moderation.

## Features
- **Customer Management:** User registration, authentication, profile updates, and wallet management.
- **Inventory Management:** Adding, updating, and tracking product stock levels.
- **Sales Processing:** Order handling, transaction recording, and purchase history retrieval.
- **Review System:** Submission, moderation, and feedback mechanisms for customer reviews.

## Technologies Used
- **Backend Framework:** FastAPI
- **Database:** PostgreSQL (cloud-hosted via Supabase)
- **Authentication:** JSON Web Tokens (JWT)
- **Containerization:** Docker
- **API Documentation:** Swagger/OpenAPI
- **Testing:** Pytest with FastAPI TestClient and pytest-asyncio
- **Validation:** Pydantic models

## Architecture Overview
The platform is built as a collection of independent microservices:
1. **Customer Service:** Manages user registration, authentication, and wallet.
2. **Inventory Service:** Tracks products and manages stock levels.
3. **Sales Service:** Handles purchases and integrates with customer and inventory services.
4. **Review Service:** Processes and moderates user reviews.

Each service communicates via RESTful APIs and maintains its database schema for scalability.

## Prerequisites
- Docker and Docker Compose installed on your system.
- Python 3.11+ installed (if running without Docker).

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/hashemkhodor/ecommerce_Khodor_Yamani.git  
cd ecommerce_Khodor_Yamani  
```

### 2. Build and Run All Services Using Docker Compose
A `docker-compose.yml` file is provided for orchestrating all microservices.

To build and run all services:
```bash
docker-compose up --build  
```
This will:
- Build and containerize each service with its respective `Dockerfile`.
- Expose the services on the following ports:
  - Customer Service: `http://localhost:8000`
  - Inventory Service: `http://localhost:8001`
  - Sales Service: `http://localhost:8002`
  - Review Service: `http://localhost:8003`

### 3. Access API Documentation
Once services are running, you can access the API documentation at:
- **Customer Service:** `http://localhost:8000/docs`
- **Inventory Service:** `http://localhost:8001/docs`
- **Sales Service:** `http://localhost:8002/docs`
- **Review Service:** `http://localhost:8003/docs`

## Running Tests
To run tests for any service:
1. Navigate to the service directory:
    ```bash
   cd [service-name]
   ```
2. Run the tests using pytest:
    ```bash
   python -m pytest
    ```
## Profiling
To profile the API performance of a service:
1. Navigate to the service directory:
    ```bash
   cd [service-name]
   ```
2. Run the profiler script:
    ```bash
   python -m tests.api_profiler
    ```
## Running Individual Services
To run a service individually:
1. Navigate to the service directory:
    ```bash
   cd [service-name]
    ```
2. Create a virtual environment:
    ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3. Install dependencies:
    ```bash
   pip install -r requirements.txt
    ```
4. Start the service:
    ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000
    ```
## Deployment
The project uses Docker for containerization and orchestration, enabling smooth deployment on any platform supporting Docker. Each microservice has an independent deployment pipeline defined in its `Dockerfile`.

## Contribution Guidelines
We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m "Add feature description"`.
4. Push the changes: `git push origin feature-name`.
5. Create a pull request.

## License
This project is licensed under the MIT License.

## Contact
For inquiries or support, contact:
- **Hashem Khodor**
- **Mahmoud Yamani**