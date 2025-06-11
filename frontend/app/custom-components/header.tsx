import {
  SignedOut,
  SignInButton,
  SignedIn,
  UserButton,
} from "@clerk/react-router";
import { Link, useSearchParams } from "react-router";
import { Building2, Settings, User } from "lucide-react";
import { Button } from "~/components/ui/button";
import { useAuthorization } from "~/hooks/use-authorization";

export default function Header() {
  const { isSignedIn, user } = useAuthorization();
  const [searchParams] = useSearchParams();
  const redirectUrl = searchParams.get("redirect_url");

  return (
    <div className="p-4 w-full flex justify-between items-center">
      <div className="flex items-center gap-8">
        <Link to="/" className="mt-[0.3rem]">
          <img
            src="/MediaMind_Logo.svg"
            alt="MediaMind_Logo"
            width={"140rem"}
          />
        </Link>
        {isSignedIn && user?.organization_name && (
          <div className="flex items-center gap-2 ">
            <Building2 className="h-4 w-4" />
            <span className="text-sm font-semibold text-black">
              {user.organization_name}
            </span>
          </div>
        )}
      </div>
      <div className="col-span-10 flex justify-end gap-4">
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
