import { Link } from "./Link.js";

const e = React.createElement;

export function TopNav(props) {
    return e(
        "header",
        { className: "top-nav" },
        e("a", { className: "brand", href: "/" }, "FarmsteadHelper"),
        e(
            "nav",
            { className: "menu" },
            e("a", { href: "/" }, "Home"),
            e("a", { href: "/catalog" }, "Catalog"),
            e("a", { href: "/catalog/animals/" }, "Animals"),
            e("a", { href: "/forum/" }, "Forum"),
            e("a", { href: "/map/" }, "Map"),
        ),
        e(
            "div",
            { className: "auth-box" },
            props.user
                ? e("a", { href: "/profile/" + props.user.username + "/" }, props.user.username)
                : e("a", { href: "/login/" }, "Sign in"),
        ),
    );
}
