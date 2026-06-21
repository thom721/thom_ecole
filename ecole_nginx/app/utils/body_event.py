body = f"""
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
  <tr>
    <td style="background:#12151f; border:1px solid #2a2d3a; border-radius:10px; padding:22px 26px;">
      <p style="margin:0 0 10px; color:#4f8ef7; font-size:11px; text-transform:uppercase; letter-spacing:2px; font-weight:600;">📅 Événement</p>
      <p style="margin:0 0 8px; color:#f1f1f3; font-size:17px; font-weight:700;">{event_title}</p>
      <p style="margin:0 0 4px; color:#6b7280; font-size:13px;">📍 {location}</p>
      <p style="margin:0; color:#6b7280; font-size:13px;">🕐 {start_date}</p>
    </td>
  </tr>
</table>
"""