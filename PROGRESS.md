# Capstone progress

Evidence recorded on 25 October 2026 (Asia/Calcutta). Only actual command/tool results are marked PASS.

## Phase 1 - PASS: implementation and structural verification
- Created project at D:\codex study after Test-Path returned False. No pre-existing files overwritten.
- 23 requested source/tracking files created. capstone.env awaits Terraform; version.txt is reserved for the user's Git release step.
- Structural PowerShell checks exited 0: Jenkinsfile has exactly 3 stages and Windows bat steps; root Dockerfile exactly matches FROM alpine and CMD ["echo", "Payment Gateway Running"]; manifest has Deployment, Service, Deployment, Service and no namespace; Terraform has exactly one resource; browser app.js contains only relative API URLs.
- Kubernetes manifest and Ansible playbook are authored but have NOT been server/syntax validated or applied yet.

## Phase 2 - PASS: local verification
1. Explicit installed Python path reports Python 3.12.2 (differs from supplied 3.12.10 audit; no reinstall performed).
2. python -m venv .venv and pip install -r backend\requirements-dev.txt: exit 0.
3. From backend: ..\.venv\Scripts\python.exe -m pytest -v: exit 0, collected 9 items, 9 passed, 1 warning in 0.68s.
4. Extracted Jenkins Build & Test bat commands, decoded Groovy backslashes, and executed through cmd.exe /d /c with the installed Python directory prepended to PATH: exit 0; 9 passed, 1 warning in 0.68s; printed 'Building Payment and Notification Services... Test PASSED'. Removed only the newly created .ci-venv with a checked absolute path; Test-Path returned False afterwards. This does not prove Jenkins LocalSystem Python/Docker access.
5. docker build -t payment-engine:capstone .: exit 0.
6. Verified payment-live-cs name free; docker run -d --name payment-live-cs payment-engine:capstone: exit 0; docker wait returned 0; docker ps -a reported Exited (0); docker logs printed Payment Gateway Running.
7. Before Compose: capstone-backend and capstone-frontend names absent; ports 38080/38081 free. docker compose -p capstone-simple config -q: exit 0. docker compose -p capstone-simple up -d --build: exit 0.
8. docker compose -p capstone-simple ps: capstone-backend and capstone-frontend both healthy.
9. Invoke-WebRequest through http://localhost:38080: / HTTP 200; /health HTTP 200 with {"status":"healthy","version":"v1.0-prod-bundle"}; /api/payments HTTP 200, non-empty list.
10. Valid POST payer API Demo, payee Verification, USD 99.90: HTTP 201, payment id 5. Invalid POST amount 1.234 with valid INR: HTTP 422. Newest notification references payment 5.
11. Built-in browser opened dashboard, submitted Browser Demo -> Evaluator INR 75.50: visible Payment #4 created successfully; PAY-0004 appears in ledger; notification Payment #4 created for INR 75.50 appears newest. Screenshot saved in chat outputs/compose-browser-payment.png.
12. docker image inspect all 3 tags: exit 0. Image IDs:
    - payment-engine:capstone sha256:81ed4519b824e54d28c8bb780a3e732d99553f0b8a20de49869009d2362c7d51
    - payment-backend:capstone sha256:dc74089bce02a0be00051f30ea84a674b6b9d47a641c65c53ee74ba386e7e95b
    - payment-frontend:capstone sha256:7ffcf3e1ac4c9438265f82aec14c68570b38260a104437157f61ee3e8a387624
13. Protected payment-live, capstone-jenkins, kspdb-backend-1 still running. No unrelated container changes made. kubectl config current-context: docker-desktop.

