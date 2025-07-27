# 🚀 XMRTNET Deployment Guide

## Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FDevGruGold%2FXMRT-Ecosystem&env=VITE_API_BASE_URL,VITE_STRIPE_PUBLISHABLE_KEY,VITE_WALLET_CONNECT_PROJECT_ID&envDescription=Environment%20variables%20for%20XMRTNET%20CashDapp&envLink=https%3A%2F%2Fgithub.com%2FDevGruGold%2FXMRT-Ecosystem%2Fblob%2Fmain%2F.env.example)

## 📋 Prerequisites

- Node.js 18+ 
- pnpm 8+
- Vercel account
- Git

## 🔧 Environment Setup

1. **Copy Environment Template**
   ```bash
   cp .env.example .env.local
   ```

2. **Configure Required Variables**
   ```bash
   # Minimum required for basic functionality
   VITE_API_BASE_URL=https://your-api-domain.com
   VITE_MOCK_API=true  # Set to false when real APIs are ready
   
   # For wallet functionality
   VITE_WALLET_CONNECT_PROJECT_ID=your_project_id
   VITE_METAMASK_ENABLED=true
   
   # For payment processing
   VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
   ```

## 🚀 Deployment Methods

### Method 1: Vercel CLI (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Method 2: GitHub Integration

1. **Connect Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import from GitHub: `DevGruGold/XMRT-Ecosystem`

2. **Configure Build Settings**
   - Framework Preset: `Other`
   - Build Command: `cd frontend/xmrt-dao-frontend && pnpm install && pnpm run build`
   - Output Directory: `frontend/xmrt-dao-frontend/dist`
   - Install Command: `pnpm install --store=node_modules/.pnpm-store`

3. **Add Environment Variables**
   - Copy variables from `.env.example`
   - Add them in Vercel project settings

### Method 3: Manual Build

1. **Build Locally**
   ```bash
   cd frontend/xmrt-dao-frontend
   pnpm install
   pnpm run build
   ```

2. **Upload to Vercel**
   ```bash
   vercel --prebuilt
   ```

## 🔐 Environment Variables

### Required Variables
```bash
VITE_API_BASE_URL=https://api.xmrtnet.com
VITE_WALLET_CONNECT_PROJECT_ID=your_project_id
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
```

### Optional Variables
```bash
# Blockchain RPCs
VITE_ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
VITE_POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_KEY

# Analytics
VITE_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX

# Feature Flags
VITE_ENABLE_CRYPTO_TRADING=true
VITE_ENABLE_NFT_MARKETPLACE=true
```

## 🧪 Testing Deployment

### Local Testing
```bash
# Install dependencies
pnpm install

# Start development server
cd frontend/xmrt-dao-frontend
pnpm run dev

# Build and preview
pnpm run build
pnpm run preview
```

### Production Testing
1. **Check Build Output**
   ```bash
   cd frontend/xmrt-dao-frontend/dist
   ls -la
   ```

2. **Test Routes**
   - `/` - Login page
   - `/dashboard` - Main dashboard (after login)
   - `/activity` - Transaction history
   - `/terminal` - Payment terminal
   - `/banking` - Banking features
   - `/assets` - Portfolio management
   - `/settings` - User settings

3. **Mobile Responsiveness**
   - Test on various screen sizes
   - Verify touch interactions
   - Check navigation functionality

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules pnpm-lock.yaml
   pnpm install
   ```

2. **Environment Variables Not Working**
   - Ensure variables start with `VITE_`
   - Check Vercel project settings
   - Redeploy after adding variables

3. **Routing Issues**
   - Verify `vercel.json` rewrites configuration
   - Check SPA routing setup

4. **Performance Issues**
   ```bash
   # Analyze bundle size
   pnpm run build
   npx vite-bundle-analyzer dist
   ```

### Debug Mode
```bash
# Enable debug logging
VITE_DEBUG_MODE=true pnpm run dev
```

## 📊 Performance Optimization

### Build Optimization
- Code splitting enabled
- Tree shaking configured
- Asset optimization
- Gzip compression

### Runtime Optimization
- Lazy loading components
- Image optimization
- Service worker caching
- CDN integration

## 🔒 Security Considerations

### Headers Configuration
- CSP headers configured
- XSS protection enabled
- HTTPS enforcement
- Secure cookie settings

### API Security
- CORS properly configured
- Rate limiting implemented
- Input validation
- Authentication tokens

## 📈 Monitoring

### Analytics Setup
1. **Google Analytics**
   ```bash
   VITE_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
   ```

2. **Error Tracking**
   ```bash
   VITE_SENTRY_DSN=your_sentry_dsn
   ```

3. **Performance Monitoring**
   - Core Web Vitals tracking
   - Real User Monitoring (RUM)
   - Synthetic monitoring

## 🔄 CI/CD Pipeline

### GitHub Actions (Optional)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## 📞 Support

- **Documentation**: [GitHub Repository](https://github.com/DevGruGold/XMRT-Ecosystem)
- **Issues**: [GitHub Issues](https://github.com/DevGruGold/XMRT-Ecosystem/issues)
- **Discord**: [Community Server](https://discord.gg/xmrt)

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificate active
- [ ] Custom domain configured
- [ ] Analytics tracking enabled
- [ ] Error monitoring setup
- [ ] Performance monitoring active
- [ ] Security headers configured
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured
- [ ] Documentation updated

---

**Built with ❤️ by the XMRT Community**

*Ready for production deployment on Vercel with full mobile responsiveness and placeholder APIs.*

