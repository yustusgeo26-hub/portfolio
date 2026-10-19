import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Yustus Geofrey | Data, Software & Games', description: 'Portfolio of Yustus Geofrey — data analytics, software development, automation, dashboards and game development.' };
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}</body></html>; }
