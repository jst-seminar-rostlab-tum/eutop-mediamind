import { useClerk, useSession, useUser } from "@clerk/react-router";
import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router";

// TODO: add mediamind backend request to return role/rights of user (+ within an organization)
export const useAuthorization = () => {
  const { isSignedIn, user, isLoaded } = useUser();
  const { session } = useSession();
  const clerkClient = useClerk();

  const navigate = useNavigate();
  const { pathname } = useLocation();

  console.log("clientId", clerkClient.client?.id);
  session?.getToken().then((t) => console.log("sessionToken", t));

  // redirect to error page, when not signed in
  useEffect(() => {
    if (
      isLoaded &&
      !isSignedIn &&
      !pathname.includes("error") &&
      pathname !== "/"
    ) {
      navigate("error/401?redirect_url=" + pathname);
    }
  });

  // sync user, when signed up or when something was changed in the user profile
  useEffect(() => {
    if (
      isLoaded &&
      isSignedIn &&
      ((user.updatedAt &&
        user.lastSignInAt &&
        Math.abs(user.updatedAt.getTime() - user.lastSignInAt.getTime()) >
          1000) ||
        (user.createdAt && Date.now() - user.createdAt.getTime() < 5000))
    ) {
      // Todo: Call backend to sync clerk user with mediamind db user
      console.log("user updated!");
    }
  }, [user, isLoaded, isSignedIn]);
};
