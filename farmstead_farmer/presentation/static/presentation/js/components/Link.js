import { navigate } from "../core/navigation.js";

const e = React.createElement;

export function Link(props) {
    return e(
        "a",
        {
            href: props.to,
            className: props.className || "",
            onClick: function (event) {
                if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
                    return;
                }
                event.preventDefault();
                navigate(props.to);
            },
        },
        props.children,
    );
}
