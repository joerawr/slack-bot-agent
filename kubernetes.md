# Deploying Slack Bot to Kubernetes

This guide provides the steps to deploy the Slack Bot to a Kubernetes cluster.

## 1. Build and Push the Docker Image

The bot needs to be containerized and pushed to a registry that your Kubernetes cluster can access.

```bash
# Build the image from the repository root
docker build -t ghcr.io/joerawr/slack-bot-agent:latest .

# Push the image to the registry
docker push ghcr.io/joerawr/slack-bot-agent:latest
```

## 2. Create Namespace and Secrets

Create a dedicated namespace for the bot and a secret to hold the required API tokens.

```bash
# Create the namespace
kubectl create ns bots

# Create the secret
kubectl -n bots create secret generic slack-bot-secrets \
  --from-literal=SLACK_BOT_TOKEN='your-slack-bot-token' \
  --from-literal=SLACK_APP_TOKEN='your-slack-app-token' \
  --from-literal=GEMINI_API_KEY='your-gemini-api-key' \
  --from-literal=OPENAI_API_KEY=''
```
**Note:** You must provide a value for either `GEMINI_API_KEY` or `OPENAI_API_KEY`, but not both.

## 3. Persistent Storage

To maintain the bot's history across pod restarts and node changes, we use a PersistentVolumeClaim (PVC). This example uses Longhorn, but you can adapt it to your own storage solution.

Create the following file:

**`slack-bot-pvc.yaml`**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: slack-bot-history
  namespace: bots
spec:
  accessModes: ["ReadWriteMany"]   # Requires a storage class that supports RWX
  resources:
    requests:
      storage: 1Gi
  storageClassName: longhorn       # Change if your RWX class is named differently
```

## 4. Deployment

The deployment file configures the bot's pod, mounts the persistent volume, and sets up health checks.

**Note on the Liveness Probe:** The initial liveness probe using `pgrep` was found to be unreliable. It has been replaced with a more robust `startupProbe` and `livenessProbe` that checks the main process ID.

Create the following file:

**`slack-bot-deployment.yaml`**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: slack-bot
  namespace: bots
spec:
  replicas: 1
  selector:
    matchLabels:
      app: slack-bot
  template:
    metadata:
      labels:
        app: slack-bot
    spec:
      terminationGracePeriodSeconds: 15
      containers:
        - name: app
          image: ghcr.io/joerawr/slack-bot-agent:latest
          imagePullPolicy: IfNotPresent
          env:
            - name: SLACK_BOT_TOKEN
              valueFrom: { secretKeyRef: { name: slack-bot-secrets, key: SLACK_BOT_TOKEN } }
            - name: SLACK_APP_TOKEN
              valueFrom: { secretKeyRef: { name: slack-bot-secrets, key: SLACK_APP_TOKEN } }
            - name: GEMINI_API_KEY
              valueFrom: { secretKeyRef: { name: slack-bot-secrets, key: GEMINI_API_KEY } }
            - name: OPENAI_API_KEY
              valueFrom: { secretKeyRef: { name: slack-bot-secrets, key: OPENAI_API_KEY } }
          volumeMounts:
            - name: history
              mountPath: /app/history
          startupProbe:
            exec:
              command: ["/bin/sh", "-c", "kill -0 1"]
            failureThreshold: 30
            periodSeconds: 2
          livenessProbe:
            exec:
              command: ["/bin/sh", "-c", "kill -0 1"]
            initialDelaySeconds: 30
            periodSeconds: 30
          resources:
            requests: { cpu: "50m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "512Mi" }
      volumes:
        - name: history
          persistentVolumeClaim:
            claimName: slack-bot-history
```

**Important:** This deployment is designed to run with a single replica (`replicas: 1`). Running multiple pods is not recommended unless you are configuring them for different Slack workspaces, as it can lead to unexpected behavior.

## 5. Apply the Configuration

Apply the YAML files to your cluster to deploy the bot.

```bash
kubectl apply -f slack-bot-pvc.yaml
kubectl apply -f slack-bot-deployment.yaml
```

## 6. Auditing the History File

If you need to inspect the conversation history file directly, you can use `kubectl exec`.

1.  **Get the pod name:**
    First, find the name of the running pod and export it as a variable to make the next commands easier.

    ```bash
    export POD_NAME=$(kubectl -n bots get pods -l app=slack-bot -o jsonpath='{.items[0].metadata.name}')
    ```

2.  **List files in the history volume:**
    Use the pod name to list the contents of the `/app/history` directory. The history files are named after the Slack channel ID (e.g., `C08M4A7R6P9.json`).

    ```bash
    kubectl -n bots exec $POD_NAME -- ls -l /app/history
    ```

3.  **View the history file content:**
    To view the contents of a history file in a readable, formatted way, pipe the output to `jq`. Replace `<channel_id>.json` with the actual filename from the output of the previous command.

    ```bash
    kubectl -n bots exec $POD_NAME -- cat /app/history/<channel_id>.json | jq .
    ```

    **Note:** This command uses `jq`, a lightweight command-line JSON processor. If you don't have it installed, you can use a package manager:
    - **macOS (Homebrew):** `brew install jq`
    - **Debian/Ubuntu:** `sudo apt-get install jq`

