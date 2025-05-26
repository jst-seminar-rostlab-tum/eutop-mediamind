import {
  SignedOut,
  SignInButton,
  SignedIn,
  UserButton,
  useUser,
} from "@clerk/react-router";
import { User } from "lucide-react";
import { useEffect } from "react";
import { useSearchParams } from "react-router";
import { Button } from "~/components/ui/button";

const NEW_USER_SEARCH_PARAM_NAME = "new_user";

export default function Header() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isSignedIn, user, isLoaded } = useUser();

  useEffect(() => {
    if (
      (searchParams.get(NEW_USER_SEARCH_PARAM_NAME) && isSignedIn && isLoaded,
      user)
    ) {
      console.log(user);

      //TODO: signup at mediamind backend

      searchParams.delete(NEW_USER_SEARCH_PARAM_NAME);
      setSearchParams(searchParams, { replace: true });
    }
  }, [isSignedIn, user, isLoaded]);

  return (
    <div className="p-4 w-full flex justify-between items-center">
      <img src="/MediaMind_Logo.svg" alt="MediaMind_Logo" width={"180px"} />
      <SignedOut>
        <Button variant={"outline"} asChild>
          <span>
            <User />
            {/* TODO: dashboard url */}
            <SignInButton
              forceRedirectUrl="/"
              signUpForceRedirectUrl={`/?${NEW_USER_SEARCH_PARAM_NAME}=true`}
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
