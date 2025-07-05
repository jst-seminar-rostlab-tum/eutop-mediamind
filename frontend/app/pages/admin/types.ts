export type User = {
  name: string;
  role: "admin" | "user";
};

export type DeleteTarget = {
  type: "subscription" | "organization";
  identifier: number | string;
};