## Phase 3 - PASS: startup, deployment, tunnel and NodePort verification
- User explicitly approved start with --cpus=2 --memory=2048, requiring a fresh RAM check and no retries/settings changes on failure.
- Immediately before start, Get-CimInstance reported 2.53 GiB free / 15.26 GiB total; Docker VM total 7,933,714,432 bytes; current kubectl context docker-desktop. Reported these numbers before issuing start.
- Ran exactly: minikube start -p capstone-simple --driver=docker --cpus=2 --memory=2048 --keep-context. Background exec session captured real output. First attempt exited 0; no retry or settings change.
- Startup downloaded kicbase v0.0.51 and Kubernetes v1.37.0 preload, then configured CNI and verified components. Enabled default storage-provisioner/default-storageclass addons.
- Windows responsiveness checks completed throughout startup. Free RAM observed 2.69 GiB, 2.17 GiB, then 0.86 GiB after startup and 0.88 GiB after image loads/dry run. No host unresponsiveness observed.
- minikube status -p capstone-simple: host Running, kubelet Running, apiserver Running, kubeconfig Configured; exit 0.
- kubectl --context capstone-simple -n default get nodes -o wide: capstone-simple Ready, Kubernetes v1.37.0, internal IP 192.168.49.2, containerd 2.3.4.
- Profile config read-only check: CPUs=2, MemoryMiB=2048, Driver=docker.
- minikube -p capstone-simple image load payment-backend:capstone and payment-frontend:capstone both exit 0. minikube image ls confirms docker.io/library/payment-backend:capstone and docker.io/library/payment-frontend:capstone.
- All-namespace Service inventory: NodePort 30099 unallocated. minikube ssh -- 'ss -lnt': no TCP listener on 30099.
- Target inventory before apply: no Deployments in default; only service/kubernetes on 443/TCP.
- kubectl --context capstone-simple -n default apply --dry-run=server -f 'D:\codex study\capstone-stack.yaml': exit 0; all four resources reported created (server dry run).
- Pending real apply target: context capstone-simple, namespace default, file D:\codex study\capstone-stack.yaml.
  - Deployment capstone-deployment: 2 backend replicas, payment-backend:capstone, imagePullPolicy Never.
  - Service capstone-backend: ClusterIP 8000, backend selector, ClientIP affinity.
  - Deployment capstone-frontend: 1 frontend replica, payment-frontend:capstone, backend URL http://capstone-backend:8000, imagePullPolicy Never.
  - Service capstone-nodeport: NodePort 30099 -> frontend 80.
- First apply was subsequently explicitly approved by the user and completed; see verification evidence below.
- kubectl --context capstone-simple config current-context after checks still returned docker-desktop. Existing host port-forward on 30099 untouched.
- Windows Docker driver tunnel is now running at http://127.0.0.1:63732 in hidden Minikube process PID 7468 (SSH listener PID 41716). It must keep running; port may change when restarted.
- The first-apply approval and all verification steps have now completed successfully, as recorded below.
### Actual apply and live verification
- Applied only capstone-stack.yaml using kubectl --context capstone-simple -n default apply -f: exit 0; all four resources created.
- rollout status deployment/capstone-deployment --timeout=180s and rollout status deployment/capstone-frontend --timeout=180s (both with explicit context and namespace): exit 0, successfully rolled out.
- Backend deployment 2/2 Ready; frontend deployment 1/1 Ready. All three pods Running/Ready with zero restarts at both observations. No delete/recreate/retry performed.
- Node Ready, internal IP 192.168.49.2. Services: backend ClusterIP 10.104.249.81:8000; frontend NodePort service 10.109.198.170:80 -> nodePort 30099.
- Backend EndpointSlice contains 10.244.0.3 and 10.244.0.4; frontend contains 10.244.0.5. Backend logs show both Uvicorn processes started and GET /health 200 OK. kubectl get all -l tier=backend verified pods, service, Deployment and ReplicaSet.
- Launched minikube -p capstone-simple service capstone-nodeport --url --namespace=default as a hidden background process, PID 7468; output URL http://127.0.0.1:63732. SSH process PID 41716 owns loopback listener 63732.
- Invoke-WebRequest through tunnel: / HTTP 200; /health HTTP 200 with healthy/version JSON; /api/payments HTTP 200 with 3 seeds.
- Browser submitted Cluster Demo -> Minikube Evaluator INR 125.75: Payment #4 created successfully; PAY-0004 visible in ledger and notification. Clicked Refresh data and confirmed payment remains. Screenshot outputs/minikube-browser-payment.png.
- minikube -p capstone-simple ssh -- 'curl --fail --silent --show-error http://192.168.49.2:30099/health': exit 0 and {"status":"healthy","version":"v1.0-prod-bundle"}. This proves the actual NodePort inside the node.
- Current context still docker-desktop. Host 127.0.0.1:30099 still owned by existing kubectl PID 33180. Windows free RAM later measured 1.42 GiB.
- Full cluster evidence exported to outputs/phase3-cluster-verification.log.

