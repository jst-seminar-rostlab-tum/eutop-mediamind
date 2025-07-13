import "./i18n";
import * as Sentry from "@sentry/react";
import {
  isRouteErrorResponse,
  Link,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useLocation,
} from "react-router";
import type { Route } from "./+types/root";
import "./app.css";
import { rootAuthLoader } from "@clerk/react-router/ssr.server";
import { ClerkProvider } from "@clerk/react-router";
import Header from "./custom-components/header";
import { ErrorPage } from "./pages/error/error";
import { useEffect } from "react";
import {
  AuthorizationContextProvider,
  useAuthorization,
} from "./hooks/use-authorization";
import { Toaster } from "~/components/ui/sonner";
import { Loader2 } from "lucide-react";
import { Suspense } from "react";

declare global {
  interface Window {
    __sentryInitialized?: boolean;
  }
}

export async function loader(args: Route.LoaderArgs) {
  return rootAuthLoader(args);
}

export function meta() {
  return [
    { title: "MediaMind" },
    { name: "description", content: "Welcome to MediaMind!" },
  ];
}

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

export function Layout({ children }: { children: React.ReactNode }) {
  const hotjarId = import.meta.env.VITE_HOTJAR_TAG;

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
        {/* Hotjar tracking tag */}
        {hotjarId && (
          <script
            dangerouslySetInnerHTML={{
              __html: `(function (c, s, q, u, a, r, e) {
                c.hj=c.hj||function(){(c.hj.q=c.hj.q||[]).push(arguments)};
                c._hjSettings = { hjid: a };
                r = s.getElementsByTagName('head')[0];
                e = s.createElement('script');
                e.async = true;
                e.src = q + c._hjSettings.hjid + u;
                r.appendChild(e);
              })(window, document, 'https://static.hj.contentsquare.net/c/csq-', '.js', ${hotjarId});`,
            }}
          />
        )}
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
        <Toaster />
      </body>
    </html>
  );
}

const OutletWrapper = () => {
  const { user } = useAuthorization();
  const { pathname } = useLocation();

  const isProtectedPath = pathname !== "/" && !pathname.includes("error");

  // ensure that no requests are sent before the authentication with clerk is completed (only for protected paths)
  return user || !isProtectedPath ? (
    <Outlet />
  ) : (
    <div className="flex items-center justify-center py-8">
      <Loader2 className="h-8 w-8 animate-spin" />
      <span className="ml-2 text-muted-foreground">Loading user...</span>
    </div>
  );
};

export default function App({ loaderData }: Route.ComponentProps) {
  useEffect(() => {
    if (window.__sentryInitialized) {
      return;
    }
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
    window.__sentryInitialized = true;
  }, []);

  return (
    <Suspense fallback={<div>Loading translations...</div>}>
      <ClerkProvider loaderData={loaderData}>
        <AuthorizationContextProvider>
          <Header />
          <OutletWrapper />
        </AuthorizationContextProvider>
      </ClerkProvider>
    </Suspense>
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message: string | undefined;
  let details: string | undefined;
  let stack: string | undefined;
  let code: number | undefined;

  if (isRouteErrorResponse(error)) {
    code = error.status;
  } else if (import.meta.env.DEV && error && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <>
      <div className="p-4 w-full flex justify-between items-center">
        <Link to="/">
          <img src="/MediaMind_Logo.svg" alt="MediaMind_Logo" width={"180px"} />
        </Link>
      </div>
      <ErrorPage code={code} title={message} message={details} stack={stack} />
    </>
  );
}
