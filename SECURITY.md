# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.8.x   | :white_check_mark: |
| 5.7.x   | :white_check_mark: |
| < 5.7   | :x:                |

## Reporting a Vulnerability

We take the security of `logistics-twin` seriously. If you discover a security vulnerability, please follow these steps:

1.  **Do NOT open a public issue.** This allows us to address the vulnerability before it can be exploited.
2.  **Email**: Send a detailed report to `security@logistics-twin.example.com` (replace with actual email if available).
3.  **Details**: Include:
    *   Description of the vulnerability.
    *   Steps to reproduce.
    *   Potential impact.
    *   Screenshots or proof-of-concept code.

### What happens next?

1.  We will acknowledge your report within 48 hours.
2.  We will investigate the issue and verify the vulnerability.
3.  We will work on a patch to fix the issue.
4.  We will release a security update.
5.  We will credit you (if desired) in the release notes.

## Security Best Practices

This project implements:
*   **Flask-Limiter**: To prevent rate-limiting abuse.
*   **Input Sanitization**: To prevent XSS and injection attacks.
*   **Docker Security**: Non-root user execution in production containers.
*   **Dependency Scanning**: Regular checks for vulnerable packages.

Please ensure you are using the latest version of these dependencies when deploying.
