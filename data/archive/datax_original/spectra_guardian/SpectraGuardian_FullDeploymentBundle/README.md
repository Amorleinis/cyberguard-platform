# Spectra Guardian Full Deployment Bundle

This bundle includes:

- Helm chart for Kubernetes deployment
- Kubernetes manifests (deployments, services, ingress with TLS + basic auth)
- GitHub Actions workflow for CI/CD
- Dockerfile and docker-compose.yml
- Terraform scripts for AWS EC2 provisioning
- Enhanced Streamlit dashboard with authentication snippet

## How to use

1. Customize values in Helm chart (values.yaml).
2. Replace docker image tags in manifests.
3. Set up GitHub Secrets for Docker Hub and Kubernetes access.
4. Run terraform scripts to provision AWS EC2 if needed.
5. Deploy Helm chart on your Kubernetes cluster.
6. Apply ingress manifests for TLS and basic auth.
7. Run docker-compose or use Docker commands to build/test locally.
