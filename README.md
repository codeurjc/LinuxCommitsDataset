# LinuxCommitsDataset

aws --endpoint-url https://minio.codeurjc.es s3 cp s3://michel/2023-MSR-LinuxBugs/linux-commits-2023-11-12.json.gz .
gzip -d linux-commits-2023-11-12.json.gz