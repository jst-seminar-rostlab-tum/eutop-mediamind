import {
  SignedOut,
  SignInButton,
  SignedIn,
  UserButton,
} from "@clerk/react-router";
import { User } from "lucide-react";
import { Link, useSearchParams } from "react-router";
import { Button } from "~/components/ui/button";

// TODO use dashboard
const DEFAULT_REDIRECT_URL = "/dashboard";

export default function Header() {
  const [searchParams] = useSearchParams();
  const redirectUrl = searchParams.get("redirect_url");

  return (
    <div className="p-4 w-full flex justify-between items-center">
      <Link to="/">
        <img src="/MediaMind_Logo.svg" alt="MediaMind_Logo" width={"180px"} />
      </Link>
      <SignedOut>
        <Button variant={"outline"} asChild>
          <span>
            <User />
            <SignInButton
              forceRedirectUrl={redirectUrl ?? DEFAULT_REDIRECT_URL}
            />
          </span>
        </Button>
      </SignedOut>
      <SignedIn>
        <UserButton />
      </SignedIn>
    </div>
  );
}
