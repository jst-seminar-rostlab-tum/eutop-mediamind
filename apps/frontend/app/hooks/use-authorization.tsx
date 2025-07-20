import { useUser } from "@clerk/react-router";
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type PropsWithChildren,
} from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router";
import { client } from "types/api";
import type { MediamindUser } from "types/model";

type UseAuthorizationReturn = {
  isLoaded: boolean;
  isSignedIn: boolean;
  user?: MediamindUser;
  setMediamindUser?: (user: MediamindUser) => void;
};

const initialValue: UseAuthorizationReturn = {
  isLoaded: false,
  isSignedIn: false,
  user: undefined,
};

const AuthorizationContext = createContext(initialValue);

export const AuthorizationContextProvider = ({
  children,
}: PropsWithChildren) => {
  const { i18n } = useTranslation();
  const { isSignedIn, isLoaded } = useUser();
  const [mediamindUser, setMediamindUser] = useState<MediamindUser>();

  const navigate = useNavigate();
  const { pathname } = useLocation();

  // Redirect to error page, when not signed in
  useEffect(() => {
    if (
      isLoaded &&
      !isSignedIn &&
      !pathname.includes("error") &&
      pathname !== "/"
    ) {
      setMediamindUser(undefined);
      navigate("error/401?redirect_url=" + pathname);
    }
  }, [isLoaded, isSignedIn, pathname]);

  // Redirect to error page, when user has no organization
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
        const { data: returnedUser } = await client.POST("/api/v1/users/sync");
        setMediamindUser(returnedUser);
        i18n.changeLanguage(returnedUser?.language);
      };
      sync();
    }
  }, [isLoaded, isSignedIn]);

  const authorizationHookReturnValue: UseAuthorizationReturn = {
    isLoaded,
    isSignedIn: Boolean(isSignedIn),
    user: mediamindUser,
    setMediamindUser,
  };
  return (
    <AuthorizationContext.Provider value={authorizationHookReturnValue}>
      {children}
    </AuthorizationContext.Provider>
  );
};

export const useAuthorization = () => useContext(AuthorizationContext);
