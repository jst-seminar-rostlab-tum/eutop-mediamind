import {
  SignedOut,
  SignedIn,
  UserButton,
  SignIn,
  SignUp,
} from "@clerk/react-router";
import { Link, useLocation, useSearchParams } from "react-router";
import {
  BarChart2,
  Building2,
  Contact,
  Globe,
  MoreVertical,
  Settings,
  User,
} from "lucide-react";
import { Button } from "~/components/ui/button";
import { useAuthorization } from "~/hooks/use-authorization";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "~/components/ui/popover";
import { useEffect, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { useTranslation } from "react-i18next";
import { client } from "types/api";
import { Skeleton } from "~/components/ui/skeleton";
import PersonalSettingsCard from "./user-settings/personal-settings-page";

const SIGN_UP = "ui_sign_up";
const SIGN_IN = "ui_sign_in";

export default function Header() {
  const { isSignedIn, user, isLoaded, setMediamindUser } = useAuthorization();
  const { pathname } = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const redirectUrl = searchParams.get("redirect_url");
  const [openLogin, setOpenLogin] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [updatingLanguage, setUpdatingLanguage] = useState(false);

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

  useEffect(() => {
    setOpenLogin(false);
  }, [pathname]);

  const { t, i18n } = useTranslation();

  const changeLanguage = async (lng: "en" | "de") => {
    i18n.changeLanguage(lng);
    if (user) {
      setUpdatingLanguage(true);
      await client.PUT("/api/v1/users/language", {
        params: { query: { language: lng } },
      });
      setMediamindUser?.({
        ...user,
        language: lng,
      });
      setUpdatingLanguage(false);
    }
  };

  return (
    <div className="p-4 w-full flex justify-between items-center">
      <div className="flex items-center gap-8">
        <Link to="/" className="mt-[0.3rem]">
          <img src="/MediaMind_Logo.svg" alt="MediaMind Logo" width={140} />
        </Link>
        {isSignedIn && user?.organization_name && (
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            <span className="text-sm font-semibold text-black">
              {user.organization_name}
            </span>
          </div>
        )}
      </div>

      <div className="flex justify-end items-center gap-4">
        {updatingLanguage || !isLoaded || (isLoaded && isSignedIn && !user) ? (
          <Skeleton className="h-8 w-20" />
        ) : (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="flex items-center gap-2">
                <Globe />
                {(user?.language ?? i18n.language).toLocaleUpperCase()}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => changeLanguage("en")}>
                English
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => changeLanguage("de")}>
                Deutsch
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}

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
                <User /> {t("login")}
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
          <UserButton>
            <UserButton.UserProfilePage
              label="Personal Settings"
              url="adsf"
              labelIcon={<Contact className="size-4" />}
            >
              <PersonalSettingsCard />
            </UserButton.UserProfilePage>
          </UserButton>
        </SignedIn>

        {isSignedIn && (user?.is_superuser || user?.role === "maintainer") && (
          <>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {user.is_superuser && (
                  <DropdownMenuItem asChild>
                    <Link to="/admin" className="flex items-center">
                      <Settings className="mr-2 h-4 w-4" />
                      Admin {t("admin.settings")}
                    </Link>
                  </DropdownMenuItem>
                )}
                {(user.role === "maintainer" || user.is_superuser) && (
                  <DropdownMenuItem asChild>
                    <Link
                      to="/organisation-settings"
                      className="flex items-center"
                    >
                      <Building2 className="mr-2 h-4 w-4" />
                      {t("organisation_settings.title")}
                    </Link>
                  </DropdownMenuItem>
                )}
                {user.is_superuser && (
                  <DropdownMenuItem asChild>
                    <Link to="/crawler-stats" className="flex items-center">
                      <BarChart2 className="mr-2 h-4 w-4" />
                      {t("crawler_stats.title")}
                    </Link>
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </>
        )}
      </div>
    </div>
  );
}
