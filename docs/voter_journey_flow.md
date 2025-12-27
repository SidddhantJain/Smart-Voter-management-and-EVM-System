# Voter Journey — Flow of Events (point format)

This file lists the end-to-end voter flow as concise, text-only points. Use it as a script, checklist, or to drive animation/UX capture. No diagrams included — plain bullet/numbered steps.

1. Start — machine ready
   - Ensure kiosk is powered and secure session is initialized.

2. Scene 0: Intro / Title (3–4s)
   - Full-screen title card with app name and short tagline.
   - Visual: centered headline, subtitle, small project logo.

3. Scene 1: Voter arrives & machine boots (6–8s)
   - Voter approaches kiosk area.
   - Kiosk shows boot splash (logo + progress spinner).
   - On-screen status: "Booting… Initializing secure environment".

4. Scene 2: Aadhaar entry (8–12s)
   - Display Aadhaar input field (12 digits) and primary "Verify" CTA.
   - Optional: OTP / ID-scan hint beneath input.
   - Input uses monospaced digits and visible cursor.

5. Scene 3: Biometric capture (Face / Finger / Retina) (12–16s)
   - Present three biometric method icons: Face, Fingerprint, Retina.
   - Show camera/live-feed placeholder or fingerprint pad area.
   - After capture, display compact success indicator (e.g., green check + "Verified").

6. Scene 4: Authentication & gated entry (6–8s)
   - Show authentication summary: avatar thumbnail, masked Aadhaar (e.g., ****5678), verified methods.
   - Display a prominent but gated CTA: "Proceed to Ballot" (enabled only on success).

7. Scene 5: Voting screen & choice (12–15s)
   - Show ballot UI with candidate/party tiles and a selected-candidate panel.
   - Selected tile indicates choice (border + check badge); show "Confirm Vote" CTA.
   - Confirmation modal includes a short summary and a transaction hash placeholder.

8. Scene 6: Secure vote storage (Blockchain) (8–10s)
   - Visualize vote payload → encryption padlock → ledger blocks.
   - Display masked voter fields (monospace) and a labeled state: "Encrypted & Stored".

9. Scene 7: Receipt & audit trail (6–8s)
   - Show transaction ID or QR-like block and a compact audit timeline (timestamp — action — status).
   - Example TX format: "TX: 3f9a…b1c2" (visual placeholder only).

10. Scene 8: Exit & admin dashboard (optional) (8–12s)
    - Stage A: voter leaves kiosk area.
    - Stage B: admin dashboard shows aggregated metrics (total votes, turnout %, anomaly list).

11. Scene 9: Closing slide (3–4s)
    - Full-bleed brand card with project logo, tagline, and small footer for contact/URL.

Notes and operational points
- Retry policy: allow biometric retries; after N failed attempts show "Manual assistance / Admin override" flow.
- Privacy: always mask personal identifiers in visuals (e.g., "Aadhaar: ****5678").
- Assets: reference UI screenshots as `ui_boot.png`, `ui_aadhaar.png`, `ui_biometric.png`, `ui_voting.png`, `ui_confirmation.png`.
- Use this document as a text-based script for recording or animating each scene.

---

File created: `docs/voter_journey_flow.md`
