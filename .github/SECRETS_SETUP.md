# GitHub Secrets Setup Guide

This guide explains how to configure the required GitHub secrets for CI/CD workflows.

## Required Secrets

Navigate to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

### DockerHub Secrets

| Secret Name | Description |
|-------------|-------------|
| `DOCKERHUB_USERNAME` | Your DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub access token (not password) |

#### How to Get DockerHub Token

1. Log in to [DockerHub](https://hub.docker.com)
2. Go to **Account Settings → Security**
3. Click **New Access Token**
4. Give it a description (e.g., "GitHub Actions")
5. Select **Read, Write, Delete** permissions
6. Click **Generate**
7. Copy the token immediately (you won't see it again)

## Setting Up Secrets

### Via GitHub Web UI

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Secrets and variables** (left sidebar)
4. Click **Actions**
5. Click **New repository secret**
6. Enter the secret name and value
7. Click **Add secret**

### Via GitHub CLI

```bash
# Set DockerHub secrets
gh secret set DOCKERHUB_USERNAME --body "your-username"
gh secret set DOCKERHUB_TOKEN --body "your-token"
```

## Verification

After setting up secrets, you can verify they're configured:

1. Go to **Settings → Secrets and variables → Actions**
2. You should see both secrets listed (values are hidden)

To test the CI/CD pipeline:

1. Create a new branch
2. Make a small change
3. Open a Pull Request
4. CI workflow should run automatically
5. Merge to main
6. Deploy workflow should build and push images to DockerHub

## Troubleshooting

### "Bad credentials" error in DockerHub

- Make sure you're using an access token, not your password
- Check that the token has Read/Write permissions
- Verify the token hasn't expired

### Secrets not found

- Secret names are case-sensitive
- Make sure there are no extra spaces in the values
- Check that secrets are set at the repository level, not organization level

## Docker Images

After successful deployment, your images will be available at:

- `<username>/fleet-cascade-api:latest`
- `<username>/fleet-cascade-dashboard:latest`

### Pull and Run Locally

```bash
# Pull images
docker pull <username>/fleet-cascade-api:latest
docker pull <username>/fleet-cascade-dashboard:latest

# Or use docker-compose with the images
docker-compose pull
docker-compose up
```