## Phase 4 - PASS: Terraform and Ansible
- Terraform 1.16.6 used without reinstall/update. fmt -check, init, validate, apply -auto-approve -input=false all exited 0.
- Only local_file.capstone_env created: apply result 1 added, 0 changed, 0 destroyed. Provider hashicorp/local v2.9.1 signed by HashiCorp; .terraform.lock.hcl generated for version control.
- capstone.env verified byte-for-byte: exactly 59 ASCII bytes, LF newlines, no BOM, required URL and STATUS lines.
- terraform plan -detailed-exitcode -input=false returned 0 and No changes.
- Compose remained healthy. WSL Ubuntu script ran requested Ansible command module to read capstone.env (rc=0), syntax check (exit 0) and real playbook (exit 0): ok=11 changed=0 unreachable=0 failed=0. Summary confirmed healthy http://localhost:38080 and 5 payments. No sudo or WSL network fallback used.
- Negative test after confirming no Windows listener on 38999: ansible-playbook -i localhost, validate.yml -e app_url=http://localhost:38999 returned 2 with connection refused at /health; recap ok=6 failed=1. This is the required successful negative test, not a deployment failure.
- Logs exported to outputs/phase4-terraform.log, phase4-ansible-positive.log and phase4-ansible-negative.log.

## Phase 5 - BLOCKED awaiting user Git/Jenkins/Jira actions
- Read-only git config checks returned configured identity; no Git repository exists at project root yet. No Git writes performed.
- Jenkins Windows service is Running as LocalSystem. Machine-only PATH where.exe lookup: Python exit 1 (not found); Git exit 0; Docker exit 0. Machine PATH includes a Python executable as a PATH entry rather than a Python directory. This is a static current-account machine-PATH check, NOT an actual LocalSystem execution/access test.
- Actual LocalSystem Python/Git execution and Docker pipe access remain UNVERIFIED. No Jenkins service/logon/config/job/credential changes made. User decision needed before addressing missing Python or running a new diagnostic job.
- Exact Git commands and later Jenkins/Jira click instructions are in outputs/HANDOFF.md. Git commands must be run by user, then verified read-only before proceeding.
## Phase 6 - pending
Final six-task report and evaluator demo commands await remaining verified phases.

## Known limitations
- Demo data lives in each backend process and resets on restart. ClientIP affinity provides sticky routing but does not synchronize replicas or provide persistence; nginx may pin many browser clients to one replica.
- Jenkins Deploy Cluster stage intentionally only echoes; actual deployment is performed separately after approval.
- One dependency deprecation warning from Starlette's use of an AnyIO alias; all nine tests passed.
- Current Minikube tunnel URL: http://127.0.0.1:63732; background process must stay running.



### Git release verification - PASS
Read-only checks on 25 October 2026 confirmed main and release-v1.0 both point to 228e6e789b9611b7fef082072f02fc86488b1b03 locally and on origin. History contains initial commit 6bf7ebf and release commit 228e6e7. v1.0.0-final is an annotated tag (git cat-file -t returned tag), with remote tag object 202de789c5968d9340b9b276ca2069ce18bbdd09 peeling to the release commit. git status reported clean and up to date with origin/main before this tracking update. This PROGRESS.md update is intentionally uncommitted; the user owns all Git writes. Jenkins execution and Jira remain pending.

### Jenkins diagnostic build 1 - partial prerequisite verification
Read actual saved log at C:\ProgramData\Jenkins\.jenkins\jobs\apstone-simple-pipeline\builds\1\log. whoami returned nt authority\system. git --version returned 2.43.0.windows.1. docker version returned client and server Engine 29.7.2, proving Docker server pipe access for this build's LocalSystem process. where python failed; Python execution was skipped by its conditional. Diagnostic exited 0 intentionally: Finished SUCCESS does not prove Python availability or completion of the required three-stage pipeline. Job name is apstone-simple-pipeline (missing initial c). No Jenkins settings or jobs changed by the agent. Awaiting user choice for a job-local Python path fix before source edits; actual LocalSystem Python access still needs verification.

### Jenkinsfile Python PATH fix - implemented; local verification PASS
User selected the recommended Jenkinsfile-only fix. Added a pipeline-local environment PATH prepending C:\Users\Asus\AppData\Local\Programs\Python\Python312 while retaining the inherited PATH. Exactly three original stages preserved; no global Jenkins/service/PATH/credential changes. Resolved Python 3.12.2 using that directory plus machine PATH and ran the extracted Build & Test commands via cmd: exit 0, exactly 9 passed (one dependency deprecation warning), required success echo printed. Newly created .ci-venv removed after an absolute-path check; Test-Path False. Actual LocalSystem Python execution and full pipeline remain pending user commit/push and user Jenkins clicks. Existing annotated release tag is unchanged. Evidence: outputs/jenkins-python-path-local-check.log.
