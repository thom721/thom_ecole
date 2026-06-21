html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Code de réinitialisation</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f6f9; font-family: 'Segoe UI', Arial, sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9; padding: 40px 0;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #1a73e8, #0d47a1); padding: 40px 0; text-align:center;">
              <h1 style="margin:0; color:#ffffff; font-size:28px; font-weight:700; letter-spacing:1px;">
                🎓 Lekol 360
              </h1>
              <p style="margin:8px 0 0; color:#c9d9f7; font-size:14px;">
                Plateforme scolaire numérique
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 40px 48px;">

              <h2 style="margin:0 0 16px; color:#1a1a2e; font-size:22px;">
                Réinitialisation de mot de passe
              </h2>

              <p style="margin:0 0 24px; color:#555; font-size:15px; line-height:1.7;">
                Bonjour,<br><br>
                Nous avons reçu une demande de réinitialisation de votre mot de passe.
                Utilisez le code ci-dessous pour continuer. Ce code est valable pendant
                <strong>15 minutes</strong>.
              </p>

              <!-- Code Box -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding: 8px 0 32px;">
                    <div style="
                      display: inline-block;
                      background: #f0f5ff;
                      border: 2px dashed #1a73e8;
                      border-radius: 12px;
                      padding: 20px 48px;
                    ">
                      <p style="margin:0 0 4px; color:#888; font-size:12px; text-transform:uppercase; letter-spacing:2px;">
                        Votre code
                      </p>
                      <p style="margin:0; color:#1a73e8; font-size:42px; font-weight:800; letter-spacing:10px;">
                        {{code}}
                      </p>
                    </div>
                  </td>
                </tr>
              </table>

              <!-- Warning -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="
                    background:#fff8e1;
                    border-left: 4px solid #f9a825;
                    border-radius: 6px;
                    padding: 14px 18px;
                    margin-bottom: 24px;
                  ">
                    <p style="margin:0; color:#7a6000; font-size:13px; line-height:1.6;">
                      ⚠️ Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
                      Votre mot de passe restera inchangé.
                    </p>
                  </td>
                </tr>
              </table>

              <p style="margin: 24px 0 0; color:#aaa; font-size:13px; line-height:1.6;">
                Pour votre sécurité, ne partagez jamais ce code avec quelqu'un d'autre,
                même s'il prétend faire partie de l'équipe Lekol 360.
              </p>

            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding: 0 48px;">
              <hr style="border:none; border-top:1px solid #eee; margin:0;">
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 24px 48px; text-align:center;">
              <p style="margin:0 0 6px; color:#aaa; font-size:12px;">
                © 2025 Lekol 360 — Tous droits réservés
              </p>
              <p style="margin:0; color:#ccc; font-size:11px;">
                Cet email a été envoyé automatiquement, merci de ne pas y répondre.
              </p>
            </td>
          </tr>

        </table>
        <!-- End Card -->

      </td>
    </tr>
  </table>

</body>
</html>
"""