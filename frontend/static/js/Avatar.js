// Default avatar: the user's initials on a coloured circle (no uploaded photos).
window.avatarFor = function (user) {
  const first = (user?.first_name || "").trim();
  const last = (user?.last_name || "").trim();
  let initials = (first.charAt(0) + last.charAt(0)).toUpperCase();
  if (!initials) {
    const name = (user?.nickname || user?.display_name || user?.email || "?").trim();
    initials = name.split(/\s+/).slice(0, 2).map((w) => w.charAt(0)).join("").toUpperCase() || "?";
  }
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">` +
    `<circle cx="60" cy="60" r="60" fill="#1f4e79"/>` +
    `<text x="60" y="60" fill="#fff" font-family="Arial, sans-serif" font-size="48" font-weight="700" ` +
    `text-anchor="middle" dominant-baseline="central">${initials.replace(/[<>&"]/g, "")}</text></svg>`;
  return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
};
