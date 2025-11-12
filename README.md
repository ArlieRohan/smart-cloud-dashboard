# ☁️ Smart Cloud Dashboard  
*A Flask + AWS project for cloud monitoring and EC2 instance management*

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-lightgrey)
![AWS](https://img.shields.io/badge/AWS-EC2-orange)
![Boto3](https://img.shields.io/badge/Boto3-Cloud%20SDK-yellow)
![Status](https://img.shields.io/badge/Status-Working%20Demo-success)

---

## 🧭 Overview

**Smart Cloud Dashboard** is a web-based application that allows users to **monitor and manage AWS EC2 instances** from a single interface.  
It integrates **Flask (Python)** for the backend and **AWS SDK (Boto3)** to communicate with AWS services such as **EC2** and **CloudWatch**.  

Users can:
- View all running EC2 instances  
- Start or stop instances directly from the dashboard  
- Visualize CPU utilization using live CloudWatch data  
- Deploy the app on AWS EC2 using Gunicorn and Nginx for production

---

## ✨ Features

| Feature | Description |
|----------|--------------|
| 🖥️ EC2 Instance Management | View all EC2 instances with IDs, types, states, and IPs |
| ⚙️ Start / Stop Instances | Control instance power directly from dashboard buttons |
| 📊 Real-Time CPU Metrics | Fetch CPU utilization from CloudWatch in real-time |
| ☁️ AWS Integration | Secure communication with AWS through IAM roles or credentials |
| 🔐 IAM Role Support | Works seamlessly on EC2 without embedding keys |
| 🚀 Deployment Ready | Configured to run with Gunicorn + systemd on AWS EC2 |

---

## 🧩 Architecture

# 🏗️ Improved Architecture

Below is an improved, production-aware architecture for the **Smart Cloud Dashboard**.  
It keeps your current EC2 + Flask design but adds best-practice components for security, availability, and maintainability.

---

## Mermaid diagram (rendered on GitHub)
```mermaid
flowchart LR
  subgraph Internet
    User[User Browser]
  end

  subgraph AWS-VPC
    direction TB
    ALB[Application Load Balancer<br/>(HTTPS, ACM TLS)]
    subgraph PublicSubnet
      NATGW[NAT Gateway]
      ALB
    end

    subgraph PrivateSubnet-AZ1
      EC2A[EC2 Instance (Flask + Gunicorn)<br/>AutoScaling Group (min=1,max=3)]
    end

    subgraph PrivateSubnet-AZ2
      EC2B[EC2 Instance (Flask + Gunicorn)]
    end

    RDS[(Optional) RDS / Postgres]
    S3[S3 (static assets, logs, screenshots)]
    CW[CloudWatch (Metrics & Logs)]
    IAMrole[EC2 IAM Role: EC2ReadOnly + CloudWatchReadOnly + CustomControlPolicy]
    Secrets[Secrets Manager / Parameter Store]
  end

  User -->|HTTPS| ALB
  ALB --> EC2A
  ALB --> EC2B
  EC2A -->|CloudWatch APIs| CW
  EC2A -->|EC2 Control APIs (via IAM role)| AWSec2[(AWS EC2 API)]
  EC2A --> S3
  EC2A --> RDS
  EC2A --> Secrets
  IAMrole --- EC2A
  NATGW -->|outbound| Internet



---

## 🖼️ Screenshots

### 🔹 Dashboard Overview  
![Dashboard Screenshot](https://raw.githubusercontent.com/ArlieRohan/smart-cloud-dashboard/refs/heads/main/smart-cloud-dashboard/dashboard_running.png)

### 🔹 Instance List & Control  
![Instances Screenshot](https://raw.githubusercontent.com/ArlieRohan/smart-cloud-dashboard/refs/heads/main/smart-cloud-dashboard/instances_list.png)

### 🔹 CPU Usage Graph  
![CPU Graph](https://raw.githubusercontent.com/ArlieRohan/smart-cloud-dashboard/refs/heads/main/smart-cloud-dashboard/cpu_graph.png)

---

## ⚙️ Installation & Setup

### 🧱 Clone the repository
```bash
git clone https://github.com/ArlieRohan/smart-cloud-dashboard.git
cd smart-cloud-dashboard


Create a virtual environment
python -m venv venv
# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

📦 Install dependencies
pip install -r requirements.txt
AWS Configuration

You can connect the app to AWS in two ways:

Option 1 — IAM Role (recommended)

Attach an IAM role to your EC2 instance with the following permissions:

AmazonEC2ReadOnlyAccess

CloudWatchReadOnlyAccess

(Optional) Custom policy to start/stop instances

Option 2 — Local credentials

Create a file at:

~/.aws/credentials


And add:

[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = eu-north-1

🚀 Run the Application
python -m app.main


Then open your browser and visit:

http://127.0.0.1:5000

🧰 Deployment (on AWS EC2)

Launch an EC2 instance (Ubuntu)

SSH into the instance

Install Python, Git, and dependencies

Run Gunicorn with systemd:

sudo systemctl start smart-cloud.service


Access via:

http://<your-public-ip>:5000

📜 Future Enhancements

✅ Add multi-region EC2 monitoring

✅ Integrate S3 and Lambda monitoring

✅ Enable user authentication and role-based access

✅ Improve UI with React front-end
