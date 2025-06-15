import Layout from "~/custom-components/layout";
import {
  AlertTriangle,
  Ban,
  Building2,
  Frown,
  House,
  Lock,
  MoveRight,
} from "lucide-react";
import { Link, useNavigate, useParams } from "react-router";
import Text from "~/custom-components/text";
import { useEffect, type ReactElement } from "react";
import { Button } from "~/components/ui/button";
import { useAuthorization } from "~/hooks/use-authorization";

const icons: Record<string, ReactElement> = {
  "401": <Lock className="h-12 w-12" />,
  "403": <Ban className="h-12 w-12" />,
  "404": <AlertTriangle className="h-12 w-12" />,
  "no-org": <Building2 className="h-12 w-12" />,
  fallback: <Frown className="h-12 w-12" />,
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
      "You don't have permission to view this page. You need to be part of an organization to access their pages. Please contact your admin.",
  },
  "404": {
    title: "Page Not Found",
    message: "The page you are looking for does not exist.",
  },
  "no-org": {
    title: "No Organization",
    message:
      "You are not assigned to an organization. You need to be part of an organization to access Mediamind. Please contact your admin.",
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
  code: passedCode,
}: {
  title?: string;
  message?: string;
  stack?: string;
  code?: number;
}) => {
  const { user } = useAuthorization();
  const { code: paramCode } = useParams();
  const navigate = useNavigate();

  const code = passedCode ?? paramCode;

  const usedTitle = title ?? defaultMessages[code ?? "fallback"].title;
  const usedMessage = message ?? defaultMessages[code ?? "fallback"].message;
  const usedIcon = icons[code ?? "fallback"];

  useEffect(() => {
    if (paramCode === "no-org" && user?.organization_id) {
      navigate("/dashboard");
    }
  }, [paramCode, user?.organization_id, navigate]);

  return (
    <>
      <Layout className="flex flex-col justify-center">
        <div className="flex justify-center mt-24 mb-4">{usedIcon}</div>

        <Text className="mb-2 flex justify-center" hierachy={1}>
          {usedTitle}
        </Text>

        <Text className="flex justify-center text-center">{usedMessage}</Text>

        <div className="flex justify-center m-4">
          <Link to="/">
            <Button variant="outline">
              <MoveRight />
              Back to Home
              <House />
            </Button>
          </Link>
        </div>

        {stack && (
          <pre className="w-full p-4 overflow-x-auto">
            <code>{stack}</code>
          </pre>
        )}
      </Layout>
    </>
  );
};
