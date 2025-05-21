import * as Sentry from "@sentry/react";
import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";
import type { Route } from "./+types/root";
import "./app.css";
import { useEffect } from "react";

export const links: Route.LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap",
  },
];

const CONTENTSQUARE_ID = 6408235;

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
        {/* Hotjar tracking tag */}
        <script
          src={`https://static.hj.contentsquare.net/c/csq-${CONTENTSQUARE_ID}.js`}
          async
        />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  useEffect(() => {
    // see https://docs.sentry.io/platforms/javascript/guides/react-router/data-management/data-collected/ for more info
    Sentry.init({
      dsn: "https://852023ec5d9fe86c64eed907e04346e4@o4509334816489472.ingest.de.sentry.io/4509334885564496",
      sendDefaultPii: true,
      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration(),
        Sentry.feedbackIntegration({
          colorScheme: "system",
        }),
      ],
      tracesSampleRate: 1.0,
      tracePropagationTargets: [
        "localhost",
        /^https:\/\/eutop-mediamind-backend\.vercel\.app\/api/,
      ],
      // Session Replay
      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,
      environment: import.meta.env.MODE,
    });
  }, []);

  return <Outlet />;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = "Oops!";
  let details = "An unexpected error occurred.";
  let stack: string | undefined;

  if (isRouteErrorResponse(error)) {
    message = error.status === 404 ? "404" : "Error";
    details =
      error.status === 404
        ? "The requested page could not be found."
        : error.statusText || details;
  } else if (import.meta.env.DEV && error && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <main className="pt-16 p-4 container mx-auto">
      <h1>{message}</h1>
      <p>{details}</p>
      {stack && (
        <pre className="w-full p-4 overflow-x-auto">
          <code>{stack}</code>
        </pre>
      )}
    </main>
  );
}
