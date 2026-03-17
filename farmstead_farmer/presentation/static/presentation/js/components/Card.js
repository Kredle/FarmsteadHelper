import { Link } from "./Link.js";

const e = React.createElement;

export function Card(props) {
    return e(
        "article",
        { className: "card" },
        props.image ? e("img", { className: "card-image", src: props.image, alt: props.title || "image" }) : null,
        e("h3", { className: "card-title" }, props.title || "Untitled"),
        props.subtitle ? e("p", { className: "card-subtitle" }, props.subtitle) : null,
        props.link ? e(Link, { to: props.link, className: "card-link" }, "Open") : null,
    );
}
