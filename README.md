# Avi Load Balancer Test Automation Framework

A Python-based test automation framework for VMware Avi Load Balancer API testing with support for parallel execution.

## Overview

This framework provides automated testing capabilities for Avi Load Balancer virtual services with multiple execution modes including sequential, threading, multiprocessing, and asyncio-based parallel execution.

## Features

- **User Registration & Authentication**: Automated login/logout flows
- **Virtual Service Pool Testing**: Automated enable/disable pool operations
- **Parallel Execution Support**: Multiple execution modes for scalability
  - Sequential execution
  - Threading-based parallelism
  - Multiprocessing-based parallelism
  - Asyncio-based async execution
- **YAML-based Configuration**: Easy test configuration management
- **Mock API Support**: Built-in mock server for testing

## Requirements

- Python 3.7+
- Dependencies:
  - requests==2.31.0
  - PyYAML==6.0.1

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `test_config.yaml` to configure:
- API base URL
- User credentials
- Target virtual service
- Parallelism mode and thread count
- Test cases to execute

Example configuration:
```yaml
api:
  base_url: "https://your-avi-api-endpoint.com/"
  timeout: 30

credentials:
  username: "your_username"
  password: "your_password"

target_virtual_service: "backend-vs-t1r_1000-1"

parallelism:
  method: "threading"  # Options: sequential, threading, multiprocessing, asyncio
  thread_count: 5
```

## Usage

Run the test framework:
```bash
python main.py
```

### Command-line Options

```bash
python main.py --config test_config.yaml
```

## Project Structure

```
.
├── main.py                 # Main entry point
├── config_loader.py        # YAML configuration parser
├── api_client.py          # API client for Avi Load Balancer
├── test_orchestrator.py   # Test execution orchestrator
├── mocks.py               # Mock API server
├── test_config.yaml       # Test configuration file
├── test_mocks.py          # Unit tests for mocks
├── test_orchestrator.py   # Orchestrator tests
└── requirements.txt       # Python dependencies
```

## Running Tests

Run unit tests:
```bash
python -m pytest test_mocks.py
python -m pytest test_orchestrator.py
```

## Mock Server

To run the mock API server for testing:
```bash
python mocks.py
```

## License

This project is part of an internship project.
