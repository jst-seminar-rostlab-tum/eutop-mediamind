import Layout from "~/custom-components/layout";
import { AlertTriangle, Ban, CircleX, Lock } from "lucide-react";
import { useParams } from "react-router";
import Text from "~/custom-components/text";
import type { ReactElement } from "react";

const icons: Record<string, ReactElement> = {
  "401": <Lock className="h-12 w-12" />,
  "403": <Ban className="h-12 w-12" />,
  "404": <AlertTriangle className="h-12 w-12" />,
  fallback: <CircleX className="h-12 w-12" />,
};

const defaultMessages: Record<string, { title: string; message: string }> = {
  "401": {
    title: "Not Logged In",
    message:
      "You need to log in to access this page. After you signed in you are redirected to the requested ressource",
  },
  "403": {
    title: "Access Denied",
    message:
      "You don't have permission to view this page or you are not assigned to an organization yet. You need to be part of an organization to access Mediamind. Please contact your admin.",
  },
  "404": {
    title: "Page Not Found",
    message: "The page you are looking for does not exist.",
  },
  fallback: {
    title: "Oohps!",
    message: "Something went wrong! Please contact your admin.",
  },
};

export const ErrorPage = ({
  title,
  message,
  stack,
}: {
  title?: string;
  message?: string;
  stack?: string;
}) => {
  const { code } = useParams();

  const usedTitle = title ?? defaultMessages[code ?? "fallback"].title;
  const usedMessage = message ?? defaultMessages[code ?? "fallback"].message;
  const usedIcon = icons[code ?? "fallback"];

  return (
    <>
      <Layout className="flex justify-center">
        <div className="flex justify-center mb-4">{usedIcon}</div>

        <Text className="mb-2 flex justify-center" hierachy={1}>
          {usedTitle}
        </Text>

        <Text className="flex justify-center text-center">{usedMessage}</Text>

        {stack && (
          <pre className="w-full p-4 overflow-x-auto">
            <code>{stack}</code>
          </pre>
        )}
      </Layout>
    </>
  );
};
