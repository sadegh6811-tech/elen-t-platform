import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Elen-k Unified Workspace',
    short_name: 'Elen-k',
    description: 'Advanced MCDM Autonomous System Dashboard',
    start_url: '/',
    display: 'standalone',
    orientation: 'portrait',
    background_color: '#050808',
    theme_color: '#050808',
    icons: [
      {
        src: '/icon-192.svg',
        sizes: '192x192',
        type: 'image/svg+xml',
        purpose: 'any maskable'
      },
      {
        src: '/icon-512.svg',
        sizes: '512x512',
        type: 'image/svg+xml',
        purpose: 'any maskable'
      },
    ],
  }
}
