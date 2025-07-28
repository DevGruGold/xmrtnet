# Detailed Guide: Deploying XMRT Eliza on Render

This guide provides step-by-step instructions for deploying the XMRT Eliza autonomous implementation to Render.

## Prerequisites

Before you begin, make sure you have:

1. A [Render account](https://render.com/) (free tier is sufficient to start)
2. A fork or direct access to the [DevGruGold/xmrtnet](https://github.com/DevGruGold/xmrtnet) repository
3. The necessary API keys and credentials as listed in the `.env.example` file

## Step 1: Create a Blueprint Instance on Render

Render Blueprints allow you to deploy multiple services defined in a `render.yaml` file. For the XMRT Eliza project:

1. Log in to your Render account
2. Go to the Dashboard
3. Click "New +" button in the top right
4. Select "Blueprint" from the dropdown menu
5. Connect your GitHub account if you haven't already
6. Select your forked repository or the `DevGruGold/xmrtnet` repository
7. Select the branch `eliza-autonomous-phase1-20250726` (which contains the `render.yaml` file)
8. Click "Apply Blueprint"

## Step 2: Configure Environment Variables

The XMRT Eliza project requires several environment variables. In the Render Dashboard:

1. Navigate to "Environment Groups"
2. Click "New Environment Group"
3. Name it `xmrt-env-group` (to match the name in the `render.yaml` file)
4. Add the following key environment variables (see `.env.example` for a complete list):
   - `OPENAI_API_KEY` (required for the AI components)
   - `ANTHROPIC_API_KEY` (optional, for Claude models)
   - `ETHEREUM_RPC_URL` (for blockchain connectivity)
   - `WALLET_CONNECT_PROJECT_ID` (for wallet integration)
   - `DATABASE_URL` (if using a database)
   - `VITE_API_BASE_URL` (should be set to the URL of your backend API service)
5. Click "Create Environment Group"

## Step 3: Deploy the Services

The Blueprint will automatically start deploying three services:

1. **xmrt-eliza-frontend**: The React-based user interface
2. **xmrt-eliza-ai**: The AI automation service with Eliza integration
3. **xmrt-backend-api**: The main backend API

For each service:

1. Wait for the build and deployment to complete
2. Check the logs for any errors
3. Once deployed, you'll see a unique URL for each service

### Configuring Service Dependencies

After deployment, you need to ensure the services can communicate with each other:

1. Copy the URL of the `xmrt-backend-api` service
2. Go to the `xmrt-eliza-frontend` service settings
3. Add or update the environment variable `VITE_API_BASE_URL` with the backend API URL

## Step 4: Verify the Deployment

To verify that the deployment was successful:

1. Open the frontend URL in your browser
2. You should see the XMRT DAO interface
3. Check the logs of the AI automation service to ensure Eliza is running
4. Test basic functionality such as wallet connection and AI interactions

## Step 5: Automatic Updates

Render can be configured to automatically update your deployment when changes are pushed to GitHub:

1. Go to each service's settings
2. Under "Auto-Deploy", ensure "Deploy automatically on push" is enabled
3. This ensures that future updates to the codebase are automatically deployed

## Troubleshooting Common Issues

### Service Fails to Build

- Check the build logs for specific errors
- Ensure all dependencies are correctly specified in the requirements files
- Verify that the build commands in `render.yaml` are correct

### Environment Variable Issues

- Double-check that all required environment variables are set
- Ensure the environment group is correctly linked to all services
- Check for typos in variable names

### Frontend Cannot Connect to Backend

- Verify that `VITE_API_BASE_URL` is set correctly
- Check CORS settings in the backend code
- Ensure all services are running properly

### Eliza AI Service Errors

- Verify that the AI API keys are valid and have sufficient credits
- Check the AI service logs for specific error messages
- Ensure the AI service can connect to the backend API

## Next Steps

After successful deployment, you can:

1. Set up a custom domain for your services
2. Configure SSL certificates
3. Set up monitoring and alerts
4. Implement CI/CD pipelines for automated testing before deployment

## Support and Resources

If you encounter any issues during deployment:

- Check the [Render documentation](https://render.com/docs)
- Review the XMRT Eliza documentation in the repository
- Open an issue on the GitHub repository
- Contact support at joeyleepcs@gmail.com
