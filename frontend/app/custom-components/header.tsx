import {
  SignedOut,
  SignInButton,
  SignedIn,
  UserButton,
} from "@clerk/react-router";
import { Link, useSearchParams } from "react-router";
import { Settings, User } from "lucide-react";
import { Button } from "~/components/ui/button";
import { useAuthorization } from "~/hooks/use-authorization";

export default function Header() {
  const { isSignedIn, user } = useAuthorization();
  const [searchParams] = useSearchParams();
  const redirectUrl = searchParams.get("redirect_url");

  return (
    <div className="p-4 w-full flex justify-between items-center">
      <Link to="/">
        <img src="/MediaMind_Logo.svg" alt="MediaMind_Logo" width={"140rem"} />
      </Link>
      <div className="col-span-10 flex justify-end gap-2">
        <SignedOut>
          <SignInButton forceRedirectUrl={redirectUrl ?? "/dashboard"}>
            <Button asChild variant="outline">
              <span>
                <User /> Login
              </span>
            </Button>
          </SignInButton>
        </SignedOut>
        <SignedIn>
          <UserButton />
        </SignedIn>
        {isSignedIn && user?.is_superuser && (
          <Link to="/admin">
            <Button variant="outline">
              <Settings />
            </Button>
          </Link>
        )}
      </div>
    </div>
  );
}
