import {
  SignedOut,
  SignInButton,
  SignedIn,
  UserButton,
} from "@clerk/react-router";
import { User } from "lucide-react";
import { Button } from "~/components/ui/button";
import { useAuthorization } from "~/hooks/use-authorization";

export default function Header() {
  useAuthorization();

  return (
    <div className="p-4 w-full flex justify-between items-center">
      <img src="/MediaMind_Logo.svg" alt="MediaMind_Logo" width={"180px"} />
      <SignedOut>
        <Button variant={"outline"} asChild>
          <span>
            <User />
            {/* TODO: dashboard url */}
            <SignInButton forceRedirectUrl="/" />
          </span>
        </Button>
      </SignedOut>
      <SignedIn>
        <UserButton />
      </SignedIn>
    </div>
  );
}
