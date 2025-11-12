import boto3
import requests
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
# --- Updated IMDSv2-aware metadata helper ---

def get_instance_metadata(path, timeout=1):
    """
    Fetch instance metadata using IMDSv2 if required.
    Returns text or None on any failure.
    """
    base = "http://169.254.169.254/latest/"
    try:
        # Get IMDSv2 token
        token_resp = requests.put(
            base + "api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=timeout
        )
        if token_resp.status_code == 200:
            token = token_resp.text
            r = requests.get(base + "meta-data/" + path,
                             headers={"X-aws-ec2-metadata-token": token},
                             timeout=timeout)
            if r.status_code == 200:
                return r.text
            return None
    except Exception:
        pass

    # fallback to IMDSv1 (in case IMDSv2 not required)
    try:
        r = requests.get(base + "meta-data/" + path, timeout=timeout)
        if r.status_code == 200:
            return r.text
    except Exception:
        return None
    return None

# Detect region & instance id
az = get_instance_metadata("placement/availability-zone")
REGION = az[:-1] if az else None
SELF_ID = get_instance_metadata("instance-id")

# fallback default region if metadata not available
if REGION is None:
    REGION = "eu-north-1"   # change this to your region if needed

class AWSClient:
    def __init__(self, region_name=REGION):
        self.region = region_name
        self.ec2 = boto3.client("ec2", region_name=self.region)
        self.cloudwatch = boto3.client("cloudwatch", region_name=self.region)

    def list_instances(self):
        try:
            resp = self.ec2.describe_instances()
            instances = []
            for r in resp.get("Reservations", []):
                for i in r.get("Instances", []):
                    instances.append({
                        "InstanceId": i.get("InstanceId"),
                        "State": i.get("State", {}).get("Name"),
                        "InstanceType": i.get("InstanceType"),
                        "PublicIp": i.get("PublicIpAddress"),
                        "LaunchTime": str(i.get("LaunchTime"))
                    })
            return instances
        except ClientError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}

    def start_instance(self, instance_id):
        if SELF_ID and instance_id == SELF_ID:
            print("Refusing to start host instance:", SELF_ID)
            return False
        try:
            self.ec2.start_instances(InstanceIds=[instance_id])
            return True
        except ClientError as e:
            print("Start error:", e)
            return False
        except Exception as e:
            print("Start other error:", e)
            return False

    def stop_instance(self, instance_id):
        if SELF_ID and instance_id == SELF_ID:
            print("Refusing to stop host instance:", SELF_ID)
            return False
        try:
            self.ec2.stop_instances(InstanceIds=[instance_id])
            return True
        except ClientError as e:
            print("Stop error:", e)
            return False
        except Exception as e:
            print("Stop other error:", e)
            return False

    def fetch_cpu(self, instance_id, minutes=10):
        try:
            end = datetime.utcnow()
            start = end - timedelta(minutes=minutes)
            resp = self.cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name":"InstanceId","Value":instance_id}],
                StartTime=start,
                EndTime=end,
                Period=300,
                Statistics=["Average"]
            )
            points = resp.get("Datapoints", [])
            if points:
                latest = sorted(points, key=lambda x: x["Timestamp"])[-1]
                return latest.get("Average")
            return None
        except ClientError as e:
            print("CloudWatch ClientError:", e)
            return None
        except Exception as e:
            print("CloudWatch error:", e)
            return None
