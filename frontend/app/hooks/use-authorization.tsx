import { useSession, useUser } from "@clerk/react-router";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type PropsWithChildren,
} from "react";
import { useLocation, useNavigate } from "react-router";
import { BASE_URL } from "types/api";

type UseAuthorizationReturn = {
  sessionToken?: string;
  isLoaded: boolean;
  isSignedIn: boolean;
  authorizationHeaders: Record<string, string>;
};

const AuthorizationContext = createContext({
  isLoaded: false,
  isSignedIn: false,
  authorizationHeaders: {},
});

// TODO: add mediamind backend request to return role/rights of user (+ within an organization)
export const AuthorizationContextProvider = ({
  children,
}: PropsWithChildren) => {
  const [token, setToken] = useState<string | undefined>();
  const { isSignedIn, user, isLoaded } = useUser();
  const { session } = useSession();

  const navigate = useNavigate();
  const { pathname } = useLocation();

  useEffect(() => {
    session?.getToken().then((t) => t && setToken(t));
  }, [session]);

  const authenticatedFetch = useCallback(
    async (...args: [RequestInfo, RequestInit?]) => {
      const [resource, config = {}] = args;
      const headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };

      return fetch(resource, {
        ...config,
        headers,
      }).then((res) => res.json());
    },
    [token],
  );

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
      token &&
      isLoaded &&
      isSignedIn &&
      user.lastSignInAt &&
      Math.abs(Date.now() - user.lastSignInAt.getTime()) < 2000
    ) {
      authenticatedFetch(BASE_URL + "/users/sync", {
        method: "POST",
      });
    }
  }, [user, isLoaded, isSignedIn, token]);

  const value: UseAuthorizationReturn = {
    sessionToken: token,
    isLoaded,
    isSignedIn: Boolean(isSignedIn),
    authorizationHeaders: {
      Authorization: `Bearer ${token}`,
    },
  };
  return (
    <AuthorizationContext.Provider value={value}>
      {children}
    </AuthorizationContext.Provider>
  );
};

export const useAuthorization = () => useContext(AuthorizationContext);
