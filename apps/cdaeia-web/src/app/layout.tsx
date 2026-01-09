import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Diagnostic CDAEIA - Ran.AI Agency",
  description: "Evaluez votre eligibilite au credit d'impot CDAEIA pour les entreprises technologiques quebecoises integrant l'intelligence artificielle.",
  keywords: ["CDAEIA", "credit impot", "IA", "Quebec", "PME", "technologie", "diagnostic"],
  authors: [{ name: "Ran.AI Agency" }],
  openGraph: {
    title: "Diagnostic CDAEIA - Ran.AI Agency",
    description: "Evaluez gratuitement votre eligibilite au credit d'impot CDAEIA",
    type: "website",
    locale: "fr_CA",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={`${inter.variable} font-sans antialiased bg-gray-50`}>
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">R</span>
                </div>
                <div>
                  <span className="font-semibold text-gray-900">Ran.AI Agency</span>
                  <span className="hidden sm:inline text-gray-500 text-sm ml-2">| Diagnostic CDAEIA</span>
                </div>
              </div>
              <nav className="flex items-center gap-4">
                <a
                  href="https://www.ran-ai-agency.ca"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Site web
                </a>
                <a
                  href="mailto:info@ran-ai-agency.ca"
                  className="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Contact
                </a>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="min-h-[calc(100vh-64px)]">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="text-sm text-gray-500">
                &copy; {new Date().getFullYear()} Ran.AI Agency. Tous droits reserves.
              </div>
              <div className="flex items-center gap-6 text-sm text-gray-500">
                <span>514-918-1241</span>
                <span>info@ran-ai-agency.ca</span>
                <a
                  href="https://www.ran-ai-agency.ca"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-gray-900"
                >
                  ran-ai-agency.ca
                </a>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
