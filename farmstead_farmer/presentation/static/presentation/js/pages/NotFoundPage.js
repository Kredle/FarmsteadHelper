import { Link } from "../components/Link.js";

const e = React.createElement;

export function NotFoundPage() {
    return e(
        "section",
        { className: "page" },
        e("h1", null, "Route is now SPA-driven"),
        e("p", { className: "lead" }, "This path does not have a dedicated React component yet."),
        e(Link, { to: "/" }, "Back to home"),
    );
}
