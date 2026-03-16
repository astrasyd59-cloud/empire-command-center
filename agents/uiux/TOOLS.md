# TOOLS.md - UI/UX Designer Agent

## Deployment Platforms

### Vercel
- **Token:** `VERCEL_TOKEN`
- **Primary Project:** `dibs-empire-roadmap`
- **Usage:** `vercel --token $VERCEL_TOKEN`
- **Features Used:**
  - Git-based deployments
  - Preview deployments
  - Environment variables
  - Custom domains

### Netlify
- **Token:** `NETLIFY_TOKEN`
- **Usage:** `netlify deploy --prod`
- **Features Used:**
  - Manual deploys via CLI
  - Deploy previews
  - Form handling (future)
  - Edge functions (future)

## Development Tools

### Local Stack
- **Browser:** Chrome DevTools for debugging
- **Preview:** Live Server or Vite dev server
- **Validation:** W3C Validator, axe-core

### Asset Pipeline
- Image optimization: Squoosh or Sharp
- Icon set: Lucide or Heroicons
- Fonts: System stacks (no external font loading)

## Environment Variables

```bash
# Required
export VERCEL_TOKEN=""
export NETLIFY_TOKEN=""
```

## Tool Gaps

| Missing Tool | Impact | Workaround |
|--------------|--------|------------|
| Advanced animation library | Limited motion design | CSS transitions/animations only |
| A/B testing framework | No experiment tracking | Manual variant testing |
| Design system platform | Component consistency | Documented CSS patterns |
| Image CDN | Manual optimization | Pre-optimized assets |

## Wishlist

- GSAP or Framer Motion integration
- PostHog or Split for A/B testing
- Figma API for design tokens
- Cloudinary or Imgix for image optimization
