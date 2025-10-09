# Eliza Autonomous Agent Dashboard

A professional web-based dashboard for deploying and managing the Eliza autonomous agent.

## Features

- **Real-time Monitoring**: Track agent performance, cycles, and improvements
- **Configuration Management**: Easy configuration of GitHub credentials and settings
- **24/7 Operation**: Support for continuous autonomous operation
- **Dual-Repository Support**: Manages both xmrtnet and XMRT-Ecosystem repositories
- **Activity Logs**: Real-time logging of agent activities

## Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- GitHub Personal Access Token with repo permissions
- (Optional) Gemini API key for AI-enhanced analysis

### Installation

```bash
cd frontend/eliza-dashboard
pnpm install
```

### Development

```bash
pnpm run dev
```

The dashboard will be available at http://localhost:5173

### Production Build

```bash
pnpm run build
```

The production build will be in the `dist/` directory.

## Configuration

Configure the following settings in the dashboard:

- **GitHub Token**: Personal Access Token with repo permissions
- **GitHub User**: Your GitHub username (default: DevGruGold)
- **Target Repository**: Primary repository (default: xmrtnet)
- **Ecosystem Repository**: Secondary repository (default: XMRT-Ecosystem)
- **Gemini API Key**: (Optional) For AI-enhanced analysis
- **Cycle Interval**: Time between improvement cycles in seconds
- **Max Cycles**: Maximum number of cycles (0 = infinite)
- **Operation Mode**: continuous_24_7, production, or self_improvement

## Deployment

### Deploy to Render

1. Connect your GitHub repository to Render
2. Create a new Static Site
3. Set build command: `cd frontend/eliza-dashboard && pnpm install && pnpm run build`
4. Set publish directory: `frontend/eliza-dashboard/dist`

### Deploy to Vercel

```bash
cd frontend/eliza-dashboard
vercel
```

### Deploy to Netlify

```bash
cd frontend/eliza-dashboard
pnpm run build
netlify deploy --prod --dir=dist
```

## Usage

1. Open the dashboard in your browser
2. Navigate to the "Config" tab
3. Enter your GitHub credentials and settings
4. Click "Deploy to GitHub" to save configuration
5. Go to the "Control" tab
6. Click "Start Agent" to begin autonomous operation

## Architecture

The dashboard is built with:

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality React components
- **Lucide Icons**: Beautiful icon library

## Backend Integration

The dashboard communicates with the autonomous_eliza_continuous.py script through:

- GitHub API for configuration deployment
- Real-time status updates through GitHub commits
- Activity logs from repository reports

## Security

- All credentials are stored securely in environment variables
- GitHub tokens are never exposed in the frontend
- Configuration is deployed through secure GitHub API

## Support

For issues or questions, please open an issue in the GitHub repository.

---

Built with ❤️ by the Eliza Autonomous Agent Team
