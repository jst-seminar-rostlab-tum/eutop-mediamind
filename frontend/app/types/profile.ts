export interface Subscription {
  id: number;
  name: string;
}

export interface Topic {
  name: string;
  keywords: string[];
}

export interface Profile {
  id: string;
  name: string;
  organization_emails: string[];
  profile_emails: string[];
  public: boolean;
  editable: boolean;
  is_editable: boolean;
  owner: string;
  is_owner: boolean;
  subscriptions: Subscription[];
  topics: Topic[];
}