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
import type { MediamindUser } from "types/model";

type UseAuthorizationReturn = {
  sessionToken?: string;
  isLoaded: boolean;
  isSignedIn: boolean;
  authorizationHeaders: Record<string, string>;
  user?: MediamindUser;
};

const initialValue: UseAuthorizationReturn = {
  isLoaded: false,
  isSignedIn: false,
  authorizationHeaders: {},
  sessionToken: undefined,
  user: undefined,
};

const AuthorizationContext = createContext(initialValue);

export const AuthorizationContextProvider = ({
  children,
}: PropsWithChildren) => {
  const [token, setToken] = useState<string | undefined>();
  const { isSignedIn, isLoaded } = useUser();
  const { session } = useSession();
  const [mediamindUser, setMediamindUser] = useState<MediamindUser>();

  const navigate = useNavigate();
  const { pathname } = useLocation();

  useEffect(() => {
    const fetchToken = async () => {
      if (session) {
        const token = await session.getToken();
        if (token) {
          setToken(token);
        }
      }
    };
    fetchToken();
  }, [session]);

  const authenticatedFetch = useCallback(
    async (...args: [RequestInfo, RequestInit?]) => {
      const [resource, config = {}] = args;
      const headers = {
        ...config.headers,
        Authorization: `Bearer ${await session?.getToken()}`,
      };

      return fetch(resource, {
        ...config,
        headers,
      }).then((res) => res.json());
    },
    [session?.getToken],
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
  }, [isLoaded, isSignedIn, pathname]);

  useEffect(() => {
    if (
      mediamindUser &&
      !mediamindUser.organization_id &&
      !pathname.includes("error") &&
      pathname !== "/"
    ) {
      navigate("error/no-org");
    }
  }, [mediamindUser]);

  // We sync the clerk user, after intially loading the page and signing in at clerk
  useEffect(() => {
    if (isLoaded && isSignedIn) {
      const sync = async () => {
        const returnedUser = await authenticatedFetch(
          BASE_URL + "/api/v1/users/sync",
          {
            method: "POST",
          },
        );
        setMediamindUser(returnedUser);
      };
      sync();
    }
  }, [isLoaded, isSignedIn]);

  const authorizationHookReturnValue: UseAuthorizationReturn = {
    sessionToken: token,
    isLoaded,
    isSignedIn: Boolean(isSignedIn),
    authorizationHeaders: {
      Authorization: `Bearer ${token}`,
    },
    user: mediamindUser,
  };
  return (
    <AuthorizationContext.Provider value={authorizationHookReturnValue}>
      {children}
    </AuthorizationContext.Provider>
  );
};

export const useAuthorization = () => useContext(AuthorizationContext);
