import "react-router";

declare module "react-router" {
  interface Register {
    params: Params;
  }
}

type Params = {
  "/": {};
  "/admin": {};
  "/crawler-stats": {};
  "/dashboard": {};
  "/search-profile/:searchProfileId/:matchId": {
    "searchProfileId": string;
    "matchId": string;
  };
  "/error/:code": {
    "code": string;
  };
  "/search-profile/:id": {
    "id": string;
  };
  "/dashboard/breaking": {};
  "/search-profile/:searchProfileId/reports": {
    "searchProfileId": string;
  };
};