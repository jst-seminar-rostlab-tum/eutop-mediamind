import type { ProfileReports, Report } from "../../../types/model";

const mockReports: ProfileReports = {
  reports: [
    {
      id: "550e8400-e29b-41d4-a716-446655440001",
      search_profile_id: "550e8400-e29b-41d4-a716-446655440010",
      created_at: "2025-06-07T08:15:07.697000Z",
      time_slot: "morning",
      language: "en",
      s3_key: "reports/2025/06/07/report_001.pdf",
      status: "uploaded",
    },
    {
      id: "550e8400-e29b-41d4-a716-446655440002",
      search_profile_id: "550e8400-e29b-41d4-a716-446655440011",
      created_at: "2025-06-06T14:30:22.123000Z",
      time_slot: "afternoon",
      language: "de",
      s3_key: "reports/2025/06/06/report_002.pdf",
      status: "pending",
    },
    {
      id: "550e8400-e29b-41d4-a716-446655440003",
      search_profile_id: "550e8400-e29b-41d4-a716-446655440012",
      created_at: "2025-06-05T16:45:33.456000Z",
      time_slot: null,
      language: "fr",
      s3_key: "reports/2025/06/05/report_003.pdf",
      status: "failed",
    },
    {
      id: "550e8400-e29b-41d4-a716-446655440004",
      search_profile_id: "550e8400-e29b-41d4-a716-446655440013",
      created_at: "2025-06-04T10:20:15.789000Z",
      time_slot: "evening",
      language: "es",
      s3_key: "reports/2025/06/04/report_004.pdf",
      status: "uploaded",
    },
  ],
};

const mockReportDetails: Record<string, Report> = {
  "550e8400-e29b-41d4-a716-446655440001": {
    id: "550e8400-e29b-41d4-a716-446655440001",
    search_profile_id: "550e8400-e29b-41d4-a716-446655440010",
    created_at: "2025-06-07T08:15:07.697000Z",
    time_slot: "morning",
    language: "en",
    s3_key: "reports/2025/06/07/report_001.pdf",
    status: "uploaded",
    s3_url:
      "https://my-bucket.s3.amazonaws.com/reports/2025/06/07/report_001.pdf?AWSAccessKeyId=AKIAIOSFODNN7EXAMPLE&Expires=1717747200&Signature=example123",
  },
  "550e8400-e29b-41d4-a716-446655440002": {
    id: "550e8400-e29b-41d4-a716-446655440002",
    search_profile_id: "550e8400-e29b-41d4-a716-446655440011",
    created_at: "2025-06-06T14:30:22.123000Z",
    time_slot: "afternoon",
    language: "de",
    s3_key: "reports/2025/06/06/report_002.pdf",
    status: "pending",
    s3_url: null,
  },
  "550e8400-e29b-41d4-a716-446655440003": {
    id: "550e8400-e29b-41d4-a716-446655440003",
    search_profile_id: "550e8400-e29b-41d4-a716-446655440012",
    created_at: "2025-06-05T16:45:33.456000Z",
    time_slot: null,
    language: "fr",
    s3_key: "reports/2025/06/05/report_003.pdf",
    status: "failed",
    s3_url: null,
  },
  "550e8400-e29b-41d4-a716-446655440004": {
    id: "550e8400-e29b-41d4-a716-446655440004",
    search_profile_id: "550e8400-e29b-41d4-a716-446655440013",
    created_at: "2025-06-04T10:20:15.789000Z",
    time_slot: "evening",
    language: "es",
    s3_key: "reports/2025/06/04/report_004.pdf",
    status: "uploaded",
    s3_url:
      "https://my-bucket.s3.amazonaws.com/reports/2025/06/04/report_004.pdf?AWSAccessKeyId=AKIAIOSFODNN7EXAMPLE&Expires=1717747300&Signature=example456",
  },
};

export const getReports = (): ProfileReports => {
  return mockReports;
};

export const getReport = (id: string): Report | null => {
  const report = mockReportDetails[id];
  return report || null;
};
