# Ports

Live checks on 25 October 2026 (Asia/Calcutta). Owners came from Get-NetTCPConnection/Get-Process and docker ps. All entries preserved except the newly created Compose listeners.

| Port / scope | Observed owner | Purpose / result |
|---|---|---|
| 80 / Windows host | No listener in filtered results | Free at preflight; not used on host |
| 8000 / Windows host | com.docker.backend PID 7884; wslrelay PID 36948 | Existing kspdb-backend-1; preserved |
| 8080 / Windows host | java PID 9268 | Existing Jenkins; preserved |
| 8081 / 127.0.0.1 host | com.docker.backend PID 7884 | Existing capstone-jenkins; preserved |
| 18080 / 127.0.0.1 host | com.docker.backend PID 7884 | Existing payment-live; preserved |
| 30099 / 127.0.0.1 host | kubectl PID 33180 | Existing port-forward; preserved |
| 38080 / Windows host | Free immediately before Compose; then com.docker.backend PID 7884 / wslrelay PID 36948 | capstone-frontend -> container 80; dashboard http://localhost:38080 |
| 38081 / Windows host | Free immediately before Compose; then com.docker.backend PID 7884 / wslrelay PID 36948 | capstone-backend -> container 8000; API http://localhost:38081 |
| 8000 / Compose backend container | uvicorn; backend healthy | Internal API and health checks |
| 80 / Compose frontend container | nginx; frontend healthy | Relative /api/ and /health proxy to http://backend:8000 |
| 30099 / capstone-simple node | capstone-nodeport Service | Verified healthy via curl inside node after apply; independent of host port-forward |
| 63732 / 127.0.0.1 and ::1 Windows tunnel | ssh PID 41716; launched by minikube PID 7468 | Active URL http://127.0.0.1:63732; HTTP/browser checks passed; process must keep running |
| 38999 / Windows + WSL negative test | No Windows listener; WSL connection refused | Ansible correctly failed with exit 2 |

payment-live-cs uses no published port and exits successfully by design. No host port-forward was changed.

## Minikube startup / pre-apply checks
- capstone-simple node IP: 192.168.49.2. NodePort 30099 is unallocated and has no TCP listener before apply.
- Cluster's existing kubernetes Service: TCP 443, control-plane API.
- Node ss -lnt also showed existing system listeners: 22 (SSH), 2379/2380/2381 (etcd), 8443 (API), 10010 (runtime), 10248/10250 (kubelet), 10257/10259 (controller/scheduler), 10249/10256 (kube-proxy), and 127.0.0.11:43613 (container DNS). No changes made to these.
- docker port capstone-simple reports loopback-only mappings owned by this newly created Minikube container:
  - 127.0.0.1:59195 -> 22/tcp (SSH)
  - 127.0.0.1:59193 -> 2376/tcp (node management)
  - 127.0.0.1:59196 -> 5000/tcp (registry mapping)
  - 127.0.0.1:59192 -> 8443/tcp (Kubernetes API)
  - 127.0.0.1:59194 -> 32443/tcp (HTTPS NodePort mapping)
- Application tunnel now allocated on loopback 63732 (SSH PID 41716, Minikube PID 7468). Existing host 30099 remains kubectl PID 33180.

