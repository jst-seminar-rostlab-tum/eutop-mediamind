import {
  SignedOut,
  SignedIn,
  UserButton,
  SignIn,
  SignUp,
} from "@clerk/react-router";
import { Link, useLocation, useSearchParams } from "react-router";
import { Building2, Settings, User } from "lucide-react";
import { Button } from "~/components/ui/button";
import { useAuthorization } from "~/hooks/use-authorization";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "~/components/ui/popover";
import { useEffect, useState } from "react";

const SIGN_UP = "ui_sign_up";
const SIGN_IN = "ui_sign_in";

export default function Header() {
  const { isSignedIn, user } = useAuthorization();
  const { pathname } = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const redirectUrl = searchParams.get("redirect_url");
  const [openLogin, setOpenLogin] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  useEffect(() => {
    if (searchParams.get(SIGN_UP) === "true") {
      setIsSignUp(true);
      const params = new URLSearchParams(searchParams);
      params.delete(SIGN_UP);
      setSearchParams(params);
    } else if (searchParams.get(SIGN_IN) === "true") {
      setIsSignUp(false);
      const params = new URLSearchParams(searchParams);
      params.delete(SIGN_IN);
      setSearchParams(params);
    }
  }, [searchParams]);

  // Close login on route change as header is always present
  useEffect(() => {
    setOpenLogin(false);
  }, [pathname]);

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
      <div className="flex justify-end items-center gap-4">
        <SignedOut>
          <Popover
            open={openLogin}
            onOpenChange={(open) => {
              setIsSignUp(false);
              setOpenLogin(open);
            }}
          >
            <PopoverTrigger asChild>
              <Button variant="outline">
                <>
                  <User /> Login
                </>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[25rem] p-0 border-none">
              {!isSignUp ? (
                <SignIn
                  forceRedirectUrl={redirectUrl ?? "/dashboard"}
                  signUpUrl={pathname + "?" + SIGN_UP + "=true"}
                  routing="hash"
                />
              ) : (
                <SignUp
                  forceRedirectUrl={redirectUrl ?? "/dashboard"}
                  signInUrl={pathname + "?" + SIGN_IN + "=true"}
                  routing="hash"
                />
              )}
            </PopoverContent>
          </Popover>
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
