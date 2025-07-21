import React from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";

export function MockedEmail() {
  const { t } = useTranslation();

  return (
    <div
      style={{
        margin: 0,
        backgroundColor: "#ffffff",
        fontFamily: "Helvetica, Arial, sans-serif",
      }}
    >
      <table width="100%" cellPadding={0} cellSpacing={0} border={0}>
        <tbody>
          <tr>
            <td align="center">
              <table
                width="600"
                cellPadding={0}
                cellSpacing={0}
                border={0}
                style={{
                  width: "100%",
                  maxWidth: "600px",
                  backgroundColor: "#ffffff",
                  overflow: "hidden",
                }}
              >
                {/* Header */}
                <tbody>
                  <tr>
                    <td
                      style={{
                        backgroundColor: "#4b99ff",
                        padding: "20px 35px",
                        color: "white",
                      }}
                    >
                      <h1
                        style={{
                          margin: 0,
                          fontSize: "2.1em",
                          fontWeight: 300,
                          color: "white",
                        }}
                      >
                        MediaMind
                      </h1>
                      <p
                        style={{
                          margin: "12px 0 0",
                          fontSize: "0.9em",
                          textTransform: "uppercase",
                          letterSpacing: "0.5px",
                        }}
                      >
                        {t("mock_email.date")}
                      </p>
                    </td>
                  </tr>

                  {/* Content */}
                  <tr>
                    <td
                      style={{
                        padding: "30px 40px 30px",
                        color: "#2c3e50",
                      }}
                    >
                      {/* Profile */}
                      <div
                        style={{
                          marginBottom: "25px",
                          borderBottom: "1px solid #e9ecef",
                          paddingBottom: "20px",
                        }}
                      >
                        <p
                          style={{
                            color: "#6c757d",
                            fontSize: "0.95em",
                            textTransform: "uppercase",
                            fontWeight: 500,
                            margin: "0 0 8px",
                          }}
                        >
                          {t("mock_email.search_profile")}
                        </p>
                        <p
                          style={{
                            color: "#1e5091",
                            fontSize: "1.2em",
                            fontWeight: 600,
                            margin: 0,
                          }}
                        >
                          TUM
                        </p>
                      </div>

                      {/* Message */}
                      <div
                        style={{
                          fontSize: "1.05em",
                          lineHeight: 1.65,
                          color: "#495057",
                        }}
                      >
                        <p style={{ margin: "0 0 18px" }}>
                          {t("mock_email.header")}
                          <br />
                          <br />
                          {t("mock_email.text_1")}
                          <br />
                          <br />
                          {t("mock_email.text_2")}
                        </p>
                      </div>

                      {/* Download Button */}
                      <div
                        style={{
                          textAlign: "center",
                          margin: "32px 0 0",
                        }}
                      >
                        <a
                          onClick={(e) => {
                            e.preventDefault();
                            toast.info(t("mock_email.download_toast"));
                          }}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: "inline-block",
                            background: "#1e5091",
                            color: "white",
                            textDecoration: "none",
                            fontWeight: "bold",
                            padding: "12px 32px",
                            borderRadius: "5px",
                            fontSize: "1.08em",
                            cursor: "pointer",
                          }}
                        >
                          {t("mock_email.download_here")}
                        </a>
                      </div>

                      {/* Dashboard Link */}
                      <div
                        style={{
                          fontSize: "0.95em",
                          color: "#495057",
                          marginTop: "24px",
                        }}
                      >
                        {t("mock_email.text_footer")} (
                        <a
                          onClick={(e) => {
                            e.preventDefault();
                            toast.info(t("mock_email.click_here_toast"));
                          }}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontWeight: 600,
                            color: "#1e5091",
                            textDecoration: "underline",
                            paddingBottom: "4px",
                            cursor: "pointer",
                          }}
                        >
                          {t("mock_email.click_here")}
                        </a>
                        ).
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
