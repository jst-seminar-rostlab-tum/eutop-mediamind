export type Organization = {
  name: string;
  users: User[];
};

export type Subscription = {
  name: string;
  url: string;
  username: string;
  password: string;
};

export type User = {
  name: string;
  role: "admin" | "user";
};
