import { useClerk, useSession, useUser } from "@clerk/react-router";
import { useEffect } from "react";
import { useSearchParams } from "react-router";

export const NEW_USER_SEARCH_PARAM_NAME = "new_user";

// TODO: add mediamind backend request to return role/rights of user (+ within an organization)
export const useAuthorization = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isSignedIn, user, isLoaded } = useUser();
  const { session } = useSession();
  const clerkClient = useClerk();
  console.log("clientId", clerkClient.client?.id);
  session?.getToken().then((t) => console.log("sessionToken", t));

  // create user in mediamind backend, when they return from signing up at clerk
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
};
