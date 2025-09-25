# API Monitoring Dashboard 📊

This repository contains the source code for the **API Monitoring Dashboard**, a comprehensive application designed to provide real-time visibility into the health and performance of your APIs. The dashboard aggregates key metrics, giving you the insights you need to quickly identify and troubleshoot issues, ensuring high availability and a great user experience.

---

## ✨ Key Features

This dashboard provides a clear, at-a-glance view of your API ecosystem through a variety of metrics and visualizations.

* **API Uptime & Status:** Instantly see the current operational status of your APIs, including their uptime percentage.
* **Total Requests:** Monitor the overall volume of API traffic over time. This helps you understand usage patterns and anticipate load.
* **Error Rate:** Track the percentage of failed requests to quickly detect and respond to issues.
* **OpenAI Usage Statistics:** Get a detailed breakdown of your OpenAI API consumption, including requests and token usage.
* **Request Traffic (Last 24 Hours):** Visualize traffic patterns for both your application's APIs and the OpenAI API, helping you spot anomalies like unexpected spikes or drops.
* **Detailed Logs:** Access granular logs for all API calls to facilitate in-depth root cause analysis.
* **Failed APIs with Details:** A dedicated section that highlights failed API endpoints and provides detailed information on each failure, including status codes and error messages.

---

## 🚀 Getting Started

Follow these steps to set up the project locally.

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd docuHub
   ```

2. **Install dependencies**
   ```bash
   pip install pipenv
   pipenv install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run with Docker (recommended)**
   ```bash
   docker-compose up --build
   ```

5. **Or run locally**
   ```bash
   # Start PostgreSQL and Redis
   # Then run the application
   pipenv run uvicorn app.main:app --reload
   ```

### API Documentation

Once the application is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health-check

The dashboard will be available at `http://localhost:8000`.

---
