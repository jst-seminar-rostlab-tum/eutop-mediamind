export default function useSearchProfile() {
  return {
    id: "1a2b3c4d-uuid-1",
    name: "BMW HR",
    organization_emails: ["abc@example.com", "def@example.com"],
    profile_emails: ["ghi@example.com", "jkl@example.com"],
    public: true,
    editable: false,
    is_editable: true,
    owner: "user-uuid-123",
    is_owner: true,
    subscriptions: [
      { id: 1, name: "Spiegel" },
      { id: 2, name: "Süddeutsche Zeitung" },
    ],
    topics: [
      {
        name: "Battery",
        keywords: ["Lithium", "Power", "Tesla", "Energy", "Charging", "Storage", "Electric", "Capacity"],
      },
      {
        name: "Recruiting",
        keywords: ["Talent", "Onboarding", "Interviews", "Hiring", "Candidates", "Recruitment", "Staffing", "Retention"],
      },
      {
        name: "Compliance",
        keywords: ["GDPR", "Regulations", "Privacy", "Legal", "Policies", "Standards", "Audit", "Certification"],
      },
      {
        name: "Payroll",
        keywords: ["Salary", "Benefits", "Taxes", "Compensation", "Bonuses", "Deductions", "Payments", "Accounting"],
      },
    ],
  };
}
