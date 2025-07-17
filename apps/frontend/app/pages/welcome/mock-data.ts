export const profiles = [
  {
    id: "1",
    name: "Eutop",
    is_public: true,
    organization_emails: ["user@example.com"],
    profile_emails: ["user@example.com"],
    can_read_user_ids: ["1"],
    is_reader: true,
    can_edit_user_ids: ["1"],
    is_editor: true,
    owner_id: "1",
    is_owner: true,
    language: "en",
    topics: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        keywords: ["string"],
      },
    ],
    subscriptions: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        is_subscribed: true,
      },
    ],
    new_articles_count: 3,
  },
  {
    id: "2",
    name: "TUM",
    is_public: true,
    organization_emails: ["user@example.com"],
    profile_emails: ["user@example.com"],
    can_read_user_ids: ["1"],
    is_reader: true,
    can_edit_user_ids: ["2"],
    is_editor: false,
    owner_id: "2",
    is_owner: true,
    language: "en",
    topics: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        keywords: ["string"],
      },
    ],
    subscriptions: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        is_subscribed: true,
      },
    ],
    new_articles_count: 7,
  },
  {
    id: "3",
    name: "CSEE",
    is_public: false,
    organization_emails: ["user@example.com"],
    profile_emails: ["user@example.com"],
    can_read_user_ids: ["1"],
    is_reader: true,
    can_edit_user_ids: ["1"],
    is_editor: true,
    owner_id: "1",
    is_owner: true,
    language: "en",
    topics: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        keywords: ["string"],
      },
    ],
    subscriptions: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        is_subscribed: true,
      },
    ],
    new_articles_count: 7,
  },
];
